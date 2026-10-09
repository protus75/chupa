"""Phase 5 core authoring measurements, frozen at the authoring head.

Only the authored tickets' grammar/identity is read live, following the merged Phase 3 idiom.
Registry, spec depth, closure scans and maximum-effort arithmetic are fixed snapshots.
"""

from pathlib import Path
import re

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]

AUTHORING_HEAD = '85378a89d04ec26408577a89edf7e6f727f57f29'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('retro-drain-invoker', 'phase5-continue')

REGISTRY = {'phase': 5,
 'admissions': [['retro-drain-invoker'],
                ['retro-box-activation'],
                ['scorecard-reporting'],
                ['status-projection', 'baseline-binding-reader'],
                ['retro-doctor-cli'],
                ['phase5-exit']],
 'seeds': {'retro-drain-invoker': {'deep': True,
                                   'cite': [13, 14],
                                   'fence': ['chupa/retro.py',
                                             'specs/retro.md',
                                             'tests/test_retro.py',
                                             'chupa/drain.py',
                                             'chupa/driver.py',
                                             'chupa/stages.py',
                                             'chupa/__main__.py',
                                             'chupa/box.py',
                                             'tests/test_drain.py',
                                             'tests/test_driver.py',
                                             'tests/test_stages.py',
                                             'tests/test_box.py'],
                                   'does': 'INVOKER contract plus the sections 13/19 Exit-read window '
                                           'renderer resolution and driver materialization on the same '
                                           'window-projection seam. Transition-risk preservation: every '
                                           'suite reaching `main(["drain"])` through to a merge (re-entry, '
                                           'upgrade, kill, storm, restart, provider, watchdog, pause, '
                                           'control) migrates only an assertion its scenario actually '
                                           'forces, else stays unchanged with the non-firing reason recorded '
                                           'in the seeding test.'},
           'retro-box-activation': {'deep': True,
                                    'cite': [12],
                                    'depends': ['retro-drain-invoker'],
                                    'fence': ['chupa/retro.py',
                                              'chupa/box.py',
                                              'chupa/merge.py',
                                              'chupa/author.py',
                                              'chupa/triage.py',
                                              'chupa/policy.py',
                                              'chupa/stages.py',
                                              'chupa/runner.py',
                                              'chupa/daemon.py',
                                              'chupa/drain.py',
                                              'chupa/serve.py',
                                              'chupa/status.py',
                                              'chupa/__main__.py',
                                              'tests/test_box.py',
                                              'tests/test_merge.py',
                                              'tests/test_author.py',
                                              'tests/test_triage.py',
                                              'tests/test_policy.py',
                                              'tests/test_stages.py',
                                              'tests/test_daemon_composition.py',
                                              'tests/test_drain.py',
                                              'tests/test_serve.py',
                                              'tests/test_retro_box.py'],
                                    'does': 'RETRO -> BOX contract; every production Box constructor with '
                                            'journal access receives the journal-backed rereport callback.'},
           'scorecard-reporting': {'cite': [14],
                                   'fence': ['chupa/scorecard.py',
                                             'tests/test_scorecard.py',
                                             'chupa/retro.py',
                                             'tests/test_retro.py'],
                                   'does': 'SCORECARD contract; tests/test_retro.py assertions are preserved '
                                           'unchanged.'},
           'status-projection': {'cite': [13],
                                 'depends': ['scorecard-reporting', 'retro-box-activation'],
                                 'fence': ['chupa/status.py',
                                           'tests/test_status.py',
                                           'chupa/scorecard.py',
                                           'tests/test_scorecard.py',
                                           'chupa/box.py',
                                           'tests/test_box.py',
                                           'chupa/retro.py',
                                           'tests/test_retro.py',
                                           'chupa/__main__.py',
                                           'tests/test_cli.py'],
                                 'does': 'STATUS contract.'},
           'baseline-binding-reader': {'cite': [12],
                                       'depends': ['retro-box-activation'],
                                       'fence': ['chupa/baseline.py',
                                                 'tests/test_baseline.py',
                                                 'chupa/journal.py',
                                                 'chupa/config.py',
                                                 'chupa/policy.py',
                                                 'tests/test_policy.py',
                                                 'chupa/author.py',
                                                 'tests/test_author.py',
                                                 'tests/test_retro_box.py'],
                                       'does': 'BINDING READER contract, migrating any interim go-binding '
                                               'helper into the one reader.'},
           'retro-doctor-cli': {'cite': [18],
                                'fence': ['chupa/doctor.py',
                                          'tests/test_doctor.py',
                                          'chupa/retro.py',
                                          'chupa/__main__.py',
                                          'tests/test_retro.py',
                                          'tests/test_cli.py'],
                                'does': 'VERBS contract.'},
           'phase5-exit': {'exit': True,
                           'fence': ['tickets',
                                     'tests/test_phase5_exit.py',
                                     'tests/test_seeded_phase6_core.py'],
                           'does': 'Exit reads above; authors the 19.P6 core.'}}}

POSITION = 1

UNSEEDED_SUFFIX = (('retro-box-activation',),
 ('scorecard-reporting',),
 ('status-projection', 'baseline-binding-reader'),
 ('retro-doctor-cli',),
 ('phase5-exit',))

EDGES = {'retro-drain-invoker': ('phase4-exit',), 'phase5-continue': ('retro-drain-invoker',)}

FENCE_FLOORS = {'retro-drain-invoker': ('chupa/retro.py',
                         'specs/retro.md',
                         'tests/test_retro.py',
                         'chupa/drain.py',
                         'chupa/driver.py',
                         'chupa/stages.py',
                         'chupa/__main__.py',
                         'chupa/box.py',
                         'tests/test_drain.py',
                         'tests/test_driver.py',
                         'tests/test_stages.py',
                         'tests/test_box.py'),
 'phase5-continue': ('tickets', 'tests/test_seeded_phase5_01.py')}

FENCE_ADDITIONS = {'retro-drain-invoker': {'chupa/runner.py': '19.L rule 5 and entry owner closure: pipeline/PreparedDispatch, '
                                            'prepare_pipeline and bind carry the stages owner and shared '
                                            'Driver to the CLI hook without private ctx traversal; preserve '
                                            'callable and constructor signatures.',
                         'chupa/daemon.py': '19.L rule 5: runner.bind returns TicketWriter at daemon.py:438; '
                                            'expose the composed stages owner without changing admission, '
                                            'suspension or abort behavior.',
                         'chupa/journal.py': 'Entry closed-vocabulary closure: SIGNAL_NAMES must admit the '
                                             'retro-owned retro_failed signal, with its suppression '
                                             'consumer.',
                         'tests/test_vocabularies.py': '19.L rule 5: test_every_engine_signal_name_is_listed '
                                                       'pins equality of scanned writers and SIGNAL_NAMES; '
                                                       'include retro_failed writer/consumer and preserve '
                                                       'refusal of unknown names.',
                         'tests/test_cli.py': '19.L rules 2/5: shared Stages.__call__ fixture lacks public '
                                              'driver access for forced quiescence after its merged '
                                              'terminal; migrate the fixture through the public composition '
                                              'with scripted retro output, retaining calls and lock '
                                              'assertions.',
                         'tests/test_drain_upgrade.py': '19.L rules 2/5: Script emits real docs merges; '
                                                        'child quiescence forces retro, invalidating '
                                                        'missing-Driver fixture and HEAD~1 handoff-commit '
                                                        'assumption in '
                                                        'test_a_self_upgrading_admission_hands_off_before_the_next_dispatch. '
                                                        'Pin the journaled admission SHA rather than commit '
                                                        'offsets and supply the public scripted Driver.',
                         'tests/test_seed_successor.py': '19.L rules 2/5: two work/ merges reach quiescence; '
                                                         'test_merged_parent_registers_and_runs_successor_in_same_drain '
                                                         'pins exactly five model calls and main equal to '
                                                         'last squash. Add the forced retro call/report '
                                                         'commit and public stages access while retaining '
                                                         'seed lift/dependency assertions.',
                         'tests/test_daemon_config.py': '19.L rules 2/5: test_config_snapshot_is_dormant '
                                                        'supplies a bare dispatch which reports merged; '
                                                        'migrate only the missing-stage-owner fixture at '
                                                        'forced quiescence, preserving snapshot and daemon '
                                                        'dormancy probes.',
                         'tests/test_daemon_admission.py': '19.L rules 2/5: test_daemon_admission_is_dormant '
                                                           'supplies a bare merged dispatch; provide the '
                                                           'public scripted stages carrier at quiescence, '
                                                           'preserving the daemon-construction/dispatch '
                                                           'refusal probes.',
                         'tests/test_daemon_pause.py': '19.L rules 2/5: '
                                                       'test_dispatch_pause_boundary_is_active reports '
                                                       'merged through its custom Script; carry the public '
                                                       'Driver for forced quiescence, preserving '
                                                       'control-consumption and dispatch-count assertions.',
                         'tests/test_reconcile.py': '19.L rules 2/5: '
                                                    'test_recovery_alert_does_not_change_disposition wraps '
                                                    'Stages in a bare prepare callback; propagate the public '
                                                    'stages carrier to forced quiescence without changing '
                                                    'orphan disposition or run-sequence assertions.',
                         'tests/test_flake.py': '19.L rule 2: test_flake_detection_is_dormant and '
                                                'test_flake_release_is_dormant assert an empty Box after a '
                                                'synthetic merge. Supply successful scripted retro via the '
                                                'shared public fixture so a missing Driver cannot add an '
                                                'unrelated failure report; retain flake negatives.',
                         'tests/test_storm_hold.py': '19.L rules 2/5: '
                                                     'test_live_drain_holds_only_emitting_stem uses Script '
                                                     'through five synthetic merges and quiescence. Give the '
                                                     'custom carrier public stages/Driver access and script '
                                                     'the forced report; retain resume, ordering, cap and '
                                                     'pending-message assertions.',
                         'tests/test_storm_notification_activation.py': '19.L rule 2: '
                                                                        'test_storm_activation_does_not_hold_dispatch_or_notify '
                                                                        'forbids every Effects.run call '
                                                                        'after merged quiescence. Narrow '
                                                                        'that forced assertion to '
                                                                        'notification effects, admitting the '
                                                                        'required retro report effect while '
                                                                        'still forbidding Box consumption '
                                                                        'and notification.'},
 'phase5-continue': {}}

AUTHORED = {'retro-drain-invoker': {'chars': 7752,
                         'bytes': 7752,
                         'birth_sha256': 'f7041f0a5ad3e9702abc0a3bac33fc0c3e68c881cb64a2bcaa6954d1c9d9b70a',
                         'plan': ('19.I', '19.P5.retro-drain-invoker', '13', '14'),
                         'context': ('chupa/driver.py',
                                     'chupa/__main__.py',
                                     'chupa/box.py',
                                     'tests/test_driver.py',
                                     'tests/test_box.py',
                                     'chupa/daemon.py',
                                     'chupa/journal.py',
                                     'tests/test_vocabularies.py',
                                     'tests/test_cli.py',
                                     'tests/test_drain_upgrade.py',
                                     'tests/test_seed_successor.py',
                                     'tests/test_daemon_config.py',
                                     'tests/test_daemon_admission.py',
                                     'tests/test_daemon_pause.py',
                                     'tests/test_reconcile.py',
                                     'tests/test_flake.py'),
                         'on_demand': ('chupa/drain.py',
                                       'chupa/stages.py',
                                       'tests/test_drain.py',
                                       'tests/test_stages.py',
                                       'chupa/runner.py',
                                       'tests/test_storm_hold.py',
                                       'tests/test_storm_notification_activation.py'),
                         'fenced_existing': ('chupa/drain.py',
                                             'chupa/driver.py',
                                             'chupa/stages.py',
                                             'chupa/__main__.py',
                                             'chupa/box.py',
                                             'tests/test_drain.py',
                                             'tests/test_driver.py',
                                             'tests/test_stages.py',
                                             'tests/test_box.py',
                                             'chupa/runner.py',
                                             'chupa/daemon.py',
                                             'chupa/journal.py',
                                             'tests/test_vocabularies.py',
                                             'tests/test_cli.py',
                                             'tests/test_drain_upgrade.py',
                                             'tests/test_seed_successor.py',
                                             'tests/test_daemon_config.py',
                                             'tests/test_daemon_admission.py',
                                             'tests/test_daemon_pause.py',
                                             'tests/test_reconcile.py',
                                             'tests/test_flake.py',
                                             'tests/test_storm_hold.py',
                                             'tests/test_storm_notification_activation.py'),
                         'created': ('chupa/retro.py', 'specs/retro.md', 'tests/test_retro.py'),
                         'max_effort_render': 281199,
                         'actual_max_effort_render': 279468},
 'phase5-continue': {'chars': 6380,
                     'bytes': 6380,
                     'birth_sha256': '71f775f6b99540eb269460cc090ca711ced2d87055cdc829102e5af8d4fd1c7d',
                     'plan': ('19.L', '19.I', '19.P5', '19.P5.retro-box-activation', '12', '13'),
                     'context': ('tests/test_seeded_phase3_core.py',),
                     'on_demand': (),
                     'fenced_existing': (),
                     'created': ('tickets', 'tests/test_seeded_phase5_01.py'),
                     'max_effort_render': 100487,
                     'actual_max_effort_render': 98348}}

VALIDATED_ENTRIES = {'19.P5.retro-drain-invoker': {'sha256': 'c8860e117f46299adc816002b4dcdaebbdc1f733afbdc749aca76338358854ed',
                               'chars': 10202,
                               'parts': {'Owner': 1180, 'Records': 5257, 'Observable': 1332, 'Tests': 2285},
                               'gap': None,
                               'required': True,
                               'resolves': 1,
                               'tests': ('test_window_uses_completed_report_boundary',
                                         'test_retro_trigger_boundaries',
                                         'test_report_commit_replays_without_advancing_unfinished_window',
                                         'test_failed_retro_suppresses_window_until_completion',
                                         'test_retro_hook_is_default_off',
                                         'test_drain_retro_due_quiescence_and_pre_exit',
                                         'test_retro_driver_access_is_public_and_read_only',
                                         'test_exit_read_window_materialization')},
 '19.P5.retro-box-activation': {'sha256': 'b750a8a519396f98a597a3fa040803ea113f537b35b431b8ae61944bf9789251',
                                'chars': 9207,
                                'parts': {'Owner': 1478, 'Records': 3844, 'Observable': 1070, 'Tests': 2653},
                                'gap': None,
                                'required': True,
                                'resolves': 1,
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

PLAN_CHARS = {'19.I': 1811,
 '19.P5.retro-drain-invoker': 10202,
 '13': 19840,
 '14': 7360,
 '19.L': 20912,
 '19.P5': 9792,
 '19.P5.retro-box-activation': 9207,
 '12': 20224}

FILE_CHARS = {'chupa/drain.py': 33646,
 'chupa/driver.py': 23190,
 'chupa/stages.py': 61220,
 'chupa/__main__.py': 15669,
 'chupa/box.py': 10000,
 'tests/test_drain.py': 51795,
 'tests/test_driver.py': 16683,
 'tests/test_stages.py': 32249,
 'tests/test_box.py': 6488,
 'chupa/runner.py': 38439,
 'chupa/daemon.py': 26079,
 'chupa/journal.py': 11011,
 'tests/test_vocabularies.py': 6602,
 'tests/test_cli.py': 12017,
 'tests/test_drain_upgrade.py': 12811,
 'tests/test_seed_successor.py': 11842,
 'tests/test_daemon_config.py': 16015,
 'tests/test_daemon_admission.py': 9543,
 'tests/test_daemon_pause.py': 7632,
 'tests/test_reconcile.py': 13940,
 'tests/test_flake.py': 27816,
 'tests/test_storm_hold.py': 31487,
 'tests/test_storm_notification_activation.py': 30415,
 'tests/test_seeded_phase3_core.py': 5425}

FILE_BYTES = {'chupa/drain.py': 33646,
 'chupa/driver.py': 23190,
 'chupa/stages.py': 61220,
 'chupa/__main__.py': 15669,
 'chupa/box.py': 10000,
 'tests/test_drain.py': 51795,
 'tests/test_driver.py': 16683,
 'tests/test_stages.py': 32249,
 'tests/test_box.py': 6488,
 'chupa/runner.py': 38439,
 'chupa/daemon.py': 26079,
 'chupa/journal.py': 11011,
 'tests/test_vocabularies.py': 6602,
 'tests/test_cli.py': 12017,
 'tests/test_drain_upgrade.py': 12811,
 'tests/test_seed_successor.py': 11842,
 'tests/test_daemon_config.py': 16015,
 'tests/test_daemon_admission.py': 9543,
 'tests/test_daemon_pause.py': 7632,
 'tests/test_reconcile.py': 13940,
 'tests/test_flake.py': 27816,
 'tests/test_storm_hold.py': 31487,
 'tests/test_storm_notification_activation.py': 30418,
 'tests/test_seeded_phase3_core.py': 5425}

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4896

RENDER_OVERHEAD = 2000

SCENARIOS = {'tests/test_drain.py': ('migration',
                         'Registry floor: Script and rework wrappers need public stages on forced '
                         'quiescence; preserve control waits, caps, parked-state reads, and default-off '
                         'direct-drain probes.'),
 'tests/test_drain_upgrade.py': ('migration',
                                 '19.L rules 2/5: Script emits real docs merges; child quiescence forces '
                                 'retro, invalidating missing-Driver fixture and HEAD~1 handoff-commit '
                                 'assumption in '
                                 'test_a_self_upgrading_admission_hands_off_before_the_next_dispatch. Pin '
                                 'the journaled admission SHA rather than commit offsets and supply the '
                                 'public scripted Driver.'),
 'tests/test_seed_successor.py': ('migration',
                                  '19.L rules 2/5: two work/ merges reach quiescence; '
                                  'test_merged_parent_registers_and_runs_successor_in_same_drain pins '
                                  'exactly five model calls and main equal to last squash. Add the forced '
                                  'retro call/report commit and public stages access while retaining seed '
                                  'lift/dependency assertions.'),
 'tests/test_cli.py': ('migration',
                       '19.L rules 2/5: shared Stages.__call__ fixture lacks public driver access for forced '
                       'quiescence after its merged terminal; migrate the fixture through the public '
                       'composition with scripted retro output, retaining calls and lock assertions.'),
 'tests/test_daemon_config.py': ('migration',
                                 '19.L rules 2/5: test_config_snapshot_is_dormant supplies a bare dispatch '
                                 'which reports merged; migrate only the missing-stage-owner fixture at '
                                 'forced quiescence, preserving snapshot and daemon dormancy probes.'),
 'tests/test_daemon_admission.py': ('migration',
                                    '19.L rules 2/5: test_daemon_admission_is_dormant supplies a bare merged '
                                    'dispatch; provide the public scripted stages carrier at quiescence, '
                                    'preserving the daemon-construction/dispatch refusal probes.'),
 'tests/test_daemon_pause.py': ('migration',
                                '19.L rules 2/5: test_dispatch_pause_boundary_is_active reports merged '
                                'through its custom Script; carry the public Driver for forced quiescence, '
                                'preserving control-consumption and dispatch-count assertions.'),
 'tests/test_reconcile.py': ('migration',
                             '19.L rules 2/5: test_recovery_alert_does_not_change_disposition wraps Stages '
                             'in a bare prepare callback; propagate the public stages carrier to forced '
                             'quiescence without changing orphan disposition or run-sequence assertions.'),
 'tests/test_flake.py': ('migration',
                         '19.L rule 2: test_flake_detection_is_dormant and test_flake_release_is_dormant '
                         'assert an empty Box after a synthetic merge. Supply successful scripted retro via '
                         'the shared public fixture so a missing Driver cannot add an unrelated failure '
                         'report; retain flake negatives.'),
 'tests/test_storm_hold.py': ('migration',
                              '19.L rules 2/5: test_live_drain_holds_only_emitting_stem uses Script through '
                              'five synthetic merges and quiescence. Give the custom carrier public '
                              'stages/Driver access and script the forced report; retain resume, ordering, '
                              'cap and pending-message assertions.'),
 'tests/test_storm_notification_activation.py': ('migration',
                                                 '19.L rule 2: '
                                                 'test_storm_activation_does_not_hold_dispatch_or_notify '
                                                 'forbids every Effects.run call after merged quiescence. '
                                                 'Narrow that forced assertion to notification effects, '
                                                 'admitting the required retro report effect while still '
                                                 'forbidding Box consumption and notification.'),
 'tests/test_drain_reentry.py': ('preservation',
                                 'Each successful admission changes chupa/thing.py and immediately hands off '
                                 'to NoChild; no next dispatch/pre-exit/quiescence hook in that parent. '
                                 'Fixed clock and fewer than five gate failures before merge.'),
 'tests/test_ladder.py': ('preservation',
                          'Successful chupa/thing.py merges immediately hand off to NoChild; at most three '
                          'gate_failed terminals before that handoff, no exit ticket, and fixed clock. '
                          'Refused-split follow-up has no merge and one gate failure.'),
 'tests/test_diagnose.py': ('preservation',
                            'The drain case has two failures then a chupa/thing.py upgrade to NoChild; no '
                            'forced quiescence is reached, no spike threshold or elapsed window.'),
 'tests/test_harvest.py': ('preservation',
                           'The drain re-entry ends in chupa/thing.py self-upgrade to NoChild after two '
                           'infra failures; the parent never reaches forced quiescence, and infra_error is '
                           'not a retro spike operand.'),
 'tests/test_audit.py': ('preservation',
                         'The real chupa/thing.py merge hands off to NoChild before the other red stem; the '
                         'parent never reaches forced quiescence or a due threshold.'),
 'tests/test_merge.py': ('preservation',
                         'Bootstrap CLI proof merges chupa/thing.py then hands off to NoChild; '
                         'report-producer null-commit proofs use run or serve, which have no drain hook. No '
                         'registry or custody migration.'),
 'tests/test_storm_producer.py': ('preservation',
                                  'CLI production-arrival proof merges chupa/thing.py and hands off to '
                                  'NoChild; storm_occurrence is not a retro spike, and Box consumption '
                                  'remains dormant.'),
 'tests/test_daemon_composition.py': ('preservation',
                                      'The CLI control-sharing drain is empty; inline admission proof '
                                      'upgrades chupa/thing.py to NoChild. Other live drains call drain '
                                      'directly (default-off hook); CoreRig drains the daemon scheduler, not '
                                      'the CLI drain.'),
 'tests/test_provider_cooldown_failover.py': ('preservation',
                                              'Calls drain directly with the default-off hook; the escalated '
                                              'route uses already_satisfied. Provider recovery tests run '
                                              'CoreRig or serve, not main drain.'),
 'tests/test_watchdog_activation.py': ('preservation',
                                       'CoreRig scheduler/serve compositions exercise watched calls and '
                                       'timeout harvest; none wires the CLI drain retro hook.'),
 'tests/test_restart_timers.py': ('preservation',
                                  'CoreRig and Restart direct composition; no CLI drain retro hook, despite '
                                  'scheduler merges.'),
 'tests/test_kill_cli_activation.py': ('preservation',
                                       'Live CLI kill ends nonquiescent without a merge; default-off '
                                       'LiveDrain and CoreRig own the other cases. already_satisfied does '
                                       'not land a merge.'),
 'tests/test_kill_executor_abort.py': ('preservation',
                                       'Active abort probes run direct LiveDrain/default-off or CoreRig; '
                                       'kill stops before a merge/forced quiescence.'),
 'tests/test_kill_signal_journal.py': ('preservation',
                                       'Active kill-signal probes use direct LiveDrain/default-off and '
                                       'CoreRig; no CLI merged quiescence.'),
 'tests/test_seed_path.py': ('preservation',
                             'The only main drain re-entry refuses an unresolved spec gap and settles the '
                             'other paths already_satisfied; no merge, five spikes, elapsed window, or phase '
                             'exit.'),
 'tests/test_reject_queue.py': ('preservation',
                                'Scripted drain terminal markers have no admitted commit; shared Script '
                                'migration in fenced test_drain.py supplies any forced call. Queue '
                                'assertions themselves remain unchanged.'),
 'tests/test_caps.py': ('preservation',
                        'Direct synthetic drain uses shared test_drain.py Script migration; spent-cap '
                        'assertions do not flip and no new direct composition signature is introduced.'),
 'tests/test_control_cli.py': ('shared migration',
                               'Fenced tests/test_cli.py::Stages.__call__ gains the public stages carrier '
                               'and scripted forced retro after the synthetic merge. This suite keeps '
                               'calls/lock and its unrelated dormancy/absence assertions unchanged; direct '
                               'CoreRig/LiveDrain hooks remain off.'),
 'tests/test_daemon_tasks.py': ('shared migration',
                                'Fenced tests/test_cli.py::Stages.__call__ gains the public stages carrier '
                                'and scripted forced retro after the synthetic merge. This suite keeps '
                                'calls/lock and its unrelated dormancy/absence assertions unchanged; direct '
                                'CoreRig/LiveDrain hooks remain off.'),
 'tests/test_heartbeat.py': ('shared migration',
                             'Fenced tests/test_cli.py::Stages.__call__ gains the public stages carrier and '
                             'scripted forced retro after the synthetic merge. This suite keeps calls/lock '
                             'and its unrelated dormancy/absence assertions unchanged; direct '
                             'CoreRig/LiveDrain hooks remain off.'),
 'tests/test_checkpoint.py': ('shared migration',
                              'Fenced tests/test_cli.py::Stages.__call__ gains the public stages carrier and '
                              'scripted forced retro after the synthetic merge. This suite keeps calls/lock '
                              'and its unrelated dormancy/absence assertions unchanged; direct '
                              'CoreRig/LiveDrain hooks remain off.'),
 'tests/test_kill_worker_stop.py': ('shared migration',
                                    'Fenced tests/test_cli.py::Stages.__call__ gains the public stages '
                                    'carrier and scripted forced retro after the synthetic merge. This suite '
                                    'keeps calls/lock and its unrelated dormancy/absence assertions '
                                    'unchanged; direct CoreRig/LiveDrain hooks remain off.'),
 'tests/test_kill_failure_suppression.py': ('shared migration',
                                            'Fenced tests/test_cli.py::Stages.__call__ gains the public '
                                            'stages carrier and scripted forced retro after the synthetic '
                                            'merge. This suite keeps calls/lock and its unrelated '
                                            'dormancy/absence assertions unchanged; direct CoreRig/LiveDrain '
                                            'hooks remain off.')}

PRESERVATION = ('tests/test_drain_reentry.py',
 'tests/test_ladder.py',
 'tests/test_diagnose.py',
 'tests/test_harvest.py',
 'tests/test_audit.py',
 'tests/test_merge.py',
 'tests/test_storm_producer.py',
 'tests/test_daemon_composition.py',
 'tests/test_provider_cooldown_failover.py',
 'tests/test_watchdog_activation.py',
 'tests/test_restart_timers.py',
 'tests/test_kill_cli_activation.py',
 'tests/test_kill_executor_abort.py',
 'tests/test_kill_signal_journal.py',
 'tests/test_seed_path.py',
 'tests/test_reject_queue.py',
 'tests/test_caps.py',
 'tests/test_control_cli.py',
 'tests/test_daemon_tasks.py',
 'tests/test_heartbeat.py',
 'tests/test_checkpoint.py',
 'tests/test_kill_worker_stop.py',
 'tests/test_kill_failure_suppression.py')

CLOSURE_SCAN = {'chupa/merge.py': {'sha256': 'c622919f7e12570e0e876b4f4b3e49aa111508396ef5da1a09c322ef29544c3d',
                    'lines': (46,)},
 'chupa/drain.py': {'sha256': '89bbf75a58bd7286baf129b5a992dc5a3f3c7a7a1c3d9455178fd543d4b96720',
                    'lines': (252,)},
 'chupa/__main__.py': {'sha256': 'bce04e99e5360a5af84c5594c824c7e7f235fbfd814eb39e58af0eebf8988728',
                       'lines': (44, 46, 65, 72, 124, 139, 180, 191, 197, 250, 251, 325)},
 'chupa/driver.py': {'sha256': 'a565f661b587a3ff7b6df1a588143a80127f67e96e53bbb87b79f2e10ae661e3',
                     'lines': (154, 165, 180, 197, 358, 361)},
 'chupa/box.py': {'sha256': '7d401296782c0d868fabe94a419c6d7fb5d8e1e78be03cdec45a1de3c75fd9f5',
                  'lines': (235, 237, 241)},
 'chupa/runner.py': {'sha256': 'b13782b8908b1b607d11e572ebb2c3479cdec088731d88bd7db9268bc2f93621',
                     'lines': (31,
                               72,
                               89,
                               99,
                               114,
                               128,
                               129,
                               142,
                               266,
                               296,
                               302,
                               488,
                               497,
                               512,
                               514,
                               627,
                               629)},
 'chupa/daemon.py': {'sha256': '474684932c22a826336712d364b579b2472c452a8fc6caf038e77791b30ca829',
                     'lines': (45, 49, 338)},
 'chupa/watcher.py': {'sha256': '3009da9afc78ca7d16830801191e83dd555b419e132fe74a658daddb27828b9d',
                      'lines': (66,)},
 'chupa/effects.py': {'sha256': '6fc7459f9cb5f1a3cc4e12b891771eb437d4822e166d90f08818e7dd9b372156',
                      'lines': (25, 71)},
 'chupa/gates.py': {'sha256': 'e84959455efe288a354c0a29f771ed3671a7b6f4e6783ae3008407f949dce59f',
                    'lines': (75,)},
 'chupa/redact.py': {'sha256': 'c275877a13669e9a1d9bca13cf7fd12f76e9fc98b36e6c21419c5611315f2714',
                     'lines': (23,)},
 'chupa/serve.py': {'sha256': '8d3b3b63203e462914ea365ab8cbfa7d623091decebad2c7da3b3c6fc69c0985',
                    'lines': (79, 98, 334, 375, 442)},
 'chupa/triage.py': {'sha256': '487dd345cec670dd84ef831ecbb9ac24660e3d36fefe32fef2a2fad79fd1f1d6',
                     'lines': (96, 98)},
 'chupa/thresh.py': {'sha256': '16f00392d1072ef62dd85be228c53e6e763083f495bebe7610da023c84c09b53',
                     'lines': (238,)},
 'chupa/seams.py': {'sha256': 'c465a54f053a4330f63abdcc0471747714f0d54147d070b79d9a98af213a0673',
                    'lines': (21, 41, 100)},
 'chupa/stages.py': {'sha256': 'ef7a47c4079b3303890fc1dfcd943068c4e766e81c9ec540a2afcf929290f67e',
                     'lines': (513, 553, 555, 643, 645, 1185)},
 'chupa/journal.py': {'sha256': 'c6deb58f29bb15f2276aee64a2a39ae6d7cb20da0c8815202faa2216ff17f182',
                      'lines': (36, 71, 76, 140, 142)},
 'chupa/llmeffect.py': {'sha256': 'dbd470510b70f531dd6bf606cde7f19571f4ddc194791ab3ad9bf75cc1c8a79f',
                        'lines': (35,)},
 'chupa/providers.py': {'sha256': '4f0bc7d61dc8a342a7bfce60e7442b7186a12d1a12a23510b01ba7bc3f32f77e',
                        'lines': (517,)},
 'eval/reliability_battery.py': {'sha256': '2e42e1e58c22691435e1ce58daab5e1d355fc7abc9f8dac9ac6dfc4aad912d61',
                                 'lines': (53, 149, 406, 424, 425, 429)},
 'eval/daemon_soak.py': {'sha256': 'cb4d3903d85b11cd3d2771b7db27f29b9add770702e3138211f613e672f75e98',
                         'lines': (95, 637, 651, 652, 656)},
 'eval/diagnose.py': {'sha256': 'ce87d141312865d75784136d89b22911df909ec0904a1b35b3779ee7df77bf93',
                      'lines': (140, 240, 251, 270)},
 'eval/harness.py': {'sha256': '77b68a5e79f964cfdb2ba1359af29a39c506fb28802a89a6372afc39200ee831',
                     'lines': (165, 349, 400, 411, 433)},
 'eval/shakeout/bench.py': {'sha256': '8e7c10805ec6ae5de47618b15d80f4e4a84b05aa39155405cd50f7db55833701',
                            'lines': (18, 113, 116, 121)},
 'eval/shakeout/merge.py': {'sha256': 'cca9cccf7329aaa879ae3409befc14a7a92d3e5bf0ca0689454975e6fec49399',
                            'lines': (62,)},
 'eval/shakeout/stages.py': {'sha256': '7cf99e76687320963a7b86d00ff12a6a31d327696ee301d8e95de9d6bee8f371',
                             'lines': (1, 194)},
 'eval/shakeout/run.py': {'sha256': '7973fa63020be786bdbdb83c3de2b7bacf4d63bfc1b667c7e2145006b6c4b772',
                          'lines': (43, 86, 104, 105, 109)},
 'eval/shakeout/providers.py': {'sha256': 'f06d79ee810bb031cf32bb5755928ac4f7d4aedcd82aeb26650b1ba668667df6',
                                'lines': (23,)},
 'tests/test_harvest_orphans.py': {'sha256': '7e346128a674c1f79ccef7282384b7c6d458ec2352655027ec4a7f6eb241a5cb',
                                   'lines': (22,)},
 'tests/test_daemon_pause.py': {'sha256': 'd31d3a26cbd0c333fcecc776487690b44f36d18df41a3c492110e30de45ef9e4',
                                'lines': (34, 186, 188)},
 'tests/test_daemon_soak.py': {'sha256': '958377f244eb5f8c9fb65fa000178c06c3826bf82950d4a9f71f762c49f83682',
                               'lines': (347, 363)},
 'tests/test_eval_harness.py': {'sha256': 'a3ef759b464913e38fdf76572d9c59895d3b399eee898e4f330dc60aa6ff16e4',
                                'lines': (73, 76)},
 'tests/test_gates.py': {'sha256': 'd3e72fb8dd8069a7da7447dec15face5af91fe97b5930341af591f102aef81e9',
                         'lines': (185,)},
 'tests/test_caps.py': {'sha256': 'b024d13fc0b9e63106c6ed1341ee48581b7c8f9e4a7e51ff16d04a6b220a0956',
                        'lines': (80, 81, 106, 107)},
 'tests/test_echo_stage.py': {'sha256': '5c1f25d6384fbc5c2a99ec2a5e73b650aec5f193301b1b4f1d97838405413fa0',
                              'lines': (78, 81)},
 'tests/test_watchdog.py': {'sha256': '420a90a554360f05131c20e69caf59adbf877fd434e5a7449d422f7803e11c33',
                            'lines': (177, 182, 570)},
 'tests/test_notify.py': {'sha256': 'f9edb12cffe35114969178dfeb818f44103a1c4bb5c708ba7d114a2b85a8f6cf',
                          'lines': (86, 134, 138)},
 'tests/test_drain_reentry.py': {'sha256': '63f5bc289dea1b08cf100994dc54db7643a3eae89af0800e21fdba87be8b6d8b',
                                 'lines': (5, 26, 35, 101)},
 'tests/test_heartbeat.py': {'sha256': '8d8534dfac359f50cccb3a4761e894a00c99ef637b93f34d4f39223a96f8723a',
                             'lines': (217, 226, 233, 238, 265)},
 'tests/test_requisition.py': {'sha256': '554a33195f7c2780f9a13c79c008ce2f59b9f79db82818354f93deba4fc15164',
                               'lines': (83, 88)},
 'tests/test_watchdog_activation.py': {'sha256': '347d2dd1c086fa499ca1b46ac531aaa6ea6d8d63b6caa55fabe31ea2fc991964',
                                       'lines': (173, 346)},
 'tests/test_daemon_soak_runner.py': {'sha256': '7a8f1eec806d0b86a51af8887127ed316fbd3c78dd27905bcc93b6a4947da899',
                                      'lines': (133,)},
 'tests/test_vocabularies.py': {'sha256': 'e14f8d8f9adaf713d5b761d51950d30dd14bd2c1161e204a3f935d31ebef4b43',
                                'lines': (107, 109, 119, 125, 133, 135)},
 'tests/test_cli.py': {'sha256': 'f2e790b7aa1dd4e094fc411faf02499d4e592522b590451be558f6e5e3471904',
                       'lines': (138, 306, 308, 311, 312)},
 'tests/test_control_cli.py': {'sha256': '2dda06596b87259cedfaa9fc354582266b34af52ee991553288e24f4297b7915',
                               'lines': (18, 19, 130)},
 'tests/test_drain_upgrade.py': {'sha256': 'eeee80050e7d3821564b21b83e5679b1c883b890b2bc2d828b89f7d23b53f892',
                                 'lines': (61, 78, 117)},
 'tests/test_provider_cooldown_failover.py': {'sha256': 'e8b306d6f6a185806e16360a0a876a27b419d7d4b4db89b2d54333e3be8c48b9',
                                              'lines': (40,
                                                        69,
                                                        104,
                                                        143,
                                                        315,
                                                        471,
                                                        506,
                                                        508,
                                                        523,
                                                        643,
                                                        664,
                                                        668,
                                                        686,
                                                        747)},
 'tests/test_llm_effect.py': {'sha256': 'f017681fc09041e56bf1e4b40159494302d9a4f7d25fc756bcabce4c25a66169',
                              'lines': (73, 79)},
 'tests/test_ladder.py': {'sha256': 'bcee0c92e02736dc53c393dfc19f6734f1edbf4ae0d83da3ab5492a32b77744f',
                          'lines': (55, 57, 58, 164, 166, 167, 176, 205, 206, 223, 227, 269, 270)},
 'tests/test_reliability_battery.py': {'sha256': 'becb86f3ba4d4714d3ec1f3c082912c206ae15bf03555723266049ec55fc4caa',
                                       'lines': (216, 256, 300, 305)},
 'tests/test_control.py': {'sha256': '65c02ae7b3c8cccb454025f6a58d6bb1e43fd2d48f6e7d74b8248d544c2efd57',
                           'lines': (404, 411)},
 'tests/test_daemon_config.py': {'sha256': '1682e931df7a13637904d9660d8e5df45c7853b24da7ed5472328d17c2f05fd4',
                                 'lines': (155, 189, 223, 264, 311, 364, 367, 383, 386, 388, 390)},
 'tests/test_storm_notification_activation.py': {'sha256': '21a9ccfaff493d75898429a50b53a5f57fb27488afca76c681b31dffb95f1809',
                                                 'lines': (29,
                                                           253,
                                                           260,
                                                           273,
                                                           274,
                                                           278,
                                                           291,
                                                           393,
                                                           394,
                                                           414,
                                                           459,
                                                           573,
                                                           574,
                                                           577)},
 'tests/test_daemon_composition.py': {'sha256': '3fbf5ad16cd3b4fc10809d184267ce555b570e7228b20cfa916f852e2f592c42',
                                      'lines': (53,
                                                113,
                                                536,
                                                600,
                                                601,
                                                622,
                                                631,
                                                652,
                                                665,
                                                666,
                                                669,
                                                674,
                                                868,
                                                875,
                                                891,
                                                904,
                                                906,
                                                913,
                                                918,
                                                919,
                                                948,
                                                953,
                                                959,
                                                976,
                                                987,
                                                1423,
                                                1563,
                                                1736,
                                                1759,
                                                1761,
                                                1772,
                                                1773,
                                                1775,
                                                1777,
                                                1807,
                                                1926,
                                                1937,
                                                1938,
                                                1947,
                                                1952)},
 'tests/test_shakeout.py': {'sha256': '2b3c415b3849b8120d5115b01e605b08eb9e393b120f5432260af84fbf00cc45',
                            'lines': (86, 89)},
 'tests/test_kill_worker_stop.py': {'sha256': '6099ca1d58db6c928dcd72933ff619da6f45d607656a2b36af2631b8ef03e9eb',
                                    'lines': (42, 315, 322, 328, 333, 336, 338)},
 'tests/test_mergequeue.py': {'sha256': 'd3a690502df5c631cb16c31eabe4756e5ecb95f591034f6bc742c2e87a0adf4b',
                              'lines': (42, 273, 411, 415)},
 'tests/test_kill_cli_activation.py': {'sha256': '4b8827cdbe92f388d6e7234704ee63d001693d0be2b390ed971d34bf0cbb8224',
                                       'lines': (151, 237, 704, 756, 759)},
 'tests/test_seed_path.py': {'sha256': '3e3e3f041c87365c633190193c08aa2cc02467e44ecd1bfa7fd8f9e952010a5b',
                             'lines': (72, 103, 254, 290, 723)},
 'tests/test_kill_failure_suppression.py': {'sha256': 'fad8c01cc71c2e46ed40014aca70d81befd322f991193e00b81d559183e0c968',
                                            'lines': (339, 347, 353, 358, 361, 363)},
 'tests/test_checkpoint.py': {'sha256': '8e6152e7cf44f2a66b556ed70139460dd068e85d8ffbf70c112b8b44c5ac5748',
                              'lines': (45, 68, 476, 486, 510, 512, 519, 560)},
 'tests/test_reconcile.py': {'sha256': '4b07ca005b96df41fed6b254afb448b61edb417f37eec52d4a4c2ebc685f252a',
                             'lines': (10, 123, 313)},
 'tests/test_box.py': {'sha256': '1cf8c0c4aae2622dc84e94fea98c678dca2a39e04c36f3b644592cafacdce856',
                       'lines': (37, 62, 69, 128)},
 'tests/test_storm.py': {'sha256': '2112e5f2aed76ed20638dfa2d1679c49c811698f9b56728fa5152b151b051b1b',
                         'lines': (115, 255, 267)},
 'tests/test_daemon_tasks.py': {'sha256': 'bb183bb80450fc85ebe5743596a36614502d1f1b574fa006d2e98e132032258a',
                                'lines': (319, 328, 340, 343, 354, 365)},
 'tests/test_diagnose.py': {'sha256': '13bf2e1824c899efa49714492f536cc6e358247d06adf6323bdc1d53ae6d9777',
                            'lines': (32, 33, 219)},
 'tests/test_seed_successor.py': {'sha256': 'd331597c36a7108423bbfa6c60d3fe62f5957558b7e5e449014e4ff97916e4de',
                                  'lines': (171, 194)},
 'tests/test_second_problems.py': {'sha256': '386b4c80a3996ddf9af5611b91315444a89f22bf8e2f1a81cb995c32c7d8c16c',
                                   'lines': (31, 33, 34, 39)},
 'tests/test_restart_timers.py': {'sha256': 'bb8a3efb5951fd8af7a872ccc65ca001f77d64ee8bd1776b8346a8e21a9b4200',
                                  'lines': (39, 283, 286)},
 'tests/test_git.py': {'sha256': 'e2da96db7b8dc280df1b70ba91feaca7d3eb0d6c33bf399de8837b5fcbcb51ea',
                       'lines': (23, 32)},
 'tests/test_terminal.py': {'sha256': '4fd0c9becbaf421a6f1b153cd3cb607c753f370fca6a615aa7b89332a780063a',
                            'lines': (47, 49, 145)},
 'tests/test_stages.py': {'sha256': 'c38c0f357fec51f164e8a0513c5a00f3eb40e4ad66dc9ac1ff847af2d4cea364',
                          'lines': (165, 175, 396, 409)},
 'tests/test_storm_hold.py': {'sha256': '52644ccfed84f447a58ca504376829cabbbdf1e75918590c938b313600b0a941',
                              'lines': (27, 145, 168, 219)},
 'tests/test_tickets.py': {'sha256': '801d430c9a45c15a16fb35df02fa09c975725b15de1374e022a5aa50918dd618',
                           'lines': (92,)},
 'tests/test_daemon_admission.py': {'sha256': 'd8bef4db47b3f1c10edc04d8b5713b52b48e4ebc2da088a5e752cdd483983c01',
                                    'lines': (233, 234, 247, 251, 253, 260)},
 'tests/test_reject_queue.py': {'sha256': 'afb0a9fea362c6be8acce662da1b0e8e4cbe17880800f3813a78fdbd80d4a80e',
                                'lines': (42,
                                          43,
                                          58,
                                          71,
                                          72,
                                          85,
                                          89,
                                          94,
                                          114,
                                          122,
                                          132,
                                          137,
                                          140,
                                          146,
                                          159,
                                          168,
                                          170,
                                          174,
                                          177,
                                          183,
                                          199,
                                          203,
                                          214)},
 'tests/test_flake.py': {'sha256': '0cfbf509b9f3bcde98f876a3c01f73c6f10202e340f0cf31ac435f8e60aafd43',
                         'lines': (27, 282, 284, 313, 314, 316, 337, 351, 353, 382, 383, 385, 406)},
 'tests/test_drain.py': {'sha256': '1d8964afdecb11559f6012533d6361d088399edade34c8051be2571bf6b0c0a5',
                         'lines': (89,
                                   265,
                                   270,
                                   272,
                                   390,
                                   405,
                                   415,
                                   428,
                                   437,
                                   452,
                                   502,
                                   503,
                                   566,
                                   578,
                                   653,
                                   662)},
 'tests/test_merge.py': {'sha256': '0d1ea826aff220ce41dd2164a3ede420d1ad07ea1e629b5809159e0760d78ba2',
                         'lines': (56, 117, 139, 146, 150, 151, 255, 307, 435, 443, 445, 446, 537, 540)},
 'tests/test_triage.py': {'sha256': 'afcaa6d44ef47725f18e16b37140ed09a10d27c32a60a2e66347081d850b2169',
                          'lines': (29, 85, 87)},
 'tests/test_driver.py': {'sha256': 'f42e8acc9f73f0e5686653fdc9d37a14d6419ae6e0bc6a17633bd0bb56bde76d',
                          'lines': (98, 108, 314, 380, 383, 384, 385)},
 'tests/test_storm_producer.py': {'sha256': '20778b89148802e50b977724d81a5e72113ffae572a372b460b7a4d58f63dd1d',
                                  'lines': (30, 56, 215, 221, 237, 238, 246, 260, 261, 262)},
 'tests/test_effects.py': {'sha256': 'c47fa1d340566a6923677270489c8b18627b4130204137d6414a15b5e26bc305',
                           'lines': (30,)},
 'tests/test_providers.py': {'sha256': '1da55805d0df5ec272f353a798c5af0e7eb20944aced3d1ec7e4fde41261d98a',
                             'lines': (78, 411, 468, 530, 561, 605, 614, 645, 655, 657, 682, 771, 812)},
 'tests/test_serve.py': {'sha256': 'afe9c070e806ccda57a4bbef6f996e22aef1a042ce19468da9ca5346de55ee32',
                         'lines': (152, 164)},
 'tests/test_harvest.py': {'sha256': 'efb303883aee63a3de9d6c3ca3f11f16caed3474d2aa1e72123ebf8628b37a17',
                           'lines': (20, 23)},
 'tests/test_author.py': {'sha256': '0e619d2341de87c36734c447a19c20bc0b2e3f5ee782aa8e41f58b21bc5e788e',
                          'lines': (18, 36)},
 'tests/test_diagnose_eval.py': {'sha256': 'ff22f5edcbb54b6a1bd5a60a15eab764678e50c1358c93b326ff27151e30267e',
                                 'lines': (57,)}}

CLOSURE_PATTERNS = ('Driver\\(|from_config|def run|def bind|prepare_pipeline|pipeline',
 'storm_producer|Box\\(',
 'SIGNAL_NAMES|test_every_engine_signal_name_is_listed',
 'not hasattr|__all__|is_dormant',
 'main\\(|\\[.drain.\\]|verb == .drain.')

FUTURE_EDGES = {'retro-box-activation': ('phase5-continue', 'retro-drain-invoker'),
 'phase5-continue-02': ('retro-box-activation',)}

FUTURE_REQUIRED_TESTS = ('test_completed_retro_proposals_reach_prompt_spec_merge',
 'test_tombstone_rereports_reopen_at_threshold',
 'test_tombstone_reopen_requires_journal_callback',
 'test_reopened_message_bypasses_its_tombstone',
 'test_reopened_retro_ticket_starts_draft',
 'test_standing_go_uses_the_table_and_each_override_drafts',
 'test_retro_prompt_spec_merge_requires_unique_bridge',
 'test_production_boxes_receive_rereport_callback',
 'test_retro_itemizes_confirmed_class_tombstones',
 'test_status_surfaces_confirmed_class_tombstones',
 'test_tombstone_visibility_uses_message_class')

FUTURE_FLOOR_ADDITIONS = {'chupa/journal.py': 'Entry signal writer/consumer closure for all three activation signals.',
 'tests/test_vocabularies.py': 'Signal allowlist equality/refusal tests.',
 'tests/test_status.py': 'Entry named test_status_surfaces_confirmed_class_tombstones reaches status owner.'}


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in (*a['context'], *extra)))


def test_only_the_core_and_one_continuation_are_authored():
    assert BATCH == ('retro-drain-invoker', 'phase5-continue')
    assert REGISTRY['phase'] == 5
    assert tuple(REGISTRY['seeds']) == (
        'retro-drain-invoker', 'retro-box-activation', 'scorecard-reporting',
        'status-projection', 'baseline-binding-reader', 'retro-doctor-cli', 'phase5-exit',
    )
    assert REGISTRY['admissions'] == [
        ['retro-drain-invoker'], ['retro-box-activation'], ['scorecard-reporting'],
        ['status-projection', 'baseline-binding-reader'], ['retro-doctor-cli'], ['phase5-exit'],
    ]
    assert REGISTRY['admissions'][0] == [BATCH[0]]
    assert set(EDGES) == set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(BATCH)
    assert len(BATCH) == 2 <= MAX_SEEDS_PER_ADMISSION == 3


@pytest.mark.parametrize('stem', BATCH)
def test_confirmed_seed_birth_grammar_edges_and_budgets(stem):
    t = _ticket(stem)
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    capability = 'high' if stem == 'retro-drain-invoker' else 'medium'
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == (capability, capability)
    assert t.frontmatter.kind == 'feature' and t.frontmatter.priority == 'P1'
    assert not t.frontmatter.gate_bypass
    assert t.depends == EDGES[stem]
    assert t.expected_minutes == 60 < t.stuck_minutes == DRAIN_MAX_TICKET_MINUTES == 180


def test_citation_roles_and_both_required_entry_depths():
    core, continuation = (_ticket(s) for s in BATCH)
    assert core.plan_contract == ('19.I', '19.P5.retro-drain-invoker', '13', '14')
    assert '19.L' not in core.plan_contract and '19.P5' not in core.plan_contract
    assert continuation.plan_contract == (
        '19.L', '19.I', '19.P5', '19.P5.retro-box-activation', '12', '13',
    )
    assert set(VALIDATED_ENTRIES) == {'19.P5.retro-drain-invoker', '19.P5.retro-box-activation'}
    for uid, entry in VALIDATED_ENTRIES.items():
        assert entry['required'] and entry['resolves'] == 1 and entry['gap'] is None
        assert tuple(entry['parts']) == ('Owner', 'Records', 'Observable', 'Tests')
        assert all(n > 0 for n in entry['parts'].values())
        assert sum(entry['parts'].values()) < entry['chars'] == PLAN_CHARS[uid]
        assert re.fullmatch('[0-9a-f]{64}', entry['sha256'])
        assert entry['tests']
    assert REGISTRY['seeds']['retro-drain-invoker']['deep'] is True
    assert REGISTRY['seeds']['retro-box-activation']['deep'] is True
    assert REGISTRY['seeds']['retro-box-activation']['depends'] == ['retro-drain-invoker']
    assert REGISTRY['seeds']['retro-drain-invoker']['cite'] == [13, 14]
    assert REGISTRY['seeds']['retro-box-activation']['cite'] == [12]
    assert 'KNOWN-DEEP' in core.sections['Scope in / Scope out']
    assert 'KNOWN-DEEP high/high' in continuation.sections['Scope in / Scope out']


def test_all_named_entry_obligations_and_window_contract_are_carried():
    for stem, uid in zip(BATCH, VALIDATED_ENTRIES):
        scope = _ticket(stem).sections['Scope in / Scope out']
        for name in VALIDATED_ENTRIES[uid]['tests']:
            assert name in scope, (stem, name)
        assert 'test_plan_lint' in scope
    core = _ticket('retro-drain-invoker')
    scope = core.sections['Scope in / Scope out']
    for fact in ('chupa/retro.py', 'specs/retro.md', 'Stages.driver', 'Pipeline.stages',
                 'RetroConstructionError', 'session provider payload', 'MAIN lock',
                 'unforced dispatch', 'forced pre-exit/quiescence', 'retro_failed',
                 'ticket-plane Git/Effects', 'current retro window', 'EVENT_VERSIONS',
                 'canonical declaration', 'one shared pre-stage snapshot', 'exact envelopes',
                 'null-ticket events', 'different exit stems', 'arbitrary nonblank bounds',
                 'filesystem seam', 'without a live state directory'):
        assert fact in scope, fact
    assert set(AUTHORED[core.stem]['created']) == {
        'chupa/retro.py', 'specs/retro.md', 'tests/test_retro.py',
    }
    assert any('tests/test_retro.py' in argv for argv in core.verification)
    assert 'scorecard, proposal emission/Box activation and CLI verbs to later admissions' in scope


def test_continuation_position_suffix_seed_cap_and_future_consumption():
    t = _ticket('phase5-continue')
    scope = t.sections['Scope in / Scope out']
    assert POSITION == 1
    assert UNSEEDED_SUFFIX == tuple(tuple(a) for a in REGISTRY['admissions'][POSITION:])
    assert len(UNSEEDED_SUFFIX) == 5 and UNSEEDED_SUFFIX[-1] == ('phase5-exit',)
    assert 'Position 01 carries admissions[1:]' in scope
    for admission in UNSEEDED_SUFFIX:
        assert '- ' + ', '.join(admission) in scope
    assert 'author only retro-box-activation plus phase5-continue-02' in scope
    assert 'position 02 with admissions[2:]' in scope
    assert FUTURE_EDGES == {
        'retro-box-activation': ('phase5-continue', 'retro-drain-invoker'),
        'phase5-continue-02': ('retro-box-activation',),
    }
    assert set(FUTURE_EDGES['retro-box-activation']) <= set(BATCH)
    assert set(FUTURE_EDGES['phase5-continue-02']) == set(UNSEEDED_SUFFIX[0])
    assert 'No forward dependency' in scope
    assert 'only phase5-exit and no successor' in scope
    assert 'seeding.max_seeds_per_admission' in scope and 'drain.max_ticket_minutes' in scope
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase5_01.py')
    assert t.context == ('tests/test_seeded_phase3_core.py',) and t.on_demand == ()
    assert FUTURE_REQUIRED_TESTS == VALIDATED_ENTRIES['19.P5.retro-box-activation']['tests']
    assert set(FUTURE_FLOOR_ADDITIONS) == {
        'chupa/journal.py', 'tests/test_vocabularies.py', 'tests/test_status.py',
    }
    for path, reason in FUTURE_FLOOR_ADDITIONS.items():
        assert path in scope and reason
    for fact in ('required_units', 'resolve_plan_contract', 'entry_unit_gap',
                 'Owner, Records, Observable and Tests', 'kind: spec_gap',
                 'never copy their text', 'newly named test is a creation obligation',
                 'tombstone_auto_reopened', 'retro_ticket_authored',
                 'retro_prompt_spec_change_merged', 'production Box constructor',
                 'Retain approved bytes while ticket_sha matches', 're-author only snagged seeds',
                 'single ticket-plane seed lift'):
        assert fact in scope, fact


@pytest.mark.parametrize('stem', BATCH)
def test_earned_fence_and_context_partition(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert t.scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
    if stem == BATCH[0]:
        assert FENCE_FLOORS[stem] == tuple(REGISTRY['seeds'][stem]['fence'])
    assert all(reason and ('19.L' in reason or 'closure' in reason)
               for reason in FENCE_ADDITIONS[stem].values())
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert set(t.scope_fence) == set(a['fenced_existing']) | set(a['created'])
    assert not set(a['context']) & set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert not any(p.startswith('specs/') or p == 'CHUPA_PLAN.md' for p in a['context'])
    assert set(a['context']) | set(a['on_demand']) <= set(FILE_CHARS)
    for path in a['on_demand']:
        assert render_chars(stem, (path,)) > HEADROOM_CHARS, path


def test_closure_scan_and_forced_drain_scenarios_are_recorded():
    assert len(CLOSURE_PATTERNS) == 5
    assert all(re.fullmatch('[0-9a-f]{64}', source['sha256']) and source['lines']
               and all(n > 0 for n in source['lines']) for source in CLOSURE_SCAN.values())
    assert any(p.startswith('chupa/') for p in CLOSURE_SCAN)
    assert any(p.startswith('eval/') for p in CLOSURE_SCAN)
    assert any(p.startswith('tests/') for p in CLOSURE_SCAN)
    additions = FENCE_ADDITIONS['retro-drain-invoker']
    assert {'chupa/runner.py', 'chupa/daemon.py', 'chupa/journal.py',
            'tests/test_vocabularies.py'} <= set(additions)
    assert 'PreparedDispatch' in additions['chupa/runner.py']
    assert 'TicketWriter' in additions['chupa/daemon.py']
    assert 'retro_failed' in additions['chupa/journal.py']
    assert 'test_every_engine_signal_name_is_listed' in additions['tests/test_vocabularies.py']
    core = _ticket('retro-drain-invoker')
    verified = {part for argv in core.verification for part in argv if part.startswith('tests/')}
    for path, (mode, reason) in SCENARIOS.items():
        assert reason and mode in {'migration', 'preservation', 'shared migration'}
        assert path in verified
        if mode == 'migration':
            assert path in core.scope_fence
        else:
            assert path in PRESERVATION
            assert path not in (*core.scope_fence, *core.context, *core.on_demand)
            if mode == 'shared migration':
                assert 'tests/test_cli.py' in reason and 'tests/test_cli.py' in core.scope_fence
    assert 'HEAD~1' in additions['tests/test_drain_upgrade.py']
    assert 'five model calls' in additions['tests/test_seed_successor.py']
    assert 'Effects.run' in additions['tests/test_storm_notification_activation.py']
    for family in ('drain_reentry', 'drain_upgrade', 'kill_cli_activation', 'storm_hold',
                   'restart_timers', 'provider_cooldown_failover', 'watchdog_activation',
                   'daemon_pause', 'control_cli'):
        assert f'tests/test_{family}.py' in SCENARIOS


def test_maximum_effort_renders_use_only_fixed_authoring_snapshots():
    assert re.fullmatch('[0-9a-f]{40}', AUTHORING_HEAD)
    assert IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    assert set(FILE_CHARS) == set(FILE_BYTES)
    assert all(FILE_BYTES[p] >= FILE_CHARS[p] > 0 for p in FILE_CHARS)
    assert set(PLAN_CHARS) == {pid for a in AUTHORED.values() for pid in a['plan']}
    for stem, a in AUTHORED.items():
        assert a['bytes'] >= a['chars'] > 0
        assert re.fullmatch('[0-9a-f]{64}', a['birth_sha256'])
        assert _ticket(stem).plan_contract == a['plan']
        assert render_chars(stem) == a['max_effort_render']
        assert 0 < a['actual_max_effort_render'] <= render_chars(stem) <= HEADROOM_CHARS == 300_000
    assert render_chars('retro-drain-invoker') == 281199
    assert render_chars('phase5-continue') == 100487
    scope = _ticket('phase5-continue').sections['Scope in / Scope out']
    for fact in ('fixed authoring snapshots', 'never live sizes or plan lengths',
                 'Historical seeding snapshots remain immutable', 'On-demand is earned only',
                 'Created paths, same-admission sibling creations, prompt specs and delimiter-bearing files'):
        assert fact in scope
