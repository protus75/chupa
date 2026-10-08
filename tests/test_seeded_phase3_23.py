"""Admission 23: seed identity, governing obligations and fixed authoring snapshots.

Lengths, closure decisions and base-render measurements are historical fixtures.
No test measures the current plan or source files after this authoring head.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ('outbox-only-admission',)
BATCH = (*PAYLOADS, 'phase3-continue-24')
OWN = '19.P3.outbox-only-admission'
MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'
HEADROOM_CHARS = 300_000
RENDER_OVERHEAD = 2_000
EDGES = {'outbox-only-admission': ('phase3-continue-23',),
         'phase3-continue-24': PAYLOADS}
STARTS = {'outbox-only-admission': ('high', 'high'),
          'phase3-continue-24': ('medium', 'medium')}
FENCE_FLOORS = {
    'outbox-only-admission': ('chupa/stages.py', 'chupa/merge.py',
                             'tests/test_stages.py', 'tests/test_merge.py'),
    'phase3-continue-24': ('tickets', 'tests/test_seeded_phase3_24.py'),
}
# Rules 2-5 found no invalidated predecessor or changed public signature.
# The floor contains the only changed assertion (the empty-work paved road).
FENCE_ADDITIONS = {stem: {} for stem in BATCH}
VALIDATED_ENTRIES = (OWN, '19.P3.daemon-soak')
VALIDATED_ROW_CITATIONS = {OWN: ('19.L', '10'), '19.P3.daemon-soak': ()}
COPY_REFUSAL_CHECKED = BATCH
DELIMITER_CHECKED = ('chupa/stages.py', 'chupa/merge.py', 'tests/test_stages.py',
                     'tests/test_merge.py', MERGED_IDIOM)
CONTRACT_CUSTODY = {part: OWN for part in ('Owner', 'Records', 'Observable', 'Tests')}
RECORD_CUSTODY = {
    'report discovery and validation': ('stages.py', OWN),
    'registered reports committed only by checks lift': ('checks lift alone commits', OWN),
    'Admission.commit and shared admission terminal': ('merge.py', OWN),
    'queue rebase, integration and holds': ('MergeQueue', OWN),
    'durable events': ('Journal alone writes durable events', '10'),
    'queue records': ('Box alone writes queue records', OWN),
    'control decisions': ('ControlInbox alone writes control decisions', OWN),
}
ENTRY_TESTS = (
    'test_outbox_only_check_accepts_registered_report',
    'test_outbox_only_check_requires_current_report',
    'test_outbox_only_check_failure_never_admits',
    'test_outbox_only_admission_records_null_commit_and_retires',
    'test_outbox_only_merge_regate_requires_lift_custody',
    'test_outbox_only_exception_preserves_code_lane_safety',
)
PREDECESSOR_TESTS = (
    'test_empty_diff_claimed_ok_fails_verification',
    'test_already_satisfied_is_proven_by_green_verification_and_skips_review',
    'test_verification_report_lifts_only_in_checks_commit',
    'test_invalid_report_fails_check_without_lifting_checks_or_report',
    'test_implement_report_is_not_lifted_and_stale_report_is_purged',
    'test_named_missing_report_fails_even_when_other_commands_pass',
)
SOAK_TESTS = (
    'test_daemon_soak_schema_is_closed',
    'test_daemon_soak_green_matches_observation_and_auditor',
    'test_daemon_soak_writer_validates_before_write',
    'test_daemon_soak_uses_registered_checks_lift',
)
ENTRY_VERIFICATION = ('uv', 'run', 'pytest', 'tests/test_stages.py', 'tests/test_merge.py',
    'tests/test_mergequeue.py', 'tests/test_serve.py', 'tests/test_cli.py', 'tests/test_drain.py',
    'tests/test_audit.py', 'tests/test_checkpoint.py')
PRESERVATION = ENTRY_VERIFICATION[5:]
CLOSURE_SNAPSHOT = {
    'roots': ('chupa/', 'eval/', 'tests/'),
    'patterns': ('empty.diff|already_satisfied|branch carries no committed',
                 'Admission|artifact.commit|write_squash',
                 'gather_evidence|KNOWN_ARTIFACTS|purge|lift_outbox',
                 'not hasattr|public.*(surface|operation)|absence',
                 'compose_pipeline|build_daemon_core'),
    'shared_writer_callers': ('chupa/merge.py:318', 'chupa/mergequeue.py:289'),
    'evidence_callers': ('chupa/stages.py:996', 'chupa/merge.py:308',
                         'chupa/mergequeue.py:271', 'tests/test_stages.py:543',
                         'tests/test_stages.py:568',
                         'tests/test_storm_notification_activation.py:347',
                         'tests/test_storm_notification_activation.py:352'),
    'empty_message_pins': ('tests/test_stages.py:425', 'eval/shakeout/stages.py:183'),
    'empty_message_decision': 'Preserve message; extend paved road inside the floor.',
    'code_commit_pins': ('tests/test_mergequeue.py:512', 'tests/test_serve.py:895',
                         'tests/test_daemon_composition.py:939'),
    'code_commit_decision': 'Ordinary code keeps its SHA; these assertions are not flipped.',
    'signature_decision': 'No changed public signature, constructor or composition wiring.',
    'absence_decision': 'No new public operation or invalidated production absence assertion.',
    'preserved_owners': ('chupa/runner.py', 'chupa/daemon.py', 'chupa/__main__.py',
                         'chupa/drain.py', 'chupa/serve.py', 'chupa/journal.py',
                         'chupa/restart.py', 'chupa/timers.py', 'chupa/audit.py',
                         'chupa/checkpoint.py', 'chupa/mergequeue.py'),
    'preserved_harness': 'tests/test_daemon_composition.py',
    'partition': {'chupa/stages.py': 'Context', 'chupa/merge.py': 'Context',
                  'tests/test_stages.py': 'Context', 'tests/test_merge.py': 'Context'},
}

AUTHORING_HEAD = 'b0a8b8119c40ffe54e09e1d792ad106dd9ed9768'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

IMPLEMENT_SPEC_CHARS = 4775

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

STANDING_CONTEXT = ()

PLAN_CHARS = {'19.I': 1811,
 '19.P3.outbox-only-admission': 8122,
 '19.L': 20858,
 '10': 6636,
 '19.P3': 16240,
 '13': 19708,
 '19.P3.daemon-soak': 4342,
 '19.P3.daemon-soak-runner': 7136}

FILE_CHARS = {'chupa/stages.py': 55517,
 'chupa/merge.py': 16060,
 'tests/test_stages.py': 26094,
 'tests/test_merge.py': 21147,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'outbox-only-admission': {'chars': 5831,
                           'bytes': 5831,
                           'plan': ('19.I', '19.P3.outbox-only-admission', '19.L', '10'),
                           'context': ('chupa/stages.py',
                                       'chupa/merge.py',
                                       'tests/test_stages.py',
                                       'tests/test_merge.py'),
                           'on_demand': (),
                           'fenced_existing': ('chupa/stages.py',
                                               'chupa/merge.py',
                                               'tests/test_stages.py',
                                               'tests/test_merge.py'),
                           'created': (),
                           'measured_render': 166890,
                           'birth_sha256': 'f8dc786d52b8baaf0be856a497b09d8a57791e3c90f76cf01c103833f09bfe7f'},
 'phase3-continue-24': {'chars': 8314,
                        'bytes': 8314,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.daemon-soak',
                                 '19.P3.daemon-soak-runner'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_24.py'),
                        'measured_render': 88591,
                        'birth_sha256': 'c9da258e29e750e7ca60bb3509abfa39294c7f4f702999e3d7d5c9019da90313'}}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _birth(stem):
    # A later lifecycle rejection does not change the confirmed birth contract.
    return _text(stem).replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in dict.fromkeys((*a['context'], *STANDING_CONTEXT))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('outbox-only-admission',)
    assert BATCH == ('outbox-only-admission', 'phase3-continue-24')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = validate_ticket(stem, _birth(stem), ROOT, BATCH).frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == STARTS[stem]
    assert hashlib.sha256(_birth(stem).encode()).hexdigest() == AUTHORED[stem]['birth_sha256']
    assert COPY_REFUSAL_CHECKED == BATCH
    assert not any('- **' + part + ':**' in _text(stem) for part in CONTRACT_CUSTODY)


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'outbox-only-admission': ('phase3-continue-23',),
                     'phase3-continue-24': ('outbox-only-admission',)}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    assert _ticket(stem).scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS == {key: {} for key in BATCH}
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert len(CLOSURE_SNAPSHOT['patterns']) == 5
    assert CLOSURE_SNAPSHOT['shared_writer_callers'] == ('chupa/merge.py:318', 'chupa/mergequeue.py:289')
    assert CLOSURE_SNAPSHOT['empty_message_pins'] == ('tests/test_stages.py:425', 'eval/shakeout/stages.py:183')
    assert set(CLOSURE_SNAPSHOT['partition']) == set(FENCE_FLOORS[PAYLOADS[0]])
    assert set(CLOSURE_SNAPSHOT['partition'].values()) == {'Context'}
    assert 'no earned fence additions' in _ticket(PAYLOADS[0]).sections['Scope in / Scope out']
    assert not any(path.startswith('tests/test_seeded') for path in _ticket(PAYLOADS[0]).scope_fence)


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket(PAYLOADS[0])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', OWN, '19.L', '10')
    assert VALIDATED_ROW_CITATIONS[OWN] == ('19.L', '10')
    assert set(CONTRACT_CUSTODY.values()) == {OWN}
    scope = t.sections['Scope in / Scope out']
    assert len(ENTRY_TESTS) == len(set(ENTRY_TESTS)) == 6
    assert all(name in scope for name in (*ENTRY_TESTS, *PREDECESSOR_TESTS))
    for phrase, citation in RECORD_CUSTODY.values():
        assert phrase in scope and citation in t.plan_contract
    for fact in ('Owner, Records, Observable and Tests', 'cite them', 'current-run output',
                 'purge before Verification', 'schema validation', 'checks-custody',
                 'matching lift custody', 'null-commit settlement', 'unchanged code tree',
                 'retirement', 'replay', 'approval', 'code-lane safety', 'write_squash',
                 'without a signature change', 'Journal(state_dir, clock)', 'append/read/close',
                 'bootstrap on-entry reconciliation', 'Restart/Timers ownership',
                 'ordinary DaemonTasks exception propagation and cleanup',
                 'real CLI/async serve entrypoint', 'merged production-composition harness',
                 'injected seams', 'scripted callbacks', 'disposable synthetic repositories',
                 'asyncio barriers', 'Git/Effects', 'MERGE_SPEC_VERSION',
                 'Audit the producing journals', 'dependency eligibility', 'checkpoint counting'):
        assert fact in scope, fact


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-24')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.daemon-soak', '19.P3.daemon-soak-runner')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_24.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == (OWN, '19.P3.daemon-soak')
    assert VALIDATED_ROW_CITATIONS['19.P3.daemon-soak'] == ()
    scope = t.sections['Scope in / Scope out']
    for fact in ('admissions[24:]', 'admissions[25:]', 'admissions[26:]',
                 'Author only daemon-soak and phase3-continue-25', 'high/high', 'medium/medium',
                 'entry_unit_gap', 'resolve_plan_contract', '19.P3.daemon-soak-runner',
                 '19.P3.soak-run', 'kind: spec_gap', 'never later units',
                 'never copy unit text', '19.L rules 2-5', 'record custody',
                 'Context by default', 'On-demand', '300,000-character headroom',
                 'same-admission sibling creations', 'historical seeding snapshots',
                 'authoring head', 'merged idiom blob', 'file and ticket sizes', 'plan-unit lengths',
                 'fixed authoring snapshots', 'never live sizes or live plan lengths',
                 'Terminal phase3-exit', 'seeding.max_seeds_per_admission',
                 'Keep previously approved seeds verbatim', 're-author only snagged seeds',
                 'tickets/phase3-continue-24/checks.json',
                 'chupa(phase3-continue-24): seeds ticket-plane commit',
                 'checks lift alone commits registered reports'):
        assert fact in scope, fact
    assert all(name in scope for name in SOAK_TESTS)
    assert 'uv run pytest tests/test_daemon_soak.py tests/test_stages.py' in scope
    assert not any(path in t.context for path in (
        'tests/test_seeded_phase3_22.py', 'tests/test_seeded_phase3_23.py', 'tests/test_seeded_phase3_24.py'))


@pytest.mark.parametrize('stem', BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(t.scope_fence) == set(a['fenced_existing']) | set(a['created'])
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert not set(a['context']) & set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS == 300_000
    assert a['bytes'] >= a['chars'] > 0
    assert all(PLAN_CHARS[pid] > 0 for pid in a['plan'])
    assert all(FILE_CHARS[path] > 0 for path in (*a['context'], *STANDING_CONTEXT))
    assert set(a['context']) <= set(DELIMITER_CHECKED)
    assert all(not path.startswith('specs/') and path != 'CHUPA_PLAN.md' for path in a['context'])
    assert not a['on_demand']  # Measured embedded renders fit at every effort.
    assert STANDING_CONTEXT == ()


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket(PAYLOADS[0])
    assert t.verification == (ENTRY_VERIFICATION,)
    assert PRESERVATION == ('tests/test_mergequeue.py', 'tests/test_serve.py', 'tests/test_cli.py',
                            'tests/test_drain.py', 'tests/test_audit.py', 'tests/test_checkpoint.py')
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites' in t.sections['Scope in / Scope out']
    assert _ticket('phase3-continue-24').verification == (
        ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_24.py'), ('uv', 'run', 'pytest', '-q'))
