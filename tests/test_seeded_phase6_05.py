"""Phase 6 admission 5: supervised hold and the GO-grade continuation.

Contract depth, closure, hashes and render operands are authoring-time snapshots.
Only seed identity reads the tree; custody runs production Check in a disposable repo.
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

AUTHORING_HEAD = 'cf01798a7c8d50d8225e5bfbce6c79cf166ce0de'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('supervised-merge-hold', 'phase6-continue-06')

PAYLOADS = ('supervised-merge-hold',)

POSITION = 6

UNSEEDED_SUFFIX = (('go-grade-machinery', 'go-grade-run'), ('exit-receipt-machinery',), ('phase6-exit',))

REGISTRY_ADMISSIONS = (('core-renderer', 'core-drift-classifier'),
 ('core-drift-activation', 'migrate-config'),
 ('host-contract-doc', 'fixture-host-scaffold'),
 ('bug-gate-grammar', 'report-inbox-triage'),
 ('escape-column',),
 ('supervised-merge-hold',),
 ('go-grade-machinery', 'go-grade-run'),
 ('exit-receipt-machinery',),
 ('phase6-exit',))

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

RENDER_BOUND_CHARS = 400000

REQ_RENDER_HEADROOM = 0.75

MEASURED_RENDER_TIER = 'max'

MEASURED_RENDER_EFFORT = 'max'

IMPLEMENT_BODY_CHARS = 5185

IMPLEMENT_SPEC = {'bytes': 5306, 'chars': 5306, 'sha256': 'f5d3ba603570a56f661a24d7a52d7e4543c0d003a82e36d664f5ef73f3599ddb'}

ROW_CONSUMPTION = {'supervised-merge-hold': ('escape-column',)}

FENCE_FLOORS = {'supervised-merge-hold': ('chupa/merge.py',
                           'chupa/mergequeue.py',
                           'chupa/serve.py',
                           'chupa/restart.py',
                           'chupa/baseline.py',
                           'chupa/control.py',
                           'chupa/__main__.py',
                           'chupa/stages.py',
                           'chupa/drain.py',
                           'chupa/runner.py',
                           'eval/daemon_soak.py',
                           'tests/test_merge.py',
                           'tests/test_mergequeue.py',
                           'tests/test_serve.py',
                           'tests/test_restart_timers.py',
                           'tests/test_baseline.py',
                           'tests/test_control_cli.py',
                           'tests/test_cli.py',
                           'tests/test_drain.py',
                           'tests/test_daemon_soak_runner.py',
                           'tests/test_supervised_merge_hold.py'),
 'phase6-continue-06': ('tickets', 'tests/test_seeded_phase6_06.py')}

FENCE_ADDITIONS = {'supervised-merge-hold': ('chupa/daemon.py',
                           'chupa/reconcile.py',
                           'tests/test_control.py',
                           'tests/test_reconcile.py'),
 'phase6-continue-06': ()}

CLOSURE_EVIDENCE = {'chupa/daemon.py': '19.L rule 5: TicketWriter.consume_result calls AdmissionBoundary.deliver then '
                    'harvest_failure/failure_terminal; held settlement has no live future.',
 'chupa/reconcile.py': '19.L rule 5: reconcile calls orphans then harvest, abandoned and worktree_remove for '
                       'every open run; durable completed holds need custody exclusion.',
 'tests/test_control.py': '19.L rule 2: Rig.decisions pins the closed decision keys; invalid_requests and '
                          'test_request_shape_and_identity_fail_closed pin operation shapes.',
 'tests/test_reconcile.py': '19.L rule 2: '
                            'test_running_with_no_terminal_is_reaped_to_abandoned_on_the_next_run and '
                            'test_an_open_effect_intent_is_an_orphan pin the pre-hold reap behavior.'}

CLOSURE_SCAN_PATTERN = ('AdmissionBoundary|MergeQueue|consume_result|resolve_baseline|ControlRequest|validate_request|orphans|reconcile|reviewed_sha|candidate_base|__all__|not '
 'hasattr|allowlist|def __init__|compose|build_daemon|confirm|reject')

CLOSURE_SCAN = {'chupa': {'matched_lines': 269,
           'files': 48,
           'sha256': '9505dd9c49b6c7642333775a35212ce6131c1bc854e909fae46119e3fe7fb900'},
 'eval': {'matched_lines': 60,
          'files': 10,
          'sha256': '5590b5114f3ae2b918b8c3916b438e74afe94b9c7731ad6069e2309bd0230669'},
 'tests': {'matched_lines': 1313,
           'files': 121,
           'sha256': '766136ae74caa2fb19b67d9f9978ffd436eaf7fbbe539ed4717d9ff5f7f68d8c'}}

CLOSURE_DECISIONS = ('19.L rule 2: tests/test_mergequeue.py::test_restore_rebase_safety_integration_order and '
 'tests/test_serve.py::test_serve_admission_rebases_regates_and_retires are fenced for admission changes.',
 '19.L rule 3: serve is already active; no construction dormancy fixture flips. No historical seeding '
 'fixture may be migrated.',
 '19.L rule 4: the hold entry assigns existing seam owners and introduces no new module.',
 '19.L rule 5: chupa/serve.py::Serve.merge zips ordered pending with queue.process results; identity '
 'delivery must use the producing stem and attempt.',
 '19.L rule 5: chupa/runner.py::bind calls compose_pipeline; Serve.__init__.prepared supplies '
 'AdmissionBoundary daemon mode; both are already fenced.',
 '19.L rule 5: eval/daemon_soak.py::_Member.prepare/start/settled and _observe exercise live serve and read '
 'review/check evidence; fenced for operator confirms and candidate-base regate proof.',
 '19.L rule 5: resolve_baseline(config, events, specs_dir) keeps its signature; author.py and baseline tests '
 'remain valid.',
 '19.L rule 5: pause/resume/kill keep operation-specific shapes and existing ControlRequest calls; no '
 'existing public-surface allowlist or standalone queue signature needs widening.',
 'Preserve tests/test_daemon_composition.py and tests/test_daemon_tasks.py standalone/foreground queue '
 'semantics; only daemon mode selects supervision. They are Verification-only.')

AUTHORED = {'supervised-merge-hold': {'bytes': 6695,
                           'chars': 6695,
                           'sha256': '6e167e95387377a81a8f567206fcddd8b148705f323cd2adcd6009ecf0ac6765',
                           'plan': ('19.I', '19.P6.supervised-merge-hold', '9', '12'),
                           'context': ('chupa/restart.py',
                                       'chupa/reconcile.py',
                                       'chupa/baseline.py',
                                       'tests/test_baseline.py',
                                       'chupa/control.py',
                                       'tests/test_control_cli.py',
                                       'tests/test_reconcile.py',
                                       'tests/test_daemon_soak_runner.py',
                                       'chupa/mergequeue.py',
                                       'tests/test_control.py',
                                       'chupa/__main__.py',
                                       'chupa/merge.py',
                                       'chupa/serve.py',
                                       'chupa/daemon.py',
                                       'tests/test_cli.py'),
                           'on_demand': ('chupa/stages.py',
                                         'chupa/drain.py',
                                         'chupa/runner.py',
                                         'eval/daemon_soak.py',
                                         'tests/test_merge.py',
                                         'tests/test_mergequeue.py',
                                         'tests/test_serve.py',
                                         'tests/test_restart_timers.py',
                                         'tests/test_drain.py'),
                           'fence': ('chupa/merge.py',
                                     'chupa/mergequeue.py',
                                     'chupa/serve.py',
                                     'chupa/restart.py',
                                     'chupa/baseline.py',
                                     'chupa/control.py',
                                     'chupa/__main__.py',
                                     'chupa/stages.py',
                                     'chupa/drain.py',
                                     'chupa/runner.py',
                                     'eval/daemon_soak.py',
                                     'tests/test_merge.py',
                                     'tests/test_mergequeue.py',
                                     'tests/test_serve.py',
                                     'tests/test_restart_timers.py',
                                     'tests/test_baseline.py',
                                     'tests/test_control_cli.py',
                                     'tests/test_cli.py',
                                     'tests/test_drain.py',
                                     'tests/test_daemon_soak_runner.py',
                                     'tests/test_supervised_merge_hold.py',
                                     'chupa/daemon.py',
                                     'chupa/reconcile.py',
                                     'tests/test_control.py',
                                     'tests/test_reconcile.py'),
                           'depends': ('phase6-continue-05', 'escape-column'),
                           'expected': 60,
                           'stuck': 90,
                           'fenced_existing': ('chupa/merge.py',
                                               'chupa/mergequeue.py',
                                               'chupa/serve.py',
                                               'chupa/restart.py',
                                               'chupa/baseline.py',
                                               'chupa/control.py',
                                               'chupa/__main__.py',
                                               'chupa/stages.py',
                                               'chupa/drain.py',
                                               'chupa/runner.py',
                                               'eval/daemon_soak.py',
                                               'tests/test_merge.py',
                                               'tests/test_mergequeue.py',
                                               'tests/test_serve.py',
                                               'tests/test_restart_timers.py',
                                               'tests/test_baseline.py',
                                               'tests/test_control_cli.py',
                                               'tests/test_cli.py',
                                               'tests/test_drain.py',
                                               'tests/test_daemon_soak_runner.py',
                                               'chupa/daemon.py',
                                               'chupa/reconcile.py',
                                               'tests/test_control.py',
                                               'tests/test_reconcile.py'),
                           'created': ('tests/test_supervised_merge_hold.py',),
                           'actual_render': 285230,
                           'render_overhead': 334,
                           'on_demand_embedding': {'chupa/stages.py': 356358,
                                                   'chupa/drain.py': 320140,
                                                   'chupa/runner.py': 323760,
                                                   'eval/daemon_soak.py': 321764,
                                                   'tests/test_merge.py': 331411,
                                                   'tests/test_mergequeue.py': 339934,
                                                   'tests/test_serve.py': 363045,
                                                   'tests/test_restart_timers.py': 319307,
                                                   'tests/test_drain.py': 346382},
                           'embedding_overhead': {'chupa/stages.py': 22,
                                                  'chupa/drain.py': 21,
                                                  'chupa/runner.py': 22,
                                                  'eval/daemon_soak.py': 26,
                                                  'tests/test_merge.py': 26,
                                                  'tests/test_mergequeue.py': 31,
                                                  'tests/test_serve.py': 26,
                                                  'tests/test_restart_timers.py': 35,
                                                  'tests/test_drain.py': 26}},
 'phase6-continue-06': {'bytes': 5838,
                        'chars': 5838,
                        'sha256': '368f836b39854e7df82a40265d5f278fa6d30990961e9712e7174a5aad836a2f',
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P6',
                                 '13',
                                 '19.P6.go-grade-machinery',
                                 '19.P6.go-grade-run',
                                 '19.P6.exit-receipt-machinery',
                                 '19.P6.fixture-host-scaffold',
                                 '19.P6.supervised-merge-hold'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fence': ('tickets', 'tests/test_seeded_phase6_06.py'),
                        'depends': ('supervised-merge-hold',),
                        'expected': 60,
                        'stuck': 90,
                        'fenced_existing': (),
                        'created': ('tests/test_seeded_phase6_06.py',),
                        'actual_render': 107783,
                        'render_overhead': -18,
                        'on_demand_embedding': {},
                        'embedding_overhead': {}}}

REQUIRED = {'supervised-merge-hold': ('19.P6.supervised-merge-hold',),
 'phase6-continue-06': ('19.P6.go-grade-machinery',
                        '19.P6.go-grade-run',
                        '19.P6.exit-receipt-machinery',
                        '19.P6.fixture-host-scaffold',
                        '19.P6.supervised-merge-hold')}

ENTRY_DEPTH = {'19.P6.supervised-merge-hold': {'bytes': 12388,
                                 'chars': 12388,
                                 'sha256': '3cd14d759d766a796aff1aff764b9a9f57f20a874c2cd0f19687a745cb167013',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 1822, 'Records': 3853, 'Observable': 3538, 'Tests': 3041},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
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
 '19.P6.go-grade-machinery': {'bytes': 8163,
                              'chars': 8163,
                              'sha256': '06416436a5ca1b24503215f6b9732d815df650d3d039b55418d6af6b4334bdc9',
                              'resolves': 1,
                              'gap': None,
                              'parts': {'Owner': 1318, 'Records': 3643, 'Observable': 1294, 'Tests': 1767},
                              'missing_part_rejected': {'Owner': True,
                                                        'Records': True,
                                                        'Observable': True,
                                                        'Tests': True},
                              'tests': ('test_go_grade_entry_units',
                                        'test_go_grade_fixture_floors_and_author_separation',
                                        'test_go_grade_scoring_and_partial_report',
                                        'test_go_grade_shared_cap_includes_retries_and_author_graph',
                                        'test_go_grade_author_graph_uses_local_prompt',
                                        'test_eval_budget_ceiling_before_spawn',
                                        'test_record_go_requires_complete_floors_identity_and_operator_judgment',
                                        'test_review_baseline_report_closed_schema',
                                        'test_review_baseline_report_registered_checks_lift')},
 '19.P6.go-grade-run': {'bytes': 3377,
                        'chars': 3377,
                        'sha256': 'b2c959c1c85c04990f5422dbd9371ca3ddc8d02287e7ce54f17516d2d070466a',
                        'resolves': 1,
                        'gap': None,
                        'parts': {'Owner': 483, 'Records': 1041, 'Observable': 813, 'Tests': 910},
                        'missing_part_rejected': {'Owner': True,
                                                  'Records': True,
                                                  'Observable': True,
                                                  'Tests': True},
                        'tests': ('test_go_grade_scoring_and_partial_report',
                                  'test_record_go_requires_complete_floors_identity_and_operator_judgment',
                                  'test_review_baseline_report_closed_schema',
                                  'test_review_baseline_report_registered_checks_lift',
                                  'test_outbox_only_check_requires_current_report',
                                  'test_outbox_only_merge_regate_requires_lift_custody',
                                  'test_outbox_only_admission_records_null_commit_and_retires')},
 '19.P6.exit-receipt-machinery': {'bytes': 7110,
                                  'chars': 7110,
                                  'sha256': 'b8275a4dd5817f3f1ea2459500f0e1ef3c31e8a9c55ea0e8b6789fa88e8d2f2d',
                                  'resolves': 1,
                                  'gap': None,
                                  'parts': {'Owner': 1115,
                                            'Records': 2514,
                                            'Observable': 1565,
                                            'Tests': 1763},
                                  'missing_part_rejected': {'Owner': True,
                                                            'Records': True,
                                                            'Observable': True,
                                                            'Tests': True},
                                  'tests': ('test_exit_receipt_entry_unit',
                                            'test_host_loop_closed_schema',
                                            'test_host_loop_drives_supervised_fixture_serve',
                                            'test_host_loop_report_regression_and_escape',
                                            'test_host_loop_requires_member_auditor_green',
                                            'test_exit_receipt_closed_schema_and_baseline_identity',
                                            'test_exit_receipt_regenerates_from_committed_bytes',
                                            'test_host_loop_and_receipt_registered_checks_lift',
                                            'test_host_loop_regression_uses_real_bug_gate')},
 '19.P6.fixture-host-scaffold': {'bytes': 6157,
                                 'chars': 6157,
                                 'sha256': 'f67e09cc8d94030c66a580cdd0f794e4472aa0ccde256dc823ab3c8a0e56fbfc',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 681, 'Records': 2312, 'Observable': 1329, 'Tests': 1700},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'tests': ('test_fixture_host_entry_units',
                                           'test_fixture_profile_loads',
                                           'test_fixture_scenario_list_is_closed',
                                           'test_fixture_replay_is_deterministic',
                                           'test_fixture_regression_exists_at_base',
                                           'test_fixture_escape_is_machine_introduced',
                                           'test_fixture_reports_are_bounded',
                                           'test_fixture_cli_adapter_roundtrip',
                                           'test_fixture_scaffold_is_dormant')}}

HOLD_OBLIGATIONS = (('tests/test_supervised_merge_hold.py',
  'test_supervised_hold_entry_unit',
  'required_units, unique resolve_plan_contract resolution, and every entry_unit_gap part'),
 ('tests/test_supervised_merge_hold.py',
  'test_hold_after_green_before_main_mutation',
  'all baseline refusal cases, safety/integration ordering, and gate-red refusal'),
 ('tests/test_supervised_merge_hold.py',
  'test_go_coverage_uses_actual_review_identity',
  'served identity, tier coverage, contradictory evidence, and later GO'),
 ('tests/test_supervised_merge_hold.py',
  'test_held_run_keeps_worktree_and_has_no_terminal',
  'typed hold, stable vocabularies, retained custody, and no failure/cap path'),
 ('tests/test_serve.py',
  'test_supervised_hold_allows_other_work',
  'unrelated work and heartbeat progress, backpressure, exclusion, and result identity'),
 ('tests/test_mergequeue.py',
  'test_supervised_confirm_regates_moved_main',
  'unchanged/moved bases, two candidates, clean approval carry, conflicts, red gates, and trees'),
 ('tests/test_control.py',
  'test_supervised_request_identity_and_replay',
  'request/decision closure, stale identities, replay, duplicates, and both crash boundaries'),
 ('tests/test_control_cli.py',
  'test_confirm_held_without_writer_lock',
  'live and dirless publication, writer-lock independence, and draft/Reject preservation'),
 ('tests/test_control_cli.py',
  'test_reject_held_candidate',
  'rejection, dependency notification, no cap re-arm, and unchanged main'),
 ('tests/test_restart_timers.py',
  'test_restart_reconstructs_supervised_admission',
  'completed/partial receipts, releases across crashes, corrupt evidence, and repeated recovery'),
 ('tests/test_reconcile.py',
  'test_live_hold_is_not_an_orphan',
  'retained held ownership, no model rerun, incomplete intents, and ordinary orphan handling'),
 ('tests/test_merge.py',
  'test_foreground_admission_never_supervised_holds',
  'foreground exemption through its actual composition'),
 ('tests/test_drain.py',
  'test_bootstrap_never_supervised_holds',
  'bootstrap exemption through its actual composition'),
 ('tests/test_daemon_soak_runner.py',
  'test_soak_uses_candidate_base_regate_receipt',
  'real served identity, operator fixture confirms, moved base, and member-local audit'))

PLAN_SIZES = {'19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P6.supervised-merge-hold': {'bytes': 12388,
                                 'chars': 12388,
                                 'sha256': '3cd14d759d766a796aff1aff764b9a9f57f20a874c2cd0f19687a745cb167013'},
 '9': {'bytes': 20096,
       'chars': 20096,
       'sha256': 'd9aea752580c76267512cf8cae3eccb687f23965da59fce2a3fa1bc4c0a361fe'},
 '12': {'bytes': 20224,
        'chars': 20224,
        'sha256': 'd3917109abd72822abd53cfadc7c74913fb6186ba72191820d0600c26cfac8cb'},
 '19.L': {'bytes': 20912,
          'chars': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa'},
 '19.P6': {'bytes': 11595,
           'chars': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c'},
 '13': {'bytes': 19840,
        'chars': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P6.go-grade-machinery': {'bytes': 8163,
                              'chars': 8163,
                              'sha256': '06416436a5ca1b24503215f6b9732d815df650d3d039b55418d6af6b4334bdc9'},
 '19.P6.go-grade-run': {'bytes': 3377,
                        'chars': 3377,
                        'sha256': 'b2c959c1c85c04990f5422dbd9371ca3ddc8d02287e7ce54f17516d2d070466a'},
 '19.P6.exit-receipt-machinery': {'bytes': 7110,
                                  'chars': 7110,
                                  'sha256': 'b8275a4dd5817f3f1ea2459500f0e1ef3c31e8a9c55ea0e8b6789fa88e8d2f2d'},
 '19.P6.fixture-host-scaffold': {'bytes': 6157,
                                 'chars': 6157,
                                 'sha256': 'f67e09cc8d94030c66a580cdd0f794e4472aa0ccde256dc823ab3c8a0e56fbfc'}}

FILE_SIZES = {'chupa/merge.py': {'bytes': 21717,
                    'chars': 21717,
                    'sha256': '83efe01c4a2013046f69da93037a6a4b6e362c5fd3a79e0faa08f74d0f06504c',
                    'delimiter_free': True,
                    'quoted_chars': 21717},
 'chupa/mergequeue.py': {'bytes': 16262,
                         'chars': 16262,
                         'sha256': 'f5e150bf011a5b1e1d091a261a4eb2982ab261b7312652ba659266d78b19af56',
                         'delimiter_free': True,
                         'quoted_chars': 16262},
 'chupa/serve.py': {'bytes': 21874,
                    'chars': 21874,
                    'sha256': 'a5321ec380443dfb4c9b026dec400f7d963cb64293f53713ec96150b941ee0fa',
                    'delimiter_free': True,
                    'quoted_chars': 21874},
 'chupa/restart.py': {'bytes': 1951,
                      'chars': 1951,
                      'sha256': 'c28604080de390ecd048f5f0463572c2087708fbae4fabc2635df55bfa91a985',
                      'delimiter_free': True,
                      'quoted_chars': 1951},
 'chupa/baseline.py': {'bytes': 3413,
                       'chars': 3413,
                       'sha256': '93e8c3a61a322591308bb752fe9cb16c89e57090cde4280c9e24e9b0ab36e9d9',
                       'delimiter_free': True,
                       'quoted_chars': 3413},
 'chupa/control.py': {'bytes': 9879,
                      'chars': 9879,
                      'sha256': 'd07474e79a31b6cbd5019ba2ca0cbd5d4f128a12af4659940d2787ced0b12f33',
                      'delimiter_free': True,
                      'quoted_chars': 9879},
 'chupa/__main__.py': {'bytes': 19550,
                       'chars': 19550,
                       'sha256': 'f7c61fc7900607e2a1441fd8459058ed7dd631e12336ff3ac840e2113735364a',
                       'delimiter_free': True,
                       'quoted_chars': 19550},
 'chupa/stages.py': {'bytes': 71106,
                     'chars': 71106,
                     'sha256': '0bf96fd6f95e3de9049805ac78f42105dbc24b92d3767392b16c85bf261318e1',
                     'delimiter_free': True,
                     'quoted_chars': 71106},
 'chupa/drain.py': {'bytes': 34889,
                    'chars': 34889,
                    'sha256': '76318f0a0026d8066141e4fab2f69f489d8079b8f8ab7d9da40071cb26f2bf62',
                    'delimiter_free': True,
                    'quoted_chars': 34889},
 'chupa/runner.py': {'bytes': 38508,
                     'chars': 38508,
                     'sha256': 'b1d8c2debc4a150a8e29d4bb3aaa86fb5e14482db2a4eb1f3d061a673ba941e4',
                     'delimiter_free': True,
                     'quoted_chars': 38508},
 'eval/daemon_soak.py': {'bytes': 36511,
                         'chars': 36511,
                         'sha256': 'cfae264b498d6786e31d15f6f2d9536c58a74a6d447520020c6333f3b666a919',
                         'delimiter_free': False,
                         'quoted_chars': 36508},
 'tests/test_merge.py': {'bytes': 46155,
                         'chars': 46155,
                         'sha256': '9ccfdc1864b5712936239876f51d808b191646b35f8fb4beb16d0d7ae6ba776d',
                         'delimiter_free': True,
                         'quoted_chars': 46155},
 'tests/test_mergequeue.py': {'bytes': 54673,
                              'chars': 54673,
                              'sha256': 'eb6c6b0a54704bb4561e725f5fd925dfc10ae07a66a3602bd742c86fd51c3f6e',
                              'delimiter_free': True,
                              'quoted_chars': 54673},
 'tests/test_serve.py': {'bytes': 77789,
                         'chars': 77789,
                         'sha256': '5ac3f0dcc74307a929c99f7a86bfbfbac655e5e399290cb37b06a1b0dbaef748',
                         'delimiter_free': True,
                         'quoted_chars': 77789},
 'tests/test_restart_timers.py': {'bytes': 34042,
                                  'chars': 34042,
                                  'sha256': '3dfa913ded80d91c9b61eef44b460648f56f4a45208207131087a8ba8049541d',
                                  'delimiter_free': True,
                                  'quoted_chars': 34042},
 'tests/test_baseline.py': {'bytes': 7609,
                            'chars': 7609,
                            'sha256': '216ccb3ca1e68fd6caf00715c1d5bfe2192dc35f28d0bc93086b05e45f0f091b',
                            'delimiter_free': True,
                            'quoted_chars': 7609},
 'tests/test_control_cli.py': {'bytes': 10264,
                               'chars': 10264,
                               'sha256': '2dda06596b87259cedfaa9fc354582266b34af52ee991553288e24f4297b7915',
                               'delimiter_free': True,
                               'quoted_chars': 10264},
 'tests/test_cli.py': {'bytes': 30441,
                       'chars': 30441,
                       'sha256': 'bb5fd7746d0a9136d309bbc3fd0448ee3f15dcfb099e7b822ca7c59500b5ef15',
                       'delimiter_free': True,
                       'quoted_chars': 30441},
 'tests/test_drain.py': {'bytes': 61126,
                         'chars': 61126,
                         'sha256': 'f84244716b11916ea11b5d7eda23068f6bef7cd475def5ab690cadc7417fbe31',
                         'delimiter_free': True,
                         'quoted_chars': 61126},
 'tests/test_daemon_soak_runner.py': {'bytes': 15622,
                                      'chars': 15622,
                                      'sha256': '7a8f1eec806d0b86a51af8887127ed316fbd3c78dd27905bcc93b6a4947da899',
                                      'delimiter_free': True,
                                      'quoted_chars': 15622},
 'chupa/daemon.py': {'bytes': 26187,
                     'chars': 26187,
                     'sha256': '6bba2e43daee7e3a5b7c178babaf0326fb69bbb10060a5ca0d44d013b3bce60b',
                     'delimiter_free': True,
                     'quoted_chars': 26187},
 'chupa/reconcile.py': {'bytes': 2715,
                        'chars': 2715,
                        'sha256': '22132375e18cfcb8a0a92779c752c0bd379086e97a838766aa62ab05ce04e466',
                        'delimiter_free': True,
                        'quoted_chars': 2715},
 'tests/test_control.py': {'bytes': 17034,
                           'chars': 17031,
                           'sha256': '65c02ae7b3c8cccb454025f6a58d6bb1e43fd2d48f6e7d74b8248d544c2efd57',
                           'delimiter_free': True,
                           'quoted_chars': 17031},
 'tests/test_reconcile.py': {'bytes': 13982,
                             'chars': 13982,
                             'sha256': 'b711465f1faa6e4bc8ac02960c2c0e77a9ac430754d7bad371d7dd98ec69338e',
                             'delimiter_free': True,
                             'quoted_chars': 13982},
 'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559',
                                      'delimiter_free': True,
                                      'quoted_chars': 5425}}

HISTORICAL_SNAPSHOTS = {'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559'},
 'tests/test_seeded_phase6_core.py': {'bytes': 35196,
                                      'chars': 35196,
                                      'sha256': '7606a766e009e53284c8154c971847ed5f58b20dfff3f945266d35a324870cae'},
 'tests/test_seeded_phase6_01.py': {'bytes': 57492,
                                    'chars': 57492,
                                    'sha256': '735465971d2bb73e92e29e7b25ed9d6690b400268fa95044c786dab85befaabe'},
 'tests/test_seeded_phase6_02.py': {'bytes': 34282,
                                    'chars': 34282,
                                    'sha256': '215e19c190648bbd108913994c5efd6e7c4343bf8f0db43723d2b8644c23c772'},
 'tests/test_seeded_phase6_03.py': {'bytes': 37248,
                                    'chars': 37248,
                                    'sha256': '4c94c271fdaf398680493b3afcc8fba59e8011306ba268e6b6c8a903b20eb915'},
 'tests/test_seeded_phase6_04.py': {'bytes': 40447,
                                    'chars': 40447,
                                    'sha256': 'c2456fe6ee2160dcb851760ec587ec4a75b4227a31e9d87a2860af41939f71ca'}}

COPY_VIOLATIONS = ()

AUTHORING_TRACKED_SEEDS = ()

DELIVERY = {'seeds': ('tickets/supervised-merge-hold/ticket.md', 'tickets/phase6-continue-06/ticket.md'),
 'commit_only': 'tests/test_seeded_phase6_05.py',
 'approval_record': 'tickets/phase6-continue-05/checks.json',
 'review': 'requisition_review',
 'lift': 'ticket-plane',
 'retry': 'retain approved bytes while ticket_sha matches; author only snagged seeds'}


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_BODY_CHARS + a["chars"] + a["render_overhead"]
            + sum(PLAN_SIZES[uid]["chars"] for uid in a["plan"])
            + sum(FILE_SIZES[path]["chars"] for path in a["context"])
            + sum(FILE_SIZES[path]["quoted_chars"] + a["embedding_overhead"][path] for path in extra))


def test_phase6_05_exact_admission():
    assert BATCH == ("supervised-merge-hold", "phase6-continue-06")
    assert PAYLOADS == REGISTRY_ADMISSIONS[5] == ("supervised-merge-hold",)
    assert POSITION == 6 and UNSEEDED_SUFFIX == REGISTRY_ADMISSIONS[POSITION:]
    assert UNSEEDED_SUFFIX == (
        ("go-grade-machinery", "go-grade-run"), ("exit-receipt-machinery",), ("phase6-exit",))
    assert len(set(BATCH)) == len(BATCH) == 2 <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(BATCH)
    assert ROW_CONSUMPTION == {"supervised-merge-hold": ("escape-column",)}
    for stem in BATCH:
        t, a = _ticket(stem), AUTHORED[stem]
        assert (t.frontmatter.source, t.frontmatter.state, t.frontmatter.kind,
                t.frontmatter.priority) == ("seed", "confirmed", "feature", "P1")
        tier = "high" if stem in PAYLOADS else "medium"
        assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == (tier, tier)
        assert t.depends == a["depends"]
        assert t.plan_contract == a["plan"]
        assert (t.expected_minutes, t.stuck_minutes) == (a["expected"], a["stuck"])
        assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES
        # Consumption cannot point into the remaining admissions.
        assert not set(t.depends) & {s for admission in UNSEEDED_SUFFIX for s in admission}
    hold, successor = (_ticket(stem) for stem in BATCH)
    assert hold.depends == ("phase6-continue-05", "escape-column")
    assert hold.plan_contract == ("19.I", "19.P6.supervised-merge-hold", "9", "12")
    assert successor.depends == PAYLOADS
    assert successor.scope_fence == ("tickets", "tests/test_seeded_phase6_06.py")
    assert successor.context == ("tests/test_seeded_phase3_core.py",)
    assert successor.plan_contract == (
        "19.L", "19.I", "19.P6", "13", "19.P6.go-grade-machinery", "19.P6.go-grade-run",
        "19.P6.exit-receipt-machinery", "19.P6.fixture-host-scaffold", "19.P6.supervised-merge-hold")
    scope = successor.sections["Scope in / Scope out"]
    suffix = scope.split("Position 6 carries admissions[6:]:\n", 1)[1].split("\n\nAuthor exactly", 1)[0]
    assert suffix.splitlines() == ["- [" + ", ".join(a) + "]" for a in UNSEEDED_SUFFIX]
    for fact in ("Author exactly go-grade-machinery, go-grade-run and phase6-continue-07",
                 "position 7 and admissions[7:]", "depends on both GO-grade payloads",
                 "deep: true", "high/high", "medium/medium", "KNOWN-HARD", "no successor",
                 "seeding.max_seeds_per_admission", "drain.max_ticket_minutes", "three seeds"):
        assert fact in scope
    assert "deep: true" in hold.sections["Scope in / Scope out"]
    assert "high/high" in hold.sections["Scope in / Scope out"]


def test_phase6_05_entry_depth():
    assert REQUIRED == {
        "supervised-merge-hold": ("19.P6.supervised-merge-hold",),
        "phase6-continue-06": ("19.P6.go-grade-machinery", "19.P6.go-grade-run",
                               "19.P6.exit-receipt-machinery", "19.P6.fixture-host-scaffold",
                               "19.P6.supervised-merge-hold")}
    assert set(ENTRY_DEPTH) == {uid for units in REQUIRED.values() for uid in units}
    for stem, units in REQUIRED.items():
        assert len(units) == len(set(units))
        assert set(units) <= set(AUTHORED[stem]["plan"])
        for uid in units:
            d = ENTRY_DEPTH[uid]
            assert d["resolves"] == 1 and d["gap"] is None
            assert set(d["parts"]) == {"Owner", "Records", "Observable", "Tests"}
            assert all(n > 0 for n in d["parts"].values())
            assert d["missing_part_rejected"].keys() == d["parts"].keys()
            assert all(d["missing_part_rejected"].values())
            assert {k: d[k] for k in ("bytes", "chars", "sha256")} == PLAN_SIZES[uid]
            assert d["tests"]
    names = (
        "test_supervised_hold_entry_unit", "test_hold_after_green_before_main_mutation",
        "test_go_coverage_uses_actual_review_identity", "test_held_run_keeps_worktree_and_has_no_terminal",
        "test_supervised_hold_allows_other_work", "test_supervised_confirm_regates_moved_main",
        "test_supervised_request_identity_and_replay", "test_confirm_held_without_writer_lock",
        "test_reject_held_candidate", "test_restart_reconstructs_supervised_admission",
        "test_live_hold_is_not_an_orphan", "test_foreground_admission_never_supervised_holds",
        "test_bootstrap_never_supervised_holds", "test_soak_uses_candidate_base_regate_receipt")
    assert ENTRY_DEPTH["19.P6.supervised-merge-hold"]["tests"] == names
    assert tuple(name for _, name, _ in HOLD_OBLIGATIONS) == names
    hold = _ticket(PAYLOADS[0])
    acceptance = hold.sections["Acceptance criteria"]
    for path, name, summary in HOLD_OBLIGATIONS:
        assert path + "::" + name in acceptance and summary in acceptance
        assert path in hold.scope_fence
        assert path in {arg for argv in hold.verification for arg in argv}
    assert all(op in acceptance for op in ("required_units", "resolve_plan_contract", "entry_unit_gap"))
    successor = _ticket(BATCH[-1])
    scope = successor.sections["Scope in / Scope out"]
    for op in ("required_units", "resolve_plan_contract", "entry_unit_gap", "Owner", "Records",
               "Observable", "Tests", "before grammar and review", "both GO-grade",
               "fixture-host-scaffold", "supervised-merge-hold", "go-grade-machinery", "go-grade-run"):
        assert op in scope
    assert not COPY_VIOLATIONS


def test_phase6_05_closure():
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert FENCE_ADDITIONS == {
        "supervised-merge-hold": ("chupa/daemon.py", "chupa/reconcile.py",
                                 "tests/test_control.py", "tests/test_reconcile.py"),
        "phase6-continue-06": ()}
    assert set(CLOSURE_EVIDENCE) == set(FENCE_ADDITIONS[PAYLOADS[0]])
    assert all("19.L rule 2" in reason or "19.L rule 5" in reason
               for reason in CLOSURE_EVIDENCE.values())
    assert "TicketWriter.consume_result" in CLOSURE_EVIDENCE["chupa/daemon.py"]
    assert "orphans" in CLOSURE_EVIDENCE["chupa/reconcile.py"]
    assert "Rig.decisions" in CLOSURE_EVIDENCE["tests/test_control.py"]
    assert "test_an_open_effect_intent_is_an_orphan" in CLOSURE_EVIDENCE["tests/test_reconcile.py"]
    assert len(CLOSURE_DECISIONS) == 9
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    for record in CLOSURE_SCAN.values():
        assert record["matched_lines"] > 0 and record["files"] > 0
        assert len(record["sha256"]) == 64
    assert set(HISTORICAL_SNAPSHOTS) == {
        "tests/test_seeded_phase3_core.py", "tests/test_seeded_phase6_core.py",
        "tests/test_seeded_phase6_01.py", "tests/test_seeded_phase6_02.py",
        "tests/test_seeded_phase6_03.py", "tests/test_seeded_phase6_04.py"}
    assert FILE_SIZES["tests/test_seeded_phase3_core.py"]["sha256"] == (
        HISTORICAL_SNAPSHOTS["tests/test_seeded_phase3_core.py"]["sha256"])
    assert RENDER_BOUND_CHARS == 400_000 and REQ_RENDER_HEADROOM == 0.75
    assert (MEASURED_RENDER_TIER, MEASURED_RENDER_EFFORT) == ("max", "max")
    for stem, a in AUTHORED.items():
        t = _ticket(stem)
        assert t.scope_fence == (*FENCE_FLOORS[stem], *FENCE_ADDITIONS[stem])
        assert (t.context, t.on_demand) == (a["context"], a["on_demand"])
        assert set(a["fenced_existing"]) <= set(t.context) | set(t.on_demand)
        assert not set(t.context) & set(t.on_demand)
        assert not set(a["created"]) & (set(t.context) | set(t.on_demand))
        assert not {"tests/test_seeded_phase6_05.py", "tests/test_seeded_phase6_06.py"} & set(t.context)
        assert not set(HISTORICAL_SNAPSHOTS) & set(t.scope_fence)
        assert all(FILE_SIZES[p]["delimiter_free"] and not p.startswith("specs/") for p in t.context)
        assert render_chars(stem) == a["actual_render"] <= RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM
        assert set(a["on_demand_embedding"]) == set(a["embedding_overhead"]) == set(t.on_demand)
        for p in t.on_demand:
            assert p in a["fenced_existing"]
            assert render_chars(stem, (p,)) == a["on_demand_embedding"][p] > (
                RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM)
        data = (ROOT / ticket_path(stem)).read_bytes()
        assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
            a["bytes"], a["chars"], a["sha256"])
    assert AUTHORED[PAYLOADS[0]]["created"] == ("tests/test_supervised_merge_hold.py",)
    assert AUTHORED[BATCH[-1]]["created"] == ("tests/test_seeded_phase6_06.py",)
    assert not FILE_SIZES["eval/daemon_soak.py"]["delimiter_free"]
    assert "eval/daemon_soak.py" in _ticket(PAYLOADS[0]).on_demand
    for record in (*PLAN_SIZES.values(), *FILE_SIZES.values(),
                   *HISTORICAL_SNAPSHOTS.values(), IMPLEMENT_SPEC):
        assert record["bytes"] >= record["chars"] > 0 and len(record["sha256"]) == 64
    preserved = {"tests/test_daemon_composition.py", "tests/test_daemon_tasks.py",
                 "tests/test_kill_signal_journal.py", "tests/test_storm_hold.py",
                 "tests/test_bug_gate.py", "tests/test_rework.py"}
    hold = _ticket(PAYLOADS[0])
    assert not preserved & (set(hold.context) | set(hold.on_demand) | set(hold.scope_fence))
    assert preserved <= {arg for argv in hold.verification for arg in argv}


def test_phase6_05_check_owns_seed_custody(seed_repo):
    assert AUTHORING_TRACKED_SEEDS == ()
    assert DELIVERY == {
        "seeds": tuple(ticket_path(s) for s in BATCH),
        "commit_only": "tests/test_seeded_phase6_05.py",
        "approval_record": "tickets/phase6-continue-05/checks.json",
        "review": "requisition_review", "lift": "ticket-plane",
        "retry": "retain approved bytes while ticket_sha matches; author only snagged seeds"}
    raw = (ROOT / ticket_path(BATCH[-1])).read_text()
    for fact in ("uncommitted", "requisition_review", "tickets/phase6-continue-06/checks.json",
                 "ticket-plane seed lift", "approved bytes", "ticket_sha", "snagged seeds"):
        assert fact in raw

    # Exercise the actual seeding lane with minimal contracts on disposable main.
    # Production hold/GO-grade modules are intentionally not required by this ticket.
    seeder = "phase6-continue-05"
    own = ticket_path(seeder)
    setup, _ = context(seed_repo, [])
    setup.fs.write(seed_repo / own, seeding_text().encode())
    (seed_repo / ticket_path(STEM)).unlink()

    async def prepare():
        await setup.git.add(seed_repo, [own, ticket_path(STEM)])
        await setup.git.commit(seed_repo, "use the phase6 seeder identity")
    asyncio.run(prepare())
    ticket = validate_ticket(seeder, (seed_repo / own).read_text(), seed_repo)
    seeds = {s: seed_text(s) for s in BATCH}
    approved, snagged = sorted(BATCH)
    snag = {"code": "scope", "message": "missing test", "paved_road": "name the test",
            "kind": "authoring_error"}

    def implement_seeds(ctx, emitted, *, retry=False):
        async def act(request):
            assert request.surface == "implement" and request.worktree is not None
            if retry:
                assert "## Approved seeds (keep verbatim)" in request.rendered
                assert (request.worktree / ticket_path(approved)).read_text() == seeds[approved]
                assert set(emitted) == {snagged}
            for stem, text in emitted.items():
                ctx.fs.write(request.worktree / ticket_path(stem), text.encode())

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
    ctx.driver.llm = SeedLLM([implement_reply(), requisition("approve"),
                             requisition("snag", [snag]), diagnosis_reply()])
    ctx.driver.llm.emit = implement_seeds(ctx, seeds)
    assert asyncio.run(drive(ctx, ticket)) == "gate_failed"
    receipt = Invoice.model_validate_json((seed_repo / DELIVERY["approval_record"]).read_text())
    assert [(s.stem, s.verdict) for s in receipt.seeds] == [(approved, "approve"), (snagged, "snag")]
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
    assert "missing test" in requests[0].rendered and "tested." in requests[0].rendered
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
        changed = await retry.git._run(seed_repo, "show", "--format=", "--name-only",
                                      lift.body["result"]["commit"])
        assert set(changed.splitlines()) == set(DELIVERY["seeds"])
        subjects = (await retry.git._run(seed_repo, "log", "--format=%s")).splitlines()
        assert subjects.count("chupa(" + seeder + "): seeds") == 1
        intake = [e for e in events if e.type == EventType.SIGNAL
                  and e.body.get("signal") == "ticket_intake" and e.body.get("seeded_by") == seeder]
        assert [e.ticket for e in intake] == sorted(BATCH)
        assert all(events.index(check) < events.index(lift) < events.index(e) for e in intake)
    asyncio.run(custody())
