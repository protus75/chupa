"""Admission 22: fixed authoring snapshots and cited recovery obligations.

Only this admission and its immediate lookahead were needed for authoring.
Birth hashes also pin copy-refusal and delimiter checks performed at this head.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

PAYLOADS = ('worker-recovery-disposition',)
BATCH = (*PAYLOADS, 'phase3-continue-23')
MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'
HEADROOM_CHARS = 300_000
RENDER_OVERHEAD = 2_000
STANDING_CONTEXT = ()
EDGES = {'worker-recovery-disposition': ('phase3-continue-22',),
         'phase3-continue-23': PAYLOADS}
STARTS = {'worker-recovery-disposition': ('high', 'high'),
          'phase3-continue-23': ('medium', 'medium')}
FENCE_FLOORS = {'worker-recovery-disposition': ('chupa/reconcile.py', 'tests/test_reconcile.py'),
                'phase3-continue-23': ('tickets', 'tests/test_seeded_phase3_23.py')}
FENCE_ADDITIONS = {
    'worker-recovery-disposition': {
        'chupa/journal.py': '19.L seam-owner closure: SIGNAL_NAMES registration; Context',
        'tests/test_restart_timers.py': '19.L rule 2: test_restart_reuses_orphan_reconciliation '
                                      'last-record-at-removal assertion; Context',
        'tests/test_kill_failure_suppression.py': '19.L rule 2: '
            'test_kill_suppression_preserves_run_and_abort_failures last-record assertion; Context',
    },
    'phase3-continue-23': {},
}
OWN = '19.P3.worker-recovery-disposition'
VALIDATED_ENTRIES = (OWN, '19.P3.outbox-only-admission')
VALIDATED_ROW_CITATIONS = {OWN: ('6', '15'), '19.P3.outbox-only-admission': ('19.L', '10')}
CONTRACT_CUSTODY = {part: OWN for part in ('Owner', 'Records', 'Observable', 'Tests')}
RECORD_CUSTODY = {
    'RECOVERY_ALERT and recovery/abandonment emission': ('reconcile.py', OWN),
    'run_seq, TERMINAL_STATES, envelope and SIGNAL_NAMES': ('Journal', OWN),
    'durable events': ('Journal', '6'),
    'queue records': ('Box', '15'),
    'control decisions': ('ControlInbox', '15'),
}
ENTRY_TESTS = (
    'test_recovery_alert_records_producing_run',
    'test_recovery_alert_precedes_worktree_removal',
    'test_recovery_alert_is_once_per_reaped_run',
    'test_recovery_alert_failures_preserve_terminal_history',
    'test_recovery_alert_does_not_change_disposition',
    'test_every_engine_signal_name_is_listed',
    'test_listed_signal_names_are_accepted',
    'test_unknown_signal_name_is_refused_at_append',
    'test_restart_reuses_orphan_reconciliation',
)
OUTBOX_TESTS = (
    'test_outbox_only_check_accepts_registered_report',
    'test_outbox_only_check_requires_current_report',
    'test_outbox_only_check_failure_never_admits',
    'test_outbox_only_admission_records_null_commit_and_retires',
    'test_outbox_only_merge_regate_requires_lift_custody',
    'test_outbox_only_exception_preserves_code_lane_safety',
)
ENTRY_VERIFICATION = ('uv', 'run', 'pytest', 'tests/test_reconcile.py',
    'tests/test_restart_timers.py', 'tests/test_cli.py', 'tests/test_drain.py',
    'tests/test_journal.py', 'tests/test_vocabularies.py', 'tests/test_audit.py')
OUTBOX_VERIFICATION = ('uv', 'run', 'pytest', 'tests/test_stages.py', 'tests/test_merge.py',
    'tests/test_mergequeue.py', 'tests/test_serve.py', 'tests/test_cli.py', 'tests/test_drain.py',
    'tests/test_audit.py', 'tests/test_checkpoint.py')
PRESERVATION = ENTRY_VERIFICATION[5:]
CLOSURE_SNAPSHOT = {
    'roots': ('chupa/', 'eval/', 'tests/'),
    'patterns': ('recovery_alert|SIGNAL_NAMES|run_seq|reconcile|abandoned',
                 'read\\(\\)\\[-1\\]|events\\[-1\\]|records\\[-1\\]',
                 'not hasattr|production.*absence|public.*(surface|operation)',
                 'reconcile\\(|reconcile\\.reconcile|Journal\\(|build_daemon_core'),
    'production_callers': ('chupa/runner.py', 'chupa/drain.py', 'chupa/restart.py'),
    'test_callers': ('tests/test_reconcile.py', 'tests/test_restart_timers.py',
                     'tests/test_kill_failure_suppression.py'),
    'contradicted_assertions': ('tests/test_restart_timers.py:147',
                               'tests/test_kill_failure_suppression.py:327'),
    'preserved_roots': ('chupa/__main__.py', 'chupa/serve.py', 'chupa/daemon.py',
                        'eval/shakeout/recovery.py', 'tests/test_daemon_composition.py'),
    'preserved_predecessors': ('tests/test_harvest_orphans.py', 'tests/test_cli.py',
                              'tests/test_drain.py', 'tests/test_serve.py'),
}

AUTHORING_HEAD = 'a723480bb4ed340e1d0890ee18acbfda6fa30e8d'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

IMPLEMENT_SPEC_CHARS = 4775

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P3.worker-recovery-disposition': 6582,
 '6': 38005,
 '15': 17104,
 '19.L': 20858,
 '19.P3': 16240,
 '13': 19708,
 '19.P3.outbox-only-admission': 8122,
 '10': 6636,
 '19.P3.daemon-soak': 4342}

FILE_CHARS = {'chupa/reconcile.py': 2452,
 'tests/test_reconcile.py': 4420,
 'chupa/journal.py': 10588,
 'tests/test_restart_timers.py': 30910,
 'tests/test_kill_failure_suppression.py': 19127,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'worker-recovery-disposition': {'chars': 5216,
                                 'plan': ('19.I', '19.P3.worker-recovery-disposition', '6', '15'),
                                 'context': ('chupa/reconcile.py',
                                             'tests/test_reconcile.py',
                                             'chupa/journal.py',
                                             'tests/test_restart_timers.py',
                                             'tests/test_kill_failure_suppression.py'),
                                 'on_demand': (),
                                 'fenced_existing': ('chupa/reconcile.py',
                                                     'tests/test_reconcile.py',
                                                     'chupa/journal.py',
                                                     'tests/test_restart_timers.py',
                                                     'tests/test_kill_failure_suppression.py'),
                                 'created': (),
                                 'measured_render': 141091,
                                 'birth_sha256': '4c60c57c038d3d3ce2425cdf197567deec9a92dc57912917e5f27170ed376980'},
 'phase3-continue-23': {'chars': 9346,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.outbox-only-admission',
                                 '10',
                                 '19.P3.daemon-soak'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_23.py'),
                        'measured_render': 97245,
                        'birth_sha256': '7df5a67381ea5a9e59840b642d2184609c327285b7673fff6946639efee72f5e'}}



def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _birth(stem):
    # Rejection is later lifecycle history; these fixtures pin confirmed birth.
    return _text(stem).replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in dict.fromkeys((*a['context'], *STANDING_CONTEXT))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('worker-recovery-disposition',)
    assert BATCH == ('worker-recovery-disposition', 'phase3-continue-23')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    t = validate_ticket(stem, _birth(stem), ROOT, BATCH)
    fm = t.frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == STARTS[stem]
    assert hashlib.sha256(_birth(stem).encode()).hexdigest() == AUTHORED[stem]['birth_sha256']
    assert all('- **' + part + ':**' not in _text(stem) for part in CONTRACT_CUSTODY)


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'worker-recovery-disposition': ('phase3-continue-22',),
                     'phase3-continue-23': ('worker-recovery-disposition',)}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert t.scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert FENCE_FLOORS[PAYLOADS[0]] == ('chupa/reconcile.py', 'tests/test_reconcile.py')
    assert set(FENCE_ADDITIONS[PAYLOADS[0]]) == {
        'chupa/journal.py', 'tests/test_restart_timers.py', 'tests/test_kill_failure_suppression.py'}
    assert FENCE_ADDITIONS['phase3-continue-23'] == {}
    for path, reason in FENCE_ADDITIONS[stem].items():
        assert path in t.context and path in t.sections['Scope in / Scope out']
        assert '19.L' in reason and 'Context' in reason
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert len(CLOSURE_SNAPSHOT['patterns']) == 4
    assert CLOSURE_SNAPSHOT['production_callers'] == (
        'chupa/runner.py', 'chupa/drain.py', 'chupa/restart.py')
    assert not any(path.startswith('tests/test_seeded') for path in _ticket(PAYLOADS[0]).scope_fence)


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket(PAYLOADS[0])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', OWN, '6', '15')
    assert VALIDATED_ROW_CITATIONS[OWN] == ('6', '15')
    assert set(CONTRACT_CUSTODY.values()) == {OWN}
    assert len(ENTRY_TESTS) == len(set(ENTRY_TESTS)) == 9
    scope = t.sections['Scope in / Scope out']
    assert all(name in scope for name in ENTRY_TESTS)
    for fact in ('Owner, Records, Observable and Tests', 'cite them', 'Record custody',
                 'ordered recovery evidence', 'failure ordering', 'producing sequence',
                 'before abandonment', 'idempotence', 'unchanged disposition',
                 'shared startup/sweep ownership', 'clean/empty', 'historical non-ok',
                 'intent-only', 'missing worktrees', 'later re-entry', 'live-run exclusion',
                 'missing-running-witness', 'Keep vocabulary preservation tests unchanged',
                 'Journal(state_dir, clock)', 'append/read/close', 'bootstrap on-entry recovery',
                 'Restart startup/idle ownership', 'ordinary DaemonTasks exception propagation and cleanup',
                 'real CLI/async serve entrypoint', 'merged production-composition harness',
                 'injected seams', 'scripted callbacks', 'disposable synthetic repositories', 'asyncio barriers',
                 'No notification transport or routing work'):
        assert fact in scope, fact
    for record, (owner, citation) in RECORD_CUSTODY.items():
        assert citation in t.plan_contract
        assert owner in scope, record
    for fact in ('Journal alone durably appends', 'Box alone writes queue records',
                 'ControlInbox alone writes control decisions',
                 'test_kill_suppression_preserves_run_and_abort_failures'):
        assert fact in scope


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-23')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.outbox-only-admission', '10', '19.P3.daemon-soak')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_23.py')
    assert AUTHORING_HEAD == 'a723480bb4ed340e1d0890ee18acbfda6fa30e8d'
    assert MERGED_IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    assert VALIDATED_ENTRIES == (OWN, '19.P3.outbox-only-admission')
    assert VALIDATED_ROW_CITATIONS['19.P3.outbox-only-admission'] == ('19.L', '10')
    scope = t.sections['Scope in / Scope out']
    for fact in ('admissions[23:]', 'admissions[24:]', 'admissions[25:]',
                 'Author only outbox-only-admission and phase3-continue-24',
                 'high/high', 'medium/medium', 'entry_unit_gap', 'resolve_plan_contract',
                 '19.P3.daemon-soak', 'kind: spec_gap', 'only the current admission and immediate',
                 'never copy unit text', '19.L rules 2-5', 'record custody',
                 'Context by default', 'On-demand', '300,000-character headroom',
                 'same-admission sibling creations', 'historical seeding snapshots',
                 'authoring head', 'merged idiom blob', 'file and ticket sizes', 'plan-unit lengths',
                 'fixed authoring snapshots', 'never live sizes or live plan lengths',
                 'Terminal phase3-exit', 'seeding.max_seeds_per_admission',
                 'Keep previously approved seeds verbatim', 're-author only snagged seeds',
                 'tickets/phase3-continue-23/checks.json',
                 'chupa(phase3-continue-23): seeds ticket-plane commit'):
        assert fact in scope, fact
    assert all(name in scope for name in OUTBOX_TESTS)
    assert ' '.join(OUTBOX_VERIFICATION) in scope
    assert not any(path in t.context for path in (
        'tests/test_seeded_phase3_21.py', 'tests/test_seeded_phase3_22.py', 'tests/test_seeded_phase3_23.py'))


@pytest.mark.parametrize('stem', BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(t.scope_fence) == set(a['fenced_existing']) | set(a['created'])
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert not set(a['context']) & set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS == 300_000
    assert a['chars'] > 0 and all(PLAN_CHARS[pid] > 0 for pid in a['plan'])
    assert all(FILE_CHARS[path] > 0 for path in (*a['context'], *STANDING_CONTEXT))
    assert all(not path.startswith('specs/') and path != 'CHUPA_PLAN.md' for path in a['context'])
    assert not a['on_demand']  # All existing fenced paths fit embedded at the authoring head.


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket(PAYLOADS[0])
    assert t.verification == (ENTRY_VERIFICATION,
        ('uv', 'run', 'pytest', 'tests/test_kill_failure_suppression.py'))
    assert PRESERVATION == ('tests/test_cli.py', 'tests/test_drain.py', 'tests/test_journal.py',
                            'tests/test_vocabularies.py', 'tests/test_audit.py')
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites' in t.sections['Scope in / Scope out']
    assert _ticket('phase3-continue-23').verification == (
        ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_23.py'), ('uv', 'run', 'pytest', '-q'))
