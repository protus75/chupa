"""Phase 6 admission 1: historical authoring operands, never live-plan/size arithmetic.

The approved migration and successor bytes were retained. All entry resolution,
depth mutation checks and closure scans ran before the remaining seed was written.
Seed bytes remain ticket-plane output; Check owns approvals and their single lift.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]
RENDER_BOUND_CHARS = 400_000
REQ_RENDER_HEADROOM = 0.75
HEADROOM_CHARS = int(RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM)

AUTHORING_HEAD = '14c8e9e4ea3d4454092a6cc5368c39491959806d'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('core-drift-activation', 'migrate-config', 'phase6-continue-02')

PAYLOADS = ('core-drift-activation', 'migrate-config')

POSITION = 2

UNSEEDED_SUFFIX = (('host-contract-doc', 'fixture-host-scaffold'),
 ('bug-gate-grammar', 'report-inbox-triage'),
 ('escape-column',),
 ('supervised-merge-hold',),
 ('go-grade-machinery', 'go-grade-run'),
 ('exit-receipt-machinery',),
 ('phase6-exit',))

ROW_CONSUMPTION = {'core-drift-activation': ('core-drift-classifier',), 'migrate-config': ('core-renderer',)}

FENCE_FLOORS = {'core-drift-activation': ('chupa/hostfiles.py',
                           'chupa/gates.py',
                           'chupa/config.py',
                           'chupa/merge.py',
                           'chupa/providers.py',
                           'chupa/__main__.py',
                           'tests/test_hostfiles.py',
                           'tests/test_gates.py',
                           'tests/test_merge.py',
                           'tests/test_providers.py',
                           'tests/test_cli.py'),
 'migrate-config': ('chupa/config.py',
                    'chupa/__main__.py',
                    'tests/test_config.py',
                    'tests/test_cli.py'),
 'phase6-continue-02': ('tickets', 'tests/test_seeded_phase6_02.py')}

FENCE_ADDITIONS = {'core-drift-activation': ('CLAUDE.md',
                           'AGENTS.md',
                           'chupa/stages.py',
                           'tests/test_stages.py',
                           'tests/test_seed_path.py',
                           'tests/test_drain.py',
                           'tests/test_mergequeue.py',
                           'tests/test_terminal.py',
                           'tests/test_seed_successor.py',
                           'tests/test_daemon_soak.py',
                           'eval/daemon_soak.py',
                           'eval/reliability_battery.py',
                           'eval/shakeout/bench.py',
                           'tests/test_restart_timers.py'),
 'migrate-config': (),
 'phase6-continue-02': ()}

CLOSURE_EVIDENCE = {'CLAUDE.md': '19.P6.core-drift-activation Owner/Observable forces first adoption of the routed '
              'claude conduct file in the activation candidate.',
 'AGENTS.md': '19.P6.core-drift-activation Owner/Observable forces first adoption of the routed '
              'codex conduct file in the activation candidate.',
 'chupa/stages.py': 'CHECK_GATES at line 875 and check at line 1100 compose the production caller; '
                    'merge.py:351 and mergequeue.py:274 rerun that set.',
 'tests/test_stages.py': 'repo at line 162 commits CONFIG routing fake at line 97 without '
                         'AGENTS.md; test_implement_check_review_all_ok_with_artifacts_and_provenance and '
                         'test_outbox_only_check_accepts_registered_report require green Check.',
 'tests/test_seed_path.py': 'repo at line 41 builds its own fake-routed host; '
                            'test_two_approved_seeds_have_one_ticket_plane_commit_and_individual_reviews '
                            'at line 119 requires merged.',
 'tests/test_drain.py': 'make_root at line 70 commits a claude-routed host without CLAUDE.md; '
                        'production drain/rework tests consume this builder and require merges.',
 'tests/test_mergequeue.py': 'ctx at line 32 builds an independent fake-routed host; queue '
                             'integration runs stages.CHECK_GATES at mergequeue.py:274.',
 'tests/test_terminal.py': 'repo at line 27 independently commits the fake CONFIG; run drives '
                           'Check and merge and its terminal assertions must retain their intended '
                           'cause.',
 'tests/test_seed_successor.py': 'test_merged_parent_registers_and_runs_successor_in_same_drain at '
                                 'line 45 creates its own fake-routed initial dict and requires '
                                 'two production merges.',
 'tests/test_daemon_soak.py': 'test_daemon_soak_uses_registered_checks_lift at line 230 replaces '
                              'the root claude CONFIG with fake CONFIG at line 252 before '
                              'production Check.',
 'eval/daemon_soak.py': 'initialize at line 190 commits claude routing without CLAUDE.md, '
                        'then runs production pipelines through supervised serve.',
 'eval/reliability_battery.py': 'initialize at line 125 commits both codex and claude '
                                'routing without either conduct file before '
                                'runner.prepare_pipeline at line 149.',
 'eval/shakeout/bench.py': 'Bench.initialize at line 75 commits fake routing without AGENTS.md; '
                           'Bench._pipeline composes production bind/pipeline for the shakeout '
                           'battery.',
 'tests/test_restart_timers.py': 'repository at line 33 replaces the claude-only root routing with tests.test_providers '
                                 'CONFIG claude+codex routing without AGENTS.md; serve and recovery '
                                 'suites drive production Check and merge admission through it.'}

AUTHORED = {'core-drift-activation': {'bytes': 7317,
                           'chars': 7317,
                           'sha256': '3fa2bc7f97978f7ed30d67111fb65a6732817cab47784c0c12403ed4676748a2',
                           'plan': ('19.I',
                                    '19.P6.core-drift-activation',
                                    '19.P6.core-renderer',
                                    '19.P6.core-drift-classifier',
                                    '7',
                                    '8'),
                           'context': ('chupa/mergequeue.py',
                                       'chupa/seams.py',
                                       'chupa/stages.py',
                                       'tests/test_drain.py',
                                       'tests/test_mergequeue.py',
                                       'tests/test_merge.py',
                                       'tests/test_gates.py'),
                           'on_demand': ('chupa/hostfiles.py',
                                         'chupa/gates.py',
                                         'chupa/config.py',
                                         'chupa/merge.py',
                                         'chupa/providers.py',
                                         'chupa/__main__.py',
                                         'tests/test_hostfiles.py',
                                         'tests/test_providers.py',
                                         'tests/test_cli.py',
                                         'CLAUDE.md',
                                         'AGENTS.md',
                                         'tests/test_stages.py',
                                         'tests/test_seed_path.py',
                                         'tests/test_terminal.py',
                                         'tests/test_seed_successor.py',
                                         'tests/test_daemon_soak.py',
                                         'eval/daemon_soak.py',
                                         'eval/reliability_battery.py',
                                         'eval/shakeout/bench.py',
                                         'tests/test_restart_timers.py'),
                           'fence': ('chupa/hostfiles.py',
                                     'chupa/gates.py',
                                     'chupa/config.py',
                                     'chupa/merge.py',
                                     'chupa/providers.py',
                                     'chupa/__main__.py',
                                     'tests/test_hostfiles.py',
                                     'tests/test_gates.py',
                                     'tests/test_merge.py',
                                     'tests/test_providers.py',
                                     'tests/test_cli.py',
                                     'CLAUDE.md',
                                     'AGENTS.md',
                                     'chupa/stages.py',
                                     'tests/test_stages.py',
                                     'tests/test_seed_path.py',
                                     'tests/test_drain.py',
                                     'tests/test_mergequeue.py',
                                     'tests/test_terminal.py',
                                     'tests/test_seed_successor.py',
                                     'tests/test_daemon_soak.py',
                                     'eval/daemon_soak.py',
                                     'eval/reliability_battery.py',
                                     'eval/shakeout/bench.py',
                                         'tests/test_restart_timers.py'),
                           'depends': ('phase6-continue', 'core-drift-classifier'),
                           'expected': 60,
                           'stuck': 90,
                           'actual_render': 297714,
                           'render_overhead': 121},
 'migrate-config': {'bytes': 3832,
                    'chars': 3832,
                    'sha256': '88f806b1f2a1537ffbc21814e058fe28c261468956e824cda2efd5b123b281ec',
                    'plan': ('19.I', '19.P6.migrate-config', '15'),
                    'context': ('chupa/config.py',
                                'chupa/__main__.py',
                                'tests/test_config.py',
                                'tests/test_cli.py',
                                'chupa/seams.py'),
                    'on_demand': (),
                    'fence': ('chupa/config.py',
                              'chupa/__main__.py',
                              'tests/test_config.py',
                              'tests/test_cli.py'),
                    'depends': ('phase6-continue', 'core-renderer'),
                    'expected': 60,
                    'stuck': 90,
                    'actual_render': 107106,
                    'render_overhead': 61},
 'phase6-continue-02': {'bytes': 6370,
                        'chars': 6370,
                        'sha256': '92cf2898668d9bd3c47d52250b152d314aa23d55c65c82d084ea417536bfe7c1',
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P6',
                                 '13',
                                 '19.P6.host-contract-doc',
                                 '19.P6.fixture-host-scaffold',
                                 '19.P6.core-drift-activation',
                                 '15',
                                 '19.P6.bug-gate-grammar',
                                 '19.P6.report-inbox-triage',
                                 '7',
                                 '12'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fence': ('tickets', 'tests/test_seeded_phase6_02.py'),
                        'depends': ('core-drift-activation', 'migrate-config'),
                        'expected': 60,
                        'stuck': 90,
                        'actual_render': 142114,
                        'render_overhead': -18}}

REQUIRED = {'core-drift-activation': ('19.P6.core-drift-activation',
                           '19.P6.core-renderer',
                           '19.P6.core-drift-classifier'),
 'migrate-config': ('19.P6.migrate-config',),
 'phase6-continue-02': ('19.P6.host-contract-doc',
                        '19.P6.fixture-host-scaffold',
                        '19.P6.core-drift-activation',
                        '19.P6.bug-gate-grammar',
                        '19.P6.report-inbox-triage')}

ENTRY_DEPTH = {'19.P6.core-drift-activation': {'bytes': 6515,
                                 'chars': 6515,
                                 'sha256': '9fa122a8968296fc759d3f0ca60fc3da7b697870516ab34b420acd2049707011',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 1232,
                                           'Records': 1800,
                                           'Observable': 1235,
                                           'Tests': 2124},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'tests': ('test_hostfiles',
                                           'test_core_activation_entry_unit',
                                           'test_core_classifier_unreachable_from_production_gates',
                                           'test_core_drift_reachable_from_production_gates',
                                           'test_gates',
                                           'test_core_drift_gate_reports',
                                           'test_core_drift_default_hard',
                                           'test_merge',
                                           'test_core_drift_merge_rerun',
                                           'test_core_drift_candidate_template',
                                           'test_providers',
                                           'test_routed_conduct_paths',
                                           'test_cli',
                                           'test_core_and_gate_share_routed_paths',
                                           'test_core_activation_first_adoption',
                                           'test_core_activation_committed_conduct',
                                           'test_core_activation_first_adoption_merge')},
 '19.P6.core-renderer': {'bytes': 4415,
                         'chars': 4415,
                         'sha256': '5c3e4e5b41a70d3762b7d68d3da52e4fae07ef15ac452a8165e06300b580727f',
                         'resolves': 1,
                         'gap': None,
                         'parts': {'Owner': 656, 'Records': 1399, 'Observable': 742, 'Tests': 1486},
                         'missing_part_rejected': {'Owner': True,
                                                   'Records': True,
                                                   'Observable': True,
                                                   'Tests': True},
                         'tests': ('test_hostfiles',
                                   'test_renderer_entry_unit',
                                   'test_core_first_adoption_preserves_project_bytes',
                                   'test_core_refresh_preserves_remainder',
                                   'test_core_marker_corruption_refuses_without_writes',
                                   'test_core_render_is_byte_idempotent',
                                   'test_core_golden_uses_branch_template',
                                   'test_cli',
                                   'test_core_routed_conduct_files',
                                   'test_core_refusal_and_no_git')},
 '19.P6.core-drift-classifier': {'bytes': 4211,
                                 'chars': 4211,
                                 'sha256': '1f5ad897c314b376776104dcbdf555fd81f3b402628fedeec3d40a345a0a01b8',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 414,
                                           'Records': 1610,
                                           'Observable': 657,
                                           'Tests': 1393},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'tests': ('test_hostfiles',
                                           'test_classifier_entry_unit',
                                           'test_core_drift_classification',
                                           'test_core_drift_refuses_marker_corruption',
                                           'test_core_remainder_process_refusals',
                                           'test_core_remainder_accepts_project_rules',
                                           'test_core_drift_uses_branch_render',
                                           'test_core_classifier_is_pure',
                                           'test_core_classifier_unreachable_from_production_gates')},
 '19.P6.migrate-config': {'bytes': 3596,
                          'chars': 3596,
                          'sha256': 'ccee47e8964daeb1d0b2a128a2b3b25011890fe09ca3db5c0e05387cb946c267',
                          'resolves': 1,
                          'gap': None,
                          'parts': {'Owner': 401,
                                    'Records': 1122,
                                    'Observable': 736,
                                    'Tests': 1216},
                          'missing_part_rejected': {'Owner': True,
                                                    'Records': True,
                                                    'Observable': True,
                                                    'Tests': True},
                          'tests': ('test_config',
                                    'test_migrate_config_entry_unit',
                                    'test_migrate_config_zero_to_one',
                                    'test_migrate_config_validates_before_write',
                                    'test_migrate_config_current_is_noop',
                                    'test_migrate_config_refuses_unsupported_inputs',
                                    'test_older_schema_version_is_refused_naming_migrate_config',
                                    'test_cli',
                                    'test_migrate_config_before_load')},
 '19.P6.host-contract-doc': {'bytes': 3729,
                             'chars': 3729,
                             'sha256': 'd6f8fd4ccfae12e9428ee8ffa7d2c25261b22aa35fd251f9347faa06cd75f601',
                             'resolves': 1,
                             'gap': None,
                             'parts': {'Owner': 370,
                                       'Records': 1447,
                                       'Observable': 738,
                                       'Tests': 1034},
                             'missing_part_rejected': {'Owner': True,
                                                       'Records': True,
                                                       'Observable': True,
                                                       'Tests': True},
                             'tests': ('test_host_contract',
                                       'test_host_contract_entry_unit',
                                       'test_host_contract_example_loads',
                                       'test_host_contract_schema_coverage',
                                       'test_host_contract_migration_and_managed_ownership',
                                       'test_host_contract_seam_inventory',
                                       'test_host_contract_report_custody_and_cutover')},
 '19.P6.fixture-host-scaffold': {'bytes': 4901,
                                 'chars': 4901,
                                 'sha256': '6d539213afac5a50c8fe3065bf3fdf1c32c87cc6a0d24145b978e04d7a9b081e',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 681,
                                           'Records': 1346,
                                           'Observable': 1329,
                                           'Tests': 1410},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'tests': ('test_fixture_host',
                                           'test_fixture_host_entry_units',
                                           'test_fixture_profile_loads',
                                           'test_fixture_scenario_list_is_closed',
                                           'test_fixture_replay_is_deterministic',
                                           'test_fixture_regression_exists_at_base',
                                           'test_fixture_escape_is_machine_introduced',
                                           'test_fixture_reports_are_bounded',
                                           'test_fixture_cli_adapter_roundtrip',
                                           'test_fixture_scaffold_is_dormant')},
 '19.P6.bug-gate-grammar': {'bytes': 3922,
                            'chars': 3922,
                            'sha256': 'c5432aed7a4f2665a06b7cebf5ef759fc4cc793f7c7231bee8945b9fb8cd1db2',
                            'resolves': 1,
                            'gap': None,
                            'parts': {'Owner': 498,
                                      'Records': 1523,
                                      'Observable': 605,
                                      'Tests': 1165},
                            'missing_part_rejected': {'Owner': True,
                                                      'Records': True,
                                                      'Observable': True,
                                                      'Tests': True},
                            'tests': ('test_tickets',
                                      'test_bug_ticket_with_regression_validates',
                                      'test_grammar_refusals',
                                      'test_bug_gate',
                                      'test_bug_gate_entry_units',
                                      'test_regression_overlay_proves_defect',
                                      'test_passing_new_test_is_not_bug_evidence',
                                      'test_missing_base_input_is_not_bug_evidence',
                                      'test_bug_gate_requires_evidence',
                                      'test_bug_gate_rejects_red_head',
                                      'test_bug_gate_refuses_invalid_carries',
                                      'test_bug_gate_execution_failure_is_closed',
                                      'test_bug_gate_check_wiring',
                                      'test_bug_gate_base_cleanup')},
 '19.P6.report-inbox-triage': {'bytes': 6470,
                               'chars': 6470,
                               'sha256': '7554e633033b41150ec51622d0537929a1773626b8f0a936893f58a38972df0a',
                               'resolves': 1,
                               'gap': None,
                               'parts': {'Owner': 843,
                                         'Records': 2507,
                                         'Observable': 1337,
                                         'Tests': 1643},
                               'missing_part_rejected': {'Owner': True,
                                                         'Records': True,
                                                         'Observable': True,
                                                         'Tests': True},
                               'tests': ('test_inbox',
                                         'test_report_inbox_entry_units',
                                         'test_report_schema_is_closed',
                                         'test_report_evidence_bounds',
                                         'test_report_custody_precedes_enqueue',
                                         'test_report_retry_ingests_once',
                                         'test_box',
                                         'test_host_report_signature',
                                         'test_triage',
                                         'test_report_ingested_before_pending_scan',
                                         'test_serve',
                                         'test_empty_box_report_intake',
                                         'test_report_consumer_is_sequential',
                                         'test_author',
                                         'test_bug_report_evidence_ticket_plane_commit',
                                         'test_bug_report_text_stays_untrusted',
                                         'test_report_author_failure_is_decision',
                                         'test_report_replay_to_regression')}}

PLAN_SIZES = {'19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P6.core-drift-activation': {'bytes': 6515,
                                 'chars': 6515,
                                 'sha256': '9fa122a8968296fc759d3f0ca60fc3da7b697870516ab34b420acd2049707011'},
 '19.P6.core-renderer': {'bytes': 4415,
                         'chars': 4415,
                         'sha256': '5c3e4e5b41a70d3762b7d68d3da52e4fae07ef15ac452a8165e06300b580727f'},
 '19.P6.core-drift-classifier': {'bytes': 4211,
                                 'chars': 4211,
                                 'sha256': '1f5ad897c314b376776104dcbdf555fd81f3b402628fedeec3d40a345a0a01b8'},
 '7': {'bytes': 8173,
       'chars': 8173,
       'sha256': '5946c32455a2d8859111c4b56e2674de365f2e60da9eeb1b98776ba3c4f6e2c7'},
 '8': {'bytes': 8712,
       'chars': 8712,
       'sha256': '7024a6dc821bad113cc141046646426ee3c397bc3f877f27bbf2dae6b5e53ae1'},
 '19.P6.migrate-config': {'bytes': 3596,
                          'chars': 3596,
                          'sha256': 'ccee47e8964daeb1d0b2a128a2b3b25011890fe09ca3db5c0e05387cb946c267'},
 '15': {'bytes': 17253,
        'chars': 17253,
        'sha256': 'ece80fdf277f4a2b4786623e8d359f0aa1d3a9fba489a3706e241cdd5bb3d3ad'},
 '19.L': {'bytes': 20912,
          'chars': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa'},
 '19.P6': {'bytes': 11595,
           'chars': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c'},
 '13': {'bytes': 19840,
        'chars': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P6.host-contract-doc': {'bytes': 3729,
                             'chars': 3729,
                             'sha256': 'd6f8fd4ccfae12e9428ee8ffa7d2c25261b22aa35fd251f9347faa06cd75f601'},
 '19.P6.fixture-host-scaffold': {'bytes': 4901,
                                 'chars': 4901,
                                 'sha256': '6d539213afac5a50c8fe3065bf3fdf1c32c87cc6a0d24145b978e04d7a9b081e'},
 '19.P6.bug-gate-grammar': {'bytes': 3922,
                            'chars': 3922,
                            'sha256': 'c5432aed7a4f2665a06b7cebf5ef759fc4cc793f7c7231bee8945b9fb8cd1db2'},
 '19.P6.report-inbox-triage': {'bytes': 6470,
                               'chars': 6470,
                               'sha256': '7554e633033b41150ec51622d0537929a1773626b8f0a936893f58a38972df0a'},
 '12': {'bytes': 20224,
        'chars': 20224,
        'sha256': 'd3917109abd72822abd53cfadc7c74913fb6186ba72191820d0600c26cfac8cb'}}

FILE_SIZES = {'chupa/hostfiles.py': {'bytes': 7442,
                        'chars': 7442,
                        'sha256': '481fbcee2b635355c90fc2caf366bcf28df96b10b498dab208495e087d7eac9a'},
 'chupa/gates.py': {'bytes': 4945,
                    'chars': 4945,
                    'sha256': 'e84959455efe288a354c0a29f771ed3671a7b6f4e6783ae3008407f949dce59f'},
 'chupa/config.py': {'bytes': 12245,
                     'chars': 12245,
                     'sha256': 'f7f8f3e3855ff958a9d1ee5e2fd3fd87f02978cad6cfa83952dc64d0546c82cf'},
 'chupa/merge.py': {'bytes': 21717,
                    'chars': 21717,
                    'sha256': '83efe01c4a2013046f69da93037a6a4b6e362c5fd3a79e0faa08f74d0f06504c'},
 'chupa/providers.py': {'bytes': 27676,
                        'chars': 27676,
                        'sha256': '4f0bc7d61dc8a342a7bfce60e7442b7186a12d1a12a23510b01ba7bc3f32f77e'},
 'chupa/__main__.py': {'bytes': 19473,
                       'chars': 19473,
                       'sha256': 'cc8e80e268ebd637199d67e3844a42011b4b5be4caf51c06cd8547e0c2a2c850'},
 'tests/test_hostfiles.py': {'bytes': 18915,
                             'chars': 18915,
                             'sha256': '338f53d7c33b4a2a5891bcb2d45621a23f3c36db51f1ec2df3c0c25fdde2b68b'},
 'tests/test_gates.py': {'bytes': 7724,
                         'chars': 7724,
                         'sha256': 'd3e72fb8dd8069a7da7447dec15face5af91fe97b5930341af591f102aef81e9'},
 'tests/test_merge.py': {'bytes': 39739,
                         'chars': 39739,
                         'sha256': 'fb09ae48356c3f8864d918fcf96ccee70b55732ce859af7a0235882771006028'},
 'tests/test_providers.py': {'bytes': 38656,
                             'chars': 38654,
                             'sha256': '1da55805d0df5ec272f353a798c5af0e7eb20944aced3d1ec7e4fde41261d98a'},
 'tests/test_cli.py': {'bytes': 24198,
                       'chars': 24198,
                       'sha256': '5c207ccf2317d1378358dd0dba3d558db9ca632de93bd7f69077885fbcb55457'},
 'CLAUDE.md': {'bytes': 9078,
               'chars': 9078,
               'sha256': '0700c91717de549e480c1cc19db385556115924ff1bb075e297be09bfc80aaef'},
 'AGENTS.md': {'bytes': 3808,
               'chars': 3808,
               'sha256': '2664f2064d2a4c820b0947e1d6bacefd6617641f23664f10d3c93e0bf55a2c1a'},
 'chupa/stages.py': {'bytes': 63065,
                     'chars': 63065,
                     'sha256': '87ded1b415e8051504bc1227af6ac8c2ed434ba53102af14fc918cfb1d902935'},
 'tests/test_stages.py': {'bytes': 34579,
                          'chars': 34579,
                          'sha256': '11fca05abbb5881ca288ec22a1d4d5e95bfe974900b01c983bbf98cafffdab77'},
 'tests/test_seed_path.py': {'bytes': 38877,
                             'chars': 38877,
                             'sha256': '3e3e3f041c87365c633190193c08aa2cc02467e44ecd1bfa7fd8f9e952010a5b'},
 'tests/test_drain.py': {'bytes': 61057,
                         'chars': 61057,
                         'sha256': 'ddb0d970d7e13fa679ef103f79a60dfb47afe098e1a2c5bf10452c0535157b10'},
 'tests/test_mergequeue.py': {'bytes': 53452,
                              'chars': 53452,
                              'sha256': 'd3a690502df5c631cb16c31eabe4756e5ecb95f591034f6bc742c2e87a0adf4b'},
 'tests/test_terminal.py': {'bytes': 6165,
                            'chars': 6165,
                            'sha256': '4fd0c9becbaf421a6f1b153cd3cb607c753f370fca6a615aa7b89332a780063a'},
 'tests/test_seed_successor.py': {'bytes': 12131,
                                  'chars': 12131,
                                  'sha256': '636f04a4e14fe20241f021c496a30fcbdf904197ac40ef019b7924eea7c3c239'},
 'tests/test_daemon_soak.py': {'bytes': 17690,
                               'chars': 17687,
                               'sha256': '958377f244eb5f8c9fb65fa000178c06c3826bf82950d4a9f71f762c49f83682'},
 'eval/daemon_soak.py': {'bytes': 36204,
                         'chars': 36204,
                         'sha256': 'cb4d3903d85b11cd3d2771b7db27f29b9add770702e3138211f613e672f75e98'},
 'eval/reliability_battery.py': {'bytes': 23709,
                                 'chars': 23709,
                                 'sha256': '2e42e1e58c22691435e1ce58daab5e1d355fc7abc9f8dac9ac6dfc4aad912d61'},
 'tests/test_restart_timers.py': {'bytes': 33950,
                                 'chars': 33950,
                                 'sha256': 'bb8a3efb5951fd8af7a872ccc65ca001f77d64ee8bd1776b8346a8e21a9b4200'},
 'eval/shakeout/bench.py': {'bytes': 5063,
                            'chars': 5063,
                            'sha256': '8e7c10805ec6ae5de47618b15d80f4e4a84b05aa39155405cd50f7db55833701'},
 'chupa/mergequeue.py': {'bytes': 16262,
                         'chars': 16262,
                         'sha256': 'f5e150bf011a5b1e1d091a261a4eb2982ab261b7312652ba659266d78b19af56'},
 'chupa/seams.py': {'bytes': 10148,
                    'chars': 10148,
                    'sha256': 'c465a54f053a4330f63abdcc0471747714f0d54147d070b79d9a98af213a0673'},
 'tests/test_config.py': {'bytes': 9497,
                          'chars': 9497,
                          'sha256': 'd757880b574b2c60f150fc00ca7cc50dc78b2af6dd8748853fdc3e9a6db938e2'},
 'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559'}}

DELIMITER_FREE_CONTEXT = {'chupa/hostfiles.py': True,
 'chupa/gates.py': True,
 'chupa/config.py': True,
 'chupa/merge.py': True,
 'chupa/providers.py': True,
 'chupa/__main__.py': True,
 'tests/test_hostfiles.py': True,
 'tests/test_gates.py': True,
 'tests/test_merge.py': True,
 'tests/test_providers.py': True,
 'tests/test_cli.py': True,
 'CLAUDE.md': True,
 'AGENTS.md': True,
 'chupa/stages.py': True,
 'tests/test_stages.py': True,
 'tests/test_seed_path.py': True,
 'tests/test_drain.py': True,
 'tests/test_mergequeue.py': True,
 'tests/test_terminal.py': True,
 'tests/test_seed_successor.py': True,
 'tests/test_daemon_soak.py': True,
 'eval/daemon_soak.py': False,
 'eval/reliability_battery.py': False,
 'eval/shakeout/bench.py': True,
 'chupa/mergequeue.py': True,
 'chupa/seams.py': True,
 'tests/test_config.py': True,
 'tests/test_seeded_phase3_core.py': True}

IMPLEMENT_SPEC_SIZE = {'bytes': 5113,
 'chars': 5113,
 'sha256': '99062ce8142c9abe06c224098b01d6899d3ddf8b7019aec0bc09da1e9d15fb43'}

IMPLEMENT_BODY_CHARS = 4992

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

SCAN_PATTERN = ('hostfiles|core_drift|CHECK_GATES|MERGE_GATES|not hasattr|__all__|allowlist|def __init__|^def '
 '|^async def |^class |compose|prepare_pipeline|run_stages|git.init|"init"')

CLOSURE_SCAN = {'chupa': {'matched_lines': 607,
           'bytes': 42894,
           'chars': 42894,
           'sha256': '0bb1cf120a4504be91619fe96a613c0070dcf3cca9b35f9d576077d7ecbc2b62',
           'files': 52},
 'eval': {'matched_lines': 128,
          'bytes': 9273,
          'chars': 9273,
          'sha256': 'ed56c29c0f27cb347256c69ed718b76f671a1b6db59ec5e2c34b7dda575de24a',
          'files': 13},
 'tests': {'matched_lines': 2335,
           'bytes': 211861,
           'chars': 211861,
           'sha256': '78f1a4340994188445af5670bf3054493275ffea3c178eddbba8838599e1091d',
           'files': 129}}

IMPORT_CLOSURE = {'test_stages': ('tests/test_audit.py:6: from tests.test_stages import agent, implement_reply, '
                 'verdict',
                 'tests/test_daemon_composition.py:1084: from tests.test_stages import agent, '
                 'verdict',
                 'tests/test_daemon_composition.py:1921: from tests.test_stages import STEM, '
                 'TICKET, agent, verdict',
                 'tests/test_daemon_soak.py:36: from tests.test_stages import CONFIG, STEM, TICKET',
                 'tests/test_diagnose.py:21: from tests.test_stages import ENV, SNAG, STEM, agent, '
                 'git, verdict',
                 'tests/test_drain.py:484: from tests.test_stages import ENV, SNAG, STEM, agent, '
                 'verdict',
                 'tests/test_drain.py:547: from tests.test_stages import ENV, SNAG, STEM, agent, '
                 'verdict',
                 'tests/test_drain.py:613: from tests.test_stages import ENV, STEM, agent, verdict',
                 'tests/test_drain_reentry.py:19: from tests.test_stages import ENV, SNAG, STEM, '
                 'agent, git, verdict',
                 'tests/test_hardening.py:110: from tests.test_stages import STEM, git',
                 'tests/test_hardening.py:151: from tests.test_stages import STEM',
                 'tests/test_harvest.py:16: from tests.test_stages import ENV, SNAG, STEM, agent, '
                 'git, verdict',
                 'tests/test_harvest_orphans.py:12: from tests.test_stages import ENV, STEM, '
                 'agent, git, verdict',
                 'tests/test_hostfiles.py:17: from tests.test_stages import agent, verdict',
                 'tests/test_kill_cli_activation.py:27: from tests.test_stages import agent, '
                 'implement_reply, verdict',
                 'tests/test_ladder.py:14: from tests.test_stages import ENV, SNAG, STEM, agent, '
                 'git, verdict',
                 'tests/test_merge.py:25: from tests.test_stages import ENV, SNAG, SPECS, STEM, '
                 'agent, author, git, verdict',
                 'tests/test_merge.py:27: from tests.test_stages import report_context, '
                 '_report_bytes',
                 'tests/test_merge.py:525: from tests.test_stages import TICKET',
                 'tests/test_merge.py:694: from tests.test_stages import implement_reply',
                 'tests/test_mergequeue.py:26: from tests.test_stages import CONFIG, ENV, SECRET, '
                 'SPECS, STEM, TICKET',
                 'tests/test_reject_queue.py:20: from tests.test_stages import STEM',
                 'tests/test_requisition.py:154: from tests.test_stages import implement_reply',
                 'tests/test_retro_box.py:25: from tests.test_stages import implement_reply, '
                 'verdict',
                 'tests/test_rework.py:25: from tests.test_stages import TICKET',
                 'tests/test_scorecard.py:22: from tests.test_stages import implement_reply',
                 'tests/test_second_problems.py:13: from tests.test_stages import ENV, STEM, '
                 'agent, verdict',
                 'tests/test_seed_path.py:21: from tests.test_stages import CONFIG, ENV, STEM, '
                 'TICKET, git, implement_reply, verdict',
                 'tests/test_seed_successor.py:18: from tests.test_stages import CONFIG, ENV, '
                 'TICKET, implement_reply, verdict',
                 'tests/test_serve.py:783: from tests.test_stages import implement_reply, verdict, '
                 'SNAG',
                 'tests/test_serve.py:841: from tests.test_stages import TICKET',
                 'tests/test_storm_notification_activation.py:27: from tests.test_stages import '
                 'STEM, agent',
                 'tests/test_storm_producer.py:20: from tests.test_stages import STEM, TICKET, '
                 'agent, verdict',
                 'tests/test_terminal.py:19: from tests.test_stages import CONFIG, ENV, SNAG, '
                 'STEM, TICKET, agent, git, implement_reply, verdict'),
 'test_seed_path': ('tests/test_hardening.py:12: from tests.test_seed_path import repo, '
                    'add_registry_row, context, ticket, terminal_body',
                    'tests/test_merge.py:23: from tests.test_seed_path import (context as '
                    'seed_context, repo as seed_repo, requisition, seed_text,'),
 'test_drain': ('tests/test_author.py:13: from tests.test_drain import Clock, commit_ticket, '
                'confirmed, make_root',
                'tests/test_baseline.py:15: from tests.test_drain import Clock',
                'tests/test_box.py:140: from tests.test_drain import Clock, commit_ticket, '
                'confirmed',
                'tests/test_box.py:200: from tests.test_drain import Clock',
                'tests/test_box.py:236: from tests.test_drain import Clock',
                'tests/test_box.py:283: from tests.test_drain import Clock',
                'tests/test_caps.py:15: from tests.test_drain import Clock, Script, commit_ticket, '
                'confirmed, drain, journal, make_root',
                'tests/test_daemon_composition.py:1345: from tests.test_drain import Clock, '
                'journal',
                'tests/test_daemon_composition.py:1438: from tests.test_drain import confirmed, '
                'offer_events',
                'tests/test_daemon_composition.py:1483: from tests.test_drain import confirmed, '
                'offer_events',
                'tests/test_daemon_composition.py:1493: from tests.test_drain import round_record',
                'tests/test_daemon_composition.py:1540: from tests.test_drain import confirmed',
                'tests/test_daemon_composition.py:1680: from tests.test_drain import confirmed',
                'tests/test_daemon_pause.py:15: from tests.test_drain import Script, journal',
                'tests/test_diagnose.py:193: from tests.test_drain import mechanical_first',
                'tests/test_drain_upgrade.py:22: from tests.test_drain import Clock, '
                'commit_ticket, confirmed, journal, make_root, retry_draws, tos',
                'tests/test_kill_cli_activation.py:23: from tests.test_drain import confirmed, '
                'offer_events',
                'tests/test_phase5_exit.py:325: from tests.test_drain import '
                'test_drain_retro_due_quiescence_and_pre_exit as forced',
                'tests/test_reject_queue.py:17: from tests.test_drain import Clock, Script, '
                'commit_ticket, confirmed, drain, journal, make_root',
                'tests/test_reject_queue.py:18: from tests.test_drain import bound_arrival, '
                'commit_plan',
                'tests/test_retro.py:20: from tests.test_drain import Clock, make_root, '
                'pause_checkout, confirmed, commit_ticket',
                'tests/test_retro_box.py:24: from tests.test_drain import pause_checkout',
                'tests/test_scorecard.py:20: from tests.test_drain import confirmed',
                'tests/test_stages.py:40: from tests.test_drain import pause_checkout',
                'tests/test_status.py:22: from tests.test_drain import Clock, make_root',
                'tests/test_storm_hold.py:22: from tests.test_drain import Script, commit_ticket, '
                'confirmed, make_root, pause_checkout',
                'tests/test_storm_notification_activation.py:23: from tests.test_drain import '
                'Script, commit_ticket, confirmed, make_root',
                'tests/test_triage.py:15: from tests.test_drain import Clock, commit_ticket, '
                'confirmed, make_root'),
 'test_cli': ('tests/test_author.py:12: from tests.test_cli import ENV, git_out',
              'tests/test_caps.py:14: from tests.test_cli import git_out',
              'tests/test_checkpoint.py:21: from tests.test_cli import Clock, ENV, Stages, root, '
              'ticket, write',
              'tests/test_control.py:16: from tests.test_cli import Stages, cli, journal, root, '
              'ticket, write',
              'tests/test_control_cli.py:13: from tests.test_cli import Clock, ENV, Stages, root, '
              'ticket, write',
              'tests/test_daemon_admission.py:13: from tests.test_cli import ENV, PLAN, Clock, '
              'root, ticket, write, with_retro_driver',
              'tests/test_daemon_composition.py:25: from tests.test_cli import PLAN, root, write',
              'tests/test_daemon_composition.py:1346: from tests.test_cli import ENV as '
              'checkout_env',
              'tests/test_daemon_composition.py:1735: from tests.test_cli import Clock, ENV as '
              'checkout_env',
              'tests/test_daemon_config.py:16: from tests.test_cli import ENV, Clock, root, '
              'ticket, write, with_retro_driver',
              'tests/test_daemon_pause.py:11: from tests.test_cli import CONFIG, ENV, Clock, root, '
              'ticket, write',
              'tests/test_daemon_soak.py:33: from tests.test_cli import ENV, root',
              'tests/test_daemon_tasks.py:14: from tests.test_cli import ENV, Clock, Stages, root, '
              'ticket, write',
              'tests/test_doctor.py:13: from tests.test_cli import root, ENV, Clock, journal',
              'tests/test_drain.py:23: from tests.test_cli import CONFIG, ENV, PLAN, git_out, '
              'ticket, write, with_retro_driver',
              'tests/test_drain_upgrade.py:21: from tests.test_cli import ENV, git_out, '
              'with_retro_driver',
              'tests/test_flake.py:16: from tests.test_cli import Clock, ENV, Stages, root, '
              'ticket, write',
              'tests/test_heartbeat.py:15: from tests.test_cli import ENV, Clock, Stages, root, '
              'ticket, write',
              'tests/test_kill_cli_activation.py:20: from tests.test_cli import ENV, Clock, '
              'Stages, root, write',
              'tests/test_kill_executor_abort.py:11: from tests.test_cli import root',
              'tests/test_kill_failure_suppression.py:14: from tests.test_cli import ENV, Clock, '
              'Stages, root, ticket, write',
              'tests/test_kill_signal_journal.py:14: from tests.test_cli import root',
              'tests/test_kill_worker_stop.py:11: from tests.test_cli import ENV, Clock, Stages, '
              'root, ticket, write',
              'tests/test_merge.py:26: from tests.test_cli import root',
              'tests/test_provider_cooldown_failover.py:26: from tests.test_cli import root, '
              'write, PLAN',
              'tests/test_reconcile.py:15: from tests.test_cli import ENV, Clock, Stages, cli, '
              'git_out, journal, root, ticket, write  # noqa: F401',
              'tests/test_reject_queue.py:16: from tests.test_cli import ENV, git_out',
              'tests/test_restart_timers.py:19: from tests.test_cli import ENV, PLAN, root',
              'tests/test_scheduler.py:15: from tests.test_cli import PLAN, TICKET',
              'tests/test_serve.py:25: from tests.test_cli import ENV, PLAN, root, write',
              'tests/test_status.py:21: from tests.test_cli import ENV',
              'tests/test_storm_hold.py:20: from tests.test_cli import ENV',
              'tests/test_storm_notification_activation.py:19: from tests.test_cli import ENV',
              'tests/test_triage.py:14: from tests.test_cli import ENV, git_out',
              'tests/test_watchdog_activation.py:17: from tests.test_cli import root, write'),
 'test_mergequeue': ('tests/test_daemon_composition.py:30: from tests.test_mergequeue import ctx '
                     'as admission_context, ready',
                     'tests/test_daemon_composition.py:1083: from tests.test_mergequeue import '
                     'conflict',
                     'tests/test_daemon_composition.py:1160: from tests.test_mergequeue import '
                     'commit',
                     'tests/test_daemon_composition.py:1804: from tests.test_mergequeue import '
                     'host, scripted',
                     'tests/test_daemon_tasks.py:16: from tests.test_mergequeue import ctx as '
                     'admission_context, ready',
                     'tests/test_kill_failure_suppression.py:20: from tests.test_mergequeue import '
                     'ctx as admission_context, ready',
                     'tests/test_restart_timers.py:285: from tests.test_mergequeue import ready',
                     'tests/test_rework.py:24: from tests.test_mergequeue import commit, conflict, '
                     'ctx, import_closure',
                     'tests/test_serve.py:600: from tests.test_mergequeue import ready',
                     'tests/test_storm_notification_activation.py:26: from tests.test_mergequeue '
                     'import ctx as admission_context, ready, scripted',
                     'tests/test_storm_producer.py:19: from tests.test_mergequeue import ctx as '
                     'admission_context  # noqa: F401')}

COPY_VIOLATIONS = ()


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_BODY_CHARS + a["chars"] + a["render_overhead"]
            + sum(PLAN_SIZES[i]["chars"] for i in a["plan"])
            + sum(FILE_SIZES[p]["chars"] for p in (*a["context"], *extra)))


def test_phase6_01_exact_admission():
    assert BATCH == ("core-drift-activation", "migrate-config", "phase6-continue-02")
    assert PAYLOADS == BATCH[:2] and len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert POSITION == 2
    assert UNSEEDED_SUFFIX == (
        ("host-contract-doc", "fixture-host-scaffold"),
        ("bug-gate-grammar", "report-inbox-triage"), ("escape-column",),
        ("supervised-merge-hold",), ("go-grade-machinery", "go-grade-run"),
        ("exit-receipt-machinery",), ("phase6-exit",))
    assert set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(BATCH)
    for stem in BATCH:
        t, a = _ticket(stem), AUTHORED[stem]
        assert (t.frontmatter.source, t.frontmatter.state) == ("seed", "confirmed")
        assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("medium", "medium")
        assert t.plan_contract == a["plan"]
        assert t.depends == a["depends"]
        assert (t.expected_minutes, t.stuck_minutes) == (a["expected"], a["stuck"])
        assert t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES
        assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
        if stem in PAYLOADS:
            assert set(t.depends) == {"phase6-continue", *ROW_CONSUMPTION[stem]}
            assert {"19.I", "19.P6." + stem} <= set(t.plan_contract)
            assert not {"19.L", "19.P6"} & set(t.plan_contract)
        else:
            assert set(t.depends) == set(PAYLOADS)
            assert {"19.L", "19.I", "19.P6", "13", "19.P6.host-contract-doc",
                    "19.P6.fixture-host-scaffold", "19.P6.core-drift-activation",
                    "19.P6.bug-gate-grammar", "19.P6.report-inbox-triage"} <= set(t.plan_contract)
            assert t.context == ("tests/test_seeded_phase3_core.py",)
            assert t.scope_fence == ("tickets", "tests/test_seeded_phase6_02.py")
            for fact in ("Position 2", "admissions[2:]", "position 3", "admissions[3:]",
                         "high/high", "medium/medium", "phase6-exit", "no successor"):
                assert fact in (ROOT / ticket_path(t.stem)).read_text()
    # Neither consumption nor the seeder introduces a dependency on a later row.
    later = {s for row in UNSEEDED_SUFFIX for s in row}
    assert all(not later & set(a["depends"]) for a in AUTHORED.values())


def test_phase6_01_entry_depth():
    assert REQUIRED["core-drift-activation"] == (
        "19.P6.core-drift-activation", "19.P6.core-renderer", "19.P6.core-drift-classifier")
    assert REQUIRED["migrate-config"] == ("19.P6.migrate-config",)
    assert REQUIRED["phase6-continue-02"] == (
        "19.P6.host-contract-doc", "19.P6.fixture-host-scaffold",
        "19.P6.core-drift-activation", "19.P6.bug-gate-grammar", "19.P6.report-inbox-triage")
    assert set(ENTRY_DEPTH) == {u for us in REQUIRED.values() for u in us}
    for stem, units in REQUIRED.items():
        assert len(units) == len(set(units))
        assert set(units) <= set(AUTHORED[stem]["plan"])
        for uid in units:
            d = ENTRY_DEPTH[uid]
            assert d["resolves"] == 1 and d["gap"] is None
            assert set(d["parts"]) == {"Owner", "Records", "Observable", "Tests"}
            assert all(v > 0 for v in d["parts"].values())
            assert all(d["missing_part_rejected"].values())
            assert d["missing_part_rejected"].keys() == d["parts"].keys()
            assert {k: d[k] for k in ("chars", "bytes", "sha256")} == PLAN_SIZES[uid]
    for stem in PAYLOADS:
        unit = "19.P6." + stem
        raw = (ROOT / ticket_path(stem)).read_text()
        acceptance = raw.split("## Acceptance criteria\n", 1)[1].split("\n## Verification", 1)[0]
        for name in ENTRY_DEPTH[unit]["tests"]:
            if name == "test_core_classifier_unreachable_from_production_gates":
                assert name in raw and "test_core_drift_reachable_from_production_gates" in acceptance
            else:
                assert name in acceptance, (stem, name)
    assert not COPY_VIOLATIONS


def test_phase6_01_closure():
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert RENDER_BOUND_CHARS == 400_000 and REQ_RENDER_HEADROOM == 0.75
    activation = "core-drift-activation"
    assert set(CLOSURE_EVIDENCE) == set(FENCE_ADDITIONS[activation])
    assert all(v.strip() for v in CLOSURE_EVIDENCE.values())
    assert {"CLAUDE.md", "AGENTS.md", "chupa/stages.py", "tests/test_stages.py",
            "tests/test_seed_path.py", "tests/test_drain.py", "tests/test_mergequeue.py",
            "tests/test_terminal.py", "tests/test_seed_successor.py", "tests/test_daemon_soak.py",
            "eval/daemon_soak.py", "eval/reliability_battery.py", "eval/shakeout/bench.py",
            "tests/test_restart_timers.py"} == set(CLOSURE_EVIDENCE)
    assert "mergequeue.py:274" in CLOSURE_EVIDENCE["chupa/stages.py"]
    assert "test_core_classifier_unreachable_from_production_gates" in (ROOT / ticket_path(activation)).read_text()
    assert "tests/test_hostfiles.py" in FENCE_FLOORS[activation]
    assert len(AUTHORED[activation]["fence"]) <= 30
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    for scan in CLOSURE_SCAN.values():
        assert scan["matched_lines"] > 0 and scan["files"] > 0
        assert len(scan["sha256"]) == 64
    assert all(IMPORT_CLOSURE.values())
    for stem, a in AUTHORED.items():
        t = _ticket(stem)
        assert (t.context, t.on_demand) == (a["context"], a["on_demand"])
        assert not set(t.context) & set(t.on_demand)
        existing = set(a["fence"]) if stem in PAYLOADS else set()
        assert existing <= set(t.context) | set(t.on_demand)
        assert not {"tests/test_seeded_phase6_01.py", "tests/test_seeded_phase6_02.py"} & set(t.context)
        assert all(DELIMITER_FREE_CONTEXT[p] and not p.startswith("specs/") for p in t.context)
        assert render_chars(stem) == a["actual_render"] <= HEADROOM_CHARS
        for path in t.on_demand:
            assert render_chars(stem, (path,)) > HEADROOM_CHARS, path
        for path in (*t.context, *t.on_demand):
            s = FILE_SIZES[path]
            assert s["bytes"] >= s["chars"] > 0 and len(s["sha256"]) == 64
    # These consumers inherit repaired owners; they earn no separate fence widening.
    assert any("tests/test_merge.py" in row for row in IMPORT_CLOSURE["test_seed_path"])
    assert any("tests/test_author.py" in row for row in IMPORT_CLOSURE["test_drain"])


@pytest.mark.parametrize("stem", BATCH)
def test_phase6_01_recorded_ticket_bytes(stem):
    # Ticket identity may be checked live; plan, Context sizes and render operands stay historical.
    data = (ROOT / ticket_path(stem)).read_bytes()
    a = AUTHORED[stem]
    assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
        a["bytes"], a["chars"], a["sha256"])


def test_phase6_01_check_owns_seed_custody():
    t = _ticket("phase6-continue-02")
    for fact in ("requisition_review", "checks.json", "ticket-plane seed lift",
                 "approved bytes", "ticket_sha", "uncommitted"):
        assert fact in (ROOT / ticket_path(t.stem)).read_text()
    # Production custody and retry behavior are preservation suites, not this test's write targets.
    assert "tests/test_seed_path.py" in AUTHORED["core-drift-activation"]["fence"]
