"""Closed, disposable production provider battery (19.P4.reliability-battery)."""

import argparse
import asyncio
import json
import os
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from chupa import __main__ as cli, runner
from chupa.artifacts import (Harvest, RELIABILITY_BATTERY_MEMBERS, _RELIABILITY_BATTERY_EXPECTED,
    RELIABILITY_BATTERY_SPEC_VERSION, ReliabilityBatteryEntry, ReliabilityBatteryReport)
from chupa.audit import audit_journal
from chupa.config import load_config
from chupa.git import Git
from chupa.journal import EventType, Journal, render_ts, run_terminals
from chupa.lockfile import Lockfile
from chupa.providers import PROBE_PROMPT
from chupa.seams import FileSystem, LocalFileSystem, SubprocessExec
from chupa.tickets import intake, validate_ticket
from eval.daemon_soak import _Time, _turn


class BatteryRefused(ValueError):
    def __init__(self, member, detail):
        super().__init__(f"{member}: {detail}; repair this member's production evidence and rerun "
                         "uv run python -m eval.reliability_battery --out <path>")


def write_report(path: Path, report: ReliabilityBatteryReport, fs: FileSystem) -> None:
    validated = ReliabilityBatteryReport.model_validate(report.model_dump())
    for entry in validated.entries:
        if not entry.green:
            raise BatteryRefused(entry.member, f"red observation {entry.observed}; auditor {entry.auditor}")
    fs.write(path, (validated.model_dump_json(indent=2) + "\n").encode("utf-8"))


class _Exec:
    """Script only provider CLI transport; Git and fixture verification execute normally."""

    def __init__(self, member):
        self.member = member
        self.real = SubprocessExec()
        self.calls = []
        self.entered = asyncio.Event()
        self.block = False

    async def run(self, argv, *, cwd, env, timeout, stdin_path=None, on_spawn=None, on_stdout_line=None):
        argv = list(argv)
        if argv[0] not in {'codex', 'claude', 'pnpm'}:
            return await self.real.run(argv, cwd=cwd, env=env, timeout=timeout,
                stdin_path=stdin_path, on_spawn=on_spawn, on_stdout_line=on_stdout_line)
        if argv[0] == 'pnpm' or argv[1:] == ['--version']:
            return 0, '1.2.3', ''
        prompt = stdin_path.read_text()
        if prompt == PROBE_PROMPT:
            reply = 'ok'
        else:
            self.entered.set()
            if self.block:
                await asyncio.get_running_loop().create_future()
            surface = next(s for s in ('review', 'diagnose', 'implement')
                           if f'<<chupa-data:begin {"diff" if s == "review" else "harvest" if s == "diagnose" else "ticket"}>>' in prompt)
            model_flag = '-m' if argv[0] == 'codex' else '--model'
            model = argv[argv.index(model_flag) + 1]
            if surface == 'implement' and self.member.failures:
                failure = self.member.failures.pop(0)
                result = (17, '', failure)
                self.calls.append((argv[0], model, surface, result))
                return result
            if surface == 'implement':
                self.member.fs.write(cwd / 'work.txt', b'recovered\n')
                await self.member.git.add(cwd, ['work.txt'])
                await self.member.git.commit(cwd, 'scripted recovered implementation')
                reply = json.dumps(dict(outcome='ok', summary='Recovered fixture', surprises='none',
                    dead_ends='none', predicted_vs_actual='none', findings=[], second_problems=[]))
            elif surface == 'review':
                reply = json.dumps(dict(verdict='approve', summary='Fixture reviewed', findings=[]))
            else:
                reply = json.dumps(dict(verdict='abandon-human', lessons=['Inspect captured failure']))
        if argv[0] == 'codex':
            out = '\n'.join(json.dumps(e) for e in (
                dict(type='item.completed', item=dict(type='agent_message', text=reply)),
                dict(type='turn.completed', usage=dict(input_tokens=1, output_tokens=1)))) + '\n'
        else:
            out = json.dumps(dict(type='result', subtype='success', is_error=False,
                                  result=reply, total_cost_usd=0.0)) + '\n'
        if on_stdout_line:
            for line in out.splitlines(keepends=True):
                on_stdout_line(line)
        result = (0, out, '')
        if prompt != PROBE_PROMPT:
            self.calls.append((argv[0], model, surface, result))
        return result

    def kill_group(self, pgid):
        self.real.kill_group(pgid)


class _Member:
    def __init__(self, root, name):
        self.root, self.name = root, name
        self.fault = ("quota-fault", "cooling-fault", "unknown-fault")[RELIABILITY_BATTERY_MEMBERS.index(name)]
        self.time = _Time()
        self.fs = LocalFileSystem()
        self.journal = Journal(root / '.chupa/state', self.time)
        self.exec = _Exec(self)
        self.env = dict(PATH=os.defpath, HOME='/nonexistent', GIT_CONFIG_NOSYSTEM='1',
            GIT_CONFIG_GLOBAL='/dev/null', GIT_AUTHOR_NAME='battery', GIT_AUTHOR_EMAIL='battery@example.invalid',
            GIT_COMMITTER_NAME='battery', GIT_COMMITTER_EMAIL='battery@example.invalid')
        self.git = Git(self.exec, env=self.env, timeout=30)
        self.failures = ['alien failure 17'] if name == RELIABILITY_BATTERY_MEMBERS[2] else ['usage limit reached']
        if name == RELIABILITY_BATTERY_MEMBERS[1]:
            self.failures.append('quota exhausted')
        self.writers = []
        self.hold = None
        self.closed = False
        self.lock = None

    async def initialize(self):
        self.root.mkdir(parents=True)
        providers = [dict(name=name, kind='cli', package='fixture-cli',
            models_by_tier=dict.fromkeys(('low', 'medium', 'high', 'max'), f'{name}-inherited'),
            limits=dict(concurrency=1, quota_window_minutes=window, est_cost_per_call_usd=0.0))
            for name, window in (('codex', 1), ('claude', 2))]
        config = dict(schema_version=1, state_dir='.chupa/state', worktree_root='.chupa/worktrees',
            providers=providers, routing=[dict(tier='medium', surface=s,
                candidates=[dict(provider='codex'), dict(provider='claude', model='claude-pinned')])
                for s in ('implement', 'review')], caps=dict(infra=1),
            review=dict(mechanical=[dict(code='fixture', argv=[sys.executable, 'verify.py'],
                trigger='always', severity='hard')]), merge=dict(safety_checks=['fixture']),
            engine_plane_safety_inventory=['config.yaml'])
        files = {'config.yaml': yaml.safe_dump(config), '.gitignore': '.chupa/\n',
                 'CHUPA_PLAN.md': '# Disposable battery plan\n', 'work.txt': 'base\n',
                 'verify.py': "from pathlib import Path\nassert Path('work.txt').read_text().strip() in {'base', 'recovered'}\n"}
        for path, data in files.items():
            self.fs.write(self.root / path, data.encode())
        await self.git.init(self.root, branch='main')
        await self.git.add(self.root, list(files))
        await self.git.commit(self.root, 'disposable battery baseline')
        checkout = runner.Checkout(self.root, load_config(None, cwd=self.root), self.env,
            self.exec, self.git, self.journal, self.fs, self.time, self.time.sleep)
        async def prepare(local):
            writer = await runner.prepare_pipeline(local)
            self.writers.append(writer)
            return writer
        self.owner = cli.build_serve(checkout, plan=files['CHUPA_PLAN.md'], prepare=prepare)
        self.core = self.owner.core
        self.checkout = self.owner.checkout
        self.session = self.core.control.providers
        self.lock = Lockfile(checkout.config.state_dir, instance_id='battery', clock=self.time)
        self.lock.acquire()
        await self.core.startup()

    async def add(self, stem):
        raw = ("---\nstate: confirmed\nsource: human\npriority: P2\nkind: feature\n---\n\n"
            "## Depends on\nnone\n\n## Context\n- verify.py\n\n## Goal / Why\nExercise fixture.\n\n"
            "## Scope in / Scope out\nIn: fixture work. Out: live work.\n\n## Scope fence\n- work.txt\n\n"
            f"## Acceptance criteria\n1. `{sys.executable} verify.py` exits 0.\n\n## Verification\n```\n"
            f"{sys.executable} verify.py\n```\n\n## Definition of rejected\nRequires live work.\n\n"
            "## Time budget\n- expected: 1m\n- stuck: 20m\n")
        self.fs.write(self.root / f'tickets/{stem}/ticket.md', raw.encode())
        await intake(self.root, self.git, self.journal, self.fs)
        ticket = validate_ticket(stem, raw, self.root)
        self.core.scheduler.update(ticket)
        return ticket

    async def dispatch(self, stem):
        await self.add(stem)
        return await self.core.scheduler.dispatch_next()

    async def exercise(self):
        await self.dispatch(self.fault)
        if self.name == RELIABILITY_BATTERY_MEMBERS[1]:
            await self.dispatch('cooling-second')
            await self.dispatch('cooling-recovery')
            self.hold = tuple(self.journal.read())
            self.held_calls = tuple(self.exec.calls)
            if await self.core.scheduler.dispatch_next() is not None:
                raise BatteryRefused(self.name, 'drought did not remain held')
            deadline = min(self.session.cooling().values())
            wait = asyncio.create_task(self.session.wait_until(deadline))
            try:
                await _turn()
                self.time.advance((deadline - self.time()).total_seconds())
                await wait
            finally:
                wait.cancel()
                await asyncio.gather(wait, return_exceptions=True)
            dispatch = asyncio.create_task(self.core.scheduler.dispatch_next())
            try:
                for _ in range(100000):
                    if self.owner.queue.pending:
                        break
                    if dispatch.done():
                        dispatch.result()
                        raise BatteryRefused(self.name, 'recovery never offered merge')
                    await _turn()
                else:
                    raise BatteryRefused(self.name, 'recovery merge offer missing')
                await self.finish_recovery(dispatch)
            finally:
                dispatch.cancel()
                await asyncio.gather(dispatch, return_exceptions=True)

    async def finish_recovery(self, dispatch):
        merger = asyncio.create_task(self.owner.merge())
        try:
            for _ in range(100000):
                if dispatch.done():
                    break
                if merger.done():
                    merger.result()
                await _turn()
            else:
                raise BatteryRefused(self.name, 'recovery did not complete')
        finally:
            merger.cancel()
            await asyncio.gather(merger, return_exceptions=True)
        await dispatch

    async def stop(self):
        from chupa.daemon import _protected_cleanup
        async def cleanup():
            try:
                for writer in self.writers:
                    await writer.abort_current()
                if hasattr(self, 'session'):
                    await self.session.close()
                if hasattr(self, 'checkout'):
                    trees = await self.git._run(self.root, 'worktree', 'list', '--porcelain')
                    for line in trees.splitlines():
                        if line.startswith('worktree '):
                            path = Path(line.removeprefix('worktree '))
                            if path != self.root:
                                await self.git.worktree_remove(self.root, path)
            finally:
                if self.lock:
                    self.lock.release()
                self.closed = True
        await _protected_cleanup(asyncio.create_task(cleanup()))


def _observe(m):
    """Award observations only from this member's full journal and durable production harvests."""
    def need(condition, detail):
        if not condition:
            raise BatteryRefused(m.name, detail)
    need(m.closed and not m.time.waits and not m.session.waits
         and all(w.ctx.driver._active is None for w in m.writers), 'owned lifetimes still active')
    need(m.journal.dir == m.root / '.chupa/state/journal', 'cross-member journal')
    events = m.journal.read()
    allowed = {m.fault, 'cooling-second', 'cooling-recovery'} if m.name == RELIABILITY_BATTERY_MEMBERS[1] else {m.fault}
    need(all(e.ticket is None or e.ticket in allowed for e in events), 'cross-member evidence')
    index = RELIABILITY_BATTERY_MEMBERS.index(m.name)
    fault_stems = [m.fault, 'cooling-second'] if index == 1 else [m.fault]
    quota = index != 2
    outcomes = [e for e in events if e.body.get('signal') == 'provider_call_outcome']
    need(len(outcomes) == (4 if index == 1 else 1) and len(m.exec.calls) == len(outcomes),
         'extra/missing executed call or inline retry')
    need([e.body.get('cap') for e in events if e.type == EventType.CAP_CONSUMED]
         == ([] if quota else ['infra']), 'contradictory member infra accounting')
    for stem, provider in zip(fault_stems, ('codex', 'claude')):
        rows = [e for e in outcomes if e.ticket == stem]
        need(len(rows) == 1 and rows[0].body.get('provider') == provider
             and rows[0].body.get('call_key') == f'llm/{stem}/0/implement/0/1'
             and rows[0].body.get('failure_class') == ('quota_exhausted' if quota else 'unclassified'),
             f'{stem}/0 classification/attempt identity missing or contradictory')
        call_key = f'llm/{stem}/0/implement/0/1'
        need(sum(e.type == EventType.EFFECT_INTENT and e.key == call_key for e in events) == 1
             and not any(e.type == EventType.EFFECT_COMPLETION and e.key == call_key for e in events),
             f'{stem}/0 failed call intent/completion contradiction')
        for kind, path in (('run-record', f'tickets/{stem}/run.md'),
                           ('harvest', f'tickets/{stem}/attempts/0/harvest.json')):
            custody = [e for e in events if e.type == EventType.EFFECT_COMPLETION
                       and e.key == f'ticket-plane/{stem}/0/{kind}']
            need(len(custody) == 1 and custody[0].body.get('result', {}).get('paths') == [path]
                 and custody[0].body['result'].get('commit'), f'{stem}/0 {kind} custody missing')
        need(sum(e.ticket == stem and e.body.get('to') == 'running' for e in events) == 1,
             f'{stem}/0 running attempt missing')
        terms = run_terminals(events, stem)
        need(len(terms) == 1 and terms[0].body.get('to') == 'infra_error'
             and terms[0].body.get('stage') == 'implement'
             and terms[0].body.get('reason') == ('quota_exhausted' if quota else 'infra_error'), f'{stem}/0 harvested terminal missing')
        path = m.root / f'tickets/{stem}/attempts/0/harvest.json'
        need(path.is_file(), f'{stem}/0 harvest missing')
        harvest = Harvest.model_validate_json(path.read_bytes())
        need(harvest.attempt == 0 and harvest.stage == 'implement' and harvest.terminal == 'infra_error'
             and harvest.run_record == f'tickets/{stem}/run.md', f'{stem}/0 harvest identity wrong')
        model = 'codex-inherited' if provider == 'codex' else 'claude-pinned'
        record = m.root / harvest.run_record
        need(record.is_file() and f'- provider: {provider}\n- model: {model}' in record.read_text(),
             f'{stem}/0 served run identity missing')
        calls = [c for c in m.exec.calls if c[2] == 'implement' and c[3][0] != 0]
        need(len(calls) == len(fault_stems) and calls[fault_stems.index(stem)][:2] == (provider, model),
             'ordered fault calls missing or inline retry')
        caps = [e for e in events if e.ticket == stem and e.type == EventType.CAP_CONSUMED]
        arms = [e for e in events if e.type == EventType.TIMER_ARMED
                and e.body.get('timer_id', '').startswith(f'provider-cooldown/{provider}/')]
        need(f'{provider}:' in harvest.stage_log_tail, f'{stem}/0 provider error capture missing')
        if quota:
            need([f.code for f in harvest.findings] == ['quota_exhausted']
                 and f'{provider}:' in harvest.findings[0].message
                 and any(text in harvest.findings[0].message.lower()
                         for text in ('quota', 'usage limit reached')),
                 f'{stem}/0 quota finding missing')
            need(not caps and 'dispatch' not in terms[0].body and 'routed' not in terms[0].body,
                 f'{stem}/0 quota drew failure spine')
            provider_config = next(p for p in m.checkout.config.providers if p.name == provider)
            deadline = render_ts(datetime.fromisoformat(rows[0].ts)
                + timedelta(minutes=provider_config.limits.quota_window_minutes))
            need(len(arms) == 1 and arms[0].body == dict(
                timer_id=f'provider-cooldown/{provider}/{deadline}', deadline=deadline)
                and arms[0].ticket is arms[0].key is None
                and events.index(rows[0]) < events.index(arms[0]) < events.index(terms[0]),
                f'{stem}/0 exact persisted cooldown missing')
            need(not any(e.ticket == stem and e.body.get('signal') in {'diagnosis', 'reject_arrival'}
                         for e in events), f'{stem}/0 quota diagnosis or Reject arrival')
        else:
            need(not harvest.findings and 'alien failure 17' in (harvest.reason or '')
                 and 'exit 17' in (harvest.reason or '') and 'alien failure 17' in harvest.stage_log_tail,
                 'unknown failure lost captured exit/stderr evidence')
            need([e.body.get('cap') for e in caps] == ['infra'] and not arms
                 and not any(e.body.get('failure_class') == 'quota_exhausted' for e in outcomes),
                 'unknown failure infra accounting/classification wrong')
    if index == 1:
        need(m.hold is not None, 'drought snapshot missing')
        hold = list(m.hold)
        need(events[:len(hold)] == hold, 'hold is not this member journal prefix')
        parks = [e for e in hold if e.ticket == 'cooling-recovery' and e.type == EventType.STATE_TRANSITION]
        need(len(parks) == 1 and parks[0].body == dict(to='infra_error', reason='provider_drought',
            provider_drought=dict(tier='medium', surface='implement', providers=['codex', 'claude']))
            and parks[0].key is None, 'structured cost-free drought hold missing')
        need(not any(e.ticket == 'cooling-recovery' and (e.type in {EventType.EFFECT_INTENT, EventType.CAP_CONSUMED}
            or e.body.get('signal') in {'diagnosis', 'reject_arrival', 'provider_call_outcome'}) for e in hold)
            and len(m.held_calls) == 2, 'drought made call/cap/diagnosis/Reject arrival')
        arms = [e for e in hold if e.type == EventType.TIMER_ARMED]
        earliest = min(arms, key=lambda e: e.body['deadline'])
        fires = [e for e in events if e.type == EventType.TIMER_FIRED]
        need(len(fires) == 1 and fires[0].body == earliest.body and fires[0].ticket is fires[0].key is None
             and fires[0].ts == earliest.body['deadline'], 'earliest matching timer_fired missing')
        need(not any(e.type == EventType.CAP_CONSUMED or e.body.get('signal') in {'diagnosis', 'reject_arrival'}
                     for e in events), 'cooling recovery drew failure spine')
        recovered = [e for e in outcomes if e.ticket == 'cooling-recovery']
        need(len(recovered) == 2 and all(e.body.get('provider') == 'codex' and e.body.get('failure_class') is None
             for e in recovered) and events.index(fires[0]) < events.index(recovered[0]),
             'automatic recovery served another identity')
        need(sum(e.ticket == 'cooling-recovery' and e.body.get('to') == 'running' for e in events) == 1,
             'recovered running attempt missing')
        for surface in ('implement', 'review'):
            key = f'llm/cooling-recovery/0/{surface}/0/1'
            need(sum(e.type == EventType.EFFECT_INTENT and e.key == key for e in events) == 1,
                 'recovered call intent missing')
            completions = [e for e in events if e.type == EventType.EFFECT_COMPLETION and e.key == key]
            need(len(completions) == 1, 'recovered result/completion missing')
            body = completions[0].body
            need(all(body[k].get('provider') == 'codex' and body[k].get('model') == 'codex-inherited'
                     for k in ('result', 'cost')), 'recovered result/completion served identity differs')
        custody = [e for e in events if e.type == EventType.EFFECT_COMPLETION
                   and e.key == 'ticket-plane/cooling-recovery/0/run-record']
        need(len(custody) == 1 and custody[0].body.get('result', {}).get('paths') ==
             ['tickets/cooling-recovery/run.md'], 'recovered run record custody missing')
        record = m.root / 'tickets/cooling-recovery/run.md'
        need(record.is_file() and '- provider: codex\n- model: codex-inherited' in record.read_text()
             and [e.body['to'] for e in run_terminals(events, 'cooling-recovery')] == ['merged'],
             'automatic recovery run/terminal missing')
    violations = audit_journal(m.journal)
    auditor = [f'{v.invariant}: {v.ticket or "-"}: {v.detail}' for v in violations]
    expected = _RELIABILITY_BATTERY_EXPECTED[index]
    return ReliabilityBatteryEntry(member=m.name, planted_fault='Scripted CLI exit/stderr failure',
        expected=expected, observed=expected if not auditor else 'auditor_violation',
        producing_run=f'{m.fault}/0', auditor=auditor, green=not auditor)


async def _run_member(root, name):
    member = _Member(root / name, name)
    try:
        try:
            await member.initialize()
            await member.exercise()
        finally:
            await member.stop()
        return _observe(member)
    except asyncio.CancelledError:
        raise
    except BatteryRefused:
        raise
    except Exception as exc:
        raise BatteryRefused(name, str(exc)) from exc
    finally:
        member.journal.close()


async def produce(root: Path) -> ReliabilityBatteryReport:
    sha = await Git(SubprocessExec(), env=os.environ, timeout=30).rev_parse(Path.cwd(), 'HEAD')
    entries = [await _run_member(root, name) for name in RELIABILITY_BATTERY_MEMBERS]
    return ReliabilityBatteryReport(produced_by_spec_version=RELIABILITY_BATTERY_SPEC_VERSION,
                                   produced_at_sha=sha, entries=entries)


async def _main(argv=None):
    parser = argparse.ArgumentParser(prog='python -m eval.reliability_battery')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory(prefix='chupa-reliability-battery-') as directory:
            report = await produce(Path(directory))
        report = ReliabilityBatteryReport.model_validate(report.model_dump())
        for entry in report.entries:
            if not entry.green:
                raise BatteryRefused(entry.member, f'red observation {entry.observed}; auditor {entry.auditor}')
        write_report(args.out, report, LocalFileSystem())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    return asyncio.run(_main(argv))


if __name__ == '__main__':
    raise SystemExit(main())
