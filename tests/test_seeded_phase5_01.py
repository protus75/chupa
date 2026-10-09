"""Phase 5 position 01: fixed authoring snapshots, following the merged Phase 3 idiom.

Only seed identity/grammar is read live. Render sizes, plan depth, registry and closure
evidence are frozen; later tickets never refresh these historical measurements.
"""

import hashlib
from pathlib import Path
import re

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]

AUTHORING_HEAD = '147eb2e7fb2407799fa793cb3e2c6d89629090db'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('retro-box-activation', 'phase5-continue-02')

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

FENCE_ADDITIONS = {'chupa/journal.py': '19.L rule 5: register tombstone_auto_reopened, retro_ticket_authored and '
                     'retro_prompt_spec_change_merged in SIGNAL_NAMES with their sole writers and consumers.',
 'tests/test_vocabularies.py': '19.L rule 5: test_every_engine_signal_name_is_listed pins equality of actual '
                               'signal writers and the closed vocabulary; retain unknown-name refusal.',
 'tests/test_status.py': '19.L rule 5 and the entry Tests: create '
                         'test_status_surfaces_confirmed_class_tombstones at the existing status projection '
                         'caller.',
 'tests/test_retro.py': '19.L rules 2-3: '
                        'test_receipt_uses_engine_provenance_usage_calibration_and_tombstones ends with an '
                        'empty Box despite a completed proposal; migrate that negative to one evidenced '
                        'proposal and add test_retro_itemizes_confirmed_class_tombstones, retaining report '
                        'custody and provenance.',
 'chupa/driver.py': '19.L rule 5 and entry Owner: the Driver failure producer calls storm_producer at the '
                    'journal-holding production root; ensure its Box receives the same callback through the '
                    'shared wrapper without changing that wrapper signature.'}

CREATED = ('tests/test_retro_box.py', 'tests/test_status.py')

FENCED_EXISTING = ('chupa/retro.py',
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
 'chupa/journal.py',
 'tests/test_vocabularies.py',
 'tests/test_retro.py',
 'chupa/driver.py')

AUTHORED = {'retro-box-activation': {'chars': 10278,
                          'bytes': 10278,
                          'sha256': 'ba12168f00aff22003c68ce97caa6509c743accf46bbbda08ff45e3c94736d6c',
                          'plan': ('19.I', '19.P5.retro-box-activation', '12'),
                          'context': ('chupa/policy.py',
                                      'chupa/status.py',
                                      'tests/test_policy.py',
                                      'tests/test_box.py',
                                      'tests/test_vocabularies.py',
                                      'tests/test_author.py',
                                      'chupa/author.py',
                                      'tests/test_triage.py',
                                      'chupa/box.py',
                                      'chupa/triage.py',
                                      'chupa/journal.py',
                                      'chupa/retro.py',
                                      'tests/test_retro.py',
                                      'chupa/__main__.py',
                                      'chupa/merge.py',
                                      'chupa/serve.py',
                                      'chupa/driver.py',
                                      'chupa/daemon.py',
                                      'tests/test_merge.py'),
                          'on_demand': ('chupa/stages.py',
                                        'chupa/runner.py',
                                        'chupa/drain.py',
                                        'tests/test_stages.py',
                                        'tests/test_daemon_composition.py',
                                        'tests/test_drain.py',
                                        'tests/test_serve.py'),
                          'fence': ('chupa/retro.py',
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
                                    'tests/test_retro_box.py',
                                    'chupa/journal.py',
                                    'tests/test_vocabularies.py',
                                    'tests/test_status.py',
                                    'tests/test_retro.py',
                                    'chupa/driver.py'),
                          'depends': ('phase5-continue', 'retro-drain-invoker'),
                          'expected': 90,
                          'stuck': 180},
 'phase5-continue-02': {'chars': 5174,
                        'bytes': 5174,
                        'sha256': '830e969ccd63727f40b802f0e54b22500810fe0d08b174ead23bbc8e55384214',
                        'plan': ('19.L', '19.I', '19.P5', '19.P5.scorecard-reporting', '14', '13'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fence': ('tickets', 'tests/test_seeded_phase5_02.py'),
                        'depends': ('retro-box-activation',),
                        'expected': 60,
                        'stuck': 180}}

REQUIRED = {'retro-box-activation': ('19.P5.retro-box-activation',),
 'phase5-continue-02': ('19.P5.scorecard-reporting',)}

ENTRY_DEPTH = {'19.P5.retro-box-activation': {'sha256': 'b750a8a519396f98a597a3fa040803ea113f537b35b431b8ae61944bf9789251',
                                'chars': 9207,
                                'parts': {'Owner': 1478, 'Records': 3844, 'Observable': 1070, 'Tests': 2653},
                                'gap': None,
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
                                          'test_tombstone_visibility_uses_message_class')},
 '19.P5.scorecard-reporting': {'sha256': '4ece442f6aad5f09bbbc4ae2ed91be9740179135db245166a1e66c3cd5ec6a73',
                               'chars': 5628,
                               'parts': {'Owner': 608, 'Records': 2422, 'Observable': 925, 'Tests': 1524},
                               'gap': None,
                               'resolves': 1,
                               'tests': ('test_scorecard_entry_unit',
                                         'test_scorecard_uses_completed_check_evidence',
                                         'test_scorecard_catches_resolved_and_upheld_findings',
                                         'test_scorecard_rates_and_prune_threshold',
                                         'test_scorecard_totals_and_rendering')}}

FILE_SIZES = {'chupa/retro.py': {'chars': 12741, 'bytes': 12741},
 'chupa/box.py': {'chars': 10000, 'bytes': 10000},
 'chupa/merge.py': {'chars': 18346, 'bytes': 18346},
 'chupa/author.py': {'chars': 9766, 'bytes': 9766},
 'chupa/triage.py': {'chars': 10026, 'bytes': 10026},
 'chupa/policy.py': {'chars': 3289, 'bytes': 3289},
 'chupa/stages.py': {'chars': 62878, 'bytes': 62878},
 'chupa/runner.py': {'chars': 38508, 'bytes': 38508},
 'chupa/daemon.py': {'chars': 26121, 'bytes': 26121},
 'chupa/drain.py': {'chars': 34889, 'bytes': 34889},
 'chupa/serve.py': {'chars': 21790, 'bytes': 21790},
 'chupa/status.py': {'chars': 3606, 'bytes': 3606},
 'chupa/__main__.py': {'chars': 16000, 'bytes': 16000},
 'tests/test_box.py': {'chars': 6488, 'bytes': 6488},
 'tests/test_merge.py': {'chars': 34356, 'bytes': 34356},
 'tests/test_author.py': {'chars': 7176, 'bytes': 7176},
 'tests/test_triage.py': {'chars': 9925, 'bytes': 9925},
 'tests/test_policy.py': {'chars': 4111, 'bytes': 4111},
 'tests/test_stages.py': {'chars': 34579, 'bytes': 34579},
 'tests/test_daemon_composition.py': {'chars': 93925, 'bytes': 93925},
 'tests/test_drain.py': {'chars': 60565, 'bytes': 60565},
 'tests/test_serve.py': {'chars': 75256, 'bytes': 75256},
 'chupa/journal.py': {'chars': 11027, 'bytes': 11027},
 'tests/test_vocabularies.py': {'chars': 6602, 'bytes': 6602},
 'tests/test_retro.py': {'chars': 14587, 'bytes': 14587},
 'chupa/driver.py': {'chars': 23810, 'bytes': 23810},
 'tests/test_seeded_phase3_core.py': {'chars': 5425, 'bytes': 5425}}

PLAN_CHARS = {'19.I': 1811,
 '19.P5.retro-box-activation': 9207,
 '12': 20224,
 '19.L': 20912,
 '19.P5': 9792,
 '19.P5.scorecard-reporting': 5628,
 '14': 7360,
 '13': 19840}

IMPLEMENT_SPEC_CHARS = 4896

RENDER_OVERHEAD = 2000

HEADROOM_CHARS = 300000

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

PRODUCTION_CALLERS = {'chupa/__main__.py': {'sha256': '9adf37e256776d1baf6be834f81b5fd808eca8e8d0dd727b66e7546d0d32c024',
                       'lines': (46,)},
 'chupa/box.py': {'sha256': '7d401296782c0d868fabe94a419c6d7fb5d8e1e78be03cdec45a1de3c75fd9f5',
                  'lines': (21, 235, 241)},
 'chupa/daemon.py': {'sha256': '59796b1036333786646b03ab8e3b68e07b5b756bf3bec54706d6b6cca3fd5da4',
                     'lines': (45, 49)},
 'chupa/driver.py': {'sha256': '1d5cceec4544c4bd969b7fe2e0a76cd6c73277d104fb627540a2f5f631efb81c',
                     'lines': (373,)},
 'chupa/retro.py': {'sha256': '2441723b07cb3b38c2ebeef387c8fc50aceafbfa9d7d4297593da583a2911540',
                    'lines': (200,)},
 'chupa/runner.py': {'sha256': 'b1d8c2debc4a150a8e29d4bb3aaa86fb5e14482db2a4eb1f3d061a673ba941e4',
                     'lines': (298, 304, 516, 631)},
 'chupa/stages.py': {'sha256': '05d7df882cf74325f56fb90799a33938e6763a5b0da641b928712b9adaaa9bfa',
                     'lines': (591, 681)},
 'chupa/triage.py': {'sha256': '487dd345cec670dd84ef831ecbb9ac24660e3d36fefe32fef2a2fad79fd1f1d6',
                     'lines': (96,)}}

CLOSURE_SCAN = {'chupa/__main__.py': {'sha256': '9adf37e256776d1baf6be834f81b5fd808eca8e8d0dd727b66e7546d0d32c024',
                       'lines': (46,)},
 'chupa/author.py': {'sha256': 'd19ba65621a0ae8f43a141e0dd3c46a7d830cef7bec8eab2a40bef3251de0a36',
                     'lines': (136,)},
 'chupa/box.py': {'sha256': '7d401296782c0d868fabe94a419c6d7fb5d8e1e78be03cdec45a1de3c75fd9f5',
                  'lines': (21, 235, 241)},
 'chupa/config.py': {'sha256': 'f7f8f3e3855ff958a9d1ee5e2fd3fd87f02978cad6cfa83952dc64d0546c82cf',
                     'lines': (24, 40)},
 'chupa/daemon.py': {'sha256': '59796b1036333786646b03ab8e3b68e07b5b756bf3bec54706d6b6cca3fd5da4',
                     'lines': (45, 49)},
 'chupa/driver.py': {'sha256': '1d5cceec4544c4bd969b7fe2e0a76cd6c73277d104fb627540a2f5f631efb81c',
                     'lines': (373,)},
 'chupa/journal.py': {'sha256': '5240293a729704e2f6e362abdade8edd8d6b575e920c5d0eeac8d372f01d80e5',
                      'lines': (36, 140, 142)},
 'chupa/llmeffect.py': {'sha256': 'dbd470510b70f531dd6bf606cde7f19571f4ddc194791ab3ad9bf75cc1c8a79f',
                        'lines': (35,)},
 'chupa/policy.py': {'sha256': '7763ed9b6af8f42a9167e8eebd03591ea299732690ced052819d5808e50fbf2e',
                     'lines': (68,)},
 'chupa/retro.py': {'sha256': '2441723b07cb3b38c2ebeef387c8fc50aceafbfa9d7d4297593da583a2911540',
                    'lines': (200,)},
 'chupa/runner.py': {'sha256': 'b1d8c2debc4a150a8e29d4bb3aaa86fb5e14482db2a4eb1f3d061a673ba941e4',
                     'lines': (298, 304, 516, 631)},
 'chupa/stages.py': {'sha256': '05d7df882cf74325f56fb90799a33938e6763a5b0da641b928712b9adaaa9bfa',
                     'lines': (591, 681)},
 'chupa/triage.py': {'sha256': '487dd345cec670dd84ef831ecbb9ac24660e3d36fefe32fef2a2fad79fd1f1d6',
                     'lines': (96,)},
 'eval/shakeout/stages.py': {'sha256': '7cf99e76687320963a7b86d00ff12a6a31d327696ee301d8e95de9d6bee8f371',
                             'lines': (194,)},
 'tests/test_author.py': {'sha256': '0e619d2341de87c36734c447a19c20bc0b2e3f5ee782aa8e41f58b21bc5e788e',
                          'lines': (36,)},
 'tests/test_box.py': {'sha256': '1cf8c0c4aae2622dc84e94fea98c678dca2a39e04c36f3b644592cafacdce856',
                       'lines': (37, 62, 69, 128)},
 'tests/test_checkpoint.py': {'sha256': '8e6152e7cf44f2a66b556ed70139460dd068e85d8ffbf70c112b8b44c5ac5748',
                              'lines': (68, 476, 486, 560)},
 'tests/test_config.py': {'sha256': 'd757880b574b2c60f150fc00ca7cc50dc78b2af6dd8748853fdc3e9a6db938e2',
                          'lines': (79,)},
 'tests/test_daemon_admission.py': {'sha256': '32f567c6e1d93e04677ff35ffad01e9927ff1388a70b28f8d8859550732571d0',
                                    'lines': (233,)},
 'tests/test_daemon_config.py': {'sha256': '6e9483b55fee6b99a07f8c2dd781a0fd6072f65691cfde66b02dc01da5dfc2ef',
                                 'lines': (364,)},
 'tests/test_diagnose.py': {'sha256': '13bf2e1824c899efa49714492f536cc6e358247d06adf6323bdc1d53ae6d9777',
                            'lines': (219,)},
 'tests/test_drain.py': {'sha256': 'aa4495c8a2faaec2638a31595c545122c9d83d5f79ec030cf1a323335b8d8409',
                         'lines': (265, 272)},
 'tests/test_drain_reentry.py': {'sha256': '63f5bc289dea1b08cf100994dc54db7643a3eae89af0800e21fdba87be8b6d8b',
                                 'lines': (101,)},
 'tests/test_flake.py': {'sha256': '0cfbf509b9f3bcde98f876a3c01f73c6f10202e340f0cf31ac435f8e60aafd43',
                         'lines': (27, 282, 284, 316, 337, 351, 353, 385, 406)},
 'tests/test_heartbeat.py': {'sha256': '8d8534dfac359f50cccb3a4761e894a00c99ef637b93f34d4f39223a96f8723a',
                             'lines': (217,)},
 'tests/test_kill_failure_suppression.py': {'sha256': 'fad8c01cc71c2e46ed40014aca70d81befd322f991193e00b81d559183e0c968',
                                            'lines': (339,)},
 'tests/test_kill_worker_stop.py': {'sha256': '6099ca1d58db6c928dcd72933ff619da6f45d607656a2b36af2631b8ef03e9eb',
                                    'lines': (315,)},
 'tests/test_merge.py': {'sha256': '0d1ea826aff220ce41dd2164a3ede420d1ad07ea1e629b5809159e0760d78ba2',
                         'lines': (307,)},
 'tests/test_mergequeue.py': {'sha256': 'd3a690502df5c631cb16c31eabe4756e5ecb95f591034f6bc742c2e87a0adf4b',
                              'lines': (273, 411)},
 'tests/test_policy.py': {'sha256': 'b3a3bc0856f5e93021ec149d1e4d1a11bcd2b6c9422cd8308f05aaf20a0250f4',
                          'lines': (42, 82)},
 'tests/test_provider_cooldown_failover.py': {'sha256': 'e8b306d6f6a185806e16360a0a876a27b419d7d4b4db89b2d54333e3be8c48b9',
                                              'lines': (104,)},
 'tests/test_reconcile.py': {'sha256': 'b711465f1faa6e4bc8ac02960c2c0e77a9ac430754d7bad371d7dd98ec69338e',
                             'lines': (10, 123)},
 'tests/test_retro.py': {'sha256': 'b72597ed4ef6dc1cc229ee4aad51c0d4a5800eadbd3694e7192e3dd61a478ad5',
                         'lines': (203, 210, 221, 270)},
 'tests/test_second_problems.py': {'sha256': '386b4c80a3996ddf9af5611b91315444a89f22bf8e2f1a81cb995c32c7d8c16c',
                                   'lines': (39,)},
 'tests/test_stages.py': {'sha256': 'ad0144c96e59c5403029224550d1c80f880bc3743f6130df3a4ebeb8dfa983ff',
                          'lines': (444, 457)},
 'tests/test_storm.py': {'sha256': '2112e5f2aed76ed20638dfa2d1679c49c811698f9b56728fa5152b151b051b1b',
                         'lines': (115, 255)},
 'tests/test_storm_hold.py': {'sha256': '52644ccfed84f447a58ca504376829cabbbdf1e75918590c938b313600b0a941',
                              'lines': (145,)},
 'tests/test_storm_notification_activation.py': {'sha256': '86fd8fedc081dda8496bc401650c1e1c9dc9ea17524d381a5d0f2d37574d855a',
                                                 'lines': (253, 297, 420, 465, 583)},
 'tests/test_storm_producer.py': {'sha256': '20778b89148802e50b977724d81a5e72113ffae572a372b460b7a4d58f63dd1d',
                                  'lines': (30, 56, 215, 221, 262)},
 'tests/test_triage.py': {'sha256': 'afcaa6d44ef47725f18e16b37140ed09a10d27c32a60a2e66347081d850b2169',
                          'lines': (29,)},
 'tests/test_vocabularies.py': {'sha256': 'e14f8d8f9adaf713d5b761d51950d30dd14bd2c1161e204a3f935d31ebef4b43',
                                'lines': (109, 119, 125, 133, 135)},
 'tests/test_watchdog.py': {'sha256': '420a90a554360f05131c20e69caf59adbf877fd434e5a7449d422f7803e11c33',
                            'lines': (177, 182)}}

PRESERVATION = {'tests/test_drain_upgrade.py': '19.L rules 2/5: Script emits real docs merges; child quiescence forces '
                                'retro, invalidating missing-Driver fixture and HEAD~1 handoff-commit '
                                'assumption in '
                                'test_a_self_upgrading_admission_hands_off_before_the_next_dispatch. Pin the '
                                'journaled admission SHA rather than commit offsets and supply the public '
                                'scripted Driver. This activation leaves the invoker and dispatch triggers '
                                'unchanged; shared CLI retro fixtures return empty proposals, so no new Box '
                                'consumption or scheduling assertion is earned.',
 'tests/test_seed_successor.py': '19.L rules 2/5: two work/ merges reach quiescence; '
                                 'test_merged_parent_registers_and_runs_successor_in_same_drain pins exactly '
                                 'five model calls and main equal to last squash. Add the forced retro '
                                 'call/report commit and public stages access while retaining seed '
                                 'lift/dependency assertions. This activation leaves the invoker and '
                                 'dispatch triggers unchanged; shared CLI retro fixtures return empty '
                                 'proposals, so no new Box consumption or scheduling assertion is earned.',
 'tests/test_cli.py': '19.L rules 2/5: shared Stages.__call__ fixture lacks public driver access for forced '
                      'quiescence after its merged terminal; migrate the fixture through the public '
                      'composition with scripted retro output, retaining calls and lock assertions. This '
                      'activation leaves the invoker and dispatch triggers unchanged; shared CLI retro '
                      'fixtures return empty proposals, so no new Box consumption or scheduling assertion is '
                      'earned.',
 'tests/test_daemon_config.py': '19.L rules 2/5: test_config_snapshot_is_dormant supplies a bare dispatch '
                                'which reports merged; migrate only the missing-stage-owner fixture at '
                                'forced quiescence, preserving snapshot and daemon dormancy probes. This '
                                'activation leaves the invoker and dispatch triggers unchanged; shared CLI '
                                'retro fixtures return empty proposals, so no new Box consumption or '
                                'scheduling assertion is earned.',
 'tests/test_daemon_admission.py': '19.L rules 2/5: test_daemon_admission_is_dormant supplies a bare merged '
                                   'dispatch; provide the public scripted stages carrier at quiescence, '
                                   'preserving the daemon-construction/dispatch refusal probes. This '
                                   'activation leaves the invoker and dispatch triggers unchanged; shared '
                                   'CLI retro fixtures return empty proposals, so no new Box consumption or '
                                   'scheduling assertion is earned.',
 'tests/test_daemon_pause.py': '19.L rules 2/5: test_dispatch_pause_boundary_is_active reports merged '
                               'through its custom Script; carry the public Driver for forced quiescence, '
                               'preserving control-consumption and dispatch-count assertions. This '
                               'activation leaves the invoker and dispatch triggers unchanged; shared CLI '
                               'retro fixtures return empty proposals, so no new Box consumption or '
                               'scheduling assertion is earned.',
 'tests/test_reconcile.py': '19.L rules 2/5: test_recovery_alert_does_not_change_disposition wraps Stages in '
                            'a bare prepare callback; propagate the public stages carrier to forced '
                            'quiescence without changing orphan disposition or run-sequence assertions. This '
                            'activation leaves the invoker and dispatch triggers unchanged; shared CLI retro '
                            'fixtures return empty proposals, so no new Box consumption or scheduling '
                            'assertion is earned.',
 'tests/test_flake.py': '19.L rule 2: test_flake_detection_is_dormant and test_flake_release_is_dormant '
                        'assert an empty Box after a synthetic merge. Supply successful scripted retro via '
                        'the shared public fixture so a missing Driver cannot add an unrelated failure '
                        'report; retain flake negatives. This activation leaves the invoker and dispatch '
                        'triggers unchanged; shared CLI retro fixtures return empty proposals, so no new Box '
                        'consumption or scheduling assertion is earned.',
 'tests/test_storm_hold.py': '19.L rules 2/5: test_live_drain_holds_only_emitting_stem uses Script through '
                             'five synthetic merges and quiescence. Give the custom carrier public '
                             'stages/Driver access and script the forced report; retain resume, ordering, '
                             'cap and pending-message assertions. This activation leaves the invoker and '
                             'dispatch triggers unchanged; shared CLI retro fixtures return empty proposals, '
                             'so no new Box consumption or scheduling assertion is earned.',
 'tests/test_storm_notification_activation.py': 'Resolved/recovery fixtures use kind=decision, not '
                                                'tombstone; pending storm arrivals do not count tombstone '
                                                're-reports. CLI retro outputs empty proposals; preserve '
                                                'hold, replay, signal-before-queue and no-consumption '
                                                'assertions.',
 'tests/test_drain_reentry.py': 'Each successful admission changes chupa/thing.py and immediately hands off '
                                'to NoChild; no next dispatch/pre-exit/quiescence hook in that parent. Fixed '
                                'clock and fewer than five gate failures before merge. This activation '
                                'leaves the invoker and dispatch triggers unchanged; shared CLI retro '
                                'fixtures return empty proposals, so no new Box consumption or scheduling '
                                'assertion is earned.',
 'tests/test_ladder.py': 'Successful chupa/thing.py merges immediately hand off to NoChild; at most three '
                         'gate_failed terminals before that handoff, no exit ticket, and fixed clock. '
                         'Refused-split follow-up has no merge and one gate failure. This activation leaves '
                         'the invoker and dispatch triggers unchanged; shared CLI retro fixtures return '
                         'empty proposals, so no new Box consumption or scheduling assertion is earned.',
 'tests/test_diagnose.py': 'The drain case has two failures then a chupa/thing.py upgrade to NoChild; no '
                           'forced quiescence is reached, no spike threshold or elapsed window. This '
                           'activation leaves the invoker and dispatch triggers unchanged; shared CLI retro '
                           'fixtures return empty proposals, so no new Box consumption or scheduling '
                           'assertion is earned.',
 'tests/test_harvest.py': 'The drain re-entry ends in chupa/thing.py self-upgrade to NoChild after two infra '
                          'failures; the parent never reaches forced quiescence, and infra_error is not a '
                          'retro spike operand. This activation leaves the invoker and dispatch triggers '
                          'unchanged; shared CLI retro fixtures return empty proposals, so no new Box '
                          'consumption or scheduling assertion is earned.',
 'tests/test_audit.py': 'The real chupa/thing.py merge hands off to NoChild before the other red stem; the '
                        'parent never reaches forced quiescence or a due threshold. This activation leaves '
                        'the invoker and dispatch triggers unchanged; shared CLI retro fixtures return empty '
                        'proposals, so no new Box consumption or scheduling assertion is earned.',
 'tests/test_storm_producer.py': 'test_dedup_preserves_resolved_message_and_incoming_identity resolves '
                                 'kind=decision, not tombstone; its write-free signature dedup remains '
                                 'unchanged. Shared wrapper signature stays fixed.',
 'tests/test_provider_cooldown_failover.py': 'Calls drain directly with the default-off hook; the escalated '
                                             'route uses already_satisfied. Provider recovery tests run '
                                             'CoreRig or serve, not main drain. This activation leaves the '
                                             'invoker and dispatch triggers unchanged; shared CLI retro '
                                             'fixtures return empty proposals, so no new Box consumption or '
                                             'scheduling assertion is earned.',
 'tests/test_watchdog_activation.py': 'CoreRig scheduler/serve compositions exercise watched calls and '
                                      'timeout harvest; none wires the CLI drain retro hook. This activation '
                                      'leaves the invoker and dispatch triggers unchanged; shared CLI retro '
                                      'fixtures return empty proposals, so no new Box consumption or '
                                      'scheduling assertion is earned.',
 'tests/test_restart_timers.py': 'CoreRig and Restart direct composition; no CLI drain retro hook, despite '
                                 'scheduler merges. This activation leaves the invoker and dispatch triggers '
                                 'unchanged; shared CLI retro fixtures return empty proposals, so no new Box '
                                 'consumption or scheduling assertion is earned.',
 'tests/test_kill_cli_activation.py': 'Live CLI kill ends nonquiescent without a merge; default-off '
                                      'LiveDrain and CoreRig own the other cases. already_satisfied does not '
                                      'land a merge. This activation leaves the invoker and dispatch '
                                      'triggers unchanged; shared CLI retro fixtures return empty proposals, '
                                      'so no new Box consumption or scheduling assertion is earned.',
 'tests/test_kill_executor_abort.py': 'Active abort probes run direct LiveDrain/default-off or CoreRig; kill '
                                      'stops before a merge/forced quiescence. This activation leaves the '
                                      'invoker and dispatch triggers unchanged; shared CLI retro fixtures '
                                      'return empty proposals, so no new Box consumption or scheduling '
                                      'assertion is earned.',
 'tests/test_kill_signal_journal.py': 'Active kill-signal probes use direct LiveDrain/default-off and '
                                      'CoreRig; no CLI merged quiescence. This activation leaves the invoker '
                                      'and dispatch triggers unchanged; shared CLI retro fixtures return '
                                      'empty proposals, so no new Box consumption or scheduling assertion is '
                                      'earned.',
 'tests/test_seed_path.py': 'The only main drain re-entry refuses an unresolved spec gap and settles the '
                            'other paths already_satisfied; no merge, five spikes, elapsed window, or phase '
                            'exit. This activation leaves the invoker and dispatch triggers unchanged; '
                            'shared CLI retro fixtures return empty proposals, so no new Box consumption or '
                            'scheduling assertion is earned.',
 'tests/test_reject_queue.py': 'Scripted drain terminal markers have no admitted commit; shared Script '
                               'migration in fenced test_drain.py supplies any forced call. Queue assertions '
                               'themselves remain unchanged. This activation leaves the invoker and dispatch '
                               'triggers unchanged; shared CLI retro fixtures return empty proposals, so no '
                               'new Box consumption or scheduling assertion is earned.',
 'tests/test_caps.py': 'Direct synthetic drain uses shared test_drain.py Script migration; spent-cap '
                       'assertions do not flip and no new direct composition signature is introduced. This '
                       'activation leaves the invoker and dispatch triggers unchanged; shared CLI retro '
                       'fixtures return empty proposals, so no new Box consumption or scheduling assertion '
                       'is earned.',
 'tests/test_control_cli.py': 'Fenced tests/test_cli.py::Stages.__call__ gains the public stages carrier and '
                              'scripted forced retro after the synthetic merge. This suite keeps calls/lock '
                              'and its unrelated dormancy/absence assertions unchanged; direct '
                              'CoreRig/LiveDrain hooks remain off. This activation leaves the invoker and '
                              'dispatch triggers unchanged; shared CLI retro fixtures return empty '
                              'proposals, so no new Box consumption or scheduling assertion is earned.',
 'tests/test_daemon_tasks.py': 'Fenced tests/test_cli.py::Stages.__call__ gains the public stages carrier '
                               'and scripted forced retro after the synthetic merge. This suite keeps '
                               'calls/lock and its unrelated dormancy/absence assertions unchanged; direct '
                               'CoreRig/LiveDrain hooks remain off. This activation leaves the invoker and '
                               'dispatch triggers unchanged; shared CLI retro fixtures return empty '
                               'proposals, so no new Box consumption or scheduling assertion is earned.',
 'tests/test_heartbeat.py': 'Fenced tests/test_cli.py::Stages.__call__ gains the public stages carrier and '
                            'scripted forced retro after the synthetic merge. This suite keeps calls/lock '
                            'and its unrelated dormancy/absence assertions unchanged; direct '
                            'CoreRig/LiveDrain hooks remain off. This activation leaves the invoker and '
                            'dispatch triggers unchanged; shared CLI retro fixtures return empty proposals, '
                            'so no new Box consumption or scheduling assertion is earned.',
 'tests/test_checkpoint.py': 'Fenced tests/test_cli.py::Stages.__call__ gains the public stages carrier and '
                             'scripted forced retro after the synthetic merge. This suite keeps calls/lock '
                             'and its unrelated dormancy/absence assertions unchanged; direct '
                             'CoreRig/LiveDrain hooks remain off. This activation leaves the invoker and '
                             'dispatch triggers unchanged; shared CLI retro fixtures return empty proposals, '
                             'so no new Box consumption or scheduling assertion is earned.',
 'tests/test_kill_worker_stop.py': 'Fenced tests/test_cli.py::Stages.__call__ gains the public stages '
                                   'carrier and scripted forced retro after the synthetic merge. This suite '
                                   'keeps calls/lock and its unrelated dormancy/absence assertions '
                                   'unchanged; direct CoreRig/LiveDrain hooks remain off. This activation '
                                   'leaves the invoker and dispatch triggers unchanged; shared CLI retro '
                                   'fixtures return empty proposals, so no new Box consumption or scheduling '
                                   'assertion is earned.',
 'tests/test_kill_failure_suppression.py': 'Fenced tests/test_cli.py::Stages.__call__ gains the public '
                                           'stages carrier and scripted forced retro after the synthetic '
                                           'merge. This suite keeps calls/lock and its unrelated '
                                           'dormancy/absence assertions unchanged; direct CoreRig/LiveDrain '
                                           'hooks remain off. This activation leaves the invoker and '
                                           'dispatch triggers unchanged; shared CLI retro fixtures return '
                                           'empty proposals, so no new Box consumption or scheduling '
                                           'assertion is earned.',
 'tests/test_driver.py': 'Driver producers inherit the callback from storm_producer without new parameters; '
                         'preserve exit-window materialization, grants, timeouts and diagnostics. Existing '
                         'fixtures do not re-report tombstones.',
 'tests/test_storm.py': 'Ledger and shared producer signature remain fixed; direct ledger tests and pending '
                        'arrivals do not reopen tombstones.',
 'tests/test_plan_lint.py': 'Unchanged lint suite; entry-depth helper proofs are created in fenced '
                            'tests/test_retro_box.py, following merged tests/test_retro.py.'}

DELIMITER_FREE_CONTEXT = {'chupa/policy.py': True,
 'chupa/status.py': True,
 'tests/test_policy.py': True,
 'tests/test_box.py': True,
 'tests/test_vocabularies.py': True,
 'tests/test_author.py': True,
 'chupa/author.py': True,
 'tests/test_triage.py': True,
 'chupa/box.py': True,
 'chupa/triage.py': True,
 'chupa/journal.py': True,
 'chupa/retro.py': True,
 'tests/test_retro.py': True,
 'chupa/__main__.py': True,
 'chupa/merge.py': True,
 'chupa/serve.py': True,
 'chupa/driver.py': True,
 'chupa/daemon.py': True,
 'tests/test_merge.py': True,
 'tests/test_seeded_phase3_core.py': True}

PREDECESSOR_SHA256 = 'f7041f0a5ad3e9702abc0a3bac33fc0c3e68c881cb64a2bcaa6954d1c9d9b70a'


def _body(t):
    return '\n'.join(t.sections.values())


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[uid] for uid in a['plan'])
            + sum(FILE_SIZES[p]['chars'] for p in (*a['context'], *extra)))


def test_exact_admission_and_finite_continuation():
    assert BATCH == ('retro-box-activation', 'phase5-continue-02')
    assert REGISTRY['phase'] == 5
    assert tuple(REGISTRY['seeds']) == tuple(s for a in REGISTRY['admissions'] for s in a)
    assert POSITION == 1
    assert UNSEEDED_SUFFIX == (('retro-box-activation',), ('scorecard-reporting',),
                               ('status-projection', 'baseline-binding-reader'),
                               ('retro-doctor-cli',), ('phase5-exit',))
    assert UNSEEDED_SUFFIX == tuple(tuple(a) for a in REGISTRY['admissions'][POSITION:])
    assert len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    # Each later admission shrinks by one, includes its successor in the cap, and terminates.
    for n, admission in enumerate(REGISTRY['admissions'][POSITION:], POSITION):
        terminal = n == len(REGISTRY['admissions']) - 1
        assert len(admission) + (not terminal) <= MAX_SEEDS_PER_ADMISSION
        assert len(REGISTRY['admissions'][n + 1:]) < len(REGISTRY['admissions'][n:])
        if terminal:
            assert admission == ['phase5-exit'] and REGISTRY['seeds'][admission[0]]['exit']


@pytest.mark.parametrize('stem', BATCH)
def test_grammar_birth_edges_fence_and_budgets(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    tier = 'high' if stem == BATCH[0] else 'medium'
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == (tier, tier)
    assert t.depends == a['depends']
    assert t.scope_fence == a['fence']
    assert t.plan_contract == a['plan']
    assert t.expected_minutes == a['expected'] < t.stuck_minutes == a['stuck'] <= DRAIN_MAX_TICKET_MINUTES
    if stem == BATCH[0]:
        assert set(t.depends) == {'phase5-continue', *REGISTRY['seeds'][stem]['depends']}
        assert set(t.scope_fence) == set(REGISTRY['seeds'][stem]['fence']) | set(FENCE_ADDITIONS)
        assert REGISTRY['seeds'][stem]['deep'] is True and 'KNOWN-DEEP' in _body(t)
        assert t.plan_contract == ('19.I', '19.P5.retro-box-activation', '12')
    else:
        assert t.depends == ('retro-box-activation',)
        assert t.scope_fence == ('tickets', 'tests/test_seeded_phase5_02.py')
        assert t.plan_contract == ('19.L', '19.I', '19.P5', '19.P5.scorecard-reporting', '14', '13')


@pytest.mark.parametrize('stem', BATCH)
def test_authored_partition_and_fixed_maximum_effort_render(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert not set(t.context) & set(t.on_demand)
    assert render_chars(stem) <= HEADROOM_CHARS == 300_000
    if stem == BATCH[0]:
        assert set(FENCED_EXISTING) == set(t.context) | set(t.on_demand)
        assert not set(CREATED) & (set(t.context) | set(t.on_demand))
    else:
        assert t.context == ('tests/test_seeded_phase3_core.py',) and not t.on_demand
    for p in t.on_demand:
        assert render_chars(stem, (p,)) > HEADROOM_CHARS, p
    assert all(not p.startswith(('specs/', 'tickets/')) for p in t.context)
    assert 'tests/test_plan_lint.py' not in (*t.context, *t.scope_fence, *t.on_demand)
    assert all(DELIMITER_FREE_CONTEXT[p] for p in t.context)


def test_authoring_measurements_are_complete():
    assert re.fullmatch(r'[0-9a-f]{40}', AUTHORING_HEAD)
    assert re.fullmatch(r'[0-9a-f]{40}', IDIOM_BLOB)
    assert re.fullmatch(r'[0-9a-f]{64}', PREDECESSOR_SHA256)
    for data in FILE_SIZES.values():
        assert 0 < data['chars'] <= data['bytes']
    for stem, a in AUTHORED.items():
        raw = (ROOT / ticket_path(stem)).read_bytes()
        # Pin text without live render measurements: sizes above remain the arithmetic authority.
        assert hashlib.sha256(raw).hexdigest() == a['sha256']
        assert 0 < a['chars'] <= a['bytes']


def test_required_entry_depth_was_proven_before_authoring_both_seeds():
    assert REQUIRED == {'retro-box-activation': ('19.P5.retro-box-activation',),
                        'phase5-continue-02': ('19.P5.scorecard-reporting',)}
    assert set(ENTRY_DEPTH) == {u for units in REQUIRED.values() for u in units}
    for uid, e in ENTRY_DEPTH.items():
        assert e['gap'] is None and e['resolves'] == 1
        assert set(e['parts']) == {'Owner', 'Records', 'Observable', 'Tests'}
        assert all(n > 0 for n in e['parts'].values())
        assert re.fullmatch(r'[0-9a-f]{64}', e['sha256'])
        assert e['chars'] == PLAN_CHARS[uid]
        for stem, units in REQUIRED.items():
            if uid in units:
                for obligation in e['tests']:
                    assert obligation in _body(_ticket(stem))


def test_named_obligations_and_plan_proof_have_fenced_owners():
    t = _ticket(BATCH[0])
    names = ENTRY_DEPTH['19.P5.retro-box-activation']['tests']
    assert len(names) == 11
    for word in ('required_units', 'resolve_plan_contract', 'entry_unit_gap',
                 'test_retro_box_entry_unit', 'Keep tests/test_plan_lint.py green unchanged'):
        assert word in _body(t)
    assert 'tests/test_retro_box.py' in CREATED and 'tests/test_retro_box.py' in t.scope_fence
    assert {'tests/test_status.py', 'tests/test_retro.py', 'chupa/journal.py',
            'tests/test_vocabularies.py', 'chupa/driver.py'} == set(FENCE_ADDITIONS)
    assert all('19.L' in reason for reason in FENCE_ADDITIONS.values())
    for signal in ('tombstone_auto_reopened', 'retro_ticket_authored', 'retro_prompt_spec_change_merged'):
        assert signal in _body(t) and signal in FENCE_ADDITIONS['chupa/journal.py']


def test_production_caller_and_predecessor_closure():
    t = _ticket(BATCH[0])
    assert set(PRODUCTION_CALLERS) == {'chupa/box.py', 'chupa/daemon.py', 'chupa/triage.py',
        'chupa/driver.py', 'chupa/stages.py', 'chupa/runner.py', 'chupa/__main__.py', 'chupa/retro.py'}
    assert set(PRODUCTION_CALLERS) <= set(t.scope_fence)
    assert all(e['lines'] and re.fullmatch(r'[0-9a-f]{64}', e['sha256']) for e in CLOSURE_SCAN.values())
    for phrase in ('bootstrap ingestion', 'operator triage', 'storm_producer',
                   'Signature and semantic dedup', 'existing-record recovery',
                   'policy.start_state(reopen=...)', 'real squash SHA', 'message_class',
                   'Bootstrap drain still never scans the Box', 'worker/task counts stay fixed',
                   'test_receipt_uses_engine_provenance_usage_calibration_and_tombstones',
                   'Stages.driver/Pipeline.stages', 'baseline-binding-reader'):
        assert phrase in _body(t)


def test_preservation_suites_are_verification_only():
    t = _ticket(BATCH[0])
    commands = {p for argv in t.verification for p in argv}
    assert set(PRESERVATION) <= commands
    assert not set(PRESERVATION) & set((*t.scope_fence, *t.context, *t.on_demand))
    assert all(reason for reason in PRESERVATION.values())
    assert 'kind=decision' in PRESERVATION['tests/test_storm_producer.py']


def test_successor_position_and_check_custody_are_explicit():
    t = _ticket(BATCH[1])
    for phrase in ('Position 02', 'admissions[2:]', 'position 03', 'admissions[3:]',
                   'phase5-continue-03 depends only on scorecard-reporting',
                   'last admission authors only phase5-exit without a successor',
                   'requisition_review', 'single ticket-plane seed lift',
                   'Retain approved bytes while ticket_sha matches',
                   'seeding.max_seeds_per_admission', 'drain.max_ticket_minutes'):
        assert phrase in _body(t)
    assert 'tests/test_seeded_phase5_03.py' in _body(t)
    assert 'only the new batch test is committed' in _body(t)
