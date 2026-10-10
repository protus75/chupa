"""Phase 6 admission 3: immutable authoring snapshots and direct seed identity.

Only ticket identity is read live, following the merged Phase 3 core idiom.
Plan, source sizes, depth and closure evidence are fixed authoring-time operands.
"""
import hashlib
from pathlib import Path

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]

AUTHORING_HEAD = 'db6a9d568a390f746cdddc037b775c7a8b3a2492'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('bug-gate-grammar', 'report-inbox-triage', 'phase6-continue-04')

PAYLOADS = ('bug-gate-grammar', 'report-inbox-triage')

POSITION = 4

UNSEEDED_SUFFIX = (('escape-column',),
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

ROW_CONSUMPTION = {'bug-gate-grammar': ('fixture-host-scaffold',), 'report-inbox-triage': ('bug-gate-grammar',)}

FENCE_FLOORS = {'bug-gate-grammar': ('chupa/tickets.py',
                      'chupa/gates.py',
                      'chupa/stages.py',
                      'tests/test_tickets.py',
                      'tests/test_gates.py',
                      'tests/test_bug_gate.py'),
 'report-inbox-triage': ('chupa/inbox.py',
                         'chupa/box.py',
                         'chupa/triage.py',
                         'chupa/author.py',
                         'chupa/daemon.py',
                         'chupa/serve.py',
                         'tests/test_box.py',
                         'tests/test_triage.py',
                         'tests/test_author.py',
                         'tests/test_serve.py',
                         'tests/test_inbox.py'),
 'phase6-continue-04': ('tickets', 'tests/test_seeded_phase6_04.py')}

FENCE_ADDITIONS = {'bug-gate-grammar': ('tests/test_mergequeue.py', 'tests/test_serve.py'),
 'report-inbox-triage': (),
 'phase6-continue-04': ()}

CLOSURE_EVIDENCE = {'bug-gate-grammar': {'tests/test_mergequeue.py': '19.L rule 2: '
                                                  'test_strategy_resolution_still_regates at line '
                                                  '676 pins integration gates without '
                                                  'bug_evidence; CHECK_GATES registration changes '
                                                  'its exact list.',
                      'tests/test_serve.py': '19.L rule 2: '
                                             'test_serve_conflict_handoff_runs_after_admission_unwinds '
                                             'at line 1307 pins integration gates without '
                                             'bug_evidence; CHECK_GATES registration changes its '
                                             'exact list.'},
 'report-inbox-triage': {},
 'phase6-continue-04': {}}

AUTHORED = {'bug-gate-grammar': {'bytes': 5109,
                      'chars': 5109,
                      'sha256': '4e78c895341c45c729a15a30acaf32750dc958ba8e92c247b30693feac0afbb3',
                      'plan': ('19.I', '19.P6.bug-gate-grammar', '7', '13'),
                      'context': ('chupa/tickets.py',
                                  'chupa/gates.py',
                                  'chupa/stages.py',
                                  'tests/test_tickets.py',
                                  'tests/test_gates.py',
                                  'tests/test_mergequeue.py',
                                  'chupa/merge.py',
                                  'chupa/mergequeue.py',
                                  'chupa/git.py',
                                  'chupa/seams.py',
                                  'hosts/fixture/scaffold.py',
                                  'hosts/fixture/regression_test.py'),
                      'on_demand': ('tests/test_serve.py',),
                      'fence': ('chupa/tickets.py',
                                'chupa/gates.py',
                                'chupa/stages.py',
                                'tests/test_tickets.py',
                                'tests/test_gates.py',
                                'tests/test_bug_gate.py',
                                'tests/test_mergequeue.py',
                                'tests/test_serve.py'),
                      'depends': ('phase6-continue-03', 'fixture-host-scaffold'),
                      'expected': 60,
                      'stuck': 90,
                      'fenced_existing': ('chupa/tickets.py',
                                          'chupa/gates.py',
                                          'chupa/stages.py',
                                          'tests/test_tickets.py',
                                          'tests/test_gates.py',
                                          'tests/test_mergequeue.py',
                                          'tests/test_serve.py'),
                      'created': ('tests/test_bug_gate.py',),
                      'actual_render': 282659,
                      'render_overhead': 252,
                      'on_demand_embedding': {'tests/test_serve.py': 357955}},
 'report-inbox-triage': {'bytes': 4688,
                         'chars': 4688,
                         'sha256': '89ff882be844b8bdb397b197cefe68ca0aaa080a6e618e489d29eee34b9f7fb8',
                         'plan': ('19.I',
                                  '19.P6.report-inbox-triage',
                                  '19.P6.bug-gate-grammar',
                                  '12'),
                         'context': ('chupa/box.py',
                                     'chupa/triage.py',
                                     'chupa/author.py',
                                     'chupa/daemon.py',
                                     'chupa/serve.py',
                                     'tests/test_box.py',
                                     'tests/test_triage.py',
                                     'tests/test_author.py',
                                     'tests/test_serve.py',
                                     'chupa/tickets.py',
                                     'chupa/seams.py',
                                     'hosts/fixture/scaffold.py',
                                     'hosts/fixture/replay.py'),
                         'on_demand': (),
                         'fence': ('chupa/inbox.py',
                                   'chupa/box.py',
                                   'chupa/triage.py',
                                   'chupa/author.py',
                                   'chupa/daemon.py',
                                   'chupa/serve.py',
                                   'tests/test_box.py',
                                   'tests/test_triage.py',
                                   'tests/test_author.py',
                                   'tests/test_serve.py',
                                   'tests/test_inbox.py'),
                         'depends': ('phase6-continue-03', 'bug-gate-grammar'),
                         'expected': 60,
                         'stuck': 90,
                         'fenced_existing': ('chupa/box.py',
                                             'chupa/triage.py',
                                             'chupa/author.py',
                                             'chupa/daemon.py',
                                             'chupa/serve.py',
                                             'tests/test_box.py',
                                             'tests/test_triage.py',
                                             'tests/test_author.py',
                                             'tests/test_serve.py'),
                         'created': ('chupa/inbox.py', 'tests/test_inbox.py'),
                         'actual_render': 294883,
                         'render_overhead': 259},
 'phase6-continue-04': {'bytes': 5480,
                        'chars': 5480,
                        'sha256': '7049c89a5f82dea334cc240e474456ecc8a752cc9be519072d13d299304c13f0',
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P6',
                                 '13',
                                 '19.P6.escape-column',
                                 '19.P6.bug-gate-grammar',
                                 '19.P6.report-inbox-triage',
                                 '19.P6.supervised-merge-hold'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fence': ('tickets', 'tests/test_seeded_phase6_04.py'),
                        'depends': ('bug-gate-grammar', 'report-inbox-triage'),
                        'expected': 60,
                        'stuck': 90,
                        'fenced_existing': (),
                        'created': ('tests/test_seeded_phase6_04.py',),
                        'actual_render': 102446,
                        'render_overhead': -18}}

REQUIRED = {'bug-gate-grammar': ('19.P6.bug-gate-grammar',),
 'report-inbox-triage': ('19.P6.report-inbox-triage', '19.P6.bug-gate-grammar'),
 'phase6-continue-04': ('19.P6.escape-column',
                        '19.P6.bug-gate-grammar',
                        '19.P6.report-inbox-triage',
                        '19.P6.supervised-merge-hold')}

ENTRY_DEPTH = {'19.P6.bug-gate-grammar': {'bytes': 6134,
                            'chars': 6134,
                            'sha256': '2cc216db9be3bf8ec66ae2e266db2db8a8e34ef7374083a5a3b975ac3c0d36ec',
                            'resolves': 1,
                            'gap': None,
                            'parts': {'Owner': 1067,
                                      'Records': 1971,
                                      'Observable': 1051,
                                      'Tests': 1914},
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
 '19.P6.escape-column': {'bytes': 7224,
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
                                           'test_soak_uses_candidate_base_regate_receipt')}}

PLAN_SIZES = {'19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P6.bug-gate-grammar': {'bytes': 6134,
                            'chars': 6134,
                            'sha256': '2cc216db9be3bf8ec66ae2e266db2db8a8e34ef7374083a5a3b975ac3c0d36ec'},
 '7': {'bytes': 8173,
       'chars': 8173,
       'sha256': '5946c32455a2d8859111c4b56e2674de365f2e60da9eeb1b98776ba3c4f6e2c7'},
 '13': {'bytes': 19840,
        'chars': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P6.report-inbox-triage': {'bytes': 6470,
                               'chars': 6470,
                               'sha256': '7554e633033b41150ec51622d0537929a1773626b8f0a936893f58a38972df0a'},
 '12': {'bytes': 20224,
        'chars': 20224,
        'sha256': 'd3917109abd72822abd53cfadc7c74913fb6186ba72191820d0600c26cfac8cb'},
 '19.L': {'bytes': 20912,
          'chars': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa'},
 '19.P6': {'bytes': 11595,
           'chars': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c'},
 '19.P6.escape-column': {'bytes': 7224,
                         'chars': 7224,
                         'sha256': '5dd54b53e88e321bc64253a36aabcb84f95cad70aca25803c804da30963a1151'},
 '19.P6.supervised-merge-hold': {'bytes': 12388,
                                 'chars': 12388,
                                 'sha256': '3cd14d759d766a796aff1aff764b9a9f57f20a874c2cd0f19687a745cb167013'}}

FILE_SIZES = {'chupa/tickets.py': {'bytes': 28863,
                      'chars': 28863,
                      'sha256': '3659d183c95f5949f2c0bbb1bdf444d3da2d9c27a533d91de7b2551f6398b2d1',
                      'delimiter_free': True},
 'chupa/gates.py': {'bytes': 4945,
                    'chars': 4945,
                    'sha256': 'e84959455efe288a354c0a29f771ed3671a7b6f4e6783ae3008407f949dce59f',
                    'delimiter_free': True},
 'chupa/stages.py': {'bytes': 63358,
                     'chars': 63358,
                     'sha256': '668011a632d281a0da6a83cd32c8f3f5cc326b633b8cac7a11f9ab5420283ec2',
                     'delimiter_free': True},
 'tests/test_tickets.py': {'bytes': 15659,
                           'chars': 15659,
                           'sha256': '801d430c9a45c15a16fb35df02fa09c975725b15de1374e022a5aa50918dd618',
                           'delimiter_free': True},
 'tests/test_gates.py': {'bytes': 11668,
                         'chars': 11668,
                         'sha256': '1dd27eab54843f2e02141fa30f68784ee6f269ca13fc0dba2188a6ba871c3c2d',
                         'delimiter_free': True},
 'tests/test_mergequeue.py': {'bytes': 53525,
                              'chars': 53525,
                              'sha256': '18ba76378fa15421f8f4b30a2a474064531e1cca756e47b4d73c30820c95a3ee',
                              'delimiter_free': True},
 'chupa/merge.py': {'bytes': 21717,
                    'chars': 21717,
                    'sha256': '83efe01c4a2013046f69da93037a6a4b6e362c5fd3a79e0faa08f74d0f06504c',
                    'delimiter_free': True},
 'chupa/mergequeue.py': {'bytes': 16262,
                         'chars': 16262,
                         'sha256': 'f5e150bf011a5b1e1d091a261a4eb2982ab261b7312652ba659266d78b19af56',
                         'delimiter_free': True},
 'chupa/git.py': {'bytes': 6640,
                  'chars': 6640,
                  'sha256': '3008d974925e672157e10dba62707480ffe5302a138110c720858a2243500239',
                  'delimiter_free': True},
 'chupa/seams.py': {'bytes': 10148,
                    'chars': 10148,
                    'sha256': 'c465a54f053a4330f63abdcc0471747714f0d54147d070b79d9a98af213a0673',
                    'delimiter_free': True},
 'hosts/fixture/scaffold.py': {'bytes': 3054,
                               'chars': 3054,
                               'sha256': 'c4180b9e585928fc0018e5459b925835de10aee20cd1b78eaee03b368242bbfb',
                               'delimiter_free': True},
 'hosts/fixture/regression_test.py': {'bytes': 316,
                                      'chars': 316,
                                      'sha256': '9b2185be994ab285df7da529c9210d16a7f43904dfe43c6478e6987fc0060b26',
                                      'delimiter_free': True},
 'tests/test_serve.py': {'bytes': 75270,
                         'chars': 75270,
                         'sha256': 'b82421155064ff79a4a5ed7955322ecc92d9ba62b0ee9f9043a4f3d80029262e',
                         'delimiter_free': True},
 'chupa/box.py': {'bytes': 16317,
                  'chars': 16317,
                  'sha256': 'cd49eb33379ea9ca7833c3b37dccbcf0edb5a2ec047567d27a1484cf8f341bd7',
                  'delimiter_free': True},
 'chupa/triage.py': {'bytes': 11513,
                     'chars': 11513,
                     'sha256': 'cdcabee3c5fe6c70c29d593b4f49a08408c6e13ffd0f69f3320300d46e36f575',
                     'delimiter_free': True},
 'chupa/author.py': {'bytes': 12833,
                     'chars': 12833,
                     'sha256': '6bcd16e3cfc4d7a1f829014b0fecace720bde8f1f5204436282944960154f6ff',
                     'delimiter_free': True},
 'chupa/daemon.py': {'bytes': 26187,
                     'chars': 26187,
                     'sha256': '6bba2e43daee7e3a5b7c178babaf0326fb69bbb10060a5ca0d44d013b3bce60b',
                     'delimiter_free': True},
 'chupa/serve.py': {'bytes': 21790,
                    'chars': 21790,
                    'sha256': '8d3b3b63203e462914ea365ab8cbfa7d623091decebad2c7da3b3c6fc69c0985',
                    'delimiter_free': True},
 'tests/test_box.py': {'bytes': 17312,
                       'chars': 17312,
                       'sha256': 'eeb2ee5af9ef48621329e6bf15403c195f0a334ab184cdad6f8edaa471b5bec5',
                       'delimiter_free': True},
 'tests/test_triage.py': {'bytes': 12402,
                          'chars': 12402,
                          'sha256': 'bd26408dd15cbe20d7963b48eaaa2c9663d94415c0d82954664b71c75af79ef9',
                          'delimiter_free': True},
 'tests/test_author.py': {'bytes': 14069,
                          'chars': 14069,
                          'sha256': '3fc3702205665b43acd01d52d5d1444d7a6e5ebbd1d66c6fae4e32f4edbc7a61',
                          'delimiter_free': True},
 'hosts/fixture/replay.py': {'bytes': 354,
                             'chars': 354,
                             'sha256': 'e117a1e37fd681e933dd9cbb2932bed1a270ba8d478a5dee4c0fb9864ea56390',
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
                                    'sha256': '215e19c190648bbd108913994c5efd6e7c4343bf8f0db43723d2b8644c23c772'}}

CLOSURE_SCAN_PATTERN = ('Regression|carries|bug_evidence|report_inbox|triage_pass|storm_producer|CHECK_GATES|Message|def '
 '__init__|not hasattr|__all__|allowlist|compose|build_serve')

CLOSURE_SCAN = {'chupa': {'matched_lines': 176,
           'files': 42,
           'sha256': '4f72782374042faef5e1a9adb4e31b397730fc888bc1ad472266b3fef375261a'},
 'eval': {'matched_lines': 28,
          'files': 11,
          'sha256': 'ba11460bdabc7b2540c55392d5f3146e7a51aa9c3c114281bb6e031abf2f5c75'},
 'tests': {'matched_lines': 399,
           'files': 98,
           'sha256': 'c9a2158c89704e6362e647191ea6b1a34f6c9f75105ec8432223024a3d6d659e'}}

CLOSURE_DECISIONS = ('chupa/tickets.py:Ticket parser is its constructor caller; preserve public signatures while '
 'validating existing regression sections.',
 'chupa/stages.py:gather_evidence and CHECK_GATES are already used by chupa/merge.py:346-352 and '
 'chupa/mergequeue.py:271-274; new shared regression evidence needs no owner/caller signature '
 'change.',
 'tests/test_mergequeue.py:test_strategy_resolution_still_regates and '
 'tests/test_serve.py:test_serve_conflict_handoff_runs_after_admission_unwinds pin gate lists for '
 'non-bugs; both earn fence additions under rule 2. The non-bug gate passes without executing '
 'regression.',
 'chupa/triage.py:triage_pass and _settle_pass own the existing bootstrap sequential consumer; '
 'runtime intake fits these signatures.',
 'chupa/serve.py:Serve.triage at line 261 checks pending before calling triage_pass; this already '
 'fenced composition owner must admit an initially empty inbox.',
 'chupa/box.py:Message construction is local to Box.enqueue; a report-specific Box operation '
 'preserves enqueue signatures and engine callbacks.',
 'chupa/daemon.py:storm_producer constructs the storm-aware Box and is already fenced; preserve '
 'engine signatures and storm behavior.',
 'chupa/author.py:review_candidate validates/reviews before ticket commit and resolution; evidence '
 'copy belongs to the existing owner.',
 'No other public signature/operation allowlist, dormancy or negative assertion requires widening; '
 'unrelated callers remain preservation suites.')

COPY_VIOLATIONS = ()

DELIVERY = {'seeds': ('tickets/bug-gate-grammar/ticket.md',
           'tickets/report-inbox-triage/ticket.md',
           'tickets/phase6-continue-04/ticket.md'),
 'commit_only': 'tests/test_seeded_phase6_03.py',
 'approval_record': 'tickets/phase6-continue-03/checks.json',
 'review': 'requisition_review',
 'lift': 'ticket-plane',
 'retry': 'retain approved bytes while ticket_sha matches; author only snagged seeds'}


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_BODY_CHARS + a["chars"] + a["render_overhead"]
            + sum(PLAN_SIZES[pid]["chars"] for pid in a["plan"])
            + sum(FILE_SIZES[path]["chars"] for path in (*a["context"], *extra)))


def test_phase6_03_exact_admission():
    assert BATCH == ("bug-gate-grammar", "report-inbox-triage", "phase6-continue-04")
    assert PAYLOADS == BATCH[:2]
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert POSITION == 4
    assert UNSEEDED_SUFFIX == (
        ("escape-column",), ("supervised-merge-hold",),
        ("go-grade-machinery", "go-grade-run"), ("exit-receipt-machinery",), ("phase6-exit",))
    assert ROW_CONSUMPTION == {
        "bug-gate-grammar": ("fixture-host-scaffold",),
        "report-inbox-triage": ("bug-gate-grammar",)}
    assert set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(BATCH)
    for stem in BATCH:
        t, a = _ticket(stem), AUTHORED[stem]
        assert (t.frontmatter.source, t.frontmatter.state) == ("seed", "confirmed")
        assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("medium", "medium")
        assert (t.expected_minutes, t.stuck_minutes) == (a["expected"], a["stuck"])
        assert t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES
        assert t.depends == a["depends"]
        assert t.plan_contract == a["plan"]
        assert t.scope_fence == a["fence"]
        if stem in PAYLOADS:
            assert set(t.depends) == {"phase6-continue-03", *ROW_CONSUMPTION[stem]}
            assert {"19.I", "19.P6." + stem} <= set(t.plan_contract)
            assert not {"19.L", "19.P6"} & set(t.plan_contract)
        else:
            assert t.depends == PAYLOADS
            assert t.context == ("tests/test_seeded_phase3_core.py",)
            assert t.scope_fence == ("tickets", "tests/test_seeded_phase6_04.py")
    assert AUTHORED[PAYLOADS[0]]["plan"] == ("19.I", "19.P6.bug-gate-grammar", "7", "13")
    assert AUTHORED[PAYLOADS[1]]["plan"] == (
        "19.I", "19.P6.report-inbox-triage", "19.P6.bug-gate-grammar", "12")
    assert AUTHORED[BATCH[-1]]["plan"] == (
        "19.L", "19.I", "19.P6", "13", "19.P6.escape-column",
        "19.P6.bug-gate-grammar", "19.P6.report-inbox-triage", "19.P6.supervised-merge-hold")
    later = {s for admission in UNSEEDED_SUFFIX for s in admission}
    assert all(not later & set(a["depends"]) for a in AUTHORED.values())
    raw = (ROOT / ticket_path(BATCH[-1])).read_text()
    for fact in ("Position 4 carries admissions[4:]", "position 5 and admissions[5:]",
                 "phase6-continue-05", "medium/medium", "deep: true", "high/high",
                 "KNOWN-HARD", "phase6-exit", "no successor", "seeding.max_seeds_per_admission",
                 "drain.max_ticket_minutes"):
        assert fact in raw
    suffix = raw.split("Position 4 carries admissions[4:]:\n", 1)[1].split("\n\nAuthor exactly", 1)[0]
    assert suffix.splitlines() == ["- [" + ", ".join(a) + "]" for a in UNSEEDED_SUFFIX]


def test_phase6_03_entry_depth():
    assert REQUIRED == {
        "bug-gate-grammar": ("19.P6.bug-gate-grammar",),
        "report-inbox-triage": ("19.P6.report-inbox-triage", "19.P6.bug-gate-grammar"),
        "phase6-continue-04": ("19.P6.escape-column", "19.P6.bug-gate-grammar",
                              "19.P6.report-inbox-triage", "19.P6.supervised-merge-hold")}
    assert set(ENTRY_DEPTH) == {u for ids in REQUIRED.values() for u in ids}
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
    expected = {
        "bug-gate-grammar": (
            "test_bug_ticket_with_regression_validates", "test_grammar_refusals",
            "test_bug_gate_entry_units", "test_regression_overlay_proves_defect",
            "test_passing_new_test_is_not_bug_evidence", "test_missing_base_input_is_not_bug_evidence",
            "test_bug_gate_requires_evidence", "test_bug_gate_rejects_red_head",
            "test_bug_gate_refuses_invalid_carries", "test_bug_gate_execution_failure_is_closed",
            "test_bug_gate_check_wiring", "test_bug_gate_merge_wiring",
            "test_bug_gate_merge_rebase_regates", "test_bug_gate_merge_report_custody",
            "test_strategy_resolution_still_regates", "test_bug_gate_base_cleanup"),
        "report-inbox-triage": (
            "test_report_inbox_entry_units", "test_report_schema_is_closed",
            "test_report_evidence_bounds", "test_report_custody_precedes_enqueue",
            "test_report_retry_ingests_once", "test_host_report_signature",
            "test_report_ingested_before_pending_scan", "test_empty_box_report_intake",
            "test_report_consumer_is_sequential", "test_bug_report_evidence_ticket_plane_commit",
            "test_bug_report_text_stays_untrusted", "test_report_author_failure_is_decision",
            "test_report_replay_to_regression")}
    for stem, names in expected.items():
        assert ENTRY_DEPTH["19.P6." + stem]["tests"] == names
        acceptance = _ticket(stem).sections["Acceptance criteria"]
        assert all(name in acceptance for name in names)
        assert all(op in acceptance for op in ("required_units", "resolve_plan_contract", "entry_unit_gap"))
    assert not COPY_VIOLATIONS


def test_phase6_03_closure():
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert RENDER_BOUND_CHARS == 400_000 and REQ_RENDER_HEADROOM == 0.75
    assert (MEASURED_RENDER_TIER, MEASURED_RENDER_EFFORT) == ("max", "max")
    assert FENCE_ADDITIONS == {
        "bug-gate-grammar": ("tests/test_mergequeue.py", "tests/test_serve.py"),
        "report-inbox-triage": (), "phase6-continue-04": ()}
    assert set(CLOSURE_EVIDENCE["bug-gate-grammar"]) == set(FENCE_ADDITIONS["bug-gate-grammar"])
    assert all("19.L rule 2" in reason for reason in CLOSURE_EVIDENCE["bug-gate-grammar"].values())
    assert not CLOSURE_EVIDENCE["report-inbox-triage"] and not CLOSURE_EVIDENCE["phase6-continue-04"]
    assert len(CLOSURE_DECISIONS) == 9
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    for record in CLOSURE_SCAN.values():
        assert record["matched_lines"] > 0 and record["files"] > 0
        assert len(record["sha256"]) == 64
    assert set(HISTORICAL_SNAPSHOTS) == {
        "tests/test_seeded_phase3_core.py", "tests/test_seeded_phase6_core.py",
        "tests/test_seeded_phase6_01.py", "tests/test_seeded_phase6_02.py"}
    for stem, a in AUTHORED.items():
        t = _ticket(stem)
        assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
        assert (t.context, t.on_demand) == (a["context"], a["on_demand"])
        assert set(a["fenced_existing"]) <= set(t.context) | set(t.on_demand)
        assert not set(a["created"]) & (set(t.context) | set(t.on_demand))
        assert not set(t.context) & set(t.on_demand)
        assert not {"tests/test_seeded_phase6_03.py", "tests/test_seeded_phase6_04.py",
                    "chupa/inbox.py", "tests/test_inbox.py", "tests/test_bug_gate.py"} & set(t.context)
        assert all(FILE_SIZES[path]["delimiter_free"] and not path.startswith("specs/")
                   for path in t.context)
        assert render_chars(stem) == a["actual_render"] <= RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM
        for path in t.on_demand:
            # Context adds its path header and separator to the measured render.
            assert render_chars(stem, (path,)) + len("### " + path + "\n") + 2 == a["on_demand_embedding"][path]
            assert a["on_demand_embedding"][path] > RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM
        data = (ROOT / ticket_path(stem)).read_bytes()
        assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
            a["bytes"], a["chars"], a["sha256"])
    for record in (*PLAN_SIZES.values(), *FILE_SIZES.values(),
                   *HISTORICAL_SNAPSHOTS.values(), IMPLEMENT_SPEC):
        assert record["bytes"] >= record["chars"] > 0 and len(record["sha256"]) == 64


def test_phase6_03_check_owns_seed_custody():
    assert DELIVERY["seeds"] == tuple(ticket_path(s) for s in BATCH)
    assert DELIVERY["commit_only"] == "tests/test_seeded_phase6_03.py"
    assert DELIVERY["approval_record"] == "tickets/phase6-continue-03/checks.json"
    assert DELIVERY["review"] == "requisition_review" and DELIVERY["lift"] == "ticket-plane"
    assert DELIVERY["retry"] == "retain approved bytes while ticket_sha matches; author only snagged seeds"
    raw = (ROOT / ticket_path(BATCH[-1])).read_text()
    for fact in ("uncommitted", "requisition_review", "tickets/phase6-continue-04/checks.json",
                 "ticket-plane seed lift", "approved bytes", "ticket_sha", "snagged seeds"):
        assert fact in raw
    for stem in PAYLOADS:
        t = _ticket(stem)
        assert ("uv", "run", "pytest", "-q", "tests/test_plan_lint.py") in t.verification
        assert ("uv", "run", "pytest", "-q") in t.verification
