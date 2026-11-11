"""Serve lifecycle integration tests."""

import asyncio
import json
from datetime import timedelta

import pytest

from chupa import __main__ as cli
from chupa import runner, serve, stages
from chupa.journal import EventType
from chupa.lockfile import Lockfile, LockHeld
from tests.integration.serve_rig import finish, graph, request, script, terminals, until, write
from tests.integration.test_cli import ENV, root
from tests.integration.test_daemon_composition import sources
from tests.integration.test_restart_timers import orphan
from tests.integration.test_scheduler import import_closure, text, turn


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
        assert [(stem, stage) for stem, stage, _ in calls] == [("initial", "implement"), ("initial", "check"), ("later", "implement"), ("later", "check")]
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_empty_box_report_intake(root, monkeypatch):
    from tests.integration.test_inbox import arrival

    rig = await graph(root, monkeypatch)
    config = root / "config.yaml"
    config.write_text(config.read_text() + "report_inbox: inbox\n")
    assert rig.owner.box.messages() == []
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, rig.owner.ready.is_set)
        arrival(root)
        await until(rig, lambda: rig.owner.box.messages() and rig.owner.box.messages()[0].status == "pending")
        (message,) = rig.owner.box.messages()
        assert message.report and message.has_repro
        assert message.resolution is None
        assert len([e for e in rig.journal.read() if e.body.get("signal") == "triage_pass"]) == 0
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_report_consumer_is_sequential(root, monkeypatch):
    from chupa.driver import Driver
    from tests.integration.test_inbox import arrival, raw_report

    rig = await graph(root, monkeypatch)
    config = root / "config.yaml"
    config.write_text(config.read_text() + "report_inbox: inbox\n")
    arrival(root)
    (root / "inbox/b.json").write_text(json.dumps(raw_report(summary="Another material defect")))
    calls = []
    driving = Driver.run

    async def observed(self, stage, consumed, **kwargs):
        if stage.surface == "triage":
            calls.append(stage.surface)
        return await driving(self, stage, consumed, **kwargs)

    monkeypatch.setattr(Driver, "run", observed)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: len(rig.owner.box.pending()) == 2)
        heartbeat = rig.checkout.config.state_dir / "heartbeat"
        await until(rig, heartbeat.exists)
        stamp = heartbeat.stat().st_mtime_ns
        await until(rig, lambda: heartbeat.stat().st_mtime_ns != stamp)
        assert len(rig.owner.workers) == 4
        assert len(rig.owner.tasks._consumers) == 3
        assert {m.summary for m in rig.owner.box.pending()} == {"Observed scoring defect", "Another material defect"}
        assert calls == []
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
        command = self.notifications.compose(self.checkout.config)
        assert command.exec_ is not self.checkout.exec_
        built.append(self)
        return await original(self)

    monkeypatch.setattr(serve.Serve, "run", run)
    monkeypatch.setattr(cli, "_engine_signals", lambda stop: (stop(), lambda: None)[1])
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
    contender = Lockfile(rig.checkout.config.state_dir, verb="drain", instance_id="contender", clock=rig.time)
    run = asyncio.create_task(owner.run())
    await until(rig, owner.ready.is_set)
    with pytest.raises(LockHeld):
        contender.acquire()
    other = serve.Serve(rig.checkout, read=owner.read, stems=owner.stems)
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
        await until(rig, lambda: rig.owner.control.projection.pause_id == "pause" and "work" in rig.owner.core.scheduler.pending)
        assert calls == [] and not any(e.body.get("to") == "running" for e in rig.journal.read())
        assert not any(e.type == EventType.CAP_CONSUMED for e in rig.journal.read())
        request(rig, "resume", "resume", hold="pause")
        await until(rig, lambda: terminals(rig, "work"))
        request(rig, "kill", "stop")
        await until(rig, run.done)
        assert await run == 0
        decisions = {e.body["request_id"]: e.body["decision"] for e in rig.journal.read() if e.body.get("kind") == "control_decision"}
        assert decisions == {"old": "stale", "pause": "accepted", "wrong": "stale", "resume": "accepted", "stop": "accepted"}
    finally:
        await finish(rig, run)


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
        assert any(e.key == "checkpoint-push/0" and e.type == EventType.EFFECT_COMPLETION and e.body == {"result": {"merged": 0}} for e in rig.journal.read())
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
        maintenance = rig.owner.maintenance
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
        if component == "main":
            saved = list(refreshed)
            for response in rig.owner.responses:
                response.ask()
            await until(rig, lambda: all(r.responsive() for r in rig.owner.responses))
        else:
            response = rig.owner.responses[component]
            await until(rig, lambda: response.sent > response.answered)
            saved = list(refreshed)
            checked = []
            cycle = rig.owner.heartbeat.cycle

            def observed_cycle():
                result = cycle()
                checked.append(result)
                return result

            monkeypatch.setattr(rig.owner.heartbeat, "cycle", observed_cycle)
            await until(rig, lambda: bool(checked))
            assert checked == [False]
        assert refreshed == saved
        if component == "main":
            monkeypatch.setattr(rig.owner, "maintenance", maintenance)
        release.set()
        await until(rig, lambda: len(refreshed) > len(saved))
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_consumers_use_existing_writers(root, monkeypatch):
    from chupa.driver import Driver
    from tests.integration.test_mergequeue import ready

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
    rig.fixture_confirm = True
    rig.owner.core.scheduler.drought_parked = lambda: {f"candidate-{n}" for n in range(5)}
    triaged, pushes = [], []
    driving = Driver.run

    async def driver_run(self, stage, consumed, **kwargs):
        if stage.surface == "triage":
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
    rig.owner.box.enqueue(message_class="suggestion", origin="operator", stage=None, outcome=None, summary="a policy decision", occurrence_id="fixture-arrival")
    write(root, "source", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: len([e for e in terminals(rig) if e.body.get("to") == "merged"]) == 5 and pushes)
        merged = [e for e in terminals(rig) if e.body.get("to") == "merged"]
        assert all(e.body["commit"] and e.body["reviewed_sha"] for e in merged)
        assert [m.summary for m in rig.owner.box.pending()] == ["a policy decision"]
        assert triaged == []
        write(root, "dependent", text(depends="- candidate-4"))
        await until(rig, lambda: terminals(rig, "dependent"))
        assert [stem for stem, stage, _ in calls if stage == "implement"] == ["source", "dependent"]
        assert any(e.type == EventType.EFFECT_COMPLETION and e.body == {"result": {"merged": 5}} for e in rig.journal.read())
    finally:
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
        await until(rig, lambda: any(e.body.get("signal") == "watcher_parse_failure" for e in rig.journal.read()))
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
async def test_serve_control_stop_lifecycle_log(root, monkeypatch):
    import os

    rig = await graph(root, monkeypatch)
    released = []
    release = Lockfile.release

    def observed(lock):
        rows = [json.loads(line) for line in rig.owner.log.path.read_text().splitlines()]
        released.extend(e for e in rows if e["event"] in {"engine_start", "engine_stop"})
        release(lock)

    monkeypatch.setattr(Lockfile, "release", observed)
    run = asyncio.create_task(rig.owner.run())
    await until(rig, rig.owner.ready.is_set)
    request(rig, "stop", "lifecycle-stop")
    await until(rig, run.done)
    assert await run == 0
    assert [(e["event"], e["verb"], e["pid"], e.get("outcome")) for e in released] == [("engine_start", "serve", os.getpid(), None), ("engine_stop", "serve", os.getpid(), "stopped")]
    assert all("engine_start" not in str((e.type, e.body)) and "engine_stop" not in str((e.type, e.body)) for e in rig.journal.read())
