"""Admission 11: citation-only seeds and fixed authoring snapshots.

Read YAML directly from the live P3 registry at AUTHORING_HEAD, admissions[11:].
All five needed entries (worker-stop, failure-suppression, CLI activation,
heartbeat, restart-timers) passed entry_unit_gap and resolve_plan_contract.
Render arithmetic uses only the constants recorded below, never live sizes/units.
"""

from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ('kill-worker-stop', 'kill-failure-suppression')

BATCH = ('kill-worker-stop', 'kill-failure-suppression', 'phase3-continue-12')

AUTHORING_HEAD = '2294d1faebe8ddaf9522d98ab0550c2fa899ffad'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

EDGES = {'kill-worker-stop': ('phase3-continue-11',),
 'kill-failure-suppression': ('phase3-continue-11', 'kill-worker-stop'),
 'phase3-continue-12': ('kill-worker-stop', 'kill-failure-suppression')}

FENCE_FLOORS = {'kill-worker-stop': ('chupa/daemon.py', 'tests/test_kill_worker_stop.py'),
 'kill-failure-suppression': ('chupa/daemon.py', 'tests/test_kill_failure_suppression.py'),
 'phase3-continue-12': ('tickets', 'tests/test_seeded_phase3_12.py')}

FENCE_ADDITIONS = {'kill-worker-stop': {}, 'kill-failure-suppression': {}, 'phase3-continue-12': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

PLAN_CHARS = {'19.I': 1811,
 '19.P3.kill-worker-stop': 5597,
 '20': 4367,
 '19.P3.kill-failure-suppression': 5452,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.kill-cli-activation': 12007,
 '19.P3.heartbeat': 5116,
 '19.P3.restart-timers': 8881,
 '9': 19656,
 '15': 17090,
 '6': 36783,
 '11': 26851}

FILE_CHARS = {'chupa/daemon.py': 13679,
 'chupa/control.py': 8166,
 'chupa/driver.py': 16659,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'kill-worker-stop': {'chars': 2891,
                      'plan': ('19.I', '19.P3.kill-worker-stop', '20'),
                      'context': ('chupa/daemon.py', 'chupa/control.py', 'chupa/driver.py'),
                      'on_demand': (),
                      'fenced_existing': ('chupa/daemon.py',),
                      'created': ('tests/test_kill_worker_stop.py',),
                      'measured_render': 57496},
 'kill-failure-suppression': {'chars': 2960,
                              'plan': ('19.I', '19.P3.kill-failure-suppression', '20'),
                              'context': ('chupa/daemon.py', 'chupa/control.py', 'chupa/driver.py'),
                              'on_demand': (),
                              'fenced_existing': ('chupa/daemon.py',),
                              'created': ('tests/test_kill_failure_suppression.py',),
                              'measured_render': 57420},
 'phase3-continue-12': {'chars': 10136,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '20',
                                 '19.P3.kill-cli-activation',
                                 '19.P3.heartbeat',
                                 '19.P3.restart-timers',
                                 '9',
                                 '15',
                                 '6',
                                 '11'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_12.py'),
                        'measured_render': 206910}}

ENTRY_OBLIGATIONS = {'kill-worker-stop': {'citation': '19.P3.kill-worker-stop',
                      'named_tests': ('test_executor_unwinds_before_worker_cancel',
                                      'test_worker_stop_requires_matching_kill',
                                      'test_worker_stop_observes_all_workers',
                                      'test_worker_stop_is_atomic_under_repeated_cancellation',
                                      'test_executor_abort_failure_does_not_cancel_workers',
                                      'test_kill_worker_stop_is_dormant')},
 'kill-failure-suppression': {'citation': '19.P3.kill-failure-suppression',
                              'named_tests': ('test_post_kill_worker_failures_are_suppressed',
                                              'test_worker_failures_without_matching_kill_are_preserved',
                                              'test_kill_suppression_observes_all_worker_outcomes',
                                              'test_kill_suppression_waiter_cancellation_awaits_cleanup',
                                              'test_kill_suppression_preserves_run_and_abort_failures',
                                              'test_kill_failure_suppression_is_dormant')}}

ENTRY_VERIFICATION = {'kill-worker-stop': ('uv',
                      'run',
                      'pytest',
                      'tests/test_kill_worker_stop.py',
                      'tests/test_kill_executor_abort.py',
                      'tests/test_daemon_tasks.py',
                      'tests/test_cli.py',
                      'tests/test_drain.py',
                      'tests/test_daemon_composition.py'),
 'kill-failure-suppression': ('uv',
                              'run',
                              'pytest',
                              'tests/test_kill_failure_suppression.py',
                              'tests/test_kill_worker_stop.py',
                              'tests/test_daemon_tasks.py',
                              'tests/test_cli.py',
                              'tests/test_drain.py',
                              'tests/test_daemon_composition.py')}

PRESERVATION = {'kill-worker-stop': ('tests/test_kill_executor_abort.py',
                      'tests/test_daemon_tasks.py',
                      'tests/test_cli.py',
                      'tests/test_drain.py',
                      'tests/test_daemon_composition.py'),
 'kill-failure-suppression': ('tests/test_kill_worker_stop.py',
                              'tests/test_daemon_tasks.py',
                              'tests/test_cli.py',
                              'tests/test_drain.py',
                              'tests/test_daemon_composition.py')}

DELIMITER_FREE_AT_AUTHORING = ('chupa/daemon.py', 'chupa/control.py', 'chupa/driver.py', 'tests/test_seeded_phase3_core.py')

VALIDATED_ENTRIES = ('19.P3.kill-worker-stop',
 '19.P3.kill-failure-suppression',
 '19.P3.kill-cli-activation',
 '19.P3.heartbeat',
 '19.P3.restart-timers')

CLOSURE_SNAPSHOT = {'abort_current': ('chupa/daemon.py:executor_abort',
                   'chupa/driver.py:Driver.abort_current,_abort,race,_kill',
                   'chupa/llm.py:LLM,ScriptedLLM',
                   'chupa/providers.py:ProviderLLM',
                   'tests/test_kill_executor_abort.py'),
 'timeout_review_cancellation': ('chupa/driver.py:run,race,_observe',
                                 'tests/test_driver.py',
                                 'tests/test_kill_executor_abort.py:test_external_abort_does_not_reprompt_or_report_success'),
 'task_ownership_and_failure': ('chupa/daemon.py:DaemonTasks.run',
                                'tests/test_daemon_tasks.py:test_consumer_failure_cancels_and_awaits_siblings,test_run_cancellation_awaits_all_cleanup'),
 'production': ('chupa/__main__.py:build_daemon_core,main',
                'chupa/drain.py',
                'chupa/runner.py:bind',
                'tests/test_daemon_composition.py:CoreRig,LiveDrain'),
 'old_assertions_and_allowlists': 'Grepped chupa/, eval/, tests/: no pinned daemon-operation '
                                  'allowlist or old assertion flips for these dormant boundaries; '
                                  'Driver construction/run and DaemonTasks construction/run stay '
                                  'unchanged.',
 'rules_2_5': 'No earned additions: no existing assertion, public signature, constructor, '
              'production caller or composition wiring changes. Existing daemon owner embedded; '
              'created test paths in neither; predecessor suites preserved in Verification only.',
 'next_activation': 'kill-cli-activation retains worker-stop and suppression dormancy; '
                    'serve-activation owns real worker production wiring and migrations.'}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _birth_text(stem):
    # A later rejected stamp is lifecycle history, not an unconfirmed seed birth.
    return _text(stem).replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[p] for p in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ('kill-worker-stop', 'kill-failure-suppression', 'phase3-continue-12')
    assert BATCH == (*PAYLOADS, 'phase3-continue-12') and len(set(BATCH)) == 3
    assert set(BATCH) == set(EDGES) == set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    t = validate_ticket(stem, _birth_text(stem), ROOT, BATCH)
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ('medium', 'medium')


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert 0 < t.expected_minutes <= t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES[PAYLOADS[0]] == ('phase3-continue-11',)
    assert EDGES[PAYLOADS[1]] == ('phase3-continue-11', 'kill-worker-stop')
    assert EDGES[BATCH[-1]] == PAYLOADS


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS[stem] == {}
    assert CLOSURE_SNAPSHOT['rules_2_5'].startswith('No earned additions:')
    assert set(CLOSURE_SNAPSHOT) == {
        'abort_current', 'timeout_review_cancellation', 'task_ownership_and_failure',
        'production', 'old_assertions_and_allowlists', 'rules_2_5', 'next_activation',
    }
    if stem in PAYLOADS:
        assert not any(p.startswith('tests/test_seeded_') for p in t.scope_fence)


@pytest.mark.parametrize('stem', PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    own_entry = f'19.P3.{stem}'
    # The exact governing citation carries the entire Owner/Records/Observable/Tests
    # contract, including durable matching acceptance, custody, protected cleanup,
    # executor-before-worker ordering and calibrated production dormancy evidence.
    assert t.plan_contract == AUTHORED[stem]['plan'] == ('19.I', own_entry, '20')
    assert ENTRY_OBLIGATIONS[stem]['citation'] == own_entry
    assert own_entry in VALIDATED_ENTRIES
    expected_names = (
        ('test_executor_unwinds_before_worker_cancel', 'test_worker_stop_requires_matching_kill',
         'test_worker_stop_observes_all_workers', 'test_worker_stop_is_atomic_under_repeated_cancellation',
         'test_executor_abort_failure_does_not_cancel_workers', 'test_kill_worker_stop_is_dormant')
        if stem == 'kill-worker-stop' else
        ('test_post_kill_worker_failures_are_suppressed',
         'test_worker_failures_without_matching_kill_are_preserved',
         'test_kill_suppression_observes_all_worker_outcomes',
         'test_kill_suppression_waiter_cancellation_awaits_cleanup',
         'test_kill_suppression_preserves_run_and_abort_failures',
         'test_kill_failure_suppression_is_dormant')
    )
    assert ENTRY_OBLIGATIONS[stem]['named_tests'] == expected_names
    scope = t.sections['Scope in / Scope out']
    assert own_entry in scope
    for fact in ('complete governing contract for Owner, Records, Observable',
                 'every named Tests obligation', 'real predecessor boundaries',
                 'Do not copy unit bodies', 'DaemonTasks construction/run and ownership',
                 'ordinary failure routing', 'calibrated raising probes',
                 'real CLI run/drain', 'merged production-composition harness',
                 'Deliberate wiring must trip', 'ordinary composition leaves it untouched',
                 'injected seams', 'disposable directories', 'asyncio barriers'):
        assert fact in scope, fact
    # Copies of the unit's labeled bodies are forbidden; citations remain authority.
    for part in ('Owner', 'Records', 'Observable', 'Tests'):
        assert f'- **{part}:**' not in _text(stem)


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket(BATCH[-1])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '20', '19.P3.kill-cli-activation',
        '19.P3.heartbeat', '19.P3.restart-timers', '9', '15', '6', '11',
    )
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_12.py')
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert VALIDATED_ENTRIES == (
        '19.P3.kill-worker-stop', '19.P3.kill-failure-suppression',
        '19.P3.kill-cli-activation', '19.P3.heartbeat', '19.P3.restart-timers',
    )
    assert t.verification == (('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_12.py'),
                              ('uv', 'run', 'pytest', '-q'))
    scope = t.sections['Scope in / Scope out']
    for part in ('Owner', 'Records', 'Observable', 'Tests'):
        assert f'- **{part}:**' not in scope
    for fact in (
        'BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[12:]', 'admissions[13:]',
        'admissions[14:]', 'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
        'Author only kill-cli-activation and phase3-continue-13',
        'kill-cli-activation depends on phase3-continue-12, starts high/high',
        '19.I, 19.P3.kill-cli-activation, section 20',
        'Never copy unit text into a seed or into this seeding ticket',
        "Carry this cite-don't-copy rule forward to phase3-continue-13",
        'continuation depending on kill-cli-activation',
        'its next payload is heartbeat', 'tests/test_seeded_phase3_13.py',
        "never this batch's tests/test_seeded_phase3_12.py",
        'heartbeat depends on phase3-continue-13, starts medium/medium',
        '19.I, 19.P3.heartbeat, section 9, section 15',
        'restart-timers starts high/high', '19.I, 19.P3.restart-timers, section 6, section 15',
        '19.L closure rules 2-5', 'Context/on-demand partition', '300,000-character headroom',
        'Prompt-specs and delimiter-bearing sources are never Context',
        'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
        'worker-stop and failure-suppression suites remain unchanged preservation suites',
        'serve-activation owns their production wiring and dormancy migrations',
        'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
        'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
        'terminal phase3-exit as its sole payload with no successor',
        'keep previously approved seeds verbatim', 'ticket_sha',
        'chupa(phase3-continue-12): seeds', "Commit only this ticket's new test",
        'deliberate wiring must trip the probe', 'chupa.daemon is already reachable',
        'StageContext/TicketWriter forwarding', 'ordinary DaemonTasks exception propagation',
    ):
        assert fact in scope, fact


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
    # No live sizes or unit lengths are read, even at maximum effort.
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize('stem', PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification == (ENTRY_VERIFICATION[stem], ('uv', 'run', 'pytest', '-q'))
    assert ENTRY_VERIFICATION[stem][:3] == ('uv', 'run', 'pytest')
    assert ENTRY_VERIFICATION[stem][3:] == (FENCE_FLOORS[stem][-1], *PRESERVATION[stem])
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
