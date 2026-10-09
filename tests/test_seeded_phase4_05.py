"""Terminal Phase 4 admission, using the merged Phase 3 seeding idiom.

Registry, depth, graph, evidence and render measurements are authoring snapshots.
Only ticket identity and grammar are read live, as in the merged idiom.
"""

import hashlib
from pathlib import Path

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = 'b5dc461d00a51a1c5e1fd57f3da2de91e612d518'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('phase4-exit',)

REGISTRY_ADMISSIONS = (('watchdog-event-stream', 'notify-transport'),
 ('watchdog-detector', 'watchdog-activation'),
 ('provider-cooldown-failover',),
 ('reliability-battery',),
 ('reliability-run',),
 ('phase4-exit',))

REGISTRY_STEMS = ('watchdog-event-stream',
 'notify-transport',
 'watchdog-detector',
 'watchdog-activation',
 'provider-cooldown-failover',
 'reliability-battery',
 'reliability-run',
 'phase4-exit')

UNSEEDED_SUFFIX = (('phase4-exit',),)

NEXT_REGISTRY_ADMISSIONS = (('retro-drain-invoker',),
 ('retro-box-activation',),
 ('scorecard-reporting',),
 ('status-projection', 'baseline-binding-reader'),
 ('retro-doctor-cli',),
 ('phase5-exit',))

NEXT_REGISTRY_STEMS = ('retro-drain-invoker',
 'retro-box-activation',
 'scorecard-reporting',
 'status-projection',
 'baseline-binding-reader',
 'retro-doctor-cli',
 'phase5-exit')

CORE_BATCH = ('retro-drain-invoker', 'phase5-continue')

CORE_EDGES = {'retro-drain-invoker': ('phase4-exit',), 'phase5-continue': ('retro-drain-invoker',)}

CORE_CITATIONS = {'retro-drain-invoker': ('19.I', '19.P5.retro-drain-invoker', '13', '14'),
 'phase5-continue': ('19.L', '19.I', '19.P5', '19.P5.retro-box-activation', '12', '13')}

CORE_DEEP = True

CONTINUATION_DEEP = True

EDGES = {'phase4-exit': ('phase4-continue-05',)}

PREDECESSOR_GRAPH = {'phase4-continue-05': ('reliability-run',),
 'reliability-run': ('phase4-continue-04',
                     'reliability-battery',
                     'provider-cooldown-failover',
                     'outbox-only-admission'),
 'provider-cooldown-failover': ('phase4-continue-02',),
 'phase4-continue-02': ('watchdog-detector', 'watchdog-activation'),
 'watchdog-activation': ('phase4-continue', 'watchdog-detector'),
 'watchdog-detector': ('phase4-continue',),
 'phase4-continue': ('watchdog-event-stream', 'notify-transport'),
 'notify-transport': ('phase3-exit', 'watchdog-event-stream'),
 'watchdog-event-stream': ('phase3-exit',),
 'reliability-battery': ('phase4-continue-03',),
 'phase4-continue-03': ('provider-cooldown-failover',),
 'phase4-continue-04': ('reliability-battery',)}

FENCE_FLOOR = ('tickets', 'tests/test_phase4_exit.py', 'tests/test_seeded_phase5_core.py')

FENCE_ADDITIONS = ()

CLOSURE_REASONS = {'tickets': 'registry floor: new seeds only; existing tickets and evidence read-only',
 'tests/test_phase4_exit.py': 'registry floor: new exit reads; no production or predecessor '
                              'assertion changes',
 'tests/test_seeded_phase5_core.py': 'registry floor: new next-phase authoring snapshots'}

CLOSURE_PATTERNS = ('storm_producer|Box\\(|Driver\\(|def run',
 'not hasattr|is_dormant|__all__',
 'KNOWN_ARTIFACTS|RELIABILITY_BATTERY_REPORT|produce|write_report')

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4775

RENDER_OVERHEAD = 2000

STANDING_CONTEXT = ()

PLAN_CHARS = {'19.L': 20912,
 '19.I': 1811,
 '19.P4': 5641,
 '13': 19840,
 '19.P5': 9792,
 '19.P5.retro-drain-invoker': 8511,
 '14': 7360,
 '19.P5.retro-box-activation': 9207,
 '12': 20224}

FILE_CHARS = {'chupa/artifacts.py': 10656,
 'chupa/git.py': 6640,
 'chupa/seams.py': 10148,
 'chupa/effects.py': 3229,
 'chupa/runner.py': 38439,
 'chupa/drain.py': 33646,
 'chupa/__main__.py': 15669,
 'tests/test_seeded_phase3_core.py': 5425,
 'tickets/reliability-run/reliability-battery-report.json': 1100,
 'tickets/watchdog-activation/checks.json': 9085}

FILE_BYTES = {'chupa/artifacts.py': 10656,
 'chupa/git.py': 6640,
 'chupa/seams.py': 10148,
 'chupa/effects.py': 3229,
 'chupa/runner.py': 38439,
 'chupa/drain.py': 33646,
 'chupa/__main__.py': 15669,
 'tests/test_seeded_phase3_core.py': 5425,
 'tickets/reliability-run/reliability-battery-report.json': 1100,
 'tickets/watchdog-activation/checks.json': 9085}

AUTHORED = {'chars': 11513,
 'bytes': 11513,
 'birth_sha256': '4b82fc1c00738cdad4292a4664c4fd6abe04ad844d0f844d4edc74bf732aef3c',
 'plan': ('19.L',
          '19.I',
          '19.P4',
          '13',
          '19.P5',
          '19.P5.retro-drain-invoker',
          '14',
          '19.P5.retro-box-activation',
          '12'),
 'context': ('chupa/artifacts.py',
             'chupa/git.py',
             'chupa/seams.py',
             'chupa/effects.py',
             'chupa/runner.py',
             'chupa/drain.py',
             'chupa/__main__.py',
             'tests/test_seeded_phase3_core.py',
             'tickets/reliability-run/reliability-battery-report.json',
             'tickets/watchdog-activation/checks.json'),
 'on_demand': (),
 'fenced_existing': (),
 'created': ('tickets', 'tests/test_phase4_exit.py', 'tests/test_seeded_phase5_core.py'),
 'actual_max_effort_render': 253868,
 'max_effort_render': 255623}

REQUIRED_ENTRIES = ('19.P5.retro-drain-invoker', '19.P5.retro-box-activation')

VALIDATED_ENTRIES = {'19.P5.retro-drain-invoker': {'parts': ('Owner', 'Records', 'Observable', 'Tests'),
                               'sha256': '7aa99a8519197a8444aa4360294e74daed86af7ebf0443fcceb9d5ce750c2b91',
                               'tests': ('test_window_uses_completed_report_boundary',
                                         'test_retro_trigger_boundaries',
                                         'test_report_commit_replays_without_advancing_unfinished_window',
                                         'test_failed_retro_suppresses_window_until_completion',
                                         'test_retro_hook_is_default_off',
                                         'test_drain_retro_due_quiescence_and_pre_exit',
                                         'test_retro_driver_access_is_public_and_read_only',
                                         'test_exit_read_window_materialization')},
 '19.P5.retro-box-activation': {'parts': ('Owner', 'Records', 'Observable', 'Tests'),
                                'sha256': 'b750a8a519396f98a597a3fa040803ea113f537b35b431b8ae61944bf9789251',
                                'tests': ('test_completed_retro_proposals_reach_prompt_spec_merge',
                                          'test_tombstone_rereports_reopen_at_threshold',
                                          'test_tombstone_reopen_requires_journal_callback',
                                          'test_reopened_message_bypasses_its_tombstone',
                                          'test_reopened_retro_ticket_starts_draft',
                                          'test_standing_go_uses_the_table_and_each_override_drafts',
                                          'test_retro_prompt_spec_merge_requires_unique_bridge',
                                          'test_production_boxes_receive_rereport_callback',
                                          'test_retro_itemizes_confirmed_class_tombstones',
                                          'test_status_surfaces_confirmed_class_tombstones',
                                          'test_tombstone_visibility_uses_message_class')}}

EXIT_EVIDENCE = {'report_sha256': 'ddc38d6ca8a2913be456d60a6e88142669f99570171047bc2f98cf8e886e3553',
 'checks_sha256': '923f5b2d8c1fb9443c991e506a71a9674e10077a00ff814a06eb6e46b3beab52',
 'checks_passed': True,
 'checks_bypassed': (),
 'checks_reports': (('scope_fence', 'pass'),
                    ('verification', 'pass'),
                    ('run_record', 'pass'),
                    ('diff_budget', 'pass')),
 'checks_verification': ((('uv',
                           'run',
                           'pytest',
                           'tests/test_watchdog.py',
                           'tests/test_watchdog_activation.py',
                           'tests/test_daemon_composition.py',
                           'tests/test_notify.py'),
                          0),
                         (('uv',
                           'run',
                           'pytest',
                           'tests/test_driver.py',
                           'tests/test_echo_stage.py',
                           'tests/test_kill_executor_abort.py',
                           'tests/test_kill_failure_suppression.py',
                           'tests/test_llm_effect.py',
                           'tests/test_providers.py',
                           'tests/test_requisition.py',
                           'tests/test_serve.py'),
                          0),
                         (('uv',
                           'run',
                           'pytest',
                           'tests/test_drain.py',
                           'tests/test_stages.py',
                           'tests/test_merge.py',
                           'tests/test_mergequeue.py',
                           'tests/test_seed_path.py',
                           'tests/test_eval_harness.py',
                           'tests/test_diagnose_eval.py',
                           'tests/test_storm_notification_activation.py',
                           'tests/test_effects.py',
                           'tests/test_notify.py'),
                          0),
                         (('uv',
                           'run',
                           'pytest',
                           'tests/test_shakeout.py',
                           'tests/test_daemon_soak.py',
                           'tests/test_daemon_soak_runner.py'),
                          0)),
 'merged_code_trailers': ('notify-transport',
                          'provider-cooldown-failover',
                          'reliability-battery',
                          'watchdog-activation',
                          'watchdog-detector',
                          'watchdog-event-stream'),
 'no_code_producer': 'reliability-run',
 'member_observations': (('classified_quota_exhaustion',
                          'quota_classified_cooldown_persisted',
                          'quota_classified_cooldown_persisted',
                          'quota-fault/0',
                          (),
                          True),
                         ('all_candidates_cooling_recovery',
                          'all_cooling_held_timer_fired_recovered',
                          'all_cooling_held_timer_fired_recovered',
                          'cooling-fault/0',
                          (),
                          True),
                         ('unclassified_failure_preservation',
                          'unknown_failure_unclassified',
                          'unknown_failure_unclassified',
                          'unknown-fault/0',
                          (),
                          True)),
 'source_sha': '079cac90c2244daa6a136c22f66ac12ee194b4a4',
 'spec_version': 1}

PRODUCTION_PROOFS = {'test_production_soft_band_notifies_once_without_kill': {'path': 'tests/test_watchdog_activation.py',
                                                          'sha256': 'f59227e4c1f925c3bf94953ade14706c7643d2518b9e25a820086eea2cafac2c',
                                                          'assertions': ("assert kwargs['cwd'] "
                                                                         '== tmp_path',
                                                                         "assert 'CLAUDE_KEY' "
                                                                         "not in kwargs['env'] "
                                                                         "and 'CODEX_KEY' not in "
                                                                         "kwargs['env']",
                                                                         'assert result.outcome '
                                                                         "== 'ok' and "
                                                                         'result.cost.attempts '
                                                                         '== 3',
                                                                         'assert batch[0] is '
                                                                         'batch[1] is batch[2] '
                                                                         'and batch[0].warned',
                                                                         'assert keys == '
                                                                         "[f'notify/work/spiral-warning/{seq}'] "
                                                                         '* 2',
                                                                         'assert '
                                                                         'batch[0].progress_epoch '
                                                                         '== 1',
                                                                         'assert '
                                                                         'repeated.cost.usd == '
                                                                         'result.cost.usd and '
                                                                         'repeated.cost.provider '
                                                                         '== '
                                                                         'result.cost.provider',
                                                                         'assert '
                                                                         'ctx.driver.detector is '
                                                                         'batch[0]',
                                                                         'assert len(deliveries) '
                                                                         '== seq + 1',
                                                                         'assert detectors[0] is '
                                                                         'not detectors[3] and '
                                                                         'len(deliveries) == 2 '
                                                                         'and killed == []',
                                                                         'assert [e.type for e '
                                                                         'in events] == '
                                                                         '[EventType.EFFECT_INTENT, '
                                                                         'EventType.EFFECT_COMPLETION]',
                                                                         'assert not '
                                                                         "any('stuck-past-threshold' "
                                                                         "in (e.key or '') for e "
                                                                         'in '
                                                                         'rig.journal.read())')},
 'test_production_hard_timeout_group_kill_is_harvested': {'path': 'tests/test_watchdog_activation.py',
                                                          'sha256': '8a3b217c687c4869eea41b8062036c3241482beb331aae3567dec5703f83f346',
                                                          'assertions': ('assert '
                                                                         "kwargs.get('on_stdout_line') "
                                                                         'is not None',
                                                                         'assert '
                                                                         "data['terminal'] == "
                                                                         "'timeout' and "
                                                                         "data['stage'] == "
                                                                         "'implement'",
                                                                         'assert trace[0] == '
                                                                         "'group-kill' and "
                                                                         "trace[-1] == 'reaped'",
                                                                         'assert await '
                                                                         'rig.checkout.git._run(root, '
                                                                         "'show', "
                                                                         "'HEAD:tickets/work/attempts/0/harvest.json') "
                                                                         '== harvest.read_text()',
                                                                         'assert terminals(rig, '
                                                                         "'work')[-1].body['to'] "
                                                                         "== 'timeout'",
                                                                         'assert '
                                                                         'ctx.driver.llm._exec '
                                                                         'is ctx.exec_ is '
                                                                         'rig.exec',
                                                                         'assert '
                                                                         'ctx.driver.detector.call.tools '
                                                                         "== {'tool'}",
                                                                         'assert await '
                                                                         'asyncio.wait_for(reader.read(), '
                                                                         "5) == b''",
                                                                         'assert not '
                                                                         'marker.exists() and '
                                                                         'not '
                                                                         "ctx.worktree('work').exists()",
                                                                         'assert '
                                                                         'ctx.driver._active is '
                                                                         'None and '
                                                                         'ctx.driver.llm._active '
                                                                         'is None',
                                                                         'assert not '
                                                                         "list(ctx.config.state_dir.glob('spools/work/**/output.txt'))")}}

COPY_REFUSAL_CHECKED = True


def _birth():
    return (ROOT / ticket_path('phase4-exit')).read_text().replace(
        'state: rejected', 'state: confirmed', 1)


def _ticket():
    return validate_ticket('phase4-exit', _birth(), ROOT, BATCH)


def render_chars(extra=()):
    # Sizes are permanent fixtures. Effort adds no second render bound.
    return (IMPLEMENT_SPEC_CHARS + AUTHORED['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in AUTHORED['plan'])
            + sum(FILE_CHARS[path] for path in dict.fromkeys(
                (*AUTHORED['context'], *STANDING_CONTEXT, *extra))))


def test_named_stems_cover_exactly_the_terminal_admission():
    assert BATCH == ('phase4-exit',) == REGISTRY_ADMISSIONS[5]
    assert UNSEEDED_SUFFIX == REGISTRY_ADMISSIONS[5:] == (BATCH,)
    assert REGISTRY_STEMS == tuple(s for admission in REGISTRY_ADMISSIONS for s in admission)
    assert REGISTRY_ADMISSIONS == (
        ('watchdog-event-stream', 'notify-transport'),
        ('watchdog-detector', 'watchdog-activation'),
        ('provider-cooldown-failover',), ('reliability-battery',), ('reliability-run',),
        ('phase4-exit',))
    assert set(EDGES) == set(BATCH)
    assert len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert len(CORE_BATCH) <= MAX_SEEDS_PER_ADMISSION
    assert CORE_BATCH == ('retro-drain-invoker', 'phase5-continue')
    assert NEXT_REGISTRY_ADMISSIONS == (
        ('retro-drain-invoker',), ('retro-box-activation',), ('scorecard-reporting',),
        ('status-projection', 'baseline-binding-reader'), ('retro-doctor-cli',), ('phase5-exit',))
    assert NEXT_REGISTRY_STEMS == tuple(s for a in NEXT_REGISTRY_ADMISSIONS for s in a)


def test_seed_passes_intake_lint_with_confirmed_seed_birth():
    fm = _ticket().frontmatter
    assert (fm.source, fm.state, fm.priority, fm.kind) == ('seed', 'confirmed', 'P1', 'feature')
    assert (fm.agent_tier, fm.agent_effort) == ('high', 'high')
    assert fm.gate_bypass == []
    assert hashlib.sha256(_birth().encode()).hexdigest() == AUTHORED['birth_sha256']
    assert COPY_REFUSAL_CHECKED is True
    assert '19.L names phase exits KNOWN-HARD' in _ticket().sections['Scope in / Scope out']


def test_dependencies_as_authored():
    assert _ticket().depends == EDGES['phase4-exit'] == ('phase4-continue-05',)
    assert CORE_EDGES == {
        'retro-drain-invoker': ('phase4-exit',), 'phase5-continue': ('retro-drain-invoker',)}
    assert not set(CORE_BATCH) & set(_ticket().depends)


def test_stuck_budget_fits_the_drain_envelope():
    t = _ticket()
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)
    assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180
    scope = t.sections['Scope in / Scope out']
    assert 'both stuck budgets at drain.max_ticket_minutes' in scope
    assert 'seeding.max_seeds_per_admission' in scope


def test_fence_contains_its_floor_and_only_earned_additions():
    assert _ticket().scope_fence == (*FENCE_FLOOR, *FENCE_ADDITIONS)
    assert FENCE_FLOOR == ('tickets', 'tests/test_phase4_exit.py', 'tests/test_seeded_phase5_core.py')
    assert FENCE_ADDITIONS == ()
    assert set(CLOSURE_REASONS) == set(FENCE_FLOOR)
    assert all(reason.startswith('registry floor:') for reason in CLOSURE_REASONS.values())
    assert CLOSURE_PATTERNS == (
        'storm_producer|Box\\(|Driver\\(|def run', 'not hasattr|is_dormant|__all__',
        'KNOWN_ARTIFACTS|RELIABILITY_BATTERY_REPORT|produce|write_report')
    scope = _ticket().sections['Scope in / Scope out']
    for fact in ('19.L rules 2-5', 'cited seam-owner closure', 'chupa/journal.py',
                 'forced assertion migration', 'non-firing reason', 'historical seeding snapshots',
                 'Commit only the two new tests', 'leave them uncommitted',
                 'requisition_review', 'tickets/phase4-exit/checks.json',
                 'one ticket-plane seed lift', 'Retain approved bytes while ticket_sha matches',
                 're-author only snagged seeds'):
        assert fact in scope, fact


def test_exit_cites_next_phase_and_required_core_entries():
    t = _ticket()
    assert t.plan_contract == AUTHORED['plan'] == (
        '19.L', '19.I', '19.P4', '13', '19.P5', '19.P5.retro-drain-invoker',
        '14', '19.P5.retro-box-activation', '12')
    assert REQUIRED_ENTRIES == ('19.P5.retro-drain-invoker', '19.P5.retro-box-activation')
    assert set(VALIDATED_ENTRIES) == set(REQUIRED_ENTRIES)
    for entry in VALIDATED_ENTRIES.values():
        assert entry['parts'] == ('Owner', 'Records', 'Observable', 'Tests')
        assert len(entry['sha256']) == 64 and entry['tests']
    assert VALIDATED_ENTRIES['19.P5.retro-drain-invoker']['tests'] == (
        'test_window_uses_completed_report_boundary', 'test_retro_trigger_boundaries',
        'test_report_commit_replays_without_advancing_unfinished_window',
        'test_failed_retro_suppresses_window_until_completion', 'test_retro_hook_is_default_off',
        'test_drain_retro_due_quiescence_and_pre_exit', 'test_retro_driver_access_is_public_and_read_only',
        'test_exit_read_window_materialization')
    assert VALIDATED_ENTRIES['19.P5.retro-box-activation']['tests'] == (
        'test_completed_retro_proposals_reach_prompt_spec_merge',
        'test_tombstone_rereports_reopen_at_threshold', 'test_tombstone_reopen_requires_journal_callback',
        'test_reopened_message_bypasses_its_tombstone', 'test_reopened_retro_ticket_starts_draft',
        'test_standing_go_uses_the_table_and_each_override_drafts',
        'test_retro_prompt_spec_merge_requires_unique_bridge',
        'test_production_boxes_receive_rereport_callback',
        'test_retro_itemizes_confirmed_class_tombstones',
        'test_status_surfaces_confirmed_class_tombstones', 'test_tombstone_visibility_uses_message_class')
    assert CORE_CITATIONS == {
        'retro-drain-invoker': ('19.I', '19.P5.retro-drain-invoker', '13', '14'),
        'phase5-continue': ('19.L', '19.I', '19.P5', '19.P5.retro-box-activation', '12', '13')}
    assert CORE_DEEP is CONTINUATION_DEEP is True
    scope = t.sections['Scope in / Scope out']
    for fact in ('BEGIN_REGISTRY_P5 through END_REGISTRY_P5',
                 'Author only retro-drain-invoker and phase5-continue',
                 'retro-drain-invoker depends on phase4-exit', 'starts high/high',
                 'phase5-continue starts medium/medium, depends on retro-drain-invoker',
                 'position 01 and admissions[1:]', 'shrinking suffix',
                 'never inspect or seed beyond Phase 5', 'without forward dependencies',
                 'tests/test_seeded_phase5_01.py', 'tests/test_seeded_phase3_core.py',
                 'chupa/retro.py', 'specs/retro.md', 'Exit-read window',
                 'resolve_plan_contract', 'entry_unit_gap', 'required_units',
                 'Validate the continuation\'s future entry depth in this pass',
                 'Missing or contradictory facts return premise_failed, kind: spec_gap',
                 'preserve all its named test obligations', 'never copy their text',
                 'Read owners and predecessors', 'read the battery runner from disk',
                 're-entry, upgrade, kill, storm, restart, provider, watchdog, pause and control'):
        assert fact in scope, fact
    assert CORE_BATCH[0] == NEXT_REGISTRY_ADMISSIONS[0][0]
    assert len(NEXT_REGISTRY_ADMISSIONS[1:]) == 5


def test_exit_reads_name_emitters_and_cover_transitive_dependencies():
    reached, pending = set(), list(EDGES['phase4-exit'])
    while pending:
        stem = pending.pop()
        if stem not in reached:
            reached.add(stem)
            pending.extend(PREDECESSOR_GRAPH.get(stem, ()))
    deliverables = set(REGISTRY_STEMS) - {'phase4-exit'}
    assert deliverables <= reached
    assert {'reliability-run', 'watchdog-activation'} <= reached
    assert set(EXIT_EVIDENCE['merged_code_trailers']) == deliverables - {'reliability-run'}
    assert EXIT_EVIDENCE['no_code_producer'] == 'reliability-run'
    observations = EXIT_EVIDENCE['member_observations']
    assert tuple(e[0] for e in observations) == (
        'classified_quota_exhaustion', 'all_candidates_cooling_recovery',
        'unclassified_failure_preservation')
    assert all(expected == observed and run and not auditor and green
               for _, expected, observed, run, auditor, green in observations)
    assert len(EXIT_EVIDENCE['source_sha']) == 40 and EXIT_EVIDENCE['spec_version'] == 1
    assert EXIT_EVIDENCE['checks_passed'] is True
    assert 'verification' not in EXIT_EVIDENCE['checks_bypassed']
    assert ('verification', 'pass') in EXIT_EVIDENCE['checks_reports']
    assert any('tests/test_watchdog_activation.py' in argv and rc == 0
               for argv, rc in EXIT_EVIDENCE['checks_verification'])
    assert set(PRODUCTION_PROOFS) == {
        'test_production_soft_band_notifies_once_without_kill',
        'test_production_hard_timeout_group_kill_is_harvested'}
    for proof in PRODUCTION_PROOFS.values():
        assert proof['path'] == 'tests/test_watchdog_activation.py'
        assert len(proof['sha256']) == 64 and proof['assertions']
    soft = '\n'.join(PRODUCTION_PROOFS['test_production_soft_band_notifies_once_without_kill']['assertions'])
    hard = '\n'.join(PRODUCTION_PROOFS['test_production_hard_timeout_group_kill_is_harvested']['assertions'])
    assert 'killed == []' in soft and 'EventType.EFFECT_INTENT, EventType.EFFECT_COMPLETION' in soft
    assert "trace[0] == 'group-kill'" in hard and "data['terminal'] == 'timeout'" in hard
    assert 'HEAD:tickets/work/attempts/0/harvest.json' in hard
    t = _ticket()
    scope, criteria = t.sections['Scope in / Scope out'], t.sections['Acceptance criteria']
    for test in ('test_phase4_exit_dependency_coverage',
                 'test_phase4_exit_reads_committed_reliability_report',
                 'test_phase4_exit_reads_committed_soft_band_check',
                 'test_phase4_exit_reads_committed_hard_timeout_check'):
        assert test in scope and test in criteria
    for fact in ('ReliabilityBatteryReport', 'RELIABILITY_BATTERY_REPORT',
                 'reliability-battery/reliability-run', 'watchdog-detector/watchdog-activation'):
        assert fact in scope or fact in criteria
    for fact in ('chupa/artifacts.py', 'registration in chupa/stages.py',
                 "eval/reliability_battery.py's canonical writer and production runner",
                 'member-local auditor', 'multi-candidate fixture registry',
                 'engine-lane custody', 'checks-only registered report lifting',
                 'null code commit', 'no code squash trailer', 'chupa-ticket',
                 'do not invent Git methods or cross-check approval provenance',
                 'read live journal', 'never claim that checks.json stores per-test results',
                 'without auto-kill', 'committed harvested output',
                 'returns premise_failed naming the read'):
        assert fact in scope, fact
    assert t.verification == (
        ('uv', 'run', 'pytest', '-q', 'tests/test_phase4_exit.py'),
        ('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase5_core.py'),
        ('uv', 'run', 'pytest', '-q',
         'tests/test_watchdog_activation.py::test_production_soft_band_notifies_once_without_kill',
         'tests/test_watchdog_activation.py::test_production_hard_timeout_group_kill_is_harvested'),
        ('uv', 'run', 'pytest', '-q', 'tests/test_reliability_battery.py',
         'tests/test_stages.py', 'tests/test_merge.py'),
        ('uv', 'run', 'pytest', '-q'))
    preservation = {'tests/test_watchdog_activation.py', 'tests/test_reliability_battery.py',
                    'tests/test_stages.py', 'tests/test_merge.py'}
    assert not preservation & (set(t.scope_fence) | set(t.context) | set(t.on_demand))


def test_context_closure_and_max_effort_render_use_authoring_snapshots():
    t, a = _ticket(), AUTHORED
    assert t.context == a['context'] and t.on_demand == a['on_demand'] == ()
    assert set(t.scope_fence) == set(a['created']) | set(a['fenced_existing'])
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert set(FILE_CHARS) == set(FILE_BYTES) == set(a['context'])
    assert set(PLAN_CHARS) == set(a['plan'])
    assert STANDING_CONTEXT == ()
    assert all(FILE_BYTES[p] >= FILE_CHARS[p] > 0 for p in FILE_CHARS)
    assert a['bytes'] >= a['chars'] > 0
    assert render_chars() == a['max_effort_render'] == 255623
    assert a['actual_max_effort_render'] == 253868 <= render_chars() <= HEADROOM_CHARS == 300000
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    assert 'tests/test_seeded_phase3_core.py' in t.context
    assert not any(path.startswith('specs/') for path in t.context)
    for path in a['on_demand']:
        assert render_chars((path,)) > HEADROOM_CHARS, path
    scope = t.sections['Scope in / Scope out']
    for fact in ('Created paths, same-admission sibling creations, prompt specs and delimiter-bearing files',
                 'maximum-effort renders solely from fixed authoring snapshots',
                 'never live sizes or plan lengths', 'authoring head, idiom blob, file/ticket sizes',
                 'On-demand is earned only by measured overflow'):
        assert fact in scope, fact
