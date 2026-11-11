"""Cumulative shakeout runner."""

import importlib
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

from pydantic import model_validator

from chupa.artifacts import Artifact, NonBlank, _Strict
from chupa.audit import audit
from chupa.git import Git
from chupa.seams import SubprocessExec
from tests.harness.shakeout.bench import Bench
from tests.integration.test_git import commit_lock

SHAKEOUT_SPEC_VERSION = 1


class ShakeoutEntry(_Strict):
    member: NonBlank
    group: NonBlank
    planted_fault: NonBlank
    expected: NonBlank
    observed: NonBlank
    producing_run: NonBlank
    auditor: list[NonBlank]
    green: bool

    @model_validator(mode="after")
    def _consistent(self) -> "ShakeoutEntry":
        if not re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*", self.member):
            raise ValueError("member must be a snake-case id")
        if not re.fullmatch(r"[a-z][a-z0-9_-]*/[0-9]+", self.producing_run):
            raise ValueError("producing_run must be <bench stem>/<run seq>")
        if self.green != (self.observed == self.expected and not self.auditor):
            raise ValueError("green must match the observation and empty auditor")
        return self


class ShakeoutReport(Artifact):
    entries: list[ShakeoutEntry]

    @model_validator(mode="after")
    def _unique_members(self) -> "ShakeoutReport":
        ids = [entry.member for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("member ids must be unique")
        return self


GROUPS: tuple[str, ...] = ("stages", "driver", "runner", "drain", "recovery", "merge", "providers")


@dataclass(frozen=True)
class Observation:
    observed: str
    producing_run: str


@dataclass(frozen=True)
class Member:
    id: str
    group: str
    planted_fault: str
    expected: str
    run: Callable[[Bench], Awaitable[Observation]]


class ShakeoutRefused(Exception):
    pass


def _members(group: str) -> tuple[Member, ...]:
    return importlib.import_module(f"tests.harness.shakeout.{group}").MEMBERS


async def run_member(member: Member, root: Path) -> ShakeoutEntry:
    bench = Bench(root / member.id)
    await bench.initialize()
    observation = await member.run(bench)
    violations = audit(bench.segments())
    lines = [f"{v.invariant}: {v.ticket or '-'}: {v.detail}" for v in violations]
    return ShakeoutEntry(
        member=member.id,
        group=member.group,
        planted_fault=member.planted_fault,
        expected=member.expected,
        observed=observation.observed,
        producing_run=observation.producing_run,
        auditor=lines,
        green=observation.observed == member.expected and not lines,
    )


async def produce(group: str, prior: ShakeoutReport | None, root: Path) -> ShakeoutReport:
    if group not in GROUPS:
        raise ValueError(f"unknown group {group}")
    preceding = GROUPS[: GROUPS.index(group)]
    earlier = {member.id: member for name in preceding for member in _members(name)}
    prior_entries = {entry.member: entry for entry in prior.entries} if prior is not None else {}
    for member in earlier.values():
        old = prior_entries.get(member.id)
        if old is None or not old.green:
            raise ShakeoutRefused(member.id)
        fresh = await run_member(member, root / "prior")
        if not fresh.green or fresh.observed != old.observed:
            raise ShakeoutRefused(member.id)
    entries = [prior_entries[member.id] for member in earlier.values()]
    for member in _members(group):
        entry = await run_member(member, root / group)
        if not entry.green:
            raise ShakeoutRefused(member.id)
        entries.append(entry)
    import os

    # Git provenance is read from the checkout running the report command, never supplied by a member.
    git = Git(SubprocessExec(), env=os.environ, timeout=30.0, commit_lock=commit_lock(root / ".chupa/state"))
    sha = await git.rev_parse(Path.cwd(), "HEAD")
    return ShakeoutReport(produced_by_spec_version=SHAKEOUT_SPEC_VERSION, produced_at_sha=sha, entries=entries)
