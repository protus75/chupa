"""Admission 20: identity and closure over fixed authoring measurements.

Parsed admissions[20:] directly from the plan. Both entry_unit_gap and
resolve_plan_contract validated serve, daemon-admission and recovery lookahead.
No entry body or registry suffix is duplicated here. Measurements never refresh.
"""

from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
AUTHORING_HEAD = 'afaa204641007d7faf40bf6c37d991cfd02187ca'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('serve-activation',)

BATCH = ('serve-activation', 'phase3-continue-21')

ADMISSION_INDEX = 20

NEXT_ADMISSION_INDEX = 21

NEXT_SEEDER_INDEX = 22

EDGES = {'serve-activation': ('phase3-continue-20',), 'phase3-continue-21': ('serve-activation',)}

STARTS = {'serve-activation': ('high', 'high'), 'phase3-continue-21': ('medium', 'medium')}

FENCE_FLOORS = {'serve-activation': ('chupa/serve.py',
                      'chupa/daemon.py',
                      'chupa/__main__.py',
                      'chupa/triage.py',
                      'chupa/driver.py',
                      'chupa/runner.py',
                      'chupa/stages.py',
                      'chupa/scheduler.py',
                      'chupa/storm.py',
                      'tests/test_stages.py',
                      'tests/test_daemon_admission.py',
                      'tests/test_daemon_config.py',
                      'tests/test_serve.py',
                      'tests/test_daemon_composition.py',
                      'tests/test_daemon_tasks.py',
                      'tests/test_kill_worker_stop.py',
                      'tests/test_kill_failure_suppression.py',
                      'tests/test_heartbeat.py',
                      'tests/test_storm.py'),
 'phase3-continue-21': ('tickets', 'tests/test_seeded_phase3_21.py')}

FENCE_ADDITIONS = {'serve-activation': {'tests/test_restart_timers.py': '19.L rules 2-3: '
                                                      'test_restart_construction_is_idle pins CLI '
                                                      'serve absence; Context',
                      'tests/test_checkpoint.py': '19.L rules 2-3: '
                                                  'test_checkpoint_boundary_is_dormant pins '
                                                  'production checkpoint absence; Context'},
 'phase3-continue-21': {}}

HEADROOM_CHARS = 300000

RENDER_OVERHEAD = 2000

IMPLEMENT_SPEC_CHARS = 4316

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.serve-activation': 13073,
 '18': 13338,
 '20': 4367,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.serve-merge-admission': 10740,
 '9': 19656,
 '19.P3.worker-recovery-disposition': 5589,
 '6': 36783,
 '15': 17090}

FILE_CHARS = {'tests/test_daemon_config.py': 16015,
 'tests/test_daemon_admission.py': 9543,
 'tests/test_stages.py': 26094,
 'chupa/storm.py': 9574,
 'chupa/stages.py': 53586,
 'chupa/daemon.py': 23259,
 'chupa/__main__.py': 10026,
 'tests/test_daemon_tasks.py': 13570,
 'tests/test_kill_worker_stop.py': 15142,
 'tests/test_kill_failure_suppression.py': 18836,
 'tests/test_heartbeat.py': 10343,
 'tests/test_storm.py': 11748,
 'tests/test_restart_timers.py': 30914,
 'tests/test_checkpoint.py': 24111,
 'chupa/runner.py': 34156,
 'chupa/merge.py': 13596,
 'chupa/triage.py': 9510,
 'chupa/driver.py': 16659,
 'chupa/checkpoint.py': 6775,
 'chupa/control.py': 9879,
 'chupa/scheduler.py': 2425,
 'chupa/watcher.py': 2799,
 'chupa/restart.py': 1951,
 'chupa/timers.py': 4966,
 'tests/test_daemon_composition.py': 89684,
 'tests/test_seeded_phase3_core.py': 5425}

STANDING_CONTEXT = ()

AUTHORED = {'serve-activation': {'chars': 8235,
                      'plan': ('19.I', '19.P3.serve-activation', '18', '20'),
                      'context': ('chupa/daemon.py',
                                  'chupa/__main__.py',
                                  'tests/test_daemon_tasks.py',
                                  'tests/test_kill_worker_stop.py',
                                  'tests/test_kill_failure_suppression.py',
                                  'tests/test_heartbeat.py',
                                  'tests/test_storm.py',
                                  'tests/test_restart_timers.py',
                                  'tests/test_checkpoint.py',
                                  'chupa/runner.py',
                                  'chupa/merge.py',
                                  'chupa/triage.py',
                                  'chupa/checkpoint.py',
                                  'chupa/control.py',
                                  'chupa/scheduler.py',
                                  'chupa/watcher.py',
                                  'chupa/restart.py',
                                  'chupa/timers.py',
                                  'chupa/scheduler.py'),
                      'on_demand': ('tests/test_daemon_composition.py', 'chupa/driver.py', 'chupa/stages.py', 'chupa/storm.py', 'tests/test_stages.py', 'tests/test_daemon_admission.py', 'tests/test_daemon_config.py'),
                      'fenced_existing': ('chupa/daemon.py',
                                          'chupa/__main__.py',
                                          'chupa/triage.py',
                                          'chupa/driver.py',
                                          'chupa/runner.py',
                                          'chupa/stages.py',
                                          'chupa/scheduler.py',
                                          'chupa/storm.py',
                                          'tests/test_stages.py',
                                          'tests/test_daemon_admission.py',
                                          'tests/test_daemon_config.py',
                                          'tests/test_daemon_composition.py',
                                          'tests/test_daemon_tasks.py',
                                          'tests/test_kill_worker_stop.py',
                                          'tests/test_kill_failure_suppression.py',
                                          'tests/test_heartbeat.py',
                                          'tests/test_storm.py',
                                          'tests/test_restart_timers.py',
                                          'tests/test_checkpoint.py'),
                      'created': ('chupa/serve.py', 'tests/test_serve.py'),
                      'measured_render': 288936},
 'phase3-continue-21': {'chars': 10401,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.serve-merge-admission',
                                 '9',
                                 '19.P3.worker-recovery-disposition',
                                 '6',
                                 '15'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_21.py'),
                        'measured_render': 166042}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/daemon.py',
 'chupa/scheduler.py',
 'chupa/driver.py',
 'chupa/__main__.py',
 'tests/test_daemon_tasks.py',
 'tests/test_kill_worker_stop.py',
 'tests/test_kill_failure_suppression.py',
 'tests/test_heartbeat.py',
 'tests/test_storm.py',
 'tests/test_restart_timers.py',
 'tests/test_checkpoint.py',
 'chupa/runner.py',
 'chupa/merge.py',
 'chupa/triage.py',
 'chupa/checkpoint.py',
 'chupa/control.py',
 'chupa/scheduler.py',
 'chupa/watcher.py',
 'chupa/restart.py',
 'chupa/timers.py',
 'tests/test_daemon_composition.py',
 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.serve-activation', '19.P3.serve-merge-admission', '19.P3.worker-recovery-disposition')

VALIDATED_ROW_CITATIONS = {'serve-activation': ('18', '20'),
 'serve-merge-admission': ('9',),
 'worker-recovery-disposition': ('6', '15')}

ENTRY_TESTS = {'serve-activation': ('test_serve_cli_uses_production_composition',
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
                      'test_production_serve_graph_is_reachable',
                      'test_storm_ledger_is_reachable'),
 'serve-merge-admission': ('test_daemon_prechecks_precede_offer',
                           'test_bootstrap_pipeline_keeps_inline_admission',
                           'test_admission_mode_is_explicit',
                           'test_serve_routes_settled_run_to_composed_queue_once',
                           'test_serve_admission_rebases_regates_and_retires',
                           'test_serve_admission_refusal_keeps_main_green',
                           'test_serve_conflict_handoff_runs_after_admission_unwinds',
                           'test_serve_admission_holds_and_cleanup',
                           'test_inline_admission_does_not_use_merge_queue'),
 'worker-recovery-disposition': ('test_recovery_alert_records_producing_run',
                                 'test_recovery_alert_precedes_worktree_removal',
                                 'test_recovery_alert_is_once_per_reaped_run',
                                 'test_recovery_alert_failures_preserve_terminal_history',
                                 'test_recovery_alert_does_not_change_disposition',
                                 'test_restart_reuses_orphan_reconciliation')}

CONTRACT_CUSTODY = {'Owner': '19.P3.serve-activation',
 'Records': '19.P3.serve-activation',
 'Observable': '19.P3.serve-activation',
 'Tests': '19.P3.serve-activation'}

NAMED_OBLIGATIONS = {'test_serve_cli_uses_production_composition': '19.P3.serve-activation',
 'test_serve_holds_lock_through_cleanup': '19.P3.serve-activation',
 'test_serve_startup_precedes_all_work': '19.P3.serve-activation',
 'test_serve_waits_at_quiescence_and_discovers_work': '19.P3.serve-activation',
 'test_serve_consumers_use_existing_writers': '19.P3.serve-activation',
 'test_serve_control_precedes_offer_accounting': '19.P3.serve-activation',
 'test_serve_kill_unwinds_executor_before_workers': '19.P3.serve-activation',
 'test_serve_worker_failure_and_kill_suppression': '19.P3.serve-activation',
 'test_serve_signal_stop_and_restart_recovery': '19.P3.serve-activation',
 'test_serve_recurring_maintenance_uses_injected_time': '19.P3.serve-activation',
 'test_serve_heartbeat_requires_responsive_components': '19.P3.serve-activation',
 'test_serve_storm_hold_and_resume': '19.P3.serve-activation',
 'test_production_serve_graph_is_reachable': '19.P3.serve-activation',
 'test_storm_ledger_is_reachable': '19.P3.serve-activation'}

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'patterns': ('\\bserve\\b|not hasattr|choices',
              'DaemonTasks|WorkerStop|WorkerFailureObserver|HeartbeatCycle|checkpoint_push',
              'build_daemon_core|daemon_core|compose_pipeline|prepare_pipeline|TicketWriter',
              'Journal\\(|append\\(|read\\(|close\\(',
              'public.*(surface|operation)|construction_is_idle|is_dormant'),
 'serve_absence': ('tests/test_restart_timers.py:101', 'test_restart_construction_is_idle'),
 'checkpoint_absence': ('tests/test_checkpoint.py:476',
                        'test_checkpoint_boundary_is_dormant',
                        'tests/test_checkpoint.py:523 _dormant_core'),
 'predecessor_tests': {'tests/test_daemon_tasks.py': 'test_background_consumers_are_dormant',
                       'tests/test_kill_worker_stop.py': 'test_kill_worker_stop_is_dormant',
                       'tests/test_kill_failure_suppression.py': 'test_kill_failure_suppression_is_dormant',
                       'tests/test_heartbeat.py': 'test_heartbeat_is_dormant',
                       'tests/test_storm.py': 'test_storm_ledger_is_reachable'},
 'direct_core_callers': ('tests/test_daemon_composition.py',
                         'tests/test_storm_notification_activation.py'),
 'core_alias_caller': ('tests/test_heartbeat.py', 'cli.build_daemon_core -> wired_graph'),
 'pipeline_callers': ('chupa/runner.py', 'tests/test_merge.py', 'tests/test_daemon_composition.py'),
 'production_roots': ('chupa/__main__.py:main -> run_ticket/drain',
                      'chupa/__main__.py:build_daemon_core -> StartupBoundary/Restart/Timers',
                      'chupa/runner.py:bind -> TicketWriter/compose_pipeline',
                      'eval/shakeout/bench.py:Bench -> Checkout/Journal'),
 'disposition': 'Preserve public signatures and core construction idleness; production serve owns '
                'new binding. No runner/merge mode changes here. Storm core-selection callers '
                'remain unchanged; selection hold applies at serve offers, preserving bare-core '
                'callers. Journal callers unchanged.',
 'next_admission_additions': {'chupa/runner.py': '19.L rule 5 and section 9 seam owner: '
                                                 'drive/settlement boundary; Context by default',
                              'chupa/daemon.py': '19.L rule 5 and section 9 seam owner: '
                                                 'TicketWriter/post-unwind handoff; Context by '
                                                 'default'},
 'next_seeder_additions': {'tests/test_restart_timers.py': '19.L rule 2: '
                                                           'test_restart_reuses_orphan_reconciliation '
                                                           'pins abandonment as last removal '
                                                           'record; Context by default'}}

ENTRY_VERIFICATION = ('uv',
 'run',
 'pytest',
 'tests/test_serve.py',
 'tests/test_daemon_composition.py',
 'tests/test_daemon_tasks.py',
 'tests/test_kill_worker_stop.py',
 'tests/test_kill_failure_suppression.py',
 'tests/test_heartbeat.py',
 'tests/test_storm.py',
 'tests/test_checkpoint.py',
 'tests/test_restart_timers.py',
 'tests/test_stages.py',
 'tests/test_daemon_admission.py',
 'tests/test_daemon_config.py',
 'tests/test_control.py',
 'tests/test_control_cli.py',
 'tests/test_kill_cli_activation.py',
 'tests/test_scheduler.py',
 'tests/test_mergequeue.py',
 'tests/test_triage.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_audit.py')

PRESERVATION = ('tests/test_control.py',
 'tests/test_control_cli.py',
 'tests/test_kill_cli_activation.py',
 'tests/test_scheduler.py',
 'tests/test_mergequeue.py',
 'tests/test_triage.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_audit.py')


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[p] for p in a['plan'])
            + sum(FILE_CHARS[p] for p in dict.fromkeys((*a['context'], *STANDING_CONTEXT, *extra))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('serve-activation',)
    assert BATCH == ('serve-activation', 'phase3-continue-21')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)
    assert (ADMISSION_INDEX, NEXT_ADMISSION_INDEX, NEXT_SEEDER_INDEX) == (20, 21, 22)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # Rejection can stamp later lifecycle history without changing confirmed birth.
    t = validate_ticket(stem, _text(stem).replace('state: rejected', 'state: confirmed', 1), ROOT, BATCH)
    fm = t.frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == STARTS[stem]
    assert STARTS == {'serve-activation': ('high', 'high'), 'phase3-continue-21': ('medium', 'medium')}


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == ((60, 180) if stem in PAYLOADS else (60, 90))
    assert 0 < t.expected_minutes <= t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'serve-activation': ('phase3-continue-20',),
                     'phase3-continue-21': ('serve-activation',)}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert t.scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert set(FENCE_ADDITIONS['serve-activation']) == {
        'tests/test_restart_timers.py', 'tests/test_checkpoint.py'}
    assert FENCE_ADDITIONS['phase3-continue-21'] == {}
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert len(CLOSURE_SNAPSHOT['patterns']) == 5
    scope = _ticket('serve-activation').sections['Scope in / Scope out']
    for path, reason in FENCE_ADDITIONS[stem].items():
        assert path in scope and '19.L rules 2-3' in scope
        assert 'Context' in reason and path in t.context
        assert reason.split(': ')[1].split(' ')[0] in scope
    for path, name in CLOSURE_SNAPSHOT['predecessor_tests'].items():
        assert path in FENCE_FLOORS['serve-activation']
        assert name in _ticket('serve-activation').sections['Acceptance criteria']
    assert not any(p.startswith('tests/test_seeded') for p in _ticket('serve-activation').scope_fence)
    assert CLOSURE_SNAPSHOT['direct_core_callers'] == (
        'tests/test_daemon_composition.py', 'tests/test_storm_notification_activation.py')
    assert 'Preserve public signatures' in CLOSURE_SNAPSHOT['disposition']
    assert 'Keep existing composition callers valid' in scope
    assert 'changed public signatures' in scope


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket('serve-activation')
    own = '19.P3.serve-activation'
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', own, '18', '20')
    assert VALIDATED_ROW_CITATIONS[t.stem] == ('18', '20')
    assert CONTRACT_CUSTODY == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert len(ENTRY_TESTS[t.stem]) == 14
    assert NAMED_OBLIGATIONS == {name: own for name in ENTRY_TESTS[t.stem]}
    assert set(ENTRY_TESTS[t.stem]) == {
        'test_serve_cli_uses_production_composition', 'test_serve_holds_lock_through_cleanup',
        'test_serve_startup_precedes_all_work', 'test_serve_waits_at_quiescence_and_discovers_work',
        'test_serve_consumers_use_existing_writers', 'test_serve_control_precedes_offer_accounting',
        'test_serve_kill_unwinds_executor_before_workers', 'test_serve_worker_failure_and_kill_suppression',
        'test_serve_signal_stop_and_restart_recovery', 'test_serve_recurring_maintenance_uses_injected_time',
        'test_serve_heartbeat_requires_responsive_components', 'test_serve_storm_hold_and_resume',
        'test_production_serve_graph_is_reachable', 'test_storm_ledger_is_reachable'}
    assert all(name in t.sections['Acceptance criteria'] for name in NAMED_OBLIGATIONS)
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract', 'every named invariant',
                 'record custody and sole writer', 'never copy unit text',
                 'chupa/serve.py is owned by its cited Owner', 'high/high',
                 'real CLI/async serve entrypoint', 'merged production-composition harness',
                 'Journal(state_dir, clock) and append/read/close signatures',
                 'sole durable event writer', 'sole queue-record writer', 'sole control-decision writer',
                 'bootstrap on-entry reconciliation', 'inline admission',
                 'ordinary DaemonTasks exception propagation and cleanup',
                 'injected seams', 'scripted callbacks', 'disposable synthetic repositories',
                 'asyncio barriers', 'serve-merge-admission owns later routing activation'):
        assert fact.lower() in scope.lower(), fact
    for stem in BATCH:
        for part in CONTRACT_CUSTODY:
            assert f'- **{part}:**' not in _text(stem)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-21')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.serve-merge-admission', '9',
        '19.P3.worker-recovery-disposition', '6', '15')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_21.py')
    assert AUTHORING_HEAD == 'afaa204641007d7faf40bf6c37d991cfd02187ca'
    assert MERGED_IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    assert VALIDATED_ENTRIES == ('19.P3.serve-activation', '19.P3.serve-merge-admission',
                                 '19.P3.worker-recovery-disposition')
    assert VALIDATED_ROW_CITATIONS == {'serve-activation': ('18', '20'),
        'serve-merge-admission': ('9',), 'worker-recovery-disposition': ('6', '15')}
    assert len(ENTRY_TESTS['serve-merge-admission']) == 9
    assert len(ENTRY_TESTS['worker-recovery-disposition']) == 6
    scope = t.sections['Scope in / Scope out']
    for fact in ('admissions[21:]', 'entry_unit_gap', 'resolve_plan_contract',
                 'Author only serve-merge-admission and phase3-continue-22',
                 'serve-merge-admission depends on phase3-continue-21', 'starts high/high',
                 'cites exactly 19.I, 19.P3.serve-merge-admission and section 9',
                 'depending on serve-merge-admission', 'admissions[22:]', 'admissions[23:]',
                 'worker-recovery-disposition at high/high', 'tests/test_seeded_phase3_22.py',
                 '19.P3.worker-recovery-disposition', 'section 6', 'section 15', 'next-seeder lookahead',
                 'never copy unit text', 'every named invariant obligation', 'record custody',
                 'closure greps', '300,000-character headroom', 'Context by default', 'On-demand',
                 'Prompt-specs and delimiter-bearing sources', 'fixed authoring snapshots',
                 'never live sizes or live plan lengths', 'merged idiom blob',
                 'seeding.max_seeds_per_admission', 'terminal phase3-exit', 'no successor',
                 'never seed past the next phase', 'keep previously approved seeds verbatim',
                 're-author only snagged seeds', 'requisition_review', 'checks.json',
                 'chupa(phase3-continue-21): seeds ticket-plane commit'):
        assert fact.lower() in scope.lower(), fact
    for path in (*CLOSURE_SNAPSHOT['next_admission_additions'], *CLOSURE_SNAPSHOT['next_seeder_additions']):
        assert path in scope
    assert 'test_restart_reuses_orphan_reconciliation' in scope
    assert 'tests/test_seeded_phase3_20.py' not in t.context


@pytest.mark.parametrize('stem', BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(t.scope_fence) == set(a['fenced_existing']) | set(a['created'])
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert not set(a['context']) & set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert set(a['context']) <= set(DELIMITER_FREE_AT_AUTHORING)
    assert all(not p.startswith('specs/') and p != 'CHUPA_PLAN.md' for p in a['context'])
    assert a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS == 300_000
    assert a['chars'] > 0 and all(PLAN_CHARS[p] > 0 for p in a['plan'])
    assert all(FILE_CHARS[p] > 0 for p in (*a['context'], *a['on_demand'], *STANDING_CONTEXT))
    for path in a['on_demand']:
        assert path in a['fenced_existing'] and render_chars(a, (path,)) > HEADROOM_CHARS
    assert AUTHORED['serve-activation']['on_demand'] == ('tests/test_daemon_composition.py', 'chupa/driver.py', 'chupa/stages.py', 'chupa/storm.py', 'tests/test_stages.py', 'tests/test_daemon_admission.py', 'tests/test_daemon_config.py')
    assert AUTHORED['serve-activation']['created'] == ('chupa/serve.py', 'tests/test_serve.py')
    assert 'chupa/checkpoint.py' in AUTHORED['serve-activation']['context']
    assert 'tests/test_checkpoint.py' in AUTHORED['serve-activation']['fenced_existing']
    assert AUTHORED['phase3-continue-21']['created'] == ('tickets', 'tests/test_seeded_phase3_21.py')


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket('serve-activation')
    assert t.verification == (ENTRY_VERIFICATION,)
    assert ENTRY_VERIFICATION[:3] == ('uv', 'run', 'pytest')
    assert ENTRY_VERIFICATION[3:] == (
        'tests/test_serve.py', 'tests/test_daemon_composition.py', 'tests/test_daemon_tasks.py',
        'tests/test_kill_worker_stop.py', 'tests/test_kill_failure_suppression.py',
        'tests/test_heartbeat.py', 'tests/test_storm.py', 'tests/test_checkpoint.py',
        'tests/test_restart_timers.py', 'tests/test_stages.py', 'tests/test_daemon_admission.py', 'tests/test_daemon_config.py',
        'tests/test_control.py', 'tests/test_control_cli.py',
        'tests/test_kill_cli_activation.py', 'tests/test_scheduler.py', 'tests/test_mergequeue.py',
        'tests/test_triage.py', 'tests/test_cli.py', 'tests/test_drain.py', 'tests/test_audit.py')
    assert PRESERVATION == ENTRY_VERIFICATION[15:]
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites' in t.sections['Scope in / Scope out']
    assert _ticket('phase3-continue-21').verification == (
        ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_21.py'), ('uv', 'run', 'pytest', '-q'))
