"""Phase 6 admission 4: escape seed and its continuation.

Sizes, contract depth, hashes and closure evidence are authoring-time snapshots.
Only authored ticket identity is read live, following the merged Phase 3 idiom.
The custody scenario exercises production Check on a disposable repository.
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

AUTHORING_HEAD = '80eadc21d7922943601d7b40307d9c0897366582'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('escape-column', 'phase6-continue-05')

PAYLOADS = ('escape-column',)

POSITION = 5

UNSEEDED_SUFFIX = (('supervised-merge-hold',),
 ('go-grade-machinery', 'go-grade-run'),
 ('exit-receipt-machinery',),
 ('phase6-exit',))

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

IMPLEMENT_SPEC = {'bytes': 5306,
 'chars': 5306,
 'sha256': 'f5d3ba603570a56f661a24d7a52d7e4543c0d003a82e36d664f5ef73f3599ddb'}

ROW_CONSUMPTION = {'escape-column': ('bug-gate-grammar', 'report-inbox-triage')}

FENCE_FLOORS = {'escape-column': ('chupa/scorecard.py',
                   'chupa/git.py',
                   'chupa/retro.py',
                   'chupa/__main__.py',
                   'tests/test_scorecard.py',
                   'tests/test_git.py',
                   'tests/test_retro.py',
                   'tests/test_cli.py',
                   'tests/test_mergequeue.py'),
 'phase6-continue-05': ('tickets', 'tests/test_seeded_phase6_05.py')}

FENCE_ADDITIONS = {'escape-column': ('chupa/triage.py', 'tests/test_triage.py'), 'phase6-continue-05': ()}

CLOSURE_EVIDENCE = {'chupa/triage.py': '19.L rule 5: _settle_pass calls author at lines 146 and 190, after which bug '
                    'resolution needs attribution; triage_pass at line 92 owns the sequential lane '
                    'and can retain its signature.',
 'tests/test_triage.py': '19.L rule 5: test_report_ingested_before_pending_scan and '
                         'test_report_author_failure_is_decision exercise the existing production '
                         'triage consumer; the escape entry assigns its new completion and retry '
                         'obligations here.'}

CLOSURE_SCAN_PATTERN = ('project_scorecard|SurfaceScorecardRow|production_evidence|triage_pass|_settle_pass|chupa-reviewed-sha|chupa-ticket|__all__|not '
 'hasattr|allowlist|def __init__|compose|build_daemon')

CLOSURE_SCAN = {'chupa': {'matched_lines': 109,
           'files': 41,
           'sha256': 'd66c5b84abdd25257cfec7fea5b88d02299511db52da22910684199ab2309d23'},
 'eval': {'matched_lines': 24,
          'files': 9,
          'sha256': '2e2dbf1d74129018b0462ec1a96bc5a57dbc2d9186d716ab3c862aa635db6539'},
 'tests': {'matched_lines': 344,
           'files': 91,
           'sha256': '5ea887ece5addbb2acc9b0cec9ed84ea6ed0976892d5f9053d6d3e26128c43de'}}

CLOSURE_DECISIONS = ('19.L rule 2: tests/test_scorecard.py::test_scorecard_catches_resolved_and_upheld_findings and '
 'test_scorecard_rates_and_prune_threshold pin zero escapes only without attribution; retain their '
 'behavior. The new fold adds attribution-only counts.',
 '19.L rule 2: tests/test_status.py::test_status_current_window_scorecard and '
 'tests/test_phase5_exit.py preserve Phase 5 inputs without attribution; no fence addition is '
 'earned.',
 '19.L rule 3: no dormant component is activated; existing scorecard and triage production paths '
 'remain reachable.',
 '19.L rule 4: no new module; the escape entry assigns Git, triage, scorecard, retro and CLI '
 'ownership.',
 '19.L rule 5: chupa/status.py::project, chupa/retro.py::render_report and tests/test_scorecard.py '
 'call project_scorecard(window); preserve that signature and SurfaceScorecardRow shape.',
 '19.L rule 5: chupa/serve.py::Serve.triage, chupa/__main__.py::main and eval/daemon_soak.py reach '
 'triage_pass(checkout,llm); preserve that signature and bootstrap no-consumer assertions.',
 '19.L rule 5: tests/test_git.py::test_op_argv enumerates argv cases, not a class-surface '
 'allowlist; it is already fenced for the new Git read.',
 'tests/test_mergequeue.py::test_squash_tree_trailers_and_retirement, tests/test_merge.py '
 'approval-carry tests and tests/test_serve.py trailer assertions remain true; escape reads the '
 'existing squash_message producer, never changes it.')

AUTHORED = {'escape-column': {'bytes': 5142,
                   'chars': 5142,
                   'sha256': 'eca4ac54e7d0edb3ec455b4a256730a1d9fe86b9cb6550091b125589a6095751',
                   'plan': ('19.I',
                            '19.P6.escape-column',
                            '19.P6.bug-gate-grammar',
                            '19.P6.report-inbox-triage',
                            '10',
                            '14'),
                   'context': ('chupa/scorecard.py',
                               'chupa/git.py',
                               'chupa/retro.py',
                               'chupa/__main__.py',
                               'tests/test_scorecard.py',
                               'tests/test_git.py',
                               'tests/test_retro.py',
                               'tests/test_cli.py',
                               'tests/test_mergequeue.py',
                               'chupa/triage.py',
                               'tests/test_triage.py'),
                   'on_demand': (),
                   'fence': ('chupa/scorecard.py',
                             'chupa/git.py',
                             'chupa/retro.py',
                             'chupa/__main__.py',
                             'tests/test_scorecard.py',
                             'tests/test_git.py',
                             'tests/test_retro.py',
                             'tests/test_cli.py',
                             'tests/test_mergequeue.py',
                             'chupa/triage.py',
                             'tests/test_triage.py'),
                   'depends': ('phase6-continue-04', 'bug-gate-grammar', 'report-inbox-triage'),
                   'expected': 60,
                   'stuck': 90,
                   'fenced_existing': ('chupa/scorecard.py',
                                       'chupa/git.py',
                                       'chupa/retro.py',
                                       'chupa/__main__.py',
                                       'tests/test_scorecard.py',
                                       'tests/test_git.py',
                                       'tests/test_retro.py',
                                       'tests/test_cli.py',
                                       'tests/test_mergequeue.py',
                                       'chupa/triage.py',
                                       'tests/test_triage.py'),
                   'created': (),
                   'actual_render': 257512,
                   'render_overhead': 216},
 'phase6-continue-05': {'bytes': 5730,
                        'chars': 5730,
                        'sha256': 'e404b8957ca5473c0d36e25f414ac0b76f73958f98534b546d77a8e6d1bf2eb1',
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P6',
                                 '13',
                                 '19.P6.supervised-merge-hold',
                                 '19.P6.go-grade-machinery',
                                 '19.P6.go-grade-run'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fence': ('tickets', 'tests/test_seeded_phase6_05.py'),
                        'depends': ('escape-column',),
                        'expected': 60,
                        'stuck': 90,
                        'fenced_existing': (),
                        'created': ('tests/test_seeded_phase6_05.py',),
                        'actual_render': 94408,
                        'render_overhead': -18}}

REQUIRED = {'escape-column': ('19.P6.escape-column', '19.P6.bug-gate-grammar', '19.P6.report-inbox-triage'),
 'phase6-continue-05': ('19.P6.supervised-merge-hold',
                        '19.P6.go-grade-machinery',
                        '19.P6.go-grade-run')}

ENTRY_DEPTH = {'19.P6.escape-column': {'bytes': 7224,
                         'chars': 7224,
                         'sha256': '5dd54b53e88e321bc64253a36aabcb84f95cad70aca25803c804da30963a1151',
                         'resolves': 1,
                         'gap': None,
                         'parts': {'Owner': 1081,
                                   'Records': 2749,
                                   'Observable': 1449,
                                   'Tests': 1805},
                         'missing_part_rejected': {'Owner': True,
                                                   'Records': True,
                                                   'Observable': True,
                                                   'Tests': True},
                         'tests': ('test_escape_entry_unit',
                                   'test_escape_first_parent_trailers',
                                   'test_escape_refusals',
                                   'test_resolved_bug_escape_attribution',
                                   'test_escape_attribution_retry',
                                   'test_escape_unattributed_reports',
                                   'test_escape_counts_once_per_report_ticket_surface',
                                   'test_escape_rates_and_pruning',
                                   'test_escape_report_projection',
                                   'test_status_escape_projection',
                                   'test_escape_squash_trailer_identity')},
 '19.P6.bug-gate-grammar': {'bytes': 9009,
                            'chars': 9009,
                            'sha256': '17768cdc40dc5a19993d1c9ad07b0051df3332e16b5770c2deaab9f1646c376b',
                            'resolves': 1,
                            'gap': None,
                            'parts': {'Owner': 1137,
                                      'Records': 3709,
                                      'Observable': 1348,
                                      'Tests': 2684},
                            'missing_part_rejected': {'Owner': True,
                                                      'Records': True,
                                                      'Observable': True,
                                                      'Tests': True},
                            'tests': ('test_bug_ticket_with_regression_validates',
                                      'test_grammar_refusals',
                                      'test_bug_gate_entry_units',
                                      'test_regression_overlay_proves_defect',
                                      'test_passing_new_test_is_not_bug_evidence',
                                      'test_missing_base_input_is_not_bug_evidence',
                                      'test_bug_gate_result_protocol',
                                      'test_bug_gate_indistinguishable_failures',
                                      'test_bug_gate_wrapper_execution_errors',
                                      'test_bug_gate_requires_evidence',
                                      'test_bug_gate_rejects_red_head',
                                      'test_bug_gate_refuses_invalid_carries',
                                      'test_bug_gate_execution_failure_is_closed',
                                      'test_bug_gate_check_wiring',
                                      'test_bug_gate_merge_wiring',
                                      'test_bug_gate_merge_rebase_regates',
                                      'test_bug_gate_merge_report_custody',
                                      'test_strategy_resolution_still_regates',
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
                               'tests': ('test_report_inbox_entry_units',
                                         'test_report_schema_is_closed',
                                         'test_report_evidence_bounds',
                                         'test_report_custody_precedes_enqueue',
                                         'test_report_retry_ingests_once',
                                         'test_host_report_signature',
                                         'test_report_ingested_before_pending_scan',
                                         'test_empty_box_report_intake',
                                         'test_report_consumer_is_sequential',
                                         'test_bug_report_evidence_ticket_plane_commit',
                                         'test_bug_report_text_stays_untrusted',
                                         'test_report_author_failure_is_decision',
                                         'test_report_replay_to_regression')},
 '19.P6.supervised-merge-hold': {'bytes': 12388,
                                 'chars': 12388,
                                 'sha256': '3cd14d759d766a796aff1aff764b9a9f57f20a874c2cd0f19687a745cb167013',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 1822,
                                           'Records': 3853,
                                           'Observable': 3538,
                                           'Tests': 3041},
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
                              'parts': {'Owner': 1318,
                                        'Records': 3643,
                                        'Observable': 1294,
                                        'Tests': 1767},
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
                                  'test_outbox_only_admission_records_null_commit_and_retires')}}

PLAN_SIZES = {'19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P6.escape-column': {'bytes': 7224,
                         'chars': 7224,
                         'sha256': '5dd54b53e88e321bc64253a36aabcb84f95cad70aca25803c804da30963a1151'},
 '19.P6.bug-gate-grammar': {'bytes': 9009,
                            'chars': 9009,
                            'sha256': '17768cdc40dc5a19993d1c9ad07b0051df3332e16b5770c2deaab9f1646c376b'},
 '19.P6.report-inbox-triage': {'bytes': 6470,
                               'chars': 6470,
                               'sha256': '7554e633033b41150ec51622d0537929a1773626b8f0a936893f58a38972df0a'},
 '10': {'bytes': 6636,
        'chars': 6636,
        'sha256': '3e2d0a3888b915ed8ec48f1545fbb29edc48b4e9855adb86b0a5108be443a68e'},
 '14': {'bytes': 7360,
        'chars': 7360,
        'sha256': 'f2286665a0b4e75f7141d443b4c7300e9f56eebf3c042232439c188c1f10c935'},
 '19.L': {'bytes': 20912,
          'chars': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa'},
 '19.P6': {'bytes': 11595,
           'chars': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c'},
 '13': {'bytes': 19840,
        'chars': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P6.supervised-merge-hold': {'bytes': 12388,
                                 'chars': 12388,
                                 'sha256': '3cd14d759d766a796aff1aff764b9a9f57f20a874c2cd0f19687a745cb167013'},
 '19.P6.go-grade-machinery': {'bytes': 8163,
                              'chars': 8163,
                              'sha256': '06416436a5ca1b24503215f6b9732d815df650d3d039b55418d6af6b4334bdc9'},
 '19.P6.go-grade-run': {'bytes': 3377,
                        'chars': 3377,
                        'sha256': 'b2c959c1c85c04990f5422dbd9371ca3ddc8d02287e7ce54f17516d2d070466a'}}

FILE_SIZES = {'chupa/scorecard.py': {'bytes': 3870,
                        'chars': 3870,
                        'sha256': '65df2445e2234cd58f72a60a07eb8b394764aff09feee573812a3ef69e0e0f16',
                        'delimiter_free': True},
 'chupa/git.py': {'bytes': 6640,
                  'chars': 6640,
                  'sha256': '3008d974925e672157e10dba62707480ffe5302a138110c720858a2243500239',
                  'delimiter_free': True},
 'chupa/retro.py': {'bytes': 18991,
                    'chars': 18991,
                    'sha256': '208346bbfaa9b3e4eb20accdec7431713a7a3754594ca9a9d50c94a6e309523c',
                    'delimiter_free': True},
 'chupa/__main__.py': {'bytes': 19550,
                       'chars': 19550,
                       'sha256': 'f7c61fc7900607e2a1441fd8459058ed7dd631e12336ff3ac840e2113735364a',
                       'delimiter_free': True},
 'tests/test_scorecard.py': {'bytes': 13158,
                             'chars': 13158,
                             'sha256': '9f1e03e07a2561bb079e95598a9311746696cb1601321e69f3fed1324475bff6',
                             'delimiter_free': True},
 'tests/test_git.py': {'bytes': 16617,
                       'chars': 16617,
                       'sha256': 'e2da96db7b8dc280df1b70ba91feaca7d3eb0d6c33bf399de8837b5fcbcb51ea',
                       'delimiter_free': True},
 'tests/test_retro.py': {'bytes': 19842,
                         'chars': 19842,
                         'sha256': '7b9f81319f1af055d1ac82d6882dbfb380935f091d33e608924bb97310300915',
                         'delimiter_free': True},
 'tests/test_cli.py': {'bytes': 28817,
                       'chars': 28817,
                       'sha256': '4e8e09e7963f912488436b537b32cd4cf54ae2396246fbb3f446111f54d26747',
                       'delimiter_free': True},
 'tests/test_mergequeue.py': {'bytes': 53541,
                              'chars': 53541,
                              'sha256': 'a9956ff15f4e47d463d8b4bc9373c03d1aeff89c0946bd4ccb2b4b2e0cb72793',
                              'delimiter_free': True},
 'chupa/triage.py': {'bytes': 12428,
                     'chars': 12428,
                     'sha256': 'bf23501bb011218f1850b055576e7c493d3985ddad02931450d6d72508dc34dd',
                     'delimiter_free': True},
 'tests/test_triage.py': {'bytes': 15005,
                          'chars': 15005,
                          'sha256': '14fd75fefe238d32409528f8c7e3929720ed475e62850a4359c43c06341fd605',
                          'delimiter_free': True},
 'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559',
                                      'delimiter_free': True}}

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
                                    'sha256': '4c94c271fdaf398680493b3afcc8fba59e8011306ba268e6b6c8a903b20eb915'}}

COPY_VIOLATIONS = ()

AUTHORING_TRACKED_SEEDS = ()

NEXT_ROW = {'stem': 'supervised-merge-hold',
 'deep': True,
 'depends': ('escape-column',),
 'tier': 'high',
 'effort': 'high'}

DELIVERY = {'seeds': ('tickets/escape-column/ticket.md', 'tickets/phase6-continue-05/ticket.md'),
 'commit_only': 'tests/test_seeded_phase6_04.py',
 'approval_record': 'tickets/phase6-continue-04/checks.json',
 'review': 'requisition_review',
 'lift': 'ticket-plane',
 'retry': 'retain approved bytes while ticket_sha matches; author only snagged seeds'}


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_BODY_CHARS + a["chars"] + a["render_overhead"]
            + sum(PLAN_SIZES[uid]["chars"] for uid in a["plan"])
            + sum(FILE_SIZES[path]["chars"] for path in (*a["context"], *extra)))


def test_phase6_04_exact_admission():
    assert BATCH == ("escape-column", "phase6-continue-05")
    assert PAYLOADS == ("escape-column",)
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert POSITION == 5
    assert REGISTRY_ADMISSIONS[4] == PAYLOADS
    assert REGISTRY_ADMISSIONS[POSITION:] == UNSEEDED_SUFFIX == (
        ("supervised-merge-hold",), ("go-grade-machinery", "go-grade-run"),
        ("exit-receipt-machinery",), ("phase6-exit",))
    assert ROW_CONSUMPTION == {"escape-column": ("bug-gate-grammar", "report-inbox-triage")}
    assert set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(BATCH)
    for stem in BATCH:
        t, a = _ticket(stem), AUTHORED[stem]
        assert (t.frontmatter.source, t.frontmatter.state) == ("seed", "confirmed")
        assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("medium", "medium")
        assert t.depends == a["depends"]
        assert t.plan_contract == a["plan"]
        assert t.scope_fence == a["fence"]
        assert (t.expected_minutes, t.stuck_minutes) == (60, 90) == (a["expected"], a["stuck"])
        assert t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES == 180
        assert not {s for admission in UNSEEDED_SUFFIX for s in admission} & set(t.depends)
    payload = _ticket(PAYLOADS[0])
    assert payload.depends == ("phase6-continue-04", *ROW_CONSUMPTION[payload.stem])
    assert payload.plan_contract == (
        "19.I", "19.P6.escape-column", "19.P6.bug-gate-grammar",
        "19.P6.report-inbox-triage", "10", "14")
    assert not {"19.L", "19.P6"} & set(payload.plan_contract)
    successor = _ticket(BATCH[-1])
    assert successor.depends == PAYLOADS
    assert successor.plan_contract == (
        "19.L", "19.I", "19.P6", "13", "19.P6.supervised-merge-hold",
        "19.P6.go-grade-machinery", "19.P6.go-grade-run")
    assert successor.context == ("tests/test_seeded_phase3_core.py",)
    assert successor.scope_fence == ("tickets", "tests/test_seeded_phase6_05.py")
    assert NEXT_ROW == {"stem": "supervised-merge-hold", "deep": True,
                        "depends": ("escape-column",), "tier": "high", "effort": "high"}
    raw = (ROOT / ticket_path(BATCH[-1])).read_text()
    suffix = raw.split("Position 5 carries admissions[5:]:\n", 1)[1].split("\n\nAuthor exactly", 1)[0]
    assert suffix.splitlines() == ["- [" + ", ".join(a) + "]" for a in UNSEEDED_SUFFIX]
    for fact in ("phase6-continue-06", "position 6 and admissions[6:]", "medium/medium",
                 "deep: true", "high/high", "KNOWN-HARD", "no successor",
                 "seeding.max_seeds_per_admission", "drain.max_ticket_minutes"):
        assert fact in raw


def test_phase6_04_entry_depth():
    assert REQUIRED == {
        "escape-column": ("19.P6.escape-column", "19.P6.bug-gate-grammar",
                          "19.P6.report-inbox-triage"),
        "phase6-continue-05": ("19.P6.supervised-merge-hold", "19.P6.go-grade-machinery",
                               "19.P6.go-grade-run")}
    assert set(ENTRY_DEPTH) == {uid for ids in REQUIRED.values() for uid in ids}
    for stem, ids in REQUIRED.items():
        assert len(ids) == len(set(ids))
        assert set(ids) <= set(AUTHORED[stem]["plan"])
        for uid in ids:
            d = ENTRY_DEPTH[uid]
            assert d["resolves"] == 1 and d["gap"] is None
            assert set(d["parts"]) == {"Owner", "Records", "Observable", "Tests"}
            assert all(n > 0 for n in d["parts"].values())
            assert d["missing_part_rejected"].keys() == d["parts"].keys()
            assert all(d["missing_part_rejected"].values())
            assert {k: d[k] for k in ("bytes", "chars", "sha256")} == PLAN_SIZES[uid]
            assert d["tests"]
    names = (
        "test_escape_entry_unit", "test_escape_first_parent_trailers", "test_escape_refusals",
        "test_resolved_bug_escape_attribution", "test_escape_attribution_retry",
        "test_escape_unattributed_reports", "test_escape_counts_once_per_report_ticket_surface",
        "test_escape_rates_and_pruning", "test_escape_report_projection",
        "test_status_escape_projection", "test_escape_squash_trailer_identity")
    assert ENTRY_DEPTH["19.P6.escape-column"]["tests"] == names
    acceptance = _ticket(PAYLOADS[0]).sections["Acceptance criteria"]
    assert all(name in acceptance for name in names)
    assert all(op in acceptance for op in ("required_units", "resolve_plan_contract", "entry_unit_gap"))
    successor = _ticket(BATCH[-1])
    assert all(uid in successor.plan_contract for uid in REQUIRED[successor.stem])
    raw = (ROOT / ticket_path(successor.stem)).read_text()
    for op in ("required_units", "resolve_plan_contract", "entry_unit_gap", "Owner", "Records",
               "Observable", "Tests", "both GO-grade", "before grammar and review"):
        assert op in raw
    assert not COPY_VIOLATIONS


def test_phase6_04_closure():
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert FENCE_ADDITIONS == {"escape-column": ("chupa/triage.py", "tests/test_triage.py"),
                               "phase6-continue-05": ()}
    assert set(CLOSURE_EVIDENCE) == set(FENCE_ADDITIONS[PAYLOADS[0]])
    assert all("19.L rule 5" in reason for reason in CLOSURE_EVIDENCE.values())
    assert len(CLOSURE_DECISIONS) == 8
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    for record in CLOSURE_SCAN.values():
        assert record["matched_lines"] > 0 and record["files"] > 0
        assert len(record["sha256"]) == 64
    assert set(HISTORICAL_SNAPSHOTS) == {
        "tests/test_seeded_phase3_core.py", "tests/test_seeded_phase6_core.py",
        "tests/test_seeded_phase6_01.py", "tests/test_seeded_phase6_02.py",
        "tests/test_seeded_phase6_03.py"}
    assert RENDER_BOUND_CHARS == 400_000 and REQ_RENDER_HEADROOM == 0.75
    assert (MEASURED_RENDER_TIER, MEASURED_RENDER_EFFORT) == ("max", "max")
    for stem, a in AUTHORED.items():
        t = _ticket(stem)
        assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
        assert (t.context, t.on_demand) == (a["context"], a["on_demand"])
        assert set(a["fenced_existing"]) <= set(t.context) | set(t.on_demand)
        assert not set(a["created"]) & (set(t.context) | set(t.on_demand))
        assert not set(t.context) & set(t.on_demand)
        assert not t.on_demand  # Both seeds fit with every existing fenced path embedded.
        assert not {"tests/test_seeded_phase6_04.py", "tests/test_seeded_phase6_05.py"} & set(t.context)
        assert all(FILE_SIZES[p]["delimiter_free"] and not p.startswith("specs/") for p in t.context)
        assert render_chars(stem) == a["actual_render"] <= RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM
        data = (ROOT / ticket_path(stem)).read_bytes()
        assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
            a["bytes"], a["chars"], a["sha256"])
    assert AUTHORED[PAYLOADS[0]]["created"] == ()
    assert AUTHORED[BATCH[-1]]["created"] == ("tests/test_seeded_phase6_05.py",)
    for record in (*PLAN_SIZES.values(), *FILE_SIZES.values(),
                   *HISTORICAL_SNAPSHOTS.values(), IMPLEMENT_SPEC):
        assert record["bytes"] >= record["chars"] > 0 and len(record["sha256"]) == 64
    # These callers need no edits; preserve their suites only through Verification.
    payload = _ticket(PAYLOADS[0])
    preserved = {"tests/test_inbox.py", "tests/test_author.py", "tests/test_serve.py",
                 "tests/test_status.py", "tests/test_phase5_exit.py"}
    assert not preserved & (set(payload.context) | set(payload.scope_fence))
    assert preserved <= {arg for argv in payload.verification for arg in argv}


def test_phase6_04_check_owns_seed_custody(seed_repo):
    assert AUTHORING_TRACKED_SEEDS == ()
    assert DELIVERY == {
        "seeds": tuple(ticket_path(s) for s in BATCH),
        "commit_only": "tests/test_seeded_phase6_04.py",
        "approval_record": "tickets/phase6-continue-04/checks.json",
        "review": "requisition_review", "lift": "ticket-plane",
        "retry": "retain approved bytes while ticket_sha matches; author only snagged seeds"}
    raw = (ROOT / ticket_path(BATCH[-1])).read_text()
    for fact in ("uncommitted", "requisition_review", "tickets/phase6-continue-05/checks.json",
                 "ticket-plane seed lift", "approved bytes", "ticket_sha", "snagged seeds"):
        assert fact in raw

    # Exercise the actual seeding lane with minimal contracts on disposable main.
    # Production escape/hold modules are intentionally not required by this ticket.
    seeder = "phase6-continue-04"
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
    approved, snagged = BATCH
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
        assert [(s.stem, s.verdict) for s in invoice.seeds] == [(s, "approve") for s in BATCH]
        for s in invoice.seeds:
            assert s.ticket_sha == await retry.git.rev_parse(seed_repo, "HEAD:" + ticket_path(s.stem))
        changed = await retry.git._run(seed_repo, "show", "--format=", "--name-only",
                                      lift.body["result"]["commit"])
        assert set(changed.splitlines()) == set(DELIVERY["seeds"])
        subjects = (await retry.git._run(seed_repo, "log", "--format=%s")).splitlines()
        assert subjects.count("chupa(" + seeder + "): seeds") == 1
        intake = [e for e in events if e.type == EventType.SIGNAL
                  and e.body.get("signal") == "ticket_intake" and e.body.get("seeded_by") == seeder]
        assert [e.ticket for e in intake] == list(BATCH)
        assert all(events.index(check) < events.index(lift) < events.index(e) for e in intake)
    asyncio.run(custody())
