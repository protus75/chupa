"""Heartbeat admission and successor, pinned at authoring rather than remeasured.

Entry units through journal-roll/storm-ledger and every row citation passed both
entry_unit_gap and resolve_plan_contract. The live registry suffix is a position,
never copied here. All render arithmetic uses the fixed measurements below.
"""

from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = '9cfd3f13ff24ba2d03af08ab8eb2e0312ed9754b'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('heartbeat',)

BATCH = ('heartbeat', 'phase3-continue-14')

EDGES = {'heartbeat': ('phase3-continue-13',), 'phase3-continue-14': ('heartbeat',)}

STARTS = {'heartbeat': ('medium', 'medium'), 'phase3-continue-14': ('medium', 'medium')}

FENCE_FLOORS = {'heartbeat': ('chupa/heartbeat.py', 'chupa/daemon.py', 'tests/test_heartbeat.py'),
 'phase3-continue-14': ('tickets', 'tests/test_seeded_phase3_14.py')}

FENCE_ADDITIONS = {'heartbeat': {}, 'phase3-continue-14': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.heartbeat': 5116,
 '9': 19656,
 '15': 17090,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.restart-timers': 8881,
 '6': 36783,
 '19.P3.flake-detection': 7196,
 '19.P3.flake-release': 5851,
 '11': 26851,
 '19.P3.journal-roll': 4544,
 '19.P3.storm-ledger': 5511,
 '12': 20224}

FILE_CHARS = {'chupa/daemon.py': 18885,
 'chupa/config.py': 11898,
 'chupa/seams.py': 5551,
 'chupa/__main__.py': 9179,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'heartbeat': {'chars': 4357,
               'plan': ('19.I', '19.P3.heartbeat', '9', '15'),
               'context': ('chupa/daemon.py',
                           'chupa/config.py',
                           'chupa/seams.py',
                           'chupa/__main__.py'),
               'on_demand': (),
               'fenced_existing': ('chupa/daemon.py',),
               'created': ('chupa/heartbeat.py', 'tests/test_heartbeat.py'),
               'measured_render': 97891},
 'phase3-continue-14': {'chars': 9365,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.restart-timers',
                                 '6',
                                 '15',
                                 '19.P3.flake-detection',
                                 '19.P3.flake-release',
                                 '11',
                                 '19.P3.journal-roll',
                                 '19.P3.storm-ledger',
                                 '12'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_14.py'),
                        'measured_render': 208319}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/daemon.py',
 'chupa/config.py',
 'chupa/seams.py',
 'chupa/__main__.py',
 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.heartbeat',
 '19.P3.restart-timers',
 '19.P3.flake-detection',
 '19.P3.flake-release',
 '19.P3.journal-roll',
 '19.P3.storm-ledger')

VALIDATED_ROW_CITATIONS = {'19.P3.heartbeat': ('9', '15'),
 '19.P3.restart-timers': ('6', '15'),
 '19.P3.flake-detection': ('11',),
 '19.P3.flake-release': ('11',),
 '19.P3.journal-roll': ('6',),
 '19.P3.storm-ledger': ('12',)}

CONTRACT_CUSTODY = {'Owner': '19.P3.heartbeat',
 'Records': '19.P3.heartbeat',
 'Observable': '19.P3.heartbeat',
 'Tests': '19.P3.heartbeat'}

ENTRY_TESTS = ('test_construction_is_idle',
 'test_healthy_cycle_refreshes_heartbeat',
 'test_unhealthy_core_stops_refresh',
 'test_heartbeat_failures_propagate',
 'test_external_heartbeat_freshness',
 'test_external_heartbeat_refuses_invalid_evidence',
 'test_heartbeat_is_dormant')

ENTRY_VERIFICATION = ('uv',
 'run',
 'pytest',
 'tests/test_heartbeat.py',
 'tests/test_daemon_tasks.py',
 'tests/test_daemon_composition.py',
 'tests/test_cli.py',
 'tests/test_drain.py')

PRESERVATION = ('tests/test_daemon_tasks.py',
 'tests/test_daemon_composition.py',
 'tests/test_cli.py',
 'tests/test_drain.py')

NEXT_CITATIONS = {'restart-timers': ('19.I', '19.P3.restart-timers', '6', '15'),
 'flake-detection': ('19.I', '19.P3.flake-detection', '11'),
 'flake-release': ('19.I', '19.P3.flake-release', '11'),
 'journal-roll': ('19.I', '19.P3.journal-roll', '6'),
 'storm-ledger': ('19.I', '19.P3.storm-ledger', '12')}

NEXT_STARTS = {'restart-timers': ('high', 'high'),
 'flake-detection': ('medium', 'medium'),
 'flake-release': ('medium', 'medium'),
 'journal-roll': ('medium', 'medium'),
 'storm-ledger': ('medium', 'medium')}

CLOSURE_SNAPSHOT = {'search_roots': ('chupa/', 'eval/', 'tests/'),
 'symbols': ('heartbeat',
             'DaemonTasks',
             'DaemonAdmission',
             'daemon_core',
             'build_daemon_core',
             'FileSystem.write',
             'Clock',
             'state_dir'),
 'composition_callers': ('chupa/__main__.py:build_daemon_core -> daemon_core',
                         'chupa/daemon.py:daemon_core -> DaemonAdmission',
                         'tests/test_daemon_composition.py:CoreRig -> build_daemon_core',
                         'tests/test_daemon_admission.py:DaemonAdmission',
                         'tests/test_daemon_config.py:DaemonAdmission',
                         'tests/test_daemon_pause.py:DaemonAdmission'),
 'task_callers': ('tests/test_daemon_tasks.py',
                  'tests/test_kill_worker_stop.py',
                  'tests/test_kill_failure_suppression.py'),
 'rules_2_5': 'No earned additions: heartbeat has no production caller; existing public '
              'signatures, task graph and composition stay unchanged. New-module ownership is '
              'supplied by 19.P3.heartbeat. No daemon public-operation allowlist pins the new '
              'boundary.',
 'old_assertions': 'Task count 3, tasks == (), idle CoreRig fs/journal/task checks and bootstrap '
                   'inline admission remain true; daemon import absence already migrated by '
                   'scheduler-activation. No heartbeat-absence assertion exists outside the new '
                   'test.',
 'dormancy': 'tests/test_daemon_tasks.py:test_background_consumers_are_dormant calibrates raising '
             'construction/run probes over CLI run/drain and CoreRig; heartbeat reuses that '
             'evidence shape in its own new test, without migrating it.',
 'partition': {'chupa/daemon.py': 'Context; only existing fenced file; embedding fits headroom'},
 'production_wiring_owner': 'serve-activation fences tests/test_heartbeat.py for later dormancy '
                            'migration',
 'seams': 'Config.state_dir resolves at load; FileSystem.write is atomic; Clock is zero-argument. '
          'Health/metadata callbacks come from the caller, not task-existence inference.'}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ('heartbeat', 'phase3-continue-14') == (*PAYLOADS, 'phase3-continue-14')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(AUTHORED)
    assert set(BATCH) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # A later rejected stamp records lifecycle history, not seed birth.
    birth = _text(stem).replace('state: rejected', 'state: confirmed', 1)
    t = validate_ticket(stem, birth, ROOT, BATCH)
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.priority, t.frontmatter.kind) == ('P1', 'feature')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == STARTS[stem]
    assert STARTS == {s: ('medium', 'medium') for s in BATCH}


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes <= t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'heartbeat': ('phase3-continue-13',), 'phase3-continue-14': PAYLOADS}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_FLOORS['heartbeat'] == (
        'chupa/heartbeat.py', 'chupa/daemon.py', 'tests/test_heartbeat.py')
    assert FENCE_ADDITIONS == {s: {} for s in BATCH}
    assert CLOSURE_SNAPSHOT['search_roots'] == ('chupa/', 'eval/', 'tests/')
    assert CLOSURE_SNAPSHOT['rules_2_5'].startswith('No earned additions:')
    assert CLOSURE_SNAPSHOT['partition'] == {
        'chupa/daemon.py': 'Context; only existing fenced file; embedding fits headroom'}
    for fact in ('composition_callers', 'task_callers', 'old_assertions', 'dormancy',
                 'production_wiring_owner', 'seams'):
        assert CLOSURE_SNAPSHOT[fact]
    if stem in PAYLOADS:
        scope = t.sections['Scope in / Scope out']
        for fact in ('registry floor needs no additions', 'DaemonTasks', 'DaemonAdmission',
                     'daemon_core', 'build_daemon_core', 'Config.state_dir', 'FileSystem.write',
                     'Clock', 'ordinary DaemonTasks exception propagation and cleanup',
                     'bootstrap inline admission', 'historical seeding tests'):
            assert fact in scope, fact
        assert not any(p.startswith('tests/test_seeded_') for p in t.scope_fence)


@pytest.mark.parametrize('stem', PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    own = '19.P3.heartbeat'
    assert t.plan_contract == AUTHORED[stem]['plan'] == ('19.I', own, '9', '15')
    # Governing citations own the complete obligations, not a duplicate unit body.
    assert CONTRACT_CUSTODY == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert own in VALIDATED_ENTRIES and VALIDATED_ROW_CITATIONS[own] == ('9', '15')
    assert ENTRY_TESTS == (
        'test_construction_is_idle', 'test_healthy_cycle_refreshes_heartbeat',
        'test_unhealthy_core_stops_refresh', 'test_heartbeat_failures_propagate',
        'test_external_heartbeat_freshness', 'test_external_heartbeat_refuses_invalid_evidence',
        'test_heartbeat_is_dormant')
    assert all(name in t.sections['Acceptance criteria'] for name in ENTRY_TESTS)
    assert t.verification == (ENTRY_VERIFICATION, ('uv', 'run', 'pytest', '-q'))
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract for Owner, Records, Observable',
                 'every named Tests obligation', 'record custody', 'implement all of it',
                 'new chupa/heartbeat.py', "unit's Owner", 'Never copy unit text',
                 'calibrated raising construction/cycle probes', 'real CLI run/drain',
                 'merged production-composition harness', 'deliberate wiring must trip the probe',
                 'ordinary composition must leave it untouched', 'chupa.daemon is already reachable',
                 'scripted health/metadata callbacks', 'disposable repositories', 'asyncio barriers',
                 'serve-activation owns heartbeat production wiring and dormancy migration'):
        assert fact in scope, fact
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(stem)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-14')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.restart-timers', '6', '15',
        '19.P3.flake-detection', '19.P3.flake-release', '11',
        '19.P3.journal-roll', '19.P3.storm-ledger', '12')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_14.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == (
        '19.P3.heartbeat', '19.P3.restart-timers', '19.P3.flake-detection',
        '19.P3.flake-release', '19.P3.journal-roll', '19.P3.storm-ledger')
    assert t.verification == (('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_14.py'),
                              ('uv', 'run', 'pytest', '-q'))
    assert NEXT_CITATIONS == {
        'restart-timers': ('19.I', '19.P3.restart-timers', '6', '15'),
        'flake-detection': ('19.I', '19.P3.flake-detection', '11'),
        'flake-release': ('19.I', '19.P3.flake-release', '11'),
        'journal-roll': ('19.I', '19.P3.journal-roll', '6'),
        'storm-ledger': ('19.I', '19.P3.storm-ledger', '12')}
    for row, citations in NEXT_CITATIONS.items():
        assert set(citations) <= set(t.plan_contract)
        assert NEXT_STARTS[row] == (('high', 'high') if row == 'restart-timers' else ('medium', 'medium'))
    scope = t.sections['Scope in / Scope out']
    for fact in (
        'BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[14:]', 'admissions[15:]', 'admissions[16:]',
        'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
        'Author only restart-timers and phase3-continue-15',
        'restart-timers depends on phase3-continue-14, starts high/high',
        '19.I, 19.P3.restart-timers, section 6, section 15',
        'Never copy unit text into a seed or into this seeding ticket',
        "Carry this cite-don't-copy rule forward to phase3-continue-15",
        'continuation depending on restart-timers', 'its next payload is flake-detection and flake-release',
        'tests/test_seeded_phase3_15.py', "never this batch's tests/test_seeded_phase3_14.py",
        'flake-release also depends on flake-detection', 'storm-ledger also depends on journal-roll',
        '19.P3.journal-roll', '19.P3.storm-ledger', 'section 12',
        '19.L closure rules 2-5', 'Context/on-demand partition', '300,000-character headroom',
        'Prompt-specs and delimiter-bearing sources are never Context',
        'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
        'serve-activation owns continuous maintenance scheduling', 'named invariant obligations', 'record custody',
        'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
        'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
        'terminal phase3-exit as its sole payload with no successor',
        'keep previously approved seeds verbatim', 'ticket_sha',
        'chupa(phase3-continue-14): seeds', "Commit only this ticket's new test",
        'build_daemon_core', 'startup-before-snapshot', 'member-local invariant-audited journals',
    ):
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
    # Bound arithmetic stays on permanent authoring snapshots at max effort too.
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize('stem', PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert ENTRY_VERIFICATION == (
        'uv', 'run', 'pytest', 'tests/test_heartbeat.py', 'tests/test_daemon_tasks.py',
        'tests/test_daemon_composition.py', 'tests/test_cli.py', 'tests/test_drain.py')
    assert t.verification[0] == ENTRY_VERIFICATION
    assert PRESERVATION == (
        'tests/test_daemon_tasks.py', 'tests/test_daemon_composition.py', 'tests/test_cli.py', 'tests/test_drain.py')
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites in Verification only, neither fenced nor embedded' in t.sections['Scope in / Scope out']
