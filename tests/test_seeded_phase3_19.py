"""Admission 19: fixed authoring snapshots, never refreshed from live sizes.

Parsed admissions[19:] from the live plan before writing; entry_unit_gap and
resolve_plan_contract validated checkpoint, serve and daemon-admission lookahead.
Entry bodies and registry suffixes are not copied into these historical fixtures.
"""

from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
AUTHORING_HEAD = '7a5c037710f2ce3416ecc0d12e0a52b0b9663ad5'
MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'
MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
PAYLOADS = ('checkpoint-push',)
BATCH = (*PAYLOADS, 'phase3-continue-20')
ADMISSION_INDEX, NEXT_ADMISSION_INDEX, NEXT_SEEDER_INDEX = 19, 20, 21
EDGES = {'checkpoint-push': ('phase3-continue-19',),
         'phase3-continue-20': ('checkpoint-push',)}
STARTS = {s: ('medium', 'medium') for s in BATCH}
FENCE_FLOORS = {
    'checkpoint-push': ('chupa/checkpoint.py', 'chupa/daemon.py', 'chupa/git.py',
                        'tests/test_checkpoint.py', 'tests/test_git.py', 'tests/test_mergequeue.py'),
    'phase3-continue-20': ('tickets', 'tests/test_seeded_phase3_20.py'),
}
FENCE_ADDITIONS = {s: {} for s in BATCH}
HEADROOM_CHARS = 300_000
RENDER_OVERHEAD = 2_000
CONTRACT_CUSTODY = {part: '19.P3.checkpoint-push'
                    for part in ('Owner', 'Records', 'Observable', 'Tests')}
ENTRY_VERIFICATION = (
    'uv', 'run', 'pytest', 'tests/test_checkpoint.py', 'tests/test_git.py',
    'tests/test_mergequeue.py', 'tests/test_effects.py', 'tests/test_restart_timers.py',
    'tests/test_box.py', 'tests/test_daemon_composition.py',
)
PRESERVATION = ('tests/test_effects.py', 'tests/test_restart_timers.py',
                'tests/test_box.py', 'tests/test_daemon_composition.py')
CLOSURE_SNAPSHOT = {
    'roots': ('chupa/', 'eval/', 'tests/'),
    'patterns': (r'checkpoint|push\(',
                 'build_daemon_core|daemon_core|DaemonTasks|WorkerStop|WorkerFailureObserver',
                 'serve.*not|not.*serve|not hasattr',
                 'public.*(surface|operation)|option_shaped_or_empty_refs',
                 r'Journal\(|Effects\(|Timers\(|storm_producer|arrival_id'),
    'public_operation_tests': ('tests/test_git.py::test_op_argv',
                              'tests/test_git.py::test_option_shaped_or_empty_refs_are_refused_before_exec'),
    'production_roots': ('chupa/__main__.py:main -> runner.run_ticket, drain.drain',
                         'chupa/__main__.py:build_daemon_core -> daemon_core, build_control, Restart, Timers',
                         'chupa/runner.py:bind -> TicketWriter, compose_pipeline, Effects',
                         'eval/shakeout/bench.py:Bench -> Checkout, Journal'),
    'direct_core_caller_paths': ('chupa/__main__.py', 'tests/test_daemon_composition.py',
                                 'tests/test_storm_notification_activation.py', 'tests/test_heartbeat.py'),
    'disposition': 'No changed public signature or production wiring. Git.push adds a public '
                   'operation whose enumeration is already in the floor and Context. No added '
                   'path is earned. Preserve Journal callers and bootstrap behavior.',
    'next_activation_additions': {
        'tests/test_restart_timers.py': '19.L rules 2-3: test_restart_construction_is_idle '
                                        'pins serve absence; re-grep, then Context by default',
        'tests/test_checkpoint.py': '19.L rules 2-3: test_checkpoint_boundary_is_dormant '
                                    'pins production invocation absence; created this admission; '
                                    'Context only after checkpoint-push merges',
    },
}

IMPLEMENT_SPEC_CHARS = 4316

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.checkpoint-push': 10953,
 '10': 6636,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.serve-activation': 13073,
 '18': 13338,
 '20': 4367,
 '19.P3.serve-merge-admission': 10740,
 '9': 19656}

FILE_CHARS = {'chupa/daemon.py': 22683,
 'chupa/git.py': 6503,
 'tests/test_git.py': 16028,
 'tests/test_mergequeue.py': 52056,
 'chupa/journal.py': 8953,
 'chupa/effects.py': 3229,
 'chupa/timers.py': 4966,
 'chupa/box.py': 10000,
 'chupa/storm.py': 9574,
 'chupa/config.py': 11898,
 'chupa/seams.py': 5551,
 'chupa/__main__.py': 10026,
 'tests/test_seeded_phase3_core.py': 5425}

STANDING_CONTEXT = ()

AUTHORED = {'checkpoint-push': {'chars': 4676,
                     'plan': ('19.I', '19.P3.checkpoint-push', '10'),
                     'context': ('chupa/daemon.py',
                                 'chupa/git.py',
                                 'tests/test_git.py',
                                 'tests/test_mergequeue.py',
                                 'chupa/journal.py',
                                 'chupa/effects.py',
                                 'chupa/timers.py',
                                 'chupa/box.py',
                                 'chupa/storm.py',
                                 'chupa/config.py',
                                 'chupa/seams.py',
                                 'chupa/__main__.py'),
                     'on_demand': (),
                     'fenced_existing': ('chupa/daemon.py',
                                         'chupa/git.py',
                                         'tests/test_git.py',
                                         'tests/test_mergequeue.py'),
                     'created': ('chupa/checkpoint.py', 'tests/test_checkpoint.py'),
                     'measured_render': 190073},
 'phase3-continue-20': {'chars': 10055,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.serve-activation',
                                 '18',
                                 '20',
                                 '19.P3.serve-merge-admission',
                                 '9'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_20.py'),
                        'measured_render': 137252}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/daemon.py',
 'chupa/git.py',
 'tests/test_git.py',
 'tests/test_mergequeue.py',
 'chupa/journal.py',
 'chupa/effects.py',
 'chupa/timers.py',
 'chupa/box.py',
 'chupa/storm.py',
 'chupa/config.py',
 'chupa/seams.py',
 'chupa/__main__.py',
 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.checkpoint-push', '19.P3.serve-activation', '19.P3.serve-merge-admission')

VALIDATED_ROW_CITATIONS = {'checkpoint-push': ('10',), 'serve-activation': ('18', '20'), 'serve-merge-admission': ('9',)}

ENTRY_TESTS = {'checkpoint-push': ('test_checkpoint_merge_and_daily_triggers',
                     'test_checkpoint_success_advances_once',
                     'test_checkpoint_failed_push_refires',
                     'test_checkpoint_failure_occurrence_identity',
                     'test_checkpoint_failure_report_crash_replay',
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
                      'test_production_serve_graph_is_reachable'),
 'serve-merge-admission': ('test_daemon_prechecks_precede_offer',
                           'test_bootstrap_pipeline_keeps_inline_admission',
                           'test_admission_mode_is_explicit',
                           'test_serve_routes_settled_run_to_composed_queue_once',
                           'test_serve_admission_rebases_regates_and_retires',
                           'test_serve_admission_refusal_keeps_main_green',
                           'test_serve_conflict_handoff_runs_after_admission_unwinds',
                           'test_serve_admission_holds_and_cleanup')}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[p] for p in a['plan'])
            + sum(FILE_CHARS[p] for p in dict.fromkeys((*a['context'], *STANDING_CONTEXT, *extra))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('checkpoint-push',)
    assert BATCH == ('checkpoint-push', 'phase3-continue-20')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)
    assert (ADMISSION_INDEX, NEXT_ADMISSION_INDEX, NEXT_SEEDER_INDEX) == (19, 20, 21)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # A later rejection is lifecycle history, not a different birth path.
    t = validate_ticket(stem, _text(stem).replace('state: rejected', 'state: confirmed', 1), ROOT, BATCH)
    fm = t.frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == STARTS[stem] == ('medium', 'medium')


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == ((60, 120) if stem in PAYLOADS else (60, 90))
    assert 0 < t.expected_minutes <= t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'checkpoint-push': ('phase3-continue-19',),
                     'phase3-continue-20': ('checkpoint-push',)}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS == {s: {} for s in BATCH}
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    scope = _ticket('checkpoint-push').sections['Scope in / Scope out']
    for assertion in CLOSURE_SNAPSHOT['public_operation_tests']:
        path, name = assertion.split('::')
        assert path in FENCE_FLOORS['checkpoint-push'] and name in scope
        assert path in AUTHORED['checkpoint-push']['context']
    assert 'No changed public signature' in CLOSURE_SNAPSHOT['disposition']
    assert len(CLOSURE_SNAPSHOT['production_roots']) == 4
    for path, reason in FENCE_ADDITIONS[stem].items():
        assert path in t.sections['Scope in / Scope out']
        assert '19.L' in reason and ('Context' in reason or 'On-demand' in reason)


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket('checkpoint-push')
    own = '19.P3.checkpoint-push'
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', own, '10')
    assert VALIDATED_ROW_CITATIONS[t.stem] == ('10',)
    assert CONTRACT_CUSTODY == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert ENTRY_TESTS[t.stem] == (
        'test_checkpoint_merge_and_daily_triggers', 'test_checkpoint_success_advances_once',
        'test_checkpoint_failed_push_refires', 'test_checkpoint_failure_occurrence_identity',
        'test_checkpoint_failure_report_crash_replay', 'test_checkpoint_crash_windows',
        'test_checkpoint_timer_survives_restart_and_roll', 'test_checkpoint_boundary_is_dormant',
        'test_op_argv', 'test_option_shaped_or_empty_refs_are_refused_before_exec')
    assert all(name in t.sections['Acceptance criteria'] for name in ENTRY_TESTS[t.stem])
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract', 'every named Tests obligation',
                 'record custody and sole writer', 'never copy unit text',
                 'chupa/checkpoint.py is owned by its cited Owner',
                 'Production invocation stays dormant until serve-activation',
                 'real CLI run/drain', 'build_daemon_core', 'merged production-composition harness',
                 'Journal(state_dir, clock) and append/read/close signatures',
                 'sole durable event writer', 'sole queue-record writer', 'sole control-decision writer',
                 'bootstrap on-entry reconciliation', 'inline admission',
                 'ordinary DaemonTasks exception propagation and cleanup',
                 'failure occurrence identity and crash replay', 'production storm_producer Box',
                 'existing arrival_id', 'injected seams', 'scripted callbacks',
                 'disposable repositories', 'asyncio barriers', 'historical seeding tests'):
        assert fact.lower() in scope.lower(), fact
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(t.stem)
    assert 'effect_completion' not in _text(t.stem)
    assert 'checkpoint-push-failed/' not in _text(t.stem)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-20')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.serve-activation', '18', '20',
        '19.P3.serve-merge-admission', '9')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_20.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == ('19.P3.checkpoint-push', '19.P3.serve-activation', '19.P3.serve-merge-admission')
    assert VALIDATED_ROW_CITATIONS == {'checkpoint-push': ('10',),
                                      'serve-activation': ('18', '20'), 'serve-merge-admission': ('9',)}
    assert len(ENTRY_TESTS['serve-activation']) == 13
    assert 'test_serve_admission_holds_and_cleanup' in ENTRY_TESTS['serve-merge-admission']
    scope = t.sections['Scope in / Scope out']
    for fact in ('admissions[20:]', 'entry_unit_gap', 'resolve_plan_contract',
                 'Author only serve-activation and phase3-continue-21',
                 'serve-activation depends on phase3-continue-20', 'starts high/high',
                 'cites exactly 19.I, 19.P3.serve-activation, section 18 and section 20',
                 'depending on serve-activation', 'admissions[21:]', 'admissions[22:]',
                 'serve-merge-admission at high/high', 'tests/test_seeded_phase3_21.py',
                 '19.P3.serve-merge-admission', 'section 9', 'next-seeder lookahead',
                 'never copy unit text', 'every named invariant obligation', 'record custody',
                 '300,000-character headroom', 'Context by default', 'On-demand',
                 'Prompt-specs and delimiter-bearing sources', 'fixed authoring snapshots',
                 'never live sizes or live plan lengths', 'merged idiom blob',
                 'seeding.max_seeds_per_admission', 'terminal phase3-exit', 'no successor',
                 'never seed past the next phase', 'keep previously approved seeds verbatim',
                 're-author only snagged seeds', 'requisition_review', 'checks.json',
                 'chupa(phase3-continue-20): seeds ticket-plane commit'):
        assert fact.lower() in scope.lower(), fact
    for path, reason in CLOSURE_SNAPSHOT['next_activation_additions'].items():
        assert path in scope and reason.split(': ')[1].split(' ')[0] in scope
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(t.stem)


@pytest.mark.parametrize('stem', BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert set(t.scope_fence) == set(a['fenced_existing']) | set(a['created'])
    assert not set(a['context']) & set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert set(a['context']) <= set(DELIMITER_FREE_AT_AUTHORING)
    assert all(not p.startswith('specs/') and p != 'CHUPA_PLAN.md' for p in a['context'])
    assert a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS == 300_000
    assert a['chars'] > 0 and all(PLAN_CHARS[p] > 0 for p in a['plan'])
    assert all(FILE_CHARS[p] > 0 for p in (*a['context'], *a['on_demand'], *STANDING_CONTEXT))
    for path in a['on_demand']:
        assert path in a['fenced_existing'] and render_chars(a, (path,)) > HEADROOM_CHARS
    assert AUTHORED['checkpoint-push']['created'] == ('chupa/checkpoint.py', 'tests/test_checkpoint.py')
    assert AUTHORED['phase3-continue-20']['created'] == ('tickets', 'tests/test_seeded_phase3_20.py')


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket('checkpoint-push')
    assert t.verification == (ENTRY_VERIFICATION,)
    assert set(PRESERVATION) <= set(ENTRY_VERIFICATION)
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'tests/test_mergequeue.py stays unchanged' in t.sections['Scope in / Scope out']
    assert _ticket('phase3-continue-20').verification == (
        ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_20.py'), ('uv', 'run', 'pytest', '-q'))
