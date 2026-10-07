"""Continuation 09: two seeds, fixed authoring snapshots, and earned caller closure.

The live registry was parsed directly at AUTHORING_HEAD; only positions 9, 10 and
11 were needed. Five complete entry units passed entry_unit_gap and
resolve_plan_contract before writing. The approved successor remains byte-identical.
Authoring rg across chupa/, eval/ and tests/ covered compose_pipeline, write_active,
Checkout, bind, build_control, PauseConsumer, drain, queue.resume, public allowlists,
not hasattr and hold-absence values. CALLER_SNAPSHOTS records the result. No
historical seeding fixture is migrated. Render arithmetic never reads live sizes
or live plan lengths; intake validation alone reads the governing live artifacts.
"""

import hashlib
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

PAYLOADS = ('admission-holds-activation',)

BATCH = ('admission-holds-activation', 'phase3-continue-10')

AUTHORING_HEAD = '66f29ef2775674c3cc8e001f2cf5eee809bfcab4'

MERGED_IDIOM = 'tests/test_seeded_phase3_core.py'

MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'

APPROVED_SUCCESSOR_SHA256 = '6f58f7e41fb1e5a75e19a77819b346ace303cf76d44ddc5672c5b80d9b776f6b'

HEADROOM_CHARS = 300000

IMPLEMENT_SPEC_CHARS = 4316

RENDER_OVERHEAD = 2000

EDGES = {'admission-holds-activation': ('phase3-continue-09', 'pause-resume-activation'),
 'phase3-continue-10': ('admission-holds-activation',)}

FENCE_FLOORS = {'admission-holds-activation': ('chupa/mergequeue.py',
                                'chupa/merge.py',
                                'chupa/__main__.py',
                                'eval/shakeout/bench.py',
                                'tests/test_mergequeue.py',
                                'tests/test_merge.py',
                                'tests/test_daemon_composition.py'),
 'phase3-continue-10': ('tickets', 'tests/test_seeded_phase3_10.py')}

FENCE_ADDITIONS = {'admission-holds-activation': {'chupa/runner.py': 'CALLER CLOSURE: final Checkout.control carrier '
                                                   'and production bind/prepare_pipeline '
                                                   'forwarding',
                                'chupa/drain.py': 'CALLER CLOSURE: publish/consume/retire supplied '
                                                  'carrier; remove its build_control construction',
                                'tests/test_drain.py': 'CALLER CLOSURE: direct drain root '
                                                       'pause_checkout supplies control and tests '
                                                       'exact custody',
                                'chupa/control.py': 'CALLER CLOSURE: write_active requires '
                                                    'explicitly selected hold_id',
                                'chupa/daemon.py': 'CALLER CLOSURE: write_active production caller '
                                                   'and shared admission slot/selector',
                                'tests/test_control_cli.py': 'CALLER CLOSURE: discovery and '
                                                             'retirement directly call '
                                                             'write_active; selected-hold CLI '
                                                             'test'},
 'phase3-continue-10': {}}

FILE_CHARS = {'chupa/__main__.py': 8778,
 'chupa/control.py': 8137,
 'chupa/daemon.py': 12815,
 'chupa/drain.py': 23628,
 'chupa/merge.py': 13190,
 'chupa/mergequeue.py': 15499,
 'chupa/runner.py': 33081,
 'eval/shakeout/bench.py': 4542,
 'tests/test_control_cli.py': 9168,
 'tests/test_daemon_composition.py': 76368,
 'tests/test_drain.py': 40429,
 'tests/test_merge.py': 14391,
 'tests/test_mergequeue.py': 41612,
 'tests/test_seeded_phase3_core.py': 5425}

PLAN_CHARS = {'19.I': 1811,
 '19.P3.admission-holds-activation': 17841,
 '19.L': 19332,
 '19.P3': 16053,
 '13': 19104,
 '20': 4367,
 '19.P3.kill-signal-journal': 5337,
 '19.P3.kill-executor-abort': 5396,
 '19.P3.kill-worker-stop': 5597,
 '19.P3.kill-failure-suppression': 5452,
 '6': 36783}

AUTHORED = {'admission-holds-activation': {'chars': 26777,
                                'plan': ('19.I', '19.P3.admission-holds-activation'),
                                'context': ('chupa/mergequeue.py',
                                            'chupa/merge.py',
                                            'chupa/__main__.py',
                                            'eval/shakeout/bench.py',
                                            'tests/test_mergequeue.py',
                                            'tests/test_merge.py',
                                            'chupa/runner.py',
                                            'chupa/drain.py',
                                            'tests/test_drain.py',
                                            'chupa/control.py',
                                            'chupa/daemon.py',
                                            'tests/test_control_cli.py'),
                                'on_demand': ('tests/test_daemon_composition.py',),
                                'fenced_existing': ('chupa/mergequeue.py',
                                                    'chupa/merge.py',
                                                    'chupa/__main__.py',
                                                    'eval/shakeout/bench.py',
                                                    'tests/test_mergequeue.py',
                                                    'tests/test_merge.py',
                                                    'tests/test_daemon_composition.py',
                                                    'chupa/runner.py',
                                                    'chupa/drain.py',
                                                    'tests/test_drain.py',
                                                    'chupa/control.py',
                                                    'chupa/daemon.py',
                                                    'tests/test_control_cli.py'),
                                'created': (),
                                'measured_render': 276261},
 'phase3-continue-10': {'chars': 30449,
                        'plan': ('19.L',
                                 '19.I',
                                 '19.P3',
                                 '13',
                                 '20',
                                 '19.P3.kill-signal-journal',
                                 '19.P3.kill-executor-abort',
                                 '19.P3.kill-worker-stop',
                                 '19.P3.kill-failure-suppression',
                                 '6'),
                        'context': ('tests/test_seeded_phase3_core.py',),
                        'on_demand': (),
                        'fenced_existing': (),
                        'created': ('tickets', 'tests/test_seeded_phase3_10.py'),
                        'measured_render': 159404}}

DELIMITER_FREE_AT_AUTHORING = ('chupa/__main__.py',
 'chupa/control.py',
 'chupa/daemon.py',
 'chupa/drain.py',
 'chupa/merge.py',
 'chupa/mergequeue.py',
 'chupa/runner.py',
 'eval/shakeout/bench.py',
 'tests/test_control_cli.py',
 'tests/test_daemon_composition.py',
 'tests/test_drain.py',
 'tests/test_merge.py',
 'tests/test_mergequeue.py',
 'tests/test_seeded_phase3_core.py')

ENTRY_SHA256 = {'admission-holds-activation': 'd7f231f72fa8120f0cfc4adab8093ff04ae509cf61b40cc301490b8b9f42c4a7',
 'kill-signal-journal': '016e237e308a72535b7191936032f9fbf0c3da7b51818056a3046c860677f106',
 'kill-executor-abort': 'bb6a9c45541b8018cfee67e3dde7360a814b2c0d8ed7e8865f73ba4fa869dfe8',
 'kill-worker-stop': '15ad678c8cad74d5f140e37d0234074aa1b44d9474393a3cf5c0cf7780ae1080',
 'kill-failure-suppression': '9d839772525de871cc7f5367f8d917546bf932dd99a42e87046d0f247525ea21'}

NAMED_INVARIANTS = {'admission-holds-activation': ('test_drain',
                                'test_reject_queue',
                                'test_daemon_tasks',
                                'test_control_cli',
                                'test_mergequeue',
                                'test_admission_hold_signal_precedes_projection',
                                'test_admission_resume_matches_lifecycle_and_hold',
                                'test_admission_resume_decision_precedes_release',
                                'test_distinct_red_streak_pause_and_resume',
                                'test_tree_mismatch_escalates_and_pauses',
                                'test_resume_waits_for_active_admission',
                                'test_daemon_composition',
                                'test_production_shares_one_admission_control_consumer',
                                'test_composed_admission_holds_accept_identity_bound_resume',
                                'test_bootstrap_inline_admission_never_holds',
                                'test_resume_publishes_selected_hold_identity',
                                'test_live_pause_resume_publish_without_journal_write',
                                'test_pause_resume_apply_directly_under_lock',
                                'test_drain_uses_supplied_control',
                                'test_merge',
                                'test_pipeline_requires_supplied_control',
                                'test_bootstrap_pipeline_keeps_inline_admission',
                                'test_control',
                                'test_daemon_pause',
                                'test_cli',
                                'test_shakeout'),
 'kill-signal-journal': ('test_kill_signal_journal',
                         'test_kill_decision_precedes_projection',
                         'test_kill_identity_and_shape_fail_closed',
                         'test_kill_decision_is_once',
                         'test_kill_decision_crash_recovery',
                         'test_kill_projection_stays_latched',
                         'test_kill_signal_journal_is_dormant',
                         'test_control',
                         'test_cli',
                         'test_drain',
                         'test_daemon_composition'),
 'kill-executor-abort': ('test_kill_executor_abort',
                         'test_executor_abort_stops_writer_before_cancellation',
                         'test_executor_abort_waits_for_unwind',
                         'test_executor_abort_is_atomic_under_repeated_cancellation',
                         'test_executor_abort_idle_and_completion_race',
                         'test_external_abort_does_not_reprompt_or_report_success',
                         'test_executor_abort_is_dormant',
                         'test_driver',
                         'test_cli',
                         'test_drain',
                         'test_daemon_composition'),
 'kill-worker-stop': ('test_kill_worker_stop',
                      'test_executor_unwinds_before_worker_cancel',
                      'test_worker_stop_requires_matching_kill',
                      'test_worker_stop_observes_all_workers',
                      'test_worker_stop_is_atomic_under_repeated_cancellation',
                      'test_executor_abort_failure_does_not_cancel_workers',
                      'test_kill_worker_stop_is_dormant',
                      'test_kill_executor_abort',
                      'test_daemon_tasks',
                      'test_cli',
                      'test_drain',
                      'test_daemon_composition'),
 'kill-failure-suppression': ('test_kill_failure_suppression',
                              'test_post_kill_worker_failures_are_suppressed',
                              'test_worker_failures_without_matching_kill_are_preserved',
                              'test_kill_suppression_observes_all_worker_outcomes',
                              'test_kill_suppression_waiter_cancellation_awaits_cleanup',
                              'test_kill_suppression_preserves_run_and_abort_failures',
                              'test_kill_failure_suppression_is_dormant',
                              'test_kill_worker_stop',
                              'test_daemon_tasks',
                              'test_cli',
                              'test_drain',
                              'test_daemon_composition')}

ENTRY_VERIFICATION = {'admission-holds-activation': ('uv',
                                'run',
                                'pytest',
                                'tests/test_mergequeue.py',
                                'tests/test_merge.py',
                                'tests/test_daemon_composition.py',
                                'tests/test_control.py',
                                'tests/test_control_cli.py',
                                'tests/test_daemon_pause.py',
                                'tests/test_cli.py',
                                'tests/test_drain.py',
                                'tests/test_shakeout.py'),
 'kill-signal-journal': ('uv',
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
                         'tests/test_daemon_composition.py'),
 'kill-worker-stop': ('uv',
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

PRESERVATION = ('tests/test_control.py',
 'tests/test_daemon_pause.py',
 'tests/test_cli.py',
 'tests/test_shakeout.py')

CALLER_SNAPSHOTS = {'compose_pipeline': ('chupa/runner.py', 'tests/test_daemon_composition.py'),
 'write_active': ('chupa/daemon.py', 'tests/test_control_cli.py'),
 'direct_carrier_roots': ('chupa/__main__.py',
                          'eval/shakeout/bench.py',
                          'tests/test_merge.py',
                          'tests/test_daemon_composition.py',
                          'tests/test_drain.py'),
 'unchanged_carried_bind': 'Other test bind callers, including test_seed_successor probes, receive '
                           'main pipeline checkout',
 'unchanged_positional': ('chupa/runner.py:failure_terminal',
                          'tests/test_reject_queue.py',
                          'tests/test_daemon_tasks.py',
                          'tests/test_drain.py:_Drain-only'),
 'flipped_resume': ('tests/test_mergequeue.py:510',
                    'tests/test_mergequeue.py:543',
                    'tests/test_mergequeue.py:794'),
 'dormancy_migration': ('tests/test_mergequeue.py', 'tests/test_daemon_composition.py')}


def _text(stem):
    return (ROOT / ticket_path(stem)).read_text()


def _ticket(stem):
    return validate_ticket(stem, _text(stem), ROOT)


def _digest(text):
    return hashlib.sha256(text.strip().encode()).hexdigest()


def render_chars(a, extra=()):
    return (IMPLEMENT_SPEC_CHARS + a['chars'] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a['plan'])
            + sum(FILE_CHARS[p] for p in (*a['context'], *extra)))


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ('admission-holds-activation', 'phase3-continue-10')
    assert PAYLOADS == BATCH[:1] and len(set(BATCH)) == 2
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)


@pytest.mark.parametrize('stem', BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    t = _ticket(stem)
    assert t.frontmatter.state in {'confirmed', 'rejected'}  # later rejection is lifecycle history
    birth = validate_ticket(stem, _text(stem).replace('state: rejected', 'state: confirmed', 1), ROOT)
    fm = birth.frontmatter
    assert (fm.source, fm.state, fm.kind, fm.priority) == ('seed', 'confirmed', 'feature', 'P1')
    assert (fm.agent_tier, fm.agent_effort) == ('medium', 'medium')
    assert fm.gate_bypass == []


@pytest.mark.parametrize('stem', BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert t.expected_minutes == 60 and t.stuck_minutes == 90
    assert t.expected_minutes <= t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize('stem', BATCH)
def test_dependencies_as_authored(stem):
    assert _ticket(stem).depends == EDGES[stem]
    assert EDGES[PAYLOADS[0]] == ('phase3-continue-09', 'pause-resume-activation')
    assert EDGES[BATCH[-1]] == PAYLOADS


@pytest.mark.parametrize('stem', BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t, a = _ticket(stem), AUTHORED[stem]
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    for path, reason in FENCE_ADDITIONS[stem].items():
        assert reason.startswith('CALLER CLOSURE:') and path in t.sections['Scope in / Scope out']
        assert path in a['context'] or path in a['on_demand']
    if stem == PAYLOADS[0]:
        for group in ('compose_pipeline', 'write_active', 'direct_carrier_roots', 'dormancy_migration'):
            assert set(CALLER_SNAPSHOTS[group]) <= set(t.scope_fence)
        assert {p.split(':')[0] for p in CALLER_SNAPSHOTS['flipped_resume']} <= set(t.scope_fence)
        assert not {'tests/test_reject_queue.py', 'tests/test_daemon_tasks.py',
                    'tests/test_seed_successor.py'} & set(t.scope_fence)
        assert not any(p.startswith('tests/test_seeded_') for p in t.scope_fence)


def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract():
    t = _ticket(PAYLOADS[0])
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == ('19.I', '19.P3.admission-holds-activation')
    scope = t.sections['Scope in / Scope out']
    entry = scope.split('\n\nAUTHORING CLOSURE:', 1)[0]
    # Digest covers all four complete bullets, including every shape, writer and invariant.
    assert _digest(entry) == ENTRY_SHA256[t.stem]
    for part in ('Owner', 'Records', 'Observable', 'Tests'):
        assert f'- **{part}:**' in entry
    for name in NAMED_INVARIANTS[t.stem]:
        assert name in entry
    for fact in (
        'Checkout.control: PauseConsumer | None = None',
        'replace(checkout, control=build_control(checkout))',
        'compose_pipeline(ctx, *, escalate, control)', 'uuid4().hex',
        '{kind: merge_red_streak, stems: list[str], limit: 3, hold_id: nonempty str}',
        '{kind: merge_tree_mismatch, checked_tree: str, main_tree: str, hold_id: nonempty str}',
        'journal that signal BEFORE', 'then invoke `escalate(event)`',
        'Its durable accepted decision must precede queue release',
        'process()`\'s serial boundary', 'consumer.projection.released_hold_ids',
        'write_active(state_dir, projection, fs, *, hold_id)',
        'ControlProjection.pause_id` continues to mean only the dispatch pause',
        'first CLI `resume`', 'second `resume`', 'consumer holds no queue reference',
        'consumer; `build_daemon_core` constructs its own', 'CoreRig` itself is unchanged',
        'only for the dispatching verbs `run` and `drain`',
        'real factory-returned queue', 'no fallback construction', 'never acquire admission holds',
        'The control CLI suite is therefore an edited caller suite',
    ):
        assert fact in entry, fact


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket(BATCH[-1])
    birth_text = _text(t.stem).replace('state: rejected', 'state: confirmed', 1)
    assert hashlib.sha256(birth_text.encode()).hexdigest() == APPROVED_SUCCESSOR_SHA256
    assert t.plan_contract == AUTHORED[t.stem]['plan'] == (
        '19.L', '19.I', '19.P3', '13', '20', '19.P3.kill-signal-journal',
        '19.P3.kill-executor-abort', '19.P3.kill-worker-stop', '19.P3.kill-failure-suppression', '6',
    )
    assert t.scope_fence == ('tickets', 'tests/test_seeded_phase3_10.py')
    assert t.context == (MERGED_IDIOM,) == ('tests/test_seeded_phase3_core.py',)
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    scope = t.sections['Scope in / Scope out']
    for stem, following in (
        ('kill-signal-journal', 'Carry this complete kill-executor-abort contract verbatim:'),
        ('kill-executor-abort', 'Create phase3-continue-11'),
        ('kill-worker-stop', 'Carry this complete kill-failure-suppression contract into the successor verbatim:'),
        ('kill-failure-suppression', 'Each continuation authors only'),
    ):
        marker = (f'Carry this complete {stem} contract verbatim:' if stem in
                  {'kill-signal-journal', 'kill-executor-abort'} else
                  f'Carry this complete {stem} contract into the successor verbatim:')
        carried = scope.split(marker, 1)[1].split(following, 1)[0].strip()
        assert _digest(carried) == ENTRY_SHA256[stem]
        for name in NAMED_INVARIANTS[stem]:
            assert name in carried
        assert ' '.join(ENTRY_VERIFICATION[stem]) in carried
    for fact in (
        'BEGIN_REGISTRY_P3', 'END_REGISTRY_P3', 'admissions[10:]', 'admissions[11:]',
        'admissions[12:]', 'entry_unit_gap', 'resolve_plan_contract', 'section 11.4',
        'premise_failed', 'Author only kill-signal-journal, kill-executor-abort and phase3-continue-11',
        'Both implementing seeds start medium/medium and depend on phase3-continue-10',
        'kill-executor-abort also explicitly depends on kill-signal-journal',
        '19.I, 19.P3.kill-signal-journal, section 20',
        '19.I, 19.P3.kill-executor-abort, section 20, section 6',
        'depending on both kill-signal-journal and kill-executor-abort',
        'tests/test_seeded_phase3_11.py', 'never this batch\'s tests/test_seeded_phase3_10.py',
        '19.L closure rules 2-5', 'Context/on-demand partition', '300,000-character headroom',
        'Prompt-specs and delimiter-bearing sources are never Context',
        'Preservation suites stay unchanged in Verification only, neither fenced nor embedded',
        'file sizes, ticket sizes and plan-unit lengths recorded IN that test',
        'seeding.max_seeds_per_admission', 'Deep rows start high/high; other rows medium/medium',
        'terminal phase3-exit as its sole payload with no successor',
        'keep previously approved seeds verbatim', 'ticket_sha',
        'chupa(phase3-continue-10): seeds', 'Commit only this ticket\'s new test',
    ):
        assert fact in scope, fact
    assert t.verification == (('uv', 'run', 'pytest', '-q', 'tests/test_seeded_phase3_10.py'),
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


def test_payloads_run_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket(PAYLOADS[0])
    assert t.verification == (ENTRY_VERIFICATION[t.stem], ('uv', 'run', 'pytest', '-q'))
    assert set(PRESERVATION) <= set(ENTRY_VERIFICATION[t.stem])
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
