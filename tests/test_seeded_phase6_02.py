"""Admission 2: direct seeds and immutable authoring-time contract/render snapshots.

Plan and Context contents are never read by this historical test. Only seed identity
is checked against the materialized tickets, following the merged Phase 3 idiom.
"""
import hashlib
from pathlib import Path

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]

AUTHORING_HEAD = '869bd256052191ae31060cb9a6a5bae2982a9d8d'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

BATCH = ('host-contract-doc', 'fixture-host-scaffold', 'phase6-continue-03')

PAYLOADS = ('host-contract-doc', 'fixture-host-scaffold')

POSITION = 3

UNSEEDED_SUFFIX = (('bug-gate-grammar', 'report-inbox-triage'),
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

ROW_CONSUMPTION = {'host-contract-doc': ('migrate-config',),
 'fixture-host-scaffold': ('host-contract-doc', 'core-drift-activation')}

FENCE_FLOORS = {'host-contract-doc': ('docs/host-contract.md', 'tests/test_host_contract.py'),
 'fixture-host-scaffold': ('hosts/fixture/', 'tests/test_fixture_host.py'),
 'phase6-continue-03': ('tickets', 'tests/test_seeded_phase6_03.py')}

FENCE_ADDITIONS = {'host-contract-doc': (), 'fixture-host-scaffold': (), 'phase6-continue-03': ()}

CLOSURE_EVIDENCE = {'host-contract-doc': {}, 'fixture-host-scaffold': {}, 'phase6-continue-03': {}}

AUTHORED = {'host-contract-doc': {'bytes': 4743,
                       'chars': 4743,
                       'sha256': 'f0fecbd273032643f5299a3468511b138983e90f060a8e42939c0fe2315e6610',
                       'plan': ('19.I', '19.P6.host-contract-doc', '15', '12'),
                       'context': ('chupa/config.py',
                                   'chupa/seams.py',
                                   'chupa/hostfiles.py',
                                   'chupa/providers.py',
                                   'chupa/lockfile.py',
                                   'chupa/specs.py',
                                   'chupa/gates.py',
                                   'chupa/mergequeue.py',
                                   'chupa/tickets.py'),
                       'on_demand': (),
                       'fence': ('docs/host-contract.md', 'tests/test_host_contract.py'),
                       'depends': ('phase6-continue-02', 'migrate-config'),
                       'expected': 60,
                       'stuck': 90,
                       'fenced_existing': (),
                       'created': ('docs/host-contract.md', 'tests/test_host_contract.py'),
                       'actual_render': 194315,
                       'render_overhead': 151},
 'fixture-host-scaffold': {'bytes': 4797,
                           'chars': 4797,
                           'sha256': 'e5a41f1fd477d0d4eb80bbb6cb15df980414ea4d279b78df5e4b3c7e1757d4df',
                           'plan': ('19.I',
                                    '19.P6.fixture-host-scaffold',
                                    '19.P6.host-contract-doc',
                                    '19.P6.core-drift-activation',
                                    '15',
                                    '12'),
                           'context': ('chupa/config.py',
                                       'chupa/providers.py',
                                       'chupa/seams.py',
                                       'chupa/llm.py',
                                       'chupa/hostfiles.py',
                                       'chupa/artifacts.py',
                                       'chupa/specs.py'),
                           'on_demand': (),
                           'fence': ('hosts/fixture/', 'tests/test_fixture_host.py'),
                           'depends': ('phase6-continue-02',
                                       'host-contract-doc',
                                       'core-drift-activation'),
                           'expected': 60,
                           'stuck': 90,
                           'fenced_existing': (),
                           'created': ('hosts/fixture/', 'tests/test_fixture_host.py'),
                           'actual_render': 169207,
                           'render_overhead': 101},
 'phase6-continue-03': {'bytes': 5655,
                        'chars': 5655,
                        'sha256': '6b908d97ee5e72b56235e31d9a32f6409504fa19e0ab0bbb3911abe165765c77',
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P6',
                                 '13',
                                 '19.P6.bug-gate-grammar',
                                 '19.P6.report-inbox-triage',
                                 '19.P6.escape-column'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fence': ('tickets', 'tests/test_seeded_phase6_03.py'),
                        'depends': ('host-contract-doc', 'fixture-host-scaffold'),
                        'expected': 60,
                        'stuck': 90,
                        'fenced_existing': (),
                        'created': ('tests/test_seeded_phase6_03.py',),
                        'actual_render': 88021,
                        'render_overhead': -18}}

REQUIRED = {'host-contract-doc': ('19.P6.host-contract-doc',),
 'fixture-host-scaffold': ('19.P6.fixture-host-scaffold',
                           '19.P6.host-contract-doc',
                           '19.P6.core-drift-activation'),
 'phase6-continue-03': ('19.P6.bug-gate-grammar',
                        '19.P6.report-inbox-triage',
                        '19.P6.escape-column')}

ENTRY_DEPTH = {'19.P6.host-contract-doc': {'bytes': 3729,
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
                             'tests': ('test_host_contract_entry_unit',
                                       'test_host_contract_example_loads',
                                       'test_host_contract_schema_coverage',
                                       'test_host_contract_migration_and_managed_ownership',
                                       'test_host_contract_seam_inventory',
                                       'test_host_contract_report_custody_and_cutover')},
 '19.P6.fixture-host-scaffold': {'bytes': 6157,
                                 'chars': 6157,
                                 'sha256': 'f67e09cc8d94030c66a580cdd0f794e4472aa0ccde256dc823ab3c8a0e56fbfc',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 681,
                                           'Records': 2312,
                                           'Observable': 1329,
                                           'Tests': 1700},
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
                                           'test_fixture_scaffold_is_dormant')},
 '19.P6.core-drift-activation': {'bytes': 8560,
                                 'chars': 8560,
                                 'sha256': '97c95d010147fb541e49f7584700a3e987fc70e30993a079aea987286556d243',
                                 'resolves': 1,
                                 'gap': None,
                                 'parts': {'Owner': 1954,
                                           'Records': 2087,
                                           'Observable': 1409,
                                           'Tests': 2986},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'tests': ('test_core_activation_entry_unit',
                                           'test_core_classifier_unreachable_from_production_gates',
                                           'test_core_drift_reachable_from_production_gates',
                                           'test_core_drift_gate_reports',
                                           'test_core_drift_default_hard',
                                           'test_core_drift_merge_rerun',
                                           'test_core_drift_candidate_template',
                                           'test_routed_conduct_paths',
                                           'test_core_and_gate_share_routed_paths',
                                           'test_core_activation_first_adoption',
                                           'test_core_activation_committed_conduct',
                                           'test_core_activation_first_adoption_merge',
                                           'test_outbox_only_admission_records_null_commit_and_retires',
                                           'test_serve_conflict_handoff_runs_after_admission_unwinds')},
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
                                   'test_escape_squash_trailer_identity')}}

PLAN_SIZES = {'19.I': {'bytes': 1811,
          'chars': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P6.host-contract-doc': {'bytes': 3729,
                             'chars': 3729,
                             'sha256': 'd6f8fd4ccfae12e9428ee8ffa7d2c25261b22aa35fd251f9347faa06cd75f601'},
 '15': {'bytes': 17253,
        'chars': 17253,
        'sha256': 'ece80fdf277f4a2b4786623e8d359f0aa1d3a9fba489a3706e241cdd5bb3d3ad'},
 '12': {'bytes': 20224,
        'chars': 20224,
        'sha256': 'd3917109abd72822abd53cfadc7c74913fb6186ba72191820d0600c26cfac8cb'},
 '19.P6.fixture-host-scaffold': {'bytes': 6157,
                                 'chars': 6157,
                                 'sha256': 'f67e09cc8d94030c66a580cdd0f794e4472aa0ccde256dc823ab3c8a0e56fbfc'},
 '19.P6.core-drift-activation': {'bytes': 8560,
                                 'chars': 8560,
                                 'sha256': '97c95d010147fb541e49f7584700a3e987fc70e30993a079aea987286556d243'},
 '19.L': {'bytes': 20912,
          'chars': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa'},
 '19.P6': {'bytes': 11595,
           'chars': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c'},
 '13': {'bytes': 19840,
        'chars': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P6.bug-gate-grammar': {'bytes': 3922,
                            'chars': 3922,
                            'sha256': 'c5432aed7a4f2665a06b7cebf5ef759fc4cc793f7c7231bee8945b9fb8cd1db2'},
 '19.P6.report-inbox-triage': {'bytes': 6470,
                               'chars': 6470,
                               'sha256': '7554e633033b41150ec51622d0537929a1773626b8f0a936893f58a38972df0a'},
 '19.P6.escape-column': {'bytes': 7224,
                         'chars': 7224,
                         'sha256': '5dd54b53e88e321bc64253a36aabcb84f95cad70aca25803c804da30963a1151'}}

FILE_SIZES = {'chupa/config.py': {'bytes': 15828,
                     'chars': 15828,
                     'sha256': '9c73e65de2e76bce26ede5d8e6ccbd54e909677682da5f0f1df554f2505148d4',
                     'delimiter_free': True},
 'chupa/seams.py': {'bytes': 10148,
                    'chars': 10148,
                    'sha256': 'c465a54f053a4330f63abdcc0471747714f0d54147d070b79d9a98af213a0673',
                    'delimiter_free': True},
 'chupa/hostfiles.py': {'bytes': 10676,
                        'chars': 10676,
                        'sha256': '39199126de87e4c8c87d7276a8624f4974c00614ac41194710ef8d1490481bb5',
                        'delimiter_free': True},
 'chupa/providers.py': {'bytes': 28092,
                        'chars': 28092,
                        'sha256': '772af76f8d83e21607c46d0519a7cb4316839244df9d9187e4213b231ebd3398',
                        'delimiter_free': True},
 'chupa/lockfile.py': {'bytes': 3273,
                       'chars': 3273,
                       'sha256': '9497194aa4cd22638656f538acf80ab9b0e5bd7e1c454a87ed1ed78df64ac39c',
                       'delimiter_free': True},
 'chupa/specs.py': {'bytes': 23132,
                    'chars': 23132,
                    'sha256': '9489699ab36ac88ab134f52f08d9b781e2051fa3314c9466af5558e959bec54d',
                    'delimiter_free': True},
 'chupa/gates.py': {'bytes': 4945,
                    'chars': 4945,
                    'sha256': 'e84959455efe288a354c0a29f771ed3671a7b6f4e6783ae3008407f949dce59f',
                    'delimiter_free': True},
 'chupa/mergequeue.py': {'bytes': 16262,
                         'chars': 16262,
                         'sha256': 'f5e150bf011a5b1e1d091a261a4eb2982ab261b7312652ba659266d78b19af56',
                         'delimiter_free': True},
 'chupa/tickets.py': {'bytes': 28863,
                      'chars': 28863,
                      'sha256': '3659d183c95f5949f2c0bbb1bdf444d3da2d9c27a533d91de7b2551f6398b2d1',
                      'delimiter_free': True},
 'chupa/llm.py': {'bytes': 2858,
                  'chars': 2858,
                  'sha256': '48ac1dbdd99e211c419e5737dffc773195e55e57db3eb229fc3e4195e5b65156',
                  'delimiter_free': True},
 'chupa/artifacts.py': {'bytes': 10656,
                        'chars': 10656,
                        'sha256': 'be7867f624c0b48e8ef8a1dfdf74fd653a8bc9d93ba7e06a8b4bcd470f115617',
                        'delimiter_free': True},
 'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559',
                                      'delimiter_free': True}}

CLOSURE_SCAN_PATTERN = ('host.contract|fixture.host|hosts/fixture|ADAPTERS|WRITING_SURFACES|not '
 'hasattr|__all__|allowlist|def __init__|^def |^async def |compose|preflight|stdin_path')

CLOSURE_SCAN = {'chupa': {'matched_lines': 405,
           'files': 51,
           'sha256': 'a697f8c2dcc320c8c1dfb08fd84881233dcf1576e34867050e0df0c321b5ba96'},
 'eval': {'matched_lines': 116,
          'files': 18,
          'sha256': '3b36794466cabb75b7863621b0a39efd4a0d429db85a4fe17939bc3e2893ac2e'},
 'tests': {'matched_lines': 2315,
           'files': 131,
           'sha256': 'ef25d9d75997ce726a5aae0ef836883c60eb0417607f8b116cab7482349fb3b4'}}

CLOSURE_DECISIONS = ('chupa/providers.py:29 WRITING_SURFACES remains implement-only; fixture scripts add no surface.',
 'chupa/providers.py:494 ADAPTERS remains claude/codex; fixture claude uses the existing '
 'registration.',
 'chupa/providers.py:528-532 ProviderLLM constructs the existing adapter; no '
 'constructor/signature/wiring change.',
 'tests/test_providers.py:467 constructs ADAPTERS[name] unchanged; it is a preservation suite.',
 'eval/daemon_soak.py:195 and eval/reliability_battery.py:129 construct scripted providers '
 'unchanged.',
 'Both payloads create their entire registry floor; no production flip contradicts an existing '
 'negative assertion.')

COPY_VIOLATIONS = ()

CONTEXT_OWNER_EVIDENCE = {'chupa/gates.py': 'chupa/gates.py:48 Gate.check(artifact, workspace) -> GateReport owns the '
                   'interface in documentation criterion 5.',
 'chupa/mergequeue.py': 'chupa/mergequeue.py:137 MergeQueue.host_checks calls _command at line 161; '
                        'line 120 runs argv, line 135 builds the report, line 145 resolves exactly '
                        'one hard safety entry and line 157 selects always/hard integration checks.',
 'chupa/tickets.py': 'chupa/tickets.py:50 Frontmatter owns the closed fields; parse_ticket line '
                     '279 calls Frontmatter.model_validate. Section 15 governs additive-only '
                     'policy.'}

HISTORICAL_SNAPSHOTS = {'tests/test_seeded_phase3_core.py': {'bytes': 5425,
                                      'chars': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559'},
 'tests/test_seeded_phase6_core.py': {'bytes': 35196,
                                      'chars': 35196,
                                      'sha256': '7606a766e009e53284c8154c971847ed5f58b20dfff3f945266d35a324870cae'},
 'tests/test_seeded_phase6_01.py': {'bytes': 57492,
                                    'chars': 57492,
                                    'sha256': '735465971d2bb73e92e29e7b25ed9d6690b400268fa95044c786dab85befaabe'}}

APPROVED_SEED_SHA = {'fixture-host-scaffold': '0d52e0850a6ddc924fa65be2d33cf7e14eb312d5',
 'phase6-continue-03': '63430a4d95568b9f9e0f1bf506780da2370a06de'}

def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def render_chars(stem, extra=()):
    # Recorded overhead includes Context headings, placeholder removal and trailing-newline
    # removal. Tier/effort metadata does not change the production Implement body.
    a = AUTHORED[stem]
    return (IMPLEMENT_BODY_CHARS + a["chars"] + a["render_overhead"]
            + sum(PLAN_SIZES[p]["chars"] for p in a["plan"])
            + sum(FILE_SIZES[p]["chars"] for p in (*a["context"], *extra)))


def test_phase6_02_exact_admission():
    assert BATCH == ("host-contract-doc", "fixture-host-scaffold", "phase6-continue-03")
    assert PAYLOADS == BATCH[:2]
    assert len(set(BATCH)) == len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert POSITION == 3
    assert UNSEEDED_SUFFIX == (
        ("bug-gate-grammar", "report-inbox-triage"), ("escape-column",),
        ("supervised-merge-hold",), ("go-grade-machinery", "go-grade-run"),
        ("exit-receipt-machinery",), ("phase6-exit",))
    assert ROW_CONSUMPTION == {
        "host-contract-doc": ("migrate-config",),
        "fixture-host-scaffold": ("host-contract-doc", "core-drift-activation")}
    assert FENCE_FLOORS == {
        "host-contract-doc": ("docs/host-contract.md", "tests/test_host_contract.py"),
        "fixture-host-scaffold": ("hosts/fixture/", "tests/test_fixture_host.py"),
        "phase6-continue-03": ("tickets", "tests/test_seeded_phase6_03.py")}
    assert set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(BATCH)
    for stem in BATCH:
        t, a = _ticket(stem), AUTHORED[stem]
        assert (t.frontmatter.source, t.frontmatter.state) == ("seed", "confirmed")
        assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("medium", "medium")
        assert (t.expected_minutes, t.stuck_minutes) == (a["expected"], a["stuck"])
        assert t.expected_minutes < t.stuck_minutes <= DRAIN_MAX_TICKET_MINUTES
        assert t.depends == a["depends"]
        assert t.plan_contract == a["plan"]
        assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
        if stem in PAYLOADS:
            assert set(t.depends) == {"phase6-continue-02", *ROW_CONSUMPTION[stem]}
            assert {"19.I", "19.P6." + stem} <= set(t.plan_contract)
            assert not {"19.L", "19.P6"} & set(t.plan_contract)
        else:
            assert t.depends == PAYLOADS
            assert t.scope_fence == ("tickets", "tests/test_seeded_phase6_03.py")
            assert t.context == ("tests/test_seeded_phase3_core.py",)
    assert AUTHORED["host-contract-doc"]["plan"] == ("19.I", "19.P6.host-contract-doc", "15", "12")
    assert AUTHORED["fixture-host-scaffold"]["plan"] == (
        "19.I", "19.P6.fixture-host-scaffold", "19.P6.host-contract-doc",
        "19.P6.core-drift-activation", "15", "12")
    assert AUTHORED["phase6-continue-03"]["plan"] == (
        "19.L", "19.I", "19.P6", "13", "19.P6.bug-gate-grammar",
        "19.P6.report-inbox-triage", "19.P6.escape-column")
    later = {stem for admission in UNSEEDED_SUFFIX for stem in admission}
    assert all(not later & set(a["depends"]) for a in AUTHORED.values())
    raw = (ROOT / ticket_path(BATCH[-1])).read_text()
    for fact in ("Position 3", "admissions[3:]", "position 4", "admissions[4:]",
                 "phase6-continue-04", "medium/medium", "deep: true",
                 "high/high", "KNOWN-HARD", "phase6-exit", "no successor",
                 "seeding.max_seeds_per_admission", "drain.max_ticket_minutes"):
        assert fact in raw


def test_phase6_02_entry_depth():
    assert REQUIRED == {
        "host-contract-doc": ("19.P6.host-contract-doc",),
        "fixture-host-scaffold": ("19.P6.fixture-host-scaffold",
                                 "19.P6.host-contract-doc", "19.P6.core-drift-activation"),
        "phase6-continue-03": ("19.P6.bug-gate-grammar", "19.P6.report-inbox-triage",
                               "19.P6.escape-column")}
    assert set(ENTRY_DEPTH) == {u for units in REQUIRED.values() for u in units}
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
            assert {k: d[k] for k in ("chars", "bytes", "sha256")} == PLAN_SIZES[uid]
    expected = {
        "host-contract-doc": (
            "test_host_contract_entry_unit", "test_host_contract_example_loads",
            "test_host_contract_schema_coverage", "test_host_contract_migration_and_managed_ownership",
            "test_host_contract_seam_inventory", "test_host_contract_report_custody_and_cutover"),
        "fixture-host-scaffold": (
            "test_fixture_host_entry_units", "test_fixture_profile_loads",
            "test_fixture_scenario_list_is_closed", "test_fixture_replay_is_deterministic",
            "test_fixture_regression_exists_at_base", "test_fixture_escape_is_machine_introduced",
            "test_fixture_reports_are_bounded", "test_fixture_cli_adapter_roundtrip",
            "test_fixture_scaffold_is_dormant")}
    for stem, obligations in expected.items():
        assert ENTRY_DEPTH["19.P6." + stem]["tests"] == obligations
        raw = (ROOT / ticket_path(stem)).read_text()
        acceptance = raw.split("## Acceptance criteria\n", 1)[1].split("\n## Verification", 1)[0]
        assert all(name in acceptance for name in obligations)
        assert "chupa/specs.py" in AUTHORED[stem]["context"]
        assert "12" in AUTHORED[stem]["plan"]
        for operation in ("required_units", "resolve_plan_contract"):
            assert operation in acceptance
    fixture = _ticket("fixture-host-scaffold").sections["Acceptance criteria"]
    for obligation in ("schema_version 1", "both origins", "summary/app_commit/app_version",
                       "implicated_paths", "evidence.replay/log", "game_slug/anomaly_code/location",
                       "player omits", "unknown report/evidence keys", "non-1 versions",
                       "initial_state/actions", "regular evidence files", "1 MiB", "64 KiB",
                       "exact-boundary", "without importing an unbuilt inbox validator"):
        assert obligation in fixture
    assert not COPY_VIOLATIONS


def test_phase6_02_closure():
    assert len(AUTHORING_HEAD) == len(IDIOM_BLOB) == 40
    assert RENDER_BOUND_CHARS == 400_000 and REQ_RENDER_HEADROOM == 0.75
    assert (MEASURED_RENDER_TIER, MEASURED_RENDER_EFFORT) == ("max", "max")
    assert FENCE_ADDITIONS == {stem: () for stem in BATCH}
    assert CLOSURE_EVIDENCE == {stem: {} for stem in BATCH}
    assert len(CLOSURE_DECISIONS) == 6
    assert set(CONTEXT_OWNER_EVIDENCE) == {"chupa/gates.py", "chupa/mergequeue.py", "chupa/tickets.py"}
    assert set(CONTEXT_OWNER_EVIDENCE) <= set(AUTHORED["host-contract-doc"]["context"])
    assert all(CONTEXT_OWNER_EVIDENCE.values())
    for snapshot in HISTORICAL_SNAPSHOTS.values():
        assert snapshot["bytes"] >= snapshot["chars"] > 0 and len(snapshot["sha256"]) == 64
    assert "providers.py:494 ADAPTERS" in CLOSURE_DECISIONS[1]
    assert "no production flip" in CLOSURE_DECISIONS[-1]
    assert set(CLOSURE_SCAN) == {"chupa", "eval", "tests"}
    for record in CLOSURE_SCAN.values():
        assert record["matched_lines"] > 0 and record["files"] > 0
        assert len(record["sha256"]) == 64
    for stem, a in AUTHORED.items():
        t = _ticket(stem)
        assert (t.context, t.on_demand) == (a["context"], a["on_demand"])
        assert not set(t.context) & set(t.on_demand)
        assert set(a["fenced_existing"]) <= set(t.context) | set(t.on_demand)
        assert not set(a["created"]) & (set(t.context) | set(t.on_demand))
        assert not {"tests/test_seeded_phase6_02.py", "tests/test_seeded_phase6_03.py",
                    "docs/host-contract.md", "tests/test_host_contract.py",
                    "hosts/fixture/", "tests/test_fixture_host.py"} & set(t.context)
        assert all(FILE_SIZES[p]["delimiter_free"] and not p.startswith("specs/")
                   for p in t.context)
        assert not t.on_demand  # All complete embedded renders are comfortably below headroom.
        assert render_chars(stem) == a["actual_render"] <= RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM
        for path in t.on_demand:
            assert render_chars(stem, (path,)) > RENDER_BOUND_CHARS * REQ_RENDER_HEADROOM
        for path in t.context:
            s = FILE_SIZES[path]
            assert s["bytes"] >= s["chars"] > 0 and len(s["sha256"]) == 64
        data = (ROOT / ticket_path(stem)).read_bytes()
        assert (len(data), len(data.decode()), hashlib.sha256(data).hexdigest()) == (
            a["bytes"], a["chars"], a["sha256"])
    for record in (*PLAN_SIZES.values(), IMPLEMENT_SPEC):
        assert record["bytes"] >= record["chars"] > 0 and len(record["sha256"]) == 64


def test_phase6_02_check_owns_seed_custody():
    # Check, not this implementer/test, writes approvals and performs the ticket-plane lift.
    raw = (ROOT / ticket_path("phase6-continue-03")).read_text()
    for fact in ("requisition_review", "tickets/phase6-continue-03/checks.json",
                 "ticket-plane seed lift", "approved bytes", "ticket_sha", "uncommitted"):
        assert fact in raw
    for stem in PAYLOADS:
        t = _ticket(stem)
        assert ("uv", "run", "pytest", "-q", "tests/test_plan_lint.py") in t.verification
        assert ("uv", "run", "pytest", "-q") in t.verification

def test_phase6_02_approved_bytes_retained():
    assert set(APPROVED_SEED_SHA) == {"fixture-host-scaffold", "phase6-continue-03"}
    for stem, approved_sha in APPROVED_SEED_SHA.items():
        data = (ROOT / ticket_path(stem)).read_bytes()
        assert hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == approved_sha
    acceptance = _ticket("host-contract-doc").sections["Acceptance criteria"]
    for owner in CONTEXT_OWNER_EVIDENCE:
        assert owner in acceptance
    for obligation in ("Gate.check", "host_checks", "rc 0", "exactly one hard",
                       "always/hard", "Frontmatter", "additive-only"):
        assert obligation in acceptance
