"""Cumulative shakeout runner and sole report writer."""

import argparse
import asyncio
import importlib
import tempfile
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

from chupa.artifacts import SHAKEOUT_SPEC_VERSION, ShakeoutEntry, ShakeoutReport
from chupa.audit import audit
from chupa.git import Git
from chupa.seams import FileSystem, LocalFileSystem, SubprocessExec
from eval.shakeout.bench import Bench

GROUPS: tuple[str, ...] = ("stages", "driver")


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
    return importlib.import_module(f"eval.shakeout.{group}").MEMBERS


async def run_member(member: Member, root: Path) -> ShakeoutEntry:
    bench = Bench(root / member.id)
    await bench.initialize()
    observation = await member.run(bench)
    violations = audit(bench.segments())
    lines = [f"{v.invariant}: {v.ticket or '-'}: {v.detail}" for v in violations]
    return ShakeoutEntry(member=member.id, group=member.group, planted_fault=member.planted_fault,
                         expected=member.expected, observed=observation.observed,
                         producing_run=observation.producing_run, auditor=lines,
                         green=observation.observed == member.expected and not lines)


async def produce(group: str, prior: ShakeoutReport | None, root: Path) -> ShakeoutReport:
    if group not in GROUPS:
        raise ValueError(f"unknown group {group}")
    preceding = GROUPS[:GROUPS.index(group)]
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
    git = Git(SubprocessExec(), env=os.environ, timeout=30.0)
    sha = await git.rev_parse(Path.cwd(), "HEAD")
    return ShakeoutReport(produced_by_spec_version=SHAKEOUT_SPEC_VERSION,
                          produced_at_sha=sha, entries=entries)


def write_report(path: Path, report: ShakeoutReport, fs: FileSystem | None = None) -> None:
    (fs or LocalFileSystem()).write(path, (report.model_dump_json(indent=2) + "\n").encode())


async def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", required=True)
    parser.add_argument("--prior", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.group not in GROUPS:
        return 2
    prior = ShakeoutReport.model_validate_json(args.prior.read_bytes()) if args.prior else None
    try:
        with tempfile.TemporaryDirectory() as dirname:
            report = await produce(args.group, prior, Path(dirname))
    except ShakeoutRefused:
        return 1
    write_report(args.out, report)
    return 0


def main(argv: list[str] | None = None) -> int:
    return asyncio.run(_main(argv))


if __name__ == "__main__":
    raise SystemExit(main())
