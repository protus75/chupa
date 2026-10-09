"""Terminal Phase 5 admission, using the merged Phase 3 core idiom.

All size, depth and closure operands are immutable authoring-time snapshots.
Check owns approvals and the ticket-plane lift; the seed stays off this code commit.
"""

import hashlib
import re
from pathlib import Path

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]

AUTHORING_HEAD = '2c54e720cdf5a133d98e9637acf30b201d394108'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

POSITION = 5

ADMISSIONS = (('retro-drain-invoker',),
 ('retro-box-activation',),
 ('scorecard-reporting',),
 ('status-projection', 'baseline-binding-reader'),
 ('retro-doctor-cli',),
 ('phase5-exit',))

ROWS = {'retro-drain-invoker': {'deep': True,
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
                                   'tests/test_box.py']},
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
                                    'tests/test_retro_box.py']},
 'scorecard-reporting': {'cite': [14],
                         'fence': ['chupa/scorecard.py',
                                   'tests/test_scorecard.py',
                                   'chupa/retro.py',
                                   'tests/test_retro.py']},
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
                                 'tests/test_cli.py']},
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
                                       'tests/test_retro_box.py']},
 'retro-doctor-cli': {'cite': [18],
                      'fence': ['chupa/doctor.py',
                                'tests/test_doctor.py',
                                'chupa/retro.py',
                                'chupa/__main__.py',
                                'tests/test_retro.py',
                                'tests/test_cli.py']},
 'phase5-exit': {'exit': True,
                 'fence': ['tickets',
                           'tests/test_phase5_exit.py',
                           'tests/test_seeded_phase6_core.py']}}

UNSEEDED_SUFFIX = (('phase5-exit',),)

BATCH = ('phase5-exit',)

AUTHORED = {'chars': 11241,
 'bytes': 11241,
 'sha256': '713afa1094e62b1e028be14bd3cf7798a154962fb9fb9f474d5c137fe8ad10ef',
 'plan': ('19.L',
          '19.I',
          '19.P5',
          '19.P6',
          '13',
          '19.P6.core-renderer',
          '19.P6.core-drift-classifier',
          '8',
          '15'),
 'context': ('chupa/retro.py',
             'chupa/scorecard.py',
             'chupa/baseline.py',
             'chupa/git.py',
             'chupa/seams.py',
             'chupa/specs.py',
             'chupa/stages.py',
             'chupa/config.py',
             'tests/test_seeded_phase3_core.py',
             'tickets/retro-box-activation/checks.json',
             'tickets/baseline-binding-reader/checks.json'),
 'on_demand': (),
 'depends': ('phase5-continue-05',),
 'fence': ('tickets', 'tests/test_phase5_exit.py', 'tests/test_seeded_phase6_core.py'),
 'expected': 60,
 'stuck': 180}

REQUIRED = ('19.P6.core-renderer', '19.P6.core-drift-classifier')

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
                                           'test_core_classifier_unreachable_from_production_gates')}}

PLAN_SIZES = {'19.L': {'chars': 20912,
          'bytes': 20912,
          'sha256': '66e84cac9dacd539b1b29b3e51c82dfdade10c5228e8faea15a6adc8716ef4aa'},
 '19.I': {'chars': 1811,
          'bytes': 1811,
          'sha256': 'cfc0b1be4cfe88be240b6ae604660bd9d27a660cebbd7cad73ceca448091553c'},
 '19.P5': {'chars': 9792,
           'bytes': 9792,
           'sha256': 'c85ad87ba606c5c0ca540b1f5ae10bb10802775a44d702805a493a83469366c2'},
 '19.P6': {'chars': 11595,
           'bytes': 11595,
           'sha256': '8c8c4cefa506c9186fa0c5cf692485b84a8eee5a49a2e3b68a9171d5bd9e167c'},
 '13': {'chars': 19840,
        'bytes': 19840,
        'sha256': '62498fb56d1b5fae322306359b35345a8c0beae1f40c670c7fb5d5722b0a649f'},
 '19.P6.core-renderer': {'chars': 4415,
                         'bytes': 4415,
                         'sha256': '5c3e4e5b41a70d3762b7d68d3da52e4fae07ef15ac452a8165e06300b580727f'},
 '19.P6.core-drift-classifier': {'chars': 4211,
                                 'bytes': 4211,
                                 'sha256': '1f5ad897c314b376776104dcbdf555fd81f3b402628fedeec3d40a345a0a01b8'},
 '8': {'chars': 8712,
       'bytes': 8712,
       'sha256': '7024a6dc821bad113cc141046646426ee3c397bc3f877f27bbf2dae6b5e53ae1'},
 '15': {'chars': 17253,
        'bytes': 17253,
        'sha256': 'ece80fdf277f4a2b4786623e8d359f0aa1d3a9fba489a3706e241cdd5bb3d3ad'}}

FILE_SIZES = {'chupa/retro.py': {'chars': 17582,
                    'bytes': 17582,
                    'sha256': 'fdcca1647d597e6dfd212007897d64f512dc300a6b699be9bd12c8be5858620a'},
 'chupa/scorecard.py': {'chars': 3870,
                        'bytes': 3870,
                        'sha256': '65df2445e2234cd58f72a60a07eb8b394764aff09feee573812a3ef69e0e0f16'},
 'chupa/baseline.py': {'chars': 3413,
                       'bytes': 3413,
                       'sha256': '93e8c3a61a322591308bb752fe9cb16c89e57090cde4280c9e24e9b0ab36e9d9'},
 'chupa/git.py': {'chars': 6640,
                  'bytes': 6640,
                  'sha256': '3008d974925e672157e10dba62707480ffe5302a138110c720858a2243500239'},
 'chupa/seams.py': {'chars': 10148,
                    'bytes': 10148,
                    'sha256': 'c465a54f053a4330f63abdcc0471747714f0d54147d070b79d9a98af213a0673'},
 'chupa/specs.py': {'chars': 23132,
                    'bytes': 23132,
                    'sha256': '9489699ab36ac88ab134f52f08d9b781e2051fa3314c9466af5558e959bec54d'},
 'chupa/stages.py': {'chars': 63065,
                     'bytes': 63065,
                     'sha256': '87ded1b415e8051504bc1227af6ac8c2ed434ba53102af14fc918cfb1d902935'},
 'chupa/config.py': {'chars': 12245,
                     'bytes': 12245,
                     'sha256': 'f7f8f3e3855ff958a9d1ee5e2fd3fd87f02978cad6cfa83952dc64d0546c82cf'},
 'tests/test_seeded_phase3_core.py': {'chars': 5425,
                                      'bytes': 5425,
                                      'sha256': 'ad6a6400e55e4c98d8a9fb4e57ebfa706c5f9e1156e7344d7626dc7255077559'},
 'tickets/retro-box-activation/checks.json': {'chars': 8509,
                                              'bytes': 8509,
                                              'sha256': 'c4d1addecbaa84768882d0f11f9a1ce4d4e75990bb841cf8fb9d80e26ae1fd83'},
 'tickets/baseline-binding-reader/checks.json': {'chars': 4731,
                                                 'bytes': 4731,
                                                 'sha256': '09244fd152a7f1fa39b9762b0a42763b1b4892ba955ec024ba792409a98913b8'}}

IMPLEMENT_SPEC_CHARS = 4896

RENDER_OVERHEAD = 2000

HEADROOM_CHARS = 300000

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

PREDECESSOR_GRAPH = {'phase5-continue-05': ('retro-doctor-cli',),
 'retro-doctor-cli': ('phase5-continue-04',),
 'phase5-continue-04': ('status-projection', 'baseline-binding-reader'),
 'status-projection': ('phase5-continue-03', 'scorecard-reporting', 'retro-box-activation'),
 'phase5-continue-03': ('scorecard-reporting',),
 'scorecard-reporting': ('phase5-continue-02',),
 'phase5-continue-02': ('retro-box-activation',),
 'retro-box-activation': ('phase5-continue', 'retro-drain-invoker'),
 'phase5-continue': ('retro-drain-invoker',),
 'retro-drain-invoker': ('phase4-exit',),
 'phase4-exit': (),
 'baseline-binding-reader': ('phase5-continue-03', 'retro-box-activation')}

PREDECESSOR_HASHES = {'phase5-continue-05': 'a51bf33ababa7461e392c2ecedcae8f1f3c500c9430c3d75cadc6b446acf1b5e',
 'retro-doctor-cli': 'fd22939843bcf1e00cecc99c0e128281c1e36167701fdbb4fffd4ed90c4f6b51',
 'phase5-continue-04': '1739d6a605eac6ecd413d489789fd52cdecc706b51eb8981c48c8e700524e39a',
 'status-projection': 'f386d9267675b40faf72068e02f38ead4bcaa8f580f632cbf93450bf1c7be77d',
 'phase5-continue-03': '728edc3dd972a9031f2f35ba6a1b89990c369393883cc6a33eb127cc6844c970',
 'scorecard-reporting': '8737b430dac8a64651215e0dc757cbfafb6c2e4d619d3a8e58b80da26c71e068',
 'phase5-continue-02': '830e969ccd63727f40b802f0e54b22500810fe0d08b174ead23bbc8e55384214',
 'retro-box-activation': 'ba12168f00aff22003c68ce97caa6509c743accf46bbbda08ff45e3c94736d6c',
 'phase5-continue': '71f775f6b99540eb269460cc090ca711ced2d87055cdc829102e5af8d4fd1c7d',
 'retro-drain-invoker': 'f7041f0a5ad3e9702abc0a3bac33fc0c3e68c881cb64a2bcaa6954d1c9d9b70a',
 'phase4-exit': '4b82fc1c00738cdad4292a4664c4fd6abe04ad844d0f844d4edc74bf732aef3c',
 'baseline-binding-reader': '941aa1aa6adc4952ab9c674548dbb487afec8940c3e3dff0f935e4008eecde17'}

PHASE5_PAYLOADS = ('retro-drain-invoker',
 'retro-box-activation',
 'scorecard-reporting',
 'status-projection',
 'baseline-binding-reader',
 'retro-doctor-cli')

APPROVAL_EVIDENCE = {'retro-box-activation': {'chars': 8509,
                          'bytes': 8509,
                          'sha256': 'c4d1addecbaa84768882d0f11f9a1ce4d4e75990bb841cf8fb9d80e26ae1fd83',
                          'passed': True,
                          'produced_at_sha': '0182fcf420bfa2bf5797cebfb2b30b1f7f649ed5',
                          'verification': (('uv', 'run', 'pytest', '-q', 'tests/test_retro_box.py'),
                                           ('uv',
                                            'run',
                                            'pytest',
                                            '-q',
                                            'tests/test_box.py',
                                            'tests/test_triage.py',
                                            'tests/test_author.py',
                                            'tests/test_policy.py',
                                            'tests/test_merge.py'),
                                           ('uv',
                                            'run',
                                            'pytest',
                                            '-q',
                                            'tests/test_daemon_composition.py',
                                            'tests/test_status.py',
                                            'tests/test_retro.py',
                                            'tests/test_vocabularies.py'),
                                           ('uv', 'run', 'pytest', '-q', 'tests/test_plan_lint.py'),
                                           ('uv',
                                            'run',
                                            'pytest',
                                            '-q',
                                            'tests/test_drain_upgrade.py',
                                            'tests/test_seed_successor.py',
                                            'tests/test_cli.py',
                                            'tests/test_daemon_config.py',
                                            'tests/test_daemon_admission.py',
                                            'tests/test_daemon_pause.py',
                                            'tests/test_reconcile.py',
                                            'tests/test_flake.py',
                                            'tests/test_storm_hold.py',
                                            'tests/test_storm_notification_activation.py',
                                            'tests/test_drain_reentry.py',
                                            'tests/test_ladder.py',
                                            'tests/test_diagnose.py',
                                            'tests/test_harvest.py',
                                            'tests/test_audit.py',
                                            'tests/test_storm_producer.py',
                                            'tests/test_provider_cooldown_failover.py',
                                            'tests/test_watchdog_activation.py',
                                            'tests/test_restart_timers.py',
                                            'tests/test_kill_cli_activation.py',
                                            'tests/test_kill_executor_abort.py',
                                            'tests/test_kill_signal_journal.py',
                                            'tests/test_seed_path.py',
                                            'tests/test_reject_queue.py',
                                            'tests/test_caps.py',
                                            'tests/test_control_cli.py',
                                            'tests/test_daemon_tasks.py',
                                            'tests/test_heartbeat.py',
                                            'tests/test_checkpoint.py',
                                            'tests/test_kill_worker_stop.py',
                                            'tests/test_kill_failure_suppression.py',
                                            'tests/test_driver.py',
                                            'tests/test_storm.py',
                                            'tests/test_plan_lint.py'),
                                           ('uv', 'run', 'pytest', '-q')),
                          'bypassed': (),
                          'verification_passed': True},
 'baseline-binding-reader': {'chars': 4731,
                             'bytes': 4731,
                             'sha256': '09244fd152a7f1fa39b9762b0a42763b1b4892ba955ec024ba792409a98913b8',
                             'passed': True,
                             'produced_at_sha': 'b54c2664229aeeb8e5b1f253dbfd48396f24f857',
                             'verification': (('uv',
                                               'run',
                                               'pytest',
                                               '-q',
                                               'tests/test_baseline.py',
                                               'tests/test_policy.py',
                                               'tests/test_author.py',
                                               'tests/test_retro_box.py'),
                                              ('uv',
                                               'run',
                                               'pytest',
                                               '-q',
                                               'tests/test_eval_harness.py'),
                                              ('uv',
                                               'run',
                                               'pytest',
                                               '-q',
                                               'tests/test_plan_lint.py'),
                                              ('uv', 'run', 'pytest', '-q')),
                             'bypassed': (),
                             'verification_passed': True}}

CLOSURE_PATTERN = 'phase5-exit|Retro|production_evidence|project_scorecard|resolve_baseline|core-renderer|core_drift|not hasattr|__all__|allowlist|^class |^    def __init__|^def |^async def |compose|build_daemon|prepare_pipeline'

CLOSURE_SCAN = {'chupa': {'files_read': 52,
           'matched_lines': 606,
           'sha256': 'f3f5462c446570c95e95ef0796b535c99f371d7b5c4ccccb098f7cc63d7f5eb2'},
 'eval': {'files_read': 13,
          'matched_lines': 125,
          'sha256': '440b7e1326ba2f01d3abcb0b3028155efef59d923f3bbb35950d93333da29cc5'},
 'tests': {'files_read': 125,
           'matched_lines': 2283,
           'sha256': '9aabac22d7b98b059966914d65149105825e74daf13fff467a21d9d6fc9b27f9'}}

COPY_VIOLATIONS = ()

FENCE_ADDITIONS = {}

CREATED = ('tests/test_phase5_exit.py', 'tests/test_seeded_phase6_core.py')

DELIMITER_FREE_CONTEXT = {'chupa/retro.py': True,
 'chupa/scorecard.py': True,
 'chupa/baseline.py': True,
 'chupa/git.py': True,
 'chupa/seams.py': True,
 'chupa/specs.py': True,
 'chupa/stages.py': True,
 'chupa/config.py': True,
 'tests/test_seeded_phase3_core.py': True,
 'tickets/retro-box-activation/checks.json': True,
 'tickets/baseline-binding-reader/checks.json': True}

# No production signature, constructor, operation or activation changes at this exit.
# Retro production_evidence -> render_report, drain's forced hook, and baseline's
# resolve_baseline keep their callers. No existing negative assertion flips.
# The exit creates only tests and seeds; rules 2-5 earn no fence additions.
CLOSURE_DECISIONS = {
    '19.L.2': 'tests/test_retro.py receipt readers and tests/test_drain.py pre-exit dispatch '
              'remain valid; no old receipt assertion is superseded.',
    '19.L.3': 'No dormant component is activated; baseline/retro compositions stay wired.',
    '19.L.4': 'No new module here; 19.P6.core-renderer owns future chupa/hostfiles.py.',
    '19.L.5': 'Retro, production_evidence, project_scorecard and resolve_baseline keep '
              'signatures and composition callers; no operation allowlist changes.',
}


def _ticket():
    return validate_ticket('phase5-exit', (ROOT / ticket_path('phase5-exit')).read_text(), ROOT)


def _body():
    return (ROOT / ticket_path('phase5-exit')).read_text()


def render_chars(extra=()):
    return (IMPLEMENT_SPEC_CHARS + AUTHORED['chars'] + RENDER_OVERHEAD
            + sum(PLAN_SIZES[uid]['chars'] for uid in AUTHORED['plan'])
            + sum(FILE_SIZES[path]['chars'] for path in (*AUTHORED['context'], *extra)))


def test_terminal_registry_order_suffix_and_single_seed():
    assert POSITION == 5
    assert ADMISSIONS == (('retro-drain-invoker',), ('retro-box-activation',),
                          ('scorecard-reporting',),
                          ('status-projection', 'baseline-binding-reader'),
                          ('retro-doctor-cli',), ('phase5-exit',))
    assert ADMISSIONS[POSITION:] == UNSEEDED_SUFFIX == (('phase5-exit',),)
    assert BATCH == UNSEEDED_SUFFIX[0] == ('phase5-exit',)
    assert len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    assert set(ROWS) == {s for admission in ADMISSIONS for s in admission}
    seen = set()
    for admission in ADMISSIONS:
        for stem in admission:
            row = ROWS[stem]
            assert set(row.get('depends', ())) <= seen | set(admission)
            if row.get('deep') or row.get('exit'):
                assert len(admission) == 1
        seen.update(admission)


def test_intake_grammar_birth_role_citations_tier_and_budget():
    t = _ticket()
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ('high', 'high')
    assert t.depends == AUTHORED['depends'] == ('phase5-continue-05',)
    assert t.plan_contract == AUTHORED['plan'] == (
        '19.L', '19.I', '19.P5', '19.P6', '13', '19.P6.core-renderer',
        '19.P6.core-drift-classifier', '8', '15')
    assert t.expected_minutes == 60 < t.stuck_minutes == 180 <= DRAIN_MAX_TICKET_MINUTES
    assert '19.L identifies phase exits as KNOWN-HARD' in _body()
    for phrase in ('medium/medium', 'deep: true', 'KNOWN-DEEP high/high',
                   'seeding.max_seeds_per_admission', 'drain.max_ticket_minutes'):
        assert phrase in _body()


def test_transitive_payload_coverage_and_registry_consumption():
    visited = set()
    def walk(stem):
        assert stem != 'phase5-exit'  # A predecessor cannot point forward to this batch.
        if stem in visited:
            return
        visited.add(stem)
        for predecessor in PREDECESSOR_GRAPH[stem]:
            walk(predecessor)
    walk('phase5-continue-05')
    assert visited == set(PREDECESSOR_GRAPH) == set(PREDECESSOR_HASHES)
    assert PHASE5_PAYLOADS == tuple(s for a in ADMISSIONS[:POSITION] for s in a)
    assert set(PHASE5_PAYLOADS) <= visited
    for stem in PHASE5_PAYLOADS:
        assert set(ROWS[stem].get('depends', ())) <= set(PREDECESSOR_GRAPH[stem])
        assert stem in _ticket().sections['Acceptance criteria'] or stem in _body()
    assert 'test_phase5_exit_dependency_coverage' in _ticket().sections['Acceptance criteria']
    assert 'Dispatch is the merged-presence proof' in _body()
    assert 'Do not cross-check predecessor approvals as entry provenance' in _body()


def test_earned_fence_and_context_partition_with_fixed_render():
    t = _ticket()
    assert t.scope_fence == AUTHORED['fence'] == tuple(ROWS['phase5-exit']['fence'])
    assert FENCE_ADDITIONS == {}
    assert COPY_VIOLATIONS == ()
    assert set(CLOSURE_DECISIONS) == {'19.L.2', '19.L.3', '19.L.4', '19.L.5'}
    assert all(CLOSURE_DECISIONS.values())
    assert set(CLOSURE_SCAN) == {'chupa', 'eval', 'tests'}
    assert all(scan['files_read'] > 0 for scan in CLOSURE_SCAN.values())
    assert t.context == AUTHORED['context'] and t.on_demand == AUTHORED['on_demand'] == ()
    assert not set(CREATED) & set((*t.context, *t.on_demand))
    assert 'tests/test_seeded_phase3_core.py' in t.context
    assert 'tests/test_seeded_phase5_05.py' not in t.context
    assert all(DELIMITER_FREE_CONTEXT.values())
    assert not any(p.startswith('specs/') for p in t.context)
    # The ticket-plane fence is the new seed write lane, not all existing ticket data.
    assert CREATED == ('tests/test_phase5_exit.py', 'tests/test_seeded_phase6_core.py')
    assert render_chars() <= HEADROOM_CHARS == 400_000 * .75
    for path in t.on_demand:
        assert render_chars((path,)) > HEADROOM_CHARS
    suites = {'tests/test_retro_box.py', 'tests/test_baseline.py', 'tests/test_retro.py',
              'tests/test_scorecard.py', 'tests/test_drain.py', 'tests/test_plan_lint.py'}
    assert suites <= {arg for argv in t.verification for arg in argv}
    assert not suites & set((*t.scope_fence, *t.context, *t.on_demand))


def test_required_core_depth_snapshots_and_named_tests():
    assert REQUIRED == ('19.P6.core-renderer', '19.P6.core-drift-classifier')
    assert set(ENTRY_DEPTH) == set(REQUIRED)
    expected = {
        REQUIRED[0]: ('test_renderer_entry_unit', 'test_core_first_adoption_preserves_project_bytes',
                      'test_core_refresh_preserves_remainder',
                      'test_core_marker_corruption_refuses_without_writes',
                      'test_core_render_is_byte_idempotent', 'test_core_golden_uses_branch_template',
                      'test_core_routed_conduct_files', 'test_core_refusal_and_no_git'),
        REQUIRED[1]: ('test_classifier_entry_unit', 'test_core_drift_classification',
                      'test_core_drift_refuses_marker_corruption',
                      'test_core_remainder_process_refusals', 'test_core_remainder_accepts_project_rules',
                      'test_core_drift_uses_branch_render', 'test_core_classifier_is_pure',
                      'test_core_classifier_unreachable_from_production_gates'),
    }
    for uid, entry in ENTRY_DEPTH.items():
        assert entry['gap'] is None and entry['resolves'] == 1
        assert set(entry['parts']) == {'Owner', 'Records', 'Observable', 'Tests'}
        assert all(n > 0 for n in entry['parts'].values())
        assert entry['missing_part_rejected'] == dict.fromkeys(entry['parts'], True)
        assert entry['sha256'] == PLAN_SIZES[uid]['sha256']
        assert entry['tests'] == expected[uid]
        assert all(name in _body() for name in entry['tests'])
    for name in ('resolve_plan_contract', 'required_units', 'entry_unit_gap',
                 'Owner, Records, Observable and Tests', 'kind: spec_gap'):
        assert name in _body()


def test_named_exit_reads_emitters_and_real_pre_exit_producer():
    criteria = _ticket().sections['Acceptance criteria']
    for obligation in ('test_phase5_exit_dependency_coverage', 'test_phase5_exit_committed_retro',
                       'test_phase5_exit_retro_provenance', 'test_phase5_exit_retro_box',
                       'test_phase5_exit_baseline'):
        assert obligation in criteria
    for phrase in ('retro-drain-invoker + scorecard-reporting', 'producer forced pre-exit retro',
                   'scorecard', 'numeric spend/tokens', 'existing surfaces/stems', 'zero escapes',
                   'production provenance', 'retro-box-activation', 'baseline-binding-reader'):
        assert phrase in criteria
    for phrase in ('lexicographically latest committed tickets/retro/<seq>.md',
                   'Receipt absence during phase5-continue-05 authoring is expected',
                   "absence at this exit's run is an unmet read", 'production_evidence',
                   'project_scorecard', 'fixture provenance', 'window_final_event',
                   'never require a live ignored journal', 'unmet exit read returns premise_failed',
                   'test_completed_retro_proposals_reach_prompt_spec_merge',
                   'test_baseline_states_and_latest_signal', 'test_baseline_routing_and_spec_drift'):
        assert phrase in _body()
    assert set(APPROVAL_EVIDENCE) == {'retro-box-activation', 'baseline-binding-reader'}
    for stem, receipt in APPROVAL_EVIDENCE.items():
        assert receipt['passed'] and receipt['verification_passed']
        assert 'verification' not in receipt['bypassed']
        assert any('tests/test_retro_box.py' in argv if stem == 'retro-box-activation'
                   else 'tests/test_baseline.py' in argv for argv in receipt['verification'])


def test_next_phase_core_only_edges_and_engine_check_custody():
    for phrase in ('exactly core-renderer, core-drift-classifier and phase6-continue',
                   'Core payloads depend on phase5-exit',
                   'core-drift-classifier also depends on core-renderer',
                   'phase6-continue depends on both core payloads', 'position 1 with admissions[1:]',
                   'refuse forward edges', 'never later payloads', 'Write the three new seed files',
                   'leave them uncommitted', 'Commit only the two new tests', 'requisition_review',
                   'tickets/phase5-exit/checks.json before one ticket-plane seed lift',
                   'retains approved bytes while ticket_sha matches', 're-authors only snagged seeds'):
        assert phrase in _body()


def test_authoring_hashes_sizes_and_seed_byte_identity():
    assert re.fullmatch(r'[0-9a-f]{40}', AUTHORING_HEAD)
    assert IDIOM_BLOB == '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
    assert hashlib.sha256((ROOT / ticket_path('phase5-exit')).read_bytes()).hexdigest() == AUTHORED['sha256']
    for record in (*PLAN_SIZES.values(), *FILE_SIZES.values(), AUTHORED,
                   *ENTRY_DEPTH.values(), *APPROVAL_EVIDENCE.values()):
        assert 0 < record['chars'] <= record['bytes']
        assert re.fullmatch(r'[0-9a-f]{64}', record['sha256'])
    assert all(re.fullmatch(r'[0-9a-f]{64}', sha) for sha in PREDECESSOR_HASHES.values())
    assert IMPLEMENT_SPEC_CHARS > 0 and RENDER_OVERHEAD == 2000
