"""Durable Suggestion Box and decision registry formats (plan section 12)."""

import asyncio
import hashlib
import json
import os
import re
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Literal, get_args

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from chupa.config import load_config
from chupa.git import Git
from chupa.journal import Journal
from chupa.seams import Clock, FileSystem, LocalFileSystem, SubprocessExec

BOX_DIR = "box"
MessageClass = Literal["suggestion", "failure_report", "override_report", "retro_finding", "bug_report"]
MESSAGE_CLASSES = get_args(MessageClass)
BOOTSTRAP_ORIGIN = "bootstrap-ingest"
BOOTSTRAP_FILE = "bootstrap/suggestions.md"
DECISIONS_DIR = "tickets/decisions"


class BoxError(Exception):
    """A box message or registry record is missing or invalid."""


def normalize(reason: str) -> str:
    kept = " ".join(token for token in reason.split() if "/" not in token)
    return " ".join(re.sub(r"\d+", "", kept).split())


def signature(*fields: str, reason: str) -> str:
    payload = json.dumps([*fields, normalize(reason)], separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


NonBlank = Annotated[str, Field(min_length=1, pattern=r"\S")]


class _Strict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class Verdict(_Strict):
    verdict: Literal["author", "tombstone", "decision"]
    produced_by_spec_version: NonBlank
    rationale: NonBlank


class Resolution(_Strict):
    kind: Literal["ticket", "tombstone", "decision"]
    link: NonBlank


class Message(_Strict):
    id: NonBlank
    seq: Annotated[int, Field(ge=1)]
    signature: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    message_class: MessageClass
    summary: NonBlank
    origin: NonBlank
    stage: str | None
    outcome: str | None
    bug_origin: Literal["self_diagnosed", "player"] | None
    has_repro: bool | None
    status: Literal["pending", "resolved"]
    verdict: Verdict | None
    resolution: Resolution | None

    @model_validator(mode="after")
    def _coherent(self) -> "Message":
        if (self.stage is None) != (self.outcome is None):
            raise ValueError("stage and outcome must both be set or both be null")
        if (self.bug_origin is not None and self.has_repro is not None) != (self.message_class == "bug_report"):
            raise ValueError("bug_origin and has_repro are required exactly for bug_report")
        if (self.status == "resolved") != (self.resolution is not None):
            raise ValueError("resolution is required exactly when resolved")
        return self


class Box:
    def __init__(self, root: Path, fs: FileSystem, *,
                 arrival: Callable[..., object] | None = None,
                 recover: Callable[[], None] | None = None) -> None:
        self.root = root
        self.fs = fs
        self._arrival = arrival
        self._recover = recover

    def messages(self) -> list[Message]:
        result = []
        for path in self.root.glob("*.json"):
            try:
                result.append(Message.model_validate_json(path.read_text()))
            except (OSError, ValidationError, ValueError) as exc:
                raise BoxError(f"invalid box file {path}: {exc}") from exc
        return sorted(result, key=lambda message: message.seq)

    def pending(self) -> list[Message]:
        return [message for message in self.messages() if message.status == "pending"]

    def get(self, id: str) -> Message:
        for message in self.messages():
            if message.id == id:
                return message
        raise BoxError(f"unknown box id {id}")

    def _path(self, message: Message) -> Path:
        return self.root / f"{message.seq:06d}-{message.signature[:8]}.json"

    def _write(self, message: Message) -> None:
        self.fs.write(self._path(message), message.model_dump_json().encode())

    def enqueue(
        self, *, message_class: MessageClass, origin: str, summary: str,
        stage: str | None = None, outcome: str | None = None, reason: str | None = None,
        bug_origin: Literal["self_diagnosed", "player"] | None = None, has_repro: bool | None = None,
        occurrence_id: str | None = None,
    ) -> tuple[str, bool]:
        if self._arrival is not None and (not isinstance(occurrence_id, str) or not occurrence_id.strip()):
            raise BoxError("occurrence_id must be a nonblank producer-supplied string; "
                           "supply a fresh id for a distinct arrival and reuse it on retry")
        if (stage is None) != (outcome is None):
            raise BoxError("stage and outcome must both be set or both be null")
        fields = (message_class, origin) if stage is None else (message_class, origin, stage, outcome)
        digest = signature(*fields, reason=summary if reason is None else reason)
        try:
            message = Message(
                id=f"box-000001-{digest[:8]}", seq=1, signature=digest, message_class=message_class, summary=summary,
                origin=origin, stage=stage, outcome=outcome, bug_origin=bug_origin, has_repro=has_repro,
                status="pending", verdict=None, resolution=None,
            )
        except ValidationError as exc:
            raise BoxError(f"invalid box message: {exc}") from exc
        existing = self.messages()
        if self._arrival is not None:
            self._arrival(signature=digest, occurrence_id=occurrence_id,
                          emitting_stage=stage, emitting_origin=origin)
            # An arrival may publish its trip report before this source message.
            existing = self.messages()
        for prior in existing:
            if prior.signature == digest:
                return prior.id, False
        seq = max((prior.seq for prior in existing), default=0) + 1
        id = f"box-{seq:06d}-{digest[:8]}"
        message = message.model_copy(update={"id": id, "seq": seq})
        self._write(message)
        return id, True

    def recover(self) -> None:
        if self._recover is not None:
            self._recover()

    def publish_storm_report(self, body: dict, count: int) -> tuple[str, bool]:
        return self.enqueue(
            message_class="failure_report", origin="storm-breaker/" + body["trip_id"],
            summary=(f"P0 storm breaker trip: signature {body['signature']}; trip {body['trip_id']}; "
                     f"{count} occurrences in one-hour window; emitting stage "
                     f"{body['emitting_stage']!r}, origin {body['emitting_origin']!r}"),
            reason="storm breaker trip", occurrence_id="storm-report/" + body["trip_id"],
        )

    def record_verdict(self, id: str, verdict: Verdict) -> None:
        message = self.get(id)
        self._write(message.model_copy(update={"verdict": verdict}))

    def resolve(self, id: str, resolution: Resolution) -> None:
        message = self.get(id)
        if message.status == "resolved":
            raise BoxError(f"box id {id} is already resolved")
        self._write(message.model_copy(update={"status": "resolved", "resolution": resolution}))


class DecisionRecord(_Strict):
    id: NonBlank
    kind: Literal["decision", "tombstone"]
    link: NonBlank
    reopen_after_days: Annotated[int, Field(ge=1)]


def record_path(id: str) -> Path:
    return Path(DECISIONS_DIR) / f"{id}.md"


def render_record(record: DecisionRecord, body: str) -> str:
    return f"---\n{yaml.safe_dump(record.model_dump(), sort_keys=False)}---\n{body}"


def parse_record(text: str) -> tuple[DecisionRecord, str]:
    if not text.startswith("---\n"):
        raise BoxError("decision record missing YAML frontmatter")
    front, separator, body = text[4:].partition("\n---\n")
    if not separator:
        raise BoxError("decision record missing closing YAML fence")
    try:
        return DecisionRecord.model_validate(yaml.safe_load(front)), body
    except (yaml.YAMLError, ValidationError) as exc:
        raise BoxError(f"invalid decision record: {exc}") from exc


def read_registry(repo: Path) -> list[tuple[DecisionRecord, str]]:
    records = []
    for path in (repo / DECISIONS_DIR).glob("*.md"):
        try:
            records.append(parse_record(path.read_text()))
        except (OSError, BoxError) as exc:
            raise BoxError(f"invalid decision record {path}: {exc}") from exc
    return sorted(records, key=lambda item: item[0].id)


def ingest_bootstrap(box: Box, text: str) -> list[str]:
    from chupa.storm import arrival_id

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return [
        box.enqueue(message_class="suggestion", origin=BOOTSTRAP_ORIGIN, summary=line.strip(),
                    occurrence_id=arrival_id("bootstrap-ingest", digest, n))[0]
        for n, line in enumerate(text.splitlines(), 1) if line.strip()
    ]


async def ingest_main_checkout(cwd: Path, git: Git, fs: FileSystem, *,
                               journal: Journal | None = None, clock: Clock | None = None) -> int:
    root = (await git.git_common_dir(cwd)).parent
    config = load_config(None, cwd=root)
    source = root / BOOTSTRAP_FILE
    if not source.exists():
        return 0
    if journal is None:
        box = Box(config.state_dir / BOX_DIR, fs)
    else:
        from chupa.daemon import storm_producer

        if clock is None:
            raise BoxError("journal-holding ingest requires the checkout clock; supply its injected clock")
        box = storm_producer(root=config.state_dir / BOX_DIR, fs=fs, journal=journal, clock=clock)
        box.recover()
    before = len(box.messages())
    ingest_bootstrap(box, source.read_text())
    return len(box.messages()) - before


if __name__ == "__main__":
    git = Git(SubprocessExec(), env=os.environ, timeout=30.0)
    count = asyncio.run(ingest_main_checkout(Path.cwd(), git, LocalFileSystem()))
    print(f"ingested {count} new suggestion messages")
