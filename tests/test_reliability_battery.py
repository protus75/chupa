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
from eval import reliability_battery as battery

MEMBERS = artifacts.RELIABILITY_BATTERY_MEMBERS
EXPECTED = artifacts._RELIABILITY_BATTERY_EXPECTED


def report():
    return artifacts.ReliabilityBatteryReport(produced_by_spec_version=1, produced_at_sha='source',
        entries=[artifacts.ReliabilityBatteryEntry(member=m, planted_fault='fixture fault', expected=e,
            observed=e, producing_run=f'fixture-{i}/0', auditor=[], green=True)
            for i, (m, e) in enumerate(zip(MEMBERS, EXPECTED))])


def test_reliability_battery_schema_is_closed():
    assert artifacts.RELIABILITY_BATTERY_REPORT == 'reliability-battery-report.json'
    assert artifacts.RELIABILITY_BATTERY_SPEC_VERSION == 1
    assert set(artifacts.ReliabilityBatteryEntry.model_fields) == {
        'member', 'planted_fault', 'expected', 'observed', 'producing_run', 'auditor', 'green'}
    assert set(artifacts.ReliabilityBatteryReport.model_fields) == {
        'artifact_schema_version', 'produced_by_spec_version', 'produced_at_sha', 'entries'}
    data = report().model_dump()
    invalid = []
    for field, value in [('member', 'other'), ('planted_fault', ' '), ('expected', 'other'),
                         ('observed', ''), ('producing_run', 'bad/-1'), ('producing_run', '../x/0'),
                         ('producing_run', 'fixture/1.0'), ('auditor', [' ']), ('green', 1),
                         ('green', 'true'), ('observed', 1), ('auditor', 'none'), ('auditor', [1]),
                         ('producing_run', 1), ('planted_fault', True), ('extra', 1)]:
        d = copy.deepcopy(data); d['entries'][0][field] = value; invalid.append(d)
    for entries in ([], data['entries'][:-1], data['entries'][::-1], data['entries'] * 2,
                    [data['entries'][0]] * 3):
        invalid.append({**data, 'entries': entries})
    for field, value in [('artifact_schema_version', 2), ('artifact_schema_version', True),
                         ('produced_by_spec_version', '1'), ('produced_at_sha', ''), ('extra', 1)]:
        invalid.append({**data, field: value})
    for d in invalid:
        with pytest.raises(ValidationError):
            artifacts.ReliabilityBatteryReport.model_validate(d)
    for version in (0, 1):
        assert artifacts.ReliabilityBatteryReport.model_validate({**data,
            'artifact_schema_version': version}).artifact_schema_version == version


def test_reliability_battery_green_requires_observation_and_auditor():
    data = report().entries[0].model_dump()
    for observed, auditor in [('missing', []), (EXPECTED[0], ['declared_cap: -: unknown cap'])]:
        entry = artifacts.ReliabilityBatteryEntry.model_validate({**data, 'observed': observed,
                                                                'auditor': auditor, 'green': False})
        assert not entry.green
        with pytest.raises(ValidationError):
            artifacts.ReliabilityBatteryEntry.model_validate({**entry.model_dump(), 'green': True})
    with pytest.raises(ValidationError):
        artifacts.ReliabilityBatteryEntry.model_validate({**data, 'green': False})


class FS:
    def __init__(self): self.writes = []
    def write(self, path, data): self.writes.append((path, data))


def test_reliability_battery_writer_validates_before_write(tmp_path):
    fs = FS(); path = tmp_path / 'report.json'; good = report()
    battery.write_report(path, good, fs)
    assert fs.writes == [(path, (good.model_dump_json(indent=2) + '\n').encode('utf-8'))]
    assert not path.exists()
    for bad in [good.model_copy(update={'entries': []}),
                good.model_copy(update={'entries': [good.entries[0].model_copy(update={'green': False}),
                                                    *good.entries[1:]]}),
                good.model_copy(update={'entries': [good.entries[0].model_copy(
                    update={'observed': 'missing', 'green': False}), *good.entries[1:]]})]:
        fs.writes.clear()
        with pytest.raises(ValueError): battery.write_report(path, bad, fs)
        assert not fs.writes


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
    assert entry.observed == EXPECTED[0] and entry.producing_run == 'quota-fault/0'
    assert m.exec.calls == [('codex', 'codex-inherited', 'implement', (17, '', 'usage limit reached'))]
    assert len(m.session.timers.pending) == 1
    assert not list(tmp_path.rglob(artifacts.RELIABILITY_BATTERY_REPORT))


@pytest.mark.asyncio
async def test_all_candidates_cooling_recovery(tmp_path):
    m = await member(tmp_path, 1)
    assert battery._observe(m).observed == EXPECTED[1]
    assert [c[:2] for c in m.exec.calls] == [('codex', 'codex-inherited'), ('claude', 'claude-pinned'),
                                          ('codex', 'codex-inherited'), ('codex', 'codex-inherited')]
    assert len(m.session.timers.fired) == len(m.session.timers.pending) == 1
    assert (m.root / 'work.txt').read_text() == 'recovered\n'
    assert all(w.ctx.driver.llm.session is m.session for w in m.writers)


@pytest.mark.asyncio
async def test_unclassified_failure_preservation(tmp_path):
    m = await member(tmp_path, 2)
    assert battery._observe(m).observed == EXPECTED[2]
    assert len(m.exec.calls) == 1 and m.exec.calls[0][3] == (17, '', 'alien failure 17')
    assert not m.session.timers.pending


@pytest.mark.asyncio
@pytest.mark.parametrize('index', range(3))
async def test_reliability_battery_requires_member_local_evidence(tmp_path, monkeypatch, index):
    m = await member(tmp_path, index)
    history = m.journal.read()
    # Every required fault/hold/recovery journal fact is independently removed or contradicted.
    required = [e for e in history if e.type in {EventType.TIMER_ARMED, EventType.TIMER_FIRED,
        EventType.STATE_TRANSITION} or e.body.get('signal') == 'provider_call_outcome'
        or e.type == EventType.EFFECT_COMPLETION and (e.key.endswith('/harvest')
        or e.key.endswith('/run-record') or e.key.startswith('llm/'))
        or e.type == EventType.EFFECT_INTENT and e.key.startswith('llm/')
        or e.type == EventType.CAP_CONSUMED]
    for event in required:
        altered = [e for e in history if e is not event]
        monkeypatch.setattr(m.journal, 'read', lambda: altered)
        try:
            assert not battery._observe(m).green, event
        except battery.BatteryRefused:
            pass
    for event in required:
        body = copy.deepcopy(event.body)
        if event.type == EventType.TIMER_ARMED or event.type == EventType.TIMER_FIRED:
            body['deadline'] = '2026-01-01T23:59:00+00:00'
        elif event.body.get('signal') == 'provider_call_outcome':
            body['failure_class'] = 'auth_error'
        elif event.type == EventType.STATE_TRANSITION:
            body['to'] = 'rejected'
        elif event.type == EventType.CAP_CONSUMED:
            body['cap'] = 'retry'
        elif event.type == EventType.EFFECT_COMPLETION:
            if event.key.startswith('llm/'):
                body['result']['provider'] = 'foreign'
            else:
                body['result']['paths'] = ['tickets/foreign/run.md']
        else:
            body = None
        changed = replace(event, body=body) if body is not None else replace(event, key='foreign/key')
        altered = [changed if e is event else e for e in history]
        monkeypatch.setattr(m.journal, 'read', lambda: altered)
        try:
            assert not battery._observe(m).green, event
        except battery.BatteryRefused:
            pass
    monkeypatch.setattr(m.journal, 'read', lambda: history)
    for path in list((m.root / 'tickets').rglob('harvest.json')) + list((m.root / 'tickets').rglob('run.md')):
        original = path.read_bytes(); path.unlink()
        with pytest.raises(battery.BatteryRefused): battery._observe(m)
        m.fs.write(path, original)
        m.fs.write(path, original.replace(b'codex', b'alien').replace(b'claude', b'alien'))
        with pytest.raises((battery.BatteryRefused, ValidationError)): battery._observe(m)
        m.fs.write(path, original)
    foreign = replace(history[0], ticket='foreign-fault')
    monkeypatch.setattr(m.journal, 'read', lambda: [foreign, *history[1:]])
    with pytest.raises(battery.BatteryRefused, match='cross-member'): battery._observe(m)
    monkeypatch.setattr(m.journal, 'read', lambda: history)
    violations = [Violation('declared_cap', None, 'bad cap'), Violation('one_terminal_per_run', m.fault, 'bad run')]
    real_audit_journal = battery.audit_journal
    monkeypatch.setattr(battery, 'audit_journal', lambda _: violations)
    entry = battery._observe(m)
    assert not entry.green and entry.auditor == ['declared_cap: -: bad cap',
                                               f'one_terminal_per_run: {m.fault}: bad run']
    monkeypatch.setattr(battery, 'audit_journal', real_audit_journal)
    assert battery._observe(m).green
    fault_outcome = next(e for e in history if e.ticket == m.fault
                         and e.body.get('signal') == 'provider_call_outcome')
    monkeypatch.setattr(m.journal, 'read', lambda: [e for e in history if e is not fault_outcome])
    assert real_audit_journal(m.journal) == []
    m.success = m.auditor = True
    with pytest.raises(battery.BatteryRefused, match='extra/missing executed call or inline retry'):
        battery._observe(m)


@pytest.mark.asyncio
@pytest.mark.parametrize('mode', ['success', 'failure', 'cancellation'])
async def test_reliability_battery_cleans_up_owned_lifetimes(tmp_path, monkeypatch, mode):
    original = battery._Member
    created = []
    def construct(*args):
        m = original(*args); created.append(m)
        if mode == 'failure':
            async def fail():
                await m.add(m.fault)
                writer = await runner.prepare_pipeline(m.checkout)
                m.writers.append(writer)
                await stages.prepare_worktree(writer.ctx, m.fault)
                raise ValueError('planted harness failure')
            m.exercise = fail
        if mode == 'cancellation': m.exec.block = True
        return m
    monkeypatch.setattr(battery, '_Member', construct)
    task = asyncio.create_task(battery._run_member(tmp_path, MEMBERS[0]))
    if mode == 'cancellation':
        while not created or not created[0].exec.entered.is_set(): await battery._turn()
        task.cancel()
        with pytest.raises(asyncio.CancelledError): await task
    elif mode == 'failure':
        with pytest.raises(battery.BatteryRefused): await task
    else: assert (await task).green
    [m] = created
    assert m.closed and not m.time.waits and not m.session.waits
    assert m.core.admission.task is None and all(w.ctx.driver._active is None for w in m.writers)
    trees = await m.git._run(m.root, 'worktree', 'list', '--porcelain')
    assert sum(line.startswith('worktree ') for line in trees.splitlines()) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('case', ['current', 'invalid', 'missing', 'stale', 'inherited', 'equal-copy'])
async def test_reliability_battery_uses_registered_checks_lift(tmp_path, case):
    assert stages.KNOWN_ARTIFACTS[artifacts.RELIABILITY_BATTERY_REPORT] is artifacts.ReliabilityBatteryReport
    m = battery._Member(tmp_path / 'custody', MEMBERS[0]); await m.initialize()
    name = artifacts.RELIABILITY_BATTERY_REPORT; rel = f'tickets/producer/{name}'
    try:
        ticket = await m.add('producer')
        source = b'{"invalid": true}' if case == 'invalid' else (report().model_dump_json() + '\n').encode()
        m.fs.write(m.root / 'source.json', source)
        if case in {'inherited', 'equal-copy'}: m.fs.write(m.root / rel, source)
        await m.git.add(m.root, ['source.json', *([rel] if case in {'inherited', 'equal-copy'} else [])])
        await m.git.commit(m.root, 'custody source')
        code = f"from pathlib import Path; Path({rel!r}).write_bytes(Path('source.json').read_bytes())"
        command = (sys.executable, '-c', code) if case in {'current', 'invalid', 'equal-copy'} else (
            sys.executable, '-c', 'pass', '--out', rel)
        ticket = replace(ticket, verification=(command,))
        writer = await runner.prepare_pipeline(m.checkout)
        m.writers.append(writer); ctx = writer.ctx
        worktree = await stages.prepare_worktree(ctx, 'producer')
        reply = stages.ImplementReply(outcome='ok', summary='fixture', surprises='none', dead_ends='none',
                                      predicted_vs_actual='none', findings=[])
        spec = load_spec((ctx.specs_dir / 'implement.md').read_text())
        m.fs.write(m.root / 'tickets/producer/run.md', stages.run_record(reply, artifacts.Cost(), spec, []).encode())
        if case == 'stale':
            m.fs.write(worktree / rel, source)
            assert await stages.lift_outbox(ctx, 'producer', 'run-record', attempt=0) is None
            assert not (m.root / rel).exists()
        if case == 'equal-copy':
            assert await stages.lift_outbox(ctx, 'producer', 'checks', attempt=0) is None
        slip = stages.PackingSlip(produced_by_spec_version=1, produced_at_sha='fixture', stem='producer',
            branch='producer', outcome='ok', summary='fixture', run_record='tickets/producer/run.md')
        result = await stages.check(ctx, ticket, slip, attempt=0)
        assert result.outcome == ('ok' if case == 'current' else 'gate_failed')
        lifts = [e for e in m.journal.read() if e.type == EventType.EFFECT_COMPLETION
                 and e.key == 'ticket-plane/producer/0/checks']
        if case == 'current':
            assert lifts[0].body['result']['paths'] == ['tickets/producer/checks.json', rel]
            assert artifacts.ReliabilityBatteryReport.model_validate_json((m.root / rel).read_bytes()) == report()
        if case == 'invalid':
            assert not lifts and not (m.root / 'tickets/producer/checks.json').exists()
        if case in {'stale', 'inherited'}: assert not (worktree / rel).exists()
    finally: await m.stop()


@pytest.mark.asyncio
async def test_reliability_battery_command_writes_only_on_green(tmp_path, monkeypatch, capsys):
    target = tmp_path / 'report.json'
    rc, out, err = await SubprocessExec().run(['uv', 'run', 'python', '-m', 'eval.reliability_battery',
        '--out', str(target)], cwd=Path.cwd(), env=os.environ, timeout=60)
    assert rc == 0, err
    produced = artifacts.ReliabilityBatteryReport.model_validate_json(target.read_bytes())
    sha = await Git(SubprocessExec(), env=os.environ, timeout=30).rev_parse(Path.cwd(), 'HEAD')
    assert produced.produced_at_sha == sha and produced.produced_by_spec_version == 1
    assert all(e.green for e in produced.entries)
    target.unlink()
    async def red(_):
        r = report(); entry = r.entries[1].model_copy(update={'observed': 'missing', 'green': False})
        return r.model_copy(update={'entries': [r.entries[0], entry, r.entries[2]]})
    monkeypatch.setattr(battery, 'write_report', lambda *_: pytest.fail('writer called for incomplete/red battery'))
    monkeypatch.setattr(battery, 'produce', red)
    assert await battery._main(['--out', str(target)]) == 1 and not target.exists()
    message = capsys.readouterr().err
    assert MEMBERS[1] in message and 'repair' in message and 'uv run python -m eval.reliability_battery --out <path>' in message
    async def refused(_): raise battery.BatteryRefused(MEMBERS[2], 'missing error evidence')
    monkeypatch.setattr(battery, 'produce', refused)
    assert await battery._main(['--out', str(target)]) == 1 and not target.exists()
    message = capsys.readouterr().err
    assert MEMBERS[2] in message and 'missing error evidence' in message and 'rerun' in message
    # The production import graph has no battery call or import; both import idioms are examined.
    import ast
    for path in Path('chupa').glob('*.py'):
        tree = ast.parse(path.read_text())
        assert not any(isinstance(n, ast.Import) and any('reliability_battery' in a.name for a in n.names)
            or isinstance(n, ast.ImportFrom) and ('reliability_battery' in (n.module or '')
                or any(a.name == 'reliability_battery' for a in n.names)) for n in ast.walk(tree))
