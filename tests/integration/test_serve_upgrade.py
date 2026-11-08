"""Drive the CLI's continuous graph with disposable repositories and injected time."""

import asyncio
import json

import pytest

from chupa import daemon, runner, stages
from chupa.audit import audit_journal
from chupa.control import publish_request
from chupa.journal import EventType
from chupa.lockfile import Lockfile
from chupa.merge import Admission
from chupa.mergequeue import CONFLICT_FACTS, RED_STREAK, TREE_MISMATCH, MergeQueue, TreeMismatch
from tests.integration.serve_rig import (
    UpgradeChild,
    admission_config,
    admission_graph,
    admission_ticket,
    enable_upgrade,
    finish,
    graph,
    request,
    retro_scenario,
    script,
    start_admission,
    terminals,
    trip,
    until,
    write,
)
from tests.integration.test_cli import ENV, root
from tests.integration.test_scheduler import text, turn


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["chupa/thing.py", "docs/guide.md"])
async def test_upgrade_after_real_merge(root, monkeypatch, path):
    rig = await admission_graph(root, monkeypatch, {"work": {path: "ok\n"}})
    await enable_upgrade(rig, root)
    admission_ticket(root, "work", paths=(path,))
    checked_after_merge = asyncio.Event()
    check_upgrade = rig.owner.check_upgrade

    async def checked():
        await check_upgrade()
        if terminals(rig, "work"):
            checked_after_merge.set()

    monkeypatch.setattr(rig.owner, "check_upgrade", checked)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: bool(terminals(rig, "work")))
        if path.startswith("chupa/"):
            await until(rig, run.done)
            assert await run == 7
            assert len(rig.owner.reexec.calls) == 1
            argv, cwd, env, timeout = rig.owner.reexec.calls[0]
            assert argv == ["uv", "run", "--project", str(rig.owner.engine), "python", "-m", "chupa", "--config", "config.yaml", "serve"]
            assert cwd == root and env == rig.checkout.env and timeout is None
            [handoff] = [e for e in rig.journal.read() if e.body.get("signal") == "serve_handoff"]
            assert handoff.body == {"signal": "serve_handoff", "chupa": await rig.checkout.git.rev_parse(root, "HEAD:chupa")}
            assert rig.journal.read().index(terminals(rig, "work")[0]) < rig.journal.read().index(handoff)
        else:
            await until(rig, checked_after_merge.is_set)
            assert not rig.owner.reexec.calls and not run.done()
    finally:
        if not run.done():
            await finish(rig, run)


@pytest.mark.asyncio
async def test_external_engine_change_at_admission(root, tmp_path, monkeypatch):
    rig = await graph(root, monkeypatch)
    engine = tmp_path / "engine"
    (engine / "chupa").mkdir(parents=True)
    (engine / "chupa/a.py").write_text("old")
    await rig.checkout.git.init(engine, branch="main")
    await rig.checkout.git.add(engine, ["chupa"])
    await rig.checkout.git.commit(engine, "base")
    await enable_upgrade(rig, engine)
    run = asyncio.create_task(rig.owner.run())
    await until(rig, rig.owner.ready.is_set)
    (engine / "chupa/a.py").write_text("new")
    await rig.checkout.git.add(engine, ["chupa/a.py"])
    await rig.checkout.git.commit(engine, "upgrade")
    await until(rig, run.done)
    assert await run == 7 and len(rig.owner.reexec.calls) == 1
    assert any(e.body.get("signal") == "serve_handoff" for e in rig.journal.read())


@pytest.mark.asyncio
async def test_upgrade_waits_for_continuation(root, monkeypatch):
    calls, _, _ = script(monkeypatch)
    rig = await graph(root, monkeypatch)
    await enable_upgrade(rig, root)
    hold = trip(rig, stage="check")
    write(root, "work", text(priority="P0"))
    run = asyncio.create_task(rig.owner.run())
    await until(rig, lambda: "work" in rig.owner.writers and "work" in rig.owner.writers["work"].continuations)
    await until(rig, lambda: rig.owner.core.scheduler.active is None and rig.owner.core.admission.active is None)
    async with rig.owner.core.admission._slot:
        (root / "chupa/thing.py").write_text("changed")
        await rig.checkout.git.add(root, ["chupa/thing.py"])
        await rig.checkout.git.commit(root, "upgrade")
    await until(rig, lambda: rig.owner.upgrade is not None)
    write(root, "other", text())
    assert not run.done() and not rig.owner.reexec.calls
    assert not any(stem == "other" for stem, _, _ in calls)
    request(rig, "resume", "release-upgrade", hold=hold)
    await until(rig, run.done)
    assert await run == 7 and len(rig.owner.reexec.calls) == 1
    assert terminals(rig, "work") and not terminals(rig, "other")


@pytest.mark.asyncio
async def test_non_git_engine_disables_upgrade(root, tmp_path, monkeypatch):
    rig = await graph(root, monkeypatch)
    rig.owner.engine = tmp_path / "not-a-repo"
    rig.owner.engine.mkdir()
    rig.owner.reexec = UpgradeChild(rig)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, rig.owner.ready.is_set)
        assert rig.owner.trees is None and not rig.owner.reexec.calls
        events = [json.loads(line) for line in rig.owner.log.path.read_text().splitlines()]
        assert sum(e["event"] == "self_upgrade_off" for e in events) == 1
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_kill_accepted_during_upgrade_cleanup_prevents_spawn(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    await enable_upgrade(rig, root)
    cleanup = rig.owner.cleanup

    async def killing_cleanup():
        request(rig, "kill", "kill-before-spawn")
        rig.owner.control.poll()
        await cleanup()

    monkeypatch.setattr(rig.owner, "cleanup", killing_cleanup)
    run = asyncio.create_task(rig.owner.run())
    await until(rig, rig.owner.ready.is_set)
    async with rig.owner.core.admission._slot:
        (root / "chupa/thing.py").write_text("changed")
        await rig.checkout.git.add(root, ["chupa/thing.py"])
        await rig.checkout.git.commit(root, "upgrade")
    await until(rig, run.done)
    assert await run == 0 and not rig.owner.reexec.calls
    assert any(e.body.get("request_id") == "kill-before-spawn" and e.body.get("decision") == "accepted" for e in rig.journal.read())


@pytest.mark.asyncio
async def test_stop_finishes_merge_without_admitting_next_or_spawning(root, monkeypatch):
    entered, release = asyncio.Event(), asyncio.Event()

    async def settled(rig, ctx, ticket, attempt):
        if ticket.stem == "aa":
            entered.set()
            await release.wait()

    rig = await admission_graph(root, monkeypatch, {"aa": {"docs/a.txt": "a\n"}, "bb": {"docs/b.txt": "b\n"}}, settled=settled)
    await enable_upgrade(rig, root)
    admission_ticket(root, "aa", paths=("docs/a.txt",), priority="P0")
    admission_ticket(root, "bb", paths=("docs/b.txt",), priority="P1")
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, entered.is_set)
        request(rig, "stop", "finish-current")
        await until(rig, lambda: rig.owner.control.projection.stop_requested)
        assert not run.done()
        release.set()
        await until(rig, run.done)
        assert await run == 0
        assert [e.body["to"] for e in terminals(rig, "aa")] == ["merged"]
        assert not any(e.ticket == "bb" and e.body.get("to") == "running" for e in rig.journal.read())
        assert not rig.owner.reexec.calls
        lock = Lockfile(rig.checkout.config.state_dir, instance_id="probe", clock=rig.time)
        lock.acquire()
        lock.release()
    finally:
        release.set()
        if not run.done():
            await finish(rig, run)
