"""Phase 4 admission 03: immutable authoring snapshots; live tickets retain intake lint.

Sizes, entry-depth evidence and max-effort renders are pinned at authoring, never remeasured.
"""
import hashlib
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = '78186f778a805d07e8032260f72670108b67a001'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('reliability-battery',)

BATCH = ('reliability-battery', 'phase4-continue-04')

REGISTRY_ADMISSIONS = (('watchdog-event-stream', 'notify-transport'),
 ('watchdog-detector', 'watchdog-activation'),
 ('provider-cooldown-failover',),
 ('reliability-battery',),
 ('reliability-run',),
 ('phase4-exit',))

UNSEEDED_SUFFIX = (('reliability-run',), ('phase4-exit',))

REGISTRY_SHA256 = '77ea8ec6b81c5cc7daafa6e15c4aab1318fd094de929cb0ba42a2fdcc901e9df'

EDGES = {'reliability-battery': ('phase4-continue-03',), 'phase4-continue-04': ('reliability-battery',)}

FENCE_FLOORS = {'reliability-battery': ('eval/reliability_battery.py',
                         'chupa/artifacts.py',
                         'chupa/stages.py',
                         'tests/test_reliability_battery.py'),
 'phase4-continue-04': ('tickets', 'tests/test_seeded_phase4_04.py')}

FENCE_ADDITIONS = {'reliability-battery': {}, 'phase4-continue-04': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4775

RENDER_OVERHEAD = 2000

STANDING_CONTEXT = ()

DRAIN_MAX_TICKET_MINUTES = 180

MAX_SEEDS_PER_ADMISSION = 3

PLAN_CHARS = {'19.I': 1811,
 '19.P4.reliability-battery': 6888,
 '19.P4.provider-cooldown-failover': 13252,
 '6': 38048,
 '19.L': 20912,
 '19.P4': 5641,
 '13': 19840,
 '19.P4.reliability-run': 3372}

FILE_CHARS = {'chupa/artifacts.py': 8748,
 'chupa/stages.py': 61056,
 'chupa/providers.py': 27676,
 'chupa/timers.py': 4966,
 'chupa/audit.py': 5261,
 'chupa/journal.py': 11011,
 'chupa/seams.py': 10148,
 'chupa/git.py': 6640,
 'chupa/runner.py': 38439,
 'chupa/driver.py': 23190,
 'tickets/provider-cooldown-failover/ticket.md': 8343,
 'tests/test_seeded_phase3_core.py': 5425}

FILE_BYTES = {'chupa/artifacts.py': 8748,
 'chupa/stages.py': 61056,
 'chupa/providers.py': 27676,
 'chupa/timers.py': 4966,
 'chupa/audit.py': 5261,
 'chupa/journal.py': 11011,
 'chupa/seams.py': 10148,
 'chupa/git.py': 6640,
 'chupa/runner.py': 38439,
 'chupa/driver.py': 23190,
 'tickets/provider-cooldown-failover/ticket.md': 8343,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'reliability-battery': {'chars': 6341,
                         'bytes': 6341,
                         'plan': ('19.I',
                                  '19.P4.reliability-battery',
                                  '19.P4.provider-cooldown-failover',
                                  '6'),
                         'context': ('chupa/artifacts.py',
                                     'chupa/stages.py',
                                     'chupa/providers.py',
                                     'chupa/timers.py',
                                     'chupa/audit.py',
                                     'chupa/journal.py',
                                     'chupa/seams.py',
                                     'chupa/git.py',
                                     'chupa/runner.py',
                                     'chupa/driver.py',
                                     'tickets/provider-cooldown-failover/ticket.md'),
                         'on_demand': (),
                         'fenced_existing': ('chupa/artifacts.py', 'chupa/stages.py'),
                         'created': ('eval/reliability_battery.py',
                                     'tests/test_reliability_battery.py'),
                         'measured_render': 276809,
                         'birth_sha256': 'cdb5b2924bcf71edc5590f7a26c1b224a3c5e6c2bd4755d89f7ca6d9c9badf76'},
 'phase4-continue-04': {'chars': 6067,
                        'bytes': 6067,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P4',
                                 '13',
                                 '19.P4.reliability-run',
                                 '19.P4.reliability-battery'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase4_04.py'),
                        'measured_render': 74713,
                        'birth_sha256': 'b17405c20ffa10ed2044d8308340f06681d296abc5f0fc736f01a28704ddbe23'}}

VALIDATED_ENTRIES = {'19.P4.reliability-battery': {'Owner': True, 'Records': True, 'Observable': True, 'Tests': True},
 '19.P4.provider-cooldown-failover': {'Owner': True,
                                      'Records': True,
                                      'Observable': True,
                                      'Tests': True},
 '19.P4.reliability-run': {'Owner': True, 'Records': True, 'Observable': True, 'Tests': True}}

REQUIRED_ENTRIES = {'reliability-battery': ('19.P4.reliability-battery', '19.P4.provider-cooldown-failover'),
 'phase4-continue-04': ('19.P4.reliability-run', '19.P4.reliability-battery')}

VALIDATED_ROW_CITATIONS = {'19.P4.reliability-battery': ('6',), '19.P4.reliability-run': ()}

ENTRY_TESTS = ('test_reliability_battery_schema_is_closed',
 'test_reliability_battery_green_requires_observation_and_auditor',
 'test_reliability_battery_writer_validates_before_write',
 'test_reliability_battery_uses_registered_checks_lift',
 'test_classified_quota_exhaustion',
 'test_all_candidates_cooling_recovery',
 'test_unclassified_failure_preservation',
 'test_reliability_battery_requires_member_local_evidence',
 'test_reliability_battery_cleans_up_owned_lifetimes',
 'test_reliability_battery_command_writes_only_on_green')

CUSTODY_TESTS = ('test_verification_report_lifts_only_in_checks_commit',
 'test_invalid_report_fails_check_without_lifting_checks_or_report',
 'test_implement_report_is_not_lifted_and_stale_report_is_purged',
 'test_named_missing_report_fails_even_when_other_commands_pass',
 'test_outbox_only_check_requires_current_report')

SUCCESSOR_TESTS = ('test_named_stems_cover_exactly_this_admission_and_successor',
 'test_seed_passes_intake_lint_with_confirmed_seed_birth',
 'test_dependencies_as_authored',
 'test_stuck_budget_fits_the_drain_envelope',
 'test_fence_contains_its_floor_and_only_earned_additions',
 'test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract',
 'test_successor_cites_next_admission_and_embeds_merged_earlier_idiom',
 'test_context_closure_and_max_effort_render_use_authoring_snapshots')

DELIMITER_CHECKED = ('chupa/artifacts.py',
 'chupa/stages.py',
 'chupa/providers.py',
 'chupa/timers.py',
 'chupa/audit.py',
 'chupa/journal.py',
 'chupa/seams.py',
 'chupa/git.py',
 'chupa/runner.py',
 'chupa/driver.py',
 'tickets/provider-cooldown-failover/ticket.md',
 'tests/test_seeded_phase3_core.py')

COPY_REFUSAL_CHECKED = ('reliability-battery', 'phase4-continue-04')

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'patterns': ('produce|write_report|ReliabilityBattery',
              'KNOWN_ARTIFACTS|Artifact|purge|lift_outbox',
              'ProviderLLM|ProviderSession|prepare_pipeline|build_daemon_core',
              '__all__|not hasattr|public.*allowlist|is_dormant'),
 'paths': {'eval/reliability_battery.py': ('registry floor: new runner and canonical writer owned '
                                           'by the battery entry',
                                           'created'),
           'chupa/artifacts.py': ('registry floor: closed schema and constants owner', 'Context'),
           'chupa/stages.py': ('registry floor: existing report registration owner', 'Context'),
           'tests/test_reliability_battery.py': ('registry floor: new entry-named battery proofs',
                                                 'created')},
 'decision': 'New eval runner has no existing callers; model additions and mapping registration '
             'change no public signatures, constructor arity, production wiring or predecessor '
             'absence assertions. No allowlist pins these additive surfaces; no earned additions.'}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _birth(stem):
    # A later rejection changes lifecycle state, not the authored seed identity.
    return _text(stem).replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in dict.fromkeys(
                (*a['context'], *STANDING_CONTEXT, *extra))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('reliability-battery',)
    assert BATCH == ('reliability-battery', 'phase4-continue-04')
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(BATCH) == set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED)
    assert REGISTRY_ADMISSIONS == (
        ('watchdog-event-stream', 'notify-transport'), ('watchdog-detector', 'watchdog-activation'),
        ('provider-cooldown-failover',), ('reliability-battery',), ('reliability-run',), ('phase4-exit',))
    assert REGISTRY_ADMISSIONS[3] == PAYLOADS
    assert UNSEEDED_SUFFIX == REGISTRY_ADMISSIONS[4:] == (('reliability-run',), ('phase4-exit',))
    assert len(REGISTRY_SHA256) == 64


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = validate_ticket(stem, _birth(stem), ROOT, BATCH).frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == ('medium', 'medium')
    assert fm.gate_bypass == []
    assert hashlib.sha256(_birth(stem).encode()).hexdigest() == AUTHORED[stem]['birth_sha256']
    assert COPY_REFUSAL_CHECKED == BATCH
    assert not any('- **' + part + ':**' in _birth(stem)
                   for part in ('Owner', 'Records', 'Observable', 'Tests'))


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES == {'reliability-battery': ('phase4-continue-03',),
                     'phase4-continue-04': ('reliability-battery',)}


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert t.scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS == {s: {} for s in BATCH}
    assert FENCE_FLOORS == {
        'reliability-battery': ('eval/reliability_battery.py', 'chupa/artifacts.py',
                                'chupa/stages.py', 'tests/test_reliability_battery.py'),
        'phase4-continue-04': ('tickets', 'tests/test_seeded_phase4_04.py')}
    assert tuple(CLOSURE_SNAPSHOT['paths']) == FENCE_FLOORS[PAYLOADS[0]]
    for path, (reason, partition) in CLOSURE_SNAPSHOT['paths'].items():
        assert reason.startswith('registry floor:')
        assert partition == ('Context' if path in AUTHORED[PAYLOADS[0]]['fenced_existing'] else 'created')
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert len(CLOSURE_SNAPSHOT['patterns']) == 4
    assert 'no existing callers' in CLOSURE_SNAPSHOT['decision']
    assert 'No allowlist' in CLOSURE_SNAPSHOT['decision']
    assert 'no earned fence additions' in _ticket(PAYLOADS[0]).sections['Scope in / Scope out']


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    own, predecessor = '19.P4.reliability-battery', '19.P4.provider-cooldown-failover'
    t = _ticket(PAYLOADS[0])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', own, predecessor, '6')
    assert '19.L' not in t.plan_contract and '19.P4' not in t.plan_contract
    assert VALIDATED_ROW_CITATIONS == {own: ('6',), '19.P4.reliability-run': ()}
    assert REQUIRED_ENTRIES[t.stem] == (own, predecessor)
    assert set(VALIDATED_ENTRIES) == {own, predecessor, '19.P4.reliability-run'}
    assert all(parts == dict.fromkeys(('Owner', 'Records', 'Observable', 'Tests'), True)
               for parts in VALIDATED_ENTRIES.values())
    assert ENTRY_TESTS == (
        'test_reliability_battery_schema_is_closed',
        'test_reliability_battery_green_requires_observation_and_auditor',
        'test_reliability_battery_writer_validates_before_write',
        'test_reliability_battery_uses_registered_checks_lift',
        'test_classified_quota_exhaustion', 'test_all_candidates_cooling_recovery',
        'test_unclassified_failure_preservation',
        'test_reliability_battery_requires_member_local_evidence',
        'test_reliability_battery_cleans_up_owned_lifetimes',
        'test_reliability_battery_command_writes_only_on_green')
    scope = t.sections['Scope in / Scope out']
    assert all(name in scope for name in (*ENTRY_TESTS, *CUSTODY_TESTS))
    for fact in (
        'Owner, Records, Observable and Tests', 'eval/reliability_battery.py owns produce and write_report',
        'chupa/artifacts.py owns ReliabilityBatteryEntry, ReliabilityBatteryReport',
        'chupa/stages.py owns registration', 'publishes no exit artifact', 'separate later producer',
        'merged production composition', 'multi-candidate fixture registry', 'scripted CLI failures',
        'no tests imports', 'one provider payload and one Timers lifetime',
        'classified_quota_exhaustion', 'all_candidates_cooling_recovery',
        'unclassified_failure_preservation', 'harvested failed terminal', 'exact persisted cooldown',
        'absence of infra draw or inline retry', 'cost-free drought hold',
        'no call, cap, diagnosis or Reject arrival', 'earliest deadline', 'matching timer_fired',
        'automatic recovery', 'result/completion/run-record served identity',
        'unclassified with normal infra accounting and captured error evidence',
        'member-local production records and the entire member journal',
        'producing_run', 'audit_journal supplies ordered violation descriptions',
        'Missing evidence, contradictory evidence, cross-member evidence',
        'supplied success/auditor verdict', 'await owned lifetimes before auditing',
        'Git cleans disposable worktrees on success, failure and cancellation',
        'clock, sleep, process-exec and filesystem seams', 'closed schema fields and strict types',
        'fixed expected values', 'unique complete member order', 'run identity',
        'inherited version policy', 'spec/source-HEAD provenance', 'false-green rejection',
        'canonical writer revalidates', 'refuses red/invalid reports without writing',
        'canonical UTF-8 JSON', 'trailing newline through FileSystem.write', 'no Git or journal action',
        'own name in KNOWN_ARTIFACTS', 'purge before Verification', 'schema validation',
        'named-report-required', 'checks-only custody', 'inherited-copy exclusion',
        'uv run python -m eval.reliability_battery --out <path>', 'all-green completion',
        'member-specific repair road', 'no selector, committer or automatic invocation'):
        assert fact in scope, fact
    preservation = ('tests/test_stages.py', 'tests/test_provider_cooldown_failover.py', 'tests/test_audit.py')
    assert t.verification == (('uv', 'run', 'pytest', 'tests/test_reliability_battery.py', *preservation),)
    assert not set(preservation) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase4-continue-04')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P4', '13', '19.P4.reliability-run', '19.P4.reliability-battery')
    assert REQUIRED_ENTRIES[t.stem] == ('19.P4.reliability-run', '19.P4.reliability-battery')
    assert t.context == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase4_04.py')
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    scope = t.sections['Scope in / Scope out']
    for fact in (
        'BEGIN_REGISTRY_P4 through END_REGISTRY_P4', 'admissions[4:]', 'admissions[5:]',
        'Author only reliability-run and phase4-continue-05',
        'phase4-continue-04, reliability-battery, provider-cooldown-failover and outbox-only-admission',
        'successor depends on reliability-run', 'medium/medium', 'high/high',
        'seeding.max_seeds_per_admission', 'drain.max_ticket_minutes',
        'entry_unit_gap', 'resolve_plan_contract', 'kind: spec_gap', 'never copy unit text',
        'no uncited later entry', '19.P5', 'Owner, Records, Observable and Tests',
        'uv run pytest tests/test_reliability_battery.py tests/test_stages.py tests/test_merge.py',
        'uv run python -m eval.reliability_battery --out tickets/reliability-run/reliability-battery-report.json',
        'report stays uncommitted', 'No code, schema, registration or tests',
        'fresh all-green member-local evidence', 'source provenance', 'purge/current-report requirement',
        'checks-only custody', 'inherited-copy exclusion', 'empty code diff', 'exact producing-lift custody',
        'null-commit settlement and one retirement', 'already_satisfied is no substitute',
        '19.L rules 2-5', 'seam-owner closure', 'Context', 'On-demand',
        '300,000-character headroom', 'same-admission sibling creations', 'delimiter-bearing files',
        'Historical seeding snapshots remain immutable', 'authoring head', 'merged idiom blob',
        'file and ticket sizes', 'cited-unit lengths', 'fixed authoring snapshots',
        'never live sizes or live plan lengths', 'commit only the new batch test',
        'requisition_review', 'tickets/phase4-continue-04/checks.json', 'one ticket-plane seed lift',
        'Keep approved bytes while ticket_sha matches', 're-author only snagged seeds',
        'test_outbox_only_check_accepts_registered_report', 'test_outbox_only_check_requires_current_report',
        'test_outbox_only_merge_regate_requires_lift_custody',
        'test_outbox_only_admission_records_null_commit_and_retires'):
        assert fact in scope, fact
    assert all(name in scope for name in SUCCESSOR_TESTS)
    assert t.verification == (('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase4_04.py'),
                              ('uv', 'run', 'pytest', '-q'))


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
    assert AUTHORED['reliability-battery']['fenced_existing'] == ('chupa/artifacts.py', 'chupa/stages.py')
    assert AUTHORED['reliability-battery']['created'] == (
        'eval/reliability_battery.py', 'tests/test_reliability_battery.py')
    assert not set(a['context']) & {'tests/test_seeded_phase4_02.py', 'tests/test_seeded_phase4_03.py'}
