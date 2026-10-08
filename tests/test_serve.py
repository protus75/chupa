"""Drive the CLI's continuous graph with disposable repositories and injected time."""

import asyncio
import json
import signal
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

import pytest

from chupa import __main__ as cli, daemon, runner, serve, stages, triage
from chupa.artifacts import Cost, StageResult
from chupa.audit import audit_journal
from chupa.control import ControlRequest, publish_request
from chupa.daemon import TicketWriter
from chupa.driver import LlmStage
from chupa.journal import EventType, run_seq
from chupa.llm import FakeLLM, HANG
from chupa.lockfile import Lockfile, LockHeld
from chupa.seams import LocalFileSystem
from chupa.stages import Invoice, PackingSlip
from tests.test_cli import ENV, PLAN, root, write
from tests.test_daemon_composition import sources
from tests.test_restart_timers import orphan, repository
from tests.test_scheduler import import_closure, text, turn
from tests.test_triage import reply


async def until(rig, predicate):
    for n in range(20000):
        if predicate():
            return
        if n % 20 == 0:
            rig.time.advance(serve.SERVE_POLL_S)
        await turn()
    raise AssertionError("production graph did not reach the scripted boundary")


async def graph(root, monkeypatch, **kwargs):
    rig = await repository(root, monkeypatch)
    rig.fs.publish = LocalFileSystem().publish
    rig.exec.reply = reply("decision")
    owner = serve.Serve(rig.checkout, plan=PLAN,
        read=lambda stem: (root / f"tickets/{stem}/ticket.md").read_text()
            if (root / f"tickets/{stem}/ticket.md").is_file() else None,
        stems=lambda: (p.parent.name for p in (root / "tickets").glob("*/ticket.md")), **kwargs)
    rig.owner = owner
    return rig


def script(monkeypatch, *, worktree=False, before=None, terminal="already_satisfied"):
    calls, contexts, artifacts = [], {}, {}
    async def implement(ctx, ticket, *, attempt):
        calls.append((ticket.stem, "implement", attempt))
        contexts[ticket.stem] = ctx
        if worktree:
            await stages.prepare_worktree(ctx, ticket.stem)
        if before is not None:
            await before(ctx, ticket, "implement", attempt)
        artifact = PackingSlip(produced_by_spec_version=1, produced_at_sha="fixture",
            stem=ticket.stem, branch=ticket.stem, outcome="ok", summary="scripted",
            run_record=f"tickets/{ticket.stem}/run.md")
        artifacts[ticket.stem] = artifact
        return StageResult(outcome="ok", artifact=artifact, cost=Cost(), findings=[])
    async def check(ctx, ticket, slip, *, attempt):
        assert slip is artifacts[ticket.stem] and ctx is contexts[ticket.stem]
        calls.append((ticket.stem, "check", attempt))
        if before is not None:
            await before(ctx, ticket, "check", attempt)
        invoice = Invoice(produced_by_spec_version=1, produced_at_sha="fixture", stem=ticket.stem,
            passed=True, changed_files=[], inserted_lines=0, bypassed=[], reports=[])
        artifacts[ticket.stem] = invoice
        return StageResult(outcome=terminal, artifact=invoice, cost=Cost(), findings=[])
    async def review(ctx, ticket, invoice, *, attempt):
        assert invoice is artifacts[ticket.stem]
        calls.append((ticket.stem, "review", attempt))
        if before is not None:
            await before(ctx, ticket, "review", attempt)
        return StageResult(outcome="budget_exceeded", artifact=None, cost=Cost(), findings=[])
    async def diagnosis(*args, **kwargs):
        return SimpleNamespace(verdict="abandon-human", lessons=[], mechanical=None)
    monkeypatch.setattr(stages, "implement", implement)
    monkeypatch.setattr(stages, "check", check)
    monkeypatch.setattr(stages, "review", review)
    monkeypatch.setattr(runner, "diagnose", diagnosis)
    return calls, contexts, artifacts


def terminals(rig, stem=None):
    return [e for e in rig.journal.read() if e.type == EventType.STATE_TRANSITION
            and e.body.get("to") != "running" and (stem is None or e.ticket == stem)]


def request(rig, verb, identity, hold=None, lifecycle=None):
    owner = rig.owner
    publish_request(rig.checkout.config.state_dir,
        ControlRequest(identity, lifecycle or owner.control.projection.lifecycle_id, verb, hold), rig.fs)


def trip(rig, stem="work", stage="check", signature="a"):
    for index in range(6):
        rig.owner.box.enqueue(message_class="failure_report", origin=stem, stage=stage,
            outcome="gate_failed", summary=signature, occurrence_id=f"{signature}/{index}")
    return [identity for identity, target in rig.owner.storm.held_stages().items()
            if target == {"emitting_origin": stem, "emitting_stage": stage}][-1]


async def finish(rig, run):
    rig.owner.stop()
    await until(rig, run.done)
    assert await run == 0
    assert rig.owner.tasks.tasks == () and all(task.done() for task in rig.owner.workers)
    assert json.loads((rig.checkout.config.state_dir / "control/active.json").read_text()) is None
    assert audit_journal(rig.journal) == []


async def activated_graph(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: (rig.checkout.config.state_dir / "heartbeat").exists())
    finally:
        await finish(rig, run)
    return rig


@pytest.mark.asyncio
async def test_serve_waits_at_quiescence_and_discovers_work(root, monkeypatch):
    calls, _, _ = script(monkeypatch)
    rig = await graph(root, monkeypatch)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: rig.owner.ready.is_set())
        assert not run.done() and calls == []
        write(root, "initial", text())
        await until(rig, lambda: len(terminals(rig, "initial")) == 1)
        assert not run.done()
        write(root, "later", text(depends="- initial"))
        await until(rig, lambda: len(terminals(rig, "later")) == 1)
        assert [(stem, stage) for stem, stage, _ in calls] == [
            ("initial", "implement"), ("initial", "check"), ("later", "implement"), ("later", "check")]
    finally:
        await finish(rig, run)


def test_serve_cli_uses_production_composition(root, monkeypatch):
    built = []
    original = serve.Serve.run
    async def run(self):
        assert self.workers == () and self.tasks.tasks == ()
        assert self.checkout.journal.read() == []
        assert self.core.restart.timers.journal is self.checkout.journal
        assert self.control is self.core.control is self.checkout.control
        assert self.control.inbox.journal is self.checkout.journal
        built.append(self)
        return await original(self)
    monkeypatch.setattr(serve.Serve, "run", run)
    monkeypatch.setattr(cli, "_serve_signals", lambda stop: (stop(), lambda: None)[1])
    assert cli.main(["serve"], cwd=root, env=ENV) == 0
    assert len(built) == 1 and len(built[0].workers) == 4
    assert "chupa.serve" in import_closure(sources())


@pytest.mark.asyncio
async def test_serve_holds_lock_through_cleanup(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    owner = rig.owner
    entering, release = asyncio.Event(), asyncio.Event()
    async def abort():
        entering.set()
        await release.wait()
    monkeypatch.setattr(owner, "abort", abort)
    contender = Lockfile(rig.checkout.config.state_dir, instance_id="contender", clock=rig.time)
    run = asyncio.create_task(owner.run())
    await until(rig, owner.ready.is_set)
    with pytest.raises(LockHeld):
        contender.acquire()
    other = serve.Serve(rig.checkout, plan=PLAN, read=owner.read, stems=owner.stems)
    try:
        with pytest.raises(LockHeld):
            await other.run()
    except BaseException:
        release.set()
        owner.stop()
        await until(rig, run.done)
        raise
    request(rig, "kill", "stop")
    await until(rig, entering.is_set)
    for _ in range(3):
        run.cancel()
        await turn()
        assert not run.done() and all(not t.done() for t in owner.workers)
        with pytest.raises(LockHeld):
            contender.acquire()
        assert json.loads((rig.checkout.config.state_dir / "control/active.json").read_text()) is not None
    release.set()
    await finish(rig, run)
    contender.acquire()
    contender.release()


@pytest.mark.asyncio
async def test_serve_startup_precedes_all_work(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    dead = await orphan(rig, "dead")
    rig.owner.core.restart.timers.arm("overdue", rig.time() - timedelta(seconds=1), ticket=None)
    calls, _, _ = script(monkeypatch)
    write(root, "work", text())
    original = runner.harvest_orphan
    harvested, release = asyncio.Event(), asyncio.Event()
    async def harvest(checkout, stem, attempt):
        assert checkout.journal is rig.journal
        harvested.set()
        await release.wait()
        await original(checkout, stem, attempt)
    monkeypatch.setattr(runner, "harvest_orphan", harvest)
    run = asyncio.create_task(rig.owner.run())
    await until(rig, harvested.is_set)
    assert calls == [] and not rig.owner.ready.is_set()
    assert not (rig.checkout.config.state_dir / "control/active.json").exists()
    release.set()
    try:
        await until(rig, lambda: terminals(rig, "work"))
        assert not dead.exists()
        history = rig.journal.read()
        abandoned = next(i for i, e in enumerate(history) if e.body.get("to") == "abandoned")
        fired = next(i for i, e in enumerate(history) if e.type == EventType.TIMER_FIRED)
        intake = next(i for i, e in enumerate(history) if e.body.get("signal") == "ticket_intake")
        assert abandoned < fired < intake
        assert any(e.ticket == "dead" and e.type == EventType.EFFECT_COMPLETION for e in history)
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_recovery_refusal_starts_no_work(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    rig.journal.append(EventType.TIMER_FIRED, {"timer_id": "unpaired", "deadline": rig.time().isoformat()})
    write(root, "work", text())
    with pytest.raises(runner.Refusal, match="startup recovery refused"):
        await rig.owner.run()
    assert rig.owner.workers == () and not rig.owner.core.restart.ready
    assert not any(e.body.get("signal") == "ticket_intake" for e in rig.journal.read())


@pytest.mark.asyncio
async def test_serve_control_precedes_offer_accounting(root, monkeypatch):
    calls, _, _ = script(monkeypatch)
    rig = await graph(root, monkeypatch)
    request(rig, "pause", "pause")
    request(rig, "kill", "old", lifecycle="retired")
    request(rig, "resume", "wrong", hold="other")
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: rig.owner.control.projection.pause_id == "pause"
                    and "work" in rig.owner.core.scheduler.pending)
        assert calls == [] and not any(e.body.get("to") == "running" for e in rig.journal.read())
        assert not any(e.type == EventType.CAP_CONSUMED for e in rig.journal.read())
        request(rig, "resume", "resume", hold="pause")
        await until(rig, lambda: terminals(rig, "work"))
        request(rig, "kill", "stop")
        await until(rig, run.done)
        assert await run == 0
        decisions = {e.body["request_id"]: e.body["decision"] for e in rig.journal.read()
                     if e.body.get("kind") == "control_decision"}
        assert decisions == {"old": "stale", "pause": "accepted", "wrong": "stale",
                             "resume": "accepted", "stop": "accepted"}
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
@pytest.mark.parametrize("ending", ["exception", "return", "cancel", "kill", "signal"])
async def test_serve_worker_failure_and_kill_suppression(root, monkeypatch, ending):
    failures = []
    rig = await graph(root, monkeypatch, failure=failures.append)
    entered, release = asyncio.Event(), asyncio.Event()
    error = ValueError("scripted consumer failure")
    cancellation = asyncio.CancelledError("scripted consumer cancellation")
    async def bad():
        entered.set()
        await release.wait()
        if ending == "exception":
            raise error
        if ending == "cancel":
            raise cancellation
    rig.owner.tasks._consumers = (bad, rig.owner.merge, rig.owner.triage)
    run = asyncio.create_task(rig.owner.run())
    await until(rig, entered.is_set)
    if ending == "kill":
        request(rig, "kill", "stop")
    elif ending == "signal":
        rig.owner.stop()
    else:
        release.set()
    await until(rig, run.done)
    assert await run == (0 if ending in {"kill", "signal"} else 1)
    if ending in {"kill", "signal"}:
        assert failures == []
    else:
        assert len(failures) == 1
        if ending == "exception":
            assert failures[0] is error
        elif ending == "cancel":
            assert failures[0] is cancellation
        else:
            assert isinstance(failures[0], RuntimeError)
            assert str(failures[0]) == "owned serve consumer returned unexpectedly"
            assert failures[0] is rig.owner.workers[1].exception()
    assert all(t.done() for t in rig.owner.workers)
    assert all(t.cancelled() or not t._log_traceback for t in rig.owner.workers)
    applied = [e for e in rig.journal.read() if e.body.get("kind") == "kill_applied"]
    assert len(applied) == (1 if ending == "kill" else 0)
    assert audit_journal(rig.journal) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["implement", "check", "review"])
async def test_serve_storm_suspends_stage_and_frees_selection(root, monkeypatch, stage):
    calls, contexts, artifacts = script(monkeypatch, terminal="ok" if stage == "review" else "already_satisfied")
    rig = await graph(root, monkeypatch)
    hold = trip(rig, stage=stage)
    write(root, "work", text(priority="P0"))
    write(root, "other", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: terminals(rig, "other"))
        await until(rig, lambda: rig.owner.core.admission.active is None
                    and rig.owner.core.scheduler.active is None)
        assert not terminals(rig, "work")
        assert not rig.owner.core.admission._slot.locked() or rig.owner.core.admission.active is None
        assert rig.owner.core.scheduler.active is None
        expected = [] if stage == "implement" else ["implement"] if stage == "check" else ["implement", "check"]
        assert [s for stem, s, _ in calls if stem == "work"] == expected
        prior = rig.owner.resume(SimpleNamespace(stem="work"))
        if stage == "implement":
            assert prior is None and not any(e.ticket == "work" and e.body.get("to") == "running"
                                             for e in rig.journal.read())
        else:
            assert isinstance(prior, TicketWriter)
            retained = prior.continuations["work"]
            assert retained.ctx is contexts["work"] and retained.next_stage == stage
            assert retained.run.results[expected[-1]].artifact is artifacts["work"]
        request(rig, "resume", "release", hold=hold)
        await until(rig, lambda: terminals(rig, "work"))
        assert [s for stem, s, _ in calls if stem == "work"] == expected + (
            ["implement", "check"] if stage == "implement" else [stage])
        assert sum(e.ticket == "work" and e.body.get("to") == "running" for e in rig.journal.read()) == 1
        assert len([e for e in rig.journal.read() if e.body.get("kind") == "storm_breaker_trip"]) == 1
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_storm_hold_and_resume(root, monkeypatch):
    await test_serve_storm_suspends_stage_and_frees_selection(root, monkeypatch, "check")


class HeldLLM(FakeLLM):
    def __init__(self):
        super().__init__([HANG])
        self.entered, self.cleaning, self.release = (asyncio.Event() for _ in range(3))
    async def call(self, request):
        self.entered.set()
        try:
            return await super().call(request)
        finally:
            self.cleaning.set()
            await self.release.wait()


async def active_graph(root, monkeypatch, *, signals=None, failure=None):
    llm = HeldLLM()
    async def prepare(local):
        return runner.bind(local, llm)
    rig = await graph(root, monkeypatch, prepare=prepare, signals=signals, failure=failure)
    async def implementing(ctx, ticket, *, attempt):
        await stages.prepare_worktree(ctx, ticket.stem)
        return await ctx.driver.run(LlmStage(surface="implement", emits=PackingSlip, gates=[],
            render=lambda *_: "scripted implement"), ticket, ticket=ticket.stem,
            attempt=attempt, workspace=ctx.worktree(ticket.stem), tier="medium", effort="medium",
            stuck_budget=1200)
    monkeypatch.setattr(stages, "implement", implementing)
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    await until(rig, llm.entered.is_set)
    return rig, llm, run


@pytest.mark.asyncio
async def test_serve_kill_unwinds_executor_before_workers(root, monkeypatch):
    rig, llm, run = await active_graph(root, monkeypatch)
    owner = rig.owner
    failures, order = [], []
    owner.observer.failure = failures.append
    for task in owner.workers:
        task.add_done_callback(lambda _: order.append("worker"))
    request(rig, "pause", "pause")
    await until(rig, lambda: owner.control.projection.pause_id == "pause")
    request(rig, "kill", "stop")
    await until(rig, llm.cleaning.is_set)
    assert order == [] and llm.aborted == 1
    assert any(e.body.get("request_id") == "stop" and e.body.get("decision") == "accepted"
               for e in rig.journal.read())
    assert not any(e.body.get("kind") == "kill_applied" for e in rig.journal.read())
    for _ in range(3):
        run.cancel()
        await turn()
        assert not run.done() and all(not t.done() for t in owner.workers)
    request(rig, "kill", "stop-again")
    llm.release.set()
    await finish(rig, run)
    assert order == ["worker"] * 4 and failures == []
    assert {e.body["request_id"] for e in rig.journal.read() if e.body.get("kind") == "kill_applied"} == {
        "stop", "stop-again"}
    assert not terminals(rig, "work")
    assert rig.checkout.config.worktree_root.joinpath("work").exists()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["SIGINT", "SIGTERM", "cancel"])
async def test_serve_signal_stop_and_restart_recovery(root, monkeypatch, mode):
    delivered, removed = {}, []
    loop = asyncio.get_running_loop()
    monkeypatch.setattr(loop, "add_signal_handler", lambda sig, handler: delivered.__setitem__(sig, handler))
    monkeypatch.setattr(loop, "remove_signal_handler", lambda sig: removed.append(sig))
    failures = []
    rig, llm, run = await active_graph(root, monkeypatch, signals=cli._serve_signals,
                                       failure=failures.append)
    if mode == "cancel":
        run.cancel()
    else:
        delivered[getattr(signal, mode)]()
    await until(rig, llm.cleaning.is_set)
    assert not run.done() and all(not t.done() for t in rig.owner.workers)
    llm.release.set()
    await finish(rig, run)
    assert failures == []
    assert set(removed) == {signal.SIGINT, signal.SIGTERM}
    assert not any(e.body.get("kind") in {"control_decision", "kill_applied"} for e in rig.journal.read())
    calls, _, _ = script(monkeypatch)
    old = rig.owner
    rig.owner = serve.Serve(rig.checkout, plan=PLAN, read=old.read, stems=old.stems)
    restarted = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: len(terminals(rig, "work")) == 2)
        assert [e.body["to"] for e in terminals(rig, "work")] == ["abandoned", "already_satisfied"]
        assert calls == [("work", "implement", 1), ("work", "check", 1)]
    finally:
        await finish(rig, restarted)


@pytest.mark.asyncio
async def test_serve_storm_resume_retains_producing_run(root, monkeypatch):
    calls, contexts, artifacts = script(monkeypatch)
    rig = await graph(root, monkeypatch)
    first = trip(rig, signature="a")
    second = trip(rig, signature="b")
    write(root, "work", text(priority="P0"))
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: "work" in rig.owner.writers
                    and "work" in rig.owner.writers["work"].continuations)
        writer = rig.owner.writers["work"]
        retained = writer.continuations["work"]
        snapshot, artifact = retained.ctx.config, artifacts["work"]
        path = root / "config.yaml"
        path.write_text(path.read_text() + "scheduler: {max_unmerged: 7}\n")
        request(rig, "resume", "first", hold=first)
        await until(rig, lambda: first in rig.owner.control.projection.released_hold_ids)
        assert writer.continuations["work"] is retained and not terminals(rig, "work")
        write(root, "other", text())
        await until(rig, lambda: terminals(rig, "other"))
        assert contexts["other"].config is not snapshot
        request(rig, "resume", "second", hold=second)
        await until(rig, lambda: terminals(rig, "work"))
        assert contexts["work"].config is snapshot and retained.run.attempt == 0
        assert retained.run.results["implement"].artifact is artifact
        assert [stage for stem, stage, _ in calls if stem == "work"] == ["implement", "check"]
        assert len(terminals(rig, "work")) == 1
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["kill", "signal", "cancel"])
async def test_serve_suspended_run_cleanup_and_restart(root, monkeypatch, mode):
    calls, _, _ = script(monkeypatch, worktree=True)
    rig = await graph(root, monkeypatch)
    hold = trip(rig)
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: "work" in rig.owner.writers
                    and "work" in rig.owner.writers["work"].continuations)
        retained = rig.owner.writers["work"].continuations["work"]
        await until(rig, lambda: rig.owner.core.admission.active is None)
        assert await rig.owner.core.sweep_orphans() == []
        assert retained.ctx.worktree("work").exists() and not terminals(rig, "work")
        request(rig, "pause", "pause")
        await until(rig, lambda: rig.owner.control.projection.pause_id == "pause")
        if mode == "kill":
            request(rig, "kill", "stop")
        elif mode == "cancel":
            run.cancel()
        else:
            rig.owner.stop()
    finally:
        await finish(rig, run)
    assert rig.owner.writers["work"].continuations == {}
    assert retained.ctx.worktree("work").exists() and not terminals(rig, "work")
    old = rig.owner
    rig.owner = serve.Serve(rig.checkout, plan=PLAN, read=old.read, stems=old.stems)
    restarted = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: len(calls) == 2 and calls[-1][-1] == 1)
        assert [e.body["to"] for e in terminals(rig, "work")] == ["abandoned"]
        assert hold in rig.owner.storm.held_stages()
        request(rig, "resume", "release", hold=hold)
        await until(rig, lambda: len(terminals(rig, "work")) == 2)
    finally:
        await finish(rig, restarted)


@pytest.mark.asyncio
async def test_serve_recurring_maintenance_uses_injected_time(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    pushes, original = [], rig.exec.run
    async def execute(argv, **kwargs):
        if argv[3:4] == ["push"]:
            pushes.append(list(argv))
            return (1, "", "scripted push failed") if len(pushes) == 1 else (0, "", "")
        return await original(argv, **kwargs)
    monkeypatch.setattr(rig.exec, "run", execute)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: "checkpoint-push/0" in rig.owner.core.restart.timers.pending)
        rig.time.advance(24 * 3600)
        await until(rig, lambda: len(pushes) == 2)
        assert any(e.body.get("kind") == "checkpoint_push_failed" for e in rig.journal.read())
        assert any(e.key == "checkpoint-push/0" and e.type == EventType.EFFECT_COMPLETION
                   and e.body == {"result": {"merged": 0}} for e in rig.journal.read())
        assert len([e for e in rig.journal.read() if e.type == EventType.TIMER_FIRED]) == 1
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
@pytest.mark.parametrize("component", [0, 1, 2, 3, "main"])
async def test_serve_heartbeat_requires_responsive_components(root, monkeypatch, component):
    rig = await graph(root, monkeypatch)
    refreshed = []
    original = rig.fs.write
    def write_fs(path, data):
        if path.name == "heartbeat":
            refreshed.append(rig.time())
        original(path, data)
    monkeypatch.setattr(rig.fs, "write", write_fs)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: len(refreshed) >= 2)
        release, entered = asyncio.Event(), asyncio.Event()
        original_wait = None if component == "main" else rig.owner.responses[component].wait
        async def wedge(work=None):
            entered.set()
            try:
                await release.wait()
                if work is not None:
                    return await original_wait(work)
            finally:
                if work is not None and hasattr(work, "close"):
                    work.close()
        if component == "main":
            monkeypatch.setattr(rig.owner, "maintenance", wedge)
        else:
            monkeypatch.setattr(rig.owner.responses[component], "wait", wedge)
        await until(rig, entered.is_set)
        for _ in range(100):
            rig.time.advance(0.1)
            await turn()
        saved = list(refreshed)
        for _ in range(100):
            rig.time.advance(0.1)
            await turn()
        assert refreshed == saved
        release.set()
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_consumers_use_existing_writers(root, monkeypatch):
    from chupa.driver import Driver
    from tests.test_mergequeue import ready
    calls, contexts, _ = script(monkeypatch)
    rig = await graph(root, monkeypatch)
    original = stages.implement
    async def implementing(ctx, ticket, *, attempt):
        if ticket.stem == "source":
            assert ctx.driver.journal is ctx.driver.effects._journal is rig.journal
            writer = rig.owner.writers["source"]
            assert writer.queue.control is rig.owner.control
            for n in range(5):
                path = f"chupa/queued{n}.py"
                work = await ready(ctx, f"candidate-{n}", changes={path: "ok\n"}, fence=(path,))
                # The existing ready-candidate fixture represents an earlier producing run.
                rig.transition(work.stem, "running")
                writer.queue.offer(work, attempt=0)
        return await original(ctx, ticket, attempt=attempt)
    monkeypatch.setattr(stages, "implement", implementing)
    rig.owner.core.scheduler.drought_parked = lambda: {f"candidate-{n}" for n in range(5)}
    triaged, pushes = [], []
    driving = Driver.run
    async def driver_run(self, stage, consumed, **kwargs):
        if stage.surface == "triage":
            assert self.journal is self.effects._journal is rig.journal
            assert rig.owner.control.author_driver is self
            assert rig.owner.core.admission.active is None
            triaged.append(self)
        return await driving(self, stage, consumed, **kwargs)
    monkeypatch.setattr(Driver, "run", driver_run)
    execute = rig.exec.run
    async def execution(argv, **kwargs):
        if argv[3:4] == ["push"]:
            pushes.append(list(argv))
            return 0, "", ""
        return await execute(argv, **kwargs)
    monkeypatch.setattr(rig.exec, "run", execution)
    rig.owner.box.enqueue(message_class="suggestion", origin="operator", stage=None,
                          outcome=None, summary="a policy decision", occurrence_id="fixture-arrival")
    write(root, "source", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: len([e for e in terminals(rig) if e.body.get("to") == "merged"]) == 5
                    and pushes and triaged)
        merged = [e for e in terminals(rig) if e.body.get("to") == "merged"]
        assert all(e.body["commit"] and e.body["reviewed_sha"] for e in merged)
        assert rig.owner.box.pending() == []
        assert len(triaged) == 1
        write(root, "dependent", text(depends="- candidate-4"))
        await until(rig, lambda: terminals(rig, "dependent"))
        assert [stem for stem, stage, _ in calls if stage == "implement"] == ["source", "dependent"]
        assert any(e.type == EventType.EFFECT_COMPLETION and e.body == {"result": {"merged": 5}}
                   for e in rig.journal.read())
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_author_uses_shared_journal(root, monkeypatch):
    from chupa.driver import Driver
    from tests.test_triage import author_reply, requisition_reply
    llm = FakeLLM([reply("author"), author_reply("drafted"), requisition_reply("approve")])
    observed = []
    run_driver = Driver.run
    rig = await graph(root, monkeypatch)
    from chupa.config import load_config
    config = root / "config.yaml"
    config.write_text(config.read_text().replace("routing:\n", "routing:\n"
        "  - {tier: high, surface: review, candidates: [{provider: claude}]}\n"
        "  - {tier: max, surface: review, candidates: [{provider: claude}]}\n"))
    rig.checkout = replace(rig.checkout, config=load_config(None, cwd=root))
    old = rig.owner
    rig.owner = serve.Serve(rig.checkout, plan=PLAN, read=old.read, stems=old.stems)
    async def driving(self, stage, consumed, **kwargs):
        assert self.journal is self.effects._journal is rig.journal
        assert rig.owner.control.author_driver is self
        self.llm = llm
        observed.append((self, stage.surface))
        return await run_driver(self, stage, consumed, **kwargs)
    monkeypatch.setattr(Driver, "run", driving)
    rig.owner.box.enqueue(message_class="suggestion", origin="operator", stage=None,
        outcome=None, summary="an authored repair", occurrence_id="author-fixture")
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: rig.owner.box.pending() == [])
        assert [surface for _, surface in observed] == ["triage", "author"]
        assert observed[0][0] is observed[1][0]
        assert [r.surface for r in llm.requests] == ["triage", "author", "requisition_review"]
        assert (root / "tickets/drafted/ticket.md").is_file()
        assert any(e.type == EventType.EFFECT_COMPLETION and e.key == "ticket-plane/drafted/author"
                   for e in rig.journal.read())
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_kill_unwinds_check_cleanup(root, monkeypatch):
    entered, cleaning, release = (asyncio.Event() for _ in range(3))
    async def before(ctx, ticket, stage, attempt):
        if stage == "check":
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleaning.set()
                await release.wait()
    script(monkeypatch, before=before)
    rig = await graph(root, monkeypatch)
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, entered.is_set)
        request(rig, "kill", "stop")
        await until(rig, cleaning.is_set)
        assert all(not t.cancelling() and not t.done() for t in rig.owner.workers)
        assert not any(e.body.get("kind") == "kill_applied" for e in rig.journal.read())
    finally:
        release.set()
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_watcher_edits_deletions_and_last_good(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    request(rig, "pause", "pause")
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: "work" in rig.owner.core.watcher.cache)
        original = rig.owner.core.watcher.cache["work"]
        write(root, "work", "---\ninvalid: [\n")
        await until(rig, lambda: any(e.body.get("signal") == "watcher_parse_failure"
                                    for e in rig.journal.read()))
        assert rig.owner.core.watcher.cache["work"] is original
        assert rig.owner.core.scheduler.pending["work"] is original
        write(root, "work", text(priority="P0"))
        await until(rig, lambda: rig.owner.core.watcher.cache["work"].frontmatter.priority == "P0")
        root.joinpath("tickets/work/ticket.md").unlink()
        await until(rig, lambda: "work" not in rig.owner.core.watcher.cache)
        assert "work" not in rig.owner.core.scheduler.pending and not terminals(rig, "work")
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_kill_unwinds_preparation(root, monkeypatch):
    entered, cleaning, release = (asyncio.Event() for _ in range(3))
    async def prepare(local):
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cleaning.set()
            await release.wait()
    rig = await graph(root, monkeypatch, prepare=prepare)
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, entered.is_set)
        request(rig, "kill", "stop")
        await until(rig, cleaning.is_set)
        assert all(not t.cancelling() and not t.done() for t in rig.owner.workers)
        assert not any(e.body.get("to") == "running" for e in rig.journal.read())
    finally:
        release.set()
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_abort_failure_does_not_apply_kill(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    async def abort():
        raise OSError("scripted abort cleanup failure")
    monkeypatch.setattr(rig.owner, "abort", abort)
    run = asyncio.create_task(rig.owner.run())
    await until(rig, rig.owner.ready.is_set)
    request(rig, "kill", "stop")
    await until(rig, run.done)
    assert await run == 1 and all(t.done() for t in rig.owner.workers)
    assert not any(e.body.get("kind") == "kill_applied" for e in rig.journal.read())
    assert audit_journal(rig.journal) == []
