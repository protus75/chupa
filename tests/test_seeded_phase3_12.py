"""Admission 12: two citation-only seeds and fixed authoring snapshots.

YAML was parsed directly between the live P3 registry sentinels at AUTHORING_HEAD,
starting at admissions[12:]. The successor starts at admissions[13:]. No registry
is copied here. All five needed entry units passed entry_unit_gap and
resolve_plan_contract, as did their row citations and sections 13/20/9/15/6/11.
Sizes and plan-unit lengths below are immutable authoring evidence; tests never
measure the live tree or resolve live unit lengths for render arithmetic.
"""

from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

PAYLOADS = ('kill-cli-activation',)

BATCH = ('kill-cli-activation', 'phase3-continue-13')

AUTHORING_HEAD = 'da0d3c6db8f5c5f1ba7caa925d01f5cb5c42690c'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

EDGES = {'kill-cli-activation': ('phase3-continue-12',), 'phase3-continue-13': ('kill-cli-activation',)}

STARTS = {'kill-cli-activation': ('high', 'high'), 'phase3-continue-13': ('medium', 'medium')}

FENCE_FLOORS = {'kill-cli-activation': ('chupa/daemon.py',
                         'chupa/stages.py',
                         'chupa/drain.py',
                         'chupa/__main__.py',
                         'tests/test_kill_signal_journal.py',
                         'tests/test_kill_executor_abort.py',
                         'tests/test_kill_cli_activation.py'),
 'phase3-continue-13': ('tickets', 'tests/test_seeded_phase3_13.py')}

FENCE_ADDITIONS = {'kill-cli-activation': {}, 'phase3-continue-13': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

PLAN_CHARS = {'19.I': 1811,
 '19.P3.kill-cli-activation': 12007,
 '20': 4367,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.heartbeat': 5116,
 '9': 19656,
 '15': 17090,
 '19.P3.restart-timers': 8881,
 '6': 36783,
 '19.P3.flake-detection': 7196,
 '19.P3.flake-release': 5851,
 '11': 26851}

FILE_CHARS = {'chupa/daemon.py': 16571,
 'chupa/stages.py': 50682,
 'chupa/drain.py': 23710,
 'chupa/__main__.py': 8899,
 'tests/test_kill_signal_journal.py': 13912,
 'tests/test_kill_executor_abort.py': 13106,
 'chupa/control.py': 8166,
 'chupa/driver.py': 16659,
 'chupa/runner.py': 33227,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'kill-cli-activation': {'chars': 5114,
                         'plan': ('19.I', '19.P3.kill-cli-activation', '20'),
                         'context': ('chupa/daemon.py',
                                     'chupa/stages.py',
                                     'chupa/drain.py',
                                     'chupa/__main__.py',
                                     'tests/test_kill_signal_journal.py',
                                     'tests/test_kill_executor_abort.py',
                                     'chupa/control.py',
                                     'chupa/driver.py',
                                     'chupa/runner.py'),
                         'on_demand': (),
                         'fenced_existing': ('chupa/daemon.py',
                                             'chupa/stages.py',
                                             'chupa/drain.py',
                                             'chupa/__main__.py',
                                             'tests/test_kill_signal_journal.py',
                                             'tests/test_kill_executor_abort.py'),
                         'created': ('tests/test_kill_cli_activation.py',),
                         'measured_render': 214547},
 'phase3-continue-13': {'chars': 9005,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '19.P3.heartbeat',
                                 '9',
                                 '15',
                                 '19.P3.restart-timers',
                                 '6',
                                 '19.P3.flake-detection',
                                 '19.P3.flake-release',
                                 '11'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets',
                                    'tests/test_seeded_phase3_13.py'),
                        'measured_render': 204470}}

VALIDATED_ENTRIES = ('19.P3.kill-cli-activation',
 '19.P3.heartbeat',
 '19.P3.restart-timers',
 '19.P3.flake-detection',
 '19.P3.flake-release')

DELIMITER_FREE_AT_AUTHORING = ('chupa/daemon.py',
 'chupa/stages.py',
 'chupa/drain.py',
 'chupa/__main__.py',
 'tests/test_kill_signal_journal.py',
 'tests/test_kill_executor_abort.py',
 'chupa/control.py',
 'chupa/driver.py',
 'chupa/runner.py',
 'tests/test_seeded_phase3_core.py')

ENTRY_TESTS = ('test_kill_signal_journal_is_dormant',
 'test_executor_abort_is_dormant',
 'test_live_kill_publishes_only_bound_request',
 'test_idle_kill_refuses_without_state',
 'test_kill_discovery_and_lifecycle_races_fail_closed',
 'test_live_drain_kill_reaches_production_driver',
 'test_kill_stops_before_all_offer_accounting',
 'test_kill_application_is_once_and_identity_bound',
 'test_kill_cleanup_is_atomic_and_failures_propagate',
 'test_killed_run_is_terminal_or_restart_reconcilable',
 'test_kill_activation_keeps_worker_boundaries_dormant',
 'test_kill_signal_journal_is_active_in_drain',
 'test_executor_abort_is_active_in_drain')

ENTRY_VERIFICATION = ('uv',
 'run',
 'pytest',
 'tests/test_kill_cli_activation.py',
 'tests/test_kill_signal_journal.py',
 'tests/test_kill_executor_abort.py',
 'tests/test_kill_worker_stop.py',
 'tests/test_kill_failure_suppression.py',
 'tests/test_control.py',
 'tests/test_control_cli.py',
 'tests/test_daemon_tasks.py',
 'tests/test_driver.py',
 'tests/test_stages.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_daemon_composition.py',
 'tests/test_reconcile.py')

PRESERVATION = ('tests/test_kill_worker_stop.py',
 'tests/test_kill_failure_suppression.py',
 'tests/test_control.py',
 'tests/test_control_cli.py',
 'tests/test_daemon_tasks.py',
 'tests/test_driver.py',
 'tests/test_stages.py',
 'tests/test_cli.py',
 'tests/test_drain.py',
 'tests/test_daemon_composition.py',
 'tests/test_reconcile.py')

CONTRACT_CUSTODY = {'Owner': '19.P3.kill-cli-activation',
 'Records': '19.P3.kill-cli-activation',
 'Observable': '19.P3.kill-cli-activation',
 'Tests': '19.P3.kill-cli-activation'}

NEXT_STARTS = {'heartbeat': ('medium', 'medium'),
 'restart-timers': ('high', 'high'),
 'flake-detection': ('medium', 'medium'),
 'flake-release': ('medium', 'medium')}

NEXT_CITATIONS = {'heartbeat': ('19.I', '19.P3.heartbeat', '9', '15'),
 'restart-timers': ('19.I', '19.P3.restart-timers', '6', '15'),
 'flake-detection': ('19.I', '19.P3.flake-detection', '11'),
 'flake-release': ('19.I', '19.P3.flake-release', '11')}

CLOSURE_SNAPSHOT = {'search_roots': ('chupa/', 'eval/', 'tests/'),
 'abort_current': ('chupa/driver.py:Driver.abort_current,_abort,race,_kill',
                   'chupa/daemon.py:executor_abort',
                   'chupa/llm.py:LLM,FakeLLM',
                   'chupa/providers.py:ProviderLLM',
                   'chupa/requisition.py:Driver.race',
                   'tests/test_kill_executor_abort.py'),
 'forwarding': ('chupa/stages.py:StageContext',
                'chupa/daemon.py:TicketWriter',
                'chupa/runner.py:bind,Pipeline,Dispatch',
                'chupa/__main__.py:main,build_control',
                'chupa/drain.py:drain,_Drain'),
 'composition_callers': ('chupa/runner.py:bind',
                         'eval/shakeout/bench.py',
                         'tests/test_merge.py',
                         'tests/test_daemon_composition.py'),
 'timeout_review_cancellation': 'Driver owns invocation, call, optional review and timer cleanup; '
                                'construction/run/race signatures stay unchanged, including the '
                                'requisition caller.',
 'task_ownership_and_failure': 'DaemonTasks.run owns watcher/merge/box tasks and ordinary '
                               'exception propagation; WorkerStop and WorkerFailureObserver remain '
                               'dormant until serve-activation.',
 'assertion_migrations': {'tests/test_kill_signal_journal.py': ('test_kill_signal_journal_is_dormant',
                                                                'test_kill_signal_journal_is_active_in_drain'),
                          'tests/test_kill_executor_abort.py': ('test_executor_abort_is_dormant',
                                                                'test_executor_abort_is_active_in_drain')},
 'allowlists_and_absence': 'No daemon/Stages public-operation allowlist or CLI kill-absence '
                           'assertion was found; CLI pause/resume and shared holds stay unchanged. '
                           'No historical seeding test is migrated.',
 'rules_2_5': 'No earned additions: both forced predecessor migrations and all production owners '
              'are already in the registry floor; callable signatures and direct caller '
              'construction stay unchanged. All fenced existing files are embedded, created test '
              'excluded; preservation suites are Verification-only.',
 'next_construction': 'heartbeat preserves DaemonTasks/DaemonAdmission/composition signatures and '
                      'Config/FileSystem/Clock seams; serve-activation owns production cycle '
                      'wiring.'}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[path] for path in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ('kill-cli-activation', 'phase3-continue-13')
    assert BATCH == (*PAYLOADS, 'phase3-continue-13') and len(set(BATCH)) == 2
    assert set(BATCH) == set(EDGES) == set(STARTS) == set(AUTHORED)
    assert set(BATCH) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS)
    assert len(BATCH) <= 3  # authoring-time seeding.max_seeds_per_admission


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    # A later Reject stamp is lifecycle history; seeds were born confirmed.
    birth = _text(stem).replace('state: rejected', 'state: confirmed', 1)
    t = validate_ticket(stem, birth, ROOT, BATCH)
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == STARTS[stem]
    assert (t.frontmatter.priority, t.frontmatter.kind) == ('P1', 'feature')
    assert STARTS == {'kill-cli-activation': ('high', 'high'),
                      'phase3-continue-13': ('medium', 'medium')}


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert 0 < t.expected_minutes <= t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes
    assert (t.expected_minutes, t.stuck_minutes) == (60, 90)


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES['kill-cli-activation'] == ('phase3-continue-12',)
    assert EDGES['phase3-continue-13'] == PAYLOADS


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS[stem] == {}
    assert CLOSURE_SNAPSHOT['rules_2_5'].startswith('No earned additions:')
    assert CLOSURE_SNAPSHOT['search_roots'] == ('chupa/', 'eval/', 'tests/')
    for reason in ('abort_current', 'forwarding', 'composition_callers',
                   'timeout_review_cancellation', 'task_ownership_and_failure',
                   'allowlists_and_absence', 'next_construction'):
        assert CLOSURE_SNAPSHOT[reason]
    assert CLOSURE_SNAPSHOT['assertion_migrations'] == {
        'tests/test_kill_signal_journal.py': ('test_kill_signal_journal_is_dormant',
                                             'test_kill_signal_journal_is_active_in_drain'),
        'tests/test_kill_executor_abort.py': ('test_executor_abort_is_dormant',
                                             'test_executor_abort_is_active_in_drain'),
    }
    assert set(CLOSURE_SNAPSHOT['assertion_migrations']) <= set(FENCE_FLOORS[PAYLOADS[0]])
    if stem in PAYLOADS:
        assert not any(path.startswith('tests/test_seeded_') for path in t.scope_fence)
        scope = t.sections['Scope in / Scope out']
        for fact in ('registry floor needs no additions', 'Driver construction/run',
                     'Pipeline/Dispatch', 'runner.bind', 'StageContext/TicketWriter',
                     'shared admission/dispatch hold semantics', 'historical seeding tests'):
            assert fact in scope, fact


@pytest.mark.parametrize('stem', PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    own = '19.P3.kill-cli-activation'
    assert t.plan_contract == AUTHORED[stem]['plan'] == ('19.I', own, '20')
    # The citation is the authority for ALL obligations and sole-writer custody,
    # not duplicated record bodies or a second specification in this fixture.
    assert CONTRACT_CUSTODY == {part: own for part in ('Owner', 'Records', 'Observable', 'Tests')}
    assert own in VALIDATED_ENTRIES
    assert ENTRY_TESTS == (
        'test_kill_signal_journal_is_dormant', 'test_executor_abort_is_dormant',
        'test_live_kill_publishes_only_bound_request', 'test_idle_kill_refuses_without_state',
        'test_kill_discovery_and_lifecycle_races_fail_closed',
        'test_live_drain_kill_reaches_production_driver',
        'test_kill_stops_before_all_offer_accounting',
        'test_kill_application_is_once_and_identity_bound',
        'test_kill_cleanup_is_atomic_and_failures_propagate',
        'test_killed_run_is_terminal_or_restart_reconcilable',
        'test_kill_activation_keeps_worker_boundaries_dormant',
        'test_kill_signal_journal_is_active_in_drain', 'test_executor_abort_is_active_in_drain',
    )
    scope = t.sections['Scope in / Scope out']
    for fact in (own, 'complete governing contract for Owner, Records, Observable',
                 'every named Tests obligation', 'record custody', 'implement all of it',
                 'real predecessor boundaries', 'Never copy unit text',
                 'calibrated raising probes', 'real CLI run/drain',
                 'merged production-composition harness', 'deliberate wiring must trip',
                 'ordinary composition must leave it untouched', 'chupa.daemon is already reachable',
                 'scripted LLMs', 'disposable repositories', 'asyncio barriers',
                 'ordinary DaemonTasks exception propagation and cleanup',
                 'serve-activation owns their production wiring and dormancy migrations'):
        assert fact in scope, fact
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(stem)
    assert t.verification == (ENTRY_VERIFICATION, ('uv', 'run', 'pytest', '-q'))


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket(BATCH[-1])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '19.P3.heartbeat', '9', '15',
        '19.P3.restart-timers', '6', '19.P3.flake-detection', '19.P3.flake-release', '11',
    )
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_13.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == (
        '19.P3.kill-cli-activation', '19.P3.heartbeat', '19.P3.restart-timers',
        '19.P3.flake-detection', '19.P3.flake-release',
    )
    assert t.verification == (('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_13.py'),
                              ('uv', 'run', 'pytest', '-q'))
    for row, citations in NEXT_CITATIONS.items():
        assert set(citations) <= set(t.plan_contract)
        assert citations[:2] == ('19.I', f'19.P3.{row}')
        assert NEXT_STARTS[row] == (('high', 'high') if row == 'restart-timers' else ('medium', 'medium'))
    scope = t.sections['Scope in / Scope out']
    for fact in (
        'BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[13:]', 'admissions[14:]', 'admissions[15:]',
        'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
        'Author only heartbeat and phase3-continue-14',
        'heartbeat depends on phase3-continue-13, starts medium/medium',
        '19.I, 19.P3.heartbeat, section 9, section 15',
        'Never copy unit text into a seed or into this seeding ticket',
        "Carry this cite-don't-copy rule forward to phase3-continue-14",
        'continuation depending on heartbeat', 'its next payload is restart-timers',
        'tests/test_seeded_phase3_14.py', "never this batch's tests/test_seeded_phase3_13.py",
        'restart-timers depends on phase3-continue-14, starts high/high',
        '19.I, 19.P3.restart-timers, section 6, section 15',
        'flake-release also depends on flake-detection',
        '19.L closure rules 2-5', 'Context/on-demand partition', '300,000-character headroom',
        'Prompt-specs and delimiter-bearing sources are never Context',
        'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
        'serve-activation owns heartbeat production wiring', 'named invariant obligations', 'record custody',
        'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
        'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
        'terminal phase3-exit as its sole payload with no successor',
        'keep previously approved seeds verbatim', 'ticket_sha',
        'chupa(phase3-continue-13): seeds', "Commit only this ticket's new test",
        'deliberate wiring must trip the probe', 'chupa.daemon is already reachable',
    ):
        assert fact in scope, fact
    for part in CONTRACT_CUSTODY:
        assert f'- **{part}:**' not in _text(t.stem)


@pytest.mark.parametrize('stem', BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a['context'] and t.on_demand == a['on_demand']
    assert set(t.scope_fence) == set(a['fenced_existing']) | set(a['created'])
    assert set(a['fenced_existing']) <= set(a['context']) | set(a['on_demand'])
    assert not set(a['created']) & (set(a['context']) | set(a['on_demand']))
    assert not set(a['context']) & set(a['on_demand'])
    assert set(a['context']) <= set(DELIMITER_FREE_AT_AUTHORING)
    assert not any(p.startswith('specs/') or p == 'CHUPA_PLAN.md' for p in a['context'])
    assert all(FILE_CHARS[p] > 0 for p in (*a['context'], *a['on_demand']))
    assert all(PLAN_CHARS[pid] > 0 for pid in a['plan'])
    assert 0 < a['measured_render'] <= render_chars(a) <= HEADROOM_CHARS
    # All arithmetic uses permanent constants, including at max effort.
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize('stem', PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification[0] == ENTRY_VERIFICATION
    assert set(ENTRY_VERIFICATION[3:]) == set(PRESERVATION) | {
        'tests/test_kill_cli_activation.py', 'tests/test_kill_signal_journal.py',
        'tests/test_kill_executor_abort.py',
    }
    assert {'tests/test_kill_worker_stop.py', 'tests/test_kill_failure_suppression.py'} <= set(PRESERVATION)
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
    assert 'unchanged preservation suites in Verification only, neither fenced nor embedded' in t.sections['Scope in / Scope out']
