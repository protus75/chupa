"""Admission 10: approved payloads and citation-only successor, fixed authoring snapshots.

Parsed the live registry directly at AUTHORING_HEAD: positions 10, 11 and 12.
All five entry units passed entry_unit_gap and resolve_plan_contract before writing.
Authoring rg across chupa/, eval/ and tests/ covered abort_current, Driver callers,
timeout ownership, optional review waits, cancellation handling, public allowlists,
ControlInbox, kill_requested, DaemonTasks and production absence assertions.
No rule 2-5 addition was earned; existing construction/run signatures stay fixed.
Approved payload bytes are retained under 19.L's approve-holds rule. Their old
inline contracts are pinned, but the new successor cites units without copying.
Render arithmetic reads only constants below, never live file or plan lengths.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

PAYLOADS = ('kill-signal-journal', 'kill-executor-abort')

BATCH = ('kill-signal-journal', 'kill-executor-abort', 'phase3-continue-11')

AUTHORING_HEAD = '286337fbd53fa821ca8c88d51123a1177c04f018'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

APPROVED_SHA256 = {'kill-signal-journal': '1ccd48c5ca52b3f033998fda2e72e931c1a792590c247033fe8688c2c2d566e4',
 'kill-executor-abort': '2153388f69cce3a913608b57f518758df6d7b54d39bc6b913d0fdde9f54335cd'}

ENTRY_SHA256 = {'kill-signal-journal': '016e237e308a72535b7191936032f9fbf0c3da7b51818056a3046c860677f106',
 'kill-executor-abort': 'bb6a9c45541b8018cfee67e3dde7360a814b2c0d8ed7e8865f73ba4fa869dfe8'}

EDGES = {'kill-signal-journal': ('phase3-continue-10',),
 'kill-executor-abort': ('phase3-continue-10', 'kill-signal-journal'),
 'phase3-continue-11': ('kill-signal-journal', 'kill-executor-abort')}

FENCE_FLOORS = {'kill-signal-journal': ('chupa/control.py',
                         'chupa/daemon.py',
                         'tests/test_kill_signal_journal.py'),
 'kill-executor-abort': ('chupa/daemon.py', 'chupa/driver.py', 'tests/test_kill_executor_abort.py'),
 'phase3-continue-11': ('tickets', 'tests/test_seeded_phase3_11.py')}

FENCE_ADDITIONS = {'kill-signal-journal': {}, 'kill-executor-abort': {}, 'phase3-continue-11': {}}

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

PLAN_CHARS = {'19.I': 1811,
 '19.P3.kill-signal-journal': 5337,
 '20': 4367,
 '19.P3.kill-executor-abort': 5396,
 '6': 36783,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.kill-worker-stop': 5597,
 '19.P3.kill-failure-suppression': 5452,
 '19.P3.kill-cli-activation': 12007,
 '11': 26851}

FILE_CHARS = {'chupa/control.py': 8166,
 'chupa/daemon.py': 13482,
 'chupa/driver.py': 11582,
 'tests/test_seeded_phase3_core.py': 5425}

AUTHORED = {'kill-signal-journal': {'chars': 9183,
                         'plan': ('19.I', '19.P3.kill-signal-journal', '20'),
                         'context': ('chupa/control.py', 'chupa/daemon.py'),
                         'on_demand': (),
                         'fenced_existing': ('chupa/control.py', 'chupa/daemon.py'),
                         'created': ('tests/test_kill_signal_journal.py',),
                         'measured_render': 46650},
 'kill-executor-abort': {'chars': 9289,
                         'plan': ('19.I', '19.P3.kill-executor-abort', '20', '6'),
                         'context': ('chupa/daemon.py', 'chupa/driver.py'),
                         'on_demand': (),
                         'fenced_existing': ('chupa/daemon.py', 'chupa/driver.py'),
                         'created': ('tests/test_kill_executor_abort.py',),
                         'measured_render': 87013},
 'phase3-continue-11': {'chars': 9864,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '20',
                                 '19.P3.kill-worker-stop',
                                 '19.P3.kill-failure-suppression',
                                 '19.P3.kill-cli-activation',
                                 '6',
                                 '11'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_11.py'),
                        'measured_render': 166944}}

NAMED_INVARIANTS = {'kill-signal-journal': ('test_kill_decision_precedes_projection',
                         'test_kill_identity_and_shape_fail_closed',
                         'test_kill_decision_is_once',
                         'test_kill_decision_crash_recovery',
                         'test_kill_projection_stays_latched',
                         'test_kill_signal_journal_is_dormant'),
 'kill-executor-abort': ('test_executor_abort_stops_writer_before_cancellation',
                         'test_executor_abort_waits_for_unwind',
                         'test_executor_abort_is_atomic_under_repeated_cancellation',
                         'test_executor_abort_idle_and_completion_race',
                         'test_external_abort_does_not_reprompt_or_report_success',
                         'test_executor_abort_is_dormant'),
 'kill-worker-stop': ('test_executor_unwinds_before_worker_cancel',
                      'test_worker_stop_requires_matching_kill',
                      'test_worker_stop_observes_all_workers',
                      'test_worker_stop_is_atomic_under_repeated_cancellation',
                      'test_executor_abort_failure_does_not_cancel_workers',
                      'test_kill_worker_stop_is_dormant'),
 'kill-failure-suppression': ('test_post_kill_worker_failures_are_suppressed',
                              'test_worker_failures_without_matching_kill_are_preserved',
                              'test_kill_suppression_observes_all_worker_outcomes',
                              'test_kill_suppression_waiter_cancellation_awaits_cleanup',
                              'test_kill_suppression_preserves_run_and_abort_failures',
                              'test_kill_failure_suppression_is_dormant'),
 'kill-cli-activation': ('test_kill_signal_journal_is_dormant',
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
                         'test_executor_abort_is_active_in_drain')}

ENTRY_VERIFICATION = {'kill-signal-journal': ('uv',
                         'run',
                         'pytest',
                         'tests/test_kill_signal_journal.py',
                         'tests/test_control.py',
                         'tests/test_cli.py',
                         'tests/test_drain.py',
                         'tests/test_daemon_composition.py'),
 'kill-executor-abort': ('uv',
                         'run',
                         'pytest',
                         'tests/test_kill_executor_abort.py',
                         'tests/test_driver.py',
                         'tests/test_cli.py',
                         'tests/test_drain.py',
                         'tests/test_daemon_composition.py')}

PRESERVATION = {'kill-signal-journal': ('tests/test_control.py',
                         'tests/test_cli.py',
                         'tests/test_drain.py',
                         'tests/test_daemon_composition.py'),
 'kill-executor-abort': ('tests/test_driver.py',
                         'tests/test_cli.py',
                         'tests/test_drain.py',
                         'tests/test_daemon_composition.py')}

DELIMITER_FREE_AT_AUTHORING = ('chupa/control.py', 'chupa/daemon.py', 'chupa/driver.py', 'tests/test_seeded_phase3_core.py')

CLOSURE_SNAPSHOT = {'abort_current': ('chupa/driver.py:_kill',
                   'chupa/llm.py:LLM,ScriptedLLM',
                   'chupa/providers.py:ProviderLLM'),
 'Driver.race': ('chupa/driver.py:run', 'chupa/requisition.py:review_ticket'),
 'public_signatures': 'Driver construction/run/race unchanged; no allowlist pins Driver or daemon '
                      'operations',
 'old_kill_assertions': 'tests/test_control.py preserves latched projection and decided-file '
                        'inertia',
 'production_graph': 'tests/test_daemon_composition.py CoreRig and LiveDrain preserve shared '
                     'control and inline admission',
 'partition': 'Existing owners embedded; created tests in neither; preservation suites '
              'Verification only',
 'earned_additions': 'None: no signature, construction, production wiring, or pinned public '
                     'surface is flipped'}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _birth_text(stem):
    # A later Reject stamp is history, not an unconfirmed seed birth.
    return _text(stem).replace('state: rejected', 'state: confirmed', 1)


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT, BATCH)


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[p] for p in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ('kill-signal-journal', 'kill-executor-abort', 'phase3-continue-11')
    assert BATCH == (*PAYLOADS, 'phase3-continue-11') and len(set(BATCH)) == 3
    assert set(BATCH) == set(EDGES) == set(AUTHORED) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    t = validate_ticket(stem, _birth_text(stem), ROOT, BATCH)
    assert (t.frontmatter.source, t.frontmatter.state) == ('seed', 'confirmed')
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ('medium', 'medium')
    if stem in APPROVED_SHA256:
        assert hashlib.sha256(_birth_text(stem).encode()).hexdigest() == APPROVED_SHA256[stem]


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    assert 0 < _ticket(stem).expected_minutes <= _ticket(stem).stuck_minutes
    assert _ticket(stem).stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES[PAYLOADS[0]] == ('phase3-continue-10',)
    assert EDGES[PAYLOADS[1]] == ('phase3-continue-10', 'kill-signal-journal')
    assert EDGES[BATCH[-1]] == PAYLOADS


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert FENCE_ADDITIONS[stem] == {}
    assert CLOSURE_SNAPSHOT['earned_additions'].startswith('None:')
    assert not any(p.startswith('tests/test_seeded_') for p in t.scope_fence if stem in PAYLOADS)


@pytest.mark.parametrize('stem', PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    expected = ('19.I', f'19.P3.{stem}', '20') + (('6',) if stem == PAYLOADS[1] else ())
    assert t.plan_contract == AUTHORED[stem]['plan'] == expected
    scope = t.sections['Scope in / Scope out']
    entry = scope.split('\n\nAUTHORING CLOSURE:', 1)[0].strip()
    assert hashlib.sha256(entry.encode()).hexdigest() == ENTRY_SHA256[stem]
    for part in ('Owner', 'Records', 'Observable', 'Tests'):
        assert f'- **{part}:**' in entry
    for name in NAMED_INVARIANTS[stem]:
        assert name in entry
    assert ' '.join(ENTRY_VERIFICATION[stem]) in entry
    # The complete digest above covers every record key, sole writer, edge and invariant.
    for fact in ('No new module', 'real CLI', 'production', 'dormant', 'unwind'):
        assert fact in scope, fact
    if stem == PAYLOADS[0]:
        for fact in ('CONTROL_DECISION = "control_decision"', 'null ticket/key',
                     'append/fsync the decision before application', 'kill_requested: bool',
                     'Old-lifecycle decisions never latch', 'solely by the lock-holding consumer'):
            assert fact in entry, fact
    else:
        for fact in ('Driver.abort_current()', 'LLM.abort_current()', 'BEFORE cancelling',
                     'finish the protected cleanup', 'never fabricate a completion',
                     'writes no journal record', 'optional review wait', 'same cleanup ownership'):
            assert fact in entry, fact


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket(BATCH[-1])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '20', '19.P3.kill-worker-stop',
        '19.P3.kill-failure-suppression', '19.P3.kill-cli-activation', '6', '11',
    )
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_11.py')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    scope = t.sections['Scope in / Scope out']
    assert not any(f'- **{part}:**' in scope for part in ('Owner', 'Records', 'Observable', 'Tests'))
    assert 'Carry every own-entry' not in scope and 'Carry this complete' not in scope
    for fact in (
        'BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[11:]', 'admissions[12:]',
        'admissions[13:]', 'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
        'Author only kill-worker-stop, kill-failure-suppression and phase3-continue-12',
        'Both implementing seeds start medium/medium and depend on phase3-continue-11',
        'kill-failure-suppression also explicitly depends on kill-worker-stop',
        '19.I, 19.P3.kill-worker-stop, section 20',
        '19.I, 19.P3.kill-failure-suppression, section 20',
        'Never copy unit text into a seed or into this seeding ticket',
        "Carry this cite-don't-copy rule forward to phase3-continue-12",
        'depending on both kill-worker-stop and kill-failure-suppression',
        'tests/test_seeded_phase3_12.py', "never this batch's tests/test_seeded_phase3_11.py",
        'kill-cli-activation depends on phase3-continue-12, starts high/high',
        '19.I, 19.P3.kill-cli-activation, section 20',
        '19.L closure rules 2-5', 'Context/on-demand partition', '300,000-character headroom',
        'Prompt-specs and delimiter-bearing sources are never Context',
        'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
        'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
        'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
        'terminal phase3-exit as its sole payload with no successor',
        'keep previously approved seeds verbatim', 'ticket_sha',
        'chupa(phase3-continue-11): seeds', "Commit only this ticket's new test",
        'deliberate wiring must trip the probe', 'chupa.daemon is already reachable',
        'serve-activation owns their production wiring and dormancy migrations',
    ):
        assert fact in scope, fact
    for stem in ('kill-worker-stop', 'kill-failure-suppression', 'kill-cli-activation'):
        assert f'19.P3.{stem}' in t.plan_contract
        assert PLAN_CHARS[f'19.P3.{stem}'] > 0 and len(NAMED_INVARIANTS[stem]) >= 6
    assert t.verification == (('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_11.py'),
                              ('uv', 'run', 'pytest', '-q'))


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
    for path in a['on_demand']:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize('stem', PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification == (ENTRY_VERIFICATION[stem], ('uv', 'run', 'pytest', '-q'))
    assert set(PRESERVATION[stem]) <= set(ENTRY_VERIFICATION[stem])
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
