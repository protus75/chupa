"""Phase 6 core authoring snapshots, using the merged Phase 3 idiom.

Size, depth and scan operands were captured before authoring committed tests.
Historical render arithmetic never inspects live plan text or live file sizes.
The two sibling creations are deliberately absent from both payload Contexts.
"""

import hashlib
from pathlib import Path
import re

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]

AUTHORING_HEAD = '8447c72d45c5c14c7bddc1b24778ff8e68f72808'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

PAYLOADS = ('core-renderer', 'core-drift-classifier')

BATCH = ('core-renderer', 'core-drift-classifier', 'phase6-continue')

POSITION = 1

ADMISSIONS = (('core-renderer', 'core-drift-classifier'),
 ('core-drift-activation', 'migrate-config'),
 ('host-contract-doc', 'fixture-host-scaffold'),
 ('bug-gate-grammar', 'report-inbox-triage'),
 ('escape-column',),
 ('supervised-merge-hold',),
 ('go-grade-machinery', 'go-grade-run'),
 ('exit-receipt-machinery',),
 ('phase6-exit',))

UNSEEDED_SUFFIX = (('core-drift-activation', 'migrate-config'),
 ('host-contract-doc', 'fixture-host-scaffold'),
 ('bug-gate-grammar', 'report-inbox-triage'),
 ('escape-column',),
 ('supervised-merge-hold',),
 ('go-grade-machinery', 'go-grade-run'),
 ('exit-receipt-machinery',),
 ('phase6-exit',))

ROW_CONSUMPTION = {'core-renderer': (),
 'core-drift-classifier': ('core-renderer',),
 'core-drift-activation': ('core-drift-classifier',),
 'migrate-config': ('core-renderer',),
 'host-contract-doc': ('migrate-config',),
 'fixture-host-scaffold': ('host-contract-doc', 'core-drift-activation'),
 'bug-gate-grammar': ('fixture-host-scaffold',),
 'report-inbox-triage': ('bug-gate-grammar',),
 'escape-column': ('bug-gate-grammar', 'report-inbox-triage'),
 'supervised-merge-hold': ('escape-column',),
 'go-grade-machinery': ('supervised-merge-hold', 'fixture-host-scaffold'),
 'go-grade-run': ('go-grade-machinery',),
 'exit-receipt-machinery': ('go-grade-run',),
 'phase6-exit': ('exit-receipt-machinery',)}

DEEP_ROWS = ('supervised-merge-hold',)

EXIT_ROWS = ('phase6-exit',)

FENCE_FLOORS = {'core-renderer': ('chupa/hostfiles.py',
                   'tests/test_hostfiles.py',
                   'chupa/__main__.py',
                   'tests/test_cli.py'),
 'core-drift-classifier': ('chupa/hostfiles.py', 'tests/test_hostfiles.py'),
 'phase6-continue': ('tickets', 'tests/test_seeded_phase6_01.py')}

FENCE_ADDITIONS = {'core-renderer': (), 'core-drift-classifier': (), 'phase6-continue': ()}

AUTHORED = {'core-renderer': {'chars': 4228,
                   'bytes': 4228,
                   'sha256': 'd125a88d0435d15d262ebcf29ba6123e7c65eba752f333ffa907c3c7e66468b8',
                   'plan': ('19.I', '19.P6.core-renderer', '8', '15'),
                   'context': ('chupa/__main__.py',
                               'tests/test_cli.py',
                               'chupa/config.py',
                               'chupa/providers.py',
                               'chupa/seams.py',
                               'chupa/specs.py'),
                   'on_demand': (),
                   'depends': ('phase5-exit',),
                   'fence': ('chupa/hostfiles.py',
                             'tests/test_hostfiles.py',
                             'chupa/__main__.py',
                             'tests/test_cli.py'),
                   'expected': 60,
                   'stuck': 90},
 'core-drift-classifier': {'chars': 5176,
                           'bytes': 5176,
                           'sha256': 'a2f35a19d1a255061cc26209c60d69d48f0736f67eeafe5eac8960dea9a35f05',
                           'plan': ('19.I',
                                    '19.P6.core-drift-classifier',
                                    '19.P6.core-renderer',
                                    '8'),
                           'context': ('chupa/gates.py',
                                       'chupa/merge.py',
                                       'chupa/stages.py',
                                       'chupa/seams.py',
                                       'chupa/specs.py'),
                           'on_demand': (),
                           'depends': ('phase5-exit', 'core-renderer'),
                           'fence': ('chupa/hostfiles.py', 'tests/test_hostfiles.py'),
                           'expected': 60,
                           'stuck': 90},
 'phase6-continue': {'chars': 7085,
                     'bytes': 7085,
                     'sha256': 'dba52460c45a2c4eea7c2369eb3b9fd0120ac70aa9b8498690bb8780b0c638ca',
                     'plan': ('19.L',
                              '19.I',
                              '19.P6',
                              '13',
                              '19.P6.core-drift-activation',
                              '19.P6.core-renderer',
                              '19.P6.core-drift-classifier',
                              '7',
                              '8',
                              '19.P6.migrate-config',
                              '15',
                              '19.P6.host-contract-doc',
                              '19.P6.fixture-host-scaffold'),
                     'context': ('tests/test_seeded_phase3_core.py',),
                     'on_demand': (),
                     'depends': ('core-renderer', 'core-drift-classifier'),
                     'fence': ('tickets', 'tests/test_seeded_phase6_01.py'),
                     'expected': 60,
                     'stuck': 90}}

REQUIRED = {'core-renderer': ('19.P6.core-renderer',),
 'core-drift-classifier': ('19.P6.core-drift-classifier', '19.P6.core-renderer'),
 'phase6-continue': ('19.P6.core-drift-activation',
                     '19.P6.core-renderer',
                     '19.P6.core-drift-classifier',
                     '19.P6.migrate-config',
                     '19.P6.host-contract-doc',
                     '19.P6.fixture-host-scaffold')}

ENTRY_DEPTH = {'19.P6.core-renderer': {'chars': 4415,
                         'bytes': 4415,
                         'sha256': '5c3e4e5b41a70d3762b7d68d3da52e4fae07ef15ac452a8165e06300b580727f',
                         'gap': None,
                         'resolves': 1,
                         'parts': {'Owner': 656, 'Records': 1399, 'Observable': 742, 'Tests': 1486},
                         'missing_part_rejected': {'Owner': True,
                                                   'Records': True,
                                                   'Observable': True,
                                                   'Tests': True},
                         'tests': ('test_renderer_entry_unit',
                                   'test_core_first_adoption_preserves_project_bytes',
                                   'test_core_refresh_preserves_remainder',
                                   'test_core_marker_corruption_refuses_without_writes',
                                   'test_core_render_is_byte_idempotent',
                                   'test_core_golden_uses_branch_template',
                                   'test_core_routed_conduct_files',
                                   'test_core_refusal_and_no_git')},
 '19.P6.core-drift-classifier': {'chars': 4211,
                                 'bytes': 4211,
                                 'sha256': '1f5ad897c314b376776104dcbdf555fd81f3b402628fedeec3d40a345a0a01b8',
                                 'gap': None,
                                 'resolves': 1,
                                 'parts': {'Owner': 414,
                                           'Records': 1610,
                                           'Observable': 657,
                                           'Tests': 1393},
                                 'missing_part_rejected': {'Owner': True,
                                                           'Records': True,
                                                           'Observable': True,
                                                           'Tests': True},
                                 'tests': ('test_classifier_entry_unit',
                                           'test_core_drift_classification',
                                           'test_core_drift_refuses_marker_corruption',
                                           'test_core_remainder_process_refusals',
                                           'test_core_remainder_accepts_project_rules',
                                           'test_core_drift_uses_branch_render',
                                           'test_core_classifier_is_pure',
                                           'test_core_classifier_unreachable_from_production_gates')},
 '19.P6.core-drift-activation': {'chars': 4299,
                                 'bytes': 4299,
                                 'sha256': '63f2d3d707814d33f3837ebe497f866c34c50c8906dd6b1ce274a012a56ad686',
                                 'gap': None,
                                 'resolves': 1,
                                 'parts': {'Owner': 755,
                                           'Records': 1327,
                                           'Observable': 770,
                                           'Tests': 1323},
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
                                           'test_core_and_gate_share_routed_paths')},
 '19.P6.migrate-config': {'chars': 3596,
                          'bytes': 3596,
                          'sha256': 'ccee47e8964daeb1d0b2a128a2b3b25011890fe09ca3db5c0e05387cb946c267',
                          'gap': None,
                          'resolves': 1,
                          'parts': {'Owner': 401,
                                    'Records': 1122,
                                    'Observable': 736,
                                    'Tests': 1216},
                          'missing_part_rejected': {'Owner': True,
                                                    'Records': True,
                                                    'Observable': True,
                                                    'Tests': True},
                          'tests': ('test_migrate_config_entry_unit',
                                    'test_migrate_config_zero_to_one',
                                    'test_migrate_config_validates_before_write',
                                    'test_migrate_config_current_is_noop',
                                    'test_migrate_config_refuses_unsupported_inputs',
                                    'test_older_schema_version_is_refused_naming_migrate_config',
                                    'test_migrate_config_before_load')},
 '19.P6.host-contract-doc': {'chars': 3729,
                             'bytes': 3729,
                             'sha256': 'd6f8fd4ccfae12e9428ee8ffa7d2c25261b22aa35fd251f9347faa06cd75f601',
                             'gap': None,
                             'resolves': 1,
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
 '19.P6.fixture-host-scaffold': {'chars': 4901,
                                 'bytes': 4901,
                                 'sha256': '6d539213afac5a50c8fe3065bf3fdf1c32c87cc6a0d24145b978e04d7a9b081e',
                                 'gap': None,
                                 'resolves': 1,
                                 'parts': {'Owner': 681,
                                           'Records': 1346,
                                           'Observable': 1329,
                                           'Tests': 1410},
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

PLAN_SIZES = {'19.I': {'chars': 1811,
          'bytes': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P6.core-renderer': {'chars': 4415,
                         'bytes': 4415,
                         'sha256': '5c3e4e5b41a70d3762b7d68d3da52e4fae07ef15ac452a8165e06300b580727f'},
 '8': {'chars': 8712,
       'bytes': 8712,
       'sha256': '7024a6dc821bad113cc141046646426ee3c397bc3f877f27bbf2dae6b5e53ae1'},
 '15': {'chars': 17253,
        'bytes': 17253,
        'sha256': 'ece80fdf277f4a2b4786623e8d359f0aa1d3a9fba489a3706e241cdd5bb3d3ad'},
 '19.P6.core-drift-classifier': {'chars': 4211,
                                 'bytes': 4211,
                                 'sha256': '1f5ad897c314b376776104dcbdf555fd81f3b402628fedeec3d40a345a0a01b8'},
 '19.L': {'chars': 20912,
          'bytes': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa'},
 '19.P6': {'chars': 11595,
           'bytes': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c'},
 '13': {'chars': 19840,
        'bytes': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P6.core-drift-activation': {'chars': 4299,
                                 'bytes': 4299,
                                 'sha256': '63f2d3d707814d33f3837ebe497f866c34c50c8906dd6b1ce274a012a56ad686'},
 '7': {'chars': 8173,
       'bytes': 8173,
       'sha256': '5946c32455a2d8859111c4b56e2674de365f2e60da9eeb1b98776ba3c4f6e2c7'},
 '19.P6.migrate-config': {'chars': 3596,
                          'bytes': 3596,
                          'sha256': 'ccee47e8964daeb1d0b2a128a2b3b25011890fe09ca3db5c0e05387cb946c267'},
 '19.P6.host-contract-doc': {'chars': 3729,
                             'bytes': 3729,
                             'sha256': 'd6f8fd4ccfae12e9428ee8ffa7d2c25261b22aa35fd251f9347faa06cd75f601'},
 '19.P6.fixture-host-scaffold': {'chars': 4901,
                                 'bytes': 4901,
                                 'sha256': '6d539213afac5a50c8fe3065bf3fdf1c32c87cc6a0d24145b978e04d7a9b081e'}}

FILE_SIZES = {'chupa/__main__.py': {'chars': 18994,
                       'bytes': 18994,
                       'sha256': 'ad14ba1912dbfe21f44d87daa67cfcfdc79675666efd216d096f0ecb394215ea'},
 'tests/test_cli.py': {'chars': 20089,
                       'bytes': 20089,
                       'sha256': '7ed7a851fe026152a1956e245e1a28a4fcfcabf13e7f55b32ccb611d0c1d0179'},
 'chupa/config.py': {'chars': 12245,
                     'bytes': 12245,
                     'sha256': 'f7f8f3e3855ff958a9d1ee5e2fd3fd87f02978cad6cfa83952dc64d0546c82cf'},
 'chupa/providers.py': {'chars': 27676,
                        'bytes': 27676,
                        'sha256': '4f0bc7d61dc8a342a7bfce60e7442b7186a12d1a12a23510b01ba7bc3f32f77e'},
 'chupa/seams.py': {'chars': 10148,
                    'bytes': 10148,
                    'sha256': 'c465a54f053a4330f63abdcc0471747714f0d54147d070b79d9a98af213a0673'},
 'chupa/specs.py': {'chars': 23132,
                    'bytes': 23132,
                    'sha256': '9489699ab36ac88ab134f52f08d9b781e2051fa3314c9466af5558e959bec54d'},
 'chupa/gates.py': {'chars': 4945,
                    'bytes': 4945,
                    'sha256': 'e84959455efe288a354c0a29f771ed3671a7b6f4e6783ae3008407f949dce59f'},
 'chupa/merge.py': {'chars': 21717,
                    'bytes': 21717,
                    'sha256': '83efe01c4a2013046f69da93037a6a4b6e362c5fd3a79e0faa08f74d0f06504c'},
 'chupa/stages.py': {'chars': 63065,
                     'bytes': 63065,
                     'sha256': '87ded1b415e8051504bc1227af6ac8c2ed434ba53102af14fc918cfb1d902935'},
 'tests/test_seeded_phase3_core.py': {'chars': 5425,
                                      'bytes': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559'}}

IMPLEMENT_SPEC_SIZE = {'chars': 4896,
 'bytes': 4896,
 'sha256': '3c0f2da83067702a14d645aea8cd2fecc0c9c6cdfa914ce1b82f496575ee1817'}

IMPLEMENT_BODY_CHARS = 4775

ACTUAL_BASE_RENDERS = {'core-renderer': 153558, 'core-drift-classifier': 152156, 'phase6-continue': 130714}

HEADROOM_CHARS = 300000

RENDER_OVERHEAD = 2000

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

DELIMITER_FREE_CONTEXT = {'chupa/__main__.py': True,
 'tests/test_cli.py': True,
 'chupa/config.py': True,
 'chupa/providers.py': True,
 'chupa/seams.py': True,
 'chupa/specs.py': True,
 'chupa/gates.py': True,
 'chupa/merge.py': True,
 'chupa/stages.py': True,
 'tests/test_seeded_phase3_core.py': True}

COPY_VIOLATIONS = ()

CLOSURE_PATTERN = ('hostfiles|core_drift|chupa:core|\\bmain\\(|_parser\\(|not '
 'hasattr|__all__|is_dormant|public.*allowlist|compose|build_daemon|def __init__|^def |^async def '
 '|^class ')

CLOSURE_SCAN = {'chupa': {'files_read': 52,
           'matched_lines': 589,
           'sha256': 'b7f7f5adfc2cb8f8cd996934720158d51a93f9ef2693afa83f6b6982e2dac526'},
 'eval': {'files_read': 13,
          'matched_lines': 131,
          'sha256': '26927a92a60624fba2138e2944bf99a09d17b33183df5e60eb0b52e855f909e7'},
 'tests': {'files_read': 126,
           'matched_lines': 2341,
           'sha256': 'e7c62242741fc1d4fd3eb5354c067264f0b73993dd61f57c67b143ce5d7f6263'}}

MAIN_CALLER_FILES = ('chupa/__main__.py',
 'eval/daemon_soak.py',
 'eval/diagnose.py',
 'eval/harness.py',
 'eval/reliability_battery.py',
 'eval/shakeout/run.py',
 'tests/test_author.py',
 'tests/test_caps.py',
 'tests/test_checkpoint.py',
 'tests/test_cli.py',
 'tests/test_control_cli.py',
 'tests/test_daemon_admission.py',
 'tests/test_daemon_composition.py',
 'tests/test_daemon_config.py',
 'tests/test_daemon_pause.py',
 'tests/test_daemon_soak.py',
 'tests/test_daemon_tasks.py',
 'tests/test_diagnose.py',
 'tests/test_doctor.py',
 'tests/test_drain.py',
 'tests/test_drain_reentry.py',
 'tests/test_drain_upgrade.py',
 'tests/test_flake.py',
 'tests/test_harvest.py',
 'tests/test_harvest_orphans.py',
 'tests/test_heartbeat.py',
 'tests/test_kill_cli_activation.py',
 'tests/test_kill_failure_suppression.py',
 'tests/test_kill_worker_stop.py',
 'tests/test_ladder.py',
 'tests/test_merge.py',
 'tests/test_providers.py',
 'tests/test_reject_queue.py',
 'tests/test_second_problems.py',
 'tests/test_seed_path.py',
 'tests/test_seed_successor.py',
 'tests/test_seeded_phase5_01.py',
 'tests/test_seeded_phase5_02.py',
 'tests/test_seeded_phase5_03.py',
 'tests/test_seeded_phase5_04.py',
 'tests/test_seeded_phase5_core.py',
 'tests/test_serve.py',
 'tests/test_status.py',
 'tests/test_storm_hold.py',
 'tests/test_storm_notification_activation.py',
 'tests/test_storm_producer.py',
 'tests/test_terminal.py',
 'tests/test_triage.py')

CLOSURE_DECISIONS = {'19.L.2': 'No core verb-absence or hostfiles assertion exists in merged executable tests; adding '
           'the verb preserves existing CLI assertions. No contradictory test earns an addition.',
 '19.L.3': 'Classifier behavioral construction stays dormant at production gates; no activation is '
           'performed in this admission.',
 '19.L.4': '19.P6.core-renderer owns new chupa/hostfiles.py; classifier reuses it.',
 '19.L.5': 'main retains its signature; new verb composition is confined to chupa/__main__.py and '
           'tests/test_cli.py in the row floor. No renderer/parser public callers exist yet. '
           'Classifier reuses parser/render signatures and has no production caller or '
           'public-operation allowlist. Providers.resolve/candidates are consumed without '
           'signature change. No addition is earned.'}

CREATED = {'core-renderer': ('chupa/hostfiles.py', 'tests/test_hostfiles.py'),
 'core-drift-classifier': ('chupa/hostfiles.py', 'tests/test_hostfiles.py'),
 'phase6-continue': ('tests/test_seeded_phase6_01.py',)}

FENCED_EXISTING = {'core-renderer': ('chupa/__main__.py', 'tests/test_cli.py'),
 'core-drift-classifier': (),
 'phase6-continue': ()}

MODALS = ('must',
 'must not',
 'should',
 'should not',
 'shall',
 'shall not',
 'will',
 'will not',
 'may',
 'may not')

IMPERATIVES = ('author',
 'implement',
 'check',
 'review',
 'merge',
 'commit',
 'dispatch',
 'confirm',
 'reject',
 'kill',
 'pause',
 'resume',
 'triage',
 'rework',
 'drain')


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, set(BATCH) - {stem})


def render_chars(stem, extra=()):
    snapshot = AUTHORED[stem]
    return (IMPLEMENT_SPEC_SIZE['chars'] + snapshot['chars'] + RENDER_OVERHEAD
            + sum(PLAN_SIZES[uid]['chars'] for uid in snapshot['plan'])
            + sum(FILE_SIZES[path]['chars'] for path in (*snapshot['context'], *extra)))


def test_exact_core_batch_registry_consumption_and_finite_suffix():
    assert BATCH == (*PAYLOADS, 'phase6-continue') == (
        'core-renderer', 'core-drift-classifier', 'phase6-continue')
    assert ADMISSIONS[0] == PAYLOADS
    assert POSITION == 1 and UNSEEDED_SUFFIX == ADMISSIONS[POSITION:]
    assert len(UNSEEDED_SUFFIX) == 8 and UNSEEDED_SUFFIX[-1] == ('phase6-exit',)
    assert ADMISSIONS[1] == ('core-drift-activation', 'migrate-config')
    assert len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    admitted = set()
    for admission in ADMISSIONS:
        assert 1 <= len(admission) <= 2
        assert not admitted & set(admission)
        for stem in admission:
            assert set(ROW_CONSUMPTION[stem]) <= admitted | set(admission)
            if stem in DEEP_ROWS or stem in EXIT_ROWS:
                assert len(admission) == 1
        admitted.update(admission)
    assert admitted == set(ROW_CONSUMPTION)
    assert DEEP_ROWS == ('supervised-merge-hold',) and EXIT_ROWS == ('phase6-exit',)
    assert not set(PAYLOADS) & set(DEEP_ROWS + EXIT_ROWS)


@pytest.mark.parametrize('stem', BATCH)
def test_intake_grammar_confirmed_seed_birth_and_fixed_tier(stem):
    ticket = _ticket(stem)
    assert (ticket.frontmatter.source, ticket.frontmatter.state) == ('seed', 'confirmed')
    assert (ticket.frontmatter.agent_tier, ticket.frontmatter.agent_effort) == ('medium', 'medium')
    assert ticket.expected_minutes == AUTHORED[stem]['expected'] == 60
    assert ticket.stuck_minutes == AUTHORED[stem]['stuck'] == 90 <= DRAIN_MAX_TICKET_MINUTES
    assert ticket.expected_minutes < ticket.stuck_minutes


def test_exact_role_and_row_citations_and_required_entry_depth():
    expected = {
        'core-renderer': ('19.I', '19.P6.core-renderer', '8', '15'),
        'core-drift-classifier': ('19.I', '19.P6.core-drift-classifier', '19.P6.core-renderer', '8'),
        'phase6-continue': ('19.L', '19.I', '19.P6', '13', '19.P6.core-drift-activation',
            '19.P6.core-renderer', '19.P6.core-drift-classifier', '7', '8', '19.P6.migrate-config', '15', '19.P6.host-contract-doc',
            '19.P6.fixture-host-scaffold'),
    }
    assert REQUIRED == {
        'core-renderer': ('19.P6.core-renderer',),
        'core-drift-classifier': ('19.P6.core-drift-classifier', '19.P6.core-renderer'),
        'phase6-continue': ('19.P6.core-drift-activation', '19.P6.core-renderer',
                            '19.P6.core-drift-classifier', '19.P6.migrate-config',
                            '19.P6.host-contract-doc', '19.P6.fixture-host-scaffold'),
    }
    for stem in BATCH:
        assert _ticket(stem).plan_contract == AUTHORED[stem]['plan'] == expected[stem]
        assert set(REQUIRED[stem]) <= set(expected[stem])
    assert set(ENTRY_DEPTH) == {uid for units in REQUIRED.values() for uid in units}
    for uid, entry in ENTRY_DEPTH.items():
        assert entry['gap'] is None and entry['resolves'] == 1
        assert set(entry['parts']) == {'Owner', 'Records', 'Observable', 'Tests'}
        assert all(n > 0 for n in entry['parts'].values())
        assert entry['missing_part_rejected'] == dict.fromkeys(entry['parts'], True)
        assert entry['sha256'] == PLAN_SIZES[uid]['sha256']
    assert COPY_VIOLATIONS == ()


def test_seed_edges_cover_sibling_consumption_without_forward_edges():
    edges = {stem: set(_ticket(stem).depends) for stem in BATCH}
    assert edges == {
        'core-renderer': {'phase5-exit'},
        'core-drift-classifier': {'phase5-exit', 'core-renderer'},
        'phase6-continue': set(PAYLOADS),
    }
    emitted = {'phase5-exit'}
    for stem in BATCH:
        assert edges[stem] <= emitted
        assert edges[stem] == set(AUTHORED[stem]['depends'])
        if stem in PAYLOADS:
            assert set(ROW_CONSUMPTION[stem]) <= edges[stem]
        emitted.add(stem)


@pytest.mark.parametrize('stem', BATCH)
def test_earned_fence_context_partition_and_maximum_effort_render(stem):
    ticket, authored = _ticket(stem), AUTHORED[stem]
    assert ticket.scope_fence == authored['fence'] == FENCE_FLOORS[stem] + FENCE_ADDITIONS[stem]
    assert FENCE_ADDITIONS[stem] == ()
    assert ticket.context == authored['context'] and ticket.on_demand == authored['on_demand'] == ()
    assert set(FENCED_EXISTING[stem]) <= set(ticket.context) | set(ticket.on_demand)
    assert not set(CREATED[stem]) & set((*ticket.context, *ticket.on_demand))
    assert all(DELIMITER_FREE_CONTEXT[path] for path in ticket.context)
    assert not any(path.startswith('specs/') for path in ticket.context)
    assert not {'tests/test_phase5_exit.py', 'tests/test_seeded_phase6_core.py'} & set(ticket.context)
    assert set(CLOSURE_DECISIONS) == {'19.L.2', '19.L.3', '19.L.4', '19.L.5'}
    assert all(CLOSURE_DECISIONS.values())
    assert set(CLOSURE_SCAN) == {'chupa', 'eval', 'tests'}
    assert all(s['files_read'] > 0 and s['matched_lines'] > 0 for s in CLOSURE_SCAN.values())
    assert {'tests/test_cli.py', 'tests/test_drain.py', 'tests/test_merge.py',
            'tests/test_providers.py'} <= set(MAIN_CALLER_FILES)
    assert 'main retains its signature' in CLOSURE_DECISIONS['19.L.5']
    # The single bound has no effort-dependent reduction. These operands are historical.
    for effort in ('low', 'medium', 'high', 'max'):
        assert ACTUAL_BASE_RENDERS[stem] <= render_chars(stem) <= HEADROOM_CHARS == 400_000 * .75
    for path in ticket.on_demand:
        assert render_chars(stem, (path,)) > HEADROOM_CHARS
    commands = {arg for argv in ticket.verification for arg in argv}
    assert 'tests/test_plan_lint.py' in commands
    assert ('uv', 'run', 'pytest', '-q') in ticket.verification


def test_renderer_named_obligations_and_owner_are_carried_to_future_payload():
    names = ('test_renderer_entry_unit', 'test_core_first_adoption_preserves_project_bytes',
        'test_core_refresh_preserves_remainder', 'test_core_marker_corruption_refuses_without_writes',
        'test_core_render_is_byte_idempotent', 'test_core_golden_uses_branch_template',
        'test_core_routed_conduct_files', 'test_core_refusal_and_no_git')
    assert ENTRY_DEPTH['19.P6.core-renderer']['tests'] == names
    text = _text('core-renderer')
    criteria = _ticket('core-renderer').sections['Acceptance criteria']
    assert all(name in criteria for name in names)
    for phrase in ('new chupa/hostfiles.py module ownership', 'template, parser, byte renderer',
        'absent, empty and marker-free', 'mixed line endings', 'missing final newline',
        'project prefix and suffix', 'malformed, partial, duplicate, reordered, unterminated and stray',
        'corrupt member of a multi-file', 'precedes all writes', 'no further writes',
        'mechanically generated branch golden', 'detects a stale golden',
        'real CLI', 'claude-only, other-CLI-only, mixed and repeated-path',
        'exit 0', 'exit 2', 'atomic writes', 'no git, journal, provider call or gate work',
        'missing final newline', 'missing', 'entry_unit_gap'):
        assert phrase in text
    assert {'tests/test_config.py', 'tests/test_providers.py', 'tests/test_gates.py'} <= {
        arg for argv in _ticket('core-renderer').verification for arg in argv}
    assert not {'tests/test_config.py', 'tests/test_providers.py', 'tests/test_gates.py'} & set(
        (*_ticket('core-renderer').context, *_ticket('core-renderer').scope_fence))


def test_classifier_named_obligations_full_predicate_boundaries_and_dormancy():
    names = ('test_classifier_entry_unit', 'test_core_drift_classification',
        'test_core_drift_refuses_marker_corruption', 'test_core_remainder_process_refusals',
        'test_core_remainder_accepts_project_rules', 'test_core_drift_uses_branch_render',
        'test_core_classifier_is_pure', 'test_core_classifier_unreachable_from_production_gates')
    assert ENTRY_DEPTH['19.P6.core-drift-classifier']['tests'] == names
    text = _text('core-drift-classifier')
    criteria = _ticket('core-drift-classifier').sections['Acceptance criteria']
    assert all(name in criteria for name in names)
    assert MODALS == ('must', 'must not', 'should', 'should not', 'shall', 'shall not',
                      'will', 'will not', 'may', 'may not')
    assert IMPERATIVES == ('author', 'implement', 'check', 'review', 'merge', 'commit',
        'dispatch', 'confirm', 'reject', 'kill', 'pause', 'resume', 'triage', 'rework', 'drain')
    assert ', '.join(MODALS) in text and ', '.join(IMPERATIVES) in text
    for phrase in ('missing, current, drifted and refused', 'corruption/process-refusal precedence',
        'input-byte identity', 'every renderer corrupt-marker case', 'case-insensitive',
        'paragraph-opening subjects with word boundaries', 'Markdown unordered/numbered prefixes',
        'whitespace collapse', 'multiline/list continuations', 'chupacabra', 'mustache', 'reviewer',
        'other subjects', 'The chupa dashboard must use dark mode.', 'away from the opening',
        'Only the project remainder is normalized', 'changed template with its new block is current',
        'old block is drifted', 'forbids write, process, git, model and journal', 'deterministic',
        'actual production gate composition and merge rerun selection',
        'absence of classifier callers and active core_drift gate registration',
        'preserving the pre-existing vocabulary', 'later activation alone', 'shared provider resolver'):
        assert phrase in text
    preservation = {'tests/test_cli.py', 'tests/test_gates.py', 'tests/test_merge.py', 'tests/test_stages.py'}
    ticket = _ticket('core-drift-classifier')
    assert preservation <= {arg for argv in ticket.verification for arg in argv}
    assert not preservation & set((*ticket.context, *ticket.scope_fence))


def test_continuation_next_depth_shrinking_suffix_tiers_and_check_custody():
    ticket = _ticket('phase6-continue')
    text = _text(ticket.stem)
    assert ticket.context == ('tests/test_seeded_phase3_core.py',)
    for phrase in ('Position 1 carries admissions[1:]', 'position 2 and admissions[2:]',
        'exactly core-drift-activation, migrate-config and phase6-continue-02',
        'required_units', 'entry_unit_gap', 'resolve_plan_contract', 'kind: spec_gap',
        'successor\'s next-admission entries', 'Do not fabricate a missing successor entry',
        'medium/medium', 'deep: true', 'alone at high/high', 'KNOWN-HARD high/high',
        'seeding.max_seeds_per_admission', 'drain.max_ticket_minutes',
        'classifier\'s production-gate dormancy test', 'shared chupa/providers.py resolver',
        'confirmed source: seed birth', 'requisition_review',
        'tickets/phase6-continue/checks.json before one ticket-plane seed lift',
        'retains approved bytes while ticket_sha matches', 'authors only snagged seeds',
        'leave them uncommitted', 'Commit only tests/test_seeded_phase6_01.py',
        'Preservation suites appear only in Verification', 'or seeding past Phase 6'):
        assert phrase.lower() in text.lower()
    suffix_text = text.split('Position 1 carries admissions[1:]:', 1)[1].split('Author exactly', 1)[0]
    assert re.findall(r'\[([^\]]+)\]', suffix_text) == [', '.join(a) for a in UNSEEDED_SUFFIX]


def test_authoring_identity_hashes_and_recorded_operands():
    assert re.fullmatch(r'[0-9a-f]{40}', AUTHORING_HEAD)
    assert IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    for stem in BATCH:
        assert hashlib.sha256((ROOT / ticket_path(stem)).read_bytes()).hexdigest() == AUTHORED[stem]['sha256']
    for operand in (*AUTHORED.values(), *PLAN_SIZES.values(), *FILE_SIZES.values(),
                    *ENTRY_DEPTH.values(), IMPLEMENT_SPEC_SIZE):
        assert 0 < operand['chars'] <= operand['bytes']
        assert re.fullmatch(r'[0-9a-f]{64}', operand['sha256'])
    assert IMPLEMENT_BODY_CHARS < IMPLEMENT_SPEC_SIZE['chars']
    assert RENDER_OVERHEAD == 2000
