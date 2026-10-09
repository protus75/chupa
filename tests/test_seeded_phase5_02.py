"""Phase 5 admission 02: fixed authoring snapshots; later fixtures never migrate these measurements."""

import hashlib
import re
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]

AUTHORING_HEAD = '1b08ec372965e2cc88afa2dfdb9801bc8a7f9ef6'

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

POSITION = 2

UNSEEDED_SUFFIX = (('scorecard-reporting',),
 ('status-projection', 'baseline-binding-reader'),
 ('retro-doctor-cli',),
 ('phase5-exit',))

BATCH = ('scorecard-reporting', 'phase5-continue-03')

AUTHORED = {'scorecard-reporting': {'chars': 4404,
                         'bytes': 4404,
                         'sha256': '8737b430dac8a64651215e0dc757cbfafb6c2e4d619d3a8e58b80da26c71e068',
                         'plan': ('19.I', '19.P5.scorecard-reporting', '14'),
                         'context': ('chupa/retro.py', 'tests/test_retro.py'),
                         'on_demand': (),
                         'depends': ('phase5-continue-02',),
                         'fence': ('chupa/scorecard.py',
                                   'tests/test_scorecard.py',
                                   'chupa/retro.py',
                                   'tests/test_retro.py'),
                         'expected': 60,
                         'stuck': 180},
 'phase5-continue-03': {'chars': 6665,
                        'bytes': 6665,
                        'sha256': '728edc3dd972a9031f2f35ba6a1b89990c369393883cc6a33eb127cc6844c970',
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P5',
                                 '19.P5.status-projection',
                                 '19.P5.baseline-binding-reader',
                                 '13',
                                 '12'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'depends': ('scorecard-reporting',),
                        'fence': ('tickets', 'tests/test_seeded_phase5_03.py'),
                        'expected': 60,
                        'stuck': 180}}

REQUIRED = {'scorecard-reporting': ('19.P5.scorecard-reporting',),
 'phase5-continue-03': ('19.P5.status-projection', '19.P5.baseline-binding-reader')}

ENTRY_DEPTH = {'19.P5.scorecard-reporting': {'sha256': '4ece442f6aad5f09bbbc4ae2ed91be9740179135db245166a1e66c3cd5ec6a73',
                               'chars': 5628,
                               'gap': None,
                               'resolves': 1,
                               'parts': {'Owner': 608,
                                         'Records': 2422,
                                         'Observable': 925,
                                         'Tests': 1524},
                               'tests': ('test_scorecard_entry_unit',
                                         'test_scorecard_uses_completed_check_evidence',
                                         'test_scorecard_catches_resolved_and_upheld_findings',
                                         'test_scorecard_rates_and_prune_threshold',
                                         'test_scorecard_totals_and_rendering')},
 '19.P5.status-projection': {'sha256': '9b68cc56abd993b2d62256d554ed130284e6f7c71dba7154161a857e215a0b86',
                             'chars': 4211,
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
                                             'test_reopened_retro_ticket_starts_draft')}}

PLAN_CHARS = {'19.I': 1811,
 '19.P5.scorecard-reporting': 5628,
 '14': 7360,
 '19.L': 20912,
 '19.P5': 9792,
 '19.P5.status-projection': 4211,
 '19.P5.baseline-binding-reader': 4622,
 '13': 19840,
 '12': 20224}

FILE_SIZES = {'chupa/retro.py': {'chars': 15871, 'bytes': 15871},
 'tests/test_retro.py': {'chars': 16978, 'bytes': 16978},
 'tests/test_seeded_phase3_core.py': {'chars': 5425, 'bytes': 5425}}

IMPLEMENT_SPEC_CHARS = 4896

RENDER_OVERHEAD = 2000

HEADROOM_CHARS = 300000

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

CREATED = ('chupa/scorecard.py', 'tests/test_scorecard.py')

FENCED_EXISTING = ('chupa/retro.py', 'tests/test_retro.py')

FENCE_ADDITIONS = {}

CLOSURE_SCAN = {'chupa': {'files_read': 49,
           'matched_lines': 108,
           'sha256': 'c8a43322c47cb77af7680958758e944e97d7a2d65b116c99f0ed194f2eddc488'},
 'eval': {'files_read': 13,
          'matched_lines': 0,
          'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'},
 'tests': {'files_read': 119,
           'matched_lines': 597,
           'sha256': '3d96f0fe16ceb8e3a3b339dbeba2a9ae26ef1ae846efa7c3c049bf5bc01b36f3'}}

PREDECESSOR_SHA256 = 'ba12168f00aff22003c68ce97caa6509c743accf46bbbda08ff45e3c94736d6c'

PRESERVATION = {'tests/test_driver.py': 'Shared exit-window materialization retains project_window signature and '
                         'event suffix.',
 'tests/test_stages.py': 'Stages.driver and resolve_exit_window remain unchanged; no composition '
                         'arity change.',
 'tests/test_retro_box.py': 'Proposal extraction reads the retained receipt JSON block; Box bridge '
                            'remains unchanged.',
 'tests/test_vocabularies.py': 'Projection writes no new signal or journal vocabulary.',
 'tests/test_plan_lint.py': 'Entry helper proofs are created in tests/test_scorecard.py, not added '
                            'to plan lint.'}

CLOSURE_DECISIONS = {'19.L.2': 'tests/test_retro.py floor preserves every assertion; new expectations belong to '
           'tests/test_scorecard.py. No old output equality or absence assertion is flipped '
           'outside that floor.',
 '19.L.3': 'Retro invoker and Box activation are already reachable; no dormant predecessor becomes '
           'activated by this pure projection.',
 '19.L.4': '19.P5.scorecard-reporting explicitly owns new chupa/scorecard.py; the entry test is '
           'created in tests/test_scorecard.py.',
 '19.L.5': 'Window construction is local to fenced project_window; retain project_window, '
           'measurements, production_evidence, render_report, Retro public signatures. '
           'chupa/stages.py and tests/test_retro_box.py callers need no edits. No retro public '
           'operation allowlist was found.'}

DELIMITER_FREE_CONTEXT = {'chupa/retro.py': True, 'tests/test_retro.py': True, 'tests/test_seeded_phase3_core.py': True}

SUCCESSOR_LOOKAHEAD = {'unit': '19.P5.retro-doctor-cli',
 'sha256': 'ed89788c644e34de4d479e398b69ec16b384bb420a5468a8a579fd3c53e5222c',
 'chars': 4753,
 'gap': None,
 'resolves': 1,
 'parts': ('Owner', 'Records', 'Observable', 'Tests')}

def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, set(BATCH) - {stem})


def _body(ticket):
    return '\n'.join(ticket.sections.values())


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[uid] for uid in a['plan'])
            + sum(FILE_SIZES[p]['chars'] for p in (*a['context'], *extra)))


def test_exact_admission_suffix_and_cap():
    assert BATCH == ('scorecard-reporting', 'phase5-continue-03')
    assert POSITION == 2 and REGISTRY['phase'] == 5
    assert UNSEEDED_SUFFIX == (('scorecard-reporting',),
        ('status-projection', 'baseline-binding-reader'), ('retro-doctor-cli',), ('phase5-exit',))
    assert UNSEEDED_SUFFIX == tuple(tuple(a) for a in REGISTRY['admissions'][POSITION:])
    assert tuple(REGISTRY['seeds']) == tuple(s for a in REGISTRY['admissions'] for s in a)
    assert len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    for i, admission in enumerate(REGISTRY['admissions'][POSITION:], POSITION):
        terminal = i == len(REGISTRY['admissions']) - 1
        assert len(admission) + (not terminal) <= MAX_SEEDS_PER_ADMISSION
        assert len(REGISTRY['admissions'][i+1:]) < len(REGISTRY['admissions'][i:])
        if terminal:
            assert admission == ['phase5-exit'] and REGISTRY['seeds'][admission[0]]['exit']


@pytest.mark.parametrize('stem', BATCH)
def test_grammar_confirmed_birth_citations_edges_fence_budgets(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ('medium', 'medium')
    assert t.plan_contract == a['plan'] and t.scope_fence == a['fence']
    assert t.depends == a['depends']
    assert t.expected_minutes == a['expected'] < t.stuck_minutes == a['stuck'] <= DRAIN_MAX_TICKET_MINUTES
    if stem == BATCH[0]:
        assert t.depends == ('phase5-continue-02',)
        assert t.plan_contract == ('19.I', '19.P5.scorecard-reporting', '14')
        assert set(t.scope_fence) == set(REGISTRY['seeds'][stem]['fence']) | set(FENCE_ADDITIONS)
        assert not REGISTRY['seeds'][stem].get('deep')
    else:
        assert t.depends == ('scorecard-reporting',)
        assert t.scope_fence == ('tickets', 'tests/test_seeded_phase5_03.py')
        assert t.plan_contract == ('19.L', '19.I', '19.P5', '19.P5.status-projection',
                                  '19.P5.baseline-binding-reader', '13', '12')


@pytest.mark.parametrize('stem', BATCH)
def test_fixed_maximum_effort_render_and_context_closure(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert not set(t.context) & set(t.on_demand)
    assert render_chars(stem) <= HEADROOM_CHARS == 300_000
    for path in t.on_demand:
        assert render_chars(stem, (path,)) > HEADROOM_CHARS
    if stem == BATCH[0]:
        assert set(FENCED_EXISTING) <= set(t.context) | set(t.on_demand)
        assert not set(CREATED) & set((*t.context, *t.on_demand))
    else:
        assert t.context == ('tests/test_seeded_phase3_core.py',) and not t.on_demand
    assert all(not p.startswith(('specs/', 'tickets/')) for p in t.context)
    assert 'tests/test_seeded_phase5_03.py' not in t.context
    assert all(DELIMITER_FREE_CONTEXT[p] for p in t.context)


def test_authoring_snapshots_and_ticket_identity():
    assert re.fullmatch(r'[0-9a-f]{40}', AUTHORING_HEAD)
    assert re.fullmatch(r'[0-9a-f]{40}', IDIOM_BLOB)
    assert re.fullmatch(r'[0-9a-f]{64}', PREDECESSOR_SHA256)
    assert set(AUTHORED) == set(BATCH)
    for size in FILE_SIZES.values():
        assert 0 < size['chars'] <= size['bytes']
    for stem, a in AUTHORED.items():
        assert hashlib.sha256((ROOT / ticket_path(stem)).read_bytes()).hexdigest() == a['sha256']
        assert 0 < a['chars'] <= a['bytes']
    assert all(n > 0 for n in PLAN_CHARS.values())


def test_required_entry_depth_and_named_obligations():
    assert REQUIRED == {'scorecard-reporting': ('19.P5.scorecard-reporting',),
        'phase5-continue-03': ('19.P5.status-projection', '19.P5.baseline-binding-reader')}
    assert set(ENTRY_DEPTH) == {u for units in REQUIRED.values() for u in units}
    for uid, e in ENTRY_DEPTH.items():
        assert e['gap'] is None and e['resolves'] == 1
        assert set(e['parts']) == {'Owner', 'Records', 'Observable', 'Tests'}
        assert all(n > 0 for n in e['parts'].values())
        assert e['chars'] == PLAN_CHARS[uid]
        assert re.fullmatch(r'[0-9a-f]{64}', e['sha256'])
        for stem, units in REQUIRED.items():
            if uid in units:
                assert all(name in _body(_ticket(stem)) for name in e['tests'])
    assert ENTRY_DEPTH['19.P5.scorecard-reporting']['tests'] == (
        'test_scorecard_entry_unit', 'test_scorecard_uses_completed_check_evidence',
        'test_scorecard_catches_resolved_and_upheld_findings', 'test_scorecard_rates_and_prune_threshold',
        'test_scorecard_totals_and_rendering')
    for stem in BATCH:
        assert all(name in _body(_ticket(stem)) for name in
                   ('required_units', 'resolve_plan_contract', 'entry_unit_gap', 'test_plan_lint'))


def test_earned_closure_and_preservation():
    t = _ticket(BATCH[0])
    assert FENCE_ADDITIONS == {}
    assert set(CLOSURE_SCAN) == {'chupa', 'eval', 'tests'}
    assert all(s['files_read'] > 0 and s['matched_lines'] >= 0
               and re.fullmatch(r'[0-9a-f]{64}', s['sha256']) for s in CLOSURE_SCAN.values())
    assert set(CLOSURE_DECISIONS) == {'19.L.2', '19.L.3', '19.L.4', '19.L.5'}
    commands = {token for argv in t.verification for token in argv}
    assert set(PRESERVATION) <= commands
    assert not set(PRESERVATION) & set((*t.context, *t.on_demand, *t.scope_fence))
    for phrase in ('Keep every tests/test_retro.py assertion unchanged',
                   'test_receipt_uses_engine_provenance_usage_calibration_and_tombstones',
                   'Preserve public signatures and constructor arity',
                   'Stages.driver/Pipeline.stages', 'New chupa/scorecard.py is owned by that entry'):
        assert phrase in _body(t)
    assert 'tests/test_scorecard.py' in CREATED and 'tests/test_scorecard.py' in t.scope_fence


def test_successor_consumption_tiers_depth_and_check_custody():
    # The prior snag was a missing lookahead entry. Its repaired, committed
    # authoring snapshot is evidence here; later plan edits cannot change it.
    assert SUCCESSOR_LOOKAHEAD['unit'] == '19.P5.retro-doctor-cli'
    assert SUCCESSOR_LOOKAHEAD['gap'] is None
    assert SUCCESSOR_LOOKAHEAD['resolves'] == 1
    assert SUCCESSOR_LOOKAHEAD['parts'] == ('Owner', 'Records', 'Observable', 'Tests')
    assert SUCCESSOR_LOOKAHEAD['chars'] > 0
    assert re.fullmatch(r'[0-9a-f]{64}', SUCCESSOR_LOOKAHEAD['sha256'])
    text = _body(_ticket(BATCH[1]))
    for phrase in ('Position 03', 'admissions[3:]', 'position 04', 'admissions[4:]',
                   'phase5-continue-04 depends on both status-projection and baseline-binding-reader',
                   'last admission authors only phase5-exit without a successor',
                   'medium/medium', 'deep: true', 'KNOWN-DEEP high/high', 'KNOWN-HARD high/high',
                   '19.P5.retro-doctor-cli', 'tests/test_seeded_phase5_04.py',
                   'requisition_review', 'single ticket-plane seed lift',
                   'Retain approved bytes while ticket_sha matches', 're-author only snagged seeds',
                   'seeding.max_seeds_per_admission', 'drain.max_ticket_minutes',
                   'only the new batch test is committed', 'retro-box-activation', 'go_binds'):
        assert phrase in text
