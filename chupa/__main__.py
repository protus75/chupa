"""The CLI module entry (CHUPA_PLAN.md section 18): `uv run python -m chupa <verb>`.

The composition root: the only place real seams are constructed. Exit 2 is an engine-plane refusal.
"""

import argparse
import asyncio
import os
import sys
from collections.abc import Awaitable, Callable, Mapping, Sequence, Set
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from chupa import control, drain, runner, triage
from chupa.config import ConfigError, ConfigSnapshot, load_config
from chupa.daemon import DaemonCore, PauseConsumer, daemon_core
from chupa.daemon import StartupBoundary
from chupa.git import Git
from chupa.journal import Journal, JournalCorruption
from chupa.lockfile import LockHeld, Lockfile
from chupa.providers import ProviderLLM, ProviderSetupError, child_env
from chupa.restart import Restart
from chupa.seams import Clock, ExecutableNotFound, LocalFileSystem, ProcessExec, SubprocessExec
from chupa.status import project, render
from chupa.timers import Timers
from chupa.tickets import IntakeRefused, Ticket, TicketInvalid, stem_findings, template, ticket_path, validate_ticket

GIT_TIMEOUT_S = 30.0


def _clock() -> datetime:
    return datetime.now(UTC)


def build_control(checkout: runner.Checkout) -> PauseConsumer:
    """Compose without reading requests, publishing discovery, or starting tasks."""
    return PauseConsumer(journal=checkout.journal, lifecycle_id=uuid4().hex,
                         state_dir=checkout.config.state_dir, fs=checkout.fs, sleep=checkout.sleep,
                         files=lambda: (checkout.config.state_dir / "control/inbox").glob("*"),
                         read=Path.read_bytes)


def build_daemon_core(
    checkout: runner.Checkout, *, config_path: Path | None = None, plan: str | None,
    read: Callable[[str], str | None], debounce: float,
    quarantined: Callable[[], Set[str]], drought_parked: Callable[[], Set[str]],
    completed_unmerged: Callable[[], int],
    prepare: Callable[[runner.Checkout], Awaitable[runner.Dispatch]] = runner.prepare_pipeline,
) -> DaemonCore:
    """Compose the production core without starting consumers or preparing a dispatch."""
    consumer = build_control(checkout)
    checkout = replace(checkout, control=consumer)

    def bind(snapshot: ConfigSnapshot) -> runner.Dispatch:
        local = replace(checkout, config=snapshot)

        async def dispatch(ticket: Ticket) -> str:
            callback = await prepare(local)
            return await callback(ticket)

        return dispatch

    core = daemon_core(
        checkout.repo, journal=checkout.journal,
        load=lambda: load_config(config_path, cwd=checkout.repo), bind=bind, plan=plan, read=read,
        clock=checkout.clock, sleep=checkout.sleep, debounce=debounce,
        quarantined=quarantined, drought_parked=drought_parked,
        completed_unmerged=completed_unmerged, max_unmerged=checkout.config.scheduler.max_unmerged,
        before_dispatch=consumer.checkpoint, control=consumer,
    )
    timers = Timers(journal=checkout.journal, clock=checkout.clock, sleep=checkout.sleep)
    restart = Restart(checkout, timers=timers,
                      owned=lambda: core.admission.active is not None or core.admission.task is not None)
    core.admission.restart = restart
    core.admission._before_dispatch = StartupBoundary(restart, consumer).checkpoint
    return core


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m chupa")
    ap.add_argument("--config", type=Path, help="config path (default: config.yaml at the checkout root)")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("status", help="project current state from the journal (read-only)")
    for verb in ("pause", "resume"):
        sub.add_parser(verb, help=f"submit {verb} to the running engine, or do nothing under the idle lock")
    sub.add_parser("kill", help="submit kill to the running drain; refuse when nothing is running")
    sub.add_parser("triage", help="make one sequential pass over pending suggestions under the lock")
    new = sub.add_parser("new", help="template tickets/<stem>/ticket.md and lint it")
    new.add_argument("stem")
    run = sub.add_parser("run", help="drive one ticket through intake and the stage pipeline under the lock")
    run.add_argument("stem")
    for verb in ("confirm", "reject"):
        sub.add_parser(verb, help=f"{verb} a draft or Reject item under the lock").add_argument("stem")
    dr = sub.add_parser("drain", help="run every eligible ticket to quiescence under the lock")
    dr.add_argument("--parked", action="append", default=[], metavar="STEM",
                    help="a stem the handing-off parent drain parked (set by the self-upgrade re-exec)")
    return ap


def main(
    argv: Sequence[str] | None = None,
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    clock: Clock = _clock,
    pipeline: runner.Pipeline = runner.pipeline,
    reexec: ProcessExec | None = None,
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
        if args.verb in {"pause", "resume", "kill"}:
            return asyncio.run(_control(checkout, args.verb))
        if args.verb in {"confirm", "reject"}:
            return asyncio.run(runner.verdict(args.stem, checkout, kill=args.verb == "reject"))
        if args.verb == "triage":
            async def one_pass() -> list[tuple[str, str]]:
                lock = Lockfile(config.state_dir, instance_id=await checkout.git.describe(repo), clock=clock)
                lock.acquire()
                try:
                    llm = ProviderLLM(config, exec_=exec_, fs=checkout.fs, env=env,
                                      cwd=repo, timeout=runner.call_timeout(config))
                    return await triage.triage_pass(checkout, llm)
                finally:
                    lock.release()

            lines = asyncio.run(one_pass())
            print("\n".join(line for _, line in lines) if lines else "no pending suggestions")
            return 0
        checkout = replace(checkout, control=build_control(checkout))
        dispatch = pipeline(checkout)
        if args.verb == "drain":
            # The handoff's own seam instance, never shared with active work (section 15).
            report = asyncio.run(drain.drain(checkout, dispatch, reexec=reexec or SubprocessExec(),
                                             parked=args.parked))
            if report.handoff is None:
                print(report.render(), end="")
            return report.exit_code
        return asyncio.run(runner.run_ticket(args.stem, checkout, dispatch))
    except (ConfigError, runner.Refusal, LockHeld, IntakeRefused, JournalCorruption, ProviderSetupError,
            ExecutableNotFound) as e:
        print(f"chupa {args.verb}: {e}", file=sys.stderr)
        return runner.EXIT_REFUSED


async def _control(checkout: runner.Checkout, verb: str) -> int:
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo),
                    clock=checkout.clock)
    try:
        lock.acquire()
    except LockHeld:
        try:
            lifecycle, hold = control.read_active(checkout.config.state_dir, Path.read_bytes)
        except ValueError as exc:
            raise runner.Refusal("current control identity unavailable", str(exc)) from exc
        if verb == "resume" and hold is None:
            raise runner.Refusal("no current hold identity",
                                 "read the running engine's current control identity and submit a new request")
        request = control.ControlRequest(uuid4().hex, lifecycle, verb, hold if verb == "resume" else None)
        control.publish_request(checkout.config.state_dir, request, checkout.fs)
        print(f"{verb} submitted: {request.request_id}")
    else:
        try:
            if verb == "kill":
                raise runner.Refusal("nothing running to kill",
                                     "start a drain before submitting kill")
            print(f"nothing running to {verb}")
        finally:
            lock.release()
    return 0


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
