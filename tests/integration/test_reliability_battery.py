"""Closed evidence, production faults and existing checks custody for the battery."""

import asyncio
import copy
import json
import os
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import ValidationError

from chupa import artifacts, runner, stages
from chupa.audit import Violation
from chupa.git import Git
from chupa.journal import EventType
from chupa.seams import SubprocessExec
from chupa.specs import load_spec
from tests.harness import reliability_battery as battery

MEMBERS = battery.RELIABILITY_BATTERY_MEMBERS
EXPECTED = battery._RELIABILITY_BATTERY_EXPECTED


def report():
    return battery.ReliabilityBatteryReport(
        produced_by_spec_version=1,
        produced_at_sha="source",
        entries=[
            battery.ReliabilityBatteryEntry(member=m, planted_fault="fixture fault", expected=e, observed=e, producing_run=f"fixture-{i}/0", auditor=[], green=True)
            for i, (m, e) in enumerate(zip(MEMBERS, EXPECTED))
        ],
    )


def test_reliability_battery_schema_is_closed():
    assert battery.RELIABILITY_BATTERY_SPEC_VERSION == 1
    assert set(battery.ReliabilityBatteryEntry.model_fields) == {"member", "planted_fault", "expected", "observed", "producing_run", "auditor", "green"}
    assert set(battery.ReliabilityBatteryReport.model_fields) == {"artifact_schema_version", "produced_by_spec_version", "produced_at_sha", "entries"}
    data = report().model_dump()
    invalid = []
    for field, value in [
        ("member", "other"),
        ("planted_fault", " "),
        ("expected", "other"),
        ("observed", ""),
        ("producing_run", "bad/-1"),
        ("producing_run", "../x/0"),
        ("producing_run", "fixture/1.0"),
        ("auditor", [" "]),
        ("green", 1),
        ("green", "true"),
        ("observed", 1),
        ("auditor", "none"),
        ("auditor", [1]),
        ("producing_run", 1),
        ("planted_fault", True),
        ("extra", 1),
    ]:
        d = copy.deepcopy(data)
        d["entries"][0][field] = value
        invalid.append(d)
    for entries in ([], data["entries"][:-1], data["entries"][::-1], data["entries"] * 2, [data["entries"][0]] * 3):
        invalid.append({**data, "entries": entries})
    for field, value in [("artifact_schema_version", 2), ("artifact_schema_version", True), ("produced_by_spec_version", "1"), ("produced_at_sha", ""), ("extra", 1)]:
        invalid.append({**data, field: value})
    for d in invalid:
        with pytest.raises(ValidationError):
            battery.ReliabilityBatteryReport.model_validate(d)
    for version in (0, 1):
        assert battery.ReliabilityBatteryReport.model_validate({**data, "artifact_schema_version": version}).artifact_schema_version == version


def test_reliability_battery_green_requires_observation_and_auditor():
    data = report().entries[0].model_dump()
    for observed, auditor in [("missing", []), (EXPECTED[0], ["declared_cap: -: unknown cap"])]:
        entry = battery.ReliabilityBatteryEntry.model_validate({**data, "observed": observed, "auditor": auditor, "green": False})
        assert not entry.green
        with pytest.raises(ValidationError):
            battery.ReliabilityBatteryEntry.model_validate({**entry.model_dump(), "green": True})
    with pytest.raises(ValidationError):
        battery.ReliabilityBatteryEntry.model_validate({**data, "green": False})


async def member(tmp_path, index):
    m = battery._Member(tmp_path / MEMBERS[index], MEMBERS[index])
    try:
        await m.initialize()
        await m.exercise()
    finally:
        await m.stop()
    assert battery._observe(m).green
    return m


@pytest.mark.asyncio
async def test_classified_quota_exhaustion(tmp_path):
    m = await member(tmp_path, 0)
    entry = battery._observe(m)
    assert entry.observed == EXPECTED[0] and entry.producing_run == "quota-fault/0"
    assert m.exec.calls == [("codex", "codex-inherited", "implement", (17, "", "usage limit reached"))]
    assert len(m.session.timers.pending) == 1


@pytest.mark.asyncio
async def test_all_candidates_cooling_recovery(tmp_path):
    m = await member(tmp_path, 1)
    assert battery._observe(m).observed == EXPECTED[1]
    assert [c[:2] for c in m.exec.calls] == [("codex", "codex-inherited"), ("claude", "claude-pinned"), ("codex", "codex-inherited"), ("codex", "codex-inherited")]
    assert len(m.session.timers.fired) == len(m.session.timers.pending) == 1
    assert (m.root / "work.txt").read_text() == "recovered\n"
    assert all(w.ctx.driver.llm.session is m.session for w in m.writers)


@pytest.mark.asyncio
async def test_cooling_recovery_after_many_turns(tmp_path, monkeypatch):
    m = battery._Member(tmp_path / MEMBERS[1], MEMBERS[1])
    await m.initialize()
    dispatch = m.core.scheduler.dispatch_next
    turn = battery._turn
    release = asyncio.Event()
    calls = turns = 0

    async def delayed_dispatch():
        nonlocal calls
        calls += 1
        if calls == 5:
            await release.wait()
        return await dispatch()

    async def slowed_turn():
        nonlocal turns
        if calls == 5 and not release.is_set():
            turns += 1
            if turns > 100000:
                release.set()
        await turn()
        await asyncio.sleep(0)

    monkeypatch.setattr(m.core.scheduler, "dispatch_next", delayed_dispatch)
    monkeypatch.setattr(battery, "_turn", slowed_turn)
    try:
        await m.exercise()
    finally:
        await m.stop()
    assert turns > 100000
    assert battery._observe(m).observed == EXPECTED[1]


@pytest.mark.asyncio
async def test_unclassified_failure_preservation(tmp_path):
    m = await member(tmp_path, 2)
    assert battery._observe(m).observed == EXPECTED[2]
    assert len(m.exec.calls) == 1 and m.exec.calls[0][3] == (17, "", "alien failure 17")
    assert not m.session.timers.pending


@pytest.mark.asyncio
@pytest.mark.parametrize("index", range(3))
async def test_reliability_battery_requires_member_local_evidence(tmp_path, monkeypatch, index):
    m = await member(tmp_path, index)
    history = m.journal.read()
    # Every required fault/hold/recovery journal fact is independently removed or contradicted.
    required = [
        e
        for e in history
        if e.type in {EventType.TIMER_ARMED, EventType.TIMER_FIRED, EventType.STATE_TRANSITION}
        or e.body.get("signal") == "provider_call_outcome"
        or e.type == EventType.EFFECT_COMPLETION
        and (e.key.endswith("/harvest") or e.key.endswith("/run-record") or e.key.startswith("llm/"))
        or e.type == EventType.EFFECT_INTENT
        and e.key.startswith("llm/")
        or (e.type == EventType.CAP_CONSUMED and e.body.get("ticket_sha") != "seed")
    ]
    for event in required:
        altered = [e for e in history if e is not event]
        monkeypatch.setattr(m.journal, "read", lambda: altered)
        try:
            assert not battery._observe(m).green, event
        except battery.BatteryRefused:
            pass
    for event in required:
        body = copy.deepcopy(event.body)
        if event.type == EventType.TIMER_ARMED or event.type == EventType.TIMER_FIRED:
            body["deadline"] = "2026-01-01T23:59:00+00:00"
        elif event.body.get("signal") == "provider_call_outcome":
            body["failure_class"] = "auth_error"
        elif event.type == EventType.STATE_TRANSITION:
            body["to"] = "rejected"
        elif event.type == EventType.CAP_CONSUMED:
            body["cap"] = "retry"
        elif event.type == EventType.EFFECT_COMPLETION:
            if event.key.startswith("llm/"):
                body["result"]["provider"] = "foreign"
            else:
                body["result"]["paths"] = ["tickets/foreign/run.md"]
        else:
            body = None
        changed = replace(event, body=body) if body is not None else replace(event, key="foreign/key")
        altered = [changed if e is event else e for e in history]
        monkeypatch.setattr(m.journal, "read", lambda: altered)
        try:
            assert not battery._observe(m).green, event
        except battery.BatteryRefused:
            pass
    monkeypatch.setattr(m.journal, "read", lambda: history)
    for path in list((m.root / "tickets").rglob("harvest.json")) + list((m.root / "tickets").rglob("run.md")):
        original = path.read_bytes()
        path.unlink()
        with pytest.raises(battery.BatteryRefused):
            battery._observe(m)
        m.fs.write(path, original)
        m.fs.write(path, original.replace(b"codex", b"alien").replace(b"claude", b"alien"))
        with pytest.raises((battery.BatteryRefused, ValidationError)):
            battery._observe(m)
        m.fs.write(path, original)
    foreign = replace(history[0], ticket="foreign-fault")
    monkeypatch.setattr(m.journal, "read", lambda: [foreign, *history[1:]])
    with pytest.raises(battery.BatteryRefused, match="cross-member"):
        battery._observe(m)
    monkeypatch.setattr(m.journal, "read", lambda: history)
    violations = [Violation("declared_cap", None, "bad cap"), Violation("one_terminal_per_run", m.fault, "bad run")]
    real_audit_journal = battery.audit_journal
    monkeypatch.setattr(battery, "audit_journal", lambda _: violations)
    entry = battery._observe(m)
    assert not entry.green and entry.auditor == ["declared_cap: -: bad cap", f"one_terminal_per_run: {m.fault}: bad run"]
    monkeypatch.setattr(battery, "audit_journal", real_audit_journal)
    assert battery._observe(m).green
    fault_outcome = next(e for e in history if e.ticket == m.fault and e.body.get("signal") == "provider_call_outcome")
    monkeypatch.setattr(m.journal, "read", lambda: [e for e in history if e is not fault_outcome])
    assert real_audit_journal(m.journal) == []
    m.success = m.auditor = True
    with pytest.raises(battery.BatteryRefused, match="extra/missing executed call or inline retry"):
        battery._observe(m)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["success", "failure", "cancellation"])
async def test_reliability_battery_cleans_up_owned_lifetimes(tmp_path, monkeypatch, mode):
    original = battery._Member
    created = []

    def construct(*args):
        m = original(*args)
        created.append(m)
        if mode == "failure":

            async def fail():
                await m.add(m.fault)
                writer = await runner.prepare_pipeline(m.checkout)
                m.writers.append(writer)
                await stages.prepare_worktree(writer.ctx, m.fault)
                raise ValueError("planted harness failure")

            m.exercise = fail
        if mode == "cancellation":
            m.exec.block = True
        return m

    monkeypatch.setattr(battery, "_Member", construct)
    task = asyncio.create_task(battery._run_member(tmp_path, MEMBERS[0]))
    if mode == "cancellation":
        while not created or not created[0].exec.entered.is_set():
            await battery._turn()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    elif mode == "failure":
        with pytest.raises(battery.BatteryRefused):
            await task
    else:
        assert (await task).green
    [m] = created
    assert m.closed and not m.time.waits and not m.session.waits
    assert m.core.admission.task is None and all(w.ctx.driver._active is None for w in m.writers)
    trees = await m.git._run(m.root, "worktree", "list", "--porcelain")
    assert sum(line.startswith("worktree ") for line in trees.splitlines()) == 1
