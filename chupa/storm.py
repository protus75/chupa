"""Dormant journal-backed storm occurrences (CHUPA_PLAN.md 19.P3.storm-ledger)."""

import re
from datetime import datetime, timedelta
from typing import Any

from chupa.journal import Event, EventType, Journal, render_ts
from chupa.seams import Clock

STORM_WINDOW = timedelta(hours=1)
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
