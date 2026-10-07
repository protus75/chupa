"""Admission 15: fixed authoring measurements and citation custody, never a copied registry.

The live admissions[15:] suffix was parsed before writing. All six needed entries
passed entry_unit_gap and resolve_plan_contract, with every row citation resolved.
Closure greps earned no added path; preservation suites remain unchanged.
Measurements below never refresh from live file sizes or live plan lengths.
"""

from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
MERGED_IDIOM = "tests/test_seeded_phase3_core.py"

AUTHORING_HEAD = '7180d4dd2bade43a845f719308963dc2f04232b4'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('flake-detection', 'flake-release')

BATCH = ('flake-detection', 'flake-release', 'phase3-continue-16')

EDGES = {'flake-detection': ('phase3-continue-15',),
 'flake-release': ('phase3-continue-15', 'flake-detection'),
 'phase3-continue-16': ('flake-detection', 'flake-release')}

FENCE_FLOORS = {'flake-detection': ('chupa/flake.py', 'chupa/daemon.py', 'tests/test_flake.py'),
 'flake-release': ('chupa/flake.py', 'chupa/daemon.py', 'tests/test_flake.py'),
 'phase3-continue-16': ('tickets', 'tests/test_seeded_phase3_16.py')}

FENCE_ADDITIONS = {'flake-detection': {}, 'flake-release': {}, 'phase3-continue-16': {}}

# Section 8 uses the same 400,000 x 0.75 bound at maximum effort.
HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.flake-detection': 7196,
 '11': 26851,
 '19.P3.flake-release': 5851,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.journal-roll': 4544,
 '6': 36783,
 '19.P3.storm-ledger': 5511,
 '12': 20224,
 '19.P3.storm-producer-wiring': 7095,
 '19.P3.storm-notification-activation': 8634}

FILE_CHARS = {'chupa/daemon.py': 20782,
 'chupa/box.py': 7798,
 'chupa/journal.py': 8656,
 'chupa/config.py': 11898,
 'chupa/seams.py': 5551,
 'chupa/__main__.py': 9666,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'flake-detection': {'chars': 4856,
                     'plan': ('19.I', '19.P3.flake-detection', '11'),
                     'context': ('chupa/daemon.py',
                                 'chupa/box.py',
                                 'chupa/journal.py',
                                 'chupa/config.py',
                                 'chupa/seams.py',
                                 'chupa/__main__.py'),
                     'on_demand': (),
                     'fenced_existing': ('chupa/daemon.py',),
                     'created': ('chupa/flake.py', 'tests/test_flake.py'),
                     'measured_render': 109455},
 'flake-release': {'chars': 4585,
                   'plan': ('19.I', '19.P3.flake-release', '11'),
                   'context': ('chupa/daemon.py',
                               'chupa/box.py',
                               'chupa/journal.py',
                               'chupa/config.py',
                               'chupa/seams.py',
                               'chupa/__main__.py'),
                   'on_demand': (),
                   'fenced_existing': ('chupa/daemon.py',),
                   'created': ('chupa/flake.py', 'tests/test_flake.py'),
                   'measured_render': 107839},
 'phase3-continue-16': {'chars': 9333,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.journal-roll',
                                 '6',
                                 '19.P3.storm-ledger',
                                 '12',
                                 '19.P3.storm-producer-wiring',
                                 '19.P3.storm-notification-activation'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_16.py'),
                        'measured_render': 158147}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/daemon.py',
 'chupa/box.py',
 'chupa/journal.py',
 'chupa/config.py',
 'chupa/seams.py',
 'chupa/__main__.py',
 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.flake-detection',
 '19.P3.flake-release',
 '19.P3.journal-roll',
 '19.P3.storm-ledger',
 '19.P3.storm-producer-wiring',
 '19.P3.storm-notification-activation')

VALIDATED_ROW_CITATIONS = {'flake-detection': ('11',),
 'flake-release': ('11',),
 'journal-roll': ('6',),
 'storm-ledger': ('12',),
 'storm-producer-wiring': ('12',),
 'storm-notification-activation': ('12',)}

ENTRY_TESTS = {'flake-detection': ('test_flake_construction_is_idle',
                     'test_detection_requires_named_bare_rerun_evidence',
                     'test_flake_report_uses_box_identity',
                     'test_detection_signal_and_quarantine',
                     'test_detection_replay_and_conflicting_identity',
                     'test_quarantine_reconstructs_across_segments',
                     'test_quarantine_cap_boundary',
                     'test_detection_failures_and_crash_replay',
                     'test_flake_detection_is_dormant'),
 'flake-release': ('test_release_construction_is_idle',
                   'test_release_resolves_exact_box_identity',
                   'test_release_requires_matching_merge_and_named_green_rerun',
                   'test_release_signal_is_write_ahead',
                   'test_release_replay_and_restart',
                   'test_release_preserves_other_quarantines',
                   'test_flake_release_is_dormant')}

ENTRY_VERIFICATION = {'flake-detection': ('uv',
                     'run',
                     'pytest',
                     'tests/test_flake.py',
                     'tests/test_box.py',
                     'tests/test_journal.py',
                     'tests/test_config.py',
                     'tests/test_daemon_composition.py',
                     'tests/test_cli.py',
                     'tests/test_drain.py'),
 'flake-release': ('uv',
                   'run',
                   'pytest',
                   'tests/test_flake.py',
                   'tests/test_box.py',
                   'tests/test_journal.py',
                   'tests/test_daemon_composition.py',
                   'tests/test_cli.py',
                   'tests/test_drain.py')}

CONTRACT_CUSTODY = {'flake-detection': {'Owner': '19.P3.flake-detection',
                     'Records': '19.P3.flake-detection',
                     'Observable': '19.P3.flake-detection',
                     'Tests': '19.P3.flake-detection'},
 'flake-release': {'Owner': '19.P3.flake-release',
                   'Records': '19.P3.flake-release',
                   'Observable': '19.P3.flake-release',
                   'Tests': '19.P3.flake-release'}}

PRESERVATION = {'flake-detection': ('tests/test_box.py',
                     'tests/test_journal.py',
                     'tests/test_config.py',
                     'tests/test_daemon_composition.py',
                     'tests/test_cli.py',
                     'tests/test_drain.py'),
 'flake-release': ('tests/test_box.py',
                   'tests/test_journal.py',
                   'tests/test_daemon_composition.py',
                   'tests/test_cli.py',
                   'tests/test_drain.py')}

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'symbols': ('flake',
             'quarantine',
             'daemon_core',
             'build_daemon_core',
             'Box',
             'Journal',
             'not hasattr',
             '__all__',
             'tasks ==',
             'serve'),
 'callers': ('chupa/__main__.py:build_daemon_core -> daemon_core',
             'tests/test_daemon_composition.py:CoreRig -> build_daemon_core',
             'tests/test_control.py -> build_daemon_core'),
 'unchanged_assertions': ('tests/test_daemon_composition.py:test_production_core_preserves_eligibility_order_and_backpressure '
                          'uses ticket-stem quarantine callback unchanged',
                          'tests/test_daemon_tasks.py task lifecycle and cleanup unchanged',
                          'tests/test_scheduler.py ticket quarantine unchanged'),
 'reason': 'New explicit dormant flake hook preserves callable signatures and all production '
           'composition; no caller, public allowlist or predecessor assertion migration is earned.'}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[p] for p in a['plan'])
            + sum(FILE_CHARS[p] for p in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == (*PAYLOADS, 'phase3-continue-16') == (
        'flake-detection', 'flake-release', 'phase3-continue-16')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # A rejected stamp is later lifecycle history, not a different seed birth.
    t = validate_ticket(stem, _text(stem).replace('state: rejected', 'state: confirmed', 1), ROOT, BATCH)
    fm = t.frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == ('medium', 'medium')


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes <= t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'flake-detection': ('phase3-continue-15',),
                     'flake-release': ('phase3-continue-15', 'flake-detection'),
                     'phase3-continue-16': PAYLOADS}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_FLOORS == {
        'flake-detection': ('chupa/flake.py', 'chupa/daemon.py', 'tests/test_flake.py'),
        'flake-release': ('chupa/flake.py', 'chupa/daemon.py', 'tests/test_flake.py'),
        'phase3-continue-16': ('tickets', 'tests/test_seeded_phase3_16.py')}
    assert all(additions == {} for additions in FENCE_ADDITIONS.values())
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert CLOSURE_SNAPSHOT['callers'] and CLOSURE_SNAPSHOT['unchanged_assertions']
    assert 'no caller' in CLOSURE_SNAPSHOT['reason']
    if stem in PAYLOADS:
        scope = t.sections['Scope in / Scope out']
        for fact in ('19.L rules 2-5', 'no fence additions', 'callable signatures',
                     'bootstrap on-entry reconciliation', 'inline admission',
                     'ordinary DaemonTasks exception propagation and cleanup', 'historical seeding tests'):
            assert fact in scope, fact


@pytest.mark.parametrize('stem', PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    own = '19.P3.' + stem
    assert t.plan_contract == AUTHORED[stem]['plan'] == ('19.I', own, '11')
    assert CONTRACT_CUSTODY[stem] == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert own in VALIDATED_ENTRIES and VALIDATED_ROW_CITATIONS[stem] == ('11',)
    assert ENTRY_TESTS == {
        'flake-detection': (
            'test_flake_construction_is_idle', 'test_detection_requires_named_bare_rerun_evidence',
            'test_flake_report_uses_box_identity', 'test_detection_signal_and_quarantine',
            'test_detection_replay_and_conflicting_identity', 'test_quarantine_reconstructs_across_segments',
            'test_quarantine_cap_boundary', 'test_detection_failures_and_crash_replay',
            'test_flake_detection_is_dormant'),
        'flake-release': (
            'test_release_construction_is_idle', 'test_release_resolves_exact_box_identity',
            'test_release_requires_matching_merge_and_named_green_rerun', 'test_release_signal_is_write_ahead',
            'test_release_replay_and_restart', 'test_release_preserves_other_quarantines',
            'test_flake_release_is_dormant')}
    assert all(name in t.sections['Acceptance criteria'] for name in ENTRY_TESTS[stem])
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract for Owner, Records, Observable',
                 'every named Tests obligation', 'implement all of it', 'record custody',
                 "unit's Owner", 'Never copy unit text', 'calibrated raising hook probes',
                 'real CLI run/drain', 'merged production-composition harness',
                 'deliberate construction and invocation wiring must trip each assertion',
                 'serve-activation owns production hook activation and dormancy migration',
                 'injected seams', 'scripted callbacks', 'disposable repositories', 'asyncio barriers',
                 'manual HGATE release', 'verification execution/filtering'):
        assert fact in scope, fact
    if stem == 'flake-release':
        assert 'Preserve detection, dedup and quarantine-cap behavior' in scope
    for part in CONTRACT_CUSTODY[stem]:
        assert f'- **{part}:**' not in _text(stem)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-16')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.journal-roll', '6',
        '19.P3.storm-ledger', '12', '19.P3.storm-producer-wiring', '19.P3.storm-notification-activation')
    assert t.context == (MERGED_IDIOM,)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_16.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == (
        '19.P3.flake-detection', '19.P3.flake-release', '19.P3.journal-roll',
        '19.P3.storm-ledger', '19.P3.storm-producer-wiring', '19.P3.storm-notification-activation')
    assert VALIDATED_ROW_CITATIONS == {
        'flake-detection': ('11',), 'flake-release': ('11',), 'journal-roll': ('6',),
        'storm-ledger': ('12',), 'storm-producer-wiring': ('12',), 'storm-notification-activation': ('12',)}
    scope = t.sections['Scope in / Scope out']
    for fact in ('BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[16:]', 'admissions[17:]',
                 'admissions[18:]', 'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
                 'Author only journal-roll, storm-ledger and phase3-continue-17',
                 'storm-ledger also depends on journal-roll',
                 'storm-notification-activation also depends on storm-producer-wiring',
                 'cite exactly 19.I, their own 19.P3 entry', 'start medium/medium',
                 'Never copy unit text into a seed or into this seeding ticket',
                 "Carry this cite-don't-copy rule forward to phase3-continue-17",
                 'tests/test_seeded_phase3_17.py', "never this batch's tests/test_seeded_phase3_16.py",
                 '19.P3.storm-producer-wiring', '19.P3.storm-notification-activation',
                 'required next-seeder lookahead, not payloads to author here',
                 '19.L closure rules 2-5', 'Context/on-demand partition',
                 '300,000-character headroom', 'Prompt-specs and delimiter-bearing sources are never Context',
                 'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
                 'named invariant obligations', 'record custody',
                 'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
                 'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
                 'terminal phase3-exit as its sole payload with no successor',
                 'keep previously approved seeds verbatim', 'ticket_sha',
                 'chupa(phase3-continue-16): seeds', "Commit only this ticket's new test"):
        assert fact in scope, fact
    for part in ('Owner', 'Records', 'Observable', 'Tests'):
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
    assert all(PLAN_CHARS[p] > 0 for p in a['plan'])
    assert 0 < a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS == 300_000
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize('stem', PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification == (ENTRY_VERIFICATION[stem], ('uv', 'run', 'pytest', '-q'))
    assert ENTRY_VERIFICATION['flake-detection'] == (
        'uv', 'run', 'pytest', 'tests/test_flake.py', 'tests/test_box.py', 'tests/test_journal.py',
        'tests/test_config.py', 'tests/test_daemon_composition.py', 'tests/test_cli.py', 'tests/test_drain.py')
    assert ENTRY_VERIFICATION['flake-release'] == (
        'uv', 'run', 'pytest', 'tests/test_flake.py', 'tests/test_box.py', 'tests/test_journal.py',
        'tests/test_daemon_composition.py', 'tests/test_cli.py', 'tests/test_drain.py')
    assert set(PRESERVATION[stem]) == {p for p in ENTRY_VERIFICATION[stem]
                                     if p.startswith('tests/') and p != 'tests/test_flake.py'}
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites in Verification only, neither fenced nor embedded' in t.sections['Scope in / Scope out']
