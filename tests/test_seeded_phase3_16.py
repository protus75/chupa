"""Admission 16: citation custody and fixed authoring snapshots.

Parsed admissions[16:] directly from the live registry before writing; all five
needed complete entries passed entry_unit_gap and resolve_plan_contract, as did
their row citations. No registry or entry-unit body is duplicated here.
Measurements never refresh from live file sizes or live plan lengths.
"""

from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = 'ee99b04206b471f3b38e2b7ebeba57ae5d33f16f'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

APPROVED_STORM_LEDGER_SHA256 = '506c384a0feac8a2cbec3d1cc6ac22e1019df1d0476c3e2e62847be6bf5da244'

PAYLOADS = ('journal-roll', 'storm-ledger')

BATCH = ('journal-roll', 'storm-ledger', 'phase3-continue-17')

EDGES = {'journal-roll': ('phase3-continue-16',),
 'storm-ledger': ('phase3-continue-16', 'journal-roll'),
 'phase3-continue-17': ('journal-roll', 'storm-ledger')}

FENCE_FLOORS = {'journal-roll': ('chupa/journal.py', 'tests/test_journal_roll.py'),
 'storm-ledger': ('chupa/storm.py', 'tests/test_storm.py'),
 'phase3-continue-17': ('tickets', 'tests/test_seeded_phase3_17.py')}

FENCE_ADDITIONS = {'journal-roll': {}, 'storm-ledger': {}, 'phase3-continue-17': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.journal-roll': 4544,
 '6': 36783,
 '19.P3.storm-ledger': 5511,
 '12': 20224,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.storm-producer-wiring': 7095,
 '19.P3.storm-notification-activation': 14524,
 '19.P3.storm-dispatch-hold': 9662,
 '20': 4367}

FILE_CHARS = {'chupa/journal.py': 8656,
 'chupa/box.py': 7798,
 'chupa/config.py': 11898,
 'chupa/seams.py': 5551,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'journal-roll': {'chars': 3095,
                  'plan': ('19.I', '19.P3.journal-roll', '6'),
                  'context': ('chupa/journal.py',
                              'chupa/box.py',
                              'chupa/config.py',
                              'chupa/seams.py'),
                  'on_demand': (),
                  'fenced_existing': ('chupa/journal.py',),
                  'created': ('tests/test_journal_roll.py',),
                  'measured_render': 84480},
 'storm-ledger': {'chars': 3198,
                  'plan': ('19.I', '19.P3.storm-ledger', '12'),
                  'context': ('chupa/journal.py',
                              'chupa/box.py',
                              'chupa/config.py',
                              'chupa/seams.py'),
                  'on_demand': (),
                  'fenced_existing': (),
                  'created': ('chupa/storm.py', 'tests/test_storm.py'),
                  'measured_render': 68991},
 'phase3-continue-17': {'chars': 10309,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.storm-producer-wiring',
                                 '19.P3.storm-notification-activation',
                                 '12',
                                 '19.P3.storm-dispatch-hold',
                                 '20'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_17.py'),
                        'measured_render': 132204}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/journal.py',
 'chupa/box.py',
 'chupa/config.py',
 'chupa/seams.py',
 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.journal-roll',
 '19.P3.storm-ledger',
 '19.P3.storm-producer-wiring',
 '19.P3.storm-notification-activation',
 '19.P3.storm-dispatch-hold')

VALIDATED_ROW_CITATIONS = {'journal-roll': ('6',),
 'storm-ledger': ('12',),
 'storm-producer-wiring': ('12',),
 'storm-notification-activation': ('12',),
 'storm-dispatch-hold': ('12', '20')}

ENTRY_TESTS = {'journal-roll': ('test_roll_constants_and_size_boundary',
                  'test_roll_age_boundary_uses_injected_clock',
                  'test_roll_sequence_and_restart',
                  'test_roll_preserves_records_and_read_laws',
                  'test_startup_tail_repair_precedes_roll',
                  'test_roll_durability_and_failures'),
 'storm-ledger': ('test_storm_construction_and_reads_are_idle',
                  'test_occurrence_signal_shape_and_identity',
                  'test_occurrence_replay_is_once',
                  'test_window_boundaries_and_signature_isolation',
                  'test_occurrences_survive_roll_and_restart',
                  'test_occurrence_append_failures_and_crash_replay',
                  'test_ledger_has_no_trip_side_effects',
                  'test_storm_ledger_is_dormant')}

ENTRY_VERIFICATION = {'journal-roll': ('uv',
                  'run',
                  'pytest',
                  'tests/test_journal_roll.py',
                  'tests/test_journal.py',
                  'tests/test_effects.py',
                  'tests/test_audit.py'),
 'storm-ledger': ('uv',
                  'run',
                  'pytest',
                  'tests/test_storm.py',
                  'tests/test_journal_roll.py',
                  'tests/test_journal.py',
                  'tests/test_box.py')}

PRESERVATION = {'journal-roll': ('tests/test_journal.py', 'tests/test_effects.py', 'tests/test_audit.py'),
 'storm-ledger': ('tests/test_journal_roll.py', 'tests/test_journal.py', 'tests/test_box.py')}

CONTRACT_CUSTODY = {'journal-roll': {'Owner': '19.P3.journal-roll',
                  'Records': '19.P3.journal-roll',
                  'Observable': '19.P3.journal-roll',
                  'Tests': '19.P3.journal-roll'},
 'storm-ledger': {'Owner': '19.P3.storm-ledger',
                  'Records': '19.P3.storm-ledger',
                  'Observable': '19.P3.storm-ledger',
                  'Tests': '19.P3.storm-ledger'}}

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'patterns': ('Journal(',
              'append',
              'read_segments',
              'read',
              'close',
              'ROLL_',
              'storm',
              'Box(',
              'enqueue',
              'not hasattr',
              '__all__',
              'tasks ==',
              'box.*event',
              'build_daemon_core'),
 'production_callers': ('chupa/__main__.py',
                        'chupa/driver.py',
                        'chupa/audit.py',
                        'eval/harness.py',
                        'eval/shakeout/bench.py'),
 'direct_test_callers': ('tests/test_diagnose_eval.py',
                         'tests/test_author.py',
                         'tests/test_harvest.py',
                         'tests/test_effects.py',
                         'tests/test_driver.py',
                         'tests/test_triage.py',
                         'tests/test_drain.py',
                         'tests/test_flake.py',
                         'tests/test_tickets.py',
                         'tests/test_kill_signal_journal.py',
                         'tests/test_journal.py',
                         'tests/test_terminal.py',
                         'tests/test_restart_timers.py',
                         'tests/test_thresh.py',
                         'tests/test_diagnose.py',
                         'tests/test_reconcile.py',
                         'tests/test_kill_cli_activation.py',
                         'tests/test_daemon_composition.py',
                         'tests/test_scheduler.py',
                         'tests/test_control.py',
                         'tests/test_fault_injection.py',
                         'tests/test_ladder.py',
                         'tests/test_llm_effect.py',
                         'tests/test_drain_upgrade.py',
                         'tests/test_cli.py',
                         'tests/test_heartbeat.py',
                         'tests/test_drain_reentry.py',
                         'tests/test_caps.py',
                         'tests/test_eval_harness.py',
                         'tests/test_harvest_orphans.py',
                         'tests/test_audit.py'),
 'unchanged_assertions': ('tests/test_journal.py::test_append_goes_to_newest_segment_without_rolling: '
                          'first complete event ts equals T0, not filename date; no age roll',
                          'tests/test_daemon_tasks.py: ordinary exception propagation and cleanup '
                          'unchanged',
                          'tests/test_drain.py::test_drain_merges_without_scanning_the_box: no '
                          'triage calls and pre-existing message pending; no blanket no-box-event '
                          'assertion'),
 'reason': 'Journal signatures and all direct callers remain valid; storm module is new and '
           'dormant. No public allowlist, caller, composition or predecessor assertion migration '
           'is earned.',
 'next_activation_additions': {'chupa/runner.py': '19.P3.storm-notification-activation '
                                                  'Owner/Records, 19.L rule 5: Rework fallback and '
                                                  'dead dependencies',
                               'chupa/stages.py': '19.P3.storm-notification-activation '
                                                  'Owner/Records, 19.L rule 5: second problems and '
                                                  'base-red reports',
                               'chupa/flake.py': '19.P3.storm-notification-activation '
                                                 'Owner/Records, 19.L rule 5: detection id seam, '
                                                 'detection/release stay dormant',
                               'tests/test_storm_producer.py': '19.P3.storm-notification-activation '
                                                               'Observable, 19.L rules 2-3: '
                                                               'sibling-created production absence '
                                                               'test; neither Context nor '
                                                               'On-demand'},
 'next_hold_migration': '19.P3.storm-dispatch-hold Observable: earn predecessor dispatch-absence '
                        'assertion test_storm_activation_does_not_hold_dispatch_or_notify; '
                        'preserve no-notify'}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[p] for p in a['plan'])
            + sum(FILE_CHARS[p] for p in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == (*PAYLOADS, 'phase3-continue-17') == (
        'journal-roll', 'storm-ledger', 'phase3-continue-17')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # A later rejected stamp is lifecycle history, not seed birth.
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
    assert EDGES == {'journal-roll': ('phase3-continue-16',),
                     'storm-ledger': ('phase3-continue-16', 'journal-roll'),
                     'phase3-continue-17': PAYLOADS}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    assert set(_ticket(stem).scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_FLOORS == {
        'journal-roll': ('chupa/journal.py', 'tests/test_journal_roll.py'),
        'storm-ledger': ('chupa/storm.py', 'tests/test_storm.py'),
        'phase3-continue-17': ('tickets', 'tests/test_seeded_phase3_17.py')}
    assert all(additions == {} for additions in FENCE_ADDITIONS.values())
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert CLOSURE_SNAPSHOT['production_callers'] and CLOSURE_SNAPSHOT['direct_test_callers']
    assert len(CLOSURE_SNAPSHOT['unchanged_assertions']) == 3
    if stem in PAYLOADS:
        scope = _ticket(stem).sections['Scope in / Scope out']
        for fact in ('19.L rules 2-5', 'no fence additions', 'bootstrap on-entry reconciliation',
                     'inline admission', 'ordinary DaemonTasks exception propagation and cleanup',
                     'historical seeding tests'):
            assert fact in scope, fact


@pytest.mark.parametrize('stem', PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    own = '19.P3.' + stem
    row = '6' if stem == 'journal-roll' else '12'
    assert t.plan_contract == AUTHORED[stem]['plan'] == ('19.I', own, row)
    assert CONTRACT_CUSTODY[stem] == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert own in VALIDATED_ENTRIES and VALIDATED_ROW_CITATIONS[stem] == (row,)
    assert len(ENTRY_TESTS[stem]) == (6 if stem == 'journal-roll' else 8)
    assert all(name in t.sections['Acceptance criteria'] for name in ENTRY_TESTS[stem])
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract for Owner, Records, Observable',
                 'every named Tests obligation', 'implement all of it', 'record custody',
                 "unit's Owner", 'never copy unit text', 'real CLI run/drain',
                 'build_daemon_core', 'merged production-composition harness', 'Journal',
                 'sole durable writer',
                 'injected seams', 'scripted callbacks', 'disposable repositories', 'asyncio barriers',
                 'manual HGATE release', 'verification filtering', 'unearned records'):
        assert fact in scope, fact
    assert 'boundary, replay, corruption, durability and crash' in _text(stem)
    for part in CONTRACT_CUSTODY[stem]:
        assert f'- **{part}:**' not in _text(stem)
    if stem == 'journal-roll':
        assert 'Journal(state_dir, clock) and append/read/close signatures and all direct callers' in scope
        assert 'test_append_goes_to_newest_segment_without_rolling' in scope
    else:
        assert 'New chupa/storm.py' in scope and 'occurrence-only ledger dormant' in scope
        assert 'trip/report/notification/hold' in scope


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-17')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.storm-producer-wiring',
        '19.P3.storm-notification-activation', '12', '19.P3.storm-dispatch-hold', '20')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_17.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == (
        '19.P3.journal-roll', '19.P3.storm-ledger', '19.P3.storm-producer-wiring',
        '19.P3.storm-notification-activation', '19.P3.storm-dispatch-hold')
    assert VALIDATED_ROW_CITATIONS == {
        'journal-roll': ('6',), 'storm-ledger': ('12',), 'storm-producer-wiring': ('12',),
        'storm-notification-activation': ('12',), 'storm-dispatch-hold': ('12', '20')}
    scope = t.sections['Scope in / Scope out']
    for fact in ('BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[17:]', 'admissions[18:]',
                 'admissions[19:]', 'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
                 'Author only storm-producer-wiring, storm-notification-activation and phase3-continue-18',
                 'storm-notification-activation also depends on storm-producer-wiring',
                 'cite exactly 19.I, their own 19.P3 entry and section 12', 'start medium/medium',
                 'Never copy unit text into a seed or into this seeding ticket',
                 "Carry this cite-don't-copy rule forward to phase3-continue-18",
                 'tests/test_seeded_phase3_18.py', "never this batch's tests/test_seeded_phase3_17.py",
                 '19.P3.storm-dispatch-hold', 'section 20', 'deep storm-dispatch-hold at high/high',
                 'required next-seeder lookahead, not payloads to author here',
                 '19.L closure rules 2-5', 'Context/on-demand partition',
                 '300,000-character headroom', 'Prompt-specs and delimiter-bearing sources are never Context',
                 'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
                 'named invariant obligations', 'record custody',
                 'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
                 'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
                 'terminal phase3-exit as its sole payload with no successor',
                 'keep previously approved seeds verbatim', 'ticket_sha',
                 'chupa(phase3-continue-17): seeds', "Commit only this ticket's new test",
                 'test_production_arrival_site_closure', 'test_production_occurrence_id_recipes',
                 'test_production_arrival_preserves_caller_behavior',
                 'closed production arrival-site list and all replay-stable occurrence_id recipes',
                 'test_storm_activation_does_not_hold_dispatch_or_notify',
                 'tests/test_drain.py::test_drain_merges_without_scanning_the_box'):
        assert fact in scope, fact
    for path, reason in CLOSURE_SNAPSHOT['next_activation_additions'].items():
        assert path in scope and '19.L' in reason
    assert 'sibling' in scope and 'never Context here' in scope
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
    assert ENTRY_VERIFICATION == {
        'journal-roll': ('uv', 'run', 'pytest', 'tests/test_journal_roll.py', 'tests/test_journal.py',
                         'tests/test_effects.py', 'tests/test_audit.py'),
        'storm-ledger': ('uv', 'run', 'pytest', 'tests/test_storm.py', 'tests/test_journal_roll.py',
                         'tests/test_journal.py', 'tests/test_box.py')}
    assert set(PRESERVATION[stem]) == {p for p in ENTRY_VERIFICATION[stem]
                                     if p.startswith('tests/') and p not in t.scope_fence}
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites in Verification only, neither fenced nor embedded' in t.sections['Scope in / Scope out']
