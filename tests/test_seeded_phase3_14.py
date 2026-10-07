"""Admission 14: fixed authoring measurements, never a copied registry or live size fold.

The live admissions[14:] suffix and complete needed units were read before writing.
All five entries passed entry_unit_gap and resolve_plan_contract, with row citations
and sections 13/6/15/11/12 resolved. Approved successor bytes are preserved.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = 'c0c6fec070a3c749d9d7757f338ffe8b400e2a4c'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

APPROVED_SUCCESSOR_SHA256 = '3b3e8dfbcda61f07f2177940ad5c31a81fcafacd0ac39194e19bdef38314152c'

PAYLOADS = ('restart-timers',)

BATCH = ('restart-timers', 'phase3-continue-15')

EDGES = {'restart-timers': ('phase3-continue-14',), 'phase3-continue-15': ('restart-timers',)}

STARTS = {'restart-timers': ('high', 'high'), 'phase3-continue-15': ('medium', 'medium')}

FENCE_FLOORS = {'restart-timers': ('chupa/restart.py',
                    'chupa/timers.py',
                    'chupa/daemon.py',
                    'chupa/__main__.py',
                    'tests/test_restart_timers.py'),
 'phase3-continue-15': ('tickets', 'tests/test_seeded_phase3_15.py')}

FENCE_ADDITIONS = {'restart-timers': {'tests/test_daemon_composition.py': ('checkpoint identity assertion at 1261 '
                                                         'and pre-startup running plant in '
                                                         'test_production_core_preserves_eligibility_order_and_backpressure '
                                                         'at 323; preserve other '
                                                         'eligibility/order/backpressure '
                                                         'assertions',
                                                         'Context'),
                    'tests/test_daemon_pause.py': ('checkpoint identity assertion at 201 must '
                                                   'prove composed startup then pause',
                                                   'Context'),
                    'tests/test_control.py': ('test_control_inbox_is_active checkpoint identity at '
                                              '386/391 and removal calibration must prove composed '
                                              'startup/pause binding',
                                              'Context')},
 'phase3-continue-15': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.restart-timers': 8881,
 '6': 36783,
 '15': 17090,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.flake-detection': 7196,
 '19.P3.flake-release': 5851,
 '11': 26851,
 '19.P3.journal-roll': 4544,
 '19.P3.storm-ledger': 5511,
 '12': 20224}

FILE_CHARS = {'chupa/daemon.py': 19633,
 'chupa/__main__.py': 9179,
 'tests/test_daemon_composition.py': 89342,
 'tests/test_daemon_pause.py': 7639,
 'tests/test_control.py': 17077,
 'chupa/reconcile.py': 2452,
 'chupa/journal.py': 8656,
 'chupa/config.py': 11898,
 'chupa/seams.py': 5551,
 'chupa/git.py': 6503,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'restart-timers': {'chars': 5531,
                    'plan': ('19.I', '19.P3.restart-timers', '6', '15'),
                    'context': ('chupa/daemon.py',
                                'chupa/__main__.py',
                                'tests/test_daemon_composition.py',
                                'tests/test_daemon_pause.py',
                                'tests/test_control.py',
                                'chupa/reconcile.py',
                                'chupa/journal.py',
                                'chupa/config.py',
                                'chupa/seams.py',
                                'chupa/git.py'),
                    'on_demand': (),
                    'fenced_existing': ('chupa/daemon.py',
                                        'chupa/__main__.py',
                                        'tests/test_daemon_composition.py',
                                        'tests/test_daemon_pause.py',
                                        'tests/test_control.py'),
                    'created': ('chupa/restart.py',
                                'chupa/timers.py',
                                'tests/test_restart_timers.py'),
                    'measured_render': 252541},
 'phase3-continue-15': {'chars': 9095,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.flake-detection',
                                 '19.P3.flake-release',
                                 '11',
                                 '19.P3.journal-roll',
                                 '6',
                                 '19.P3.storm-ledger',
                                 '12'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_15.py'),
                        'measured_render': 182078}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/daemon.py',
 'chupa/__main__.py',
 'tests/test_daemon_composition.py',
 'tests/test_daemon_pause.py',
 'tests/test_control.py',
 'chupa/reconcile.py',
 'chupa/journal.py',
 'chupa/config.py',
 'chupa/seams.py',
 'chupa/git.py',
 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.restart-timers',
 '19.P3.flake-detection',
 '19.P3.flake-release',
 '19.P3.journal-roll',
 '19.P3.storm-ledger')

VALIDATED_ROW_CITATIONS = {'19.P3.restart-timers': ('6', '15'),
 '19.P3.flake-detection': ('11',),
 '19.P3.flake-release': ('11',),
 '19.P3.journal-roll': ('6',),
 '19.P3.storm-ledger': ('12',)}

CONTRACT_CUSTODY = {'Owner': '19.P3.restart-timers',
 'Records': '19.P3.restart-timers',
 'Observable': '19.P3.restart-timers',
 'Tests': '19.P3.restart-timers'}

ENTRY_TESTS = ('test_restart_construction_is_idle',
 'test_restart_reuses_orphan_reconciliation',
 'test_orphan_sweep_preserves_live_ownership',
 'test_timer_records_and_identity',
 'test_timer_append_is_write_ahead',
 'test_timers_rearm_from_journal',
 'test_timer_deadline_wait_uses_injected_sleep',
 'test_production_restart_precedes_dispatch',
 'test_restart_failures_do_not_report_ready')

ENTRY_VERIFICATION = ('uv',
 'run',
 'pytest',
 'tests/test_restart_timers.py',
 'tests/test_reconcile.py',
 'tests/test_daemon_composition.py',
 'tests/test_daemon_admission.py',
 'tests/test_daemon_config.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_journal.py',
 'tests/test_audit.py')

PRESERVATION = ('tests/test_reconcile.py',
 'tests/test_daemon_admission.py',
 'tests/test_daemon_config.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_journal.py',
 'tests/test_audit.py')

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'symbols': ('CoreRig',
             'build_daemon_core',
             'daemon_core',
             'DaemonAdmission',
             '_before_dispatch',
             'snapshot_dispatch',
             'running',
             'effect_intent',
             'not hasattr',
             '__all__',
             'tasks ==',
             'TIMER_ARMED',
             'TIMER_FIRED'),
 'safe_plants': ('tests/test_scheduler.py:433 closes leaf-b before first dispatch',
                 'tests/test_daemon_composition.py LiveDrain uses bootstrap on-entry or closed '
                 'terminal history',
                 'tests/test_kill_cli_activation.py LiveDrain uses bootstrap on-entry recovery'),
 'unchanged_callers': ('tests/test_daemon_admission.py',
                       'tests/test_daemon_config.py',
                       'tests/test_daemon_tasks.py',
                       'tests/test_heartbeat.py',
                       'tests/test_kill_worker_stop.py',
                       'tests/test_kill_failure_suppression.py'),
 'import_pin': 'from chupa.daemon import DaemonCore, PauseConsumer, daemon_core',
 'public_surface': 'no public-operation allowlist forces further additions; callable signatures '
                   'preserved; no serve verb or background loop'}



def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == (*PAYLOADS, 'phase3-continue-15') == ('restart-timers', 'phase3-continue-15')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(AUTHORED)
    assert set(BATCH) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # Rejected is later lifecycle history; pin the confirmed seed birth separately.
    t = validate_ticket(stem, _text(stem).replace('state: rejected', 'state: confirmed', 1), ROOT, BATCH)
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.priority, t.frontmatter.kind) == ('P1', 'feature')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == STARTS[stem]
    assert STARTS == {'restart-timers': ('high', 'high'), 'phase3-continue-15': ('medium', 'medium')}


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes <= t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'restart-timers': ('phase3-continue-14',), 'phase3-continue-15': PAYLOADS}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert set(FENCE_ADDITIONS['restart-timers']) == {
        'tests/test_daemon_composition.py', 'tests/test_daemon_pause.py', 'tests/test_control.py'}
    assert FENCE_ADDITIONS['phase3-continue-15'] == {}
    for path, (reason, partition) in FENCE_ADDITIONS[stem].items():
        assert reason and partition == 'Context' and path in t.context
        assert path in t.sections['Scope in / Scope out']
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert CLOSURE_SNAPSHOT['safe_plants'] and CLOSURE_SNAPSHOT['unchanged_callers']
    if stem in PAYLOADS:
        scope = t.sections['Scope in / Scope out']
        for fact in ('19.L rules 2-5', 'test_production_core_preserves_eligibility_order_and_backpressure',
                     'Await the composed startup before planting running',
                     'Keep every other eligibility, ordering and backpressure assertion unchanged',
                     'assert_bound', 'leaf-b', CLOSURE_SNAPSHOT['import_pin'],
                     'callable signatures', 'ordinary DaemonTasks exception propagation and cleanup',
                     'historical seeding tests'):
            assert fact in scope, fact
        assert not any(path.startswith('tests/test_seeded_') for path in t.scope_fence)


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket('restart-timers')
    own = '19.P3.restart-timers'
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', own, '6', '15')
    assert CONTRACT_CUSTODY == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert own in VALIDATED_ENTRIES and VALIDATED_ROW_CITATIONS[own] == ('6', '15')
    assert ENTRY_TESTS == (
        'test_restart_construction_is_idle', 'test_restart_reuses_orphan_reconciliation',
        'test_orphan_sweep_preserves_live_ownership', 'test_timer_records_and_identity',
        'test_timer_append_is_write_ahead', 'test_timers_rearm_from_journal',
        'test_timer_deadline_wait_uses_injected_sleep', 'test_production_restart_precedes_dispatch',
        'test_restart_failures_do_not_report_ready')
    assert all(name in t.sections['Acceptance criteria'] for name in ENTRY_TESTS)
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract for Owner, Records, Observable',
                 'every named Tests obligation', 'implement all of it', 'record custody',
                 "unit's Owner", 'Never copy unit text', 'runner.harvest_orphan',
                 'real CLI run/drain', 'merged production-composition harness', 'real build_daemon_core',
                 'barrier-held reconciliation', 'injected recovery failures',
                 'member-local invariant-audited journals', 'bootstrap on-entry reconciliation',
                 'inline admission', 'serve-activation owns continuous maintenance scheduling',
                 'injected Clock/Sleep', 'disposable repositories', 'asyncio barriers'):
        assert fact in scope, fact
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(t.stem)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-15')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.flake-detection', '19.P3.flake-release',
        '11', '19.P3.journal-roll', '6', '19.P3.storm-ledger', '12')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_15.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    # Check approval is held while bytes match; never re-author this approved seed.
    birth = _text(t.stem).replace('state: rejected', 'state: confirmed', 1)
    assert hashlib.sha256(birth.encode()).hexdigest() == APPROVED_SUCCESSOR_SHA256
    assert VALIDATED_ENTRIES == (
        '19.P3.restart-timers', '19.P3.flake-detection', '19.P3.flake-release',
        '19.P3.journal-roll', '19.P3.storm-ledger')
    scope = t.sections['Scope in / Scope out']
    for fact in ('BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[15:]', 'admissions[16:]',
                 'admissions[17:]', 'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
                 'Author only flake-detection, flake-release and phase3-continue-16',
                 'flake-release also depends on flake-detection',
                 'storm-ledger also depends on journal-roll',
                 '19.I, their own 19.P3 entry, section 11', 'start medium/medium',
                 'Never copy unit text into a seed or into this seeding ticket',
                 "Carry this cite-don't-copy rule forward to phase3-continue-16",
                 'tests/test_seeded_phase3_16.py',
                 "never this batch's tests/test_seeded_phase3_15.py",
                 '19.P3.journal-roll', '19.P3.storm-ledger', 'section 6', 'section 12',
                 'required next-seeder lookahead, not payloads to author here',
                 '19.L closure rules 2-5', 'Context/on-demand partition',
                 '300,000-character headroom', 'Prompt-specs and delimiter-bearing sources are never Context',
                 'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
                 'named invariant obligations', 'record custody',
                 'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
                 'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
                 'terminal phase3-exit as its sole payload with no successor',
                 'keep previously approved seeds verbatim', 'ticket_sha',
                 'chupa(phase3-continue-15): seeds', "Commit only this ticket's new test"):
        assert fact in scope, fact
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(t.stem)


@pytest.mark.parametrize('stem', BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(t.scope_fence) == set(a['fenced_existing']) | set(a['created'])
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert not set(a['context']) & set(a['on_demand'])
    assert set(a['context']) <= set(DELIMITER_FREE_AT_AUTHORING)
    assert not any(p.startswith('specs/') or p == 'CHUPA_PLAN.md' for p in a['context'])
    assert all(FILE_CHARS[p] > 0 for p in (*a['context'], *a['on_demand']))
    assert all(PLAN_CHARS[pid] > 0 for pid in a['plan'])
    assert 0 < a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket('restart-timers')
    assert ENTRY_VERIFICATION == (
        'uv', 'run', 'pytest', 'tests/test_restart_timers.py', 'tests/test_reconcile.py',
        'tests/test_daemon_composition.py', 'tests/test_daemon_admission.py',
        'tests/test_daemon_config.py', 'tests/test_cli.py', 'tests/test_drain.py',
        'tests/test_journal.py', 'tests/test_audit.py')
    assert t.verification == (ENTRY_VERIFICATION,
                             ('uv', 'run', 'pytest', 'tests/test_daemon_pause.py', 'tests/test_control.py'),
                             ('uv', 'run', 'pytest', '-q'))
    assert PRESERVATION == (
        'tests/test_reconcile.py', 'tests/test_daemon_admission.py', 'tests/test_daemon_config.py',
        'tests/test_cli.py', 'tests/test_drain.py', 'tests/test_journal.py', 'tests/test_audit.py')
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites in Verification only, neither fenced nor embedded' in t.sections['Scope in / Scope out']
