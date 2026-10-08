"""Admission 17: governing citations, earned closure and fixed authoring snapshots.

Parsed admissions[17:] directly from the live plan registry. All needed entries
passed entry_unit_gap and resolve_plan_contract, including their row citations.
No registry suffix or entry-unit body is copied here. Measurements never refresh.
"""

from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = '0935bb02a5f4240fc6d09c73f256c3a8d1c4ac44'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('storm-producer-wiring', 'storm-notification-activation')

BATCH = ('storm-producer-wiring', 'storm-notification-activation', 'phase3-continue-18')

EDGES = {'storm-producer-wiring': ('phase3-continue-17',),
 'storm-notification-activation': ('phase3-continue-17', 'storm-producer-wiring'),
 'phase3-continue-18': ('storm-producer-wiring', 'storm-notification-activation')}

FENCE_FLOORS = {'storm-producer-wiring': ('chupa/storm.py',
                           'chupa/box.py',
                           'chupa/daemon.py',
                           'tests/test_storm.py',
                           'tests/test_storm_producer.py'),
 'storm-notification-activation': ('chupa/storm.py',
                                   'chupa/box.py',
                                   'chupa/daemon.py',
                                   'chupa/__main__.py',
                                   'tests/test_storm.py',
                                   'tests/test_drain.py',
                                   'tests/test_storm_notification_activation.py'),
 'phase3-continue-18': ('tickets', 'tests/test_seeded_phase3_18.py')}

FENCE_ADDITIONS = {'storm-producer-wiring': {},
 'storm-notification-activation': {'chupa/runner.py': '19.L rule 5; activation Owner/Records earn '
                                                      'Rework fallback and dead-dependency '
                                                      'arrivals; Context',
                                   'chupa/stages.py': '19.L rule 5; activation Owner/Records earn '
                                                      'second-problem and base-red arrivals; '
                                                      'Context',
                                   'chupa/flake.py': '19.L rule 5; activation Owner/Records earn '
                                                     'optional detection identity seam; Context; '
                                                     'detection and release remain dormant',
                                   'tests/test_storm_producer.py': '19.L rules 2-3; activation '
                                                                   'Observable earns predecessor '
                                                                   'production-absence migration; '
                                                                   'sibling-created, neither '
                                                                   'Context nor On-demand'},
 'phase3-continue-18': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.storm-producer-wiring': 7095,
 '12': 20224,
 '19.P3.storm-notification-activation': 14524,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.storm-dispatch-hold': 9662,
 '20': 4367,
 '19.P3.checkpoint-push': 7067,
 '10': 6636}

FILE_CHARS = {'chupa/storm.py': 3932,
 'chupa/box.py': 7798,
 'chupa/daemon.py': 21155,
 'tests/test_storm.py': 12452,
 'chupa/journal.py': 8953,
 'chupa/config.py': 11898,
 'chupa/seams.py': 5551,
 'chupa/__main__.py': 9666,
 'tests/test_drain.py': 43454,
 'chupa/runner.py': 33227,
 'chupa/stages.py': 50768,
 'chupa/flake.py': 8728,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'storm-producer-wiring': {'chars': 4172,
                           'plan': ('19.I', '19.P3.storm-producer-wiring', '12'),
                           'context': ('chupa/storm.py',
                                       'chupa/box.py',
                                       'chupa/daemon.py',
                                       'tests/test_storm.py',
                                       'chupa/journal.py',
                                       'chupa/config.py',
                                       'chupa/seams.py'),
                           'on_demand': (),
                           'fenced_existing': ('chupa/storm.py',
                                               'chupa/box.py',
                                               'chupa/daemon.py',
                                               'tests/test_storm.py'),
                           'created': ('tests/test_storm_producer.py',),
                           'measured_render': 109454},
 'storm-notification-activation': {'chars': 5504,
                                   'plan': ('19.I', '19.P3.storm-notification-activation', '12'),
                                   'context': ('chupa/storm.py',
                                               'chupa/box.py',
                                               'chupa/daemon.py',
                                               'chupa/__main__.py',
                                               'tests/test_storm.py',
                                               'tests/test_drain.py',
                                               'chupa/runner.py',
                                               'chupa/stages.py',
                                               'chupa/flake.py',
                                               'chupa/journal.py',
                                               'chupa/config.py',
                                               'chupa/seams.py'),
                                   'on_demand': (),
                                   'fenced_existing': ('chupa/storm.py',
                                                       'chupa/box.py',
                                                       'chupa/daemon.py',
                                                       'chupa/__main__.py',
                                                       'tests/test_storm.py',
                                                       'tests/test_drain.py',
                                                       'chupa/runner.py',
                                                       'chupa/stages.py',
                                                       'chupa/flake.py'),
                                   'created': ('tests/test_storm_notification_activation.py',
                                               'tests/test_storm_producer.py'),
                                   'measured_render': 264173},
 'phase3-continue-18': {'chars': 9184,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.storm-dispatch-hold',
                                 '12',
                                 '20',
                                 '19.P3.checkpoint-push',
                                 '10'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_18.py'),
                        'measured_render': 123163}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/storm.py',
 'chupa/box.py',
 'chupa/daemon.py',
 'tests/test_storm.py',
 'chupa/journal.py',
 'chupa/config.py',
 'chupa/seams.py',
 'chupa/__main__.py',
 'tests/test_drain.py',
 'chupa/runner.py',
 'chupa/stages.py',
 'chupa/flake.py',
 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.storm-producer-wiring',
 '19.P3.storm-notification-activation',
 '19.P3.storm-dispatch-hold',
 '19.P3.checkpoint-push')

VALIDATED_ROW_CITATIONS = {'storm-producer-wiring': ('12',),
 'storm-notification-activation': ('12',),
 'storm-dispatch-hold': ('12', '20'),
 'checkpoint-push': ('10',)}

ENTRY_TESTS = {'storm-producer-wiring': ('test_new_and_dedup_arrivals_record_occurrences',
                           'test_arrival_replay_survives_restart_and_roll',
                           'test_dedup_preserves_resolved_message_and_incoming_identity',
                           'test_invalid_arrivals_and_callback_failures_do_not_publish',
                           'test_enqueue_crash_replay_finishes_once',
                           'test_box_operations_without_arrivals_are_idle',
                           'test_storm_producer_hook_is_dormant'),
 'storm-notification-activation': ('test_production_occurrence_id_recipes',
                                   'test_production_arrival_preserves_caller_behavior',
                                   'test_production_arrivals_and_dedup_hits_trip_once',
                                   'test_storm_threshold_window_and_signature_isolation',
                                   'test_storm_trip_targets_are_closed',
                                   'test_storm_trip_and_report_crash_replay',
                                   'test_storm_trip_evidence_fails_closed',
                                   'test_storm_report_cannot_recurse',
                                   'test_storm_activation_does_not_hold_dispatch_or_notify',
                                   'test_production_arrival_site_closure',
                                   'test_drain_merges_without_scanning_the_box'),
 'storm-dispatch-hold': ('test_live_drain_holds_only_emitting_stem',
                         'test_storm_hold_precedes_all_dispatch_accounting',
                         'test_non_pipeline_and_non_ticket_trips_do_not_hold',
                         'test_live_resume_releases_in_same_drain',
                         'test_storm_resume_is_identity_bound_and_once',
                         'test_multiple_storm_holds_release_independently',
                         'test_storm_hold_survives_restart_roll_and_expiry',
                         'test_storm_release_rearms_on_new_arrivals_only',
                         'test_storm_hold_crash_and_corrupt_evidence',
                         'test_storm_wait_preserves_kill_budget_and_quiescence'),
 'checkpoint-push': ('test_checkpoint_merge_and_daily_triggers',
                     'test_checkpoint_success_advances_once',
                     'test_checkpoint_failed_push_refires',
                     'test_checkpoint_crash_windows',
                     'test_checkpoint_timer_survives_restart_and_roll',
                     'test_checkpoint_boundary_is_dormant',
                     'test_op_argv',
                     'test_option_shaped_or_empty_refs_are_refused_before_exec')}

ENTRY_VERIFICATION = {'storm-producer-wiring': ('uv',
                           'run',
                           'pytest',
                           'tests/test_storm_producer.py',
                           'tests/test_storm.py',
                           'tests/test_box.py',
                           'tests/test_daemon_composition.py',
                           'tests/test_journal.py',
                           'tests/test_journal_roll.py'),
 'storm-notification-activation': ('uv',
                                   'run',
                                   'pytest',
                                   'tests/test_storm_notification_activation.py',
                                   'tests/test_storm.py',
                                   'tests/test_storm_producer.py',
                                   'tests/test_drain.py',
                                   'tests/test_box.py',
                                   'tests/test_journal.py',
                                   'tests/test_journal_roll.py')}

PRESERVATION = {'storm-producer-wiring': ('tests/test_box.py',
                           'tests/test_daemon_composition.py',
                           'tests/test_journal.py',
                           'tests/test_journal_roll.py'),
 'storm-notification-activation': ('tests/test_box.py',
                                   'tests/test_journal.py',
                                   'tests/test_journal_roll.py')}

CONTRACT_CUSTODY = {'storm-producer-wiring': {'Owner': '19.P3.storm-producer-wiring',
                           'Records': '19.P3.storm-producer-wiring',
                           'Observable': '19.P3.storm-producer-wiring',
                           'Tests': '19.P3.storm-producer-wiring'},
 'storm-notification-activation': {'Owner': '19.P3.storm-notification-activation',
                                   'Records': '19.P3.storm-notification-activation',
                                   'Observable': '19.P3.storm-notification-activation',
                                   'Tests': '19.P3.storm-notification-activation'},
 'storm-dispatch-hold': {'Owner': '19.P3.storm-dispatch-hold',
                         'Records': '19.P3.storm-dispatch-hold',
                         'Observable': '19.P3.storm-dispatch-hold',
                         'Tests': '19.P3.storm-dispatch-hold'},
 'checkpoint-push': {'Owner': '19.P3.checkpoint-push',
                     'Records': '19.P3.checkpoint-push',
                     'Observable': '19.P3.checkpoint-push',
                     'Tests': '19.P3.checkpoint-push'}}

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'patterns': ('Box(',
              '.enqueue(',
              'Journal(',
              'append',
              'read',
              'close',
              'build_daemon_core(',
              'storm',
              'not hasattr',
              '__all__',
              'tasks ==',
              'box.*event'),
 'production_arrival_callers': ('chupa/runner.py::failure_terminal:239,243',
                                'chupa/runner.py::_dead_dependents:549',
                                'chupa/stages.py::implement:490',
                                'chupa/stages.py::gather_evidence:587',
                                'chupa/flake.py::Flake.detect:164',
                                'chupa/box.py::ingest_bootstrap:190',
                                'chupa/box.py::ingest_main_checkout:201'),
 'callback_free_direct_tests': ('tests/test_author.py',
                                'tests/test_triage.py',
                                'tests/test_drain.py',
                                'tests/test_flake.py',
                                'tests/test_storm.py',
                                'tests/test_box.py'),
 'read_only_box_callers': ('chupa/triage.py:95',
                           'eval/shakeout/stages.py:194',
                           'tests/test_merge.py:198',
                           'tests/test_mergequeue.py:273,393',
                           'tests/test_stages.py:396,409',
                           'tests/test_second_problems.py:39',
                           'tests/test_diagnose.py:219',
                           'tests/test_drain_reentry.py:101'),
 'predecessor_migrations': {'tests/test_storm.py::test_storm_ledger_is_dormant': '19.L rules 2-3; '
                                                                                 'producer may '
                                                                                 'replace only '
                                                                                 'import absence '
                                                                                 'with behavioral '
                                                                                 'dormancy, '
                                                                                 'activation '
                                                                                 'proves '
                                                                                 'production '
                                                                                 'reachability',
                            'tests/test_storm.py::test_ledger_has_no_trip_side_effects': '19.L '
                                                                                         'rule 2; '
                                                                                         'activation '
                                                                                         'migrates '
                                                                                         'only '
                                                                                         'no-trip '
                                                                                         'assertion, '
                                                                                         'retains '
                                                                                         'ledger '
                                                                                         'obligations',
                            'tests/test_storm_producer.py::test_storm_producer_hook_is_dormant': '19.L '
                                                                                                 'rules '
                                                                                                 '2-3; '
                                                                                                 'sibling-created '
                                                                                                 'predecessor '
                                                                                                 'production '
                                                                                                 'absence '
                                                                                                 'migrates '
                                                                                                 'on '
                                                                                                 'activation'},
 'unchanged_assertions': ('tests/test_drain.py:264-276 triage calls empty, pending status, no '
                          'triage_pass signal; no blanket no-box-event assertion',
                          'tests/test_daemon_tasks.py ordinary exception propagation and cleanup '
                          'unchanged',
                          'Box read-only and callback-free direct callers unchanged; no public '
                          'allowlist migration'),
 'next_hold_migration': '19.P3.storm-dispatch-hold Observable; fence '
                        'test_storm_activation_does_not_hold_dispatch_or_notify and any other '
                        'predecessor dispatch-absence assertions, retaining no-notify'}

def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[p] for p in a['plan'])
            + sum(FILE_CHARS[p] for p in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == (*PAYLOADS, 'phase3-continue-18') == (
        'storm-producer-wiring', 'storm-notification-activation', 'phase3-continue-18')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # Rejection is a later lifecycle stamp, never a different birth path.
    t = validate_ticket(stem, _text(stem).replace('state: rejected', 'state: confirmed', 1), ROOT, BATCH)
    fm = t.frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == ('medium', 'medium')


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes <= t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {
        'storm-producer-wiring': ('phase3-continue-17',),
        'storm-notification-activation': ('phase3-continue-17', 'storm-producer-wiring'),
        'phase3-continue-18': PAYLOADS,
    }


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_FLOORS == {
        'storm-producer-wiring': ('chupa/storm.py', 'chupa/box.py', 'chupa/daemon.py',
                                  'tests/test_storm.py', 'tests/test_storm_producer.py'),
        'storm-notification-activation': ('chupa/storm.py', 'chupa/box.py', 'chupa/daemon.py',
                                        'chupa/__main__.py', 'tests/test_storm.py',
                                        'tests/test_drain.py', 'tests/test_storm_notification_activation.py'),
        'phase3-continue-18': ('tickets', 'tests/test_seeded_phase3_18.py'),
    }
    assert FENCE_ADDITIONS['storm-producer-wiring'] == FENCE_ADDITIONS['phase3-continue-18'] == {}
    assert set(FENCE_ADDITIONS['storm-notification-activation']) == {
        'chupa/runner.py', 'chupa/stages.py', 'chupa/flake.py', 'tests/test_storm_producer.py'}
    for path, reason in FENCE_ADDITIONS[stem].items():
        assert path in t.sections['Scope in / Scope out']
        assert '19.L rule' in reason
        if path.startswith('chupa/'):
            assert path in t.context and 'Context' in reason
        else:
            assert path not in (*t.context, *t.on_demand) and 'sibling-created' in reason
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert len(CLOSURE_SNAPSHOT['production_arrival_callers']) == 7
    assert len(CLOSURE_SNAPSHOT['predecessor_migrations']) == 3
    if stem in PAYLOADS:
        scope = t.sections['Scope in / Scope out']
        for fact in ('19.L rules 2-5', 'bootstrap on-entry reconciliation', 'inline admission',
                     'ordinary DaemonTasks exception propagation and cleanup', 'historical seeding tests'):
            assert fact in scope


@pytest.mark.parametrize('stem', PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    own = '19.P3.' + stem
    assert t.plan_contract == AUTHORED[stem]['plan'] == ('19.I', own, '12')
    assert own in VALIDATED_ENTRIES and VALIDATED_ROW_CITATIONS[stem] == ('12',)
    assert CONTRACT_CUSTODY[stem] == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert len(ENTRY_TESTS[stem]) == (7 if stem == PAYLOADS[0] else 11)
    assert all(name in t.sections['Acceptance criteria'] for name in ENTRY_TESTS[stem])
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract for Owner, Records, Observable',
                 'every named Tests obligation', 'implement all of it', 'record custody',
                 "unit's Owner", 'never copy unit text', 'real CLI run/drain', 'build_daemon_core',
                 'merged production-composition harness', 'sole durable event writer',
                 'sole queue-record writer', 'Journal(state_dir, clock) and append/read/close signatures',
                 'occurrence, replay, window, corruption, durability and crash', 'injected seams',
                 'scripted callbacks', 'disposable repositories', 'asyncio barriers',
                 'manual HGATE release', 'verification filtering', 'unearned records'):
        assert fact in scope, fact
    for part in CONTRACT_CUSTODY[stem]:
        assert f'- **{part}:**' not in _text(stem)
    if stem == PAYLOADS[0]:
        assert 'behaviorally dormant until storm-notification-activation' in scope
        assert 'test_storm_ledger_is_dormant' in scope
        assert 'Preserve test_ledger_has_no_trip_side_effects' in scope
    else:
        for fact in ('closed production arrival-site list and all replay-stable occurrence_id recipes',
                     'never derive new records from caller reads', 'test_production_arrival_site_closure',
                     'test_production_occurrence_id_recipes', 'test_production_arrival_preserves_caller_behavior',
                     'test_storm_activation_does_not_hold_dispatch_or_notify',
                     'test_drain_merges_without_scanning_the_box', 'triage-call and pending-status assertions',
                     'not a blanket no-box-event assertion', 'no external notify transport or dispatch suppression',
                     'storm-dispatch-hold alone owns the later hold and identity-bound release', 'never Context here'):
            assert fact in scope, fact


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-18')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.storm-dispatch-hold', '12', '20',
        '19.P3.checkpoint-push', '10')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_18.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == (
        '19.P3.storm-producer-wiring', '19.P3.storm-notification-activation',
        '19.P3.storm-dispatch-hold', '19.P3.checkpoint-push')
    assert VALIDATED_ROW_CITATIONS == {
        'storm-producer-wiring': ('12',), 'storm-notification-activation': ('12',),
        'storm-dispatch-hold': ('12', '20'), 'checkpoint-push': ('10',)}
    assert len(ENTRY_TESTS['storm-dispatch-hold']) == 10
    assert CONTRACT_CUSTODY['storm-dispatch-hold'] == {
        part: '19.P3.storm-dispatch-hold' for part in ('Owner', 'Records', 'Observable', 'Tests')}
    scope = t.sections['Scope in / Scope out']
    for fact in ('BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[18:]', 'admissions[19:]',
                 'admissions[20:]', 'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
                 'Author only storm-dispatch-hold and phase3-continue-19',
                 'hold depends on phase3-continue-18, starts high/high',
                 'cites exactly 19.I, 19.P3.storm-dispatch-hold, section 12 and section 20',
                 'Never copy unit text into a seed or into this seeding ticket',
                 "Carry this cite-don't-copy rule forward to phase3-continue-19",
                 'checkpoint-push at medium/medium', 'tests/test_seeded_phase3_19.py',
                 "never this batch's tests/test_seeded_phase3_18.py", '19.P3.checkpoint-push', 'section 10',
                 'required next-seeder lookahead, not payloads to author here', '19.L closure rules 2-5',
                 'Context/on-demand partition', '300,000-character headroom',
                 'Prompt-specs and delimiter-bearing sources are never Context',
                 'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
                 'named invariant obligations', 'record custody',
                 'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
                 'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
                 'terminal phase3-exit as its sole payload with no successor',
                 'keep previously approved seeds verbatim', 'ticket_sha',
                 'chupa(phase3-continue-18): seeds', "Commit only this ticket's new test",
                 'test_storm_activation_does_not_hold_dispatch_or_notify', 'retaining its no-notify proof',
                 'tests/test_storm.py and tests/test_storm_producer.py',
                 'never derive new records from caller reads', 'Journal remains the sole durable event writer',
                 'ControlInbox the sole control-decision writer'):
        assert fact in scope, fact
    for name in (
        'test_named_stems_cover_exactly_this_admission_and_successor',
        'test_seed_passes_intake_lint_with_confirmed_seed_birth',
        'test_stuck_budget_fits_the_drain_envelope', 'test_dependencies_as_authored',
        'test_fence_contains_its_floor_and_only_earned_additions',
        'test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract',
        'test_successor_cites_next_admission_and_embeds_merged_earlier_idiom',
        'test_context_closure_and_max_effort_render_use_authoring_snapshots',
        'test_payloads_run_preservation_suites_without_fencing_or_embedding_them',
    ):
        assert name in scope
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
    assert 0 < a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS == 300000
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path
    assert 'tests/test_storm_producer.py' in AUTHORED[PAYLOADS[1]]['created']
    assert 'tests/test_storm_producer.py' not in (*t.context, *t.on_demand)


@pytest.mark.parametrize('stem', PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification == (ENTRY_VERIFICATION[stem], ('uv', 'run', 'pytest', '-q'))
    assert ENTRY_VERIFICATION == {
        'storm-producer-wiring': ('uv', 'run', 'pytest', 'tests/test_storm_producer.py',
                                  'tests/test_storm.py', 'tests/test_box.py',
                                  'tests/test_daemon_composition.py', 'tests/test_journal.py',
                                  'tests/test_journal_roll.py'),
        'storm-notification-activation': ('uv', 'run', 'pytest',
                                        'tests/test_storm_notification_activation.py',
                                        'tests/test_storm.py', 'tests/test_storm_producer.py',
                                        'tests/test_drain.py', 'tests/test_box.py',
                                        'tests/test_journal.py', 'tests/test_journal_roll.py'),
    }
    assert set(PRESERVATION[stem]) == {p for p in ENTRY_VERIFICATION[stem]
                                     if p.startswith('tests/') and p not in t.scope_fence}
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites in Verification only, neither fenced nor embedded' in t.sections['Scope in / Scope out']
