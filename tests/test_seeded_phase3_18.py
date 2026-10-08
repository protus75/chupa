"""Admission 18: live-registry preflight, earned closures and fixed authoring snapshots.

Parsed admissions[18:] directly from the plan. Hold, checkpoint and serve entries
passed entry_unit_gap and resolve_plan_contract with every row citation before
writing. No entry-unit body or registry suffix is copied here. Never refresh sizes.
"""

from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = 'e98187e807bdb021e19298e4b2570905038bfe85'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('storm-dispatch-hold',)

BATCH = ('storm-dispatch-hold', 'phase3-continue-19')

ADMISSION_INDEX = 18

NEXT_ADMISSION_INDEX = 19

NEXT_SEEDER_INDEX = 20

EDGES = {'storm-dispatch-hold': ('phase3-continue-18',), 'phase3-continue-19': ('storm-dispatch-hold',)}

STARTS = {'storm-dispatch-hold': ('high', 'high'), 'phase3-continue-19': ('medium', 'medium')}

FENCE_FLOORS = {'storm-dispatch-hold': ('chupa/storm.py',
                         'chupa/control.py',
                         'chupa/daemon.py',
                         'chupa/drain.py',
                         'chupa/__main__.py',
                         'tests/test_storm_hold.py'),
 'phase3-continue-19': ('tickets', 'tests/test_seeded_phase3_19.py')}

FENCE_ADDITIONS = {'storm-dispatch-hold': {'tests/test_storm_notification_activation.py': '19.L rules 2-3: '
                                                                        'test_storm_activation_does_not_hold_dispatch_or_notify '
                                                                        'and '
                                                                        'test_storm_leaves_daemon_selection_and_accounting_unchanged; '
                                                                        'migrate only invalidated '
                                                                        'dispatch absence, retain '
                                                                        'no-notify; Context',
                         'tests/test_storm.py': '19.L rules 2-3: '
                                                'test_ledger_trip_uses_only_journal_and_box '
                                                'forbids PauseConsumer.hold; preserve direct '
                                                'component idleness and ledger invariants; Context',
                         'tests/test_storm_producer.py': '19.L rules 2-3: '
                                                         'test_storm_producer_hook_is_active '
                                                         'forbids PauseConsumer.hold; preserve '
                                                         'arrival/replay/crash and direct '
                                                         'idleness; Context'},
 'phase3-continue-19': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.storm-dispatch-hold': 9662,
 '12': 20224,
 '20': 4367,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.checkpoint-push': 7067,
 '10': 6636,
 '19.P3.serve-activation': 13073,
 '18': 13338}

FILE_CHARS = {'chupa/storm.py': 7964,
 'chupa/control.py': 8166,
 'chupa/daemon.py': 21868,
 'chupa/drain.py': 27168,
 'chupa/__main__.py': 9886,
 'tests/test_storm_notification_activation.py': 28874,
 'tests/test_storm.py': 11762,
 'tests/test_storm_producer.py': 13340,
 'chupa/journal.py': 8953,
 'chupa/box.py': 10000,
 'chupa/config.py': 11898,
 'chupa/seams.py': 5551,
 'tests/test_seeded_phase3_core.py': 5425}

STANDING_CONTEXT = ()

AUTHORED = {'storm-dispatch-hold': {'chars': 6795,
                         'plan': ('19.I', '19.P3.storm-dispatch-hold', '12', '20'),
                         'context': ('chupa/storm.py',
                                     'chupa/control.py',
                                     'chupa/daemon.py',
                                     'chupa/drain.py',
                                     'chupa/__main__.py',
                                     'tests/test_storm_notification_activation.py',
                                     'tests/test_storm.py',
                                     'tests/test_storm_producer.py',
                                     'chupa/journal.py',
                                     'chupa/box.py',
                                     'chupa/config.py',
                                     'chupa/seams.py'),
                         'on_demand': (),
                         'fenced_existing': ('chupa/storm.py',
                                             'chupa/control.py',
                                             'chupa/daemon.py',
                                             'chupa/drain.py',
                                             'chupa/__main__.py',
                                             'tests/test_storm_notification_activation.py',
                                             'tests/test_storm.py',
                                             'tests/test_storm_producer.py'),
                         'created': ('tests/test_storm_hold.py',),
                         'measured_render': 212855},
 'phase3-continue-19': {'chars': 8871,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.checkpoint-push',
                                 '10',
                                 '19.P3.serve-activation',
                                 '18',
                                 '20'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_19.py'),
                        'measured_render': 119375}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/storm.py',
 'chupa/control.py',
 'chupa/daemon.py',
 'chupa/drain.py',
 'chupa/__main__.py',
 'tests/test_storm_notification_activation.py',
 'tests/test_storm.py',
 'tests/test_storm_producer.py',
 'chupa/journal.py',
 'chupa/box.py',
 'chupa/config.py',
 'chupa/seams.py',
 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.storm-dispatch-hold', '19.P3.checkpoint-push', '19.P3.serve-activation')

VALIDATED_ROW_CITATIONS = {'storm-dispatch-hold': ('12', '20'), 'checkpoint-push': ('10',), 'serve-activation': ('18', '20')}

ENTRY_TESTS = {'storm-dispatch-hold': ('test_live_drain_holds_only_emitting_stem',
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
                     'test_option_shaped_or_empty_refs_are_refused_before_exec'),
 'serve-activation': ('test_serve_cli_uses_production_composition',
                      'test_serve_holds_lock_through_cleanup',
                      'test_serve_startup_precedes_all_work',
                      'test_serve_waits_at_quiescence_and_discovers_work',
                      'test_serve_consumers_use_existing_writers',
                      'test_serve_control_precedes_offer_accounting',
                      'test_serve_kill_unwinds_executor_before_workers',
                      'test_serve_worker_failure_and_kill_suppression',
                      'test_serve_signal_stop_and_restart_recovery',
                      'test_serve_recurring_maintenance_uses_injected_time',
                      'test_serve_heartbeat_requires_responsive_components',
                      'test_serve_storm_hold_and_resume',
                      'test_production_serve_graph_is_reachable')}

CONTRACT_CUSTODY = {'Owner': '19.P3.storm-dispatch-hold',
 'Records': '19.P3.storm-dispatch-hold',
 'Observable': '19.P3.storm-dispatch-hold',
 'Tests': '19.P3.storm-dispatch-hold'}

ENTRY_VERIFICATION = ('uv',
 'run',
 'pytest',
 'tests/test_storm_hold.py',
 'tests/test_storm_notification_activation.py',
 'tests/test_storm.py',
 'tests/test_storm_producer.py',
 'tests/test_control.py',
 'tests/test_control_cli.py',
 'tests/test_daemon_pause.py',
 'tests/test_drain.py',
 'tests/test_kill_cli_activation.py',
 'tests/test_daemon_composition.py',
 'tests/test_box.py',
 'tests/test_journal.py',
 'tests/test_journal_roll.py')

PRESERVATION = ('tests/test_control.py',
 'tests/test_control_cli.py',
 'tests/test_daemon_pause.py',
 'tests/test_drain.py',
 'tests/test_kill_cli_activation.py',
 'tests/test_daemon_composition.py',
 'tests/test_box.py',
 'tests/test_journal.py',
 'tests/test_journal_roll.py')

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'patterns': ('storm|Storm|STORM_TRIP',
              'PauseConsumer|ControlInbox|released_hold_ids',
              'build_control|build_daemon_core|storm_producer',
              'not hasattr|no.*(hold|storm)|storm.*(unchanged|absence)',
              'public.*(surface|operation)|allowed.*(method|operation)'),
 'production_callers': ('chupa/__main__.py:build_control -> storm_producer, PauseConsumer',
                        'chupa/__main__.py:build_daemon_core -> build_control, daemon_core',
                        'chupa/__main__.py:main -> build_control, drain.drain, runner.run_ticket',
                        'chupa/box.py:ingest_main_checkout -> storm_producer',
                        'chupa/runner.py:failure_terminal, run_ticket, _dead_dependents -> '
                        'storm_producer',
                        'chupa/stages.py:implement, gather_evidence -> storm_producer',
                        'eval/shakeout/bench.py -> build_control, drain.drain'),
 'direct_control_caller_paths': ('chupa/daemon.py',
                                 'chupa/__main__.py',
                                 'eval/shakeout/bench.py',
                                 'tests/test_control.py',
                                 'tests/test_kill_signal_journal.py',
                                 'tests/test_kill_cli_activation.py',
                                 'tests/test_mergequeue.py',
                                 'tests/test_daemon_composition.py',
                                 'tests/test_merge.py',
                                 'tests/test_drain.py',
                                 'tests/test_control_cli.py',
                                 'tests/test_flake.py',
                                 'tests/test_heartbeat.py',
                                 'tests/test_storm_notification_activation.py'),
 'direct_storm_caller_paths': ('chupa/daemon.py', 'chupa/__main__.py', 'chupa/box.py',
                              'chupa/runner.py', 'chupa/stages.py', 'tests/test_drain.py',
                              'tests/test_storm.py', 'tests/test_storm_producer.py',
                              'tests/test_storm_notification_activation.py'),
 'predecessor_assertions': ('tests/test_storm_notification_activation.py::test_storm_activation_does_not_hold_dispatch_or_notify',
                            'tests/test_storm_notification_activation.py::test_storm_leaves_daemon_selection_and_accounting_unchanged',
                            'tests/test_storm.py::test_ledger_trip_uses_only_journal_and_box',
                            'tests/test_storm_producer.py::test_storm_producer_hook_is_active'),
 'disposition': 'Public constructor and operation signatures stay valid; production composition '
                'owners are in the registry floor. No caller-read record invention and no further '
                'earned caller path. Preserve run/drain reconciliation, inline admission, ordinary '
                'DaemonTasks exceptions/cleanup; daemon stage selection activates later through '
                'serve, direct construction stays idle. Historical seeding tests are immutable.',
 'next_payload': 'checkpoint-push: tests/test_git.py public-operation allowlist is already fenced; '
                 'new checkpoint module/test are created, not Context; Effects/Timers/admission '
                 'records keep their writers',
 'next_seeder': 'serve-activation: validated entry and row citations 18/20; deep high/high, '
                'closures earned by future authoring greps, not a payload of this batch'}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    # One bound at max effort; sizes are frozen, never measured by this test.
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[p] for p in a['plan'])
            + sum(FILE_CHARS[p] for p in dict.fromkeys((*a['context'], *STANDING_CONTEXT, *extra))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('storm-dispatch-hold',)
    assert BATCH == (*PAYLOADS, 'phase3-continue-19')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)
    assert (ADMISSION_INDEX, NEXT_ADMISSION_INDEX, NEXT_SEEDER_INDEX) == (18, 19, 20)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # A later rejection is lifecycle history, not a different birth path.
    t = validate_ticket(stem, _text(stem).replace('state: rejected', 'state: confirmed', 1), ROOT, BATCH)
    fm = t.frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == STARTS[stem]
    assert STARTS == {'storm-dispatch-hold': ('high', 'high'),
                      'phase3-continue-19': ('medium', 'medium')}


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == ((90, 180) if stem in PAYLOADS else (60, 90))
    assert 0 < t.expected_minutes <= t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'storm-dispatch-hold': ('phase3-continue-18',),
                     'phase3-continue-19': ('storm-dispatch-hold',)}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_FLOORS == {
        'storm-dispatch-hold': ('chupa/storm.py', 'chupa/control.py', 'chupa/daemon.py',
                               'chupa/drain.py', 'chupa/__main__.py', 'tests/test_storm_hold.py'),
        'phase3-continue-19': ('tickets', 'tests/test_seeded_phase3_19.py'),
    }
    assert set(FENCE_ADDITIONS['storm-dispatch-hold']) == {
        'tests/test_storm_notification_activation.py', 'tests/test_storm.py', 'tests/test_storm_producer.py'}
    assert FENCE_ADDITIONS['phase3-continue-19'] == {}
    for path, reason in FENCE_ADDITIONS[stem].items():
        assert path in t.sections['Scope in / Scope out']
        assert '19.L rules 2-3' in reason and 'Context' in reason
        assert path in t.context
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert len(CLOSURE_SNAPSHOT['predecessor_assertions']) == 4
    for assertion in CLOSURE_SNAPSHOT['predecessor_assertions']:
        path, name = assertion.split('::')
        assert path in FENCE_ADDITIONS[PAYLOADS[0]]
        assert name in _ticket(PAYLOADS[0]).sections['Scope in / Scope out']
    assert len(CLOSURE_SNAPSHOT['production_callers']) == 7
    assert 'eval/shakeout/bench.py' in CLOSURE_SNAPSHOT['direct_control_caller_paths']
    assert 'signatures stay valid' in CLOSURE_SNAPSHOT['disposition']


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket('storm-dispatch-hold')
    own = '19.P3.storm-dispatch-hold'
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', own, '12', '20')
    assert VALIDATED_ROW_CITATIONS[t.stem] == ('12', '20')
    assert CONTRACT_CUSTODY == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert ENTRY_TESTS[t.stem] == (
        'test_live_drain_holds_only_emitting_stem',
        'test_storm_hold_precedes_all_dispatch_accounting',
        'test_non_pipeline_and_non_ticket_trips_do_not_hold',
        'test_live_resume_releases_in_same_drain',
        'test_storm_resume_is_identity_bound_and_once',
        'test_multiple_storm_holds_release_independently',
        'test_storm_hold_survives_restart_roll_and_expiry',
        'test_storm_release_rearms_on_new_arrivals_only',
        'test_storm_hold_crash_and_corrupt_evidence',
        'test_storm_wait_preserves_kill_budget_and_quiescence',
    )
    assert all(name in t.sections['Acceptance criteria'] for name in ENTRY_TESTS[t.stem])
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract', 'every named Tests obligation',
                 'record custody and release authority', 'never copy unit text',
                 'real CLI run/drain', 'build_daemon_core', 'merged production-composition harness',
                 'Journal(state_dir, clock) and append/read/close signatures',
                 'sole durable event writer', 'sole queue-record writer', 'sole control-decision writer',
                 'bootstrap on-entry reconciliation', 'inline admission',
                 'ordinary DaemonTasks exception propagation and cleanup',
                 'occurrence, replay, window, corruption, durability and crash',
                 'no-external-notify', 'injected seams', 'scripted callbacks',
                 'disposable repositories', 'asyncio barriers', 'historical seeding tests'):
        assert fact in scope, fact
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(t.stem)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-19')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.checkpoint-push', '10',
        '19.P3.serve-activation', '18', '20')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_19.py')
    assert VALIDATED_ENTRIES == ('19.P3.storm-dispatch-hold', '19.P3.checkpoint-push',
                                 '19.P3.serve-activation')
    assert VALIDATED_ROW_CITATIONS == {'storm-dispatch-hold': ('12', '20'),
                                      'checkpoint-push': ('10',), 'serve-activation': ('18', '20')}
    assert len(ENTRY_TESTS['checkpoint-push']) == 8
    assert 'test_serve_storm_hold_and_resume' in ENTRY_TESTS['serve-activation']
    scope = t.sections['Scope in / Scope out']
    for fact in ('admissions[19:]', 'entry_unit_gap', 'resolve_plan_contract',
                 'Author only checkpoint-push and phase3-continue-20',
                 'checkpoint-push depends on phase3-continue-19', 'starts medium/medium',
                 'cites exactly 19.I, 19.P3.checkpoint-push and section 10',
                 'admissions[20:]', 'admissions[21:]', 'serve-activation at high/high',
                 'depending on checkpoint-push', 'tests/test_seeded_phase3_20.py',
                 "never this batch's tests/test_seeded_phase3_19.py",
                 'section 18 and section 20', 'next-seeder lookahead, not payloads',
                 '19.L closure rules 2-5', 'grep flipped symbols', 'chupa/, eval/ and tests/',
                 'record custody', 'named invariant', 'Never copy unit text',
                 '300,000-character headroom', 'Prompt-specs and delimiter-bearing sources',
                 'Created paths belong in neither', 'plan-unit lengths recorded IN that test',
                 'authoring head, merged idiom blob', 'seeding.max_seeds_per_admission',
                 'terminal phase3-exit as its sole payload with no successor',
                 'never seed past the next phase', 'keep previously approved seeds verbatim',
                 're-author only snagged seeds', 'uncommitted for Check',
                 'chupa(phase3-continue-19): seeds ticket-plane commit'):
        assert fact in scope, fact
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(t.stem)


@pytest.mark.parametrize('stem', BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert AUTHORING_HEAD == 'e98187e807bdb021e19298e4b2570905038bfe85'
    assert MERGED_IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(t.scope_fence) == set(a['fenced_existing']) | set(a['created'])
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert not set(a['context']) & set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert set(a['context']) <= set(DELIMITER_FREE_AT_AUTHORING)
    assert not any(p.startswith('specs/') or p == 'CHUPA_PLAN.md' for p in a['context'])
    assert all(FILE_CHARS[p] > 0 for p in (*a['context'], *a['on_demand']))
    assert all(PLAN_CHARS[p] > 0 for p in a['plan'])
    assert 0 < a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS == 300000
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS
    assert 'tests/test_seeded_phase3_18.py' not in (*t.context, *t.on_demand)
    assert 'tests/test_storm_hold.py' in AUTHORED[PAYLOADS[0]]['created']


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket('storm-dispatch-hold')
    assert t.verification == (ENTRY_VERIFICATION, ('uv', 'run', 'pytest', '-q'))
    assert ENTRY_VERIFICATION == ('uv', 'run', 'pytest', 'tests/test_storm_hold.py',
        'tests/test_storm_notification_activation.py', 'tests/test_storm.py', 'tests/test_storm_producer.py',
        'tests/test_control.py', 'tests/test_control_cli.py', 'tests/test_daemon_pause.py',
        'tests/test_drain.py', 'tests/test_kill_cli_activation.py', 'tests/test_daemon_composition.py',
        'tests/test_box.py', 'tests/test_journal.py', 'tests/test_journal_roll.py')
    assert set(PRESERVATION) == {p for p in ENTRY_VERIFICATION
                                 if p.startswith('tests/') and p not in t.scope_fence}
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites in Verification only, neither fenced nor embedded' in t.sections['Scope in / Scope out']
