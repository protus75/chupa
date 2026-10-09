"""Phase 5 admission 03: immutable authoring snapshots and seed identity.

Render arithmetic and depth evidence never measure later code or plan bytes.
Check owns approvals and the ticket-plane lift; Implement commits only this test.
"""

import hashlib
import re
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

AUTHORING_HEAD = 'f06f09132fa0718d17d62e7db3df082093e0eeb9'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

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
                                   'does': 'INVOKER contract plus the sections 13/19 Exit-read '
                                           'window renderer resolution and driver materialization '
                                           'on the same window-projection seam. Transition-risk '
                                           'preservation: every suite reaching `main(["drain"])` '
                                           'through to a merge (re-entry, upgrade, kill, storm, '
                                           'restart, provider, watchdog, pause, control) migrates '
                                           'only an assertion its scenario actually forces, else '
                                           'stays unchanged with the non-firing reason recorded in '
                                           'the seeding test.'},
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
                                    'does': 'RETRO -> BOX contract; every production Box '
                                            'constructor with journal access receives the '
                                            'journal-backed rereport callback.'},
           'scorecard-reporting': {'cite': [14],
                                   'fence': ['chupa/scorecard.py',
                                             'tests/test_scorecard.py',
                                             'chupa/retro.py',
                                             'tests/test_retro.py'],
                                   'does': 'SCORECARD contract; tests/test_retro.py assertions are '
                                           'preserved unchanged.'},
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
                                       'does': 'BINDING READER contract, migrating any interim '
                                               'go-binding helper into the one reader.'},
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

POSITION = 3

UNSEEDED_SUFFIX = (('status-projection', 'baseline-binding-reader'), ('retro-doctor-cli',), ('phase5-exit',))

BATCH = ('status-projection', 'baseline-binding-reader', 'phase5-continue-04')

AUTHORED = {'status-projection': {'chars': 4606,
                       'bytes': 4606,
                       'sha256': 'f386d9267675b40faf72068e02f38ead4bcaa8f580f632cbf93450bf1c7be77d',
                       'plan': ('19.I', '19.P5.status-projection', '13'),
                       'context': ('chupa/status.py',
                                   'tests/test_status.py',
                                   'chupa/scorecard.py',
                                   'tests/test_scorecard.py',
                                   'chupa/box.py',
                                   'tests/test_box.py',
                                   'chupa/retro.py',
                                   'tests/test_retro.py',
                                   'chupa/__main__.py',
                                   'tests/test_cli.py'),
                       'on_demand': (),
                       'fence': ('chupa/status.py',
                                 'tests/test_status.py',
                                 'chupa/scorecard.py',
                                 'tests/test_scorecard.py',
                                 'chupa/box.py',
                                 'tests/test_box.py',
                                 'chupa/retro.py',
                                 'tests/test_retro.py',
                                 'chupa/__main__.py',
                                 'tests/test_cli.py'),
                       'depends': ('phase5-continue-03',
                                   'scorecard-reporting',
                                   'retro-box-activation'),
                       'expected': 60,
                       'stuck': 180},
 'baseline-binding-reader': {'chars': 4171,
                             'bytes': 4171,
                             'sha256': '941aa1aa6adc4952ab9c674548dbb487afec8940c3e3dff0f935e4008eecde17',
                             'plan': ('19.I', '19.P5.baseline-binding-reader', '12'),
                             'context': ('chupa/journal.py',
                                         'chupa/config.py',
                                         'chupa/policy.py',
                                         'tests/test_policy.py',
                                         'chupa/author.py',
                                         'tests/test_author.py',
                                         'tests/test_retro_box.py',
                                         'chupa/providers.py'),
                             'on_demand': (),
                             'fence': ('chupa/baseline.py',
                                       'tests/test_baseline.py',
                                       'chupa/journal.py',
                                       'chupa/config.py',
                                       'chupa/policy.py',
                                       'tests/test_policy.py',
                                       'chupa/author.py',
                                       'tests/test_author.py',
                                       'tests/test_retro_box.py'),
                             'depends': ('phase5-continue-03', 'retro-box-activation'),
                             'expected': 60,
                             'stuck': 180},
 'phase5-continue-04': {'chars': 5469,
                        'bytes': 5469,
                        'sha256': '1739d6a605eac6ecd413d489789fd52cdecc706b51eb8981c48c8e700524e39a',
                        'plan': ('19.L', '19.I', '19.P5', '19.P5.retro-doctor-cli', '18', '13'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fence': ('tickets', 'tests/test_seeded_phase5_04.py'),
                        'depends': ('status-projection', 'baseline-binding-reader'),
                        'expected': 60,
                        'stuck': 180}}

REQUIRED = {'status-projection': ('19.P5.status-projection',),
 'baseline-binding-reader': ('19.P5.baseline-binding-reader',),
 'phase5-continue-04': ('19.P5.retro-doctor-cli',)}

ENTRY_DEPTH = {'19.P5.status-projection': {'sha256': '9b68cc56abd993b2d62256d554ed130284e6f7c71dba7154161a857e215a0b86',
                             'chars': 4211,
                             'bytes': 4211,
                             'gap': None,
                             'resolves': 1,
                             'parts': {'Owner': 680,
                                       'Records': 1352,
                                       'Observable': 750,
                                       'Tests': 1289},
                             'tests': ('test_status_entry_unit',
                                       'test_status_current_window_scorecard',
                                       'test_status_production_provenance',
                                       'test_status_preserves_sections_and_is_write_free',
                                       'test_status_surfaces_confirmed_class_tombstones',
                                       'test_status_on_an_empty_journal',
                                       'test_status_projects_the_journal',
                                       'test_status_is_deterministic')},
 '19.P5.baseline-binding-reader': {'sha256': '472a7a66d81355f0cca710f2485d274c7859ed286f6d1593b0c71d1df9467adb',
                                   'chars': 4622,
                                   'bytes': 4622,
                                   'gap': None,
                                   'resolves': 1,
                                   'parts': {'Owner': 953,
                                             'Records': 1529,
                                             'Observable': 638,
                                             'Tests': 1368},
                                   'tests': ('test_baseline_entry_unit',
                                             'test_baseline_states_and_latest_signal',
                                             'test_baseline_routing_and_spec_drift',
                                             'test_baseline_invalid_inputs_fail_closed',
                                             'test_author_uses_baseline_resolution',
                                             'test_bootstrap_without_a_go_or_with_phase_one_no_go_drafts_every_row',
                                             'test_standing_go_uses_the_table_and_each_override_drafts',
                                             'test_reopened_retro_ticket_starts_draft')},
 '19.P5.retro-doctor-cli': {'sha256': 'ed89788c644e34de4d479e398b69ec16b384bb420a5468a8a579fd3c53e5222c',
                            'chars': 4753,
                            'bytes': 4753,
                            'gap': None,
                            'resolves': 1,
                            'parts': {'Owner': 851,
                                      'Records': 1422,
                                      'Observable': 1082,
                                      'Tests': 1270},
                            'tests': ('test_retro_doctor_entry_unit',
                                      'test_retro_no_merge',
                                      'test_retro_success',
                                      'test_retro_no_commit',
                                      'test_retro_refusals',
                                      'test_doctor_check_order',
                                      'test_doctor_failures',
                                      'test_doctor_is_read_only',
                                      'test_doctor_cli')}}

PLAN_CHARS = {'19.I': 1811,
 '19.P5.status-projection': 4211,
 '13': 19840,
 '19.P5.baseline-binding-reader': 4622,
 '12': 20224,
 '19.L': 20912,
 '19.P5': 9792,
 '19.P5.retro-doctor-cli': 4753,
 '18': 13459}

FILE_SIZES = {'chupa/status.py': {'chars': 4368, 'bytes': 4368},
 'tests/test_status.py': {'chars': 2343, 'bytes': 2343},
 'chupa/scorecard.py': {'chars': 3870, 'bytes': 3870},
 'tests/test_scorecard.py': {'chars': 13158, 'bytes': 13158},
 'chupa/box.py': {'chars': 16317, 'bytes': 16317},
 'tests/test_box.py': {'chars': 17312, 'bytes': 17312},
 'chupa/retro.py': {'chars': 17582, 'bytes': 17582},
 'tests/test_retro.py': {'chars': 16978, 'bytes': 16978},
 'chupa/__main__.py': {'chars': 16273, 'bytes': 16273},
 'tests/test_cli.py': {'chars': 12262, 'bytes': 12262},
 'chupa/journal.py': {'chars': 11118, 'bytes': 11118},
 'chupa/config.py': {'chars': 12245, 'bytes': 12245},
 'chupa/policy.py': {'chars': 3289, 'bytes': 3289},
 'tests/test_policy.py': {'chars': 4173, 'bytes': 4173},
 'chupa/author.py': {'chars': 12813, 'bytes': 12813},
 'tests/test_author.py': {'chars': 11058, 'bytes': 11058},
 'tests/test_retro_box.py': {'chars': 8080, 'bytes': 8081},
 'chupa/providers.py': {'chars': 27676, 'bytes': 27676},
 'tests/test_seeded_phase3_core.py': {'chars': 5425, 'bytes': 5425}}

IMPLEMENT_SPEC_CHARS = 4775

RENDER_OVERHEAD = 2000

HEADROOM_CHARS = 300000

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

CREATED = {'status-projection': (),
 'baseline-binding-reader': ('chupa/baseline.py', 'tests/test_baseline.py'),
 'phase5-continue-04': ('tests/test_seeded_phase5_04.py',)}

FENCED_EXISTING = {'status-projection': ('chupa/status.py',
                       'tests/test_status.py',
                       'chupa/scorecard.py',
                       'tests/test_scorecard.py',
                       'chupa/box.py',
                       'tests/test_box.py',
                       'chupa/retro.py',
                       'tests/test_retro.py',
                       'chupa/__main__.py',
                       'tests/test_cli.py'),
 'baseline-binding-reader': ('chupa/journal.py',
                             'chupa/config.py',
                             'chupa/policy.py',
                             'tests/test_policy.py',
                             'chupa/author.py',
                             'tests/test_author.py',
                             'tests/test_retro_box.py'),
 'phase5-continue-04': ()}

FENCE_ADDITIONS = {'status-projection': {}, 'baseline-binding-reader': {}}

CLOSURE_SCAN = {'chupa': {'files_read': 50,
           'matched_lines': 60,
           'sha256': '1eb52285ca47e6eabf41248ac43e513c6c82e07b65b7d1dcba127adb8ff819f1'},
 'eval': {'files_read': 57,
          'matched_lines': 59,
          'sha256': '965dd34f027d2f4700b1f8761af973843a579b50a76173d85da3e262a94a357d'},
 'tests': {'files_read': 121,
           'matched_lines': 231,
           'sha256': 'a84f6ce65682e71237234c221a32f36f1cbac660b7e1f53ef0459d03dadf3116'}}

CLOSURE_DECISIONS = {'19.L.2': {'status-projection': 'tests/test_status.py:36 equates the direct render and CLI '
                                 'output; real provenance forces its fenced migration. '
                                 'tests/test_cli.py:218 parses sections but does not assert an '
                                 'exact section set. tests/test_reject_queue.py:59 asserts '
                                 'retained Reject text.',
            'baseline-binding-reader': 'tests/test_policy.py:9 imports go_binds and lines 49-65 '
                                       'consume it; this fenced suite migrates to the new reader '
                                       'while all starting-state assertions remain.'},
 '19.L.3': {'status-projection': 'Status, retro and scorecard are reachable already. No '
                                 'construction dormancy, verb absence, or negative composition '
                                 'assertion is activated.',
            'baseline-binding-reader': 'Author is reachable already. The interim reader is '
                                       'replaced in place; no dormant component or Phase 6 hold is '
                                       'activated.'},
 '19.L.4': {'status-projection': '19.P5.status-projection assigns status projection/rendering to '
                                 'chupa/status.py and composition to chupa/__main__.py; no new '
                                 'module.',
            'baseline-binding-reader': '19.P5.baseline-binding-reader assigns new '
                                       'chupa/baseline.py and entry tests/test_baseline.py; no '
                                       'invented owner.'},
 '19.L.5': {'status-projection': 'chupa/__main__.py:210 and tests/test_status.py:31,42 call '
                                 'project; tests/test_serve.py:1420,1431 compares retained fields '
                                 'through project. Keep its journal-only calling shape and '
                                 'last_states/reject_queue signatures; no new public operation or '
                                 'pinned allowlist is changed.',
            'baseline-binding-reader': 'chupa/author.py:14,191 and tests/test_policy.py:9,49-65 '
                                       'are every go_binds reader/import. '
                                       'eval/harness.py:36,178,343 consumes only '
                                       'baseline_identity, BASELINE_SIGNAL and TIERS, all '
                                       'retained; its preservation test is Verification only.'}}

CALLERS = {'go_binds': ('chupa/author.py', 'tests/test_policy.py'),
 'project': ('chupa/__main__.py', 'tests/test_status.py', 'tests/test_serve.py'),
 'baseline_identity_producer': ('eval/harness.py',)}

DELIMITER_FREE_CONTEXT = {'chupa/status.py': True,
 'tests/test_status.py': True,
 'chupa/scorecard.py': True,
 'tests/test_scorecard.py': True,
 'chupa/box.py': True,
 'tests/test_box.py': True,
 'chupa/retro.py': True,
 'tests/test_retro.py': True,
 'chupa/__main__.py': True,
 'tests/test_cli.py': True,
 'chupa/journal.py': True,
 'chupa/config.py': True,
 'chupa/policy.py': True,
 'tests/test_policy.py': True,
 'chupa/author.py': True,
 'tests/test_author.py': True,
 'tests/test_retro_box.py': True,
 'chupa/providers.py': True,
 'tests/test_seeded_phase3_core.py': True}

PREDECESSOR_SHA256 = '728edc3dd972a9031f2f35ba6a1b89990c369393883cc6a33eb127cc6844c970'


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, set(BATCH) - {stem})


def _body(stem):
    return '\n'.join(_ticket(stem).sections.values())


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[u] for u in a['plan'])
            + sum(FILE_SIZES[p]['chars'] for p in (*a['context'], *extra)))


def test_exact_admission_and_finite_suffix():
    assert BATCH == ('status-projection', 'baseline-binding-reader', 'phase5-continue-04')
    assert POSITION == 3 and REGISTRY['phase'] == 5
    assert UNSEEDED_SUFFIX == (('status-projection', 'baseline-binding-reader'),
                               ('retro-doctor-cli',), ('phase5-exit',))
    assert UNSEEDED_SUFFIX == tuple(tuple(a) for a in REGISTRY['admissions'][POSITION:])
    assert tuple(REGISTRY['seeds']) == tuple(s for a in REGISTRY['admissions'] for s in a)
    assert len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    for i, admission in enumerate(REGISTRY['admissions']):
        terminal = i == len(REGISTRY['admissions']) - 1
        assert len(admission) + (not terminal) <= MAX_SEEDS_PER_ADMISSION
        assert len(REGISTRY['admissions'][i+1:]) < len(REGISTRY['admissions'][i:])
        for stem in admission:
            if REGISTRY['seeds'][stem].get('deep'):
                assert admission == [stem]
        if terminal:
            assert admission == ['phase5-exit'] and REGISTRY['seeds']['phase5-exit']['exit']


@pytest.mark.parametrize('stem', BATCH)
def test_grammar_birth_role_edges_and_budgets(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ('medium', 'medium')
    assert t.plan_contract == a['plan']
    assert t.depends == a['depends']
    assert t.scope_fence == a['fence']
    assert t.expected_minutes == a['expected'] < t.stuck_minutes == a['stuck'] <= DRAIN_MAX_TICKET_MINUTES
    if stem in BATCH[:2]:
        row = REGISTRY['seeds'][stem]
        assert not row.get('deep')
        assert t.plan_contract == ('19.I', '19.P5.' + stem, str(row['cite'][0]))
        assert set(t.depends) == {'phase5-continue-03', *row['depends']}
        assert set(t.scope_fence) == set(row['fence']) | set(FENCE_ADDITIONS[stem])
        assert '19.L' not in t.plan_contract and '19.P5' not in t.plan_contract
    else:
        assert t.depends == BATCH[:2]
        assert t.plan_contract == ('19.L', '19.I', '19.P5', '19.P5.retro-doctor-cli', '18', '13')
        assert t.scope_fence == ('tickets', 'tests/test_seeded_phase5_04.py')


@pytest.mark.parametrize('stem', BATCH)
def test_fixed_maximum_effort_render_and_context_partition(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert not set(t.context) & set(t.on_demand)
    assert set(FENCED_EXISTING[stem]) <= set(t.context) | set(t.on_demand)
    assert not set(CREATED[stem]) & set((*t.context, *t.on_demand))
    assert not set(CREATED['baseline-binding-reader']) & set(t.context)
    assert render_chars(stem) <= HEADROOM_CHARS == 300_000
    for path in t.on_demand:
        assert render_chars(stem, (path,)) > HEADROOM_CHARS
    assert all(DELIMITER_FREE_CONTEXT[p] for p in t.context)
    assert all(not p.startswith(('specs/', 'tickets/')) for p in t.context)
    assert 'tests/test_seeded_phase5_03.py' not in t.context
    if stem == BATCH[2]:
        assert t.context == ('tests/test_seeded_phase3_core.py',)
    else:
        assert not set(CREATED[stem]) & set(FILE_SIZES)


def test_fixed_snapshots_and_seed_bytes():
    assert re.fullmatch(r'[0-9a-f]{40}', AUTHORING_HEAD)
    assert re.fullmatch(r'[0-9a-f]{40}', IDIOM_BLOB)
    assert re.fullmatch(r'[0-9a-f]{64}', PREDECESSOR_SHA256)
    assert set(AUTHORED) == set(REQUIRED) == set(FENCED_EXISTING) == set(CREATED) == set(BATCH)
    assert IMPLEMENT_SPEC_CHARS > 0 and RENDER_OVERHEAD == 2000
    assert all(n > 0 for n in PLAN_CHARS.values())
    assert all(0 < size['chars'] <= size['bytes'] for size in FILE_SIZES.values())
    for stem, a in AUTHORED.items():
        assert 0 < a['chars'] <= a['bytes']
        assert hashlib.sha256((ROOT / ticket_path(stem)).read_bytes()).hexdigest() == a['sha256']


def test_required_depth_and_all_named_obligations():
    assert REQUIRED == {
        'status-projection': ('19.P5.status-projection',),
        'baseline-binding-reader': ('19.P5.baseline-binding-reader',),
        'phase5-continue-04': ('19.P5.retro-doctor-cli',),
    }
    expected = {
        '19.P5.status-projection': (
            'test_status_entry_unit', 'test_status_current_window_scorecard',
            'test_status_production_provenance', 'test_status_preserves_sections_and_is_write_free',
            'test_status_surfaces_confirmed_class_tombstones', 'test_status_on_an_empty_journal',
            'test_status_projects_the_journal', 'test_status_is_deterministic'),
        '19.P5.baseline-binding-reader': (
            'test_baseline_entry_unit', 'test_baseline_states_and_latest_signal',
            'test_baseline_routing_and_spec_drift', 'test_baseline_invalid_inputs_fail_closed',
            'test_author_uses_baseline_resolution',
            'test_bootstrap_without_a_go_or_with_phase_one_no_go_drafts_every_row',
            'test_standing_go_uses_the_table_and_each_override_drafts',
            'test_reopened_retro_ticket_starts_draft'),
        '19.P5.retro-doctor-cli': (
            'test_retro_doctor_entry_unit', 'test_retro_no_merge', 'test_retro_success',
            'test_retro_no_commit', 'test_retro_refusals', 'test_doctor_check_order',
            'test_doctor_failures', 'test_doctor_is_read_only', 'test_doctor_cli'),
    }
    assert set(ENTRY_DEPTH) == set(expected)
    for uid, e in ENTRY_DEPTH.items():
        assert e['gap'] is None and e['resolves'] == 1
        assert set(e['parts']) == {'Owner', 'Records', 'Observable', 'Tests'}
        assert all(n > 0 for n in e['parts'].values())
        assert e['chars'] == PLAN_CHARS[uid] and 0 < e['chars'] <= e['bytes']
        assert re.fullmatch(r'[0-9a-f]{64}', e['sha256'])
        assert e['tests'] == expected[uid]
        for stem, units in REQUIRED.items():
            if uid in units:
                assert all(name in _body(stem) for name in expected[uid])
    for stem in BATCH:
        assert all(name in _body(stem) for name in
                   ('required_units', 'resolve_plan_contract', 'entry_unit_gap', 'test_plan_lint'))


def test_caller_closure_ownership_and_preservation():
    assert FENCE_ADDITIONS == {'status-projection': {}, 'baseline-binding-reader': {}}
    assert set(CLOSURE_DECISIONS) == {'19.L.2', '19.L.3', '19.L.4', '19.L.5'}
    assert all(set(rows) == set(BATCH[:2]) and all(rows.values())
               for rows in CLOSURE_DECISIONS.values())
    assert CALLERS['go_binds'] == ('chupa/author.py', 'tests/test_policy.py')
    assert CALLERS['project'] == ('chupa/__main__.py', 'tests/test_status.py', 'tests/test_serve.py')
    assert CALLERS['baseline_identity_producer'] == ('eval/harness.py',)
    assert set(CLOSURE_SCAN) == {'chupa', 'eval', 'tests'}
    for scan in CLOSURE_SCAN.values():
        assert scan['files_read'] > 0 and scan['matched_lines'] > 0
        assert re.fullmatch(r'[0-9a-f]{64}', scan['sha256'])
    status = _body('status-projection')
    for phrase in ('project_window', 'production_evidence', 'project_scorecard', 'Git.rev_parse',
                   'injected clock', 'loaded retro spec version', 'all old section labels and text',
                   'direct-render/CLI equality', 'project calling shape', 'last_states/reject_queue',
                   'Keep every tests/test_retro.py assertion unchanged'):
        assert phrase in status
    baseline = _body('baseline-binding-reader')
    for phrase in ('New chupa/baseline.py is owned by 19.P5.baseline-binding-reader',
                   'Replace policy.go_binds in place', 'remove the interim reader',
                   'Keep policy.baseline_identity, BASELINE_SIGNAL and TIERS',
                   "eval/harness.py's identity producer", 'existing registry fallback',
                   'real torn journal tail', "policy.start_state's go operand"):
        assert phrase in baseline
    assert CREATED['baseline-binding-reader'] == ('chupa/baseline.py', 'tests/test_baseline.py')
    assert not CREATED['status-projection']
    preservation = {
        'status-projection': ('tests/test_serve.py', 'tests/test_reject_queue.py'),
        'baseline-binding-reader': ('tests/test_eval_harness.py',),
    }
    for stem, suites in preservation.items():
        t = _ticket(stem)
        tokens = {token for argv in t.verification for token in argv}
        assert set(suites) <= tokens
        assert not set(suites) & set((*t.scope_fence, *t.context, *t.on_demand))


def test_successor_tiers_terminal_depth_and_check_custody():
    text = _body(BATCH[2])
    for phrase in ('Position 04', 'admissions[4:]', 'position 05', 'admissions[5:]',
                   'exactly retro-doctor-cli and phase5-continue-05',
                   'phase5-continue-05 depends on retro-doctor-cli',
                   'last admission authors only phase5-exit without a successor',
                   'medium/medium', 'deep: true', 'KNOWN-DEEP high/high',
                   'KNOWN-HARD high/high', '19.P6', 'section 18', 'section 13',
                   'tests/test_seeded_phase5_05.py', '300,000 characters',
                   'seeding.max_seeds_per_admission', 'drain.max_ticket_minutes',
                   'only the new batch test is committed', 'requisition_review',
                   'tickets/phase5-continue-04/checks.json', 'single ticket-plane seed lift',
                   'Retain approved bytes while ticket_sha matches', 're-author only snagged seeds',
                   '19.L rules 2-5', 'Source new chupa/doctor.py ownership from the cited entry'):
        assert phrase in text
