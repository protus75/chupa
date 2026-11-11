"""Serve kill integration tests."""

import asyncio
import json
import signal
from types import SimpleNamespace

import pytest

from chupa import __main__ as cli
from chupa import serve
from chupa.audit import audit_journal
from chupa.daemon import TicketWriter
from tests.integration.serve_rig import active_graph, finish, graph, request, script, terminals, trip, until, write
from tests.integration.test_cli import root
from tests.integration.test_scheduler import text, turn


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

    rig.owner.tasks._consumers = (bad, rig.owner.merge, rig.owner.box_intake)
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
    lifecycle = [json.loads(line) for line in rig.owner.log.path.read_text().splitlines() if json.loads(line)["event"] == "engine_stop"]
    expected = {"exception": "error: ValueError", "return": "error: RuntimeError", "cancel": "error: CancelledError", "kill": "killed", "signal": "stopped"}
    assert [e["outcome"] for e in lifecycle] == [expected[ending]]
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
        await until(rig, lambda: rig.owner.core.admission.active is None and rig.owner.core.scheduler.active is None)
        assert not terminals(rig, "work")
        assert not rig.owner.core.admission._slot.locked() or rig.owner.core.admission.active is None
        assert rig.owner.core.scheduler.active is None
        expected = [] if stage == "implement" else ["implement"] if stage == "check" else ["implement", "check"]
        assert [s for stem, s, _ in calls if stem == "work"] == expected
        prior = rig.owner.resume(SimpleNamespace(stem="work"))
        if stage == "implement":
            assert prior is None and not any(e.ticket == "work" and e.body.get("to") == "running" for e in rig.journal.read())
        else:
            assert isinstance(prior, TicketWriter)
            retained = prior.continuations["work"]
            assert retained.ctx is contexts["work"] and retained.next_stage == stage
            assert retained.run.results[expected[-1]].artifact is artifacts["work"]
        request(rig, "resume", "release", hold=hold)
        await until(rig, lambda: terminals(rig, "work"))
        assert [s for stem, s, _ in calls if stem == "work"] == expected + (["implement", "check"] if stage == "implement" else [stage])
        assert sum(e.ticket == "work" and e.body.get("to") == "running" for e in rig.journal.read()) == 1
        assert len([e for e in rig.journal.read() if e.body.get("kind") == "storm_breaker_trip"]) == 1
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_storm_hold_and_resume(root, monkeypatch):
    await test_serve_storm_suspends_stage_and_frees_selection(root, monkeypatch, "check")


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
    assert any(e.body.get("request_id") == "stop" and e.body.get("decision") == "accepted" for e in rig.journal.read())
    assert not any(e.body.get("kind") == "kill_applied" for e in rig.journal.read())
    for _ in range(3):
        run.cancel()
        await turn()
        assert not run.done() and all(not t.done() for t in owner.workers)
    request(rig, "kill", "stop-again")
    llm.release.set()
    await finish(rig, run)
    assert order == ["worker"] * 4 and failures == []
    assert {e.body["request_id"] for e in rig.journal.read() if e.body.get("kind") == "kill_applied"} == {"stop", "stop-again"}
    assert not terminals(rig, "work")
    assert rig.checkout.config.worktree_root.joinpath("work").exists()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["SIGINT", "SIGTERM", "SIGHUP", "cancel"])
async def test_serve_signal_stop_and_restart_recovery(root, monkeypatch, mode):
    delivered, removed = {}, []
    loop = asyncio.get_running_loop()
    monkeypatch.setattr(loop, "add_signal_handler", lambda sig, handler: delivered.__setitem__(sig, handler))
    monkeypatch.setattr(loop, "remove_signal_handler", lambda sig: removed.append(sig))
    failures = []
    rig, llm, run = await active_graph(root, monkeypatch, signals=cli._engine_signals, failure=failures.append)
    if mode == "cancel":
        run.cancel()
    else:
        delivered[getattr(signal, mode)]()
    await until(rig, llm.cleaning.is_set)
    assert not run.done() and all(not t.done() for t in rig.owner.workers)
    llm.release.set()
    await finish(rig, run)
    assert failures == []
    assert set(removed) == {signal.SIGINT, signal.SIGTERM, signal.SIGHUP}
    assert not any(e.body.get("kind") in {"control_decision", "kill_applied"} for e in rig.journal.read())
    calls, _, _ = script(monkeypatch)
    old = rig.owner
    rig.owner = serve.Serve(rig.checkout, read=old.read, stems=old.stems)
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
        await until(rig, lambda: "work" in rig.owner.writers and "work" in rig.owner.writers["work"].continuations)
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
        await until(rig, lambda: "work" in rig.owner.writers and "work" in rig.owner.writers["work"].continuations)
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
    rig.owner = serve.Serve(rig.checkout, read=old.read, stems=old.stems)
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
