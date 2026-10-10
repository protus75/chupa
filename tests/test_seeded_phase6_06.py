"""Phase 6 admission 6: bounded GO-grade machinery, producer and receipt seeder.

Closure, depth and render operands are immutable authoring-time snapshots.
Only ticket identity reads live files; production Check custody uses disposable main.
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

AUTHORING_HEAD = '022fd23ddbfb47b5401a02b137f80a4eab840c5d'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('go-grade-machinery', 'go-grade-run', 'phase6-continue-07')

PAYLOADS = ('go-grade-machinery', 'go-grade-run')

POSITION = 7

REGISTRY_ADMISSIONS = (('core-renderer', 'core-drift-classifier'),
 ('core-drift-activation', 'migrate-config'),
 ('host-contract-doc', 'fixture-host-scaffold'),
 ('bug-gate-grammar', 'report-inbox-triage'),
 ('escape-column',),
 ('supervised-merge-hold',),
 ('go-grade-machinery', 'go-grade-run'),
 ('exit-receipt-machinery',),
 ('phase6-exit',))

UNSEEDED_SUFFIX = (('exit-receipt-machinery',), ('phase6-exit',))

EDGES = {'go-grade-machinery': ('phase6-continue-06', 'supervised-merge-hold', 'fixture-host-scaffold'),
 'go-grade-run': ('phase6-continue-06', 'go-grade-machinery'),
 'phase6-continue-07': ('go-grade-machinery', 'go-grade-run')}

FENCE_FLOORS = {'go-grade-machinery': ('eval/harness.py',
                        'eval/fixtures/',
                        'chupa/artifacts.py',
                        'chupa/stages.py',
                        'chupa/llm.py',
                        'chupa/providers.py',
                        'tests/test_eval_harness.py',
                        'tests/test_stages.py',
                        'tests/test_providers.py',
                        'tests/test_go_grade.py'),
 'go-grade-run': ('tickets/go-grade-run/review-baseline-report.json',),
 'phase6-continue-07': ('tickets', 'tests/test_seeded_phase6_07.py')}

FENCE_ADDITIONS = {'go-grade-machinery': ('chupa/driver.py',
                        'chupa/requisition.py',
                        'tests/test_driver.py',
                        'tests/test_fixture_host.py'),
 'go-grade-run': (),
 'phase6-continue-07': ()}

CLOSURE_EVIDENCE = {'chupa/driver.py': '19.L rule 5: Driver.run constructs LLMRequest at line 299; the extended request must '
                    'carry remaining eval ceilings across retries and retain null for ordinary calls.',
 'chupa/requisition.py': '19.L rule 5: review_ticket constructs LLMRequest at line 124; its ordinary '
                         'requisition call retains the null budget.',
 'tests/test_driver.py': '19.L rule 5: test_fake_llm_refuses_when_script_exhausted constructs the positional '
                         'LLMRequest at line 357; retain ordinary null-budget construction.',
 'tests/test_fixture_host.py': '19.L rule 5: test_fixture_cli_adapter_roundtrip constructs LLMRequest at '
                               'lines 354, 369 and 372; retain scripted ordinary calls and zero-spend '
                               'behavior.'}

CLOSURE_SCAN_PATTERN = ('LLMRequest\\(|run_baseline\\(|review_stage\\(|MIN_DEFECTS|MIN_CLEAN|spike_floor|KNOWN_ARTIFACTS|__all__|not '
 'hasattr|allowlist|compose|build_serve')

CLOSURE_SCAN = {'chupa': {'matched_lines': 39,
           'files': 13,
           'sha256': 'f69ba652bb237fd28037813bca4ddec07a0f1e51b14669e41fce4d2d50bc1a8b'},
 'eval': {'matched_lines': 11,
          'files': 3,
          'sha256': 'c6ed4e58f91e0868bacaa4d07ab4d4361d9e778f7edcd5162a2057073009d90d'},
 'tests': {'matched_lines': 237,
           'files': 66,
           'sha256': 'd116d18b9d614e088d2ea8b5f66b14d2d90bc62484c26a6c592d5ad0b480cc8b'}}

CLOSURE_DECISIONS = ('19.L rule 2: test_committed_fixture_set_meets_the_spike_floor_and_differs_from_review pins 15 <= planted '
 '<= 20; preserve it and loader floors, with separate report completeness floors.',
 '19.L rule 3: this grows the active harness; no dormant production fixture or historical seeding fixture is '
 'activated or migrated.',
 '19.L rule 4: all code owners are existing modules named by the machinery entry; there is no new module.',
 '19.L rule 5: CliAdapter.invoke calls argv; subclasses ClaudeAdapter and CodexAdapter remain in the fenced '
 'chupa/providers.py. Preserve ordinary argv and invocation behavior.',
 '19.L rule 5: ProviderLLM.preflight and tests/test_providers.py::req are the other LLMRequest constructors, '
 'both already fenced.',
 'run_baseline is called by eval/harness.py::_run, tests/test_eval_harness.py::run and '
 'tests/test_watchdog_activation.py::test_eval_owned_budgets_preserve_synthetic_identities; preserve its '
 'existing parameters and scores surface. Watchdog suite is Verification-only.',
 'No public-operation allowlist or negative GO-mode assertion outside the fenced harness tests requires '
 'widening.')

REQUIRED = {'go-grade-machinery': ('19.P6.go-grade-machinery',),
 'go-grade-run': ('19.P6.go-grade-run', '19.P6.go-grade-machinery'),
 'phase6-continue-07': ('19.P6.exit-receipt-machinery',
                        '19.P6.fixture-host-scaffold',
                        '19.P6.supervised-merge-hold',
                        '19.P6.go-grade-machinery',
                        '19.P6.go-grade-run')}

ENTRY_DEPTH = {'19.P6.go-grade-machinery': {'bytes': 10834,
                              'chars': 10834,
                              'sha256': '20a0533364c7e5cae0e8cd1bf7358d41f574a6158624933b711fed49fb5a1929',
                              'resolves': 1,
                              'gap': None,
                              'parts': {'Owner': 1619, 'Records': 5048, 'Observable': 1592, 'Tests': 2434},
                              'missing_part_rejected': {'Owner': True,
                                                        'Records': True,
                                                        'Observable': True,
                                                        'Tests': True},
                              'duplicate_rejected': True,
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
                        'duplicate_rejected': True,
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
                                  'duplicate_rejected': True,
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
                                 'duplicate_rejected': True,
                                 'tests': ('test_fixture_host_entry_units',
                                           'test_fixture_profile_loads',
                                           'test_fixture_scenario_list_is_closed',
                                           'test_fixture_replay_is_deterministic',
                                           'test_fixture_regression_exists_at_base',
                                           'test_fixture_escape_is_machine_introduced',
                                           'test_fixture_reports_are_bounded',
                                           'test_fixture_cli_adapter_roundtrip',
                                           'test_fixture_scaffold_is_dormant')},
 '19.P6.supervised-merge-hold': {'bytes': 14669,
                                 'chars': 14669,
                                 'sha256': '0696b361fa55905a2bb037b29c42e1f2fd71679c3435af34fcaf8b2c471d905a',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 1822, 'Records': 4620, 'Observable': 4511, 'Tests': 3582},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'duplicate_rejected': True,
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
                                           'test_soak_uses_candidate_base_regate_receipt')}}

MACHINERY_OBLIGATIONS = (('tests/test_go_grade.py',
  'test_go_grade_entry_units',
  'required_units, unique resolve_plan_contract and all four entry_unit_gap parts'),
 ('tests/test_eval_harness.py',
  'test_go_grade_fixture_floors_and_author_separation',
  '15 planted/3 clean loader floors, separate 50 planted/15 clean completeness boundary, every class, '
  'malformed fixtures and author separation'),
 ('tests/test_eval_harness.py',
  'test_go_grade_existing_corpus_is_partial_no_go',
  'unchanged committed 18-planted/4-clean corpus produces valid partial NO_GO even with all verdicts and the '
  'graph complete'),
 ('tests/test_eval_harness.py',
  'test_go_grade_fixture_author_identity_comes_from_call',
  'scripted author provider/model/tier, existing journal/spool provenance and reviewer refusal; generated '
  'cases stay disposable'),
 ('tests/test_watchdog_activation.py',
  'test_eval_owned_budgets_preserve_synthetic_identities',
  'preserve synthetic identities and eval-owned budgets unchanged'),
 ('tests/test_eval_harness.py',
  'test_go_grade_scoring_and_partial_report',
  'caught and missed defects, false snags, absent verdicts, consistent totals, complete reports and '
  'cap-limited partial NO_GO'),
 ('tests/test_eval_harness.py',
  'test_go_grade_shared_cap_includes_retries_and_author_graph',
  'remaining USD 5.00 on every review, retry and graph call, with no spawn after exhaustion'),
 ('tests/test_eval_harness.py',
  'test_go_grade_author_graph_uses_local_prompt',
  'committed problems, resolving acyclic graph, no production Author prompt and no ticket emission'),
 ('tests/test_providers.py',
  'test_eval_budget_ceiling_before_spawn',
  'cost-reporting ceilings in argv, estimated-cost refusal before spawn and unchanged null-budget calls'),
 ('tests/test_go_grade.py',
  'test_record_go_requires_complete_floors_identity_and_operator_judgment',
  'exact 0.85/0.15 boundaries, partial/inconsistent reports, identity drift, rejected graph judgment, '
  'no-write refusal and actual matching signal identity'),
 ('tests/test_go_grade.py',
  'test_review_baseline_report_closed_schema',
  'extra fields, malformed records, inconsistent scores and signal, and partial GO refusal'),
 ('tests/test_stages.py',
  'test_review_baseline_report_registered_checks_lift',
  'canonical writer, purge before Verification, required named report, validation, sole checks custody and '
  'no machinery self-lift'))

PLAN_SIZES = {'19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P6.go-grade-machinery': {'bytes': 10834,
                              'chars': 10834,
                              'sha256': '20a0533364c7e5cae0e8cd1bf7358d41f574a6158624933b711fed49fb5a1929'},
 '12': {'bytes': 20224,
        'chars': 20224,
        'sha256': 'd3917109abd72822abd53cfadc7c74913fb6186ba72191820d0600c26cfac8cb'},
 '13': {'bytes': 19840,
        'chars': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P6.go-grade-run': {'bytes': 3377,
                        'chars': 3377,
                        'sha256': 'b2c959c1c85c04990f5422dbd9371ca3ddc8d02287e7ce54f17516d2d070466a'},
 '19.L': {'bytes': 20912,
          'chars': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa'},
 '19.P6': {'bytes': 11595,
           'chars': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c'},
 '19.P6.exit-receipt-machinery': {'bytes': 7110,
                                  'chars': 7110,
                                  'sha256': 'b8275a4dd5817f3f1ea2459500f0e1ef3c31e8a9c55ea0e8b6789fa88e8d2f2d'},
 '19.P6.fixture-host-scaffold': {'bytes': 6157,
                                 'chars': 6157,
                                 'sha256': 'f67e09cc8d94030c66a580cdd0f794e4472aa0ccde256dc823ab3c8a0e56fbfc'},
 '19.P6.supervised-merge-hold': {'bytes': 14669,
                                 'chars': 14669,
                                 'sha256': '0696b361fa55905a2bb037b29c42e1f2fd71679c3435af34fcaf8b2c471d905a'}}

FILE_SIZES = {'eval/fixtures/clean-dedupe-emails/expected.json': {'bytes': 167,
                                                     'chars': 167,
                                                     'sha256': 'deb9bb67717ad09deac3dd790d26c2c5a04de7bc220bc8a98156761e1af4f2e8',
                                                     'delimiter_free': True,
                                                     'quoted_chars': 166},
 'eval/fixtures/clean-health-endpoint/expected.json': {'bytes': 167,
                                                       'chars': 167,
                                                       'sha256': 'deb9bb67717ad09deac3dd790d26c2c5a04de7bc220bc8a98156761e1af4f2e8',
                                                       'delimiter_free': True,
                                                       'quoted_chars': 166},
 'eval/fixtures/clean-retry-config/expected.json': {'bytes': 167,
                                                    'chars': 167,
                                                    'sha256': 'deb9bb67717ad09deac3dd790d26c2c5a04de7bc220bc8a98156761e1af4f2e8',
                                                    'delimiter_free': True,
                                                    'quoted_chars': 166},
 'eval/fixtures/clean-word-count/expected.json': {'bytes': 167,
                                                  'chars': 167,
                                                  'sha256': 'deb9bb67717ad09deac3dd790d26c2c5a04de7bc220bc8a98156761e1af4f2e8',
                                                  'delimiter_free': True,
                                                  'quoted_chars': 166},
 'eval/fixtures/logic-cache-expiry/expected.json': {'bytes': 280,
                                                    'chars': 280,
                                                    'sha256': 'da7fd7d9f7c0bc5d9b2ea4373e36d57d17a15e3285b6f2cbc304070e3d49230d',
                                                    'delimiter_free': True,
                                                    'quoted_chars': 279},
 'eval/fixtures/scope-extra-flag/expected.json': {'bytes': 299,
                                                  'chars': 299,
                                                  'sha256': '283274c21485cc7fe75add3fb53dbb53b6901c967c82aa4cefb52c9a6f1a9bdd',
                                                  'delimiter_free': True,
                                                  'quoted_chars': 298},
 'eval/fixtures/logic-date-range/expected.json': {'bytes': 305,
                                                  'chars': 305,
                                                  'sha256': 'c457eca43a9a3e33f9c84fa4c1e1fff9026ee9950b5ba31a6f64514feee05c46',
                                                  'delimiter_free': True,
                                                  'quoted_chars': 304},
 'eval/fixtures/accept-csv-export/expected.json': {'bytes': 309,
                                                   'chars': 309,
                                                   'sha256': '16b6b35acb767cc989ed1df6594d680cf6b0761cb8c722093d57e1daf3df5630',
                                                   'delimiter_free': True,
                                                   'quoted_chars': 308},
 'eval/fixtures/scope-refactor/expected.json': {'bytes': 312,
                                                'chars': 312,
                                                'sha256': '947c281e7e1b07f5ec635e81024218912c907cc7a935910bfebea0997276ff64',
                                                'delimiter_free': True,
                                                'quoted_chars': 311},
 'eval/fixtures/scope-other-module/expected.json': {'bytes': 317,
                                                    'chars': 317,
                                                    'sha256': 'd8e457d23ba5af0c2c5ffe3e6c3045c590e012d4bfdb05c737aec801a9a06cbc',
                                                    'delimiter_free': True,
                                                    'quoted_chars': 316},
 'eval/fixtures/leak-log-token/expected.json': {'bytes': 318,
                                                'chars': 318,
                                                'sha256': '1523d99d811dd1aecf39b721a095306f16abfbe022c22ba97419d1a71c643382',
                                                'delimiter_free': True,
                                                'quoted_chars': 317},
 'eval/fixtures/accept-config-precedence/expected.json': {'bytes': 321,
                                                          'chars': 321,
                                                          'sha256': '5d7f8a9ad72e78003bceec50810275d77490f3f4984fa13765033cdf39a3700b',
                                                          'delimiter_free': True,
                                                          'quoted_chars': 320},
 'eval/fixtures/leak-error-message/expected.json': {'bytes': 323,
                                                    'chars': 323,
                                                    'sha256': 'abd710f21048c224dcd18c972269114447c817ee027a888daa2588cce5e69a4f',
                                                    'delimiter_free': True,
                                                    'quoted_chars': 322},
 'eval/fixtures/leak-grader-answers/expected.json': {'bytes': 326,
                                                     'chars': 326,
                                                     'sha256': '64e1d3ed332db35c1e95d8fdd252092d211119edeb6f590268f578a7acd10928',
                                                     'delimiter_free': True,
                                                     'quoted_chars': 325},
 'eval/fixtures/accept-password-policy/expected.json': {'bytes': 329,
                                                        'chars': 329,
                                                        'sha256': 'ff89a4fad95aa98ccdefed1c57e83af6192b45506714cd58ef22f2d1a6e65379',
                                                        'delimiter_free': True,
                                                        'quoted_chars': 328},
 'eval/fixtures/logic-retry-backoff/expected.json': {'bytes': 329,
                                                     'chars': 329,
                                                     'sha256': 'ec6a1d817c9c827952712f048c0a2e5d9d4a85fbf243138f644f2390ba325290',
                                                     'delimiter_free': True,
                                                     'quoted_chars': 328},
 'eval/fixtures/accept-slugify/expected.json': {'bytes': 330,
                                                'chars': 330,
                                                'sha256': 'ce458f90524274c0647478403da0ca753edecf99fd2bfa50c1ff9ffe007c29bd',
                                                'delimiter_free': True,
                                                'quoted_chars': 329},
 'eval/fixtures/leak-user-serializer/expected.json': {'bytes': 338,
                                                      'chars': 338,
                                                      'sha256': 'b9ddd0ef7991f6f6db0034b21e496b749d0a2b7e99769acfaff16c60196dfd99',
                                                      'delimiter_free': True,
                                                      'quoted_chars': 337},
 'eval/fixtures/logic-pagination/expected.json': {'bytes': 340,
                                                  'chars': 340,
                                                  'sha256': '469d55964bf4fd06a48841ada3f38801b7e487a4d52a528dba18a0b011f5159f',
                                                  'delimiter_free': True,
                                                  'quoted_chars': 339},
 'eval/fixtures/scope-bump-deps/expected.json': {'bytes': 345,
                                                 'chars': 345,
                                                 'sha256': '6f21eb824c9da6fad3aeeab6ac9d125d9743d925459331ee650ee0367ef4c70a',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 344},
 'eval/fixtures/logic-rate-limiter/expected.json': {'bytes': 346,
                                                    'chars': 346,
                                                    'sha256': '39ba9ec88e85c924547d39c4dabc5e93098d9882de3c62a540dbfc2f00e9a171',
                                                    'delimiter_free': True,
                                                    'quoted_chars': 345},
 'eval/fixtures/leak-child-env/expected.json': {'bytes': 360,
                                                'chars': 360,
                                                'sha256': '8f806c7c3e5aed047259a4a174e2bedfa2de7a519e66bfbe990d41464d059e11',
                                                'delimiter_free': True,
                                                'quoted_chars': 359},
 'eval/fixtures/scope-bump-deps/ticket.md': {'bytes': 807,
                                             'chars': 807,
                                             'sha256': '6e117cd161c7b6126e592d125bd369c33d07b633735d6276e44864cdf3e85358',
                                             'delimiter_free': True,
                                             'quoted_chars': 806},
 'eval/fixtures/scope-refactor/ticket.md': {'bytes': 827,
                                            'chars': 827,
                                            'sha256': 'ab80ab83ab9a7ddb12fa5e1e2b3e69ba1a61b95479f3fc4384917989331b21ea',
                                            'delimiter_free': True,
                                            'quoted_chars': 826},
 'eval/fixtures/clean-word-count/ticket.md': {'bytes': 828,
                                              'chars': 828,
                                              'sha256': '4dee1e063ba65adb6387be14c2cddabadae0bedfae78db281c4659b781df724d',
                                              'delimiter_free': True,
                                              'quoted_chars': 827},
 'eval/fixtures/scope-extra-flag/ticket.md': {'bytes': 872,
                                              'chars': 872,
                                              'sha256': 'c9dd6dacbb8a7c2a330e9c8eef02183fe96a55e8081da37866aa9ee24dbcfbb0',
                                              'delimiter_free': True,
                                              'quoted_chars': 871},
 'eval/fixtures/clean-retry-config/ticket.md': {'bytes': 901,
                                                'chars': 901,
                                                'sha256': 'f0af8d0cd4e077e45eb52906dae4318177358935ad7f2ae892d6bb9679952a07',
                                                'delimiter_free': True,
                                                'quoted_chars': 900},
 'eval/fixtures/leak-log-token/ticket.md': {'bytes': 935,
                                            'chars': 935,
                                            'sha256': 'af6f559f633e0a8d468b5e76b8b8393e347e9a08c62c6bc72e3ab42f87e0aa55',
                                            'delimiter_free': True,
                                            'quoted_chars': 934},
 'eval/fixtures/clean-dedupe-emails/ticket.md': {'bytes': 968,
                                                 'chars': 968,
                                                 'sha256': '5fdfd4162ba248e34f2eee6475e4b8d87fa387a77f9ae155794711a894e3d862',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 967},
 'eval/fixtures/logic-date-range/ticket.md': {'bytes': 991,
                                              'chars': 991,
                                              'sha256': '6efa783caa228a09ad6a0cc78c74bea801fb7e7790f6b8082660a83bfd722dfa',
                                              'delimiter_free': True,
                                              'quoted_chars': 990},
 'eval/fixtures/accept-slugify/ticket.md': {'bytes': 1019,
                                            'chars': 1015,
                                            'sha256': '827cafa6d6e14a0a0f4f24ccff7649a16c337b6a82ffcb1ea5b50e0294ae77bd',
                                            'delimiter_free': True,
                                            'quoted_chars': 1014},
 'eval/fixtures/leak-user-serializer/ticket.md': {'bytes': 1019,
                                                  'chars': 1019,
                                                  'sha256': '011b60415c98000f94d98c7a66922abb93479e24fd4e41f9cf113584f9f4b49a',
                                                  'delimiter_free': True,
                                                  'quoted_chars': 1018},
 'eval/fixtures/accept-password-policy/ticket.md': {'bytes': 1025,
                                                    'chars': 1025,
                                                    'sha256': '6b2e7ba23e8538b1b2d60a647e165879bf417ccb3c6054e075921b88a88b0645',
                                                    'delimiter_free': True,
                                                    'quoted_chars': 1024},
 'eval/fixtures/logic-cache-expiry/ticket.md': {'bytes': 1027,
                                                'chars': 1027,
                                                'sha256': '93f76dd534a4e5811d70b6747affcd1efdd984f585b00779512d2113a96dd834',
                                                'delimiter_free': True,
                                                'quoted_chars': 1026},
 'eval/fixtures/logic-retry-backoff/ticket.md': {'bytes': 1029,
                                                 'chars': 1029,
                                                 'sha256': '9e76911e79686a3ea584f230d5a3169f5233f48f8cbf867fef98b6ae4d569662',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 1028},
 'eval/fixtures/scope-other-module/ticket.md': {'bytes': 1030,
                                                'chars': 1030,
                                                'sha256': '6435b2287685e42149a12ac0e3c187c79f71c7ae6d6b6fe79f9251ec724df53a',
                                                'delimiter_free': True,
                                                'quoted_chars': 1029},
 'eval/fixtures/clean-health-endpoint/ticket.md': {'bytes': 1056,
                                                   'chars': 1056,
                                                   'sha256': '77395ea22c82cd0edd916efb1377417b97485a2ba462457981c9eee3585f4166',
                                                   'delimiter_free': True,
                                                   'quoted_chars': 1055},
 'eval/fixtures/leak-error-message/ticket.md': {'bytes': 1062,
                                                'chars': 1062,
                                                'sha256': 'b0c06873d62b3caa8b66e26302770b4ddb31d34a1fde10161eb844ccb25b1830',
                                                'delimiter_free': True,
                                                'quoted_chars': 1061},
 'eval/fixtures/leak-grader-answers/ticket.md': {'bytes': 1071,
                                                 'chars': 1071,
                                                 'sha256': '15ad1fb8b6e8de874ebfc6cea9217eace5861b9ed2a1401d420c1b2a7c30b80e',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 1070},
 'eval/fixtures/accept-csv-export/ticket.md': {'bytes': 1073,
                                               'chars': 1073,
                                               'sha256': '70c41ee4b06b2d4f7a346fe86456b76c64f646dcc1970cf632e972ff834068e4',
                                               'delimiter_free': True,
                                               'quoted_chars': 1072},
 'eval/fixtures/logic-pagination/ticket.md': {'bytes': 1079,
                                              'chars': 1079,
                                              'sha256': 'e27030897fd622bfa7bc28d93d70d60d36f1d012b4ec731be0d9518ec7c0b58e',
                                              'delimiter_free': True,
                                              'quoted_chars': 1078},
 'eval/fixtures/accept-config-precedence/ticket.md': {'bytes': 1131,
                                                      'chars': 1131,
                                                      'sha256': '2a730c40ce3a5219ef61235b278fe0d47ea4a7ee05d26f6853042b06b210a60d',
                                                      'delimiter_free': True,
                                                      'quoted_chars': 1130},
 'eval/fixtures/logic-rate-limiter/ticket.md': {'bytes': 1131,
                                                'chars': 1131,
                                                'sha256': 'bf49f8fe58255b8e08a9100d8ea9eb359fd5cf5f215471c0c3c9cb6d7a0f20ed',
                                                'delimiter_free': True,
                                                'quoted_chars': 1130},
 'eval/fixtures/clean-word-count/diff.patch': {'bytes': 1158,
                                               'chars': 1150,
                                               'sha256': '80b84e901c76caa5b2229c005522911684b638de1fdf767035c88b392a4063a5',
                                               'delimiter_free': True,
                                               'quoted_chars': 1149},
 'eval/fixtures/leak-child-env/ticket.md': {'bytes': 1171,
                                            'chars': 1171,
                                            'sha256': 'e8cef5e041bd52e54fa56867a1235503ad0a7d417c42b58340f81238ed05aa8f',
                                            'delimiter_free': True,
                                            'quoted_chars': 1170},
 'eval/fixtures/accept-slugify/diff.patch': {'bytes': 1477,
                                             'chars': 1474,
                                             'sha256': '6a77143a8db15faef831db58c9ba5ba542628570970382d9e77ef73bd8f088f3',
                                             'delimiter_free': True,
                                             'quoted_chars': 1473},
 'eval/fixtures/scope-bump-deps/diff.patch': {'bytes': 1736,
                                              'chars': 1736,
                                              'sha256': '3c1b82fa7d966dac664bf81cb209671a556fcc2dedefa3d2c5b60eac39263d75',
                                              'delimiter_free': True,
                                              'quoted_chars': 1735},
 'eval/fixtures/clean-dedupe-emails/diff.patch': {'bytes': 1843,
                                                  'chars': 1843,
                                                  'sha256': 'a54817d03402e090082a74e198cc7720f63cd114144be17d7dd23055298d344f',
                                                  'delimiter_free': True,
                                                  'quoted_chars': 1842},
 'eval/fixtures/scope-other-module/diff.patch': {'bytes': 1898,
                                                 'chars': 1898,
                                                 'sha256': 'c1093df31a006976d849b6b92a179562e7bccdcbd16f7a911bf29dd80d589759',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 1897},
 'eval/fixtures/scope-refactor/diff.patch': {'bytes': 1925,
                                             'chars': 1925,
                                             'sha256': '987aa88ccd0432bb10b0c9de4a06e671561d1714bbf1d54bcf4e957f7d305cbd',
                                             'delimiter_free': True,
                                             'quoted_chars': 1924},
 'eval/fixtures/leak-error-message/diff.patch': {'bytes': 2119,
                                                 'chars': 2119,
                                                 'sha256': 'fe2107140fd69d513571fdce83affd558609ed30bf41a5c38c30f1107e87f9a6',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 2118},
 'eval/fixtures/accept-password-policy/diff.patch': {'bytes': 2167,
                                                     'chars': 2167,
                                                     'sha256': '95321d5431e4eccb76321ebef0e7ad05d5b293a747ee6a9ce8e105b037a284f5',
                                                     'delimiter_free': True,
                                                     'quoted_chars': 2166},
 'eval/fixtures/logic-date-range/diff.patch': {'bytes': 2297,
                                               'chars': 2297,
                                               'sha256': '28e11813b6bd7bf713f202d2dd1bdb1dac8ca8caec27a83d4c38af7438194c2e',
                                               'delimiter_free': True,
                                               'quoted_chars': 2296},
 'eval/fixtures/clean-health-endpoint/diff.patch': {'bytes': 2471,
                                                    'chars': 2471,
                                                    'sha256': '2f8108d9acf3f5fe3399f158030671aa0a7a2742a75b3a20493196912a8af45f',
                                                    'delimiter_free': True,
                                                    'quoted_chars': 2470},
 'eval/fixtures/leak-grader-answers/diff.patch': {'bytes': 2480,
                                                  'chars': 2480,
                                                  'sha256': '4dee0cb7bea365e3d4c9aac43de5bac05f6d4875976dc0700b8fc2302bea9afc',
                                                  'delimiter_free': True,
                                                  'quoted_chars': 2479},
 'eval/fixtures/logic-cache-expiry/diff.patch': {'bytes': 2629,
                                                 'chars': 2629,
                                                 'sha256': '71590a652e501a6e092b60a2d418e54cf2b4c06e8ea90ddd98e506ba681e6e68',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 2628},
 'eval/fixtures/logic-pagination/diff.patch': {'bytes': 2676,
                                               'chars': 2676,
                                               'sha256': '77f44b97043e437ca4b83850fb81ecb1de8b83c657988c336a129b608d1a6a9c',
                                               'delimiter_free': True,
                                               'quoted_chars': 2675},
 'eval/fixtures/leak-child-env/diff.patch': {'bytes': 2677,
                                             'chars': 2677,
                                             'sha256': 'a419cab195cdca8d8ad5020c25afb6a5953e8d4c980905f2dd453136d48decf1',
                                             'delimiter_free': True,
                                             'quoted_chars': 2676},
 'eval/fixtures/leak-user-serializer/diff.patch': {'bytes': 2825,
                                                   'chars': 2825,
                                                   'sha256': '300fdec41363be69ea156054a2c097ebfc15e08d2d04f427058fd9a30c15377d',
                                                   'delimiter_free': True,
                                                   'quoted_chars': 2824},
 'chupa/llm.py': {'bytes': 2858,
                  'chars': 2858,
                  'sha256': '48ac1dbdd99e211c419e5737dffc773195e55e57db3eb229fc3e4195e5b65156',
                  'delimiter_free': True,
                  'quoted_chars': 2857},
 'eval/fixtures/clean-retry-config/diff.patch': {'bytes': 2969,
                                                 'chars': 2969,
                                                 'sha256': '83ac3de86e9ae34d8fcce1d18010b1f4884066d00a3d515dccc8c192731e3d67',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 2968},
 'eval/fixtures/accept-config-precedence/diff.patch': {'bytes': 3016,
                                                       'chars': 3016,
                                                       'sha256': '6d8ae5521eb89d3645cc0079c82e649f426b24c726476802a651dd08bf22d46f',
                                                       'delimiter_free': True,
                                                       'quoted_chars': 3015},
 'eval/fixtures/logic-retry-backoff/diff.patch': {'bytes': 3092,
                                                  'chars': 3092,
                                                  'sha256': 'e5d31ebc9205a8d65a8c46da418a10c7f17d5f2d536c760f2542744264ee81f2',
                                                  'delimiter_free': True,
                                                  'quoted_chars': 3091},
 'eval/fixtures/logic-rate-limiter/diff.patch': {'bytes': 3168,
                                                 'chars': 3168,
                                                 'sha256': '4cfdd212814692e78584fef2ed43af675f0dc6bd846d4d13a6bb1f76806dde94',
                                                 'delimiter_free': True,
                                                 'quoted_chars': 3167},
 'eval/fixtures/scope-extra-flag/diff.patch': {'bytes': 3203,
                                               'chars': 3203,
                                               'sha256': '824e19094d35afdaff86cefbfe8626a51a8926b9c09025210ecb74a34e5550e3',
                                               'delimiter_free': True,
                                               'quoted_chars': 3202},
 'eval/fixtures/accept-csv-export/diff.patch': {'bytes': 3646,
                                                'chars': 3646,
                                                'sha256': '2a133d01d0bf92a9d14a13857ea885960fb114a1bb18f9fcd1efe262365ce5cc',
                                                'delimiter_free': True,
                                                'quoted_chars': 3645},
 'eval/fixtures/leak-log-token/diff.patch': {'bytes': 3662,
                                             'chars': 3662,
                                             'sha256': 'b0a793eb1239f3f04afbdad664c9091709937e5cea629cfb78439cd1a61ed252',
                                             'delimiter_free': True,
                                             'quoted_chars': 3661},
 'tests/test_eval_harness.py': {'bytes': 8083,
                                'chars': 8083,
                                'sha256': 'a3ef759b464913e38fdf76572d9c59895d3b399eee898e4f330dc60aa6ff16e4',
                                'delimiter_free': True,
                                'quoted_chars': 8082},
 'chupa/requisition.py': {'bytes': 8648,
                          'chars': 8648,
                          'sha256': '8d9e86b5b98ffa6e5bbcc2333c2275a699fcd68546445d3e237e3ce121c28bff',
                          'delimiter_free': True,
                          'quoted_chars': 8647},
 'chupa/artifacts.py': {'bytes': 10656,
                        'chars': 10656,
                        'sha256': 'be7867f624c0b48e8ef8a1dfdf74fd653a8bc9d93ba7e06a8b4bcd470f115617',
                        'delimiter_free': True,
                        'quoted_chars': 10655},
 'tests/test_fixture_host.py': {'bytes': 20410,
                                'chars': 20410,
                                'sha256': '5e3d15f79167d76a1dad89b127e4be7f3bbdd0e70ac6e281847d4e484019d0d6',
                                'delimiter_free': True,
                                'quoted_chars': 20409},
 'tests/test_driver.py': {'bytes': 20801,
                          'chars': 20801,
                          'sha256': '9a7f00c3da608abc6162f41f38ed2a8d659cd96ba37600329bb7d90353e42dcf',
                          'delimiter_free': True,
                          'quoted_chars': 20800},
 'eval/harness.py': {'bytes': 21387,
                     'chars': 21387,
                     'sha256': '77b68a5e79f964cfdb2ba1359af29a39c506fb28802a89a6372afc39200ee831',
                     'delimiter_free': True,
                     'quoted_chars': 21386},
 'chupa/driver.py': {'bytes': 23810,
                     'chars': 23810,
                     'sha256': '1d5cceec4544c4bd969b7fe2e0a76cd6c73277d104fb627540a2f5f631efb81c',
                     'delimiter_free': True,
                     'quoted_chars': 23809},
 'chupa/providers.py': {'bytes': 28092,
                        'chars': 28092,
                        'sha256': '772af76f8d83e21607c46d0519a7cb4316839244df9d9187e4213b231ebd3398',
                        'delimiter_free': True,
                        'quoted_chars': 28091},
 'tests/test_stages.py': {'bytes': 35071,
                          'chars': 35071,
                          'sha256': '1df88b972710bc3cc194a8be20777da81483a76265af2b98a68b941861934acd',
                          'delimiter_free': True,
                          'quoted_chars': 35070},
 'tests/test_providers.py': {'bytes': 39372,
                             'chars': 39370,
                             'sha256': '73356f0f84320307a4da456ac2e8cc0cc8a2b54c770fecc64ca64e5b330a3796',
                             'delimiter_free': True,
                             'quoted_chars': 39369},
 'chupa/stages.py': {'bytes': 73280,
                     'chars': 73280,
                     'sha256': 'd53833839369fb1cc822d7db522b0ffeb4ee515fbc8f557c7bee359bb08f879b',
                     'delimiter_free': True,
                     'quoted_chars': 73279},
 'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559',
                                      'delimiter_free': True,
                                      'quoted_chars': 5424}}

HISTORICAL_SNAPSHOTS = {'tests/test_seeded_phase6_01.py': {'bytes': 57492,
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
                                    'sha256': 'c2456fe6ee2160dcb851760ec587ec4a75b4227a31e9d87a2860af41939f71ca'},
 'tests/test_seeded_phase6_05.py': {'bytes': 55987,
                                    'chars': 55987,
                                    'sha256': 'e4b6178af2eaa5ad6cd3b4e5aebec115d1c4f35a89412e0704bb8998e5757a1d'},
 'tests/test_seeded_phase6_core.py': {'bytes': 35196,
                                      'chars': 35196,
                                      'sha256': '7606a766e009e53284c8154c971847ed5f58b20dfff3f945266d35a324870cae'},
 'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559'}}

AUTHORED = {'go-grade-machinery': {'bytes': 9532,
                        'chars': 9532,
                        'sha256': 'a0cf4742a9f40290b6ffc3c046dea88c3e490bb52bbef2a876715c048849f3a3',
                        'plan': ('19.I', '19.P6.go-grade-machinery', '12', '13'),
                        'context': ('eval/fixtures/clean-dedupe-emails/expected.json',
                                    'eval/fixtures/clean-health-endpoint/expected.json',
                                    'eval/fixtures/clean-retry-config/expected.json',
                                    'eval/fixtures/clean-word-count/expected.json',
                                    'eval/fixtures/logic-cache-expiry/expected.json',
                                    'eval/fixtures/scope-extra-flag/expected.json',
                                    'eval/fixtures/logic-date-range/expected.json',
                                    'eval/fixtures/accept-csv-export/expected.json',
                                    'eval/fixtures/scope-refactor/expected.json',
                                    'eval/fixtures/scope-other-module/expected.json',
                                    'eval/fixtures/leak-log-token/expected.json',
                                    'eval/fixtures/accept-config-precedence/expected.json',
                                    'eval/fixtures/leak-error-message/expected.json',
                                    'eval/fixtures/leak-grader-answers/expected.json',
                                    'eval/fixtures/accept-password-policy/expected.json',
                                    'eval/fixtures/logic-retry-backoff/expected.json',
                                    'eval/fixtures/accept-slugify/expected.json',
                                    'eval/fixtures/leak-user-serializer/expected.json',
                                    'eval/fixtures/logic-pagination/expected.json',
                                    'eval/fixtures/scope-bump-deps/expected.json',
                                    'eval/fixtures/logic-rate-limiter/expected.json',
                                    'eval/fixtures/leak-child-env/expected.json',
                                    'eval/fixtures/scope-bump-deps/ticket.md',
                                    'eval/fixtures/scope-refactor/ticket.md',
                                    'eval/fixtures/clean-word-count/ticket.md',
                                    'eval/fixtures/scope-extra-flag/ticket.md',
                                    'eval/fixtures/clean-retry-config/ticket.md',
                                    'eval/fixtures/leak-log-token/ticket.md',
                                    'eval/fixtures/clean-dedupe-emails/ticket.md',
                                    'eval/fixtures/logic-date-range/ticket.md',
                                    'eval/fixtures/accept-slugify/ticket.md',
                                    'eval/fixtures/leak-user-serializer/ticket.md',
                                    'eval/fixtures/accept-password-policy/ticket.md',
                                    'eval/fixtures/logic-cache-expiry/ticket.md',
                                    'eval/fixtures/logic-retry-backoff/ticket.md',
                                    'eval/fixtures/scope-other-module/ticket.md',
                                    'eval/fixtures/clean-health-endpoint/ticket.md',
                                    'eval/fixtures/leak-error-message/ticket.md',
                                    'eval/fixtures/leak-grader-answers/ticket.md',
                                    'eval/fixtures/accept-csv-export/ticket.md',
                                    'eval/fixtures/logic-pagination/ticket.md',
                                    'eval/fixtures/accept-config-precedence/ticket.md',
                                    'eval/fixtures/logic-rate-limiter/ticket.md',
                                    'eval/fixtures/clean-word-count/diff.patch',
                                    'eval/fixtures/leak-child-env/ticket.md',
                                    'eval/fixtures/accept-slugify/diff.patch',
                                    'eval/fixtures/scope-bump-deps/diff.patch',
                                    'eval/fixtures/clean-dedupe-emails/diff.patch',
                                    'eval/fixtures/scope-other-module/diff.patch',
                                    'eval/fixtures/scope-refactor/diff.patch',
                                    'eval/fixtures/leak-error-message/diff.patch',
                                    'eval/fixtures/accept-password-policy/diff.patch',
                                    'eval/fixtures/logic-date-range/diff.patch',
                                    'eval/fixtures/clean-health-endpoint/diff.patch',
                                    'eval/fixtures/leak-grader-answers/diff.patch',
                                    'eval/fixtures/logic-cache-expiry/diff.patch',
                                    'eval/fixtures/logic-pagination/diff.patch',
                                    'eval/fixtures/leak-child-env/diff.patch',
                                    'eval/fixtures/leak-user-serializer/diff.patch',
                                    'chupa/llm.py',
                                    'eval/fixtures/clean-retry-config/diff.patch',
                                    'eval/fixtures/accept-config-precedence/diff.patch',
                                    'eval/fixtures/logic-retry-backoff/diff.patch',
                                    'eval/fixtures/logic-rate-limiter/diff.patch',
                                    'eval/fixtures/scope-extra-flag/diff.patch',
                                    'eval/fixtures/accept-csv-export/diff.patch',
                                    'eval/fixtures/leak-log-token/diff.patch',
                                    'tests/test_eval_harness.py',
                                    'chupa/requisition.py',
                                    'chupa/artifacts.py',
                                    'tests/test_fixture_host.py',
                                    'tests/test_driver.py',
                                    'eval/harness.py',
                                    'chupa/driver.py',
                                    'chupa/providers.py'),
                        'on_demand': ('tests/test_stages.py', 'tests/test_providers.py', 'chupa/stages.py'),
                        'fenced_existing': ('eval/harness.py',
                                            'eval/fixtures/accept-config-precedence/diff.patch',
                                            'eval/fixtures/accept-config-precedence/expected.json',
                                            'eval/fixtures/accept-config-precedence/ticket.md',
                                            'eval/fixtures/accept-csv-export/diff.patch',
                                            'eval/fixtures/accept-csv-export/expected.json',
                                            'eval/fixtures/accept-csv-export/ticket.md',
                                            'eval/fixtures/accept-password-policy/diff.patch',
                                            'eval/fixtures/accept-password-policy/expected.json',
                                            'eval/fixtures/accept-password-policy/ticket.md',
                                            'eval/fixtures/accept-slugify/diff.patch',
                                            'eval/fixtures/accept-slugify/expected.json',
                                            'eval/fixtures/accept-slugify/ticket.md',
                                            'eval/fixtures/clean-dedupe-emails/diff.patch',
                                            'eval/fixtures/clean-dedupe-emails/expected.json',
                                            'eval/fixtures/clean-dedupe-emails/ticket.md',
                                            'eval/fixtures/clean-health-endpoint/diff.patch',
                                            'eval/fixtures/clean-health-endpoint/expected.json',
                                            'eval/fixtures/clean-health-endpoint/ticket.md',
                                            'eval/fixtures/clean-retry-config/diff.patch',
                                            'eval/fixtures/clean-retry-config/expected.json',
                                            'eval/fixtures/clean-retry-config/ticket.md',
                                            'eval/fixtures/clean-word-count/diff.patch',
                                            'eval/fixtures/clean-word-count/expected.json',
                                            'eval/fixtures/clean-word-count/ticket.md',
                                            'eval/fixtures/leak-child-env/diff.patch',
                                            'eval/fixtures/leak-child-env/expected.json',
                                            'eval/fixtures/leak-child-env/ticket.md',
                                            'eval/fixtures/leak-error-message/diff.patch',
                                            'eval/fixtures/leak-error-message/expected.json',
                                            'eval/fixtures/leak-error-message/ticket.md',
                                            'eval/fixtures/leak-grader-answers/diff.patch',
                                            'eval/fixtures/leak-grader-answers/expected.json',
                                            'eval/fixtures/leak-grader-answers/ticket.md',
                                            'eval/fixtures/leak-log-token/diff.patch',
                                            'eval/fixtures/leak-log-token/expected.json',
                                            'eval/fixtures/leak-log-token/ticket.md',
                                            'eval/fixtures/leak-user-serializer/diff.patch',
                                            'eval/fixtures/leak-user-serializer/expected.json',
                                            'eval/fixtures/leak-user-serializer/ticket.md',
                                            'eval/fixtures/logic-cache-expiry/diff.patch',
                                            'eval/fixtures/logic-cache-expiry/expected.json',
                                            'eval/fixtures/logic-cache-expiry/ticket.md',
                                            'eval/fixtures/logic-date-range/diff.patch',
                                            'eval/fixtures/logic-date-range/expected.json',
                                            'eval/fixtures/logic-date-range/ticket.md',
                                            'eval/fixtures/logic-pagination/diff.patch',
                                            'eval/fixtures/logic-pagination/expected.json',
                                            'eval/fixtures/logic-pagination/ticket.md',
                                            'eval/fixtures/logic-rate-limiter/diff.patch',
                                            'eval/fixtures/logic-rate-limiter/expected.json',
                                            'eval/fixtures/logic-rate-limiter/ticket.md',
                                            'eval/fixtures/logic-retry-backoff/diff.patch',
                                            'eval/fixtures/logic-retry-backoff/expected.json',
                                            'eval/fixtures/logic-retry-backoff/ticket.md',
                                            'eval/fixtures/scope-bump-deps/diff.patch',
                                            'eval/fixtures/scope-bump-deps/expected.json',
                                            'eval/fixtures/scope-bump-deps/ticket.md',
                                            'eval/fixtures/scope-extra-flag/diff.patch',
                                            'eval/fixtures/scope-extra-flag/expected.json',
                                            'eval/fixtures/scope-extra-flag/ticket.md',
                                            'eval/fixtures/scope-other-module/diff.patch',
                                            'eval/fixtures/scope-other-module/expected.json',
                                            'eval/fixtures/scope-other-module/ticket.md',
                                            'eval/fixtures/scope-refactor/diff.patch',
                                            'eval/fixtures/scope-refactor/expected.json',
                                            'eval/fixtures/scope-refactor/ticket.md',
                                            'chupa/artifacts.py',
                                            'chupa/stages.py',
                                            'chupa/llm.py',
                                            'chupa/providers.py',
                                            'tests/test_eval_harness.py',
                                            'tests/test_stages.py',
                                            'tests/test_providers.py',
                                            'chupa/driver.py',
                                            'chupa/requisition.py',
                                            'tests/test_driver.py',
                                            'tests/test_fixture_host.py'),
                        'created': ('tests/test_go_grade.py',),
                        'actual_render': 299327,
                        'render_overhead': 3490,
                        'embedding_overhead': {'tests/test_stages.py': 27,
                                               'tests/test_providers.py': 30,
                                               'chupa/stages.py': 22},
                        'on_demand_embedding': {'tests/test_stages.py': 334425,
                                                'tests/test_providers.py': 338727,
                                                'chupa/stages.py': 372629}},
 'go-grade-run': {'bytes': 2920,
                  'chars': 2920,
                  'sha256': 'dfdfc2c36e76b60ea6ad5686b313799ea8390caaf22b9fc1405c20347312648d',
                  'plan': ('19.I', '19.P6.go-grade-run', '19.P6.go-grade-machinery'),
                  'context': ('eval/harness.py', 'chupa/artifacts.py', 'chupa/stages.py'),
                  'on_demand': (),
                  'fenced_existing': (),
                  'created': ('tickets/go-grade-run/review-baseline-report.json',),
                  'actual_render': 129462,
                  'render_overhead': 12,
                  'embedding_overhead': {},
                  'on_demand_embedding': {}},
 'phase6-continue-07': {'bytes': 5420,
                        'chars': 5420,
                        'sha256': '03ec18d3896a7e28bddd9e3c5aeda6cc69cc9c1ed0dd9f8a18f925a2e702cc57',
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
                        'created': ('tests/test_seeded_phase6_07.py',),
                        'actual_render': 112317,
                        'render_overhead': -18,
                        'embedding_overhead': {},
                        'on_demand_embedding': {}}}

IMPLEMENT_SPEC = {'bytes': 5306, 'chars': 5306, 'sha256': 'f5d3ba603570a56f661a24d7a52d7e4543c0d003a82e36d664f5ef73f3599ddb'}

IMPLEMENT_BODY_CHARS = 5185

RENDER_BOUND_CHARS = 400000

REQ_RENDER_HEADROOM = 0.75

MEASURED_RENDER_TIER = 'max'

MEASURED_RENDER_EFFORT = 'max'

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

COPY_VIOLATIONS = ()

AUTHORING_TRACKED_SEEDS = ()

DELIVERY = {'seeds': ('tickets/go-grade-machinery/ticket.md',
           'tickets/go-grade-run/ticket.md',
           'tickets/phase6-continue-07/ticket.md'),
 'commit_only': 'tests/test_seeded_phase6_06.py',
 'approval_record': 'tickets/phase6-continue-06/checks.json',
 'review': 'requisition_review',
 'lift': 'ticket-plane',
 'retry': 'retain approved bytes while ticket_sha matches; author only snagged seeds'}

def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, BATCH)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_BODY_CHARS + a["chars"] + a["render_overhead"]
            + sum(PLAN_SIZES[u]["chars"] for u in a["plan"])
            + sum(FILE_SIZES[p]["chars"] for p in a["context"])
            + sum(FILE_SIZES[p]["chars"] + a["embedding_overhead"][p] for p in extra))


def test_phase6_06_exact_admission():
    assert BATCH == ("go-grade-machinery", "go-grade-run", "phase6-continue-07")
    assert PAYLOADS == REGISTRY_ADMISSIONS[6] == BATCH[:2]
    assert POSITION == 7
    assert UNSEEDED_SUFFIX == REGISTRY_ADMISSIONS[POSITION:] == (
        ("exit-receipt-machinery",), ("phase6-exit",))
    assert len(set(BATCH)) == len(BATCH) == MAX_SEEDS_PER_ADMISSION == 3
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)
    assert EDGES == {
        "go-grade-machinery": ("phase6-continue-06", "supervised-merge-hold", "fixture-host-scaffold"),
        "go-grade-run": ("phase6-continue-06", "go-grade-machinery"),
        "phase6-continue-07": PAYLOADS}
    for s in BATCH:
        t = _ticket(s)
        assert (t.frontmatter.source, t.frontmatter.state) == ("seed", "confirmed")
        assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("medium", "medium")
        assert t.depends == EDGES[s]
        assert t.plan_contract == AUTHORED[s]["plan"]
        assert 0 < t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES
        assert not set(t.depends) & {s for a in UNSEEDED_SUFFIX for s in a}
    assert _ticket(PAYLOADS[0]).plan_contract == ("19.I", "19.P6.go-grade-machinery", "12", "13")
    assert _ticket(PAYLOADS[1]).plan_contract == (
        "19.I", "19.P6.go-grade-run", "19.P6.go-grade-machinery")
    for s in PAYLOADS:
        assert "19.L" not in _ticket(s).plan_contract and "19.P6" not in _ticket(s).plan_contract
    t = _ticket(BATCH[-1])
    assert t.scope_fence == ("tickets", "tests/test_seeded_phase6_07.py")
    assert t.context == ("tests/test_seeded_phase3_core.py",)
    assert t.plan_contract == (
        "19.L", "19.I", "19.P6", "13", "19.P6.exit-receipt-machinery",
        "19.P6.fixture-host-scaffold", "19.P6.supervised-merge-hold",
        "19.P6.go-grade-machinery", "19.P6.go-grade-run")
    scope = t.sections["Scope in / Scope out"]
    suffix = scope.split("Position 7 carries admissions[7:]:\n", 1)[1].split("\n\nAuthor exactly", 1)[0]
    assert suffix.splitlines() == ["- [" + ", ".join(a) + "]" for a in UNSEEDED_SUFFIX]
    for fact in ("Author exactly exit-receipt-machinery and phase6-continue-08",
                 "position 8 and admissions[8:]", "depends on exit-receipt-machinery",
                 "deep: true", "high/high", "medium/medium", "KNOWN-HARD", "no successor",
                 "seeding.max_seeds_per_admission", "drain.max_ticket_minutes", "two seeds"):
        assert fact in scope


def test_phase6_06_entry_depth():
    assert REQUIRED == {
        "go-grade-machinery": ("19.P6.go-grade-machinery",),
        "go-grade-run": ("19.P6.go-grade-run", "19.P6.go-grade-machinery"),
        "phase6-continue-07": ("19.P6.exit-receipt-machinery", "19.P6.fixture-host-scaffold",
                               "19.P6.supervised-merge-hold", "19.P6.go-grade-machinery",
                               "19.P6.go-grade-run")}
    assert set(ENTRY_DEPTH) == {u for units in REQUIRED.values() for u in units}
    for s, units in REQUIRED.items():
        assert len(units) == len(set(units))
        assert set(units) <= set(AUTHORED[s]["plan"])
        for u in units:
            d = ENTRY_DEPTH[u]
            assert d["resolves"] == 1 and d["gap"] is None and d["duplicate_rejected"]
            assert set(d["parts"]) == {"Owner", "Records", "Observable", "Tests"}
            assert all(n > 0 for n in d["parts"].values())
            assert d["missing_part_rejected"].keys() == d["parts"].keys()
            assert all(d["missing_part_rejected"].values())
            assert {k: d[k] for k in ("bytes", "chars", "sha256")} == PLAN_SIZES[u]
            assert d["tests"]
    names = (
        'test_go_grade_entry_units',
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
        'test_review_baseline_report_registered_checks_lift',
    )
    assert ENTRY_DEPTH["19.P6.go-grade-machinery"]["tests"] == names
    assert tuple(n for _, n, _ in MACHINERY_OBLIGATIONS) == names
    machinery = _ticket(PAYLOADS[0])
    scope = machinery.sections["Scope in / Scope out"]
    for fact in ("Preserve the committed 22 review fixtures", "byte-for-byte",
                 "loader floors at 15 planted and 3 clean",
                 "separate 50-planted/15-clean completeness requirements",
                 "partial NO_GO", "later operator-authored upkeep tickets",
                 "Scripted authored cases stay disposable"):
        assert fact in scope
    for p, n, summary in MACHINERY_OBLIGATIONS:
        assert p + "::" + n in machinery.sections["Acceptance criteria"]
        assert summary in machinery.sections["Acceptance criteria"]
        assert (p in machinery.scope_fence) == (p != "tests/test_watchdog_activation.py")
        assert ("uv", "run", "pytest", "-q", p) in machinery.verification
    producer = _ticket(PAYLOADS[1])
    assert producer.scope_fence == ("tickets/go-grade-run/review-baseline-report.json",)
    assert producer.context == ("eval/harness.py", "chupa/artifacts.py", "chupa/stages.py")
    assert producer.on_demand == ()
    assert producer.verification == (
        ("uv", "run", "pytest", "tests/test_eval_harness.py", "tests/test_go_grade.py",
         "tests/test_stages.py", "tests/test_merge.py"),
        ("uv", "run", "python", "-m", "eval.harness", "run", "--out",
         "tickets/go-grade-run/review-baseline-report.json"))
    for n in ENTRY_DEPTH["19.P6.go-grade-run"]["tests"]:
        assert n in producer.sections["Acceptance criteria"]
    assert "owns no code, schema, registration or test" in producer.sections["Scope in / Scope out"]
    assert "do not pass --record-go" in producer.sections["Scope in / Scope out"]
    scope = _ticket(BATCH[-1]).sections["Scope in / Scope out"]
    for fact in ("required_units", "resolve_plan_contract", "entry_unit_gap", "Owner", "Records",
                 "Observable", "Tests", "before grammar and review", "fixture-host-scaffold",
                 "supervised-merge-hold", "go-grade-machinery", "go-grade-run",
                 "every named machinery Tests obligation", "terminal phase6-exit contract"):
        assert fact in scope
    assert not COPY_VIOLATIONS


def test_phase6_06_closure():
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert FENCE_ADDITIONS == {
        "go-grade-machinery": ("chupa/driver.py", "chupa/requisition.py",
                               "tests/test_driver.py", "tests/test_fixture_host.py"),
        "go-grade-run": (), "phase6-continue-07": ()}
    assert set(CLOSURE_EVIDENCE) == set(FENCE_ADDITIONS[PAYLOADS[0]])
    assert all("19.L rule 5" in e and "LLMRequest" in e for e in CLOSURE_EVIDENCE.values())
    assert "Driver.run" in CLOSURE_EVIDENCE["chupa/driver.py"]
    assert "review_ticket" in CLOSURE_EVIDENCE["chupa/requisition.py"]
    assert "test_fake_llm_refuses_when_script_exhausted" in CLOSURE_EVIDENCE["tests/test_driver.py"]
    assert "test_fixture_cli_adapter_roundtrip" in CLOSURE_EVIDENCE["tests/test_fixture_host.py"]
    assert len(CLOSURE_DECISIONS) == 7
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    for record in CLOSURE_SCAN.values():
        assert record["matched_lines"] > 0 and record["files"] > 0
        assert len(record["sha256"]) == 64
    assert set(HISTORICAL_SNAPSHOTS) == {
        "tests/test_seeded_phase3_core.py", "tests/test_seeded_phase6_core.py",
        *(f"tests/test_seeded_phase6_{n:02d}.py" for n in range(1, 6))}
    assert HISTORICAL_SNAPSHOTS["tests/test_seeded_phase3_core.py"]["sha256"] == (
        FILE_SIZES["tests/test_seeded_phase3_core.py"]["sha256"])
    assert (RENDER_BOUND_CHARS, REQ_RENDER_HEADROOM) == (400_000, 0.75)
    assert (MEASURED_RENDER_TIER, MEASURED_RENDER_EFFORT) == ("max", "max")
    for s, a in AUTHORED.items():
        t = _ticket(s)
        assert t.scope_fence == (*FENCE_FLOORS[s], *FENCE_ADDITIONS[s])
        assert (t.context, t.on_demand) == (a["context"], a["on_demand"])
        assert set(a["fenced_existing"]) <= set(t.context) | set(t.on_demand)
        assert not set(t.context) & set(t.on_demand)
        assert not set(a["created"]) & (set(t.context) | set(t.on_demand))
        assert all(p not in t.scope_fence for p in HISTORICAL_SNAPSHOTS)
        assert not {"tests/test_seeded_phase6_06.py", "tests/test_seeded_phase6_07.py",
                    "tests/test_go_grade.py"} & set(t.context)
        assert all(FILE_SIZES[p]["delimiter_free"] and not p.startswith("specs/") for p in t.context)
        assert render_chars(s) == a["actual_render"] <= RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM
        assert set(a["on_demand_embedding"]) == set(a["embedding_overhead"]) == set(t.on_demand)
        for p in t.on_demand:
            assert p in a["fenced_existing"]
            assert render_chars(s, (p,)) == a["on_demand_embedding"][p] > 300_000
        data = (ROOT / ticket_path(s)).read_bytes()
        assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
            a["bytes"], a["chars"], a["sha256"])
    assert AUTHORED[PAYLOADS[0]]["created"] == ("tests/test_go_grade.py",)
    assert AUTHORED[PAYLOADS[1]]["created"] == ("tickets/go-grade-run/review-baseline-report.json",)
    assert AUTHORED[BATCH[-1]]["created"] == ("tests/test_seeded_phase6_07.py",)
    for r in (*PLAN_SIZES.values(), *FILE_SIZES.values(), *HISTORICAL_SNAPSHOTS.values(), IMPLEMENT_SPEC):
        assert r["bytes"] >= r["chars"] > 0 and len(r["sha256"]) == 64
    preserved = {"tests/test_watchdog_activation.py", "tests/test_baseline.py",
                 "tests/test_merge.py", "tests/test_seed_path.py", "tests/test_plan_lint.py"}
    machine = _ticket(PAYLOADS[0])
    assert not preserved & (set(machine.context) | set(machine.on_demand) | set(machine.scope_fence))
    assert preserved <= {arg for argv in machine.verification for arg in argv}


def test_phase6_06_check_owns_seed_custody(seed_repo):
    assert AUTHORING_TRACKED_SEEDS == ()
    assert DELIVERY == {
        "seeds": tuple(ticket_path(s) for s in BATCH),
        "commit_only": "tests/test_seeded_phase6_06.py",
        "approval_record": "tickets/phase6-continue-06/checks.json",
        "review": "requisition_review", "lift": "ticket-plane",
        "retry": "retain approved bytes while ticket_sha matches; author only snagged seeds"}
    successor = (ROOT / ticket_path(BATCH[-1])).read_text()
    for fact in ("uncommitted", "requisition_review", "tickets/phase6-continue-07/checks.json",
                 "ticket-plane seed lift", "approved bytes", "ticket_sha", "snagged seeds"):
        assert fact in successor

    seeder = "phase6-continue-06"
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
    # Match this retry's actual approved producer and successor; only machinery is authored again.
    approved = BATCH[1:]
    snagged = BATCH[0]
    snag = {"code": "scope", "message": "missing test", "paved_road": "name the test",
            "kind": "authoring_error"}

    def implement_seeds(ctx, emitted, *, retry=False):
        async def act(request):
            assert request.surface == "implement" and request.worktree is not None
            if retry:
                assert "## Approved seeds (keep verbatim)" in request.rendered
                assert all((request.worktree / ticket_path(s)).read_text() == seeds[s] for s in approved)
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
                             requisition("approve"), requisition("approve"), diagnosis_reply()])
    ctx.driver.llm.emit = implement_seeds(ctx, seeds)
    assert asyncio.run(drive(ctx, ticket)) == "gate_failed"
    receipt = Invoice.model_validate_json((seed_repo / DELIVERY["approval_record"]).read_text())
    assert [(s.stem, s.verdict) for s in receipt.seeds] == [
        (snagged, "snag"), *((s, "approve") for s in approved)]
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
    assert "missing test" in requests[0].rendered and "tested." in requests[0].rendered
    assert all((seed_repo / ticket_path(s)).read_text() == seeds[s] for s in approved)
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
