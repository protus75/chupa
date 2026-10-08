"""Identity-bound control requests (CHUPA_PLAN.md 19.P3.control-inbox)."""

import json
import re
from collections.abc import Callable, Iterable, Set
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from chupa.journal import Event, EventType, Journal
from chupa.seams import FileSystem

CONTROL_DECISION = "control_decision"
Verb = Literal["pause", "resume", "kill"]
_ID = re.compile(r"[A-Za-z0-9_-]+", re.ASCII)
_SHAPE = ('submit a new request with exactly {request_id: nonempty ASCII letters/digits/_/-, '
          'lifecycle_id: nonempty string, verb: pause | resume | kill, hold_id: string | null}; '
          'match request_id to the filename; pause/kill require null hold_id; '
          'for resume read the current hold and submit its exact nonempty identity')


@dataclass(frozen=True)
class ControlRequest:
    request_id: str
    lifecycle_id: str
    verb: Verb
    hold_id: str | None


def validate_request(value: object, filename: str) -> ControlRequest:
    if (not isinstance(value, dict)
            or set(value) != {"request_id", "lifecycle_id", "verb", "hold_id"}):
        raise ValueError(_SHAPE)
    request_id, lifecycle_id, verb, hold_id = (value[k] for k in
                                             ("request_id", "lifecycle_id", "verb", "hold_id"))
    if (not isinstance(request_id, str) or _ID.fullmatch(request_id) is None
            or filename != request_id + ".json"
            or not isinstance(lifecycle_id, str) or not lifecycle_id
            or not isinstance(verb, str) or verb not in {"pause", "resume", "kill"}
            or (verb == "resume" and (not isinstance(hold_id, str) or not hold_id))
            or (verb != "resume" and hold_id is not None)):
        raise ValueError(_SHAPE)
    return ControlRequest(request_id, lifecycle_id, verb, hold_id)


def publish_request(state_dir: Path, request: ControlRequest, fs: FileSystem) -> None:
    value = asdict(request)
    validate_request(value, str(request.request_id) + ".json")
    try:
        fs.publish(state_dir / "control/inbox" / (request.request_id + ".json"),
                   json.dumps(value, separators=(",", ":")).encode())
    except FileExistsError as exc:
        raise FileExistsError("request id already exists; submit a new request id") from exc


def _object(pairs: list[tuple[str, object]]) -> dict:
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError(_SHAPE)
    return value


@dataclass(frozen=True)
class ControlProjection:
    """Desired state, never an instruction to repeat an external action.

    Applications assign pause/kill state and release only the named hold identities.
    They must be idempotent across scans and reconstruction. Kill execution and its
    completion record belong to the later activation, not to this projection.
    """

    lifecycle_id: str
    pause_id: str | None = None
    released_hold_ids: frozenset[str] = frozenset()
    kill_requested: bool = False


def decisions(events: Iterable[Event]) -> Iterable[Event]:
    """Validate the sole inbox writer's evidence before granting release authority."""
    seen: dict[str, dict] = {}
    road = "repair the producing control evidence, never overwrite journal history"
    for event in events:
        body = event.body
        if body.get("kind") != CONTROL_DECISION:
            continue
        if (event.type != EventType.SIGNAL or event.ticket is not None or event.key is not None
                or set(body) != {"kind", "request_id", "lifecycle_id", "verb", "hold_id",
                                 "decision", "reason"}
                or not isinstance(body.get("request_id"), str)
                or _ID.fullmatch(body["request_id"]) is None
                or not isinstance(body.get("decision"), str)
                or body.get("decision") not in {"accepted", "stale", "rejected"}
                or not isinstance(body.get("reason"), str) or not body["reason"]):
            raise ValueError(f"invalid control decision; {road}")
        request_id = body["request_id"]
        if body["decision"] == "rejected":
            if any(body[field] is not None for field in ("lifecycle_id", "verb", "hold_id")):
                raise ValueError(f"invalid rejected control decision; {road}")
        else:
            try:
                validate_request({field: body[field] for field in
                                  ("request_id", "lifecycle_id", "verb", "hold_id")},
                                 request_id + ".json")
            except ValueError as exc:
                raise ValueError(f"invalid control decision; {road}") from exc
        if request_id in seen:
            if seen[request_id] != body:
                raise ValueError(f"conflicting control decision; {road}")
            continue
        seen[request_id] = body
        yield event


class ControlInbox:
    """Serial consumer owned by the existing journal lock holder.

    Listing and reading are injected filesystem seams. The owner supplies a fresh,
    restart-unique lifecycle identity and live hold identities, never hold kinds.
    """

    def __init__(self, *, journal: Journal, lifecycle_id: str,
                 holds: Callable[[], Set[str]], apply: Callable[[ControlProjection], None],
                 files: Callable[[], Iterable[Path]], read: Callable[[Path], bytes]) -> None:
        if not isinstance(lifecycle_id, str) or not lifecycle_id:
            raise ValueError("supply the owner's nonempty restart-unique lifecycle identity")
        self.journal, self.lifecycle_id = journal, lifecycle_id
        self.holds, self.apply, self.files, self.read = holds, apply, files, read
        self._applied: ControlProjection | None = None

    def _fold(self) -> tuple[set[str], ControlProjection, bool]:
        decided = set()
        pause = None
        released = set()
        killed = False
        accepted = False
        for event in decisions(self.journal.read()):
            body = event.body
            request_id = body["request_id"]
            decided.add(request_id)
            if body["decision"] != "accepted" or body["lifecycle_id"] != self.lifecycle_id:
                continue
            accepted = True
            if body["verb"] == "pause":
                pause = request_id
            elif body["verb"] == "resume":
                released.add(body["hold_id"])
                if pause == body["hold_id"]:
                    pause = None
            elif body["verb"] == "kill":
                killed = True
        return decided, ControlProjection(self.lifecycle_id, pause, frozenset(released), killed), accepted

    def recover(self) -> ControlProjection:
        _, projection, accepted = self._fold()
        if accepted and projection != self._applied:
            self.apply(projection)
            self._applied = projection
        return projection

    def consume(self) -> None:
        projection = self.recover()
        decided, _, _ = self._fold()
        for path in sorted(self.files(), key=lambda path: path.name):
            # Private temporaries and unsafe filenames cannot supply a journal identity.
            if path.suffix != ".json" or _ID.fullmatch(path.stem) is None:
                continue
            if path.stem in decided:
                continue
            body = {"kind": CONTROL_DECISION, "request_id": path.stem,
                    "lifecycle_id": None, "verb": None, "hold_id": None,
                    "decision": "rejected", "reason": _SHAPE}
            try:
                request = validate_request(json.loads(self.read(path), object_pairs_hook=_object), path.name)
            except (ValueError, UnicodeError):
                pass
            else:
                body.update(asdict(request))
                live_holds = set(self.holds()) - projection.released_hold_ids
                if projection.pause_id is not None:
                    live_holds.add(projection.pause_id)
                if request.lifecycle_id != self.lifecycle_id:
                    body.update(decision="stale", reason="read the current lifecycle and submit a new request")
                elif request.verb == "resume" and request.hold_id not in live_holds:
                    body.update(decision="stale", reason="read the current hold and submit a new request")
                else:
                    body.update(decision="accepted", reason="matching lifecycle and hold identities")
            self.journal.append(EventType.SIGNAL, body, ticket=None, key=None)
            decided.add(path.stem)
            if body["decision"] == "accepted":
                projection = self.recover()


_DISCOVERY_ROAD = ("retry after the running engine publishes its current control identity; "
                   "read that identity and submit a new request")


def write_active(state_dir: Path, projection: ControlProjection | None, fs: FileSystem, *,
                 hold_id: str | None) -> None:
    value = (None if projection is None else
             {"lifecycle_id": projection.lifecycle_id, "hold_id": hold_id})
    fs.write(state_dir / "control/active.json", (json.dumps(value) + "\n").encode())


def read_active(state_dir: Path, read: Callable[[Path], bytes]) -> tuple[str, str | None]:
    try:
        value = json.loads(read(state_dir / "control/active.json"), object_pairs_hook=_object)
        if (not isinstance(value, dict) or set(value) != {"lifecycle_id", "hold_id"}
                or not isinstance(value["lifecycle_id"], str) or not value["lifecycle_id"]
                or (value["hold_id"] is not None and
                    (not isinstance(value["hold_id"], str) or not value["hold_id"]))):
            raise ValueError
    except (OSError, ValueError, UnicodeError) as exc:
        raise ValueError(_DISCOVERY_ROAD) from exc
    return value["lifecycle_id"], value["hold_id"]
