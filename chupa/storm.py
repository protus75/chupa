"""Journal-backed storm occurrences and escalation (19.P3.storm-notification-activation)."""

import re
import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from chupa.journal import Event, EventType, Journal, render_ts
from chupa.seams import Clock

STORM_WINDOW = timedelta(hours=1)
STORM_THRESHOLD = 5
STORM_TRIP = "storm_breaker_trip"
_PREFIX = "storm-occurrence/"
_FIELDS = {"kind", "signature", "occurrence_id", "emitting_stage", "emitting_origin"}


def _invalid(reason: str) -> ValueError:
    return ValueError(f"invalid storm occurrence: {reason}; supply a fresh id for a distinct arrival "
                      "or repair the producing evidence, never overwrite journal history")


def _key(body: dict[str, Any]) -> str:
    if set(body) != _FIELDS or body.get("kind") != "storm_occurrence":
        raise _invalid("body must contain exactly the storm_occurrence fields")
    signature, identity = body["signature"], body["occurrence_id"]
    if not isinstance(signature, str) or re.fullmatch(r"[0-9a-f]{64}", signature) is None:
        raise _invalid("signature must be the producer's 64-character lowercase SHA-256 digest")
    if not isinstance(identity, str) or not identity.strip():
        raise _invalid("occurrence_id must be a nonblank producer-supplied string")
    if any(body[field] is not None and not isinstance(body[field], str)
           for field in ("emitting_stage", "emitting_origin")):
        raise _invalid("emitting_stage and emitting_origin must be strings or null")
    return f"{_PREFIX}{signature}/{identity}"


class StormLedger:
    """Direct invocation only; the caller already owns the journal's writer lock."""

    def __init__(self, *, journal: Journal, clock: Clock) -> None:
        self.journal, self.clock = journal, clock

    def _history(self) -> dict[str, Event]:
        history: dict[str, Event] = {}
        for event in self.journal.read():
            if event.type != EventType.SIGNAL:
                continue
            if event.body.get("kind") != "storm_occurrence" and not (
                event.key is not None and event.key.startswith(_PREFIX)
            ):
                continue
            key = _key(event.body)
            if event.key != key or event.ticket is not None:
                raise _invalid("key must agree with the body and ticket must be null")
            prior = history.get(key)
            if prior is not None and prior.body != event.body:
                raise _invalid(f"key {key!r} already owns different occurrence data")
            if prior is None:
                history[key] = event
        return history

    def record(self, *, signature: str, occurrence_id: str,
               emitting_stage: str | None, emitting_origin: str | None) -> Event:
        body = {"kind": "storm_occurrence", "signature": signature,
                "occurrence_id": occurrence_id, "emitting_stage": emitting_stage,
                "emitting_origin": emitting_origin}
        key = _key(body)
        prior = self._history().get(key)
        if prior is not None:
            if prior.body != body:
                raise _invalid(f"key {key!r} already owns different occurrence data")
            return prior
        return self.journal.append(EventType.SIGNAL, body, ticket=None, key=key)

    def occurrences(self, signature: str) -> tuple[Event, ...]:
        # Validate the requested digest by the same law as the durable evidence.
        _key({"kind": "storm_occurrence", "signature": signature, "occurrence_id": "projection",
              "emitting_stage": None, "emitting_origin": None})
        history = self._history()
        now = datetime.fromisoformat(render_ts(self.clock()))
        return tuple(event for event in history.values()
                     if event.body["signature"] == signature
                     and now - STORM_WINDOW < datetime.fromisoformat(event.ts) <= now)

    def count(self, signature: str) -> int:
        return len(self.occurrences(signature))


def arrival_id(*parts: str | int) -> str:
    return "storm-arrival/" + _digest(list(parts))


def _digest(parts: list) -> str:
    return hashlib.sha256(json.dumps(parts, separators=(",", ":"), ensure_ascii=True)
                          .encode("utf-8")).hexdigest()


class StormBreaker(StormLedger):
    """Recover the write-ahead escalation through the existing Box publisher."""

    def __init__(self, *, journal: Journal, clock: Clock,
                 publish: Callable[[dict[str, Any], int], object]) -> None:
        super().__init__(journal=journal, clock=clock)
        self.publish = publish
        self._recovering = False

    def _evidence(self) -> tuple[dict[str, tuple[dict[str, Any], int]], set[str]]:
        occurrences = self._history()
        now_limit = datetime.fromisoformat(render_ts(self.clock()))
        live_history: list[Event] = []
        expected: dict[str, tuple[dict[str, Any], int]] = {}
        recorded: set[str] = set()
        seen: set[str] = set()
        for event in self.journal.read():
            if event.key in occurrences and event == occurrences[event.key] and event.key not in seen:
                seen.add(event.key)
                live_history.append(event)
                signature = event.body["signature"]
                now = datetime.fromisoformat(event.ts)
                live = [item for item in live_history if item.body["signature"] == signature
                        and now - STORM_WINDOW < datetime.fromisoformat(item.ts) <= now]
                if (now <= now_limit and len(live) > STORM_THRESHOLD
                        and signature not in expected):
                    first, crossing = live[0].body["occurrence_id"], event.body["occurrence_id"]
                    stage, origin = event.body["emitting_stage"], event.body["emitting_origin"]
                    body = dict(kind=STORM_TRIP, signature=signature,
                                trip_id=_digest([signature, first, crossing]),
                                first_occurrence_id=first, crossing_occurrence_id=crossing,
                                emitting_stage=stage, emitting_origin=origin,
                                held=(dict(emitting_stage=stage, emitting_origin=origin)
                                      if stage in {"implement", "check", "review"} else None))
                    expected[signature] = body, len(live)
            reserved = event.key is not None and event.key.startswith("storm-trip/")
            if event.body.get("kind") != STORM_TRIP and not reserved:
                continue
            candidate = expected.get(event.body.get("signature")) if isinstance(event.body.get("signature"), str) else None
            if (candidate is None or event.type != EventType.SIGNAL or event.ticket is not None
                    or event.body != candidate[0]
                    or event.key != "storm-trip/" + candidate[0]["trip_id"]):
                raise _invalid("malformed or conflicting storm trip evidence")
            recorded.add(candidate[0]["trip_id"])
        return expected, recorded

    def recover(self) -> None:
        if self._recovering:
            return
        expected, recorded = self._evidence()
        self._recovering = True
        try:
            for body, count in expected.values():
                if body["trip_id"] not in recorded:
                    self.journal.append(EventType.SIGNAL, body, ticket=None,
                                        key="storm-trip/" + body["trip_id"])
                self.publish(body, count)
        finally:
            self._recovering = False

    def record(self, **arrival: Any) -> Event:
        # Refuse corrupt trip evidence before adding even an otherwise valid arrival.
        _key(dict(kind="storm_occurrence", **arrival))
        self._evidence()
        event = super().record(**arrival)
        self.recover()
        return event
