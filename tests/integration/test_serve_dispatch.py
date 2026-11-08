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
async def test_refused_uncommitted_bug_does_not_stop_serve(root, monkeypatch):
    calls, _, _ = script(monkeypatch)
    rig = await graph(root, monkeypatch)
    bug = text().replace("kind: feature", "kind: bug")
    bug += "\n## Regression\n```\npython -c 'print(1)'\n```\n- carries: tests/\n"
    write(root, "no-evidence", bug)
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, rig.owner.ready.is_set)
        # Ensure the parseable refused stem actually reaches dispatch, rather than being filtered.
        await until(rig, lambda: "no-evidence" in rig.owner.core.watcher.cache)
        await rig.owner.core.admission.dispatch(rig.owner.core.watcher.cache["no-evidence"])
        assert not run.done() and not rig.owner.stopping
        assert "no-evidence" not in rig.owner.writers
        assert calls == []
        assert not any(e.body.get("to") == "running" for e in rig.journal.read())
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
@pytest.mark.parametrize("committed", [False, True])
async def test_dispatch_republishes_ticket_changed_after_publication(root, monkeypatch, committed):
    calls, _, _ = script(monkeypatch)
    rig = await graph(root, monkeypatch)
    write(root, "work", text())
    await rig.owner.scan()
    original = (root / "tickets/work/ticket.md").read_text()
    from chupa.tickets import parse_ticket

    ticket = parse_ticket("work", original, root)
    rig.owner.publish(ticket, original)
    revised = original.replace("## Scope fence\n- chupa/", "## Scope fence\n- revised/")
    assert revised != original
    path = "tickets/work/ticket.md"
    rig.fs.write(root / path, revised.encode())
    if committed:
        await rig.checkout.git.add(root, [path])
        await rig.checkout.git.commit(root, "edit after publication", only=[path])
    await rig.owner.core.admission.dispatch(ticket)
    assert not calls and not rig.owner.writers
    if committed:
        fresh = rig.owner.core.scheduler.pending["work"]
        assert fresh.scope_fence != ticket.scope_fence
        assert not any(e.body.get("to") == "running" for e in rig.journal.read())
    else:
        assert terminals(rig, "work")[-1].body["reason"] == "ticket_changed"
    await rig.owner.control.providers.close()


@pytest.mark.asyncio
async def test_invalid_new_ticket_reaches_watcher(root, monkeypatch):
    script(monkeypatch)
    rig = await graph(root, monkeypatch)
    write(root, "invalid-new", "not a ticket")
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: any(e.ticket == "invalid-new" and e.body.get("signal") == "watcher_parse_failure" for e in rig.journal.read()))
        assert not run.done()
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_live_keep_dispatches_again_without_restart(root, monkeypatch):
    from chupa.control import AdmissionRequest

    calls, _, _ = script(monkeypatch, terminal="gate_failed")
    rig = await graph(root, monkeypatch)
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: any(e.ticket == "work" and e.body.get("routed") == "reject_queue" for e in rig.journal.read()))
        next_calls, _, _ = script(monkeypatch, terminal="already_satisfied")
        publish_request(rig.checkout.config.state_dir, AdmissionRequest("keep-live", rig.owner.control.projection.lifecycle_id, "confirm", "work", None, "operator"), rig.fs)
        await until(rig, lambda: any(e.ticket == "work" and e.body.get("to") == "already_satisfied" for e in rig.journal.read()))
        assert [(stem, stage) for stem, stage, _ in calls] == [("work", "implement"), ("work", "check")]
        assert [(stem, stage) for stem, stage, _ in next_calls] == [("work", "implement"), ("work", "check")]
        assert len([e for e in rig.journal.read() if e.ticket == "work" and e.body.get("signal") == "reject_verdict" and e.body.get("verdict") == "keep"]) == 1
        assert not run.done()
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_reoffers_failed_dispatch_with_machine_keep_and_retry(root, monkeypatch):
    calls, _, _ = script(monkeypatch, terminal="gate_failed")
    check = stages.check

    async def once(ctx, ticket, slip, *, attempt):
        result = await check(ctx, ticket, slip, attempt=attempt)
        if attempt:
            from dataclasses import replace

            return replace(result, outcome="already_satisfied")
        return result

    monkeypatch.setattr(stages, "check", once)
    rig = await graph(root, monkeypatch)
    write(root, "work", text())
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: any(e.body.get("to") == "already_satisfied" for e in terminals(rig, "work")))
        events = [e for e in rig.journal.read() if e.ticket == "work"]
        keep = [i for i, e in enumerate(events) if e.body.get("signal") == "reject_verdict" and e.body.get("actor") == "machine"]
        retry = [i for i, e in enumerate(events) if e.type == EventType.CAP_CONSUMED and e.body.get("cap") == "retry"]
        running = [i for i, e in enumerate(events) if e.body.get("to") == "running"]
        assert len(keep) == len(retry) == 1 and len(running) == 2
        assert running[0] < keep[0] < retry[0] < running[1]
        assert [attempt for stem, stage, attempt in calls if stage == "implement"] == [0, 1]
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_premise_reoffer_draws_no_retry(root, monkeypatch):
    calls, _, _ = script(monkeypatch)
    rig = await graph(root, monkeypatch)
    write(root, "work", text())
    await rig.owner.scan()
    rig.journal.append(EventType.STATE_TRANSITION, {"to": "running", "ticket_sha": "previous-content"}, ticket="work")
    rig.journal.append(EventType.STATE_TRANSITION, {"to": "premise_failed"}, ticket="work")
    run = asyncio.create_task(rig.owner.run())
    try:
        await until(rig, lambda: any(e.body.get("to") == "already_satisfied" for e in terminals(rig, "work")))
        assert [attempt for stem, stage, attempt in calls if stage == "implement"] == [1]
        assert not [e for e in rig.journal.read() if e.ticket == "work" and e.type == EventType.CAP_CONSUMED and e.body.get("cap") == "retry"]
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_serve_reoffers_merge_failure(root, monkeypatch):
    async def settled(rig, ctx, ticket, attempt):
        if attempt == 0:
            ctx.fs.write(ctx.worktree(ticket.stem) / "tickets/forbidden.md", b"forbidden")
            await ctx.git.add(ctx.worktree(ticket.stem), ["tickets/forbidden.md"])
            await ctx.git.commit(ctx.worktree(ticket.stem), "force post-rebase regate failure")

    rig = await admission_graph(root, monkeypatch, {"work": {"chupa/thing.py": "ok\n"}}, settled=settled)
    admission_ticket(root, "work")
    run = await start_admission(rig, monkeypatch)
    try:
        await until(rig, lambda: ("work", "merged") in rig.returns)
        events = [e for e in rig.journal.read() if e.ticket == "work"]
        failures = [i for i, e in enumerate(events) if e.body.get("to") == "gate_failed" and e.body.get("stage") == "merge"]
        retries = [i for i, e in enumerate(events) if e.type == EventType.CAP_CONSUMED and e.body.get("cap") == "retry"]
        running = [i for i, e in enumerate(events) if e.body.get("to") == "running"]
        assert len(failures) == len(retries) == 1 and len(running) == 2
        assert running[0] < failures[0] < retries[0] < running[1]
    finally:
        await finish(rig, run)


@pytest.mark.asyncio
async def test_requested_retro_waits_for_idle_then_resumes(root, monkeypatch):
    await retro_scenario(root, monkeypatch, "requested")


@pytest.mark.asyncio
async def test_kill_aborts_requested_retro(root, monkeypatch):
    await retro_scenario(root, monkeypatch, "kill")


@pytest.mark.asyncio
async def test_automatic_retro_runs_at_idle_when_due(root, monkeypatch):
    await retro_scenario(root, monkeypatch, "automatic")


@pytest.mark.asyncio
async def test_automatic_retro_off_when_disabled(root, monkeypatch):
    await retro_scenario(root, monkeypatch, "disabled")


@pytest.mark.asyncio
async def test_failed_retro_does_not_reblock(root, monkeypatch):
    await retro_scenario(root, monkeypatch, "failed")
