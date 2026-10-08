"""Admission 21: immutable authoring measurements, not a live registry projection.

Both required entry units passed entry_unit_gap and resolve_plan_contract at AUTHORING_HEAD.
Citations carry unit bodies; birth hashes pin the seeds checked for copy refusal.
"""

import hashlib
from pathlib import Path

import pytest
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = 'fa5c32ad8ce33dced058c65a8a99d855e252de5c'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('serve-merge-admission',)

BATCH = ('serve-merge-admission', 'phase3-continue-22')

ADMISSION_INDEX = 21

NEXT_ADMISSION_INDEX = 22

NEXT_SEEDER_INDEX = 23

EDGES = {'serve-merge-admission': ('phase3-continue-21',), 'phase3-continue-22': ('serve-merge-admission',)}

STARTS = {'serve-merge-admission': ('high', 'high'), 'phase3-continue-22': ('medium', 'medium')}

FENCE_FLOORS = {'serve-merge-admission': ('chupa/merge.py',
                           'chupa/serve.py',
                           'tests/test_merge.py',
                           'tests/test_mergequeue.py',
                           'tests/test_serve.py'),
 'phase3-continue-22': ('tickets', 'tests/test_seeded_phase3_22.py')}

FENCE_ADDITIONS = {'serve-merge-admission': {'chupa/runner.py': '19.L rule 5 caller/seam-owner closure: drive '
                                              'settlement calls admission; Context; earned by '
                                              '19.P3.serve-merge-admission',
                           'chupa/daemon.py': '19.L rule 5 caller/seam-owner closure: TicketWriter '
                                              'consumes handoffs after admission; Context; earned '
                                              'by 19.P3.serve-merge-admission'},
 'phase3-continue-22': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4775

RENDER_OVERHEAD = 2000

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.serve-merge-admission': 10740,
 '9': 20021,
 '19.L': 20908,
 '19.P3': 16240,
 '13': 19708,
 '19.P3.worker-recovery-disposition': 6582,
 '6': 38005,
 '15': 17104}

FILE_CHARS = {'chupa/merge.py': 13596,
 'chupa/serve.py': 20273,
 'tests/test_merge.py': 15398,
 'tests/test_mergequeue.py': 52056,
 'tests/test_serve.py': 34737,
 'chupa/runner.py': 35225,
 'chupa/daemon.py': 24513,
 'chupa/mergequeue.py': 16256,
 'tests/test_seeded_phase3_core.py': 5425}

STANDING_CONTEXT = ()

AUTHORED = {'serve-merge-admission': {'chars': 7824,
                           'plan': ('19.I', '19.P3.serve-merge-admission', '9'),
                           'context': ('chupa/merge.py',
                                       'chupa/serve.py',
                                       'tests/test_merge.py',
                                       'tests/test_mergequeue.py',
                                       'tests/test_serve.py',
                                       'chupa/runner.py',
                                       'chupa/daemon.py',
                                       'chupa/mergequeue.py'),
                           'on_demand': (),
                           'fenced_existing': ('chupa/merge.py',
                                               'chupa/serve.py',
                                               'tests/test_merge.py',
                                               'tests/test_mergequeue.py',
                                               'tests/test_serve.py',
                                               'chupa/runner.py',
                                               'chupa/daemon.py'),
                           'created': (),
                           'measured_render': 257193,
                           'birth_sha256': '4902dcc1aaee2231fe47f1a1436e45befb09b77cb1a671b70777e4e996a763c9'},
 'phase3-continue-22': {'chars': 9393,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.worker-recovery-disposition',
                                 '6',
                                 '15'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_22.py'),
                        'measured_render': 139933,
                        'birth_sha256': '557dd13b821527b4fc75dae5b7b8b45fbd6b82ea4a90d631d8979b44b56c0ff6'}}

VALIDATED_ENTRIES = ('19.P3.serve-merge-admission', '19.P3.worker-recovery-disposition')

VALIDATED_ROW_CITATIONS = {'serve-merge-admission': ('9',), 'worker-recovery-disposition': ('6', '15')}

ENTRY_TESTS = {'19.P3.serve-merge-admission': ('test_daemon_prechecks_precede_offer',
                                 'test_bootstrap_pipeline_keeps_inline_admission',
                                 'test_inline_admission_does_not_use_merge_queue',
                                 'test_admission_mode_is_explicit',
                                 'test_serve_routes_settled_run_to_composed_queue_once',
                                 'test_serve_admission_rebases_regates_and_retires',
                                 'test_serve_admission_refusal_keeps_main_green',
                                 'test_serve_conflict_handoff_runs_after_admission_unwinds',
                                 'test_serve_admission_holds_and_cleanup'),
 '19.P3.worker-recovery-disposition': ('test_recovery_alert_records_producing_run',
                                       'test_recovery_alert_precedes_worktree_removal',
                                       'test_recovery_alert_is_once_per_reaped_run',
                                       'test_recovery_alert_failures_preserve_terminal_history',
                                       'test_recovery_alert_does_not_change_disposition',
                                       'test_every_engine_signal_name_is_listed',
                                       'test_listed_signal_names_are_accepted',
                                       'test_unknown_signal_name_is_refused_at_append',
                                       'test_restart_reuses_orphan_reconciliation')}

CONTRACT_CUSTODY = {'Owner': '19.P3.serve-merge-admission',
 'Records': '19.P3.serve-merge-admission',
 'Observable': '19.P3.serve-merge-admission',
 'Tests': '19.P3.serve-merge-admission'}

RECORD_CUSTODY = {'Candidate': '19.P3.serve-merge-admission',
 'SeedOnMain': '19.P3.serve-merge-admission',
 'Invoice.seeds': '19.P3.serve-merge-admission',
 'StageResult': '19.P3.serve-merge-admission',
 'Admission': '19.P3.serve-merge-admission',
 'ConflictHandoff': '19.P3.serve-merge-admission',
 'MERGE_SPEC_VERSION': '19.P3.serve-merge-admission',
 'CONFLICT_FACTS': '19.P3.serve-merge-admission',
 'RED_STREAK': '19.P3.serve-merge-admission',
 'TREE_MISMATCH': '19.P3.serve-merge-admission',
 'RED_STREAK_LIMIT': '19.P3.serve-merge-admission',
 'write_squash': '19.P3.serve-merge-admission',
 'squash_message': '19.P3.serve-merge-admission',
 'runner failure terminals': '19.P3.serve-merge-admission',
 'Journal': '19.P3.serve-merge-admission',
 'Box': '19.P3.serve-merge-admission',
 'ControlInbox': '19.P3.serve-merge-admission'}

LOOKAHEAD_ADDITIONS = {'chupa/journal.py': '19.L seam-owner closure explicitly earned by '
                     '19.P3.worker-recovery-disposition: SIGNAL_NAMES registration; existing '
                     'Context by default',
 'tests/test_restart_timers.py': '19.L rule 2 explicitly earned by '
                                 '19.P3.worker-recovery-disposition: '
                                 'test_restart_reuses_orphan_reconciliation last-record-at-removal '
                                 'assertion; existing Context by default'}

ENTRY_VERIFICATION = ('uv',
 'run',
 'pytest',
 'tests/test_merge.py',
 'tests/test_mergequeue.py',
 'tests/test_serve.py',
 'tests/test_daemon_composition.py',
 'tests/test_rework.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_control.py',
 'tests/test_audit.py')

RECOVERY_VERIFICATION = ('uv',
 'run',
 'pytest',
 'tests/test_reconcile.py',
 'tests/test_restart_timers.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_journal.py',
 'tests/test_vocabularies.py',
 'tests/test_audit.py')

PRESERVATION = ('tests/test_daemon_composition.py',
 'tests/test_rework.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_control.py',
 'tests/test_audit.py')

DELIMITER_FREE_AT_AUTHORING = ('chupa/merge.py',
 'chupa/serve.py',
 'tests/test_merge.py',
 'tests/test_mergequeue.py',
 'tests/test_serve.py',
 'chupa/runner.py',
 'chupa/daemon.py',
 'chupa/mergequeue.py',
 'tests/test_seeded_phase3_core.py')

COPY_REFUSAL_CHECKED_AT_AUTHORING = ('serve-merge-admission', 'phase3-continue-22')

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'patterns': ('merge\\(|compose_pipeline|runner.bind|prepare_pipeline|TicketWriter|DaemonAdmission',
              'offer|process|pending|inline_admission|bootstrap_pipeline',
              'not hasattr|construction_is_idle|is_dormant|public.*(surface|operation)',
              'recovery_alert|SIGNAL_NAMES|run_seq|reconcile|abandoned|read\\(\\)\\[-1\\]'),
 'admission_callers': ('chupa/runner.py', 'tests/test_merge.py', 'tests/test_mergequeue.py'),
 'composition_callers': ('chupa/runner.py',
                         'tests/test_merge.py',
                         'tests/test_daemon_composition.py'),
 'preserved_bind_roots': ('chupa/__main__.py',
                          'eval/shakeout/bench.py',
                          'tests/test_daemon_composition.py'),
 'predecessor_preservation': ('test_bootstrap_pipeline_keeps_inline_admission',
                              'test_inline_admission_does_not_use_merge_queue',
                              'test_bootstrap_inline_admission_never_holds',
                              'test_merge_queue_composition_has_no_side_effects',
                              'test_serve_consumers_use_existing_writers'),
 'recovery_old_assertion': ('tests/test_restart_timers.py:147',
                            'test_restart_reuses_orphan_reconciliation',
                            'abandoned is last record at removal'),
 'disposition': 'No signature change required for bootstrap callers; explicit serve selection '
                'earns only runner/daemon owners. Ready-fixture direct queue exercises remain '
                'predecessor preservation, never activation evidence.'}

def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _birth(stem):
    # Reject stamps are lifecycle history, not a change to confirmed seed birth.
    return _text(stem).replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[p] for p in a['plan'])
            + sum(FILE_CHARS[p] for p in dict.fromkeys((*a['context'], *STANDING_CONTEXT))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('serve-merge-admission',)
    assert BATCH == ('serve-merge-admission', 'phase3-continue-22')
    assert (ADMISSION_INDEX, NEXT_ADMISSION_INDEX, NEXT_SEEDER_INDEX) == (21, 22, 23)
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    t = validate_ticket(stem, _birth(stem), ROOT, BATCH)
    fm = t.frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == STARTS[stem]
    assert STARTS == {'serve-merge-admission': ('high', 'high'), 'phase3-continue-22': ('medium', 'medium')}
    assert hashlib.sha256(_birth(stem).encode()).hexdigest() == AUTHORED[stem]['birth_sha256']
    assert stem in COPY_REFUSAL_CHECKED_AT_AUTHORING


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'serve-merge-admission': ('phase3-continue-21',),
                     'phase3-continue-22': ('serve-merge-admission',)}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert t.scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert FENCE_FLOORS['serve-merge-admission'] == (
        'chupa/merge.py', 'chupa/serve.py', 'tests/test_merge.py',
        'tests/test_mergequeue.py', 'tests/test_serve.py')
    assert set(FENCE_ADDITIONS['serve-merge-admission']) == {'chupa/runner.py', 'chupa/daemon.py'}
    assert FENCE_ADDITIONS['phase3-continue-22'] == {}
    for path, reason in FENCE_ADDITIONS[stem].items():
        assert path in t.context and path in t.sections['Scope in / Scope out']
        assert '19.L rule 5' in reason and 'Context' in reason
        assert '19.P3.serve-merge-admission' in reason
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert CLOSURE_SNAPSHOT['admission_callers'] == (
        'chupa/runner.py', 'tests/test_merge.py', 'tests/test_mergequeue.py')
    assert len(CLOSURE_SNAPSHOT['patterns']) == 4
    assert not any(p.startswith('tests/test_seeded') for p in _ticket(PAYLOADS[0]).scope_fence)


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket(PAYLOADS[0])
    own = '19.P3.serve-merge-admission'
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', own, '9')
    assert VALIDATED_ROW_CITATIONS[t.stem] == ('9',)
    assert CONTRACT_CUSTODY == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert set(RECORD_CUSTODY.values()) == {own}
    assert set(ENTRY_TESTS[own]) == {
        'test_daemon_prechecks_precede_offer', 'test_bootstrap_pipeline_keeps_inline_admission',
        'test_inline_admission_does_not_use_merge_queue', 'test_admission_mode_is_explicit',
        'test_serve_routes_settled_run_to_composed_queue_once',
        'test_serve_admission_rebases_regates_and_retires',
        'test_serve_admission_refusal_keeps_main_green',
        'test_serve_conflict_handoff_runs_after_admission_unwinds',
        'test_serve_admission_holds_and_cleanup'}
    assert all(name in t.sections['Acceptance criteria'] for name in ENTRY_TESTS[own])
    scope = t.sections['Scope in / Scope out']
    for fact in ('complete governing contract', 'record custody and sole writer', 'never copy unit text',
                 'bootstrap dispatch result', 'inline admission signature',
                 'Journal(state_dir, clock) and append/read/close signatures',
                 'bootstrap on-entry reconciliation', 'ordinary DaemonTasks exception propagation and cleanup',
                 'real CLI/async serve entrypoint', 'merged production-composition harness',
                 'scripted callbacks', 'injected seams', 'disposable synthetic repositories', 'asyncio barriers',
                 'sole durable event writer', 'sole queue-record writer', 'sole control-decision writer'):
        assert fact in scope
    for stem in BATCH:
        assert all(f'- **{part}:**' not in _text(stem) for part in CONTRACT_CUSTODY)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-22')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.worker-recovery-disposition', '6', '15')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_22.py')
    assert AUTHORING_HEAD == 'fa5c32ad8ce33dced058c65a8a99d855e252de5c'
    assert MERGED_IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    assert VALIDATED_ENTRIES == ('19.P3.serve-merge-admission', '19.P3.worker-recovery-disposition')
    recovery = '19.P3.worker-recovery-disposition'
    assert set(ENTRY_TESTS[recovery]) == {
        'test_recovery_alert_records_producing_run', 'test_recovery_alert_precedes_worktree_removal',
        'test_recovery_alert_is_once_per_reaped_run', 'test_recovery_alert_failures_preserve_terminal_history',
        'test_recovery_alert_does_not_change_disposition', 'test_restart_reuses_orphan_reconciliation',
        'test_every_engine_signal_name_is_listed', 'test_listed_signal_names_are_accepted',
        'test_unknown_signal_name_is_refused_at_append'}
    scope = t.sections['Scope in / Scope out']
    for fact in ('admissions[22:]', 'admissions[23:]', 'Author only worker-recovery-disposition and phase3-continue-23',
                 'entry_unit_gap', 'resolve_plan_contract', 'next-seeder lookahead, outbox-only-admission',
                 'never copy unit text', 'record custody', 'tests/test_vocabularies.py',
                 'test_restart_reuses_orphan_reconciliation', 'Context by default', 'On-demand',
                 '300,000-character headroom', 'fixed authoring snapshots',
                 'never live sizes or live plan lengths', 'merged idiom blob',
                 'seeding.max_seeds_per_admission', 'terminal phase3-exit', 'no successor',
                 'never seed past the next phase', 'Keep previously approved seeds verbatim',
                 're-author only snagged seeds', 'requisition_review', 'checks.json',
                 'chupa(phase3-continue-22): seeds ticket-plane commit'):
        assert fact in scope, fact
    assert all(name in scope for name in ENTRY_TESTS[recovery])
    assert ' '.join(RECOVERY_VERIFICATION) in scope
    assert 'registry floor is chupa/reconcile.py and tests/test_reconcile.py' in scope
    assert set(LOOKAHEAD_ADDITIONS) == {'chupa/journal.py', 'tests/test_restart_timers.py'}
    for path, reason in LOOKAHEAD_ADDITIONS.items():
        assert path in scope and recovery in reason and 'Context' in reason
    assert not any(p in t.context for p in ('tests/test_seeded_phase3_21.py', 'tests/test_seeded_phase3_22.py'))
    assert RECOVERY_VERIFICATION == ('uv', 'run', 'pytest', 'tests/test_reconcile.py',
        'tests/test_restart_timers.py', 'tests/test_cli.py', 'tests/test_drain.py',
        'tests/test_journal.py', 'tests/test_vocabularies.py', 'tests/test_audit.py')


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
    assert all(FILE_CHARS[p] > 0 for p in (*a['context'], *STANDING_CONTEXT))
    assert not a['on_demand']  # Every fenced existing file fits embedded at this head.


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket(PAYLOADS[0])
    assert t.verification == (ENTRY_VERIFICATION,)
    assert ENTRY_VERIFICATION == ('uv', 'run', 'pytest', 'tests/test_merge.py',
        'tests/test_mergequeue.py', 'tests/test_serve.py', 'tests/test_daemon_composition.py',
        'tests/test_rework.py', 'tests/test_cli.py', 'tests/test_drain.py',
        'tests/test_control.py', 'tests/test_audit.py')
    assert PRESERVATION == ENTRY_VERIFICATION[6:]
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites' in t.sections['Scope in / Scope out']
    assert _ticket('phase3-continue-22').verification == (
        ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_22.py'), ('uv', 'run', 'pytest', '-q'))
