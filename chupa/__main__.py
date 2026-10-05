"""The CLI module entry (CHUPA_PLAN.md section 18): `uv run python -m chupa <verb>`.

The composition root: the only place real seams are constructed. Exit 2 is an engine-plane refusal.
"""

import argparse
import asyncio
import os
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

from chupa import runner
from chupa.config import ConfigError, load_config
from chupa.git import Git
from chupa.journal import Journal, JournalCorruption
from chupa.lockfile import LockHeld
from chupa.providers import ProviderSetupError, child_env
from chupa.seams import Clock, LocalFileSystem, SubprocessExec
from chupa.status import project, render
from chupa.tickets import IntakeRefused, TicketInvalid, stem_findings, template, ticket_path, validate_ticket

GIT_TIMEOUT_S = 30.0


def _clock() -> datetime:
    return datetime.now(UTC)


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m chupa")
    ap.add_argument("--config", type=Path, help="config path (default: config.yaml at the checkout root)")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("status", help="project current state from the journal (read-only)")
    new = sub.add_parser("new", help="template tickets/<stem>/ticket.md and lint it")
    new.add_argument("stem")
    run = sub.add_parser("run", help="drive one ticket through intake and the stage pipeline under the lock")
    run.add_argument("stem")
    return ap


def main(
    argv: Sequence[str] | None = None,
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    clock: Clock = _clock,
    pipeline: runner.Pipeline = runner.pipeline,
) -> int:
    args = _parser().parse_args(argv)
    repo = Path(cwd) if cwd is not None else Path.cwd()
    env = dict(os.environ) if env is None else env
    try:
        if args.verb == "new":
            return _new(repo, args.stem)
        config = load_config(args.config, cwd=repo)
        if args.verb == "status":
            print(render(project(Journal(config.state_dir, clock).read())), end="")
            return 0
        exec_ = SubprocessExec()
        checkout = runner.Checkout(
            repo=repo, config=config, env=env, exec_=exec_,
            git=Git(exec_, env=child_env(env, config), timeout=GIT_TIMEOUT_S),
            journal=Journal(config.state_dir, clock), fs=LocalFileSystem(), clock=clock,
        )
        dispatch = pipeline(checkout)
        return asyncio.run(runner.run_ticket(args.stem, checkout, dispatch))
    except (ConfigError, runner.Refusal, LockHeld, IntakeRefused, JournalCorruption, ProviderSetupError) as e:
        print(f"chupa {args.verb}: {e}", file=sys.stderr)
        return runner.EXIT_REFUSED


def _new(repo: Path, stem: str) -> int:
    """Author the ticket file only: authorship is outside the lock fence; intake commits it on the next run."""
    if findings := stem_findings(stem):
        raise runner.Refusal(findings[0].message, findings[0].paved_road)
    rel = ticket_path(stem)
    if (repo / rel).exists():
        raise runner.Refusal(f"{rel} already exists", "edit it in place, or pick a new stem")
    text = template()
    LocalFileSystem().write(repo / rel, text.encode())
    print(f"authored {rel}")
    try:
        validate_ticket(stem, text, repo)
    except TicketInvalid as e:
        print(f"fill these before `run {stem}`:")
        for f in e.findings:
            print(f"- {f.message} ({f.paved_road})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
