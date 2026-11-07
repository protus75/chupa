"""The CLI module entry: `uv run python -m chupa <verb>`.

The composition root: the only place real seams are constructed. Exit 2 is an engine-plane refusal.
"""

import argparse
import asyncio
import json
import os
import re
import signal
import subprocess
import sys
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence, Set
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import yaml

from chupa import ask, control, drain, hostfiles, requisition, runner, serve, triage
from chupa.config import ConfigError, ConfigSnapshot, load_config, migrate_config
from chupa.daemon import DaemonCore, PauseConsumer, StartupBoundary, daemon_core
from chupa.git import Git, GitError
from chupa.journal import EventType, Journal, JournalCorruption
from chupa.lockfile import Lockfile, LockHeld
from chupa.notify import NOTIFY_TIMEOUT_S, NotificationReconciler
from chupa.providers import ProviderLLM, ProviderSession, ProviderSetupError, child_env, routed_conduct_paths
from chupa.redact import Redactor
from chupa.restart import Restart
from chupa.seams import Clock, CommandNotifications, ExecutableNotFound, LocalFileSystem, ProcessExec, SubprocessExec
from chupa.status import SETTLED, last_states, project, reject_queue, render
from chupa.storm import StormLedger
from chupa.tickets import (
    IntakeRefused,
    Ticket,
    TicketInvalid,
    _intake_claims,
    _load_frontmatter,
    _pending,
    _porcelain,
    evidence_findings,
    missing_evidence_findings,
    order,
    split_frontmatter,
    stem_findings,
    template,
    ticket_path,
    validate_ticket,
)
from chupa.timers import Timers

GIT_TIMEOUT_S = 30.0


def _clock() -> datetime:
    return datetime.now(UTC)


def build_control(checkout: runner.Checkout) -> PauseConsumer:
    """Compose without reading requests, publishing discovery, or starting tasks."""
    from chupa.daemon import storm_producer

    box = storm_producer(root=checkout.config.state_dir / "box", fs=checkout.fs, journal=checkout.journal, clock=checkout.clock)
    consumer = PauseConsumer(
        journal=checkout.journal,
        lifecycle_id=uuid4().hex,
        state_dir=checkout.config.state_dir,
        fs=checkout.fs,
        sleep=checkout.sleep,
        files=lambda: (checkout.config.state_dir / "control/inbox").glob("*"),
        read=Path.read_bytes,
        recover=box.recover,
        storm_holds=StormLedger(journal=checkout.journal, clock=checkout.clock).holds,
    )
    timers = Timers(journal=checkout.journal, clock=checkout.clock, sleep=checkout.sleep)
    consumer.providers = ProviderSession(checkout.config, journal=checkout.journal, clock=checkout.clock, sleep=checkout.sleep, timers=timers)
    consumer.load_config = lambda: load_config(None, cwd=checkout.repo)
    return consumer


def build_daemon_core(
    checkout: runner.Checkout,
    *,
    config_path: Path | None = None,
    read: Callable[[str], str | None],
    debounce: float,
    quarantined: Callable[[], Set[str]],
    drought_parked: Callable[[], Set[str]],
    completed_unmerged: Callable[[], int],
    prepare: Callable[[runner.Checkout], Awaitable[runner.Dispatch]] = runner.prepare_pipeline,
) -> DaemonCore:
    """Compose the production core without starting consumers or preparing a dispatch."""
    consumer = checkout.control or build_control(checkout)
    consumer.load_config = lambda: load_config(config_path, cwd=checkout.repo)
    checkout = replace(checkout, control=consumer)

    def bind(snapshot: ConfigSnapshot) -> runner.Dispatch:
        local = replace(checkout, config=snapshot)

        async def dispatch(ticket: Ticket) -> str:
            callback = await prepare(local)
            tier, _ = runner.capability(ticket, checkout.journal.read())
            drought = consumer.providers.drought(snapshot, tier, "implement") if consumer.providers.active else None
            if drought:
                consumer.providers.park(ticket.stem, drought)
                core.scheduler.update(ticket)
                return "infra_error"
            result = await callback(ticket)
            history = checkout.journal.read()
            body = next((e.body for e in reversed(history) if e.type == "state_transition" and e.ticket == ticket.stem), {})
            if "provider_drought" in body:
                core.scheduler.update(ticket)
            return result

        return dispatch

    core = daemon_core(
        checkout.repo,
        journal=checkout.journal,
        load=lambda: load_config(config_path, cwd=checkout.repo),
        bind=bind,
        read=read,
        ticket_sha=lambda stem: checkout.git.rev_parse(checkout.repo, f"HEAD:tickets/{stem}/ticket.md"),
        clock=checkout.clock,
        sleep=checkout.sleep,
        debounce=debounce,
        quarantined=quarantined,
        drought_parked=drought_parked,
        completed_unmerged=completed_unmerged,
        max_unmerged=checkout.config.scheduler.max_unmerged,
        before_dispatch=consumer.checkpoint,
        control=consumer,
    )
    timers = consumer.providers.timers
    restart = Restart(checkout, timers=timers, owned=lambda: core.admission.active is not None or core.admission.task is not None)
    core.admission.restart = restart
    core.admission._before_dispatch = StartupBoundary(restart, consumer).checkpoint

    def provider_holds():
        held = set(drought_parked())
        latest = {}
        for event in checkout.journal.read():
            if event.type == "state_transition" and event.ticket is not None:
                latest[event.ticket] = event.body
        for stem, body in latest.items():
            if route := body.get("provider_drought"):
                snapshot = load_config(config_path, cwd=checkout.repo)
                if consumer.providers.drought(snapshot, route["tier"], route["surface"]):
                    held.add(stem)
        return held

    core.scheduler.drought_parked = provider_holds
    return core


def build_serve(checkout: runner.Checkout, *, config_path=None, read=None, stems=None, prepare=runner.prepare_pipeline, signals=None, failure=None, argv=("serve",), reexec=None) -> serve.Serve:
    """Compose filesystem delivery at the same root as every other real seam."""

    def read_ticket(stem):
        path = checkout.repo / ticket_path(stem)
        return path.read_text() if path.is_file() else None

    return serve.Serve(
        checkout,
        config_path=config_path,
        read=read or read_ticket,
        stems=stems or (lambda: (p.parent.name for p in (checkout.repo / "tickets").glob("*/ticket.md"))),
        prepare=prepare,
        signals=signals,
        failure=failure,
        argv=argv,
        reexec=reexec,
    )


def build_notifications(checkout: runner.Checkout, *, config_path: Path | None, log) -> NotificationReconciler:
    executor = SubprocessExec()  # Never alias active work or the self-upgrade handoff.

    def compose(config):
        return CommandNotifications(executor, cwd=checkout.repo, env=child_env(checkout.env, config, serving=None), timeout=NOTIFY_TIMEOUT_S, scrub=Redactor.from_config(config, checkout.env).scrub)

    return NotificationReconciler(
        journal=checkout.journal, clock=checkout.clock, config_path=config_path or checkout.repo / "config.yaml", load=lambda: load_config(config_path, cwd=checkout.repo), compose=compose, log=log
    )


def watchdog_observation(workspace: Path, fence):
    from chupa.watchdog import ScopeObservation

    def snapshot():
        files = {}
        for prefix in fence:
            path = workspace / prefix
            paths = path.rglob("*") if path.is_dir() else (path,)
            for candidate in paths:
                if candidate.is_file():
                    files[candidate.relative_to(workspace).as_posix()] = candidate.read_bytes()
        return files

    return ScopeObservation(fence, snapshot)


def watchdog_notifications(config, env, effects, log, *, redactor, cwd, **context):
    from chupa.notify import WatchdogNotifications

    return WatchdogNotifications(
        effects=effects,
        notifications=CommandNotifications(SubprocessExec(), cwd=cwd, env=child_env(env, config, serving=None), timeout=NOTIFY_TIMEOUT_S, scrub=redactor.scrub),
        argv=config.notify,
        log=log,
        **context,
    )


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m chupa", description="Host run guide: docs/host-running.md")
    ap.add_argument("--config", type=Path, help="config path (default: config.yaml at the checkout root)")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("watch", help="read-only live engine view").add_argument("--once", action="store_true")
    sub.add_parser("snapshot", help="read-only JSON snapshot")
    sub.add_parser("status", help="project current state from the journal (read-only)")
    stats = sub.add_parser("stats", help="project journal health over a window (read-only)")
    stats.add_argument("--window", default="7d")
    stats.add_argument("--json", action="store_true")
    sub.add_parser("lint", help="validate tickets without running or writing anything").add_argument("stems", nargs="*")
    sub.add_parser("retro", help="force a retro report under the writer lock")
    sub.add_parser("doctor", help="inspect setup without changing state")
    sub.add_parser("core", help="refresh managed conduct in every routed agent's root file")
    prompt = sub.add_parser("prompt", help="render an operator prompt for a ticket")
    prompt.add_argument("kind", choices=ask.KINDS)
    prompt.add_argument("stem")
    sub.add_parser("migrate-config", help="validate and migrate schema_version: 0 to the current config schema")
    for verb in ("pause", "resume"):
        sub.add_parser(verb, help=f"submit {verb} to the running engine, or do nothing under the idle lock")
    sub.add_parser("kill", help="submit kill to the running engine; refuse when nothing is running")
    sub.add_parser("stop", help="finish the running ticket, admit nothing new, then exit")
    sub.add_parser("review", help="review a committed ticket under the lock").add_argument("stem")
    sub.add_parser("triage", help="make one sequential pass over pending suggestions under the lock")
    covgate = sub.add_parser("covgate", help="check a coverage JSON report against thresholds")
    covgate.add_argument("--gate", type=Path, default=Path("test-gate.toml"))
    covgate.add_argument("--report", type=Path, default=Path("coverage.json"))
    covgate.add_argument("command", nargs=argparse.REMAINDER)
    new = sub.add_parser("new", help="template tickets/<stem>/ticket.md and lint it")
    new.add_argument("stem")
    new.add_argument("--kind", choices=("feature", "bug", "chore"), default="feature")
    ordering = sub.add_parser("order", help="edit a ticket's priority or ordering")
    ordering.add_argument("stem")
    ordering.add_argument("--priority", choices=("P0", "P1", "P2", "P3"))
    ordering.add_argument("--runs-before", nargs="*", metavar="STEM")
    run = sub.add_parser("run", help="drive one ticket through intake and the stage pipeline under the lock")
    run.add_argument("stem")
    for verb in ("confirm", "reject"):
        verdict = sub.add_parser(verb, help=f"{verb} a draft or Reject item; publish the verdict to a running serve holding the lock")
        verdict.add_argument("stem")
        verdict.add_argument("--yes", action="store_true")
    dr = sub.add_parser("drain", help="run every eligible ticket to quiescence under the lock")
    dr.add_argument("--parked", action="append", default=[], metavar="STEM", help="a stem the handing-off parent drain parked (set by the self-upgrade re-exec)")
    dr.add_argument("--stop-lifecycle", help=argparse.SUPPRESS)
    sub.add_parser("serve", help="run the foreground daemon until kill, stop, or a signal stops it")
    return ap


def main(
    argv: Sequence[str] | None = None,
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    clock: Clock = _clock,
    pipeline: runner.Pipeline = runner.pipeline,
    reexec: ProcessExec | None = None,
    terminal: tuple[Callable[[], bool], Callable[[str], str]] | None = None,
) -> int:
    invocation = list(argv) if argv is not None else sys.argv[1:]
    args = _parser().parse_args(invocation)
    repo = Path(cwd) if cwd is not None else Path.cwd()
    env = dict(os.environ) if env is None else env
    try:
        if args.verb in {"confirm", "reject"}:
            isatty, read_input = terminal if terminal is not None else (sys.stdin.isatty, input)
            if not args.yes and not isatty():
                raise runner.Refusal("verdict requires an interactive terminal", "a human runs this in a terminal: ./dev.py confirm|reject <stem>")
        if args.verb == "migrate-config":
            migrate_config(args.config, cwd=repo, fs=LocalFileSystem())
            return 0
        if args.verb == "covgate":
            from chupa.covgate import run_gate

            if len(args.command) < 2 or args.command[0] != "--":
                print("chupa covgate: name the unit-test command after --", file=sys.stderr)
                return 2
            command = args.command[1:]
            # ProcessExec starts a new session, orphaning the test run when Check kills
            # covgate's group on timeout; inheriting the group carries the kill to it.
            try:
                return run_gate(command, gate_path=repo / args.gate, report_path=repo / args.report, run=lambda argv: subprocess.run(argv, cwd=repo, env=env).returncode)
            except FileNotFoundError:
                print(f"chupa covgate: {command[0]} not found -- install it or correct the command after --", file=sys.stderr)
                return 2
        if args.verb == "new":
            return _new(repo, args.stem, args.kind)
        if args.verb == "doctor":
            from chupa import doctor

            results = asyncio.run(doctor.check(repo=repo, config_path=args.config, env=env, exec_=SubprocessExec(), clock=clock, in_venv=sys.prefix != sys.base_prefix))
            print(doctor.render(results), end="")
            return 0 if all(r.passed for r in results) else 2
        config = load_config(args.config, cwd=repo)
        if args.verb == "core":
            hostfiles.refresh(routed_conduct_paths(config, repo), LocalFileSystem())
            return 0
        if args.verb == "prompt":
            if findings := stem_findings(args.stem):
                raise runner.Refusal(findings[0].message, findings[0].paved_road)
            if not (repo / ticket_path(args.stem)).is_file():
                raise runner.Refusal(f"{ticket_path(args.stem)} does not exist", f"author it with chupa new {args.stem}")
            print(ask.render(args.kind, args.stem, config, repo), end="")
            return 0
        exec_ = SubprocessExec()
        checkout = runner.Checkout(
            repo=repo,
            config=config,
            env=env,
            exec_=exec_,
            git=Git(exec_, env={**child_env(env, config), **({"GIT_OPTIONAL_LOCKS": "0"} if args.verb in {"lint", "watch", "snapshot"} else {})}, timeout=GIT_TIMEOUT_S),
            journal=Journal(config.state_dir, clock),
            fs=LocalFileSystem(),
            clock=clock,
        )
        if args.verb in {"watch", "snapshot"}:
            from chupa import observe

            context = observe.Context(repo.resolve(), config.state_dir.resolve(), (args.config or repo / "config.yaml").resolve(), exec_, checkout.git, child_env(env, config))
            if args.verb == "snapshot":
                print(json.dumps(observe.snapshot(context)))
            elif args.once:
                print(observe.text_snapshot(context))
            else:
                try:
                    while True:
                        print("\033[2J\033[H" + observe.text_snapshot(context), flush=True)
                        time.sleep(3)
                except KeyboardInterrupt:
                    pass
            return 0
        if args.verb == "stats":
            from chupa.stats import render_stats, window_start

            events = checkout.journal.read()
            now = checkout.clock()
            try:
                window_start(events, now, args.window)
            except ValueError as exc:
                print(f"chupa stats: {exc}", file=sys.stderr)
                return 2
            result = asyncio.run(_stats(checkout, events, now, args.window))
            print(json.dumps(result) if args.json else render_stats(result), end="\n" if args.json else "")
            return 0
        if args.verb == "lint":
            return asyncio.run(_lint(checkout, args.stems))
        if args.verb == "order":
            return _order(checkout, args.stem, args.priority, args.runs_before)
        if args.verb == "status":
            print(render(asyncio.run(_status(checkout))), end="")
            return 0
        if args.verb in {"pause", "resume", "kill", "stop"}:
            return asyncio.run(_control(checkout, args.verb))
        if args.verb in {"confirm", "reject"}:
            return asyncio.run(_verdict(checkout, args.stem, args.verb, read_input, args.yes))
        if args.verb == "review":
            return asyncio.run(_review(checkout, args.stem))
        if args.verb == "triage":

            async def one_pass() -> list[tuple[str, str]]:
                lock = Lockfile(config.state_dir, instance_id=await checkout.git.describe(repo), clock=clock)
                lock.acquire()
                session = build_control(checkout).providers
                try:
                    llm = ProviderLLM(config, exec_=exec_, fs=checkout.fs, env=env, cwd=repo, timeout=runner.call_timeout(config), session=session)
                    session.timers.reconstruct()
                    session.timers.fire_due()
                    problems = await llm.preflight() if session.active else []
                    if problems:
                        raise ProviderSetupError("; ".join(problems))
                    return await triage.triage_pass(checkout, llm)
                finally:
                    try:
                        await session.close()
                    finally:
                        lock.release()

            lines = asyncio.run(one_pass())
            print("\n".join(line for _, line in lines) if lines else "no pending suggestions")
            return 0
        if args.verb == "serve":
            return asyncio.run(serve.serve(checkout, config_path=args.config, signals=_serve_signals, argv=invocation, reexec=reexec or SubprocessExec()))
        checkout = replace(checkout, control=build_control(checkout))
        checkout.control.load_config = lambda: load_config(args.config, cwd=repo)
        dispatch = pipeline(checkout)
        if args.verb == "retro":
            return asyncio.run(_retro(checkout, dispatch))
        if args.verb == "drain":
            from chupa.retro import Retro

            class DrainDispatch:
                _retro = Retro(checkout, dispatch)

                async def __call__(self, ticket):
                    return await dispatch(ticket)

                def __getattr__(self, name):
                    return getattr(dispatch, name)

            # The handoff uses its own process seam.
            report = asyncio.run(
                drain.drain(
                    checkout,
                    DrainDispatch(),
                    reexec=reexec or SubprocessExec(),
                    parked=args.parked,
                    stop_lifecycle=args.stop_lifecycle,
                    argv=(["--config", str(args.config)] if args.config else []) + ["drain"],
                )
            )
            if report.handoff is None:
                print(report.render(), end="")
            return report.exit_code
        return asyncio.run(runner.run_ticket(args.stem, checkout, dispatch))
    except (ConfigError, runner.Refusal, LockHeld, IntakeRefused, JournalCorruption, ProviderSetupError, ExecutableNotFound, hostfiles.MarkerCorruption) as e:
        road = " -- repair the selected config and retry retro" if args.verb == "retro" and isinstance(e, ConfigError) else ""
        print(f"chupa {args.verb}: {e}{road}", file=sys.stderr)
        return runner.EXIT_REFUSED


async def _review(checkout: runner.Checkout, stem: str) -> int:
    from chupa.driver import Driver
    from chupa.effects import Effects
    from chupa.tickets import intake

    if findings := stem_findings(stem):
        raise runner.Refusal(findings[0].message, findings[0].paved_road)
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    lock.acquire()
    try:
        result = await intake(checkout.repo, checkout.git, checkout.journal, checkout.fs)
        if refused := result.refused.get(stem):
            raise runner.Refusal(f"{ticket_path(stem)} failed intake: " + "; ".join(f.message for f in refused), f"fix the ticket and retry `review {stem}`")
        path = checkout.repo / ticket_path(stem)
        if not path.is_file():
            raise runner.Refusal(f"{ticket_path(stem)} does not exist", f"author the ticket before `review {stem}`")
        history = checkout.journal.read()
        states = last_states(history)
        if states.get(stem) in SETTLED | {"rejected"}:
            raise runner.Refusal(f"{stem} is settled or rejected", "author follow-up work as a new ticket")
        text = await checkout.git._run(checkout.repo, "show", f"main:{ticket_path(stem)}")
        try:
            ticket = validate_ticket(stem, text, checkout.repo)
        except TicketInvalid as exc:
            raise runner.Refusal(f"{ticket_path(stem)} is invalid: " + "; ".join(f.message for f in exc.findings), f"fix the ticket and retry `review {stem}`") from None
        if unmerged := [dep for dep in ticket.depends if states.get(dep) != "merged"]:
            raise runner.Refusal(f"{stem} depends on unmerged {', '.join(unmerged)}", f"review {stem} after {', '.join(unmerged)} merge")
        session = build_control(checkout).providers
        try:
            llm = ProviderLLM(checkout.config, exec_=checkout.exec_, fs=checkout.fs, env=checkout.env, cwd=checkout.repo, timeout=runner.call_timeout(checkout.config), session=session)
            session.timers.reconstruct()
            session.timers.fire_due()
            problems = await llm.preflight() if session.active else []
            if problems:
                raise ProviderSetupError("; ".join(problems))
            driver = Driver.from_config(checkout.config, llm=llm, env=checkout.env, clock=checkout.clock, sleep=checkout.sleep, fs=checkout.fs)
            driver.journal = checkout.journal
            driver.effects = Effects(checkout.journal)
            verdict = await requisition.review_ticket(
                driver,
                repo=checkout.repo,
                stem=stem,
                text=text,
                specs_dir=runner.SPECS_DIR,
                tier=checkout.config.routing_default_tier,
                stem_slot=f"review-{stem}",
                run_seq=len(history),
                attempt=0,
                call_seq=1,
                expected_budget="surface",
            )
        finally:
            await session.close()
        checkout.journal.append(
            EventType.SIGNAL,
            {"signal": "requisition_verdict", "verdict": verdict.verdict, "ticket_sha": verdict.ticket_sha, "provider": verdict.provider, "model": verdict.model, "spec_version": verdict.spec_version},
            ticket=stem,
        )
        print(f"review {stem}: {verdict.verdict} -- {verdict.summary}")
        for finding in verdict.findings:
            location = f" {finding.path}:{finding.line}" if finding.path and finding.line is not None else f" {finding.path}" if finding.path else ""
            print(f"- [{finding.code}]{location} {finding.message} ({finding.paved_road})")
        return 0 if verdict.verdict == "approve" else 1
    finally:
        lock.release()


async def _retro(checkout, dispatch):
    from chupa.retro import Retro, RetroConstructionError, measurements, project_window, suppressing_failure

    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    lock.acquire()
    try:
        try:
            window = project_window(checkout.journal.read())
        except JournalCorruption as exc:
            raise runner.Refusal(str(exc), "restore journal readability from backup and retry retro") from None
        selected = bool(measurements(window)["merged_count"])
        suppressed = suppressing_failure(window) is not None
        if selected and not suppressed and hasattr(dispatch, "prepare"):
            await dispatch.prepare()
        try:
            result = await Retro(checkout, dispatch)(forced=True)
        except RetroConstructionError as exc:
            raise runner.Refusal("retro Driver unavailable", str(exc)) from None
        if not selected:
            print("retro: no merge since the latest completed report")
            return 0
        if result is not None:
            print(f"retro: committed tickets/retro/{window.sequence:06d}.md")
            return 0
        print("retro: no report committed; inspect status and the Suggestion Box")
        return 1
    finally:
        try:
            await checkout.control.providers.close()
        finally:
            lock.release()


async def _lint(checkout: runner.Checkout, stems: Sequence[str]) -> int:
    root = checkout.repo / "tickets"
    valid = total = 0
    exit_code = 0
    try:
        entries = list(root.iterdir())  # Unlike glob, unreadable directories must refuse.
        selected = list(dict.fromkeys(stems)) if stems else sorted(p.name for p in entries if (p / "ticket.md").is_file())
        states = last_states(checkout.journal.read())
        pending = _pending(checkout.repo, _porcelain(await checkout.git.status_porcelain(checkout.repo)))
        for stem in selected:
            rel = ticket_path(stem)
            path = checkout.repo / rel
            # Check existence before the stem grammar, without following an escaped path.
            inside = Path(stem).name == stem and stem not in {".", ".."} and path.resolve().is_relative_to(root.resolve())
            if not inside or not path.is_file():
                print(f"{rel}: no ticket file (create tickets/<stem>/ticket.md with chupa new <stem>)")
                total += 1
                exit_code = 2
                continue
            if states.get(stem) in SETTLED | {"rejected"}:
                continue
            total += 1
            text, findings = _intake_claims(stem, path.read_text(), pending.get(stem, False))
            try:
                if findings:
                    raise TicketInvalid(findings)
                ticket = validate_ticket(stem, text, checkout.repo)
                paths = await checkout.git._run(checkout.repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", f"tickets/{stem}/evidence/")
                findings = evidence_findings(ticket, checkout.repo, paths=paths.split("\0"))
            except TicketInvalid as exc:
                findings = exc.findings
            for finding in findings:
                message = " ".join(finding.message.splitlines())
                road = " ".join(finding.paved_road.splitlines())
                print(f"{finding.path or rel}: {message} ({road})")
            if findings:
                exit_code = max(exit_code, 1)
            else:
                valid += 1
    except (OSError, UnicodeError, GitError) as exc:
        print(f"{root}: {exc} (restore ticket and repository readability, then retry chupa lint)")
        exit_code = 2
    print(f"lint: {valid}/{total} tickets valid")
    return exit_code


async def _stats(checkout, events, now, window):
    from chupa.stages import Invoice
    from chupa.stats import project_stats, window_start

    start = window_start(events, now, window)
    kinds = {}
    for stem in {e.ticket for e in events if e.ticket}:
        try:
            split = split_frontmatter((checkout.repo / ticket_path(stem)).read_text())
            data = yaml.safe_load(split[0]) if split else None
            if isinstance(data, dict) and data.get("kind") in {"feature", "bug", "chore"}:
                kinds[stem] = data["kind"]
        except OSError, UnicodeError, yaml.YAMLError:
            pass
    checks = {}
    for e in events:
        if e.type == EventType.EFFECT_COMPLETION and e.ticket and re.fullmatch(r"ticket-plane/[^/]+/\d+/checks", e.key or "") and start <= datetime.fromisoformat(e.ts) <= now:
            text = await checkout.git._run(checkout.repo, "show", f"{e.body['result']['commit']}:tickets/{e.ticket}/checks.json")
            checks[e.key] = Invoice.model_validate_json(text)
    return project_stats(events, kinds, checks, now=now, window=window)


async def _status(checkout: runner.Checkout):
    from chupa.box import BOX_DIR, Box, RereportJournal
    from chupa.retro import production_evidence, project_window
    from chupa.specs import load_spec

    events = checkout.journal.read()
    window = project_window(events)
    await production_evidence(window, checkout)
    spec = load_spec((runner.SPECS_DIR / "retro.md").read_text())
    provenance = {"head": await checkout.git.rev_parse(checkout.repo, "HEAD"), "spec_version": spec.meta.version, "at": checkout.clock().isoformat()}
    return project(
        events, window=window, provenance=provenance, box=Box(checkout.config.state_dir / BOX_DIR, checkout.fs, rereport=RereportJournal(checkout.journal)), policy=checkout.config.box_policy
    )


def _serve_signals(stop: Callable[[], None]) -> Callable[[], None]:
    """Real signal delivery is composed here, alongside the other operating-system seams."""
    loop = asyncio.get_running_loop()
    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
    for sig in previous:
        loop.add_signal_handler(sig, stop)

    def restore() -> None:
        for sig, handler in previous.items():
            loop.remove_signal_handler(sig)
            signal.signal(sig, handler)

    return restore


async def _control(checkout: runner.Checkout, verb: str) -> int:
    lock = Lockfile(checkout.config.state_dir, instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    try:
        lock.acquire()
    except LockHeld:
        try:
            lifecycle, hold = control.read_active(checkout.config.state_dir, Path.read_bytes)
        except ValueError as exc:
            raise runner.Refusal("current control identity unavailable", str(exc)) from exc
        if verb == "resume" and hold is None:
            raise runner.Refusal("no current hold identity", "read the running engine's current control identity and submit a new request")
        request = control.ControlRequest(uuid4().hex, lifecycle, verb, hold if verb == "resume" else None)
        control.publish_request(checkout.config.state_dir, request, checkout.fs)
        print(f"{verb} submitted: {request.request_id}")
    else:
        try:
            if verb == "kill":
                raise runner.Refusal("nothing running to kill", "start a drain before submitting kill")
            if verb == "stop":
                raise runner.Refusal("nothing running to stop", "start a drain or serve before submitting stop")
            print(f"nothing running to {verb}")
        finally:
            lock.release()
    return 0


async def _verdict(checkout, stem, verb, read_input, yes):
    if findings := stem_findings(stem):
        raise runner.Refusal(findings[0].message, findings[0].paved_road)
    history = checkout.journal.read()
    queued = reject_queue(history).get(stem)
    path = checkout.repo / ticket_path(stem)
    if queued is not None:
        preview = f"Reject queue: {queued.get('to', 'unknown')} -- {queued.get('reason', 'reason unavailable')}"
    elif path.is_file():
        split = split_frontmatter(path.read_text())
        data, errors = _load_frontmatter(split[0], str(path)) if split else (None, [True])
        if errors:
            raise runner.Refusal(f"{ticket_path(stem)} has invalid frontmatter", "fix the ticket and retry the verdict")
        preview = f"ticket state: {data.get('state', 'unknown')}"
    else:
        preview = "no ticket file"
    print(f"{stem}: {preview}")
    try:
        answer = "y" if yes else read_input(f"{verb} {stem}? [y/N] ")
    except EOFError:
        answer = ""
    if answer.strip().lower() not in {"y", "yes"}:
        print("verdict aborted")
        return 1
    try:
        return await runner.verdict(stem, checkout, kill=verb == "reject")
    except LockHeld:
        pass
    try:
        lifecycle, _ = control.read_active(checkout.config.state_dir, Path.read_bytes)
    except ValueError as exc:
        raise runner.Refusal("current control identity unavailable", str(exc)) from exc
    request = control.AdmissionRequest(uuid4().hex, lifecycle, verb, stem, None, "operator")
    control.publish_request(checkout.config.state_dir, request, checkout.fs)
    print(f"{verb} submitted: {request.request_id} -- ./dev.py status shows the outcome")
    return 0


def _order(checkout, stem, priority, runs_before):
    if findings := stem_findings(stem):
        raise runner.Refusal(findings[0].message, findings[0].paved_road)
    if priority is None and runs_before is None:
        raise runner.Refusal("no ordering option supplied", "supply --priority or --runs-before")
    path = checkout.repo / ticket_path(stem)
    if not path.is_file():
        raise runner.Refusal(f"{ticket_path(stem)} does not exist", f"author it with chupa new {stem}")
    state = last_states(checkout.journal.read()).get(stem)
    if state == "running":
        raise runner.Refusal(f"{stem} is running; editing a ticket during its run stops it with ticket_changed", "reorder it after the run ends")
    if state in SETTLED | {"rejected"}:
        raise runner.Refusal(f"{stem} is {state}", "author follow-up work as a new ticket")
    text = path.read_bytes().decode()
    try:
        try:
            changed = order(text, priority=priority, runs_before=runs_before)
        except ValueError, StopIteration:
            validate_ticket(stem, text, checkout.repo)
            raise runner.Refusal("ticket ordering fields cannot be edited", "use ordinary priority and section headings, then retry order") from None
        ticket = validate_ticket(stem, changed, checkout.repo)
        if priority is not None and ticket.frontmatter.priority != priority:
            raise runner.Refusal("priority line cannot be edited", "write priority as a plain `priority: P2` line, then retry order")
    except TicketInvalid as exc:
        finding = exc.findings[0]
        raise runner.Refusal(finding.message, finding.paved_road) from None
    checkout.fs.write(path, changed.encode())
    fields = ([f"priority: {priority}"] if priority is not None else []) + ([f"runs before: {', '.join(runs_before) or '(cleared)'}"] if runs_before is not None else [])
    print(f"ordered {stem}: {'; '.join(fields)}")
    return 0


def _new(repo: Path, stem: str, kind: str = "feature") -> int:
    """Author the ticket file only: authorship is outside the lock fence; intake commits it on the next run."""
    if findings := stem_findings(stem):
        raise runner.Refusal(findings[0].message, findings[0].paved_road)
    rel = ticket_path(stem)
    if (repo / rel).exists():
        raise runner.Refusal(f"{rel} already exists", "edit it in place, or pick a new stem")
    text = template(kind)
    LocalFileSystem().write(repo / rel, text.encode())
    print(f"authored {rel}")
    findings = []
    try:
        ticket = validate_ticket(stem, text, repo)
        findings = evidence_findings(ticket, repo)
    except TicketInvalid as e:
        findings = e.findings
        if kind == "bug":
            findings += missing_evidence_findings(stem, repo)
    if findings:
        print(f"fill these before `run {stem}`:")
        for f in findings:
            print(f"- {f.message} ({f.paved_road})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
