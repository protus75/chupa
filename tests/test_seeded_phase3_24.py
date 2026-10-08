"""Admission 24: identity, custody and render closure pinned at the authoring head.

Source and plan lengths are immutable snapshots; later tickets never remeasure them.
The merged core test supplies the idiom. This test covers only these two new seeds.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ('daemon-soak',)
BATCH = (*PAYLOADS, 'phase3-continue-25')
OWN = '19.P3.daemon-soak'
LOOKAHEAD = '19.P3.daemon-soak-runner'
MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'
HEADROOM_CHARS = 300_000
RENDER_OVERHEAD = 2_000
EDGES = {'daemon-soak': ('phase3-continue-24',), 'phase3-continue-25': PAYLOADS}
STARTS = {'daemon-soak': ('high', 'high'), 'phase3-continue-25': ('medium', 'medium')}
FENCE_FLOORS = {
    'daemon-soak': ('eval/daemon_soak.py', 'chupa/artifacts.py', 'chupa/stages.py',
                    'tests/test_daemon_soak.py'),
    'phase3-continue-25': ('tickets', 'tests/test_seeded_phase3_25.py'),
}
# Rules 2-5 earn nothing: dynamic registration changes no signatures or old assertions.
FENCE_ADDITIONS = {stem: {} for stem in BATCH}
VALIDATED_ENTRIES = (OWN, LOOKAHEAD)
VALIDATED_ROW_CITATIONS = {OWN: (), LOOKAHEAD: ()}
COPY_REFUSAL_CHECKED = BATCH
CONTRACT_CUSTODY = {part: OWN for part in ('Owner', 'Records', 'Observable', 'Tests')}
ENTRY_TESTS = (
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
RUNNER_TESTS = (
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
ENTRY_VERIFICATION = ('uv', 'run', 'pytest', 'tests/test_daemon_soak.py', 'tests/test_stages.py')
PRESERVATION = ('tests/test_stages.py',)
CUSTODY_PHRASES = (
    'Journal alone writes durable events', 'Box alone writes queue records',
    'ControlInbox alone writes control decisions', 'checks lift alone commits registered reports',
    'Journal(state_dir, clock)', 'append/read/close', 'bootstrap on-entry reconciliation',
    'ordinary DaemonTasks exception propagation and cleanup',
)
CLOSURE_SNAPSHOT = {
    'roots': ('chupa/', 'eval/', 'tests/'),
    'patterns': ('KNOWN_ARTIFACTS|Artifact|ShakeoutReport', 'purge|lift_outbox|model_validate_json',
                 'public|allowlist|not hasattr|absence',
                 'compose_pipeline|build_daemon_core|write_report'),
    'registration_consumers': ('chupa/stages.py:225', 'chupa/stages.py:234',
                               'chupa/stages.py:241', 'chupa/stages.py:669',
                               'chupa/stages.py:683', 'chupa/stages.py:1052',
                               'chupa/merge.py:373', 'chupa/merge.py:379'),
    'lift_callers': ('chupa/stages.py', 'chupa/runner.py', 'tests/test_merge.py'),
    'writer_precedent': 'eval/shakeout/run.py:82',
    'signature_decision': 'No existing public signature, constructor or composition wiring changes.',
    'negative_decision': 'No earlier dormancy/absence assertion or public allowlist is invalidated.',
    'preservation_decision': 'Existing report tests stay green through dynamic registration; no edit earned.',
    'partition': {'chupa/artifacts.py': 'Context', 'chupa/stages.py': 'Context'},
    'created': ('eval/daemon_soak.py', 'tests/test_daemon_soak.py'),
    'read_owners': ('chupa/artifacts.py', 'chupa/stages.py', 'eval/shakeout/run.py',
                    'chupa/git.py', 'chupa/effects.py', 'chupa/seams.py',
                    'chupa/runner.py', 'chupa/daemon.py', 'chupa/__main__.py',
                    'chupa/drain.py', 'chupa/serve.py', 'chupa/journal.py',
                    'chupa/restart.py', 'chupa/timers.py', 'chupa/reconcile.py',
                    'chupa/merge.py', 'chupa/mergequeue.py', 'chupa/box.py', 'chupa/control.py',
                    'chupa/audit.py'),
    'preserved_harness': 'tests/test_daemon_composition.py',
}

AUTHORING_HEAD = 'f2461f2b463a40c25b06be54bf787747d57f86e1'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

IMPLEMENT_SPEC_CHARS = 4896

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

STANDING_CONTEXT = ()

PLAN_CHARS = {'19.I': 1811,
 '19.P3.daemon-soak': 4342,
 '19.L': 20858,
 '19.P3': 16240,
 '13': 19708,
 '19.P3.daemon-soak-runner': 7136,
 '19.P3.soak-run': 2713}

FILE_CHARS = {'chupa/artifacts.py': 6706,
 'chupa/stages.py': 59049,
 'chupa/git.py': 6640,
 'chupa/seams.py': 5551,
 'chupa/effects.py': 3229,
 'eval/shakeout/run.py': 3981,
 'tests/test_seeded_phase3_core.py': 5425}

FILE_BYTES = {'chupa/artifacts.py': 6706,
 'chupa/stages.py': 59049,
 'chupa/git.py': 6640,
 'chupa/seams.py': 5551,
 'chupa/effects.py': 3229,
 'eval/shakeout/run.py': 3981,
 'tests/test_seeded_phase3_core.py': 5425}

DELIMITER_CHECKED = ('chupa/artifacts.py',
 'chupa/stages.py',
 'chupa/git.py',
 'chupa/seams.py',
 'chupa/effects.py',
 'eval/shakeout/run.py',
 'tests/test_seeded_phase3_core.py')

AUTHORED = {'daemon-soak': {'chars': 4892,
                 'bytes': 4892,
                 'plan': ('19.I', '19.P3.daemon-soak'),
                 'context': ('chupa/artifacts.py',
                             'chupa/stages.py',
                             'chupa/git.py',
                             'chupa/seams.py',
                             'chupa/effects.py',
                             'eval/shakeout/run.py'),
                 'on_demand': (),
                 'fenced_existing': ('chupa/artifacts.py', 'chupa/stages.py'),
                 'created': ('eval/daemon_soak.py', 'tests/test_daemon_soak.py'),
                 'measured_render': 101056,
                 'birth_sha256': 'ddb43718964c94e9767019c97256180c0d541045e8c4355ba457d1b89b3f9d39'},
 'phase3-continue-25': {'chars': 9279,
                        'bytes': 9279,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.daemon-soak-runner',
                                 '19.P3.soak-run'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_25.py'),
                        'measured_render': 87927,
                        'birth_sha256': 'c3c2f8d734a8127b706078c78071ff3060b0a247d933dc01cadb6ac089ccea09'}}



def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _birth(stem):
    # Rejection is lifecycle history; seed birth remains confirmed.
    return _text(stem).replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in dict.fromkeys((*a['context'], *STANDING_CONTEXT, *extra))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('daemon-soak',)
    assert BATCH == ('daemon-soak', 'phase3-continue-25')
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
    assert EDGES == {'daemon-soak': ('phase3-continue-24',), 'phase3-continue-25': ('daemon-soak',)}


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    assert _ticket(stem).scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS == {key: {} for key in BATCH}
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert set(CLOSURE_SNAPSHOT['partition']) == set(AUTHORED['daemon-soak']['fenced_existing'])
    assert set(CLOSURE_SNAPSHOT['partition'].values()) == {'Context'}
    assert CLOSURE_SNAPSHOT['created'] == AUTHORED['daemon-soak']['created']
    assert CLOSURE_SNAPSHOT['registration_consumers'][-2:] == ('chupa/merge.py:373', 'chupa/merge.py:379')
    assert CLOSURE_SNAPSHOT['writer_precedent'] == 'eval/shakeout/run.py:82'
    assert 'no earned fence additions' in _ticket(PAYLOADS[0]).sections['Scope in / Scope out']
    assert not any(path.startswith('tests/test_seeded') for path in _ticket(PAYLOADS[0]).scope_fence)


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket(PAYLOADS[0])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', OWN)
    assert VALIDATED_ROW_CITATIONS == {OWN: (), LOOKAHEAD: ()}
    assert set(CONTRACT_CUSTODY.values()) == {OWN}
    scope = t.sections['Scope in / Scope out']
    assert len(ENTRY_TESTS) == len(set(ENTRY_TESTS)) == 4
    assert all(name in scope for name in (*ENTRY_TESTS, *PREDECESSOR_TESTS))
    for fact in (*CUSTODY_PHRASES, 'Owner, Records, Observable and Tests',
                 'schema', 'provenance', 'strict ordered membership', 'false-green refusal',
                 'filesystem writer', 'registration', 'no machinery-produced exit report',
                 'neither a runner nor a producing run', 'report-purge before Verification',
                 'schema-validation', 'named-report-required', 'inherited byte-equal exclusion',
                 'real CLI/async serve entrypoint', 'merged production-composition harness',
                 'injected seams', 'scripted callbacks', 'disposable synthetic repositories',
                 'asyncio barriers'):
        assert fact in scope, fact


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase3-continue-25')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', LOOKAHEAD, '19.P3.soak-run')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_25.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == (OWN, LOOKAHEAD)
    scope = t.sections['Scope in / Scope out']
    for fact in (*CUSTODY_PHRASES, 'admissions[25:]', 'admissions[26:]', 'admissions[27:]',
                 'Author only daemon-soak-runner and phase3-continue-26',
                 'high/high', 'medium/medium', 'entry_unit_gap', 'resolve_plan_contract',
                 '19.P3.soak-run', 'kind: spec_gap', 'never later units', 'never copy unit text',
                 '19.L rules 2-5', 'record custody', 'Context by default', 'On-demand',
                 '300,000-character headroom', 'same-admission sibling creations',
                 'historical seeding snapshots', 'authoring head', 'merged idiom blob',
                 'file and ticket sizes', 'plan-unit lengths', 'fixed authoring snapshots',
                 'never live sizes or live plan lengths', 'Terminal phase3-exit',
                 'seeding.max_seeds_per_admission', 'Keep previously approved seeds verbatim',
                 're-author only snagged seeds', 'tickets/phase3-continue-25/checks.json',
                 'chupa(phase3-continue-25): seeds ticket-plane commit',
                 'uv run pytest tests/test_daemon_soak.py tests/test_daemon_soak_runner.py '
                 'tests/test_serve.py tests/test_mergequeue.py tests/test_reconcile.py tests/test_audit.py'):
        assert fact in scope, fact
    assert all(name in scope for name in RUNNER_TESTS)
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
    assert not set(a['context']) & {'tests/test_seeded_phase3_23.py', 'tests/test_seeded_phase3_24.py'}


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket(PAYLOADS[0])
    assert t.verification == (ENTRY_VERIFICATION,)
    assert PRESERVATION == ('tests/test_stages.py',)
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suite' in t.sections['Scope in / Scope out']
    assert _ticket('phase3-continue-25').verification == (
        ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_25.py'), ('uv', 'run', 'pytest', '-q'))
