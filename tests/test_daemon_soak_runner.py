"""Production soak evidence, false-green refusal, and owned lifetime cleanup."""

import asyncio
import json
from datetime import timedelta

import pytest
import pytest_asyncio

from chupa import __main__ as cli
from chupa.artifacts import DAEMON_SOAK_MEMBERS
from chupa.audit import audit_journal
from chupa.journal import EventType
from chupa.lockfile import Lockfile
from chupa.mergequeue import CONFLICT_FACTS, MergeQueue
from chupa.reconcile import RECOVERY_ALERT
from chupa.stages import read_review
from eval import daemon_soak as soak


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def evidence(tmp_path_factory):
    members = []
    original = soak._observe
    async def observed(member):
        members.append(member)
        return await original(member)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(soak, "_observe", observed)
        report = await soak.produce(tmp_path_factory.mktemp("production-soak"))
    return report, members


@pytest.mark.asyncio
async def test_daemon_soak_runs_production_serve(tmp_path, monkeypatch):
    built, offers, consumed, admissions = [], [], [], []
    build, offer, process = cli.build_serve, MergeQueue.offer, MergeQueue.process
    from chupa.daemon import TicketWriter
    consume = TicketWriter.consume_result
    def building(*args, **kwargs):
        owner = build(*args, **kwargs)
        built.append(owner)
        return owner
    def offered(queue, ticket, *, attempt):
        owner = next(o for o in built if o.checkout.journal is queue.ctx.driver.journal)
        writer = owner.writers[ticket.stem]
        assert writer.admission.mode == "daemon" and writer.queue is owner.queue is queue
        assert owner.core.scheduler.dispatch == owner.core.admission.dispatch
        assert owner.core.watcher.publish == owner.core.scheduler.update
        assert owner.control.inbox.journal is queue.ctx.driver.journal
        offers.append((queue, ticket.stem, attempt))
        offer(queue, ticket, attempt=attempt)
    async def processed(queue):
        # Only Serve.merge may drive the admission algorithm; dispatch never substitutes for it.
        assert any(o.mutating is asyncio.current_task() and o.queue is queue for o in built)
        result = await process(queue)
        if result:
            admissions.extend(result)
        return result
    async def consuming(writer, ticket, result, *, attempt):
        assert writer.queue.active is None and not writer.queue._slot.locked()
        assert result in admissions
        consumed.append((ticket.stem, attempt))
        await consume(writer, ticket, result, attempt=attempt)
    monkeypatch.setattr(cli, "build_serve", building)
    monkeypatch.setattr(MergeQueue, "offer", offered)
    monkeypatch.setattr(MergeQueue, "process", processed)
    monkeypatch.setattr(TicketWriter, "consume_result", consuming)
    report = await soak.produce(tmp_path / "production")
    assert all(e.green for e in report.entries)
    assert len(built) == 4  # One interrupted worker lifetime, its restart, and two fault members.
    assert [(stem, attempt) for _, stem, attempt in offers] == consumed == [
        ("worker", 1), ("mechanical", 0), ("unresolved", 0), ("unresolved", 1), ("semantic", 0)]
    assert all(len(o.workers) == 4 and all(t.done() for t in o.workers) for o in built)


def test_daemon_soak_advances_each_member_24_hours(evidence):
    _, members = evidence
    for member in members:
        assert member.time.now - member.time.start >= timedelta(hours=24)
        assert len(member.cycles) == 5 and all(all(health) for _, health in member.cycles)
        assert member.time.steps.count(6 * 3600) == 5 and member.time.sleeps
        assert member.fs.heartbeats[-1] - member.fs.heartbeats[0] >= timedelta(hours=24)
        assert member.sweeps[-1][0] - member.sweeps[0][0] >= timedelta(hours=24)
        assert member.checkpoints[-1] - member.checkpoints[0] >= timedelta(hours=24)
        segments = list(member.journal.read_segments())
        assert len(segments) >= 2
        assert any(e.type == EventType.TIMER_FIRED for e in member.journal.read())
        assert any(e.key == "checkpoint-push/0" and e.type == EventType.EFFECT_COMPLETION
                   for e in member.journal.read())


def test_daemon_soak_worker_recovery(evidence):
    report, members = evidence
    worker = members[0]
    assert report.entries[0].producing_run == "worker/0"
    assert worker.interrupted[1] == b"interrupted fixture work\n"
    assert [e.body["to"] for e in worker.terminals("worker")] == ["abandoned", "merged"]
    events = worker.journal.read()
    [alert] = [e for e in events if e.body.get("kind") == RECOVERY_ALERT]
    assert alert.body == dict(kind=RECOVERY_ALERT, disposition="alert", outcome="abandoned",
                             reason="orphaned run", run_seq=0)
    [abandoned, merged] = worker.terminals("worker")
    assert events.index(abandoned) < events.index(alert) < events.index(merged)
    removal = next(history for stem, history in worker.exec.removals if stem == "worker")
    assert removal[-1] == alert
    assert worker.models[0].aborted and worker.harvest("worker", 0).terminal == "abandoned"
    assert (worker.root / "worker.txt").read_text() == "completed\n"
    assert audit_journal(worker.journal) == []


def test_daemon_soak_conflict_rungs(evidence):
    report, members = evidence
    member = members[1]
    assert report.entries[1].producing_run == "unresolved/1"
    assert member.facts("mechanical")[0].body["resolving_rung"] == "mechanical"
    assert member.facts("mechanical")[0].body["strategy_paths"] == ["union.txt"]
    assert member.facts("unresolved")[0].body["resolving_rung"] == "rework"
    assert member.facts("unresolved")[0].body["conflicted_paths"] == ["conflict.txt"]
    [(handoff, active, locked)] = member.handoffs
    assert handoff.approval_invalidated and active is None and not locked
    review = read_review((member.root / "tickets/unresolved/review.md").read_text())
    assert review.reviewed_sha != handoff.reviewed_sha
    assert [e.body["to"] for e in member.terminals("unresolved")] == ["gate_failed", "merged"]
    reports = [m for m in member.owner.box.messages() if m.stage == "merge"]
    assert {(m.origin, m.outcome) for m in reports} == {("mechanical", "ok"), ("unresolved", "gate_failed")}
    ids = {e.body["occurrence_id"] for e in member.journal.read() if e.body.get("kind") == "storm_occurrence"}
    assert {"mechanical/0/mechanical-conflict", "unresolved/0/unresolved-conflict"} <= ids
    assert all(m.status == "resolved" for m in reports)
    assert all(result[0] == 0 for _, result in member.main_checks)


def test_daemon_soak_semantic_red_preserves_main(evidence):
    report, members = evidence
    member = members[2]
    assert report.entries[2].producing_run == "semantic/0"
    assert member.inputs[0][1][0] == member.inputs[0][2][0] == 0
    assert member.refusals and all(head == member.admission_heads["semantic"] and result[0] == 0
        and a == b == b"1\n" for head, result, a, b in member.refusals)
    assert (member.root / "a.txt").read_bytes() == b"0\n"
    assert [e.body["to"] for e in member.terminals("semantic")] == ["gate_failed"]
    assert member.harvest("semantic", 0).stage == "merge"
    spool = member.checkout.config.state_dir / "spools/semantic/0/merge-integration/verify-01.txt"
    assert "[exit 1]" in spool.read_text() and "AssertionError" in spool.read_text()
    [message] = [m for m in member.owner.box.messages() if m.origin == "semantic"]
    assert message.outcome == "gate_failed" and spool.read_text() in message.summary


@pytest.mark.asyncio
@pytest.mark.parametrize("index,field", [(i, field) for i in range(3) for field in
    ("cycles", "health", "heartbeats", "sweeps", "checkpoints", "sleeps", "timer", "checkpoint",
     "rotation", "main", "checks", "review-custody")]
    + [(0, f) for f in ("alert", "alert-sequence", "abandoned", "interrupted", "removal", "merged", "review")]
    + [(1, f) for f in ("mechanical-facts", "unresolved-facts", "handoff", "handoff-unwind", "rework",
                        "mechanical-box", "unresolved-box", "box-outcome", "harvest", "regating", "review", "terminal-stage")]
    + [(2, f) for f in ("inputs", "refusal", "semantic-box", "harvest", "integration", "terminal", "semantic-facts")])
async def test_daemon_soak_requires_member_local_evidence(evidence, monkeypatch, index, field):
    _, members = evidence
    member = members[index]
    original_events = member.journal.read()
    file = None
    if field in {"cycles", "sweeps", "checkpoints", "interrupted"}:
        monkeypatch.setattr(member, field, None if field == "interrupted" else [])
    elif field == "health":
        monkeypatch.setattr(member, "cycles", [(moment, (True, False, True, True)) for moment, _ in member.cycles])
    elif field in {"inputs", "refusal", "handoff"}:
        monkeypatch.setattr(member, {"inputs": "inputs", "refusal": "refusals", "handoff": "handoffs"}[field], [])
    elif field == "handoff-unwind":
        handoff, _, _ = member.handoffs[0]
        monkeypatch.setattr(member, "handoffs", [(handoff, "unresolved", True)])
    elif field == "heartbeats":
        monkeypatch.setattr(member.fs, "heartbeats", [])
    elif field == "sleeps":
        monkeypatch.setattr(member.time, "sleeps", [])
    elif field == "rotation":
        monkeypatch.setattr(member.journal, "read_segments", lambda: iter([tuple(original_events)]))
    elif field == "removal":
        monkeypatch.setattr(member.exec, "removals", [])
    elif field.endswith("box"):
        stem = field.removesuffix("-box")
        messages = member.owner.box.messages()
        # A different member's report is deliberately present: it cannot substitute for this one.
        other = members[2 if index == 1 else 1].owner.box.messages()
        monkeypatch.setattr(member.owner.box, "messages", lambda: [m for m in messages if m.origin != stem] + other)
    elif field == "box-outcome":
        messages = member.owner.box.messages()
        monkeypatch.setattr(member.owner.box, "messages", lambda: [m.model_copy(update={"outcome": "ok"})
            if m.origin == "unresolved" else m for m in messages])
    elif field in {"main", "harvest", "integration", "regating", "review"}:
        stem = ("worker", "unresolved", "semantic")[index]
        relative = {"main": "a.txt", "harvest": f"tickets/{stem}/attempts/0/harvest.json",
                    "review": f"tickets/{stem}/review.md",
                    "integration": ".chupa/state/spools/semantic/0/merge-integration/verify-01.txt",
                    "regating": ".chupa/state/spools/mechanical/0/merge-integration/verify-01.txt"}[field]
        file = member.root / relative
        before = file.read_bytes()
        member.fs.write(file, b"2\n" if field == "main" else b"{}")
    else:
        run = (("worker", 1), ("mechanical", 0), ("semantic", 0))[index]
        def missing(e):
            body = e.body
            return ((field == "timer" and e.type == EventType.TIMER_FIRED)
                or (field == "checkpoint" and e.key == "checkpoint-push/0")
                or (field in {"alert", "alert-sequence"} and body.get("kind") == RECOVERY_ALERT)
                or (field == "abandoned" and body.get("to") == "abandoned")
                or (field == "merged" and body.get("to") == "merged")
                or (field == "terminal" and body.get("to") == "gate_failed")
                or (field == "mechanical-facts" and body.get("kind") == CONFLICT_FACTS and e.ticket == "mechanical")
                or (field == "unresolved-facts" and body.get("kind") == CONFLICT_FACTS and e.ticket == "unresolved")
                or (field == "semantic-facts" and body.get("kind") == CONFLICT_FACTS and e.ticket == "semantic")
                or (field == "rework" and body.get("signal") == "rework_order")
                or (field == "terminal-stage" and e.ticket == "unresolved" and body.get("to") == "gate_failed")
                or (field == "checks" and e.key == f"ticket-plane/{run[0]}/{run[1]}/checks")
                or (field == "review-custody" and e.key == f"ticket-plane/{run[0]}/{run[1]}/review"))
        altered = [e for e in original_events if not missing(e)]
        if field == "alert-sequence":
            from dataclasses import replace
            altered += [replace(e, body=e.body | {"run_seq": 1}) for e in original_events if missing(e)]
        if field == "terminal-stage":
            from dataclasses import replace
            altered += [replace(e, body=e.body | {"stage": "implement"}) for e in original_events if missing(e)]
        monkeypatch.setattr(member.journal, "read", lambda: altered)
    try:
        with pytest.raises((soak.SoakRefused, ValueError)):
            await soak._observe(member)
    finally:
        if file is not None:
            member.fs.write(file, before)


@pytest.mark.asyncio
async def test_daemon_soak_requires_member_local_evidence_auditor(tmp_path, monkeypatch):
    observe = soak._observe
    async def corrupt(member):
        member.journal.append(EventType.STATE_TRANSITION, {"to": "invented"})
        return await observe(member)
    monkeypatch.setattr(soak, "_observe", corrupt)
    with pytest.raises(soak.SoakRefused, match="worker_killed_mid_run.*closed_run_states"):
        await soak._run_member(tmp_path, DAEMON_SOAK_MEMBERS[0])


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["success", "failure", "cancellation"])
async def test_daemon_soak_cleans_up_owned_lifetimes(tmp_path, monkeypatch, case):
    members = []
    init = soak._Member.initialize
    async def initialized(member):
        members.append(member)
        await init(member)
    monkeypatch.setattr(soak._Member, "initialize", initialized)
    if case == "failure":
        async def fail(member):
            raise RuntimeError("scripted member failure")
        monkeypatch.setattr(soak._Member, "recurring", fail)
    baseline = asyncio.all_tasks()
    task = asyncio.create_task(soak._run_member(tmp_path, DAEMON_SOAK_MEMBERS[0]))
    if case == "cancellation":
        while not members or not members[0].entered.is_set():
            await soak._turn()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    elif case == "failure":
        with pytest.raises(soak.SoakRefused, match="scripted member failure"):
            await task
    else:
        assert (await task).green
    [member] = members
    assert member.task is None and not member.time.waits and member.journal._closed
    assert all(o.tasks.tasks == () and all(t.done() for t in o.workers) and not o.core.watcher._waits
               and o.core.admission.task is None for o in member.lifetimes)
    assert json.loads((member.checkout.config.state_dir / "control/active.json").read_text()) is None
    lock = Lockfile(member.checkout.config.state_dir, instance_id="cleanup-proof", clock=member.time)
    lock.acquire()
    lock.release()
    trees = await member.git._run(member.root, "worktree", "list", "--porcelain")
    assert sum(line.startswith("worktree ") for line in trees.splitlines()) == 1
    assert asyncio.all_tasks() == baseline


@pytest.mark.asyncio
async def test_daemon_soak_is_rederivable(tmp_path):
    first = await soak.produce(tmp_path / "first")
    second = await soak.produce(tmp_path / "second")
    assert first.model_dump_json(indent=2) == second.model_dump_json(indent=2)
    assert tuple(e.member for e in first.entries) == DAEMON_SOAK_MEMBERS
    assert not list(tmp_path.rglob("daemon-soak-report.json"))
