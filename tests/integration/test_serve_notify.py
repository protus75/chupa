"""Serve notify integration tests."""

import asyncio
import json

import pytest

from chupa import __main__ as cli
from chupa.journal import EventType
from chupa.mergequeue import RED_STREAK
from tests.integration.serve_rig import (
    deliveries,
    escalation_batch,
    finish,
    graph,
    notify_command,
    notify_completions,
    request,
    terminals,
    trip,
    until,
)
from tests.integration.test_cli import root


@pytest.mark.asyncio
async def test_serve_reconciles_notifications_at_startup_and_poll(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    notify_command(root)
    old = escalation_batch(rig, "old")
    assert not deliveries(root)
    original = rig.owner.notifications.poll
    polled = []

    def poll(**kwargs):
        if kwargs.get("startup"):
            assert rig.owner.core.restart.ready and not rig.owner.ready.is_set()
        polled.append(kwargs.get("startup", False))
        original(**kwargs)

    monkeypatch.setattr(rig.owner.notifications, "poll", poll)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: len(notify_completions(rig)) == 3)
        assert polled[0] is True and False in polled
        assert old[0] in rig.owner.storm.holds() and rig.owner.queue.paused
        assert terminals(rig) == []
        for row in deliveries(root):
            assert row["identity"] in old and row["exit"] == "resume"
            if row["kind"] == "storm_breaker_trip":
                assert row["held"] == {"emitting_origin": "old-storm", "emitting_stage": "check"}
                assert row["signature"] and row["trip_id"] == old[0]
            elif row["kind"] == RED_STREAK:
                assert row["stems"] == ["one", "two", "three"] and row["limit"] == 3
            else:
                assert row["checked_tree"] == "checked" and row["main_tree"] == "main"
        new = escalation_batch(rig, "new")
        await until(rig, lambda: len(notify_completions(rig)) == 6)
        assert len(deliveries(root)) == 6
        for identity in (*old, *new):
            request(rig, "resume", f"release-{identity}", hold=identity)
        await until(rig, lambda: not rig.owner.storm.holds() and not rig.owner.queue.paused)
        assert len(deliveries(root)) == 6 and terminals(rig) == []
    finally:
        await finish(rig, run)
    prior = rig.owner
    rig.owner = cli.build_serve(rig.checkout, read=prior.read, stems=prior.stems)
    heartbeat = rig.checkout.config.state_dir / "heartbeat"
    stamp = heartbeat.stat().st_mtime_ns
    restarted = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: heartbeat.stat().st_mtime_ns != stamp and rig.owner.ready.is_set())
        assert rig.owner.notifications.task is None
        assert len(deliveries(root)) == len(notify_completions(rig)) == 6
    finally:
        await finish(rig, restarted)


@pytest.mark.asyncio
async def test_serve_unset_notify_warns_once_and_preserves_pending(root, monkeypatch):
    from chupa.notify import pending_escalations
    from chupa.status import project

    rig = await graph(root, monkeypatch)
    identities = escalation_batch(rig, "pending")
    status = project(rig.journal.read())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: (rig.checkout.config.state_dir / "heartbeat").exists())
        heartbeat = rig.checkout.config.state_dir / "heartbeat"
        stamp = heartbeat.stat().st_mtime_ns
        await until(rig, lambda: heartbeat.stat().st_mtime_ns != stamp)
        warnings = [json.loads(line) for line in rig.owner.log.path.read_text().splitlines() if json.loads(line)["event"] == "notify_unset"]
        assert len(warnings) == 1 and "push is off" in warnings[0]["warning"]
        assert not deliveries(root) and not notify_completions(rig)
        current = project(rig.journal.read())
        for field in ("merged", "in_flight", "blocked", "intake", "reject"):
            assert getattr(current, field) == getattr(status, field)
        assert len(pending_escalations(rig.journal.read())) == 3
        assert identities[0] in rig.owner.storm.holds() and rig.owner.queue.paused
        notify_command(root)
        await until(rig, lambda: len(notify_completions(rig)) == 3)
        assert len(deliveries(root)) == 3 and not pending_escalations(rig.journal.read())
        assert identities[0] in rig.owner.storm.holds() and rig.owner.queue.paused
        assert sum(json.loads(line)["event"] == "notify_unset" for line in rig.owner.log.path.read_text().splitlines()) == 1
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_failed_notify_backoff_and_restart(root, monkeypatch):
    from chupa.notify import NOTIFY_RETRY_S, pending_escalations

    rig = await graph(root, monkeypatch)
    notify_command(root)
    (root / "notify-fails").touch()
    trip(rig)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: rig.owner.notifications.retry_at)

        def intents():
            return [e for e in rig.journal.read() if e.type == EventType.EFFECT_INTENT and e.key.startswith("notify/")]

        assert len(intents()) == 1 and not notify_completions(rig)
        # Unrelated journal arrivals do not reset this key's failed-command backoff.
        retry_at = dict(rig.owner.notifications.retry_at)
        rig.journal.append(EventType.SIGNAL, {"kind": "author_invoked"})
        rig.time.advance(10)
        # Complete a poll after the arrival while the fake clock stays inside the retry window.
        async with asyncio.timeout(60):
            await rig.owner.maintenance()
        assert rig.owner.notifications.retry_at == retry_at
        assert rig.owner.notifications.task is None
        assert len(intents()) == len(deliveries(root)) == 1
        assert len(pending_escalations(rig.journal.read())) == 1 and terminals(rig) == []
        assert [m for m in rig.owner.box.pending() if m.message_class == "failure_report"]
        rig.time.advance(NOTIFY_RETRY_S)
        await until(rig, lambda: len(deliveries(root)) == 2 and rig.owner.notifications.retry_at != retry_at)
        assert len(intents()) == 2 and not notify_completions(rig)
    finally:
        await finish(rig, run)
    (root / "notify-fails").unlink()
    prior = rig.owner
    rig.owner = cli.build_serve(rig.checkout, read=prior.read, stems=prior.stems)
    restarted = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: len(notify_completions(rig)) == 1)
        assert len(deliveries(root)) == 3 and terminals(rig) == []
        assert not pending_escalations(rig.journal.read())
    finally:
        await finish(rig, restarted)


@pytest.mark.asyncio
async def test_serve_hung_notify_keeps_maintenance_and_cleanup_responsive(root, monkeypatch):
    rig = await graph(root, monkeypatch)
    notify_command(root)
    escalation_batch(rig, "hung")
    entered, cancelled = asyncio.Event(), asyncio.Event()
    compose = rig.owner.notifications.compose

    async def hang(argv, **kwargs):
        entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    def composed(config):
        seam = compose(config)
        monkeypatch.setattr(seam.exec_, "run", hang)
        return seam

    monkeypatch.setattr(rig.owner.notifications, "compose", composed)
    refreshed = []
    write_fs = rig.fs.write

    def written(path, data):
        if path.name == "heartbeat":
            refreshed.append(rig.time())
        write_fs(path, data)

    monkeypatch.setattr(rig.fs, "write", written)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: entered.is_set() and len(refreshed) >= 2)
        assert rig.owner.ready.is_set() and not notify_completions(rig)
        request(rig, "pause", "pause-during-notify")
        await until(rig, lambda: rig.owner.control.projection.pause_id == "pause-during-notify")
        rig.owner.core.restart.timers.arm("during-notify", rig.time(), ticket=None)
        await until(rig, lambda: "during-notify" in rig.owner.core.restart.timers.fired)
        assert terminals(rig) == []
        assert len([e for e in rig.journal.read() if e.type == EventType.EFFECT_INTENT and e.key.startswith("notify/")]) == 1
        request(rig, "kill", "kill-during-notify")
        await until(rig, run.done)
        assert await run == 0 and cancelled.is_set()
        assert rig.owner.notifications.task is None
    finally:
        await finish(rig, run)
