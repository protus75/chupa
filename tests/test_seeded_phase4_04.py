"""Phase 4 admission 04: fixed authoring snapshots, following the merged Phase 3 idiom.

Only ticket identity and grammar are read live; sizes, depth and max-effort
render evidence never follow later changes to the plan or owner files.
"""
import hashlib
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = '894ca92eb79662e26c196ef9b9dd22af94dfcb9a'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('reliability-run',)

BATCH = ('reliability-run', 'phase4-continue-05')

REGISTRY_ADMISSIONS = (('watchdog-event-stream', 'notify-transport'),
 ('watchdog-detector', 'watchdog-activation'),
 ('provider-cooldown-failover',),
 ('reliability-battery',),
 ('reliability-run',),
 ('phase4-exit',))

REGISTRY_STEMS = (
    'watchdog-event-stream', 'notify-transport', 'watchdog-detector', 'watchdog-activation',
    'provider-cooldown-failover', 'reliability-battery', 'reliability-run', 'phase4-exit',
)

VALIDATED_ROW_CITATIONS = {'reliability-run': (), 'phase4-exit': ()}
TERMINAL_ROW_EXIT = True
MEASURED_EFFORT = 'max'


REGISTRY_SHA256 = '7bbf15c3f90278afe1f30d975642f17e9d2e05765f4f049ce98e6991be10d2f0'

UNSEEDED_SUFFIX = (('phase4-exit',),)

EDGES = {'reliability-run': ('phase4-continue-04',
                     'reliability-battery',
                     'provider-cooldown-failover',
                     'outbox-only-admission'),
 'phase4-continue-05': ('reliability-run',)}

FENCE_FLOORS = {'reliability-run': ('tickets/reliability-run/reliability-battery-report.json',),
 'phase4-continue-05': ('tickets', 'tests/test_seeded_phase4_05.py')}

FENCE_ADDITIONS = {'reliability-run': (), 'phase4-continue-05': ()}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4775

RENDER_OVERHEAD = 2000

STANDING_CONTEXT = ()

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

PLAN_CHARS = {'19.I': 1811,
 '19.P4.reliability-run': 3372,
 '19.P4.reliability-battery': 6888,
 '19.L': 20912,
 '19.P4': 5641,
 '13': 19840,
 '19.P5': 9792}

FILE_CHARS = {'chupa/artifacts.py': 10656,
 'chupa/stages.py': 61220,
 'chupa/merge.py': 18346,
 'tickets/reliability-battery/ticket.md': 6341,
 'tickets/provider-cooldown-failover/ticket.md': 8343,
 'tickets/outbox-only-admission/ticket.md': 5831,
 'tests/test_seeded_phase3_core.py': 5425}

FILE_BYTES = {'chupa/artifacts.py': 10656,
 'chupa/stages.py': 61220,
 'chupa/merge.py': 18346,
 'tickets/reliability-battery/ticket.md': 6341,
 'tickets/provider-cooldown-failover/ticket.md': 8343,
 'tickets/outbox-only-admission/ticket.md': 5831,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'reliability-run': {'chars': 5151,
                     'bytes': 5151,
                     'plan': ('19.I', '19.P4.reliability-run', '19.P4.reliability-battery'),
                     'context': ('chupa/artifacts.py',
                                 'chupa/stages.py',
                                 'chupa/merge.py',
                                 'tickets/reliability-battery/ticket.md',
                                 'tickets/provider-cooldown-failover/ticket.md',
                                 'tickets/outbox-only-admission/ticket.md'),
                     'on_demand': (),
                     'fenced_existing': (),
                     'created': ('tickets/reliability-run/reliability-battery-report.json',),
                     'max_effort_render': 132886,
                     'birth_sha256': '6202f547d1aa7346c150abdb822a1c34ec1742ad61fb4e864f13919e5222aa63'},
 'phase4-continue-05': {'chars': 6000,
                        'bytes': 6000,
                        'plan': ('19.L', '19.I', '19.P4', '13', '19.P5'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase4_05.py'),
                        'max_effort_render': 74178,
                        'birth_sha256': '32fff4b43d25c33a7bb316aabacc38c90756e46fcbfe323f2aa45450492ff606'}}

VALIDATED_ENTRIES = {'19.P4.reliability-run': {'parts': ('Owner', 'Records', 'Observable', 'Tests'),
                           'sha256': 'e61ae1304153ff1c4befa66e17683b4a43a42139ad4d6ee0b80a770c2c4c5995',
                           'tests': ('test_reliability_battery_command_writes_only_on_green',
                                     'test_reliability_battery_requires_member_local_evidence',
                                     'test_reliability_battery_uses_registered_checks_lift',
                                     'test_outbox_only_check_accepts_registered_report',
                                     'test_outbox_only_check_requires_current_report',
                                     'test_outbox_only_merge_regate_requires_lift_custody',
                                     'test_outbox_only_admission_records_null_commit_and_retires')},
 '19.P4.reliability-battery': {'parts': ('Owner', 'Records', 'Observable', 'Tests'),
                               'sha256': '56474392be97ed18f13d7a1015b283783c5cb7c94d2e57efd7c4a81f4973d5e8',
                               'tests': ('test_reliability_battery_schema_is_closed',
                                         'test_reliability_battery_green_requires_observation_and_auditor',
                                         'test_reliability_battery_writer_validates_before_write',
                                         'test_reliability_battery_uses_registered_checks_lift',
                                         'test_classified_quota_exhaustion',
                                         'test_all_candidates_cooling_recovery',
                                         'test_unclassified_failure_preservation',
                                         'test_reliability_battery_requires_member_local_evidence',
                                         'test_reliability_battery_cleans_up_owned_lifetimes',
                                         'test_reliability_battery_command_writes_only_on_green',)}}

REQUIRED_ENTRIES = {'reliability-run': ('19.P4.reliability-run', '19.P4.reliability-battery'),
 'phase4-continue-05': ()}

DELIMITER_EXCLUDED = {'eval/reliability_battery.py': 23709}

COPY_REFUSAL_CHECKED = ('reliability-run', 'phase4-continue-05')

CLOSURE_SNAPSHOT = {'roots': ('chupa/', 'eval/', 'tests/'),
 'patterns': ('produce|write_report|ReliabilityBattery',
              'KNOWN_ARTIFACTS|lifted_report_paths|lift_outbox',
              '__all__|not hasattr|is_dormant|public.*allowlist',
              'ProviderLLM|ProviderSession|prepare_pipeline|build_daemon_core'),
 'paths': {'tickets/reliability-run/reliability-battery-report.json': 'registry floor: new '
                                                                      'canonical output; created',
           'tickets': 'seeder floor: new seeds only; existing tickets read-only',
           'tests/test_seeded_phase4_05.py': 'seeder floor: new batch snapshot test; created'},
 'decision': 'No code, public signature, constructor, composition, allowlist or negative assertion '
             'changes; no earned additions.'}


PRODUCER_TESTS = (
    'test_reliability_battery_command_writes_only_on_green',
    'test_reliability_battery_requires_member_local_evidence',
    'test_reliability_battery_uses_registered_checks_lift',
    'test_outbox_only_check_accepts_registered_report',
    'test_outbox_only_check_requires_current_report',
    'test_outbox_only_merge_regate_requires_lift_custody',
    'test_outbox_only_admission_records_null_commit_and_retires',
)
SUCCESSOR_TESTS = (
    'test_named_stems_cover_exactly_the_terminal_admission',
    'test_seed_passes_intake_lint_with_confirmed_seed_birth',
    'test_dependencies_as_authored',
    'test_stuck_budget_fits_the_drain_envelope',
    'test_fence_contains_its_floor_and_only_earned_additions',
    'test_exit_cites_next_phase_and_required_core_entries',
    'test_exit_reads_name_emitters_and_cover_transitive_dependencies',
    'test_context_closure_and_max_effort_render_use_authoring_snapshots',
)


def _birth(stem):
    # Lifecycle rejection does not change the authored identity.
    return (ROOT / ticket_path(stem)).read_text().replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _birth(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in dict.fromkeys(
                (*a['context'], *STANDING_CONTEXT, *extra))))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert PAYLOADS == ('reliability-run',)
    assert BATCH == ('reliability-run', 'phase4-continue-05')
    assert set(BATCH) == set(AUTHORED) == set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS)
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert REGISTRY_ADMISSIONS == (
        ('watchdog-event-stream', 'notify-transport'), ('watchdog-detector', 'watchdog-activation'),
        ('provider-cooldown-failover',), ('reliability-battery',), ('reliability-run',), ('phase4-exit',))
    assert REGISTRY_STEMS == tuple(s for admission in REGISTRY_ADMISSIONS for s in admission)
    assert REGISTRY_ADMISSIONS[4] == PAYLOADS
    assert UNSEEDED_SUFFIX == REGISTRY_ADMISSIONS[5:] == (('phase4-exit',),)
    assert TERMINAL_ROW_EXIT is True
    assert len(REGISTRY_SHA256) == 64


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = _ticket(stem).frontmatter
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
    assert EDGES == {
        'reliability-run': ('phase4-continue-04', 'reliability-battery',
                            'provider-cooldown-failover', 'outbox-only-admission'),
        'phase4-continue-05': ('reliability-run',)}
    assert not set(EDGES['reliability-run']) & set(BATCH)
    assert 'phase4-exit' not in set().union(*map(set, EDGES.values()))


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert t.scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS == dict.fromkeys(BATCH, ())
    assert FENCE_FLOORS['reliability-run'] == (
        'tickets/reliability-run/reliability-battery-report.json',)
    assert FENCE_FLOORS['phase4-continue-05'] == ('tickets', 'tests/test_seeded_phase4_05.py')
    assert set(CLOSURE_SNAPSHOT['paths']) == set().union(*map(set, FENCE_FLOORS.values()))
    assert all(reason.startswith(('registry floor:', 'seeder floor:'))
               for reason in CLOSURE_SNAPSHOT['paths'].values())
    assert CLOSURE_SNAPSHOT['roots'] == ('chupa/', 'eval/', 'tests/')
    assert len(CLOSURE_SNAPSHOT['patterns']) == 4
    assert 'no earned additions' in CLOSURE_SNAPSHOT['decision']
    assert 'no public signature, constructor, composition, allowlist or negative assertion changes' in (
        _ticket('reliability-run').sections['Scope in / Scope out'])


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket('reliability-run')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.I', '19.P4.reliability-run', '19.P4.reliability-battery')
    assert VALIDATED_ROW_CITATIONS == {'reliability-run': (), 'phase4-exit': ()}
    assert REQUIRED_ENTRIES[t.stem] == ('19.P4.reliability-run', '19.P4.reliability-battery')
    assert set(VALIDATED_ENTRIES) == set(REQUIRED_ENTRIES[t.stem])
    assert all(e['parts'] == ('Owner', 'Records', 'Observable', 'Tests')
               and len(e['sha256']) == 64 for e in VALIDATED_ENTRIES.values())
    assert VALIDATED_ENTRIES['19.P4.reliability-run']['tests'] == PRODUCER_TESTS
    assert VALIDATED_ENTRIES['19.P4.reliability-battery']['tests'] == (
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
    for fact in (*PRODUCER_TESTS,
        'Owner, Records, Observable and Tests', 'eval/reliability_battery.py owns the runner',
        'canonical writer', 'chupa/artifacts.py owns ReliabilityBatteryReport',
        'RELIABILITY_BATTERY_REPORT', 'chupa/stages.py owns checks lifting',
        'chupa/merge.py owns admission and retirement', 'no code, schema, registration or tests',
        'fresh all-green member-local evidence', 'classified_quota_exhaustion',
        'all_candidates_cooling_recovery', 'unclassified_failure_preservation', 'exact order',
        'observed value must match its fixed expected value', 'entire member-local journal',
        'producing_run', 'spec/source-HEAD provenance', 'closed report validation',
        'inherited schema-version policy', 'Missing, contradictory or cross-member observations',
        'supplied success/auditor verdicts', 'production fixture registry',
        'injected clock, sleep, process-exec and filesystem seams',
        'no live provider calls, config edits or wall waits', 'both Verification commands in order',
        'even if Implement sees existing output', 'already_satisfied is no substitute',
        'purge before Verification', 'current-report requirement', 'canonical UTF-8 JSON',
        'trailing newline', 'Leave the report uncommitted', 'no hand-copy, patch or Git-add',
        'ordinary registered OUTBOX checks lift', 'checks-only custody', 'inherited-copy exclusion',
        'Implement-only output', 'test-authored fixture reports', 'empty code diff',
        'no uncommitted code', 'exact producing-lift custody',
        'ticket-plane/reliability-run/<attempt>/checks', 'report path and ticket-plane commit',
        'schema-valid committed main blob', 'to: merged, commit: null and reviewed_sha',
        'one retirement', 'Failed output, Verification or lift cannot settle',
        'existing failure spine', 'no new records, signals, receipts, configuration, gates or lift paths'):
        assert fact in scope, fact
    assert t.verification == (
        ('uv', 'run', 'pytest', 'tests/test_reliability_battery.py', 'tests/test_stages.py', 'tests/test_merge.py'),
        ('uv', 'run', 'python', '-m', 'eval.reliability_battery', '--out',
         'tickets/reliability-run/reliability-battery-report.json'))
    preservation = {'tests/test_reliability_battery.py', 'tests/test_stages.py', 'tests/test_merge.py'}
    assert not preservation & (set(t.scope_fence) | set(t.context) | set(t.on_demand))


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket('phase4-continue-05')
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.L', '19.I', '19.P4', '13', '19.P5')
    assert REQUIRED_ENTRIES[t.stem] == ()  # terminal lookahead has no non-exit entry of its own
    assert t.context == ('tests/test_seeded_phase3_core.py',)
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    scope = t.sections['Scope in / Scope out']
    for fact in (*SUCCESSOR_TESTS,
        'BEGIN_REGISTRY_P4 through END_REGISTRY_P4', 'Position 05', 'admissions[5:]',
        'Author only phase4-exit', 'sole terminal payload, with no successor',
        'high/high', '19.L names phase exits KNOWN-HARD', 'seeding.max_seeds_per_admission',
        'drain.max_ticket_minutes', 'resolve_plan_contract', 'entry_unit_gap', 'kind: spec_gap',
        'never copy unit text', '19.P5', 'Validate that future entry depth in this owning pass',
        'Never inspect or seed beyond Phase 5', 'transitively cover every Phase 4 deliverable',
        'reliability-run and watchdog-activation', 'git squash trailers through git.py',
        'without invented verbs or approval-provenance cross-checks', 'committed reliability-run report',
        'ReliabilityBatteryReport', 'classified_quota_exhaustion', 'all_candidates_cooling_recovery',
        'unclassified_failure_preservation', 'member-local production observations and auditor evidence',
        'machinery/producer separation', 'engine-lane custody', 'fixture-written exit evidence',
        "watchdog-activation's committed passing checks.json",
        'test_production_soft_band_notifies_once_without_kill',
        'test_production_hard_timeout_group_kill_is_harvested',
        'soft-band notify intent/completion pair without auto-kill',
        'hard-timeout group kill and harvested output', 'production composition',
        'watchdog-detector/watchdog-activation as emitters',
        'committed artifacts or merged wired-and-shaped proofs', 'never live journal',
        'An unmet read returns premise_failed', 'dependency coverage and each read',
        'core-first admission plus its continuation', 'Phase 5 registry', 'avoid forward dependencies',
        '19.L rules 2-5', 'seam-owner closure', '300,000-character headroom', 'On-demand',
        'same-admission sibling creations', 'prompt specs and delimiter-bearing files',
        'Historical seeding snapshots remain immutable', 'authoring head', 'merged idiom blob',
        'file and ticket sizes and cited-unit lengths', 'fixed authoring snapshots',
        'never live sizes or live plan lengths', 'leave it uncommitted', 'commit only the new batch test',
        'requisition_review', 'tickets/phase4-continue-05/checks.json', 'one ticket-plane seed lift',
        'Keep approved bytes while ticket_sha matches', 're-author only snagged seeds'):
        assert fact in scope, fact
    assert t.verification == (('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase4_05.py'),
                              ('uv', 'run', 'pytest', '-q'))


@pytest.mark.parametrize('stem', BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(t.scope_fence) == set(a['created']) | set(a['fenced_existing'])
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert not set(a['context']) & set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert MEASURED_EFFORT == 'max'
    assert a['max_effort_render'] <= render_chars(a) <= HEADROOM_CHARS == 300_000
    assert a['bytes'] >= a['chars'] > 0
    assert all(PLAN_CHARS[pid] > 0 for pid in a['plan'])
    assert all(FILE_BYTES[path] >= FILE_CHARS[path] > 0 for path in a['context'])
    assert not set(a['context']) & set(DELIMITER_EXCLUDED)
    assert DELIMITER_EXCLUDED == {'eval/reliability_battery.py': 23709}
    assert 'Read eval/reliability_battery.py from disk' in _birth('reliability-run')
    assert all(not path.startswith('specs/') and path != 'CHUPA_PLAN.md' for path in a['context'])
    assert not set(a['context']) & {'tests/test_seeded_phase4_04.py', 'tests/test_seeded_phase4_05.py'}
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path
    assert a['fenced_existing'] == () and a['on_demand'] == () and STANDING_CONTEXT == ()
