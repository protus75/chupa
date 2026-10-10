"""Admission 7 snapshots; only seed identity reads current ticket bytes.

Depth, closure and maximum-effort feasibility use permanent authoring operands.
The production custody proof runs in a disposable repository.
"""

import asyncio
import hashlib
from pathlib import Path

import pytest

from chupa.git import GitError
from chupa.journal import EventType
from chupa.llm import FakeLLM
from chupa.runner import drive
from chupa.stages import Invoice
from chupa.tickets import ticket_path, validate_ticket
from tests.test_seed_path import context, requisition, seed_text, seeding_text
from tests.test_seed_path import repo as seed_repo
from tests.test_stages import STEM, implement_reply, verdict
from tests.test_terminal import diagnosis_reply

ROOT = Path(__file__).resolve().parents[1]
BATCH = ("exit-receipt-machinery", "phase6-continue-08")
PAYLOADS = BATCH[:1]
POSITION = 8
RENDER_BOUND_CHARS = 400_000
REQ_RENDER_HEADROOM = 0.75
MEASURED_RENDER_TIER = MEASURED_RENDER_EFFORT = "max"

AUTHORING_HEAD = '443c5b3396602c4e65c747b39a5bcbf3ddf36ae2'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

AUTHORING_TRACKED_SEEDS = ()

REGISTRY_ADMISSIONS = (('core-renderer', 'core-drift-classifier'),
 ('core-drift-activation', 'migrate-config'),
 ('host-contract-doc', 'fixture-host-scaffold'),
 ('bug-gate-grammar', 'report-inbox-triage'),
 ('escape-column',),
 ('supervised-merge-hold',),
 ('go-grade-machinery', 'go-grade-run'),
 ('exit-receipt-machinery',),
 ('phase6-exit',))

UNSEEDED_SUFFIX = (('phase6-exit',),)

REGISTRY_ROW = {'depends': ['go-grade-run'],
 'fence': ['chupa/artifacts.py',
           'chupa/stages.py',
           'eval/host_loop.py',
           'tests/test_host_loop.py',
           'tests/test_gates.py',
           'tests/test_stages.py',
           'hosts/fixture/'],
 'does': 'Closed host-loop-report.json and exit-receipt.json schemas, registration, writers, and '
         'the host-loop runner driving supervised fixture serve.'}

REGISTRY_TERMINAL = {'stem': 'phase6-exit', 'exit': True, 'depends': ('exit-receipt-machinery',)}

EDGES = {'exit-receipt-machinery': ('phase6-continue-07', 'go-grade-run'),
 'phase6-continue-08': ('exit-receipt-machinery',)}

FENCE_FLOORS = {'exit-receipt-machinery': ('chupa/artifacts.py',
                            'chupa/stages.py',
                            'eval/host_loop.py',
                            'tests/test_host_loop.py',
                            'tests/test_gates.py',
                            'tests/test_stages.py',
                            'hosts/fixture/'),
 'phase6-continue-08': ('tickets', 'tests/test_seeded_phase6_08.py')}

FENCE_ADDITIONS = {'exit-receipt-machinery': ('tests/test_fixture_host.py',), 'phase6-continue-08': ()}

REQUIRED = {'exit-receipt-machinery': ('19.P6.exit-receipt-machinery',
                            '19.P6.fixture-host-scaffold',
                            '19.P6.supervised-merge-hold',
                            '19.P6.go-grade-machinery',
                            '19.P6.go-grade-run'),
 'phase6-continue-08': ('19.P6.exit-receipt-machinery',
                        '19.P6.fixture-host-scaffold',
                        '19.P6.supervised-merge-hold',
                        '19.P6.go-grade-machinery',
                        '19.P6.go-grade-run')}

PLAN_SIZES = {'19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c',
          'delimiter_free': True},
 '19.P6.exit-receipt-machinery': {'bytes': 7110,
                                  'chars': 7110,
                                  'sha256': 'b8275a4dd5817f3f1ea2459500f0e1ef3c31e8a9c55ea0e8b6789fa88e8d2f2d',
                                  'delimiter_free': True},
 '19.P6.fixture-host-scaffold': {'bytes': 6157,
                                 'chars': 6157,
                                 'sha256': 'f67e09cc8d94030c66a580cdd0f794e4472aa0ccde256dc823ab3c8a0e56fbfc',
                                 'delimiter_free': True},
 '19.P6.supervised-merge-hold': {'bytes': 14669,
                                 'chars': 14669,
                                 'sha256': '0696b361fa55905a2bb037b29c42e1f2fd71679c3435af34fcaf8b2c471d905a',
                                 'delimiter_free': True},
 '19.P6.go-grade-machinery': {'bytes': 10834,
                              'chars': 10834,
                              'sha256': '20a0533364c7e5cae0e8cd1bf7358d41f574a6158624933b711fed49fb5a1929',
                              'delimiter_free': True},
 '19.P6.go-grade-run': {'bytes': 3377,
                        'chars': 3377,
                        'sha256': 'b2c959c1c85c04990f5422dbd9371ca3ddc8d02287e7ce54f17516d2d070466a',
                        'delimiter_free': True},
 '19.L': {'bytes': 20912,
          'chars': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa',
          'delimiter_free': True},
 '19.P6': {'bytes': 11595,
           'chars': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c',
           'delimiter_free': True},
 '13': {'bytes': 19840,
        'chars': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f',
        'delimiter_free': True}}

ENTRY_DEPTH = {'19.P6.exit-receipt-machinery': {'resolves': 1,
                                  'gap': None,
                                  'parts': {'Owner': 1115,
                                            'Records': 2514,
                                            'Observable': 1565,
                                            'Tests': 1763},
                                  'missing_part_rejected': {'Owner': True,
                                                            'Records': True,
                                                            'Observable': True,
                                                            'Tests': True},
                                  'missing_unit_rejected': True,
                                  'duplicate_rejected': True,
                                  'sha256': 'b8275a4dd5817f3f1ea2459500f0e1ef3c31e8a9c55ea0e8b6789fa88e8d2f2d',
                                  'tests': ('test_exit_receipt_entry_unit',
                                            'test_host_loop_closed_schema',
                                            'test_host_loop_drives_supervised_fixture_serve',
                                            'test_host_loop_report_regression_and_escape',
                                            'test_host_loop_requires_member_auditor_green',
                                            'test_exit_receipt_closed_schema_and_baseline_identity',
                                            'test_exit_receipt_regenerates_from_committed_bytes',
                                            'test_host_loop_and_receipt_registered_checks_lift',
                                            'test_host_loop_regression_uses_real_bug_gate')},
 '19.P6.fixture-host-scaffold': {'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 681,
                                           'Records': 2312,
                                           'Observable': 1329,
                                           'Tests': 1700},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'missing_unit_rejected': True,
                                 'duplicate_rejected': True,
                                 'sha256': 'f67e09cc8d94030c66a580cdd0f794e4472aa0ccde256dc823ab3c8a0e56fbfc',
                                 'tests': ('test_fixture_host_entry_units',
                                           'test_fixture_profile_loads',
                                           'test_fixture_scenario_list_is_closed',
                                           'test_fixture_replay_is_deterministic',
                                           'test_fixture_regression_exists_at_base',
                                           'test_fixture_escape_is_machine_introduced',
                                           'test_fixture_reports_are_bounded',
                                           'test_fixture_cli_adapter_roundtrip',
                                           'test_fixture_scaffold_is_dormant')},
 '19.P6.supervised-merge-hold': {'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 1822,
                                           'Records': 4620,
                                           'Observable': 4511,
                                           'Tests': 3582},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'missing_unit_rejected': True,
                                 'duplicate_rejected': True,
                                 'sha256': '0696b361fa55905a2bb037b29c42e1f2fd71679c3435af34fcaf8b2c471d905a',
                                 'tests': ('test_supervised_hold_entry_unit',
                                           'test_hold_after_green_before_main_mutation',
                                           'test_go_coverage_uses_actual_review_identity',
                                           'test_held_run_keeps_worktree_and_has_no_terminal',
                                           'test_supervised_hold_allows_other_work',
                                           'test_supervised_confirm_regates_moved_main',
                                           'test_supervised_request_identity_and_replay',
                                           'test_confirm_held_without_writer_lock',
                                           'test_reject_held_candidate',
                                           'test_restart_reconstructs_supervised_admission',
                                           'test_live_hold_is_not_an_orphan',
                                           'test_foreground_admission_never_supervised_holds',
                                           'test_bootstrap_never_supervised_holds',
                                           'test_soak_uses_candidate_base_regate_receipt')},
 '19.P6.go-grade-machinery': {'resolves': 1,
                              'gap': None,
                              'parts': {'Owner': 1619,
                                        'Records': 5048,
                                        'Observable': 1592,
                                        'Tests': 2434},
                              'missing_part_rejected': {'Owner': True,
                                                        'Records': True,
                                                        'Observable': True,
                                                        'Tests': True},
                              'missing_unit_rejected': True,
                              'duplicate_rejected': True,
                              'sha256': '20a0533364c7e5cae0e8cd1bf7358d41f574a6158624933b711fed49fb5a1929',
                              'tests': ('test_go_grade_entry_units',
                                        'test_go_grade_fixture_floors_and_author_separation',
                                        'test_go_grade_existing_corpus_is_partial_no_go',
                                        'test_go_grade_fixture_author_identity_comes_from_call',
                                        'test_eval_owned_budgets_preserve_synthetic_identities',
                                        'test_go_grade_scoring_and_partial_report',
                                        'test_go_grade_shared_cap_includes_retries_and_author_graph',
                                        'test_go_grade_author_graph_uses_local_prompt',
                                        'test_eval_budget_ceiling_before_spawn',
                                        'test_record_go_requires_complete_floors_identity_and_operator_judgment',
                                        'test_review_baseline_report_closed_schema',
                                        'test_review_baseline_report_registered_checks_lift')},
 '19.P6.go-grade-run': {'resolves': 1,
                        'gap': None,
                        'parts': {'Owner': 483, 'Records': 1041, 'Observable': 813, 'Tests': 910},
                        'missing_part_rejected': {'Owner': True,
                                                  'Records': True,
                                                  'Observable': True,
                                                  'Tests': True},
                        'missing_unit_rejected': True,
                        'duplicate_rejected': True,
                        'sha256': 'b2c959c1c85c04990f5422dbd9371ca3ddc8d02287e7ce54f17516d2d070466a',
                        'tests': ('test_go_grade_scoring_and_partial_report',
                                  'test_record_go_requires_complete_floors_identity_and_operator_judgment',
                                  'test_review_baseline_report_closed_schema',
                                  'test_review_baseline_report_registered_checks_lift',
                                  'test_outbox_only_check_requires_current_report',
                                  'test_outbox_only_merge_regate_requires_lift_custody',
                                  'test_outbox_only_admission_records_null_commit_and_retires')}}

FILE_SIZES = {'chupa/artifacts.py': {'bytes': 18577,
                        'chars': 18577,
                        'sha256': '8d202bcb00034f9e7af7d7f0afc4b4b14cf9800580a3267fd084d423597dcafb',
                        'delimiter_free': True},
 'chupa/stages.py': {'bytes': 73444,
                     'chars': 73444,
                     'sha256': 'f2b1dc4b2f02a9a0b41a674a14304109af703953d03660c1aa22e7c93a380d2d',
                     'delimiter_free': True},
 'tests/test_gates.py': {'bytes': 11668,
                         'chars': 11668,
                         'sha256': '1dd27eab54843f2e02141fa30f68784ee6f269ca13fc0dba2188a6ba871c3c2d',
                         'delimiter_free': True},
 'tests/test_stages.py': {'bytes': 37654,
                          'chars': 37654,
                          'sha256': 'b90671a899f04e39ee8af147030842a9243e9287b961aaf50e57bfdb484c5792',
                          'delimiter_free': True},
 'tests/test_fixture_host.py': {'bytes': 20488,
                                'chars': 20488,
                                'sha256': 'e1157abc7f94ecc848f0031c27444a1acaeed9709aed1df89cf6bbb0b7ea3bae',
                                'delimiter_free': True},
 'hosts/fixture/CLAUDE.md': {'bytes': 3353,
                             'chars': 3353,
                             'sha256': '5b75e7fbb5340a9197ccd42627250a51cb834d844062b8b52d70a3073e6d3727',
                             'delimiter_free': True},
 'hosts/fixture/README.md': {'bytes': 1892,
                             'chars': 1892,
                             'sha256': '353bfc2aad49cc1051fb423f9ea85c2ce005c9b715711bd79cd50459f450a0b8',
                             'delimiter_free': True},
 'hosts/fixture/app.py': {'bytes': 990,
                          'chars': 990,
                          'sha256': 'c74ab4d5d712976bac25ef8cd1aa624bcbca3262be59586a06d8f416b25c8449',
                          'delimiter_free': True},
 'hosts/fixture/bin/claude': {'bytes': 1581,
                              'chars': 1581,
                              'sha256': 'd93eac3b94e6e23b5497e6a6fdc957a633969cb4183df0698aa3fa717ceb28ba',
                              'delimiter_free': True},
 'hosts/fixture/bin/pnpm': {'bytes': 317,
                            'chars': 317,
                            'sha256': '2ad54d50622712faba75045689be22e8a60e0e53faa539dfa70d6eee29eb1f99',
                            'delimiter_free': True},
 'hosts/fixture/check.py': {'bytes': 251,
                            'chars': 251,
                            'sha256': '74de6b5da40af291ef3cd05f6e07cdeeb844633eee175601895146709311b61a',
                            'delimiter_free': True},
 'hosts/fixture/config.yaml': {'bytes': 978,
                               'chars': 978,
                               'sha256': 'cd342159284fc222d33d940fca97b4758e2045f5582b930924d1cac866be8ec2',
                               'delimiter_free': True},
 'hosts/fixture/evidence/escape.json': {'bytes': 75,
                                        'chars': 75,
                                        'sha256': 'ce3292cf50bdfb8ed293ae43032ca894b7a8bf4809dcaf20fa77611ee922ee67',
                                        'delimiter_free': True},
 'hosts/fixture/evidence/escape.log': {'bytes': 28,
                                       'chars': 28,
                                       'sha256': '142ed12c1f7a5c483b425d7edc2b94fd6fc04bf4514c0154e9a3fa8543c3a4af',
                                       'delimiter_free': True},
 'hosts/fixture/evidence/merge-add.json': {'bytes': 73,
                                           'chars': 73,
                                           'sha256': 'ff53f723308e439b570573f1bc79429e28e620275f3bbe008f87a7998c15ebd6',
                                           'delimiter_free': True},
 'hosts/fixture/evidence/merge-add.log': {'bytes': 31,
                                          'chars': 31,
                                          'sha256': '68d4f232b387277885dd9fe72b88ca060a7ccb375f8a2aa986cd91fb2bdce269',
                                          'delimiter_free': True},
 'hosts/fixture/evidence/merge-bonus.json': {'bytes': 75,
                                             'chars': 75,
                                             'sha256': '8ed1f25bb03ec3c90ba41d2a802129a682695a74e8745673eb98d6ddb26f96e3',
                                             'delimiter_free': True},
 'hosts/fixture/evidence/merge-bonus.log': {'bytes': 33,
                                            'chars': 33,
                                            'sha256': 'f96c67f2c43f4db9655f4617b57e3fdd287c28902dd173f3c56a84dfbcb8d103',
                                            'delimiter_free': True},
 'hosts/fixture/evidence/merge-floor.json': {'bytes': 75,
                                             'chars': 75,
                                             'sha256': 'be79557a2bbd1f0a65c1799bba3e8a559898887500a5e312845e2d1f8d387f1d',
                                             'delimiter_free': True},
 'hosts/fixture/evidence/merge-floor.log': {'bytes': 33,
                                            'chars': 33,
                                            'sha256': '43bd3bd8a9eb61a66ccdd57f7bff8ca8fff78efe9fb79db3ffd5f327370eeadb',
                                            'delimiter_free': True},
 'hosts/fixture/evidence/regression.json': {'bytes': 73,
                                            'chars': 73,
                                            'sha256': 'ff53f723308e439b570573f1bc79429e28e620275f3bbe008f87a7998c15ebd6',
                                            'delimiter_free': True},
 'hosts/fixture/evidence/regression.log': {'bytes': 32,
                                           'chars': 32,
                                           'sha256': '1694226cb9d4ffe6b6c2aa56a7ab3b037b48fb1a927cdd7755c213a3c4a4ca53',
                                           'delimiter_free': True},
 'hosts/fixture/regression_test.py': {'bytes': 316,
                                      'chars': 316,
                                      'sha256': '9b2185be994ab285df7da529c9210d16a7f43904dfe43c6478e6987fc0060b26',
                                      'delimiter_free': True},
 'hosts/fixture/replay.py': {'bytes': 354,
                             'chars': 354,
                             'sha256': 'e117a1e37fd681e933dd9cbb2932bed1a270ba8d478a5dee4c0fb9864ea56390',
                             'delimiter_free': True},
 'hosts/fixture/reports/escape.json': {'bytes': 408,
                                       'chars': 408,
                                       'sha256': 'cf91ea26979d8f1440209dd566ad1e8b5cdd7ea2691e937a02757f27605986e9',
                                       'delimiter_free': True},
 'hosts/fixture/reports/merge-add.json': {'bytes': 330,
                                          'chars': 330,
                                          'sha256': 'b94a72c95592cf0cefbf656b884f892fd9dccd3e4d3b544cc2fd27936304ddd8',
                                          'delimiter_free': True},
 'hosts/fixture/reports/merge-bonus.json': {'bytes': 325,
                                            'chars': 325,
                                            'sha256': '8b73d251d93746424dbe691b90021ffa91584c741bc65d712200d5e89a8274d9',
                                            'delimiter_free': True},
 'hosts/fixture/reports/merge-floor.json': {'bytes': 318,
                                            'chars': 318,
                                            'sha256': 'bb779a7fe75a4a9e8bf994c7da6253e23e9ba0f5875cb41cf7f5a3a6fce6c5f7',
                                            'delimiter_free': True},
 'hosts/fixture/reports/regression.json': {'bytes': 415,
                                           'chars': 415,
                                           'sha256': 'e736bc3887c9c2f97a37f6e6caf698a3a6b4836c74b2bc3a33980296fb7ffca5',
                                           'delimiter_free': True},
 'hosts/fixture/scaffold.py': {'bytes': 3054,
                               'chars': 3054,
                               'sha256': 'c4180b9e585928fc0018e5459b925835de10aee20cd1b78eaee03b368242bbfb',
                               'delimiter_free': True},
 'hosts/fixture/scripts.json': {'bytes': 10091,
                                'chars': 10091,
                                'sha256': '14ca200a03208b6be0450e7a62707ed2883ba83fe43faea05cd0e931306ab53e',
                                'delimiter_free': True},
 'hosts/fixture/settings.json': {'bytes': 69,
                                 'chars': 69,
                                 'sha256': '9dac3bf8f720b674698524d1bdd7a38972344e87578d8c55a0979d8d1b14ce17',
                                 'delimiter_free': True},
 'chupa/seams.py': {'bytes': 10148,
                    'chars': 10148,
                    'sha256': 'c465a54f053a4330f63abdcc0471747714f0d54147d070b79d9a98af213a0673',
                    'delimiter_free': True},
 'chupa/git.py': {'bytes': 8565,
                  'chars': 8565,
                  'sha256': '686cb0a3e47811706485ed2fd3da42307b0c6abaa334b36448de2093ea2a7dfe',
                  'delimiter_free': True},
 'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559',
                                      'delimiter_free': True}}

HISTORICAL_SNAPSHOTS = {'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559',
                                      'delimiter_free': True},
 'tests/test_seeded_phase6_core.py': {'bytes': 35196,
                                      'chars': 35196,
                                      'sha256': '7606a766e009e53284c8154c971847ed5f58b20dfff3f945266d35a324870cae',
                                      'delimiter_free': True},
 'tests/test_seeded_phase6_01.py': {'bytes': 57492,
                                    'chars': 57492,
                                    'sha256': '735465971d2bb73e92e29e7b25ed9d6690b400268fa95044c786dab85befaabe',
                                    'delimiter_free': True},
 'tests/test_seeded_phase6_02.py': {'bytes': 34282,
                                    'chars': 34282,
                                    'sha256': '215e19c190648bbd108913994c5efd6e7c4343bf8f0db43723d2b8644c23c772',
                                    'delimiter_free': True},
 'tests/test_seeded_phase6_03.py': {'bytes': 37248,
                                    'chars': 37248,
                                    'sha256': '4c94c271fdaf398680493b3afcc8fba59e8011306ba268e6b6c8a903b20eb915',
                                    'delimiter_free': True},
 'tests/test_seeded_phase6_04.py': {'bytes': 40447,
                                    'chars': 40447,
                                    'sha256': 'c2456fe6ee2160dcb851760ec587ec4a75b4227a31e9d87a2860af41939f71ca',
                                    'delimiter_free': True},
 'tests/test_seeded_phase6_05.py': {'bytes': 55987,
                                    'chars': 55987,
                                    'sha256': 'e4b6178af2eaa5ad6cd3b4e5aebec115d1c4f35a89412e0704bb8998e5757a1d',
                                    'delimiter_free': True},
 'tests/test_seeded_phase6_06.py': {'bytes': 83728,
                                    'chars': 83728,
                                    'sha256': 'd33a0fcdb854f35c516cf0747c6e42b50a6c1527fd2ae977b510bac0133465e6',
                                    'delimiter_free': True}}

CLOSURE_SCAN = {'chupa': {'files': 8,
           'matched_lines': 29,
           'sha256': 'cfad3d70b2eafd4afc0c463a5ae36b10e4895e092c7316907941ac46be0fabe9'},
 'eval': {'files': 4,
          'matched_lines': 8,
          'sha256': '0d7f8088e7346dc24e19ef430549c005faba23debe11cb66d6a88ac3622349c0'},
 'tests': {'files': 44,
           'matched_lines': 150,
           'sha256': '3f8b5c06b67db3ec2b443ea6aa8d1871e4aad51aef97580d1c94519c9fcf444c'}}

IMPLEMENT_SPEC = {'bytes': 5306,
 'chars': 5306,
 'sha256': 'f5d3ba603570a56f661a24d7a52d7e4543c0d003a82e36d664f5ef73f3599ddb',
 'delimiter_free': False}

IMPLEMENT_BODY_CHARS = 5185

AUTHORED = {'exit-receipt-machinery': {'bytes': 8170,
                            'chars': 8170,
                            'sha256': 'd358bcad5671766d87b90b441bd8123b052d2bbbca186acad47d9ac9edc7264c',
                            'delimiter_free': True,
                            'plan': ('19.I',
                                     '19.P6.exit-receipt-machinery',
                                     '19.P6.fixture-host-scaffold',
                                     '19.P6.supervised-merge-hold',
                                     '19.P6.go-grade-machinery',
                                     '19.P6.go-grade-run'),
                            'context': ('chupa/artifacts.py',
                                        'chupa/stages.py',
                                        'tests/test_gates.py',
                                        'tests/test_stages.py',
                                        'tests/test_fixture_host.py',
                                        'hosts/fixture/CLAUDE.md',
                                        'hosts/fixture/README.md',
                                        'hosts/fixture/app.py',
                                        'hosts/fixture/bin/claude',
                                        'hosts/fixture/bin/pnpm',
                                        'hosts/fixture/check.py',
                                        'hosts/fixture/config.yaml',
                                        'hosts/fixture/evidence/escape.json',
                                        'hosts/fixture/evidence/escape.log',
                                        'hosts/fixture/evidence/merge-add.json',
                                        'hosts/fixture/evidence/merge-add.log',
                                        'hosts/fixture/evidence/merge-bonus.json',
                                        'hosts/fixture/evidence/merge-bonus.log',
                                        'hosts/fixture/evidence/merge-floor.json',
                                        'hosts/fixture/evidence/merge-floor.log',
                                        'hosts/fixture/evidence/regression.json',
                                        'hosts/fixture/evidence/regression.log',
                                        'hosts/fixture/regression_test.py',
                                        'hosts/fixture/replay.py',
                                        'hosts/fixture/reports/escape.json',
                                        'hosts/fixture/reports/merge-add.json',
                                        'hosts/fixture/reports/merge-bonus.json',
                                        'hosts/fixture/reports/merge-floor.json',
                                        'hosts/fixture/reports/regression.json',
                                        'hosts/fixture/scaffold.py',
                                        'hosts/fixture/scripts.json',
                                        'hosts/fixture/settings.json',
                                        'chupa/seams.py',
                                        'chupa/git.py'),
                            'on_demand': (),
                            'fenced_existing': ('chupa/artifacts.py',
                                                'chupa/stages.py',
                                                'tests/test_gates.py',
                                                'tests/test_stages.py',
                                                'tests/test_fixture_host.py',
                                                'hosts/fixture/CLAUDE.md',
                                                'hosts/fixture/README.md',
                                                'hosts/fixture/app.py',
                                                'hosts/fixture/bin/claude',
                                                'hosts/fixture/bin/pnpm',
                                                'hosts/fixture/check.py',
                                                'hosts/fixture/config.yaml',
                                                'hosts/fixture/evidence/escape.json',
                                                'hosts/fixture/evidence/escape.log',
                                                'hosts/fixture/evidence/merge-add.json',
                                                'hosts/fixture/evidence/merge-add.log',
                                                'hosts/fixture/evidence/merge-bonus.json',
                                                'hosts/fixture/evidence/merge-bonus.log',
                                                'hosts/fixture/evidence/merge-floor.json',
                                                'hosts/fixture/evidence/merge-floor.log',
                                                'hosts/fixture/evidence/regression.json',
                                                'hosts/fixture/evidence/regression.log',
                                                'hosts/fixture/regression_test.py',
                                                'hosts/fixture/replay.py',
                                                'hosts/fixture/reports/escape.json',
                                                'hosts/fixture/reports/merge-add.json',
                                                'hosts/fixture/reports/merge-bonus.json',
                                                'hosts/fixture/reports/merge-floor.json',
                                                'hosts/fixture/reports/regression.json',
                                                'hosts/fixture/scaffold.py',
                                                'hosts/fixture/scripts.json',
                                                'hosts/fixture/settings.json'),
                            'created': ('eval/host_loop.py', 'tests/test_host_loop.py'),
                            'render_overhead': 1148,
                            'actual_render': 264575},
 'phase6-continue-08': {'bytes': 6218,
                        'chars': 6218,
                        'sha256': '1c0b489e43fb84f35953cb85c6b3ac170752f791b76ab7af43b2124d703121e8',
                        'delimiter_free': True,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P6',
                                 '13',
                                 '19.P6.exit-receipt-machinery',
                                 '19.P6.fixture-host-scaffold',
                                 '19.P6.supervised-merge-hold',
                                 '19.P6.go-grade-machinery',
                                 '19.P6.go-grade-run'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tests/test_seeded_phase6_08.py',),
                        'render_overhead': -18,
                        'actual_render': 113115}}

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

COPY_VIOLATIONS = ()

TERMINAL_CLOSURE = {'role_ids': ('19.L', '19.I', '19.P6', '13'),
 'resolves': True,
 'entry_id': None,
 'next_admission': ('phase6-exit',),
 'required_units': ('19.P6.exit-receipt-machinery',
                    '19.P6.fixture-host-scaffold',
                    '19.P6.supervised-merge-hold',
                    '19.P6.go-grade-machinery',
                    '19.P6.go-grade-run'),
 'seeds': (),
 'successor': None}

CLOSURE_EVIDENCE = {
    "tests/test_fixture_host.py": (
        "19.L rule 2: chupa/stages.py::_gather_bug requires a branch-changed carries "
        "file under tests/test/fixtures/fixture and JSON regression_result; "
        "hosts/fixture/scaffold.py::scripted_reply pins edits to settings.json. "
        "test_fixture_scenario_list_is_closed pins set(row) to kind/responses/edits/checks/evidence, "
        "ticket.scope_fence == ('settings.json',) and set(row['edits']) == {'settings.json'}. "
        "test_fixture_regression_exists_at_base pins diff_names(base, head) == ['settings.json']. "
        "test_fixture_profile_loads pins engine_plane_safety_inventory including root regression_test.py. "
        "These assertions must migrate with the fixture's real bug-gate shape; "
        "tests/test_fixture_host.py::implement and test_fixture_cli_adapter_roundtrip call scripted_reply."
    ),
}
CLOSURE_DECISIONS = (
    "New eval/host_loop.py has no existing callers or public-operation allowlist.",
    "Schema additions and KNOWN_ARTIFACTS registration are inside the registry fence; "
    "chupa/merge.py imports the existing mapping without a changed call signature.",
    "The runner uses existing serve/control/triage/Git seams without changing their public signatures.",
    "Fixture support remains under hosts/fixture/; its direct tests earn the sole fence addition.",
    "No dormant engine component is activated by introducing this standalone runner.",
    "eval/daemon_soak.py contains engine delimiters and is excluded from embedded Context.",
)
MACHINERY_OBLIGATIONS = (
    ("tests/test_host_loop.py", "test_exit_receipt_entry_unit"),
    ("tests/test_host_loop.py", "test_host_loop_closed_schema"),
    ("tests/test_host_loop.py", "test_host_loop_drives_supervised_fixture_serve"),
    ("tests/test_host_loop.py", "test_host_loop_report_regression_and_escape"),
    ("tests/test_host_loop.py", "test_host_loop_requires_member_auditor_green"),
    ("tests/test_host_loop.py", "test_exit_receipt_closed_schema_and_baseline_identity"),
    ("tests/test_host_loop.py", "test_exit_receipt_regenerates_from_committed_bytes"),
    ("tests/test_stages.py", "test_host_loop_and_receipt_registered_checks_lift"),
    ("tests/test_gates.py", "test_host_loop_regression_uses_real_bug_gate"),
)
DELIVERY = {
    "seeds": tuple(ticket_path(s) for s in BATCH),
    "commit_only": "tests/test_seeded_phase6_07.py",
    "approval_record": "tickets/phase6-continue-07/checks.json",
    "review": "requisition_review", "lift": "ticket-plane",
    "retry": "retain approved bytes while ticket_sha matches; author only snagged seeds",
}


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, BATCH)


def render_chars(stem):
    a = AUTHORED[stem]
    return (IMPLEMENT_BODY_CHARS + a["chars"] + a["render_overhead"]
            + sum(PLAN_SIZES[u]["chars"] for u in a["plan"])
            + sum(FILE_SIZES[p]["chars"] for p in a["context"]))


def test_phase6_07_exact_admission():
    assert PAYLOADS == REGISTRY_ADMISSIONS[7] == ("exit-receipt-machinery",)
    assert BATCH == ("exit-receipt-machinery", "phase6-continue-08")
    assert UNSEEDED_SUFFIX == REGISTRY_ADMISSIONS[POSITION:] == (("phase6-exit",),)
    assert REGISTRY_TERMINAL == {"stem": "phase6-exit", "exit": True,
                                 "depends": ("exit-receipt-machinery",)}
    assert len(set(BATCH)) == len(BATCH) == 2 <= MAX_SEEDS_PER_ADMISSION == 3
    assert EDGES == {BATCH[0]: ("phase6-continue-07", "go-grade-run"), BATCH[1]: PAYLOADS}
    assert not REGISTRY_ROW.get("deep", False)
    for stem in BATCH:
        t = _ticket(stem)
        assert (t.frontmatter.source, t.frontmatter.state) == ("seed", "confirmed")
        assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("medium", "medium")
        assert t.depends == EDGES[stem]
        assert t.plan_contract == AUTHORED[stem]["plan"]
        assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES
        assert "phase6-exit" not in t.depends
    assert _ticket(BATCH[0]).plan_contract == (
        "19.I", "19.P6.exit-receipt-machinery", "19.P6.fixture-host-scaffold",
        "19.P6.supervised-merge-hold", "19.P6.go-grade-machinery", "19.P6.go-grade-run")
    t = _ticket(BATCH[1])
    assert t.plan_contract == ("19.L", "19.I", "19.P6", "13", *REQUIRED[BATCH[1]])
    assert t.scope_fence == ("tickets", "tests/test_seeded_phase6_08.py")
    assert t.context == ("tests/test_seeded_phase3_core.py",)
    scope = t.sections["Scope in / Scope out"]
    suffix = scope.split("Position 8 carries admissions[8:]:\n", 1)[1].split("\n\nAuthor exactly", 1)[0]
    assert suffix.splitlines() == ["- [phase6-exit]"]
    for fact in ("sole terminal payload", "There is no successor", "no seeds authored by phase6-exit",
                 "terminal contract", "seeding role", "high/high", "KNOWN-HARD", "medium/medium",
                 "deep: true", "seeding.max_seeds_per_admission", "drain.max_ticket_minutes"):
        assert fact in scope


def test_phase6_07_entry_depth():
    units = ("19.P6.exit-receipt-machinery", "19.P6.fixture-host-scaffold",
             "19.P6.supervised-merge-hold", "19.P6.go-grade-machinery", "19.P6.go-grade-run")
    assert REQUIRED == {s: units for s in BATCH}
    assert set(ENTRY_DEPTH) == set(units)
    for stem in BATCH:
        assert set(REQUIRED[stem]) <= set(AUTHORED[stem]["plan"])
        for uid in REQUIRED[stem]:
            d = ENTRY_DEPTH[uid]
            assert d["resolves"] == 1 and d["gap"] is None
            assert d["missing_unit_rejected"] and d["duplicate_rejected"]
            assert set(d["parts"]) == {"Owner", "Records", "Observable", "Tests"}
            assert all(size > 0 for size in d["parts"].values())
            assert set(d["missing_part_rejected"]) == set(d["parts"])
            assert all(d["missing_part_rejected"].values())
            assert d["sha256"] == PLAN_SIZES[uid]["sha256"]
    assert ENTRY_DEPTH[units[0]]["tests"] == tuple(n for _, n in MACHINERY_OBLIGATIONS)
    t = _ticket(BATCH[0])
    for path, name in MACHINERY_OBLIGATIONS:
        assert path + "::" + name in t.sections["Acceptance criteria"]
        assert path in t.scope_fence
        assert ("uv", "run", "pytest", "-q", path) in t.verification
    for stem in BATCH:
        scope = _ticket(stem).sections["Scope in / Scope out"]
        for fact in ("required_units", "resolve_plan_contract", "entry_unit_gap", "successor",
                     "kind: spec_gap", "terminal", "phase6-exit"):
            assert fact in scope
    assert TERMINAL_CLOSURE == {
        "role_ids": ("19.L", "19.I", "19.P6", "13"), "resolves": True,
        "entry_id": None, "next_admission": ("phase6-exit",),
        "required_units": units, "seeds": (), "successor": None,
    }
    assert COPY_VIOLATIONS == ()


def test_phase6_07_closure():
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert FENCE_FLOORS[BATCH[0]] == tuple(REGISTRY_ROW["fence"])
    assert FENCE_ADDITIONS == {BATCH[0]: ("tests/test_fixture_host.py",), BATCH[1]: ()}
    assert set(CLOSURE_EVIDENCE) == set(FENCE_ADDITIONS[BATCH[0]])
    evidence = CLOSURE_EVIDENCE["tests/test_fixture_host.py"]
    for fact in ("19.L rule 2", "_gather_bug", "scripted_reply", "regression_result",
                 "test_fixture_scenario_list_is_closed", "test_fixture_regression_exists_at_base",
                 "test_fixture_profile_loads", "diff_names", "engine_plane_safety_inventory",
                 "scope_fence", "set(row)", "set(row['edits'])"):
        assert fact in evidence
    scope = _ticket(BATCH[0]).sections["Scope in / Scope out"]
    for fact in ("Migrate only predecessor assertions", "in the same commit", "exact row keys",
                 "settings-only edit vocabulary", "settings-only scope fence", "settings-only diff_names",
                 "exact engine_plane_safety_inventory", "regression_result", "durable report evidence"):
        assert fact in scope
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    assert all(r["matched_lines"] and r["files"] and len(r["sha256"]) == 64
               for r in CLOSURE_SCAN.values())
    assert set(HISTORICAL_SNAPSHOTS) == {
        "tests/test_seeded_phase3_core.py", "tests/test_seeded_phase6_core.py",
        *(f"tests/test_seeded_phase6_{n:02d}.py" for n in range(1, 7))}
    assert HISTORICAL_SNAPSHOTS["tests/test_seeded_phase3_core.py"] == FILE_SIZES["tests/test_seeded_phase3_core.py"]
    assert (RENDER_BOUND_CHARS, REQ_RENDER_HEADROOM) == (400_000, 0.75)
    assert (MEASURED_RENDER_TIER, MEASURED_RENDER_EFFORT) == ("max", "max")
    for stem, a in AUTHORED.items():
        t = _ticket(stem)
        assert t.scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
        assert (t.context, t.on_demand) == (a["context"], a["on_demand"])
        assert set(a["fenced_existing"]) <= set(t.context) | set(t.on_demand)
        assert not set(t.context) & set(t.on_demand)
        assert not set(a["created"]) & (set(t.context) | set(t.on_demand))
        assert t.on_demand == ()
        assert all(FILE_SIZES[p]["delimiter_free"] and not p.startswith("specs/") for p in t.context)
        assert not set(t.scope_fence) & set(HISTORICAL_SNAPSHOTS)
        assert render_chars(stem) == a["actual_render"] <= 300_000
        data = (ROOT / ticket_path(stem)).read_bytes()
        assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
            a["bytes"], a["chars"], a["sha256"])
    assert AUTHORED[BATCH[0]]["created"] == ("eval/host_loop.py", "tests/test_host_loop.py")
    assert AUTHORED[BATCH[1]]["created"] == ("tests/test_seeded_phase6_08.py",)
    for record in (*PLAN_SIZES.values(), *FILE_SIZES.values(), *HISTORICAL_SNAPSHOTS.values(), IMPLEMENT_SPEC):
        assert record["bytes"] >= record["chars"] > 0 and len(record["sha256"]) == 64
    t = _ticket(BATCH[0])
    preserved = {"tests/test_bug_gate.py", "tests/test_inbox.py", "tests/test_triage.py",
                 "tests/test_supervised_merge_hold.py", "tests/test_merge.py", "tests/test_seed_path.py",
                 "tests/test_plan_lint.py"}
    assert not preserved & (set(t.context) | set(t.on_demand) | set(t.scope_fence))
    assert preserved <= {arg for argv in t.verification for arg in argv}
    assert ("uv", "run", "pytest", "-q", "tests/test_fixture_host.py") in t.verification


def test_phase6_07_check_owns_seed_custody(seed_repo):
    assert AUTHORING_TRACKED_SEEDS == ()
    assert DELIVERY["approval_record"] == "tickets/phase6-continue-07/checks.json"
    assert DELIVERY["commit_only"] == "tests/test_seeded_phase6_07.py"
    successor = (ROOT / ticket_path(BATCH[-1])).read_text()
    for fact in ("uncommitted", "requisition_review", "tickets/phase6-continue-08/checks.json",
                 "ticket-plane seed lift", "approved bytes", "ticket_sha", "snagged seeds"):
        assert fact in successor
    seeder = "phase6-continue-07"
    own = ticket_path(seeder)
    setup, _ = context(seed_repo, [])
    setup.fs.write(seed_repo / own, seeding_text().encode())
    (seed_repo / ticket_path(STEM)).unlink()

    async def prepare():
        await setup.git.add(seed_repo, [own, ticket_path(STEM)])
        await setup.git.commit(seed_repo, "use admission 7 seeder identity")
    asyncio.run(prepare())
    ticket = validate_ticket(seeder, (seed_repo / own).read_text(), seed_repo)
    seeds = {s: seed_text(s) for s in BATCH}
    snagged, approved = BATCH
    snag = {"code": "scope", "message": "missing fixture test", "paved_road": "fence the test",
            "kind": "authoring_error"}

    def implement_seeds(ctx, emitted, *, retry=False):
        async def act(request):
            assert request.surface == "implement" and request.worktree is not None
            if retry:
                assert "## Approved seeds (keep verbatim)" in request.rendered
                assert (request.worktree / ticket_path(approved)).read_text() == seeds[approved]
                assert set(emitted) == {snagged}
            for s, text in emitted.items():
                ctx.fs.write(request.worktree / ticket_path(s), text.encode())
            ctx.fs.write(request.worktree / "chupa/thing.py", b"ok retry\n" if retry else b"ok\n")
            await ctx.git.add(request.worktree, ["chupa/thing.py"])
            await ctx.git.commit(request.worktree, "test implementation")
            assert not set(DELIVERY["seeds"]) & set(await ctx.git.ls_files(request.worktree))
            for path in DELIVERY["seeds"]:
                with pytest.raises(GitError):
                    await ctx.git.rev_parse(request.worktree, "HEAD:" + path)
                assert (request.worktree / path).is_file()
        return act

    class SeedLLM(FakeLLM):
        async def call(self, request):
            if request.surface == "implement":
                await self.emit(request)
            return await super().call(request)

    ctx, _ = context(seed_repo, [])
    ctx.driver.llm = SeedLLM([implement_reply(), requisition("snag", [snag]),
                             requisition("approve"), diagnosis_reply()])
    ctx.driver.llm.emit = implement_seeds(ctx, seeds)
    assert asyncio.run(drive(ctx, ticket)) == "gate_failed"
    receipt = Invoice.model_validate_json((seed_repo / DELIVERY["approval_record"]).read_text())
    assert [(s.stem, s.verdict) for s in receipt.seeds] == [(snagged, "snag"), (approved, "approve")]
    reviews = [r for r in ctx.driver.llm.requests if r.surface == "requisition_review"]
    assert len(reviews) == len(BATCH)
    for stem, request in zip(sorted(BATCH), reviews, strict=True):
        assert seeds[stem].strip() in request.rendered
        assert all(seeds[other].strip() not in request.rendered for other in BATCH if other != stem)
    assert not any((seed_repo / path).exists() for path in DELIVERY["seeds"])
    assert not any(e.key and e.key.endswith("/seeds") for e in ctx.driver.journal.read())

    repaired = seeds[snagged].replace("holds the word ok for " + snagged + ".",
                                     "holds the word ok for " + snagged + ", tested.")
    retry, _ = context(seed_repo, [])
    retry.driver.llm = SeedLLM([implement_reply(), requisition("approve"), verdict()])
    retry.driver.llm.emit = implement_seeds(retry, {snagged: repaired}, retry=True)
    assert asyncio.run(drive(retry, ticket)) == "merged"
    requests = [r for r in retry.driver.llm.requests if r.surface == "requisition_review"]
    assert len(requests) == 1 and "Verdict: snag" in requests[0].rendered
    assert "missing fixture test" in requests[0].rendered and "tested." in requests[0].rendered
    assert (seed_repo / ticket_path(approved)).read_text() == seeds[approved]
    assert (seed_repo / ticket_path(snagged)).read_text() == repaired

    async def custody():
        events = retry.driver.journal.read()
        lifts = [e for e in events if e.type == EventType.EFFECT_COMPLETION
                 and e.ticket == seeder and (e.key or "").endswith("/seeds")]
        assert len(lifts) == 1
        lift = lifts[0]
        check = next(e for e in reversed(events[:events.index(lift)])
                     if e.type == EventType.EFFECT_COMPLETION and e.ticket == seeder
                     and (e.key or "").endswith("/checks"))
        text = await retry.git._run(seed_repo, "show", check.body["result"]["commit"] + ":"
                                   + DELIVERY["approval_record"])
        invoice = Invoice.model_validate_json(text)
        assert invoice.passed
        assert [(s.stem, s.verdict) for s in invoice.seeds] == [(s, "approve") for s in sorted(BATCH)]
        for s in invoice.seeds:
            assert s.ticket_sha == await retry.git.rev_parse(seed_repo, "HEAD:" + ticket_path(s.stem))
        changed = await retry.git._run(seed_repo, "show", "--format=", "--name-only", lift.body["result"]["commit"])
        assert set(changed.splitlines()) == set(DELIVERY["seeds"])
        subjects = (await retry.git._run(seed_repo, "log", "--format=%s")).splitlines()
        assert subjects.count("chupa(" + seeder + "): seeds") == 1
        intake = [e for e in events if e.type == EventType.SIGNAL
                  and e.body.get("signal") == "ticket_intake" and e.body.get("seeded_by") == seeder]
        assert [e.ticket for e in intake] == sorted(BATCH)
        assert all(events.index(check) < events.index(lift) < events.index(e) for e in intake)
    asyncio.run(custody())
