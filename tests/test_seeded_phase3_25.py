"""Admission 25: fixed authoring snapshots, never live source sizes or plan lengths.

The merged core is the embedded idiom. Check owns seed review and ticket-plane lift.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ('daemon-soak-runner',)
BATCH = (*PAYLOADS, 'phase3-continue-26')
OWN = '19.P3.daemon-soak-runner'
LOOKAHEAD = '19.P3.soak-run'
MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'
HEADROOM_CHARS = 300_000
RENDER_OVERHEAD = 2_000
EDGES = {'daemon-soak-runner': ('phase3-continue-25',), 'phase3-continue-26': PAYLOADS}
STARTS = {'daemon-soak-runner': ('high', 'high'), 'phase3-continue-26': ('medium', 'medium')}
FENCE_FLOORS = {
    'daemon-soak-runner': ('eval/daemon_soak.py', 'tests/test_daemon_soak.py',
                         'tests/test_daemon_soak_runner.py'),
    'phase3-continue-26': ('tickets', 'tests/test_seeded_phase3_26.py'),
}
FENCE_ADDITIONS = {stem: {} for stem in BATCH}
VALIDATED_ENTRIES = (OWN, LOOKAHEAD)
VALIDATED_ROW_CITATIONS = {OWN: (), LOOKAHEAD: ()}
COPY_REFUSAL_CHECKED = BATCH
CONTRACT_CUSTODY = {part: OWN for part in ('Owner', 'Records', 'Observable', 'Tests')}
ENTRY_TESTS = (
    'test_daemon_soak_runs_production_serve',
    'test_daemon_soak_advances_each_member_24_hours',
    'test_daemon_soak_worker_recovery',
    'test_daemon_soak_conflict_rungs',
    'test_daemon_soak_semantic_red_preserves_main',
    'test_daemon_soak_requires_member_local_evidence',
    'test_daemon_soak_cleans_up_owned_lifetimes',
    'test_daemon_soak_is_rederivable',
    'test_daemon_soak_command_writes_report_only_on_green',
)
MERGED_TESTS = (
    'test_daemon_soak_schema_is_closed',
    'test_daemon_soak_green_matches_observation_and_auditor',
    'test_daemon_soak_writer_validates_before_write',
    'test_daemon_soak_uses_registered_checks_lift',
)
PREDECESSOR_TESTS = (
    'test_verification_report_lifts_only_in_checks_commit',
    'test_invalid_report_fails_check_without_lifting_checks_or_report',
    'test_implement_report_is_not_lifted_and_stale_report_is_purged',
    'test_named_missing_report_fails_even_when_other_commands_pass',
    'test_outbox_only_check_requires_current_report',
)
CUSTODY_PHRASES = (
    'Journal alone writes durable events', 'Box alone writes queue records',
    'ControlInbox alone writes control decisions', 'checks lift alone commits registered reports',
    'Journal(state_dir, clock)', 'append/read/close', 'bootstrap on-entry reconciliation',
    'ordinary DaemonTasks exception propagation and cleanup',
)
ENTRY_VERIFICATION = ('uv', 'run', 'pytest', 'tests/test_daemon_soak.py',
                      'tests/test_daemon_soak_runner.py', 'tests/test_serve.py',
                      'tests/test_mergequeue.py', 'tests/test_reconcile.py', 'tests/test_audit.py')
PRESERVATION = ENTRY_VERIFICATION[5:]
# New produce changes no existing signature or production composition binding.
# The floor's startup/import report-absence assertion remains true.
CLOSURE_SNAPSHOT = {
    'roots': ('chupa/', 'eval/', 'tests/'),
    'patterns': ('produce|write_report', 'KNOWN_ARTIFACTS|Artifact',
                 'purge|lift_outbox|model_validate_json',
                 'public|allowlist|not hasattr|absence', 'build_daemon_core|compose_pipeline'),
    'paths': {
        'eval/daemon_soak.py': ('registry floor: extend canonical writer module', 'Context'),
        'tests/test_daemon_soak.py': ('registry floor: preserve proofs and add command test', 'Context'),
        'tests/test_daemon_soak_runner.py': ('registry floor: new runner proof suite', 'created'),
    },
    'writer_callers': ('tests/test_daemon_soak.py',),
    'produce_callers': (),
    'writer_precedent': 'eval/shakeout/run.py',
    'composition_harness': 'tests/test_daemon_composition.py',
    'report_owners': ('chupa/artifacts.py', 'chupa/stages.py', 'chupa/merge.py'),
    'signature_decision': 'new produce; unchanged write_report signature and engine seams',
    'absence_decision': 'startup/import no-report stays true; module has no public allowlist',
    'addition_decision': '19.L rules 2-5 earn no additions; no seam-owner edit required',
    'serve_partition': 'chupa/serve.py remains an existing Context reference',
}

AUTHORING_HEAD = 'ed73ac5290cf961581547514ae77d5195122f587'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

IMPLEMENT_SPEC_CHARS = 4775

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

STANDING_CONTEXT = ()

PLAN_CHARS = {'19.I': 1811,
 '19.P3.daemon-soak-runner': 7136,
 '19.L': 20858,
 '19.P3': 16240,
 '13': 19708,
 '19.P3.soak-run': 2713}

FILE_CHARS = {'eval/daemon_soak.py': 667,
 'tests/test_daemon_soak.py': 15562,
 'chupa/artifacts.py': 8748,
 'chupa/stages.py': 59170,
 'chupa/git.py': 6640,
 'chupa/effects.py': 3229,
 'chupa/seams.py': 5551,
 'chupa/runner.py': 35603,
 'chupa/daemon.py': 26079,
 'chupa/__main__.py': 11605,
 'chupa/serve.py': 20113,
 'chupa/journal.py': 10606,
 'chupa/restart.py': 1951,
 'chupa/timers.py': 4966,
 'chupa/box.py': 10000,
 'chupa/audit.py': 5117,
 'chupa/rework.py': 12275,
 'chupa/mergequeue.py': 16262,
 'chupa/reconcile.py': 2715,
 'chupa/control.py': 9879,
 'eval/shakeout/run.py': 3981,
 'tests/test_seeded_phase3_core.py': 5425,
 'chupa/merge.py': 18346,
 'chupa/drain.py': 31622,
 'chupa/scheduler.py': 2907,
 'chupa/watcher.py': 2799,
 'tests/test_daemon_composition.py': 90814,
 'tests/test_serve.py': 65939,
 'tests/test_mergequeue.py': 53452,
 'tests/test_reconcile.py': 13940,
 'tests/test_audit.py': 3588,
 'tests/test_stages.py': 32249,
 'tests/test_merge.py': 34356}

FILE_BYTES = {'eval/daemon_soak.py': 667,
 'tests/test_daemon_soak.py': 15565,
 'chupa/artifacts.py': 8748,
 'chupa/stages.py': 59170,
 'chupa/git.py': 6640,
 'chupa/effects.py': 3229,
 'chupa/seams.py': 5551,
 'chupa/runner.py': 35603,
 'chupa/daemon.py': 26079,
 'chupa/__main__.py': 11605,
 'chupa/serve.py': 20113,
 'chupa/journal.py': 10606,
 'chupa/restart.py': 1951,
 'chupa/timers.py': 4966,
 'chupa/box.py': 10000,
 'chupa/audit.py': 5117,
 'chupa/rework.py': 12275,
 'chupa/mergequeue.py': 16262,
 'chupa/reconcile.py': 2715,
 'chupa/control.py': 9879,
 'eval/shakeout/run.py': 3981,
 'tests/test_seeded_phase3_core.py': 5425,
 'chupa/merge.py': 18346,
 'chupa/drain.py': 31622,
 'chupa/scheduler.py': 2907,
 'chupa/watcher.py': 2799,
 'tests/test_daemon_composition.py': 90814,
 'tests/test_serve.py': 65939,
 'tests/test_mergequeue.py': 53452,
 'tests/test_reconcile.py': 13940,
 'tests/test_audit.py': 3588,
 'tests/test_stages.py': 32249,
 'tests/test_merge.py': 34356}

DELIMITER_CHECKED = ('eval/daemon_soak.py',
 'tests/test_daemon_soak.py',
 'chupa/artifacts.py',
 'chupa/stages.py',
 'chupa/git.py',
 'chupa/effects.py',
 'chupa/seams.py',
 'chupa/runner.py',
 'chupa/daemon.py',
 'chupa/__main__.py',
 'chupa/serve.py',
 'chupa/journal.py',
 'chupa/restart.py',
 'chupa/timers.py',
 'chupa/box.py',
 'chupa/audit.py',
 'chupa/rework.py',
 'chupa/mergequeue.py',
 'chupa/reconcile.py',
 'chupa/control.py',
 'eval/shakeout/run.py',
 'tests/test_seeded_phase3_core.py')

AUTHORED = {'daemon-soak-runner': {'chars': 6168,
                        'bytes': 6168,
                        'plan': ('19.I', '19.P3.daemon-soak-runner'),
                        'context': ('eval/daemon_soak.py',
                                    'tests/test_daemon_soak.py',
                                    'chupa/artifacts.py',
                                    'chupa/stages.py',
                                    'chupa/git.py',
                                    'chupa/effects.py',
                                    'chupa/seams.py',
                                    'chupa/runner.py',
                                    'chupa/daemon.py',
                                    'chupa/__main__.py',
                                    'chupa/serve.py',
                                    'chupa/journal.py',
                                    'chupa/restart.py',
                                    'chupa/timers.py',
                                    'chupa/box.py',
                                    'chupa/audit.py',
                                    'chupa/rework.py',
                                    'chupa/mergequeue.py',
                                    'chupa/reconcile.py',
                                    'chupa/control.py',
                                    'eval/shakeout/run.py'),
                        'on_demand': (),
                        'fenced_existing': ('eval/daemon_soak.py', 'tests/test_daemon_soak.py'),
                        'created': ('tests/test_daemon_soak_runner.py',),
                        'measured_render': 291040,
                        'birth_sha256': '7c499347f42c9e97a0ebac04a5903c59c6e615a0bcf09954e2a4fdb3cc7f03b3'},
 'phase3-continue-26': {'chars': 7923,
                        'bytes': 7923,
                        'plan': ('19.L', '19.I', '19.P3', '13', '19.P3.soak-run'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_26.py'),
                        'measured_render': 79435,
                        'birth_sha256': 'c698083af1b7a1d2fc05a568256ac1ada3289e136bd82cca0bff8fb19f027680'}}




def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _birth(stem):
    # Rejection is later lifecycle history, not a different seed birth.
    return _text(stem).replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in dict.fromkeys((*a['context'], *STANDING_CONTEXT, *extra))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('daemon-soak-runner',)
    assert BATCH == ('daemon-soak-runner', 'phase3-continue-26')
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
    assert EDGES == {'daemon-soak-runner': ('phase3-continue-25',),
                     'phase3-continue-26': ('daemon-soak-runner',)}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    assert _ticket(stem).scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS == {key: {} for key in BATCH}
    assert tuple(CLOSURE_SNAPSHOT['paths']) == FENCE_FLOORS[PAYLOADS[0]]
    for path, (reason, partition) in CLOSURE_SNAPSHOT['paths'].items():
        assert reason.startswith('registry floor:')
        assert partition == ('Context' if path in AUTHORED[PAYLOADS[0]]['fenced_existing'] else 'created')
    assert CLOSURE_SNAPSHOT['writer_callers'] == ('tests/test_daemon_soak.py',)
    assert not CLOSURE_SNAPSHOT['produce_callers']
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert 'no earned fence additions' in _ticket(PAYLOADS[0]).sections['Scope in / Scope out']


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket(PAYLOADS[0])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', OWN)
    assert VALIDATED_ROW_CITATIONS == {OWN: (), LOOKAHEAD: ()}
    assert VALIDATED_ENTRIES == (OWN, LOOKAHEAD)
    assert set(CONTRACT_CUSTODY.values()) == {OWN}
    scope = t.sections['Scope in / Scope out']
    assert len(ENTRY_TESTS) == len(set(ENTRY_TESTS)) == 9
    assert len(MERGED_TESTS) == 4
    assert all(name in scope for name in (*ENTRY_TESTS, *MERGED_TESTS, *PREDECESSOR_TESTS))
    for fact in (*CUSTODY_PHRASES, 'Owner, Records, Observable and Tests',
                 'canonical write_report', 'Public produce', 'no exit report for its own lift',
                 'real dispatch and result consumption', 'original-run recovery alerts',
                 'both conflict rungs', 'integration-red refusal', 'member-local evidence',
                 'audit_journal', 'Box fault-visibility', 'strict membership', 'recurring cycles',
                 'false-green refusal', 'cleanup', 'byte-identical re-derivation',
                 'source-HEAD provenance', 'report-purge', 'schema-validation',
                 'named-report-required', 'checks-only custody', 'inherited byte-equal exclusion',
                 'real CLI/async serve entrypoint', 'merged production-composition harness',
                 'injected seams', 'scripted callbacks', 'disposable synthetic repositories',
                 'asyncio barriers', 'uv run python -m eval.daemon_soak --out <path>'):
        assert fact in scope, fact


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-26')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.L', '19.I', '19.P3', '13', LOOKAHEAD)
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_26.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    scope = t.sections['Scope in / Scope out']
    for fact in (*CUSTODY_PHRASES, 'admissions[26:]', 'admissions[27:]',
                 'Author only soak-run and phase3-continue-27', 'medium/medium', 'high/high',
                 'entry_unit_gap', 'resolve_plan_contract', 'kind: spec_gap', 'never later units',
                 'never copy unit text', '19.L rules 2-5', 'record custody', 'Context by default',
                 'On-demand', '300,000-character headroom', 'same-admission sibling creations',
                 'historical seeding snapshots', 'authoring head', 'merged idiom blob',
                 'file and ticket sizes', 'plan-unit lengths', 'fixed authoring snapshots',
                 'never live sizes or live plan lengths', 'Terminal phase3-exit',
                 'seeding.max_seeds_per_admission', 'Keep previously approved seeds verbatim',
                 're-author only snagged seeds', 'tickets/phase3-continue-26/checks.json',
                 'chupa(phase3-continue-26): seeds ticket-plane commit',
                 'terminal lookahead is governed by 19.P3',
                 'uv run python -m eval.daemon_soak --out tickets/soak-run/daemon-soak-report.json'):
        assert fact in scope, fact
    assert all(name in scope for name in (*MERGED_TESTS, *PREDECESSOR_TESTS,
        'test_daemon_soak_command_writes_report_only_on_green',
        'test_daemon_soak_requires_member_local_evidence', 'test_daemon_soak_is_rederivable',
        'test_outbox_only_check_accepts_registered_report',
        'test_outbox_only_admission_records_null_commit_and_retires'))
    assert all(name in scope for name in (
        'test_named_stems_cover_exactly_this_admission_and_successor',
        'test_seed_passes_intake_lint_with_confirmed_seed_birth',
        'test_stuck_budget_fits_the_drain_envelope', 'test_dependencies_as_authored',
        'test_fence_contains_its_floor_and_only_earned_additions',
        'test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract',
        'test_successor_cites_next_admission_and_embeds_merged_earlier_idiom',
        'test_context_closure_and_max_effort_render_use_authoring_snapshots',
        'test_payloads_run_preservation_suites_without_fencing_or_embedding_them'))


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
    assert all(FILE_BYTES[path] >= FILE_CHARS[path] > 0 for path in a['context'])
    assert set(a['context']) <= set(DELIMITER_CHECKED)
    assert all(not path.startswith('specs/') and path != 'CHUPA_PLAN.md' for path in a['context'])
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path
    assert not a['on_demand'] and STANDING_CONTEXT == ()
    assert not set(a['context']) & {'tests/test_seeded_phase3_24.py', 'tests/test_seeded_phase3_25.py'}
    assert 'chupa/serve.py' in AUTHORED[PAYLOADS[0]]['context']


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket(PAYLOADS[0])
    assert t.verification == (ENTRY_VERIFICATION,)
    assert PRESERVATION == ('tests/test_serve.py', 'tests/test_mergequeue.py',
                            'tests/test_reconcile.py', 'tests/test_audit.py')
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites' in t.sections['Scope in / Scope out']
    assert _ticket('phase3-continue-26').verification == (
        ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_26.py'), ('uv', 'run', 'pytest', '-q'))
