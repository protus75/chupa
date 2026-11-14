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

import chupa
from chupa import ask, control, drain, hostfiles, observe, reconcile, requisition, runner, seams, serve, triage
from chupa.box import UnknownBoxId
from chupa.config import ConfigError, ConfigSnapshot, load_config, migrate_config
from chupa.daemon import DaemonCore, PauseConsumer, StartupBoundary, daemon_core
from chupa.git import Git, GitError
from chupa.journal import EventType, Journal, JournalCorruption
from chupa.llm import LLMRequest
from chupa.lockfile import ENGINE_VERBS, CommitLock, CommitLockTimeout, Lockfile, LockHeld
from chupa.notify import NOTIFY_TIMEOUT_S, NotificationReconciler
from chupa.providers import ADAPTERS, PREFLIGHT_TIMEOUT_S, PROBE_PROMPT, ProviderLLM, ProviderSession, ProviderSetupError, child_env, routed_conduct_paths
from chupa.redact import Redactor
from chupa.restart import Restart
from chupa.seams import Clock, CommandNotifications, ExecutableNotFound, LocalFileSystem, ProcessExec, SubprocessExec
from chupa.status import last_states, lint_admission, order_admission, project, reject_queue, render, review_admission
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
    lint_findings,
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


async def _preflighted_llm(checkout: runner.Checkout, session: ProviderSession) -> ProviderLLM:
    llm = ProviderLLM(checkout.config, exec_=checkout.exec_, fs=checkout.fs, env=checkout.env, cwd=checkout.repo, timeout=runner.call_timeout(checkout.config), session=session)
    session.timers.reconstruct()
    session.timers.fire_due()
    problems = await llm.preflight() if session.active else []
    if problems:
        raise ProviderSetupError("; ".join(problems))
    return llm


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
        known=lambda stem: (checkout.repo / ticket_path(stem)).is_file() or any(e.ticket == stem for e in checkout.journal.read()),
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
    ap = argparse.ArgumentParser(prog="python -m chupa", description="Host guides: chupa docs")
    ap.add_argument("--config", type=Path, help="config path (default: config.yaml at the checkout root)")
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("watch", help="read-only live engine view").add_argument("--once", action="store_true")
    sub.add_parser("snapshot", help="read-only JSON snapshot")
    sub.add_parser("status", help="project current state from the journal (read-only)")
    stats = sub.add_parser("stats", help="project journal health over a window (read-only)")
    stats.add_argument("--window", default="7d")
    stats.add_argument("--json", action="store_true")
    stats.add_argument("--tree", action="store_true")
    sub.add_parser("lint", help="validate tickets without running or writing anything").add_argument("stems", nargs="*")
    sub.add_parser("retro", help="run a retro now, or queue one on the running engine")
    sub.add_parser("doctor", help="inspect setup without changing state")
    sub.add_parser("core", help="refresh managed conduct in every routed agent's root file")
    prompt = sub.add_parser("prompt", help="render an operator prompt for a ticket")
    prompt.add_argument("kind", choices=ask.KINDS)
    prompt.add_argument("stems", nargs="*")
    sub.add_parser("docs", help="print installed host guide paths")
    sub.add_parser("probe", help="probe declared providers").add_argument("providers", nargs="*")
    sub.add_parser("migrate-config", help="validate and migrate schema_version: 0 to the current config schema")
    for verb in ("pause", "resume"):
        sub.add_parser(verb, help=f"submit {verb} to the running engine, or do nothing under the idle lock")
    sub.add_parser("kill", help="submit kill to the running engine; refuse when nothing is running")
    sub.add_parser("stop", help="finish the running ticket, admit nothing new, then exit")
    sub.add_parser("review", help="review a committed ticket under the lock").add_argument("stem")
    sub.add_parser("suggest", help="queue an idea for triage").add_argument("summary")
    sub.add_parser("triage", help="make one sequential pass over pending suggestions under the lock").add_argument("ids", nargs="*")
    sub.add_parser("dismiss", help="dismiss box messages under the lock").add_argument("ids", nargs="+")
    sub.add_parser("covmap", help="build the coverage map")
    covgate = sub.add_parser("covgate", help="check a coverage JSON report against thresholds")
    covgate.add_argument("--gate", type=Path, default=Path("test-gate.toml"))
    covgate.add_argument("--report", type=Path, default=Path("coverage.json"))
    covgate.add_argument("command", nargs=argparse.REMAINDER)
    new = sub.add_parser("new", help="template tickets/<stem>/ticket.md and lint it")
    new.add_argument("stem")
    new.add_argument("--kind", choices=("feature", "bug", "chore"), default="feature")
    new.add_argument("--evidence", nargs="+", metavar="PATH")
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
        verdict.add_argument("--extension", action="store_true")
    dr = sub.add_parser("drain", help="run every eligible ticket to quiescence under the lock")
    dr.add_argument("--detach", action="store_true", help="run in its own session and append to <state_dir>/drain.out")
    dr.add_argument("--parked", action="append", default=[], metavar="STEM", help="a stem the handing-off parent drain parked (set by the self-upgrade re-exec)")
    dr.add_argument("--deadline", type=datetime.fromisoformat, default=None)
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
    spawn: Callable = seams.spawn_detached,
    terminal: tuple[Callable[[], bool], Callable[[str], str]] | None = None,
) -> int:
    invocation = list(argv) if argv is not None else sys.argv[1:]
    args = _parser().parse_args(invocation)
    repo = Path(cwd) if cwd is not None else Path.cwd()
    env = dict(os.environ) if env is None else env
    try:
        if args.verb in {"confirm", "reject"}:
            isatty, read_input = terminal if terminal is not None else (sys.stdin.isatty, input)
            if not (args.yes or args.extension) and not isatty():
                raise runner.Refusal("verdict requires an interactive terminal", "a human runs this in a terminal: ./dev.py confirm|reject <stem>")
        if args.verb == "docs":
            for name, purpose in (("authoring", "ticket authoring"), ("running", "host operation"), ("contract", "host contract"), ("qwen", "local qwen provider setup")):
                print(f"{Path(chupa.__file__).parent / 'docs' / f'host-{name}.md'}  {purpose}")
            return 0
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
            return _new(repo, args.stem, args.kind, args.evidence or ())
        if args.verb == "doctor":
            from chupa import doctor

            results = asyncio.run(doctor.check(repo=repo, config_path=args.config, env=env, exec_=SubprocessExec(), clock=clock, sleep=asyncio.sleep, in_venv=sys.prefix != sys.base_prefix))
            print(doctor.render(results), end="")
            return 0 if all(r.passed for r in results) else 2
        config = load_config(args.config, cwd=repo)
        if args.verb == "drain" and args.detach:
            output = config.state_dir / "drain.out"
            pid = spawn([sys.executable, "-m", "chupa", *(["--config", str(args.config)] if args.config else []), "drain"], cwd=repo, env=env, output=output)
            print(f"drain: pid {pid}, output {output}")
            return 0
        if args.verb == "probe":
            declared = {p.name: p for p in config.providers}
            unknown = set(args.providers) - declared.keys()
            if unknown:
                print(f"unknown providers: {', '.join(sorted(unknown))}; declared providers: {', '.join(declared)}", file=sys.stderr)
                return 2

            async def probe():
                failed = False
                exec_ = SubprocessExec()
                redactor = Redactor.from_config(config, env)
                for name in args.providers or declared:
                    provider = declared[name]
                    try:
                        if name not in ADAPTERS:
                            raise ProviderSetupError(f"provider {name!r} has no shipped cli adapter; name a provider one of {sorted(ADAPTERS)}")
                        adapter = ADAPTERS[name](
                            provider,
                            config=config,
                            exec_=exec_,
                            fs=LocalFileSystem(),
                            redactor=redactor,
                            env=env,
                            cwd=repo,
                            capture_dir=config.state_dir / "spools" / "probe",
                            timeout=PREFLIGHT_TIMEOUT_S,
                        )
                    except Exception as exc:
                        print(f"{name}: {exc}")
                        failed = True
                        continue
                    seen = set()
                    for tier in ("low", "medium", "high", "max"):
                        model = getattr(provider.models_by_tier, tier)
                        if model in seen:
                            continue
                        seen.add(model)
                        req = LLMRequest(surface="preflight", rendered=PROBE_PROMPT, tier=tier, effort="low", ticket=None, worktree=None)
                        try:
                            await adapter.invoke(req, model)
                            print(f"{name} {model}: ok")
                        except Exception as exc:
                            road = getattr(exc, "paved_road", None)
                            print(f"{name} {model}: {exc}" + (f" -- {road}" if road else ""))
                            failed = True
                return 1 if failed else 0

            return asyncio.run(probe())
        if args.verb == "core":
            hostfiles.refresh(routed_conduct_paths(config, repo), LocalFileSystem())
            return 0
        if args.verb == "prompt":
            if args.kind == "drafts":
                if args.stems:
                    raise runner.Refusal("drafts prompt takes no stems", "run chupa prompt drafts with no stems")
                from chupa import observe

                exec_ = SubprocessExec()
                git = Git(exec_, env={**child_env(env, config), "GIT_OPTIONAL_LOCKS": "0"}, timeout=GIT_TIMEOUT_S, commit_lock=CommitLock(config.state_dir, clock=clock, sleep=asyncio.sleep))
                context = observe.Context(repo.resolve(), config.state_dir.resolve(), (args.config or repo / "config.yaml").resolve(), exec_, git, child_env(env, config))
                stems = [row["stem"] for row in observe.snapshot(context)["rows"] if row["draft"]]
                if not stems:
                    raise runner.Refusal("no draft tickets await confirm or reject", "run triage, or author a ticket with chupa new")
                print(ask.render("drafts", stems, config, repo), end="")
                return 0
            if args.kind == "box":
                if not args.stems:
                    raise runner.Refusal("box prompt requires ids", "name at least one box id")
                print(ask.render("box", args.stems, config, repo), end="")
                return 0
            if len(args.stems) != 1:
                raise runner.Refusal("ticket prompt requires exactly one stem", "name one ticket stem")
            args.stem = args.stems[0]
            if findings := stem_findings(args.stem):
                raise runner.Refusal(findings[0].message, findings[0].paved_road)
            if not (repo / ticket_path(args.stem)).is_file():
                raise runner.Refusal(f"{ticket_path(args.stem)} does not exist", f"author it with chupa new {args.stem}")
            from chupa import observe

            events = observe.journal(config.state_dir)
            last = {e["ticket"]: {**e["body"], "ts": e["ts"]} for e in events if e.get("type") == "state_transition" and e.get("ticket")}
            kind = "running" if args.kind == "diagnose" and args.stem in observe.running_stems(config.state_dir, last) else args.kind
            print(ask.render(kind, args.stem, config, repo), end="")
            return 0
        exec_ = SubprocessExec()
        checkout = runner.Checkout(
            repo=repo,
            config=config,
            env=env,
            exec_=exec_,
            git=Git(
                exec_,
                env={**child_env(env, config), **({"GIT_OPTIONAL_LOCKS": "0"} if args.verb in {"lint", "watch", "snapshot"} else {})},
                timeout=GIT_TIMEOUT_S,
                commit_lock=CommitLock(config.state_dir, clock=clock, sleep=asyncio.sleep),
            ),
            journal=Journal(config.state_dir, clock),
            fs=LocalFileSystem(),
            clock=clock,
        )
        if args.verb in {"serve", "drain", "run"}:
            messages = asyncio.run(hostfiles.stale_core(repo, config, checkout.git))
            if messages:
                raise runner.Refusal("; ".join(messages), f"run chupa core, then commit the conduct files and retry {args.verb}")
        if args.verb == "suggest":
            if not args.summary.strip():
                raise runner.Refusal("blank summary", "pass the idea as one quoted argument")
            from chupa.box import Box, RereportJournal

            box = Box(config.state_dir / "box", checkout.fs, rereport=RereportJournal(checkout.journal))
            id, created = box.enqueue(message_class="suggestion", origin="session", summary=args.summary, occurrence_id=uuid4().hex)
            print(f"suggest: filed {id}" if created else f"suggest: already in the box as {id}")
            return 0
        if args.verb == "covmap":
            from chupa.covmap import build

            asyncio.run(build(repo=repo, config=config, exec_=exec_, git=checkout.git, fs=checkout.fs, env=child_env(env, config)))
            return 0
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
            from chupa.stats import render_stats, stats_tree, window_start

            events = checkout.journal.read()
            now = checkout.clock()
            try:
                window_start(events, now, args.window)
            except ValueError as exc:
                print(f"chupa stats: {exc}", file=sys.stderr)
                return 2
            result = asyncio.run(_stats(checkout, events, now, args.window))
            print(json.dumps(stats_tree(result) if args.tree else result) if args.tree or args.json else render_stats(result), end="\n" if args.tree or args.json else "")
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
            return asyncio.run(_verdict(checkout, args.stem, args.verb, read_input, args.yes, args.extension))
        if args.verb == "review":
            return asyncio.run(_review(checkout, args.stem))
        if args.verb == "dismiss":

            async def dismiss_messages():
                lock = Lockfile(config.state_dir, verb="dismiss", instance_id=await checkout.git.describe(repo), clock=clock)
                lock.acquire()
                try:
                    await runner.reap(checkout)
                    return await triage.dismiss(checkout, args.ids)
                finally:
                    lock.release()

            print("\n".join(asyncio.run(dismiss_messages())))
            return 0
        if args.verb == "triage":

            async def one_pass() -> list[tuple[str, str]]:
                lock = Lockfile(config.state_dir, verb="triage", instance_id=await checkout.git.describe(repo), clock=clock)
                lock.acquire()
                try:
                    await runner.reap(checkout)
                    session = build_control(checkout).providers
                    try:
                        triage.validate_ids(checkout, args.ids)
                        llm = await _preflighted_llm(checkout, session)
                        return await triage.triage_pass(checkout, llm, frozenset(args.ids))
                    finally:
                        await session.close()
                finally:
                    lock.release()

            lines = asyncio.run(one_pass())
            print("\n".join(line for _, line in lines) if lines else "no pending suggestions")
            return 0
        if args.verb == "serve":
            return asyncio.run(serve.serve(checkout, config_path=args.config, signals=_engine_signals, argv=invocation, reexec=reexec or SubprocessExec()))
        if args.verb == "retro":
            return asyncio.run(_retro(checkout, pipeline, config_path=args.config))
        checkout = replace(checkout, control=build_control(checkout))
        checkout.control.load_config = lambda: load_config(args.config, cwd=repo)
        dispatch = pipeline(checkout)
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
                    signals=_engine_signals,
                    reexec=reexec or SubprocessExec(),
                    parked=args.parked,
                    deadline=args.deadline,
                    stop_lifecycle=args.stop_lifecycle,
                    argv=(["--config", str(args.config)] if args.config else []) + ["drain"],
                )
            )
            if report.handoff is None:
                print(report.render(), end="")
            return report.exit_code
        return asyncio.run(runner.run_ticket(args.stem, checkout, dispatch))
    except UnknownBoxId as e:
        print(f"chupa {args.verb}: {e} -- name ids that chupa status lists", file=sys.stderr)
        return runner.EXIT_REFUSED
    except (ConfigError, runner.Refusal, LockHeld, CommitLockTimeout, IntakeRefused, JournalCorruption, ProviderSetupError, ExecutableNotFound, hostfiles.MarkerCorruption) as e:
        road = f" -- repair the selected config and retry {args.verb}" if args.verb in {"retro", "covmap"} and isinstance(e, ConfigError) else ""
        print(f"chupa {args.verb}: {e}{road}", file=sys.stderr)
        return runner.EXIT_REFUSED


async def _review(checkout: runner.Checkout, stem: str) -> int:
    from chupa.driver import Driver
    from chupa.effects import Effects
    from chupa.tickets import intake

    # Preserve stem, intake, existence and settled refusal precedence before reading main.
    admission = review_admission(stem, (), True, None)
    if admission.outcome == "refuse":
        raise runner.Refusal(admission.message, admission.paved_road)
    pending = await runner.ticket_pending(checkout.git, checkout.repo, stem)
    result = await intake(checkout.repo, checkout.git, checkout.journal, checkout.fs, stems={stem}) if pending else None
    path = checkout.repo / ticket_path(stem)
    intake_decision = result.refused.get(stem) if result else None
    history = checkout.journal.read() if path.is_file() and not intake_decision else ()
    states = last_states(history)
    admission = review_admission(stem, history, path.is_file(), None, intake_decision, pending=pending)
    if admission.outcome == "refuse":
        raise runner.Refusal(admission.message, admission.paved_road)
    text = await checkout.git._run(checkout.repo, "show", f"main:{ticket_path(stem)}")
    try:
        ticket = validate_ticket(stem, text, checkout.repo)
    except TicketInvalid as exc:
        ticket = exc.findings
    admission = review_admission(stem, history, True, ticket, pending=pending)
    if admission.outcome == "refuse":
        raise runner.Refusal(admission.message, admission.paved_road)
    unmerged = [dep for dep in ticket.depends if states.get(dep) != "merged"]
    session = build_control(checkout).providers
    try:
        llm = await _preflighted_llm(checkout, session)
        driver = Driver.from_config(checkout.config, llm=llm, env=checkout.env, clock=checkout.clock, sleep=checkout.sleep, fs=checkout.fs)
        driver.journal = checkout.journal
        driver.effects = Effects(checkout.journal)
        verdict = await requisition.review_ticket(
            driver,
            repo=checkout.repo,
            stem=stem,
            text=text,
            specs_dir=runner.SPECS_DIR,
            coverage_map=checkout.config.state_dir / "coverage-map.json" if checkout.config.review.coverage_map is not None else None,
            tier=checkout.config.routing_default_tier,
            stem_slot=f"review-{stem}",
            run_seq=len(history),
            attempt=0,
            call_seq=1,
            expected_budget="surface",
            prior=await requisition.prior_review(checkout.git, checkout.repo, history, stem, text),
        )
    finally:
        await session.close()
    if unmerged:
        print(f"review {stem}: provisional, not recorded -- depends on unmerged {', '.join(unmerged)}; the drain reviews it again before its first run")
    else:
        # A journaled approval would let the drain skip its review.
        checkout.journal.append(
            EventType.SIGNAL,
            {
                "signal": "requisition_verdict",
                "verdict": verdict.verdict,
                "findings": [{"code": f.code, "message": f.message} for f in verdict.findings],
                "ticket_sha": verdict.ticket_sha,
                "provider": verdict.provider,
                "model": verdict.model,
                "spec_version": verdict.spec_version,
            },
            ticket=stem,
        )
    print(f"review {stem}: {verdict.verdict} -- {verdict.summary}")
    for finding in verdict.findings:
        location = f" {finding.path}:{finding.line}" if finding.path and finding.line is not None else f" {finding.path}" if finding.path else ""
        print(f"- [{finding.code}]{location} {finding.message} ({finding.paved_road})")
    return 0 if verdict.verdict == "approve" else 1


def _require_engine(exc: LockHeld) -> None:
    verb = (exc.holder or {}).get("verb") or "unknown holder"
    if verb not in ENGINE_VERBS:
        raise runner.Refusal(f"writer lock held by {verb}", f"wait for {verb} to finish, then retry") from None


async def _retro(checkout, pipeline, *, config_path=None):
    from chupa.retro import Retro, RetroConstructionError, measurements, project_window, suppressing_failure

    lock = Lockfile(checkout.config.state_dir, verb="retro", instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    try:
        lock.acquire()
    except LockHeld as exc:
        _require_engine(exc)
        try:
            lifecycle, _ = control.read_active(checkout.config.state_dir, Path.read_bytes)
        except ValueError as exc:
            raise runner.Refusal("current control identity unavailable", str(exc)) from exc
        request = control.ControlRequest(uuid4().hex, lifecycle, "retro", None)
        control.publish_request(checkout.config.state_dir, request, checkout.fs)
        print(f"retro submitted: {request.request_id}; the running engine runs it between tickets")
        return 0
    try:
        await runner.reap(checkout)
        checkout = replace(checkout, control=build_control(checkout))
        checkout.control.load_config = lambda: load_config(config_path, cwd=checkout.repo)
        dispatch = pipeline(checkout)
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
            if checkout.control is not None:
                await checkout.control.providers.close()
        finally:
            lock.release()


def stuck_ceiling_finding(stuck_minutes: int, ceiling: int) -> str | None:
    if stuck_minutes > ceiling:
        return f"`## Time budget` stuck {stuck_minutes}m exceeds drain.max_ticket_minutes ({ceiling}m); lower `- stuck:` to at most {ceiling}m or split the ticket"
    return None


async def _lint(checkout: runner.Checkout, stems: Sequence[str]) -> int:
    root = checkout.repo / "tickets"
    valid = total = 0
    exit_code = 0
    try:
        entries = list(root.iterdir())  # Unlike glob, unreadable directories must refuse.
        selected = list(dict.fromkeys(stems)) if stems else sorted(p.name for p in entries if (p / "ticket.md").is_file())
        common_dir = await checkout.git.git_common_dir(checkout.repo)
        repo = checkout.repo.resolve()
        state_dir = checkout.config.state_dir.resolve()
        journal = checkout.journal
        if common_dir.parent != repo and state_dir.is_relative_to(repo):
            journal = Journal(common_dir.parent / state_dir.relative_to(repo), checkout.clock)
        events = journal.read()
        pending = _pending(checkout.repo, _porcelain(await checkout.git.status_porcelain(checkout.repo)))
        for stem in selected:
            rel = ticket_path(stem)
            path = checkout.repo / rel
            # Check existence before the stem grammar, without following an escaped path.
            inside = Path(stem).name == stem and stem not in {".", ".."} and path.resolve().is_relative_to(root.resolve())
            admission = lint_admission(stem, events, inside and path.is_file())
            if admission.outcome == "refuse":
                print(f"{rel}: {admission.message} ({admission.paved_road})")
                total += 1
                exit_code = 2
                continue
            if admission.outcome == "noop":
                continue
            total += 1
            text, findings = _intake_claims(stem, path.read_text(), pending.get(stem, False))
            ceiling_finding = None
            try:
                if findings:
                    raise TicketInvalid(findings)
                ticket = validate_ticket(stem, text, checkout.repo)
                ceiling_finding = stuck_ceiling_finding(ticket.stuck_minutes, checkout.config.drain.max_ticket_minutes)
                paths = await checkout.git._run(checkout.repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", f"tickets/{stem}/evidence/")
                findings = lint_findings(ticket, checkout.repo) + evidence_findings(ticket, checkout.repo, paths=paths.split("\0"))
            except TicketInvalid as exc:
                findings = exc.findings
            for finding in findings:
                message = " ".join(finding.message.splitlines())
                road = " ".join(finding.paved_road.splitlines())
                print(f"{finding.path or rel}: {message} ({road})")
            if ceiling_finding:
                print(f"{rel}: {ceiling_finding}")
            if findings or ceiling_finding:
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
        events,
        alive=observe.lock_holder(checkout.config.state_dir) is not None,
        window=window,
        provenance=provenance,
        box=Box(checkout.config.state_dir / BOX_DIR, checkout.fs, rereport=RereportJournal(checkout.journal)),
        policy=checkout.config.box_policy,
    )


def _engine_signals(stop: Callable[[], None]) -> Callable[[], None]:
    """Real signal delivery is composed here, alongside the other operating-system seams."""
    loop = asyncio.get_running_loop()
    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
    for sig in previous:
        loop.add_signal_handler(sig, stop)

    def restore() -> None:
        for sig, handler in previous.items():
            loop.remove_signal_handler(sig)
            signal.signal(sig, handler)

    return restore


async def _control(checkout: runner.Checkout, verb: str) -> int:
    lock = Lockfile(checkout.config.state_dir, verb=verb, instance_id=await checkout.git.describe(checkout.repo), clock=checkout.clock)
    try:
        lock.acquire()
    except LockHeld as exc:
        _require_engine(exc)
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


async def _verdict(checkout, stem, verb, read_input, yes, extension):
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
        answer = "y" if yes or extension else read_input(f"{verb} {stem}? [y/N] ")
    except EOFError:
        answer = ""
    if answer.strip().lower() not in {"y", "yes"}:
        print("verdict aborted")
        return 1
    try:
        return await runner.verdict(stem, checkout, kill=verb == "reject", extension=extension)
    except LockHeld as exc:
        _require_engine(exc)
    if await runner.ticket_pending(checkout.git, checkout.repo, stem):
        from chupa.tickets import intake

        result = await intake(checkout.repo, checkout.git, checkout.journal, checkout.fs, stems={stem})
        if refused := result.refused.get(stem):
            raise runner.Refusal(f"{ticket_path(stem)} failed intake: " + "; ".join(f.message for f in refused), "fix the ticket and retry the verdict")
    try:
        lifecycle, _ = control.read_active(checkout.config.state_dir, Path.read_bytes)
    except ValueError as exc:
        raise runner.Refusal("current control identity unavailable", str(exc)) from exc
    request = control.AdmissionRequest(uuid4().hex, lifecycle, verb, stem, None, "extension" if extension else "operator")
    control.publish_request(checkout.config.state_dir, request, checkout.fs)
    print(f"{verb} submitted: {request.request_id} -- ./dev.py status shows the outcome")
    return 0


def _order(checkout, stem, priority, runs_before):
    if findings := stem_findings(stem):
        raise runner.Refusal(findings[0].message, findings[0].paved_road)
    if priority is None and runs_before is None:
        raise runner.Refusal("no ordering option supplied", "supply --priority or --runs-before")
    path = checkout.repo / ticket_path(stem)
    exists = path.is_file()
    events = checkout.journal.read() if exists else ()
    state = last_states(events).get(stem)
    holder = observe.lock_holder(checkout.config.state_dir) if state == "running" and stem in reconcile.orphans(events) else None
    admission = order_admission(stem, events, exists, holder)
    if admission.outcome == "refuse":
        raise runner.Refusal(admission.message, admission.paved_road)
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
        admission = order_admission(stem, events, exists, holder, exc.findings)
        raise runner.Refusal(admission.message, admission.paved_road) from None
    checkout.fs.write(path, changed.encode())
    fields = ([f"priority: {priority}"] if priority is not None else []) + ([f"runs before: {', '.join(runs_before) or '(cleared)'}"] if runs_before is not None else [])
    print(f"ordered {stem}: {'; '.join(fields)}")
    return 0


def _new(repo: Path, stem: str, kind: str = "feature", evidence: Sequence[str] = ()) -> int:
    """Author a ticket and its evidence outside the lock fence."""
    if kind == "bug" and not evidence:
        raise runner.Refusal(
            "a bug ticket needs its evidence first", f"save the observed failure (output, log excerpt, or captured command output) to a file, then rerun new {stem} --kind bug --evidence <file>"
        )
    if kind != "bug" and evidence:
        raise runner.Refusal("evidence is for bug tickets", "omit --evidence or choose --kind bug")
    sources = [repo / path for path in evidence]
    for source in sources:
        if source.is_symlink() or not source.is_file():
            raise runner.Refusal(f"invalid evidence file: {source}", "supply an existing regular file that is not a symlink")
    if len({source.name for source in sources}) != len(sources):
        raise runner.Refusal("evidence files have duplicate names", "supply files with distinct names")
    if findings := stem_findings(stem):
        raise runner.Refusal(findings[0].message, findings[0].paved_road)
    rel = ticket_path(stem)
    guide = Path(chupa.__file__).parent / "docs" / "host-authoring.md"
    if (repo / rel).exists():
        raise runner.Refusal(f"{rel} already exists", f"read {guide}, then edit it in place, or pick a new stem")
    text = template(kind)
    fs = LocalFileSystem()
    fs.write(repo / rel, text.encode())
    for source in sources:
        fs.write(repo / "tickets" / stem / "evidence" / source.name, source.read_bytes())
    print(f"authored {rel}")
    print(f"read the ticket authoring guide before filling sections: {guide}")
    findings = []
    try:
        ticket = validate_ticket(stem, text, repo)
        findings = lint_findings(ticket, repo)
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
