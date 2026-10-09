"""Phase 5 admission 04: immutable authoring evidence and seed identity.

Check owns requisition approvals and the single ticket-plane lift.
Only this batch test belongs to the code branch. Render operands are fixed.
"""

import hashlib
import re
from pathlib import Path

import pytest

from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parents[1]

AUTHORING_HEAD = 'b64f3c9ee8001e54db1c5c49051985fc8089fef9'

IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

POSITION = 4

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

UNSEEDED_SUFFIX = (('retro-doctor-cli',), ('phase5-exit',))

BATCH = ('retro-doctor-cli', 'phase5-continue-05')

AUTHORED = {'retro-doctor-cli': {'chars': 4572,
                      'bytes': 4572,
                      'sha256': 'fd22939843bcf1e00cecc99c0e128281c1e36167701fdbb4fffd4ed90c4f6b51',
                      'plan': ('19.I', '19.P5.retro-doctor-cli', '18'),
                      'context': ('chupa/retro.py',
                                  'chupa/__main__.py',
                                  'tests/test_retro.py',
                                  'tests/test_cli.py',
                                  'chupa/runner.py',
                                  'chupa/seams.py',
                                  'chupa/lockfile.py',
                                  'chupa/journal.py',
                                  'chupa/config.py'),
                      'on_demand': (),
                      'depends': ('phase5-continue-04',),
                      'fence': ('chupa/doctor.py',
                                'tests/test_doctor.py',
                                'chupa/retro.py',
                                'chupa/__main__.py',
                                'tests/test_retro.py',
                                'tests/test_cli.py'),
                      'expected': 60,
                      'stuck': 180},
 'phase5-continue-05': {'chars': 5359,
                        'bytes': 5359,
                        'sha256': '4b24963461a6a0f17819bd61a4ecf3412f5e80c292febfdf7cb3555e6409b76a',
                        'plan': ('19.L', '19.I', '19.P5', '19.P6', '13'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'depends': ('retro-doctor-cli',),
                        'fence': ('tickets', 'tests/test_seeded_phase5_05.py'),
                        'expected': 60,
                        'stuck': 180}}

REQUIRED = {'retro-doctor-cli': ('19.P5.retro-doctor-cli',), 'phase5-continue-05': ()}

AUTHOR_CONTINUATION_REQUIRED = ('19.P5.retro-doctor-cli',)

ENTRY_DEPTH = {'sha256': 'ed89788c644e34de4d479e398b69ec16b384bb420a5468a8a579fd3c53e5222c',
 'chars': 4753,
 'bytes': 4753,
 'resolves': 1,
 'gap': None,
 'parts': {'Owner': 851, 'Records': 1422, 'Observable': 1082, 'Tests': 1270},
 'missing_part_rejected': {'Owner': True, 'Records': True, 'Observable': True, 'Tests': True},
 'tests': ('test_retro_doctor_entry_unit',
           'test_retro_no_merge',
           'test_retro_success',
           'test_retro_no_commit',
           'test_retro_refusals',
           'test_doctor_check_order',
           'test_doctor_failures',
           'test_doctor_is_read_only',
           'test_doctor_cli')}

PLAN_SIZES = {'19.I': {'chars': 1811, 'bytes': 1811},
 '19.P5.retro-doctor-cli': {'chars': 4753, 'bytes': 4753},
 '18': {'chars': 13459, 'bytes': 13459},
 '19.L': {'chars': 20912, 'bytes': 20912},
 '19.P5': {'chars': 9792, 'bytes': 9792},
 '19.P6': {'chars': 11595, 'bytes': 11595},
 '13': {'chars': 19840, 'bytes': 19840}}

FILE_SIZES = {'chupa/retro.py': {'chars': 17582, 'bytes': 17582},
 'chupa/__main__.py': {'chars': 16771, 'bytes': 16771},
 'tests/test_retro.py': {'chars': 16978, 'bytes': 16978},
 'tests/test_cli.py': {'chars': 12620, 'bytes': 12620},
 'chupa/runner.py': {'chars': 38508, 'bytes': 38508},
 'chupa/seams.py': {'chars': 10148, 'bytes': 10148},
 'chupa/lockfile.py': {'chars': 3273, 'bytes': 3273},
 'chupa/journal.py': {'chars': 11118, 'bytes': 11118},
 'chupa/config.py': {'chars': 12245, 'bytes': 12245},
 'tests/test_seeded_phase3_core.py': {'chars': 5425, 'bytes': 5425}}

IMPLEMENT_SPEC_CHARS = 4896

RENDER_OVERHEAD = 2000

HEADROOM_CHARS = 300000

MAX_SEEDS_PER_ADMISSION = 3

DRAIN_MAX_TICKET_MINUTES = 180

CREATED = {'retro-doctor-cli': ('chupa/doctor.py', 'tests/test_doctor.py'),
 'phase5-continue-05': ('tests/test_seeded_phase5_05.py',)}

FENCED_EXISTING = {'retro-doctor-cli': ('chupa/retro.py',
                      'chupa/__main__.py',
                      'tests/test_retro.py',
                      'tests/test_cli.py'),
 'phase5-continue-05': ()}

FENCE_ADDITIONS = {'retro-doctor-cli': {}}

CLOSURE_PATTERNS = ('\\bRetro\\b|project_window|prepare_pipeline|\\.prepare\\(|\\.driver\\(',
 'retro|doctor|not hasattr|__all__|choices|allowlist|is_dormant')

CLOSURE_SCAN = {'chupa': {'files_read': 51,
           'matched_lines': 122,
           'sha256': '04bd7364a0c0009fb9c8b45e18f5c7d6ff9d17915f78a9918f1af69b73da6d18'},
 'eval': {'files_read': 13,
          'matched_lines': 3,
          'sha256': '825b85900b8f4298dd4a9425408f5e3fc37d29343fa4b25a9f9b0af153f06671'},
 'tests': {'files_read': 123,
           'matched_lines': 763,
           'sha256': 'c0bc90e701d50295aebb4b74342e4d8325e3e447b2b2c859860e93493d8cf6c7'}}

COPY_VIOLATIONS = {'retro-doctor-cli': (), 'phase5-continue-05': ()}

# Every embedded file was read and checked at authoring, before later edits can change it.
DELIMITER_FREE_CONTEXT = {
    'chupa/retro.py': True, 'chupa/__main__.py': True,
    'tests/test_retro.py': True, 'tests/test_cli.py': True,
    'chupa/runner.py': True, 'chupa/seams.py': True,
    'chupa/lockfile.py': True, 'chupa/journal.py': True, 'chupa/config.py': True,
    'tests/test_seeded_phase3_core.py': True,
}

PREDECESSOR_SHA256 = 'c89d130b4c8f023d2b8ec013d0afaefbbcfcda542e98a93091e873097b75403c'

CLOSURE_DECISIONS = {'19.L.2': 'tests/test_cli.py:201-245 retains status sections and output; '
           'tests/test_retro.py:150-288 retains recovery, suppression, provenance and proposal '
           'assertions. No existing test pins retro/doctor verb absence. No contradicted assertion '
           'outside the registry floor.',
 '19.L.3': 'chupa/retro.py:184 is already production reachable via chupa/__main__.py:254. No '
           'dormant predecessor fixture is activated; the new doctor owner has no predecessor '
           'construction ticket.',
 '19.L.4': '19.P5.retro-doctor-cli Owner assigns new chupa/doctor.py and CLI composition; Tests '
           'assigns tests/test_doctor.py and tests/test_cli.py. No invented module owner.',
 '19.L.5': 'Keep Retro.__init__, driver, commit_report, project_window, and '
           'runner.pipeline/prepare signatures. Direct Retro constructions: chupa/__main__.py:254, '
           'tests/test_drain.py:970, tests/test_retro.py:31,217, tests/test_retro_box.py:59, '
           'tests/test_stages.py:44,50, tests/test_daemon_composition.py:2027. Existing callers '
           'keep their calling shapes; tests/test_restart_timers.py:101 asserts only serve '
           'inclusion. No public-operation allowlist pins retro or doctor absence. No eval caller '
           'changes.'}


def _ticket(stem):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, set(BATCH) - {stem})


def _body(stem):
    return '\n'.join(_ticket(stem).sections.values())


def render_chars(stem, extra=()):
    a = AUTHORED[stem]
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_SIZES[u]['chars'] for u in a['plan'])
            + sum(FILE_SIZES[p]['chars'] for p in (*a['context'], *extra)))


def test_exact_admission_order_finite_suffix_and_all_caps():
    assert BATCH == ('retro-doctor-cli', 'phase5-continue-05')
    assert POSITION == 4 and REGISTRY['phase'] == 5
    assert UNSEEDED_SUFFIX == (('retro-doctor-cli',), ('phase5-exit',))
    assert UNSEEDED_SUFFIX == tuple(tuple(a) for a in REGISTRY['admissions'][POSITION:])
    assert tuple(REGISTRY['seeds']) == tuple(s for a in REGISTRY['admissions'] for s in a)
    assert REGISTRY['admissions'] == [
        ['retro-drain-invoker'], ['retro-box-activation'], ['scorecard-reporting'],
        ['status-projection', 'baseline-binding-reader'], ['retro-doctor-cli'], ['phase5-exit']]
    assert len(BATCH) <= MAX_SEEDS_PER_ADMISSION == 3
    preceding = set()
    for i, admission in enumerate(REGISTRY['admissions']):
        terminal = i == len(REGISTRY['admissions']) - 1
        assert len(admission) + (not terminal) <= MAX_SEEDS_PER_ADMISSION
        assert len(REGISTRY['admissions'][i+1:]) < len(REGISTRY['admissions'][i:])
        for stem in admission:
            row = REGISTRY['seeds'][stem]
            assert set(row.get('depends', ())) <= preceding | set(admission)
            if row.get('deep'):
                assert admission == [stem]
        preceding.update(admission)
        if terminal:
            assert admission == ['phase5-exit'] and REGISTRY['seeds']['phase5-exit']['exit']


@pytest.mark.parametrize('stem', BATCH)
def test_intake_grammar_confirmed_birth_role_edges_fence_and_budget(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ('medium', 'medium')
    assert t.plan_contract == a['plan']
    assert t.depends == a['depends']
    assert t.scope_fence == a['fence']
    assert t.expected_minutes == a['expected'] < t.stuck_minutes == a['stuck'] <= DRAIN_MAX_TICKET_MINUTES
    if stem == BATCH[0]:
        row = REGISTRY['seeds'][stem]
        assert not row.get('deep')
        assert t.plan_contract == ('19.I', '19.P5.retro-doctor-cli', str(row['cite'][0]))
        assert t.depends == ('phase5-continue-04', *row.get('depends', ()))
        assert set(t.scope_fence) == set(row['fence']) | set(FENCE_ADDITIONS[stem])
        assert '19.L' not in t.plan_contract and '19.P5' not in t.plan_contract
    else:
        assert t.depends == BATCH[:1]
        assert t.plan_contract == ('19.L', '19.I', '19.P5', '19.P6', '13')
        assert t.scope_fence == ('tickets', 'tests/test_seeded_phase5_05.py')


@pytest.mark.parametrize('stem', BATCH)
def test_fixed_render_context_closure_and_created_path_exclusion(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert not set(t.context) & set(t.on_demand)
    assert set(FENCED_EXISTING[stem]) <= set(t.context) | set(t.on_demand)
    created = {path for paths in CREATED.values() for path in paths}
    assert not created & set((*t.context, *t.on_demand))
    assert all(not p.startswith(('specs/', 'tickets/')) for p in t.context)
    assert all(DELIMITER_FREE_CONTEXT[p] for p in t.context)
    assert 'tests/test_seeded_phase5_04.py' not in t.context
    assert render_chars(stem) <= HEADROOM_CHARS == 400_000 * .75
    for path in t.on_demand:
        assert render_chars(stem, (path,)) > HEADROOM_CHARS
    if stem == BATCH[1]:
        assert t.context == ('tests/test_seeded_phase3_core.py',)


def test_authoring_snapshots_and_approved_byte_identity():
    assert re.fullmatch(r'[0-9a-f]{40}', AUTHORING_HEAD)
    assert re.fullmatch(r'[0-9a-f]{40}', IDIOM_BLOB)
    assert re.fullmatch(r'[0-9a-f]{64}', PREDECESSOR_SHA256)
    assert set(AUTHORED) == set(REQUIRED) == set(FENCED_EXISTING) == set(CREATED) == set(BATCH)
    assert IMPLEMENT_SPEC_CHARS > 0 and RENDER_OVERHEAD == 2000
    for size in (*PLAN_SIZES.values(), *FILE_SIZES.values(), *AUTHORED.values()):
        assert 0 < size['chars'] <= size['bytes']
    for stem, a in AUTHORED.items():
        assert hashlib.sha256((ROOT / ticket_path(stem)).read_bytes()).hexdigest() == a['sha256']
    assert COPY_VIOLATIONS == {stem: () for stem in BATCH}


def test_required_entry_depth_role_resolution_and_named_owner_obligations():
    uid = '19.P5.retro-doctor-cli'
    assert REQUIRED == {'retro-doctor-cli': (uid,), 'phase5-continue-05': ()}
    assert AUTHOR_CONTINUATION_REQUIRED == (uid,)
    assert ENTRY_DEPTH['gap'] is None and ENTRY_DEPTH['resolves'] == 1
    assert set(ENTRY_DEPTH['parts']) == {'Owner', 'Records', 'Observable', 'Tests'}
    assert all(n > 0 for n in ENTRY_DEPTH['parts'].values())
    assert ENTRY_DEPTH['missing_part_rejected'] == dict.fromkeys(ENTRY_DEPTH['parts'], True)
    assert ENTRY_DEPTH['chars'] == PLAN_SIZES[uid]['chars']
    assert ENTRY_DEPTH['bytes'] == PLAN_SIZES[uid]['bytes']
    assert re.fullmatch(r'[0-9a-f]{64}', ENTRY_DEPTH['sha256'])
    assert ENTRY_DEPTH['tests'] == (
        'test_retro_doctor_entry_unit', 'test_retro_no_merge', 'test_retro_success',
        'test_retro_no_commit', 'test_retro_refusals', 'test_doctor_check_order',
        'test_doctor_failures', 'test_doctor_is_read_only', 'test_doctor_cli')
    text = _body(BATCH[0])
    assert all(name in text for name in ENTRY_DEPTH['tests'])
    for phrase in ('New chupa/doctor.py ownership comes from 19.P5.retro-doctor-cli',
                   'test_retro_doctor_entry_unit in tests/test_cli.py',
                   'in new tests/test_doctor.py', 'phase5-continue-04',
                   'Owner, Records, Observable and Tests', 'missing-part rejection'):
        assert phrase in text
    for stem in BATCH:
        assert all(name in _body(stem) for name in
                   ('required_units', 'resolve_plan_contract', 'entry_unit_gap', 'test_plan_lint'))


def test_earned_closure_callers_and_unchanged_preservation_suites():
    assert FENCE_ADDITIONS == {'retro-doctor-cli': {}}
    assert set(CLOSURE_DECISIONS) == {'19.L.2', '19.L.3', '19.L.4', '19.L.5'}
    assert all(CLOSURE_DECISIONS.values())
    assert set(CLOSURE_SCAN) == {'chupa', 'eval', 'tests'}
    for scan in CLOSURE_SCAN.values():
        assert scan['files_read'] > 0 and scan['matched_lines'] > 0
        assert re.fullmatch(r'[0-9a-f]{64}', scan['sha256'])
    t = _ticket(BATCH[0])
    suites = {'tests/test_scorecard.py', 'tests/test_status.py', 'tests/test_baseline.py',
              'tests/test_retro_box.py', 'tests/test_drain.py', 'tests/test_stages.py'}
    assert suites <= {token for argv in t.verification for token in argv}
    assert not suites & set((*t.scope_fence, *t.context, *t.on_demand))
    for phrase in ('Keep every existing tests/test_retro.py assertion unchanged',
                   "Keep Retro's public signatures", 'Pipeline.stages.driver',
                   'never dispatch a ticket', 'forced=True', 'Lockfile.acquire',
                   'continued checking', 'no traceback'):
        assert phrase in _body(BATCH[0])


def test_terminal_successor_tier_evidence_and_engine_check_custody():
    text = _body(BATCH[1])
    for phrase in ('Position 05', 'admissions[5:]', 'sole remaining suffix [phase5-exit]',
                   'exactly phase5-exit without a successor', 'depends on phase5-continue-05',
                   'transitively consumes every preceding admission payload',
                   'KNOWN-HARD high/high on 19.L evidence', 'medium/medium',
                   'deep: true', 'KNOWN-DEEP high/high', 'Phase 6 core entry units',
                   '300,000 characters', 'seeding.max_seeds_per_admission',
                   'drain.max_ticket_minutes', 'real retro receipt',
                   'transitive-dependency coverage', 'each Phase 5 exit read',
                   'tests/test_phase5_exit.py', 'tests/test_seeded_phase6_core.py',
                   'tests/test_seeded_phase5_05.py', 'No production edits',
                   'only the new batch test is committed', 'requisition_review',
                   'tickets/phase5-continue-05/checks.json', 'single ticket-plane seed lift',
                   'Retain approved bytes while ticket_sha matches', 're-author only snagged seeds'):
        assert phrase in text
