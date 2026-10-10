"""Terminal admission snapshots; only seed identity reads current ticket bytes.

Depth, closure and max-effort operands are immutable authoring evidence.
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

AUTHORING_HEAD = 'f8f65bde6cd3fd92bb50a9abad277ef8fd52c831'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

POSITION = 8

REGISTRY_ADMISSIONS = (('core-renderer', 'core-drift-classifier'),
 ('core-drift-activation', 'migrate-config'),
 ('host-contract-doc', 'fixture-host-scaffold'),
 ('bug-gate-grammar', 'report-inbox-triage'),
 ('escape-column',),
 ('supervised-merge-hold',),
 ('go-grade-machinery', 'go-grade-run'),
 ('exit-receipt-machinery',),
 ('phase6-exit',))

REGISTRY_ROW = {'exit': True,
 'depends': ['exit-receipt-machinery'],
 'fence': ['tickets/phase6-exit/host-loop-report.json',
           'tickets/phase6-exit/exit-receipt.json',
           'tests/test_phase6_exit.py'],
 'does': 'Runs eval/host_loop.py, reads the committed GO-grade report, commits the RECEIPT; no '
         'seeds, no engine edit.'}

BATCH = ('phase6-exit',)

UNSEEDED_SUFFIX = (('phase6-exit',),)

EDGES = ('phase6-continue-08', 'exit-receipt-machinery')

PLAN_IDS = ('19.L',
 '19.I',
 '19.P6',
 '19.P6.exit-receipt-machinery',
 '19.P6.fixture-host-scaffold',
 '19.P6.supervised-merge-hold',
 '19.P6.go-grade-machinery',
 '19.P6.go-grade-run')

REQUIRED = ('19.P6.exit-receipt-machinery',
 '19.P6.fixture-host-scaffold',
 '19.P6.supervised-merge-hold',
 '19.P6.go-grade-machinery',
 '19.P6.go-grade-run')

PLAN_SIZES = {'19.L': {'bytes': 20912,
          'chars': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa',
          'delimiter_free': True},
 '19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c',
          'delimiter_free': True},
 '19.P6': {'bytes': 11595,
           'chars': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c',
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
                                  'sha256': 'b8275a4dd5817f3f1ea2459500f0e1ef3c31e8a9c55ea0e8b6789fa88e8d2f2d'},
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
                                 'sha256': 'f67e09cc8d94030c66a580cdd0f794e4472aa0ccde256dc823ab3c8a0e56fbfc'},
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
                                 'sha256': '0696b361fa55905a2bb037b29c42e1f2fd71679c3435af34fcaf8b2c471d905a'},
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
                              'sha256': '20a0533364c7e5cae0e8cd1bf7358d41f574a6158624933b711fed49fb5a1929'},
 '19.P6.go-grade-run': {'resolves': 1,
                        'gap': None,
                        'parts': {'Owner': 483, 'Records': 1041, 'Observable': 813, 'Tests': 910},
                        'missing_part_rejected': {'Owner': True,
                                                  'Records': True,
                                                  'Observable': True,
                                                  'Tests': True},
                        'missing_unit_rejected': True,
                        'duplicate_rejected': True,
                        'sha256': 'b2c959c1c85c04990f5422dbd9371ca3ddc8d02287e7ce54f17516d2d070466a'}}

FILE_SIZES = {'eval/host_loop.py': {'bytes': 17966,
                       'chars': 17966,
                       'sha256': 'b2055fec7300a3c298a7843f2c564eb059dae57f665361dcf224efd5254c1fbe',
                       'delimiter_free': True},
 'chupa/artifacts.py': {'bytes': 21501,
                        'chars': 21501,
                        'sha256': '83d09e7262dd5747dd1e13fd604b7e653c5c046564552fba96eeaddd1f5d2d17',
                        'delimiter_free': True},
 'chupa/git.py': {'bytes': 8565,
                  'chars': 8565,
                  'sha256': '686cb0a3e47811706485ed2fd3da42307b0c6abaa334b36448de2093ea2a7dfe',
                  'delimiter_free': True},
 'tickets/go-grade-run/review-baseline-report.json': {'bytes': 14453,
                                                      'chars': 14448,
                                                      'sha256': 'ee377d11d5e88eb3e28f62619dabb3406817eba797caeee78f355549c44e02b0',
                                                      'delimiter_free': True}}

HISTORICAL_SNAPSHOTS = {'tests/test_seeded_phase6_01.py': {'bytes': 57492,
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
                                    'delimiter_free': True},
 'tests/test_seeded_phase6_07.py': {'bytes': 50923,
                                    'chars': 50923,
                                    'sha256': '56623910ac60af40e18ff69d22c62bd00c6eb080d725a5c8d8d82476eec8360b',
                                    'delimiter_free': True},
 'tests/test_seeded_phase6_core.py': {'bytes': 35196,
                                      'chars': 35196,
                                      'sha256': '7606a766e009e53284c8154c971847ed5f58b20dfff3f945266d35a324870cae',
                                      'delimiter_free': True},
 'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559',
                                      'delimiter_free': True}}

TICKET_SIZE = {'bytes': 8296,
 'chars': 8296,
 'sha256': '4757af0cbc5848bc190914fa9a480d9f494203c079b0f84bb03397af931f7134',
 'delimiter_free': True}

CONTEXT = ('eval/host_loop.py',
 'chupa/artifacts.py',
 'chupa/git.py',
 'tickets/go-grade-run/review-baseline-report.json')

ON_DEMAND = ()

FENCED_EXISTING = ()

CREATED = ('tickets/phase6-exit/host-loop-report.json',
 'tickets/phase6-exit/exit-receipt.json',
 'tests/test_phase6_exit.py')

FENCE_ADDITIONS = ()

CLOSURE_EVIDENCE = {}

CLOSURE_SCAN = {'chupa': {'files': ('chupa/artifacts.py', 'chupa/stages.py'),
           'matched_lines': 9,
           'sha256': 'a9735df1cba20163ba492e5fc9968381ba32428868135c065cc759f585c54304'},
 'eval': {'files': ('eval/host_loop.py',),
          'matched_lines': 8,
          'sha256': '6a1cd49b8452b2320f7fdd6c66d1854a944b29707c4205a9a70875237a519273'},
 'tests': {'files': ('tests/test_driver.py',
                     'tests/test_gates.py',
                     'tests/test_host_loop.py',
                     'tests/test_seeded_phase6_01.py',
                     'tests/test_seeded_phase6_02.py',
                     'tests/test_seeded_phase6_03.py',
                     'tests/test_seeded_phase6_04.py',
                     'tests/test_seeded_phase6_05.py',
                     'tests/test_seeded_phase6_06.py',
                     'tests/test_seeded_phase6_07.py',
                     'tests/test_seeded_phase6_core.py',
                     'tests/test_stages.py'),
           'matched_lines': 128,
           'sha256': '43489025cc1aa360253d4e8a3d51bff295dbce7345373b30f20746a6639ed3f5'}}

COMMITTED_GRAPH = {'exit-receipt-machinery': {'depends': ('phase6-continue-07', 'go-grade-run'),
                            'bytes': 8420,
                            'chars': 8420,
                            'sha256': '141fe96a0f73bb691e794ec40061ebbed3b66f704b549fa67af2f5eaa894772f',
                            'delimiter_free': True},
 'go-grade-run': {'depends': ('phase6-continue-06', 'go-grade-machinery'),
                  'bytes': 2920,
                  'chars': 2920,
                  'sha256': 'dfdfc2c36e76b60ea6ad5686b313799ea8390caaf22b9fc1405c20347312648d',
                  'delimiter_free': True},
 'go-grade-machinery': {'depends': ('phase6-continue-06',
                                    'supervised-merge-hold',
                                    'fixture-host-scaffold'),
                        'bytes': 9532,
                        'chars': 9532,
                        'sha256': 'a0cf4742a9f40290b6ffc3c046dea88c3e490bb52bbef2a876715c048849f3a3',
                        'delimiter_free': True},
 'fixture-host-scaffold': {'depends': ('phase6-continue-02',
                                       'host-contract-doc',
                                       'core-drift-activation'),
                           'bytes': 4797,
                           'chars': 4797,
                           'sha256': 'e5a41f1fd477d0d4eb80bbb6cb15df980414ea4d279b78df5e4b3c7e1757d4df',
                           'delimiter_free': True},
 'core-drift-activation': {'depends': ('phase6-continue', 'core-drift-classifier'),
                           'bytes': 8019,
                           'chars': 8019,
                           'sha256': 'b4956f220b8753eea9187529859ffc7e1f64b563e5fdb4d47baf993b4d5d8826',
                           'delimiter_free': True},
 'core-drift-classifier': {'depends': ('phase5-exit', 'core-renderer'),
                           'bytes': 5176,
                           'chars': 5176,
                           'sha256': 'a2f35a19d1a255061cc26209c60d69d48f0736f67eeafe5eac8960dea9a35f05',
                           'delimiter_free': True},
 'core-renderer': {'depends': ('phase5-exit',),
                   'bytes': 4228,
                   'chars': 4228,
                   'sha256': 'd125a88d0435d15d262ebcf29ba6123e7c65eba752f333ffa907c3c7e66468b8',
                   'delimiter_free': True},
 'phase5-exit': {'depends': ('phase5-continue-05',),
                 'bytes': 11241,
                 'chars': 11241,
                 'sha256': '713afa1094e62b1e028be14bd3cf7798a154962fb9fb9f474d5c137fe8ad10ef',
                 'delimiter_free': True},
 'phase5-continue-05': {'depends': ('retro-doctor-cli',),
                        'bytes': 5627,
                        'chars': 5627,
                        'sha256': 'a51bf33ababa7461e392c2ecedcae8f1f3c500c9430c3d75cadc6b446acf1b5e',
                        'delimiter_free': True},
 'retro-doctor-cli': {'depends': ('phase5-continue-04',),
                      'bytes': 4572,
                      'chars': 4572,
                      'sha256': 'fd22939843bcf1e00cecc99c0e128281c1e36167701fdbb4fffd4ed90c4f6b51',
                      'delimiter_free': True},
 'phase5-continue-04': {'depends': ('status-projection', 'baseline-binding-reader'),
                        'bytes': 5469,
                        'chars': 5469,
                        'sha256': '1739d6a605eac6ecd413d489789fd52cdecc706b51eb8981c48c8e700524e39a',
                        'delimiter_free': True},
 'baseline-binding-reader': {'depends': ('phase5-continue-03', 'retro-box-activation'),
                             'bytes': 4171,
                             'chars': 4171,
                             'sha256': '941aa1aa6adc4952ab9c674548dbb487afec8940c3e3dff0f935e4008eecde17',
                             'delimiter_free': True},
 'retro-box-activation': {'depends': ('phase5-continue', 'retro-drain-invoker'),
                          'bytes': 10278,
                          'chars': 10278,
                          'sha256': 'ba12168f00aff22003c68ce97caa6509c743accf46bbbda08ff45e3c94736d6c',
                          'delimiter_free': True},
 'retro-drain-invoker': {'depends': ('phase4-exit',),
                         'bytes': 7752,
                         'chars': 7752,
                         'sha256': 'f7041f0a5ad3e9702abc0a3bac33fc0c3e68c881cb64a2bcaa6954d1c9d9b70a',
                         'delimiter_free': True},
 'phase4-exit': {'depends': ('phase4-continue-05',),
                 'bytes': 11513,
                 'chars': 11513,
                 'sha256': '4b82fc1c00738cdad4292a4664c4fd6abe04ad844d0f844d4edc74bf732aef3c',
                 'delimiter_free': True},
 'phase4-continue-05': {'depends': ('reliability-run',),
                        'bytes': 6000,
                        'chars': 6000,
                        'sha256': '32fff4b43d25c33a7bb316aabacc38c90756e46fcbfe323f2aa45450492ff606',
                        'delimiter_free': True},
 'reliability-run': {'depends': ('phase4-continue-04',
                                 'reliability-battery',
                                 'provider-cooldown-failover',
                                 'outbox-only-admission'),
                     'bytes': 5151,
                     'chars': 5151,
                     'sha256': '6202f547d1aa7346c150abdb822a1c34ec1742ad61fb4e864f13919e5222aa63',
                     'delimiter_free': True},
 'outbox-only-admission': {'depends': ('phase3-continue-23',),
                           'bytes': 5831,
                           'chars': 5831,
                           'sha256': 'f8dc786d52b8baaf0be856a497b09d8a57791e3c90f76cf01c103833f09bfe7f',
                           'delimiter_free': True},
 'phase3-continue-23': {'depends': ('worker-recovery-disposition',),
                        'bytes': 9346,
                        'chars': 9346,
                        'sha256': '7df5a67381ea5a9e59840b642d2184609c327285b7673fff6946639efee72f5e',
                        'delimiter_free': True},
 'worker-recovery-disposition': {'depends': ('phase3-continue-22',),
                                 'bytes': 5216,
                                 'chars': 5216,
                                 'sha256': '4c60c57c038d3d3ce2425cdf197567deec9a92dc57912917e5f27170ed376980',
                                 'delimiter_free': True},
 'phase3-continue-22': {'depends': ('serve-merge-admission',),
                        'bytes': 9622,
                        'chars': 9622,
                        'sha256': 'c66ab8b7dcf9525d0efa52beebba8d6e63da4b947d387bded36bffe7e63c01a7',
                        'delimiter_free': True},
 'serve-merge-admission': {'depends': ('phase3-continue-21',),
                           'bytes': 7824,
                           'chars': 7824,
                           'sha256': 'c785a1edb5d69076fda33c0b860df3e8fef0503d6e26065d000c36efb4173e80',
                           'delimiter_free': True},
 'phase3-continue-21': {'depends': ('serve-activation',),
                        'bytes': 10600,
                        'chars': 10600,
                        'sha256': '5272a46dd05b8d85a9e2fd435f91d638022e6b901a14404beae2b10f9a4cd7d8',
                        'delimiter_free': True},
 'serve-activation': {'depends': ('phase3-continue-20',),
                      'bytes': 8235,
                      'chars': 8235,
                      'sha256': '83bb18569328c58a069bc93d46beaf0f7dbb9b5acba5965373533f2ab6cc3cc8',
                      'delimiter_free': True},
 'phase3-continue-20': {'depends': ('checkpoint-push',),
                        'bytes': 10055,
                        'chars': 10055,
                        'sha256': 'bb57d8edef992b81c14527b96af0842e37df0aafa89dcde7ca2410397baf6a60',
                        'delimiter_free': True},
 'checkpoint-push': {'depends': ('phase3-continue-19',),
                     'bytes': 4676,
                     'chars': 4676,
                     'sha256': '98e8fe03c19b586990fedfbb8afbe078da3422116cfb2de1262ae40df73c2803',
                     'delimiter_free': True},
 'phase3-continue-19': {'depends': ('storm-dispatch-hold',),
                        'bytes': 8871,
                        'chars': 8871,
                        'sha256': '98fe7d8c77f3368431caa53c7b66f294ee49aaa86fa8372cd125dbe66b5b80d2',
                        'delimiter_free': True},
 'storm-dispatch-hold': {'depends': ('phase3-continue-18',),
                         'bytes': 6795,
                         'chars': 6795,
                         'sha256': '32f104f83d56160ff59223111a6c073da705e8df3402196e3e135a54fab20828',
                         'delimiter_free': True},
 'phase3-continue-18': {'depends': ('storm-producer-wiring', 'storm-notification-activation'),
                        'bytes': 9184,
                        'chars': 9184,
                        'sha256': '30c1133e23d7c20ea1ce9faf4bf42009399435facf0c6bcac090ce0413871101',
                        'delimiter_free': True},
 'storm-notification-activation': {'depends': ('phase3-continue-17', 'storm-producer-wiring'),
                                   'bytes': 5504,
                                   'chars': 5504,
                                   'sha256': 'd353706e9533b8ca6347f4d3838bc185b9b7f17f225c537ed3d7c69f80c4b56e',
                                   'delimiter_free': True},
 'storm-producer-wiring': {'depends': ('phase3-continue-17',),
                           'bytes': 4172,
                           'chars': 4172,
                           'sha256': 'e6f41cb5cb3d9b1ed5d8e98aeedf63b860ac3d7abba9a64571c3dd2c8c466126',
                           'delimiter_free': True},
 'phase3-continue-17': {'depends': ('journal-roll', 'storm-ledger'),
                        'bytes': 10309,
                        'chars': 10309,
                        'sha256': 'f4a3995eb286d4c743730f97e31cd7a03fc351c7e7d6f6fecee309f217160177',
                        'delimiter_free': True},
 'storm-ledger': {'depends': ('phase3-continue-16', 'journal-roll'),
                  'bytes': 3198,
                  'chars': 3198,
                  'sha256': '506c384a0feac8a2cbec3d1cc6ac22e1019df1d0476c3e2e62847be6bf5da244',
                  'delimiter_free': True},
 'journal-roll': {'depends': ('phase3-continue-16',),
                  'bytes': 3095,
                  'chars': 3095,
                  'sha256': '6b558490aa5531834a449c4949198d376a49217add8fb9a49846aca654b7d3bf',
                  'delimiter_free': True},
 'phase3-continue-16': {'depends': ('flake-detection', 'flake-release'),
                        'bytes': 9333,
                        'chars': 9333,
                        'sha256': '137a8c68411afe93489cd583755af149099070c61e8e1370768e61f6fd2276cd',
                        'delimiter_free': True},
 'flake-release': {'depends': ('phase3-continue-15', 'flake-detection'),
                   'bytes': 4587,
                   'chars': 4585,
                   'sha256': 'b8ad48af3a72fe636f031b22fb5456d6b8d4bfe0fc1e390caa9ba17d8c94fee1',
                   'delimiter_free': True},
 'flake-detection': {'depends': ('phase3-continue-15',),
                     'bytes': 4858,
                     'chars': 4856,
                     'sha256': 'bf8b901090cb200a034ef66ca7d06c71e89d65c57c4e44ae94a7685855b94711',
                     'delimiter_free': True},
 'phase3-continue-15': {'depends': ('restart-timers',),
                        'bytes': 9095,
                        'chars': 9095,
                        'sha256': '3b3e8dfbcda61f07f2177940ad5c31a81fcafacd0ac39194e19bdef38314152c',
                        'delimiter_free': True},
 'restart-timers': {'depends': ('phase3-continue-14',),
                    'bytes': 5531,
                    'chars': 5531,
                    'sha256': '0edff8f438b031a9fbd1f510605e56fb8a8df523cb89f8a990f7d16caa603d32',
                    'delimiter_free': True},
 'phase3-continue-14': {'depends': ('heartbeat',),
                        'bytes': 9365,
                        'chars': 9365,
                        'sha256': '90aa9b8639ed83d323a0c66c7dcdcc8dab43d3e4934e5d0e799e26817cd54440',
                        'delimiter_free': True},
 'heartbeat': {'depends': ('phase3-continue-13',),
               'bytes': 4357,
               'chars': 4357,
               'sha256': '75b2567991e967008062004a1463e95a007768b66f9a4c3346c76d0bed2323ae',
               'delimiter_free': True},
 'phase3-continue-13': {'depends': ('kill-cli-activation',),
                        'bytes': 9005,
                        'chars': 9005,
                        'sha256': '184e2b959249fefee905cc5a54e891807f55095caf55efcb95837543a25b8da8',
                        'delimiter_free': True},
 'kill-cli-activation': {'depends': ('phase3-continue-12',),
                         'bytes': 5114,
                         'chars': 5114,
                         'sha256': 'b6f4043da5ff8335a916295a79dc9e32170e59dae4e3cb3d0f39fa34c4bb647a',
                         'delimiter_free': True},
 'phase3-continue-12': {'depends': ('kill-worker-stop', 'kill-failure-suppression'),
                        'bytes': 10136,
                        'chars': 10136,
                        'sha256': 'de7ade721be7049b27d5c4c95a2b53432018e986cc46b6f6194a68d490953d64',
                        'delimiter_free': True},
 'kill-failure-suppression': {'depends': ('phase3-continue-11', 'kill-worker-stop'),
                              'bytes': 2960,
                              'chars': 2960,
                              'sha256': '9f3f9df4695ce5878c6c44a280fe3de12023c15ca9c2f8e7c516af6ff56e01ae',
                              'delimiter_free': True},
 'kill-worker-stop': {'depends': ('phase3-continue-11',),
                      'bytes': 2891,
                      'chars': 2891,
                      'sha256': '578bfeee5c89faa07e6315e2c444a7ceff734d7336a6334ab4c8246db0e8d17c',
                      'delimiter_free': True},
 'phase3-continue-11': {'depends': ('kill-signal-journal', 'kill-executor-abort'),
                        'bytes': 9864,
                        'chars': 9864,
                        'sha256': '712fbd78a20e693d124f2fca6922e3b9c8cd24acf42cb6a574dd145bf58a402b',
                        'delimiter_free': True},
 'kill-executor-abort': {'depends': ('phase3-continue-10', 'kill-signal-journal'),
                         'bytes': 9289,
                         'chars': 9289,
                         'sha256': '2153388f69cce3a913608b57f518758df6d7b54d39bc6b913d0fdde9f54335cd',
                         'delimiter_free': True},
 'kill-signal-journal': {'depends': ('phase3-continue-10',),
                         'bytes': 9183,
                         'chars': 9183,
                         'sha256': '1ccd48c5ca52b3f033998fda2e72e931c1a792590c247033fe8688c2c2d566e4',
                         'delimiter_free': True},
 'phase3-continue-10': {'depends': ('admission-holds-activation',),
                        'bytes': 30449,
                        'chars': 30449,
                        'sha256': '6f58f7e41fb1e5a75e19a77819b346ace303cf76d44ddc5672c5b80d9b776f6b',
                        'delimiter_free': True},
 'admission-holds-activation': {'depends': ('phase3-continue-09', 'pause-resume-activation'),
                                'bytes': 26777,
                                'chars': 26777,
                                'sha256': '02e748d2555a288415152506dc760f5498205c414d52d90cf6b135230081b662',
                                'delimiter_free': True},
 'pause-resume-activation': {'depends': ('phase3-continue-08', 'dispatch-pause-boundary'),
                             'bytes': 14943,
                             'chars': 14943,
                             'sha256': 'ff2b2e01f01a564096debfc606d980d494a36939157a3b5458111e4337eb3991',
                             'delimiter_free': True},
 'dispatch-pause-boundary': {'depends': ('phase3-continue-08',),
                             'bytes': 9337,
                             'chars': 9337,
                             'sha256': '1eb19034973e4f595a53dd26702ecc4e05d67acbcb850475cf9637fca2d33d35',
                             'delimiter_free': True},
 'phase3-continue-08': {'depends': ('background-consumers', 'control-inbox'),
                        'bytes': 30488,
                        'chars': 30488,
                        'sha256': '5bead42e85315dff2ccd7dce27984ee515e6f4e89edddb5839d75c2af4a5aae2',
                        'delimiter_free': True},
 'control-inbox': {'depends': ('phase3-continue-07', 'background-consumers'),
                   'bytes': 11592,
                   'chars': 11592,
                   'sha256': '9bbf6575aa0af3f191c16d513e483839eb7ce8de0e593ff72a7ba5fc2133371f',
                   'delimiter_free': True},
 'background-consumers': {'depends': ('phase3-continue-07',),
                          'bytes': 8144,
                          'chars': 8144,
                          'sha256': 'd0c5bb1fd2276b830167259d8d286c13d567033b0bd50e5f9c7edaa4c9349598',
                          'delimiter_free': True},
 'phase3-continue-07': {'depends': ('merge-queue-activation', 'rework-activation'),
                        'bytes': 23469,
                        'chars': 23469,
                        'sha256': '9dbdc707fea180085c962fcecfdd01c681e5e2ca23b3a5d26c31e6664ba87220',
                        'delimiter_free': True},
 'rework-activation': {'depends': ('phase3-continue-06', 'merge-queue-activation'),
                       'bytes': 23217,
                       'chars': 23217,
                       'sha256': 'b0bf42b6742bb951a2a64e8acc3faa43d8d4d973768179159c7d1fe9d7fd24d9',
                       'delimiter_free': True},
 'merge-queue-activation': {'depends': ('phase3-continue-06',),
                            'bytes': 10083,
                            'chars': 10083,
                            'sha256': 'fd9255cdfd9b76209231a5d08cb8bf517425b309355d58782dc128e75224d340',
                            'delimiter_free': True},
 'phase3-continue-06': {'depends': ('scheduler-activation',),
                        'bytes': 10878,
                        'chars': 10878,
                        'sha256': 'a90fc50c6ac254d905fb194baa4c16c9e4fdae41fc625053aa49679e17b2b7a7',
                        'delimiter_free': True},
 'scheduler-activation': {'depends': ('phase3-continue-05',),
                          'bytes': 15962,
                          'chars': 15962,
                          'sha256': '049ad1ca4b074c6bcb2479eec4c279f60179d10c85dbd7f7a36c7a613ed1e6d1',
                          'delimiter_free': True},
 'phase3-continue-05': {'depends': ('dispatch-admission-boundary', 'dispatch-config-snapshot'),
                        'bytes': 10872,
                        'chars': 10872,
                        'sha256': '3bd472c4c33f58e2ed5913ac7dd6f9865810312acb231bbde5b4de2a24de0802',
                        'delimiter_free': True},
 'dispatch-config-snapshot': {'depends': ('phase3-continue-04', 'dispatch-admission-boundary'),
                              'bytes': 7986,
                              'chars': 7986,
                              'sha256': '13fcd38bc3978678a9ae32fbcc470697857b835ee4e984e48182bb7bc60e2dcc',
                              'delimiter_free': True},
 'dispatch-admission-boundary': {'depends': ('phase3-continue-04',),
                                 'bytes': 6355,
                                 'chars': 6355,
                                 'sha256': 'ca974d865ab396785cbdaf1846a9f1a8bdf73f9a577c892a437c496416162124',
                                 'delimiter_free': True},
 'phase3-continue-04': {'depends': ('thresh-runtime',),
                        'bytes': 9534,
                        'chars': 9534,
                        'sha256': '0aaab8c573cbe947df4e450b4067d23d5d5f2ba1399cc33067d78afeeb60037d',
                        'delimiter_free': True},
 'thresh-runtime': {'depends': ('phase3-continue-03',),
                    'bytes': 15713,
                    'chars': 15713,
                    'sha256': 'b2cee5d00286a1cc523b4073136337d526c73c3561a84856c43a8389c8d3cff9',
                    'delimiter_free': True},
 'phase3-continue-03': {'depends': ('rework-stage',),
                        'bytes': 6984,
                        'chars': 6984,
                        'sha256': '4c04149a3dac65a68d091f62581a6358cd5fafa3e649abda45d7d7c3f8b96828',
                        'delimiter_free': True},
 'rework-stage': {'depends': ('phase3-continue-02',),
                  'bytes': 14014,
                  'chars': 14014,
                  'sha256': 'f69bb5993da032f20e4fd774b02bc47d3420d768feda5950dbb6a85add525d33',
                  'delimiter_free': True},
 'phase3-continue-02': {'depends': ('merge-queue',),
                        'bytes': 6377,
                        'chars': 6377,
                        'sha256': '5405be614b6d2b76702b8463963db6f8cca7d9dc843cd09a9b1e77a30c56fc4a',
                        'delimiter_free': True},
 'merge-queue': {'depends': ('phase3-continue',),
                 'bytes': 21086,
                 'chars': 21086,
                 'sha256': '87e6cb2dfdcc7405b71b5ca96c90e91a04c2bd67cb9f4ba64343cecc3d8020f5',
                 'delimiter_free': True},
 'phase3-continue': {'depends': ('daemon-scheduler', 'seed-successor-proof'),
                     'bytes': 5697,
                     'chars': 5697,
                     'sha256': 'ffd3c60044dd9aa9d089ecb7941b87fc3d2998b3dcf0f11fa43115f2a56b9972',
                     'delimiter_free': True},
 'seed-successor-proof': {'depends': ('phase3-core',),
                          'bytes': 4883,
                          'chars': 4883,
                          'sha256': '133787868f01375de9ff6b01467f89a3ab9af9986e656f522c4c257a8a7e4d02',
                          'delimiter_free': True},
 'phase3-core': {'depends': ('phase2-exit',),
                 'bytes': 4492,
                 'chars': 4492,
                 'sha256': '173c0bc2e92723fc9f13abd1223b5ee4cfe87af64c5dd9975c4189128c42ceae',
                 'delimiter_free': True},
 'phase2-exit': {'depends': ('shakeout-providers', 'diagnosis-eval-run'),
                 'bytes': 7133,
                 'chars': 7133,
                 'sha256': 'e47fec2d6f64b8b54175c3d3b9f01ed601a63a1ddd7fc244459912fe7d7e9674',
                 'delimiter_free': True},
 'diagnosis-eval-run': {'depends': ('diagnosis-eval-harness',),
                        'bytes': 3395,
                        'chars': 3395,
                        'sha256': 'fc38c74c9b0ab3154ce65bb10d6628455b90b11c2a186fd976d177fd9ed46a98',
                        'delimiter_free': True},
 'diagnosis-eval-harness': {'depends': ('spine-diagnosis',),
                            'bytes': 9267,
                            'chars': 9267,
                            'sha256': '3ee1aef02091c5974bc84a34832b4c63a5ccd05ae29aecc5c2d0a16b108c81cc',
                            'delimiter_free': True},
 'spine-diagnosis': {'depends': ('spine-caps', 'spine-harvest', 'spine-harvest-orphans'),
                     'bytes': 13604,
                     'chars': 13604,
                     'sha256': '1d3acbb296a5726c965ed17c87f207725ff3b97153f14915a6d7d41a7aed5c58',
                     'delimiter_free': True},
 'spine-harvest-orphans': {'depends': ('spine-harvest',),
                           'bytes': 4905,
                           'chars': 4905,
                           'sha256': '9601533f197b1a529b65bd32ac1286fbd2ea709d1e2f9db2e2095714448a5b55',
                           'delimiter_free': True},
 'spine-harvest': {'depends': ('spine-caps',),
                   'bytes': 8191,
                   'chars': 8191,
                   'sha256': '9be7f182bb69569da58849c1e22491129bc8056498fde46e6cdefcb30888cadf',
                   'delimiter_free': True},
 'spine-caps': {'depends': ('plan-contract-section-render',),
                'bytes': 6957,
                'chars': 6957,
                'sha256': 'e24e39ab7516db1d16c3f34ca54a5f15bbf540879601122551fea4cf13c9932a',
                'delimiter_free': True},
 'plan-contract-section-render': {'depends': (),
                                  'bytes': 3451,
                                  'chars': 3451,
                                  'sha256': '510b77374f6ac75110893922b1160d10fd2096fa0c61cc825ddc589c08256ff0',
                                  'delimiter_free': True},
 'shakeout-providers': {'depends': ('shakeout-merge',),
                        'bytes': 5187,
                        'chars': 5186,
                        'sha256': '6ab1c8635769f579b139102b97c69d4e1ffca194a3179677ecd44da0dc66f0a8',
                        'delimiter_free': True},
 'shakeout-merge': {'depends': ('shakeout-recovery',),
                    'bytes': 3039,
                    'chars': 3039,
                    'sha256': '5a8ca348dc7e7a9702f5a3894ab04b0a51b25eb0c77f76d0c7d5e23cbd02444d',
                    'delimiter_free': True},
 'shakeout-recovery': {'depends': ('shakeout-drain',),
                       'bytes': 3171,
                       'chars': 3171,
                       'sha256': '55fdaf23ea50d59ceafcc45546a56c1e2c1e95e86586ffda4f2b51dedb252795',
                       'delimiter_free': True},
 'shakeout-drain': {'depends': ('shakeout-runner',),
                    'bytes': 3425,
                    'chars': 3425,
                    'sha256': 'ab68a6c1f029da30c129bc773f020c587898f2dfed3b0f39d04c1e58b7c60a07',
                    'delimiter_free': True},
 'shakeout-runner': {'depends': ('shakeout-driver',),
                     'bytes': 3583,
                     'chars': 3583,
                     'sha256': '95b5370cf4734300410bbbb586bc6d3ff985a9084ed1ab5857603bf04df1d0ff',
                     'delimiter_free': True},
 'shakeout-driver': {'depends': ('shakeout-stages',),
                     'bytes': 3849,
                     'chars': 3849,
                     'sha256': 'b76f77a52a2c6978c28ab5f07f237b329c7d4c868c5a4d1088a06eccb2e0b8c6',
                     'delimiter_free': True},
 'shakeout-stages': {'depends': ('shakeout-report-lane', 'verification-base-attribution'),
                     'bytes': 4557,
                     'chars': 4557,
                     'sha256': 'e636b4f409151a3fc0475a35fa334d504c9520f37e7f64e09d21be6c92c1e0b2',
                     'delimiter_free': True},
 'verification-base-attribution': {'depends': ('box-triage',),
                                   'bytes': 5758,
                                   'chars': 5758,
                                   'sha256': 'fc05dc2c40c27d86b677683f29a3712289f86f737c12e214541f18809e906b4b',
                                   'delimiter_free': True},
 'box-triage': {'depends': ('box-start-policy', 'suggestion-box'),
                'bytes': 10256,
                'chars': 10256,
                'sha256': '8185923784d6a67b059d942f0a94cc9571e0845eb7bbe16277ec11e1e60cfd53',
                'delimiter_free': True},
 'suggestion-box': {'depends': ('spine-diagnosis',),
                    'bytes': 10331,
                    'chars': 10331,
                    'sha256': 'cbebe08283b3039db3a7f57f4e96991f03996113e9161a767885028724ea8258',
                    'delimiter_free': True},
 'box-start-policy': {'depends': ('escalation-ladder', 'suggestion-box'),
                      'bytes': 5687,
                      'chars': 5687,
                      'sha256': '72004d98a6bc5f16bda3b901346abb30161c2b18e0aae5b261f252aee77212ba',
                      'delimiter_free': True},
 'escalation-ladder': {'depends': ('reject-queue-verbs',),
                       'bytes': 8228,
                       'chars': 8228,
                       'sha256': 'a60e373100f40305027b7c86279d189c15608af4f32436003b61aae7a8f877d0',
                       'delimiter_free': True},
 'reject-queue-verbs': {'depends': ('second-problems-filing', 'suggestion-box'),
                        'bytes': 10998,
                        'chars': 10998,
                        'sha256': '9b84214abf7cb2fe2b811275f670ff7441a9819e0cc385e9cb5694299c0cd3f7',
                        'delimiter_free': True},
 'second-problems-filing': {'depends': ('suggestion-box',),
                            'bytes': 5617,
                            'chars': 5617,
                            'sha256': '915424d0f0cf70a5f1ba0e695ee40cda7fe8a8a67922dbdf490537a46c45c66f',
                            'delimiter_free': True},
 'shakeout-report-lane': {'depends': ('invariant-auditor',),
                          'bytes': 8079,
                          'chars': 8079,
                          'sha256': 'dc79dc13e377d1c6cf2eaadd3c60dcd28677243cf17fa99da7b75ce32a0361b7',
                          'delimiter_free': True},
 'invariant-auditor': {'depends': ('requisition-seed-path',),
                       'bytes': 4247,
                       'chars': 4247,
                       'sha256': '5023d149dd5b184faf476cc62bfcbe57dfaccd20e425a45f85efaa92ded3e85e',
                       'delimiter_free': True},
 'requisition-seed-path': {'depends': ('requisition-author-path',),
                           'bytes': 6484,
                           'chars': 6484,
                           'sha256': 'a1fde7e859106d000d419e9818ef55777d9d2ac202f8df6a7079de7b8326040f',
                           'delimiter_free': True},
 'requisition-author-path': {'depends': ('requisition-review', 'author-stage'),
                             'bytes': 5057,
                             'chars': 5057,
                             'sha256': 'edcaf039a0381c9fdc4dcbaa7a9a243fe785323eea74b790b2437b6175b7d3a7',
                             'delimiter_free': True},
 'author-stage': {'depends': ('box-triage', 'box-start-policy'),
                  'bytes': 9292,
                  'chars': 9292,
                  'sha256': '17e7227a47e6c55879c7318be4480c396677c4d1d4e6a44597ea33e5e2b6d2f2',
                  'delimiter_free': True},
 'requisition-review': {'depends': ('author-stage',),
                        'bytes': 7571,
                        'chars': 7571,
                        'sha256': 'bb1c51e9a2de70187601fabbcd747079ac4f5585719a378b1389ca7e03f1fe3a',
                        'delimiter_free': True},
 'daemon-scheduler': {'depends': ('phase3-core',),
                      'bytes': 4624,
                      'chars': 4624,
                      'sha256': '8bd893d70b5a4bcb02e8ee83c914de0b0dc8d7a56cd6e5698de1d485609ed311',
                      'delimiter_free': True},
 'phase3-continue-09': {'depends': ('dispatch-pause-boundary', 'pause-resume-activation'),
                        'bytes': 37453,
                        'chars': 37453,
                        'sha256': 'c6435ebcaba0cf6b090cf1acbca3604c7f795c84a2030bca6edbb21599eff8aa',
                        'delimiter_free': True},
 'provider-cooldown-failover': {'depends': ('phase4-continue-02',),
                                'bytes': 8343,
                                'chars': 8343,
                                'sha256': 'e22667b38b094b96f20ff69add2e729db495bfa4ca2b8900b1ee37eeb918d9b4',
                                'delimiter_free': True},
 'phase4-continue-02': {'depends': ('watchdog-detector', 'watchdog-activation'),
                        'bytes': 4976,
                        'chars': 4976,
                        'sha256': 'b15687e4f69040ff04d1f72d44ea9dc1d2b5e0c438e8fbf78ec1ae309d450a53',
                        'delimiter_free': True},
 'watchdog-activation': {'depends': ('phase4-continue', 'watchdog-detector'),
                         'bytes': 7459,
                         'chars': 7459,
                         'sha256': '3a6ddbcf099ab17db2bcf64854dc37b8f2880003c8949ef9211d5a4525fa7b29',
                         'delimiter_free': True},
 'watchdog-detector': {'depends': ('phase4-continue',),
                       'bytes': 3857,
                       'chars': 3857,
                       'sha256': '5cab85e1fe09aca3f846cd57177fef951b71a7426aa3b5bc57cef3b788a88f15',
                       'delimiter_free': True},
 'phase4-continue': {'depends': ('watchdog-event-stream', 'notify-transport'),
                     'bytes': 5826,
                     'chars': 5826,
                     'sha256': '3a9aea38aab905a1636a9abdcf3716acdfc5593491910fb3cd299a39dd9c4c5e',
                     'delimiter_free': True},
 'notify-transport': {'depends': ('phase3-exit', 'watchdog-event-stream'),
                      'bytes': 4780,
                      'chars': 4780,
                      'sha256': '92c780f024a55fd4dad809741c17c06ec5dd47243fa37716449018aed184fe08',
                      'delimiter_free': True},
 'watchdog-event-stream': {'depends': ('phase3-exit',),
                           'bytes': 3782,
                           'chars': 3782,
                           'sha256': '0e120f3267fb3db135372d954845b57b2ce0a827a409b7eb20dc6b17e4b68276',
                           'delimiter_free': True},
 'phase3-exit': {'depends': ('phase3-continue-27',),
                 'bytes': 7933,
                 'chars': 7933,
                 'sha256': '1917f4311eea349e84aca306a004be994cafe882a3bda3b560f3549035a54081',
                 'delimiter_free': True},
 'phase3-continue-27': {'depends': ('soak-run',),
                        'bytes': 7300,
                        'chars': 7300,
                        'sha256': 'c58db75d14da778d2bc909933105e0f2300eea2829bc92019fba9213ebe92323',
                        'delimiter_free': True},
 'soak-run': {'depends': ('phase3-continue-26',),
              'bytes': 4980,
              'chars': 4980,
              'sha256': 'f13916bfc85b61863ac0fce66b4c74158948dc8731f6143f01795d3f48355e65',
              'delimiter_free': True},
 'phase3-continue-26': {'depends': ('daemon-soak-runner',),
                        'bytes': 7923,
                        'chars': 7923,
                        'sha256': 'c698083af1b7a1d2fc05a568256ac1ada3289e136bd82cca0bff8fb19f027680',
                        'delimiter_free': True},
 'daemon-soak-runner': {'depends': ('phase3-continue-25',),
                        'bytes': 6168,
                        'chars': 6168,
                        'sha256': '7c499347f42c9e97a0ebac04a5903c59c6e615a0bcf09954e2a4fdb3cc7f03b3',
                        'delimiter_free': True},
 'phase3-continue-25': {'depends': ('daemon-soak',),
                        'bytes': 9279,
                        'chars': 9279,
                        'sha256': 'c3c2f8d734a8127b706078c78071ff3060b0a247d933dc01cadb6ac089ccea09',
                        'delimiter_free': True},
 'daemon-soak': {'depends': ('phase3-continue-24',),
                 'bytes': 4892,
                 'chars': 4892,
                 'sha256': 'ddb43718964c94e9767019c97256180c0d541045e8c4355ba457d1b89b3f9d39',
                 'delimiter_free': True},
 'phase3-continue-24': {'depends': ('outbox-only-admission',),
                        'bytes': 8314,
                        'chars': 8314,
                        'sha256': 'c9da258e29e750e7ca60bb3509abfa39294c7f4f702999e3d7d5c9019da90313',
                        'delimiter_free': True},
 'reliability-battery': {'depends': ('phase4-continue-03',),
                         'bytes': 6341,
                         'chars': 6341,
                         'sha256': 'cdb5b2924bcf71edc5590f7a26c1b224a3c5e6c2bd4755d89f7ca6d9c9badf76',
                         'delimiter_free': True},
 'phase4-continue-03': {'depends': ('provider-cooldown-failover',),
                        'bytes': 5083,
                        'chars': 5083,
                        'sha256': 'c7cbd5d4c84b2852ab752e20a45bc12cadeb1008ebb6f6f5fbb4934d12471a59',
                        'delimiter_free': True},
 'phase4-continue-04': {'depends': ('reliability-battery',),
                        'bytes': 6067,
                        'chars': 6067,
                        'sha256': 'b17405c20ffa10ed2044d8308340f06681d296abc5f0fc736f01a28704ddbe23',
                        'delimiter_free': True},
 'phase5-continue': {'depends': ('retro-drain-invoker',),
                     'bytes': 6380,
                     'chars': 6380,
                     'sha256': '71f775f6b99540eb269460cc090ca711ced2d87055cdc829102e5af8d4fd1c7d',
                     'delimiter_free': True},
 'phase5-continue-03': {'depends': ('scorecard-reporting',),
                        'bytes': 6665,
                        'chars': 6665,
                        'sha256': '728edc3dd972a9031f2f35ba6a1b89990c369393883cc6a33eb127cc6844c970',
                        'delimiter_free': True},
 'scorecard-reporting': {'depends': ('phase5-continue-02',),
                         'bytes': 4404,
                         'chars': 4404,
                         'sha256': '8737b430dac8a64651215e0dc757cbfafb6c2e4d619d3a8e58b80da26c71e068',
                         'delimiter_free': True},
 'phase5-continue-02': {'depends': ('retro-box-activation',),
                        'bytes': 5174,
                        'chars': 5174,
                        'sha256': '830e969ccd63727f40b802f0e54b22500810fe0d08b174ead23bbc8e55384214',
                        'delimiter_free': True},
 'status-projection': {'depends': ('phase5-continue-03',
                                   'scorecard-reporting',
                                   'retro-box-activation'),
                       'bytes': 4606,
                       'chars': 4606,
                       'sha256': 'f386d9267675b40faf72068e02f38ead4bcaa8f580f632cbf93450bf1c7be77d',
                       'delimiter_free': True},
 'phase6-continue': {'depends': ('core-renderer', 'core-drift-classifier'),
                     'bytes': 7085,
                     'chars': 7085,
                     'sha256': 'dba52460c45a2c4eea7c2369eb3b9fd0120ac70aa9b8498690bb8780b0c638ca',
                     'delimiter_free': True},
 'host-contract-doc': {'depends': ('phase6-continue-02', 'migrate-config'),
                       'bytes': 4743,
                       'chars': 4743,
                       'sha256': 'f0fecbd273032643f5299a3468511b138983e90f060a8e42939c0fe2315e6610',
                       'delimiter_free': True},
 'migrate-config': {'depends': ('phase6-continue', 'core-renderer'),
                    'bytes': 3832,
                    'chars': 3832,
                    'sha256': '88f806b1f2a1537ffbc21814e058fe28c261468956e824cda2efd5b123b281ec',
                    'delimiter_free': True},
 'phase6-continue-02': {'depends': ('core-drift-activation', 'migrate-config'),
                        'bytes': 6370,
                        'chars': 6370,
                        'sha256': '92cf2898668d9bd3c47d52250b152d314aa23d55c65c82d084ea417536bfe7c1',
                        'delimiter_free': True},
 'supervised-merge-hold': {'depends': ('phase6-continue-05', 'escape-column'),
                           'bytes': 7336,
                           'chars': 7336,
                           'sha256': '051832e19b51072ae70d6e23f749975eb3286deaa5229384a572b9b10bb597ca',
                           'delimiter_free': True},
 'escape-column': {'depends': ('phase6-continue-04', 'bug-gate-grammar', 'report-inbox-triage'),
                   'bytes': 5142,
                   'chars': 5142,
                   'sha256': 'eca4ac54e7d0edb3ec455b4a256730a1d9fe86b9cb6550091b125589a6095751',
                   'delimiter_free': True},
 'report-inbox-triage': {'depends': ('phase6-continue-03', 'bug-gate-grammar'),
                         'bytes': 4688,
                         'chars': 4688,
                         'sha256': '89ff882be844b8bdb397b197cefe68ca0aaa080a6e618e489d29eee34b9f7fb8',
                         'delimiter_free': True},
 'bug-gate-grammar': {'depends': ('phase6-continue-03', 'fixture-host-scaffold'),
                      'bytes': 5109,
                      'chars': 5109,
                      'sha256': '4e78c895341c45c729a15a30acaf32750dc958ba8e92c247b30693feac0afbb3',
                      'delimiter_free': True},
 'phase6-continue-03': {'depends': ('host-contract-doc', 'fixture-host-scaffold'),
                        'bytes': 5655,
                        'chars': 5655,
                        'sha256': '6b908d97ee5e72b56235e31d9a32f6409504fa19e0ab0bbb3911abe165765c77',
                        'delimiter_free': True},
 'phase6-continue-04': {'depends': ('bug-gate-grammar', 'report-inbox-triage'),
                        'bytes': 5480,
                        'chars': 5480,
                        'sha256': '7049c89a5f82dea334cc240e474456ecc8a752cc9be519072d13d299304c13f0',
                        'delimiter_free': True},
 'phase6-continue-05': {'depends': ('escape-column',),
                        'bytes': 5730,
                        'chars': 5730,
                        'sha256': 'e404b8957ca5473c0d36e25f414ac0b76f73958f98534b546d77a8e6d1bf2eb1',
                        'delimiter_free': True},
 'phase6-continue-06': {'depends': ('supervised-merge-hold',),
                        'bytes': 5838,
                        'chars': 5838,
                        'sha256': '368f836b39854e7df82a40265d5f278fa6d30990961e9712e7174a5aad836a2f',
                        'delimiter_free': True},
 'phase6-continue-07': {'depends': ('go-grade-machinery', 'go-grade-run'),
                        'bytes': 5420,
                        'chars': 5420,
                        'sha256': '03ec18d3896a7e28bddd9e3c5aeda6cc69cc9c1ed0dd9f8a18f925a2e702cc57',
                        'delimiter_free': True},
 'phase6-continue-08': {'depends': ('exit-receipt-machinery',),
                        'bytes': 6218,
                        'chars': 6218,
                        'sha256': '1c0b489e43fb84f35953cb85c6b3ac170752f791b76ab7af43b2124d703121e8',
                        'delimiter_free': True}}

SQUASH_TRAILERS = {'core-renderer': {'commit': '92c3358473116aa4d92be735424aabe8840b518c',
                   'reviewed_sha': 'cb922eb80ef28ab78f227c62065417fe696468b5'},
 'core-drift-classifier': {'commit': '337f8e9d5d121c3742709de7a00f93b4f4084c72',
                           'reviewed_sha': '79040ebcdaec6d7384b178f5c13b5145bde4d75f'},
 'core-drift-activation': {'commit': '40006b5ce9a61a0a8212753614420e553df9ea14',
                           'reviewed_sha': '88cf22990c0c12c131998d86684a64442388227a'},
 'migrate-config': {'commit': 'e60f8023d59d87a4413c1866520e81aa699e0501',
                    'reviewed_sha': '6ced67389e98278d0fc968314aadebf57ece81f8'},
 'host-contract-doc': {'commit': '860c7c4d52c0e15d3936da9ab48f7e847bc6c1cc',
                       'reviewed_sha': '6f6962717fde40a0dff5276f9e14c1575ae5f07f'},
 'fixture-host-scaffold': {'commit': 'a0924ff504d441f0229dc7db91d49826fed62980',
                           'reviewed_sha': 'b00d9ad7ebb7356176efeeea1658906590cf52dc'},
 'bug-gate-grammar': {'commit': '083bbea95b89eab82fce2d305f592a4c771cab42',
                      'reviewed_sha': '5c2608bb9214d5c87d8db35c49b9f8bb9a3dab10'},
 'report-inbox-triage': {'commit': '9f6a2be7dc45397289b7361ea797c96fc3733056',
                         'reviewed_sha': '5a7836507812df5a6eee3fbdee17d239db700a39'},
 'escape-column': {'commit': 'e47704afb5f10aadc4cbb53542db8ff47c6bd871',
                   'reviewed_sha': '64e448e9e5e6350d4df1f1b6ed3d8067e187463a'},
 'supervised-merge-hold': {'commit': '7139347a388ac756ffef00450b9adf12532e3e1d',
                           'reviewed_sha': 'b129442b708ca9e7166b40c59aeaaa5b8f517333'},
 'go-grade-machinery': {'commit': 'ed601ada3ab06a75e845008d0d8ff71a3bce6cf3',
                        'reviewed_sha': '274c6ad1119f5178b3308766c53418ff6bd8f86a'},
 'exit-receipt-machinery': {'commit': '76c60e7b746b1e2d061bdd8e552c528171a14610',
                            'reviewed_sha': '51388c7e10ded04124928aacf13e00e68ee919a7'}}

BASELINE_LIFT = 'aa19fe95ae85dc4a0399f6275027d52f707d9524'

PRIOR_PAYLOADS = ('core-renderer',
 'core-drift-classifier',
 'core-drift-activation',
 'migrate-config',
 'host-contract-doc',
 'fixture-host-scaffold',
 'bug-gate-grammar',
 'report-inbox-triage',
 'escape-column',
 'supervised-merge-hold',
 'go-grade-machinery',
 'go-grade-run',
 'exit-receipt-machinery')

IMPLEMENT_SPEC = {'bytes': 5306,
 'chars': 5306,
 'sha256': 'f5d3ba603570a56f661a24d7a52d7e4543c0d003a82e36d664f5ef73f3599ddb',
 'delimiter_free': False}

IMPLEMENT_BODY_CHARS = 5185

RENDER_OVERHEAD = 66

ACTUAL_RENDER = 152492

RENDER_BOUND_CHARS = 400000

REQ_RENDER_HEADROOM = 0.75

MEASURED_RENDER_TIER = 'max'

MEASURED_RENDER_EFFORT = 'max'

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

MACHINERY_OBLIGATIONS = (('tests/test_host_loop.py', 'test_exit_receipt_entry_unit'),
 ('tests/test_host_loop.py', 'test_host_loop_closed_schema'),
 ('tests/test_host_loop.py', 'test_host_loop_drives_supervised_fixture_serve'),
 ('tests/test_host_loop.py', 'test_host_loop_report_regression_and_escape'),
 ('tests/test_host_loop.py', 'test_host_loop_requires_member_auditor_green'),
 ('tests/test_host_loop.py', 'test_exit_receipt_closed_schema_and_baseline_identity'),
 ('tests/test_host_loop.py', 'test_exit_receipt_regenerates_from_committed_bytes'),
 ('tests/test_stages.py', 'test_host_loop_and_receipt_registered_checks_lift'),
 ('tests/test_gates.py', 'test_host_loop_regression_uses_real_bug_gate'))

HARNESS_COMMAND = ('uv',
 'run',
 'python',
 '-m',
 'eval.host_loop',
 '--out',
 'tickets/phase6-exit/host-loop-report.json',
 '--receipt',
 'tickets/phase6-exit/exit-receipt.json',
 '--baseline',
 'tickets/go-grade-run/review-baseline-report.json')

AUTHORING_TRACKED_SEEDS = ()

TERMINAL_ENTRY_ID = None

SUCCESSOR = None

TERMINAL_SEEDS = ()

COPY_VIOLATIONS = ()


# The scan found no changed public seam, activation or contradicted assertion.
# eval.host_loop.regenerate/write_receipt remain callers of existing schema constructors;
# chupa.stages.KNOWN_ARTIFACTS already registers both names. All production stays unchanged.
CLOSURE_DECISIONS = (
    "eval/host_loop.py::regenerate consumes existing HostLoopReport and ReviewBaselineReport.",
    "eval/host_loop.py::write_receipt uses the existing ExitReceipt canonical writer.",
    "chupa/stages.py::KNOWN_ARTIFACTS already registers HOST_LOOP_REPORT and EXIT_RECEIPT.",
    "No signature, constructor, composition root, public operation or dormant assertion changes.",
)
EXIT_READS = {
    "machine_ticket_merge": ("exit-receipt-machinery", "phase6-exit",
                            "tickets/phase6-exit/host-loop-report.json"),
    "report_to_regression_bug_loop": ("exit-receipt-machinery", "phase6-exit",
                                     "tickets/phase6-exit/host-loop-report.json"),
    "escape_attribution": ("exit-receipt-machinery", "phase6-exit",
                          "tickets/phase6-exit/host-loop-report.json"),
    "go_grade_report": ("go-grade-machinery", "go-grade-run",
                       "tickets/go-grade-run/review-baseline-report.json"),
}
DELIVERY = {
    "seed": "tickets/phase6-exit/ticket.md",
    "commit_only": "tests/test_seeded_phase6_08.py",
    "approval_record": "tickets/phase6-continue-08/checks.json",
    "review": "requisition_review",
    "lift": "ticket-plane",
    "retry": "retain approved bytes while ticket_sha matches; author only snagged seeds",
}


def _ticket():
    return validate_ticket(BATCH[0], (ROOT / ticket_path(BATCH[0])).read_text(), ROOT)


def render_chars():
    return (IMPLEMENT_BODY_CHARS + TICKET_SIZE["chars"] + RENDER_OVERHEAD
            + sum(PLAN_SIZES[u]["chars"] for u in PLAN_IDS)
            + sum(FILE_SIZES[p]["chars"] for p in CONTEXT))


def test_phase6_08_exact_admission():
    t = _ticket()
    assert POSITION == 8
    assert BATCH == REGISTRY_ADMISSIONS[POSITION] == ("phase6-exit",)
    assert UNSEEDED_SUFFIX == REGISTRY_ADMISSIONS[POSITION:] == (BATCH,)
    assert len(BATCH) == 1 <= MAX_SEEDS_PER_ADMISSION == 3
    assert REGISTRY_ROW["exit"] is True
    assert tuple(REGISTRY_ROW["depends"]) == ("exit-receipt-machinery",)
    assert t.depends == EDGES == ("phase6-continue-08", "exit-receipt-machinery")
    assert (t.frontmatter.source, t.frontmatter.state) == ("seed", "confirmed")
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("high", "high")
    assert t.plan_contract == PLAN_IDS == ("19.L", "19.I", "19.P6", *REQUIRED)
    assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES
    assert SUCCESSOR is TERMINAL_ENTRY_ID is None
    assert TERMINAL_SEEDS == ()
    scope = t.sections["Scope in / Scope out"]
    for fact in ("Position 8", "admissions[8:]", "sole terminal payload", "KNOWN-HARD",
                 "high/high", "19.L", "No successor", "no seeds", "no next phase",
                 "no GO recording", "no live journal read"):
        assert fact in scope


def test_phase6_08_entry_depth():
    assert REQUIRED == (
        "19.P6.exit-receipt-machinery", "19.P6.fixture-host-scaffold",
        "19.P6.supervised-merge-hold", "19.P6.go-grade-machinery", "19.P6.go-grade-run")
    assert set(ENTRY_DEPTH) == set(REQUIRED)
    assert "19.P6.phase6-exit" not in PLAN_IDS
    for uid, d in ENTRY_DEPTH.items():
        assert d["resolves"] == 1 and d["gap"] is None
        assert d["missing_unit_rejected"] and d["duplicate_rejected"]
        assert set(d["parts"]) == {"Owner", "Records", "Observable", "Tests"}
        assert all(n > 0 for n in d["parts"].values())
        assert set(d["missing_part_rejected"]) == set(d["parts"])
        assert all(d["missing_part_rejected"].values())
        assert d["sha256"] == PLAN_SIZES[uid]["sha256"]
    t = _ticket()
    for fact in ("required_units", "resolve_plan_contract", "entry_unit_gap", "TERMINAL",
                 "RECEIPT", "kind: spec_gap"):
        assert fact in t.sections["Scope in / Scope out"]
    assert COPY_VIOLATIONS == ()
    criteria = t.sections["Acceptance criteria"]
    for path, name in MACHINERY_OBLIGATIONS:
        assert path + "::" + name in criteria
        assert path in {arg for argv in t.verification for arg in argv}
        assert path not in t.context and path not in t.scope_fence
    for member, (machinery, producer, output) in EXIT_READS.items():
        assert member in criteria and output in criteria
        assert machinery in criteria and producer in criteria
        assert "test_phase6_exit_" + member in criteria
    assert "test_phase6_exit_transitive_dependencies" in criteria
    assert "test_phase6_exit_receipt_regeneration" in criteria
    assert t.verification[0] == HARNESS_COMMAND
    assert HARNESS_COMMAND == (
        "uv", "run", "python", "-m", "eval.host_loop",
        "--out", "tickets/phase6-exit/host-loop-report.json",
        "--receipt", "tickets/phase6-exit/exit-receipt.json",
        "--baseline", "tickets/go-grade-run/review-baseline-report.json")
    for fact in ("FIRST", "Missing files fail closed", "fresh OUTBOX", "lifted copies",
                 "no git-HEAD read", "actual embedded verdict_signal", "partial NO_GO",
                 "Leave both reports uncommitted"):
        assert fact in t.sections["Scope in / Scope out"]


def test_phase6_08_closure():
    t = _ticket()
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert FENCE_ADDITIONS == () and CLOSURE_EVIDENCE == {}
    assert t.scope_fence == tuple(REGISTRY_ROW["fence"]) == CREATED
    assert (t.context, t.on_demand) == (CONTEXT, ON_DEMAND)
    assert FENCED_EXISTING == ON_DEMAND == ()
    assert not set(CREATED) & set(CONTEXT)
    assert not set(t.scope_fence) & set(HISTORICAL_SNAPSHOTS)
    assert all(FILE_SIZES[p]["delimiter_free"] and not p.startswith("specs/") for p in CONTEXT)
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    assert all(s["files"] and s["matched_lines"] > 0 and len(s["sha256"]) == 64
               for s in CLOSURE_SCAN.values())
    assert set(HISTORICAL_SNAPSHOTS) == {
        "tests/test_seeded_phase3_core.py", "tests/test_seeded_phase6_core.py",
        *(f"tests/test_seeded_phase6_{n:02d}.py" for n in range(1, 8))}
    assert (RENDER_BOUND_CHARS, REQ_RENDER_HEADROOM) == (400_000, 0.75)
    assert (MEASURED_RENDER_TIER, MEASURED_RENDER_EFFORT) == ("max", "max")
    assert render_chars() == ACTUAL_RENDER <= RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM
    data = (ROOT / ticket_path(t.stem)).read_bytes()
    assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
        TICKET_SIZE["bytes"], TICKET_SIZE["chars"], TICKET_SIZE["sha256"])
    for record in (*PLAN_SIZES.values(), *FILE_SIZES.values(),
                   *HISTORICAL_SNAPSHOTS.values(), *COMMITTED_GRAPH.values(), IMPLEMENT_SPEC):
        assert record["bytes"] >= record["chars"] > 0 and len(record["sha256"]) == 64
    covered = set()
    pending = list(EDGES)
    while pending:
        stem = pending.pop()
        if stem in covered:
            continue
        covered.add(stem)
        pending.extend(COMMITTED_GRAPH[stem]["depends"])
    assert set(PRIOR_PAYLOADS) <= covered
    assert PRIOR_PAYLOADS == tuple(s for row in REGISTRY_ADMISSIONS[:POSITION] for s in row)
    assert set(SQUASH_TRAILERS) == set(PRIOR_PAYLOADS) - {"go-grade-run"}
    assert len(BASELINE_LIFT) == 40
    for row in SQUASH_TRAILERS.values():
        assert len(row["commit"]) == len(row["reviewed_sha"]) == 40
    assert all(s in t.sections["Acceptance criteria"] for s in PRIOR_PAYLOADS)
    assert "no-code go-grade-run" in t.sections["Acceptance criteria"]
    preserved = {p for p, _ in MACHINERY_OBLIGATIONS} | {
        "tests/test_fixture_host.py", "tests/test_bug_gate.py", "tests/test_inbox.py",
        "tests/test_triage.py", "tests/test_supervised_merge_hold.py", "tests/test_merge.py",
        "tests/test_seed_path.py", "tests/test_eval_harness.py", "tests/test_go_grade.py",
        "tests/test_plan_lint.py"}
    assert not preserved & (set(t.context) | set(t.scope_fence))
    assert preserved <= {arg for argv in t.verification for arg in argv}


@pytest.mark.parametrize("first_verdict", ["approve", "snag"])
def test_phase6_08_check_owns_seed_custody_and_retry(seed_repo, first_verdict):
    # One seed per pass. Approval survives a checks-lift failure; a snag gets re-authored.
    assert AUTHORING_TRACKED_SEEDS == ()
    assert DELIVERY["commit_only"] == "tests/test_seeded_phase6_08.py"
    seeder, seed = "phase6-continue-08", "phase6-exit"
    own, target = ticket_path(seeder), ticket_path(seed)
    setup, _ = context(seed_repo, [])
    authored = seeding_text()
    setup.fs.write(seed_repo / 'chupa/thing.py', b'ok\n')
    setup.fs.write(seed_repo / own, authored.encode())
    (seed_repo / ticket_path(STEM)).unlink()

    async def prepare():
        await setup.git.add(seed_repo, [own, ticket_path(STEM), 'chupa/thing.py'])
        await setup.git.commit(seed_repo, "terminal seeder in disposable repository")
    asyncio.run(prepare())
    ticket = validate_ticket(seeder, authored, seed_repo)
    original = seed_text(seed, tier="high")
    fixed = original.replace("holds the word ok for phase6-exit.",
                             "holds the word ok for phase6-exit, tested.")

    class SeedLLM(FakeLLM):
        async def call(self, request):
            if request.surface == "implement":
                await self.emit(request)
            return await super().call(request)

    def implement(ctx, *, retry=False):
        async def act(request):
            assert request.worktree is not None
            path = request.worktree / target
            if retry and first_verdict == "approve":
                assert "## Approved seeds (keep verbatim)" in request.rendered
                assert path.read_text() == original
                # No seed write: keep approved bytes; the single seed has no snagged sibling.
            else:
                ctx.fs.write(path, (fixed if retry else original).encode())
            ctx.fs.write(request.worktree / "chupa/thing.py", b"ok retry\n" if retry else b"ok first\n")
            await ctx.git.add(request.worktree, ["chupa/thing.py"])
            await ctx.git.commit(request.worktree, "disposable implementation")
            assert target not in await ctx.git.ls_files(request.worktree)
            with pytest.raises(GitError):
                await ctx.git.rev_parse(request.worktree, "HEAD:" + target)
            assert path.is_file()
        return act

    snag = {"code": "scope", "message": "missing exit read", "paved_road": "name the read",
            "kind": "authoring_error"}
    ctx, _ = context(seed_repo, [])
    ctx.driver.llm = SeedLLM([implement_reply(), requisition(first_verdict,
                            [snag] if first_verdict == "snag" else []), diagnosis_reply()])
    ctx.driver.llm.emit = implement(ctx)

    if first_verdict == "approve":
        original_commit = ctx.git.commit

        async def fail_checks_lift(directory, message, *, only=()):
            if message == "chupa(" + seeder + "): checks":
                raise GitError(["git", "commit"], 1, "", "injected checks-lift failure")
            await original_commit(directory, message, only=only)
        ctx.git.commit = fail_checks_lift
    assert asyncio.run(drive(ctx, ticket)) == "gate_failed"
    receipt = Invoice.model_validate_json((seed_repo / DELIVERY["approval_record"]).read_text())
    assert [(s.stem, s.verdict) for s in receipt.seeds] == [(seed, first_verdict)]
    reviews = [r for r in ctx.driver.llm.requests if r.surface == "requisition_review"]
    assert len(reviews) == 1 and original.strip() in reviews[0].rendered
    assert not (seed_repo / target).exists()
    assert not any((e.key or "").endswith("/seeds") for e in ctx.driver.journal.read())

    retry, _ = context(seed_repo, [])
    script = [implement_reply()]
    if first_verdict == "snag":
        script.append(requisition("approve"))
    script.append(verdict())
    retry.driver.llm = SeedLLM(script)
    retry.driver.llm.emit = implement(retry, retry=True)
    assert asyncio.run(drive(retry, ticket)) == "merged"
    reviews = [r for r in retry.driver.llm.requests if r.surface == "requisition_review"]
    assert len(reviews) == (1 if first_verdict == "snag" else 0)
    if reviews:
        assert "Verdict: snag" in reviews[0].rendered and "missing exit read" in reviews[0].rendered
        assert "tested." in reviews[0].rendered
    assert (seed_repo / target).read_text() == (fixed if first_verdict == "snag" else original)

    async def custody():
        events = retry.driver.journal.read()
        lifts = [e for e in events if e.type == EventType.EFFECT_COMPLETION
                 and e.ticket == seeder and (e.key or "").endswith("/seeds")]
        assert len(lifts) == 1
        lift = lifts[0]
        check = next(e for e in reversed(events[:events.index(lift)])
                     if e.type == EventType.EFFECT_COMPLETION and e.ticket == seeder
                     and (e.key or "").endswith("/checks"))
        data = await retry.git._run(seed_repo, "show",
            check.body["result"]["commit"] + ":" + DELIVERY["approval_record"])
        invoice = Invoice.model_validate_json(data)
        assert invoice.passed
        assert [(s.stem, s.verdict) for s in invoice.seeds] == [(seed, "approve")]
        assert invoice.seeds[0].ticket_sha == await retry.git.rev_parse(seed_repo, "HEAD:" + target)
        changed = await retry.git._run(seed_repo, "show", "--format=", "--name-only",
                                      lift.body["result"]["commit"])
        assert changed.splitlines() == [target]
        subjects = (await retry.git._run(seed_repo, "log", "--format=%s")).splitlines()
        assert subjects.count("chupa(" + seeder + "): seeds") == 1
        intake = [e for e in events if e.type == EventType.SIGNAL
                  and e.body.get("signal") == "ticket_intake"
                  and e.body.get("seeded_by") == seeder]
        assert [e.ticket for e in intake] == [seed]
        assert events.index(check) < events.index(lift) < events.index(intake[0])
    asyncio.run(custody())
