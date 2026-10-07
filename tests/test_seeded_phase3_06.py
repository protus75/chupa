"""Continuation 06: one admission and its tail, pinned at the merged authoring head.

Measurements and closure findings are permanent authoring fixtures. Later seed lifecycle
history may stamp rejected; it does not change confirmed seed birth. No historical test moves.
"""

import hashlib

from dataclasses import dataclass
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ("merge-queue-activation", "rework-activation")
BATCH = (*PAYLOADS, "phase3-continue-07")
EDGES = {
    "merge-queue-activation": frozenset({"phase3-continue-06"}),
    "rework-activation": frozenset({"phase3-continue-06", "merge-queue-activation"}),
    "phase3-continue-07": frozenset(PAYLOADS),
}
START = {stem: ("medium", "medium") for stem in BATCH}
AUTHORED_STATE = {stem: "confirmed" for stem in BATCH}

# Authoring grep across chupa/, eval/ and tests/ covered MergeQueue/compose_pipeline,
# bind/pipeline callers, split/reject markers, render_over_bound, Rework/supersedes,
# import-closure negatives, not hasattr, and public-operation allowlists. The real
# binding keeps its public signatures, so unrelated bind callers need no migration.
# test_merge_queue_is_dormant and test_rework_is_dormant are already in their floors;
# the production harness has no additional queue-absence assertion at this head.
# No further earned path was found. Preservation suites below remain unedited.
FENCE_FLOORS = {'merge-queue-activation': ('chupa/merge.py',
                            'tests/test_merge.py',
                            'tests/test_mergequeue.py',
                            'tests/test_daemon_composition.py'),
 'rework-activation': ('chupa/daemon.py',
                       'chupa/rework.py',
                       'chupa/mergequeue.py',
                       'tests/test_rework.py',
                       'tests/test_daemon_composition.py'),
 'phase3-continue-07': ('tickets', 'tests/test_seeded_phase3_07.py')}
FENCE_ADDITIONS = {'merge-queue-activation': {'chupa/runner.py': 'CALLER CLOSURE: bind constructs compose_pipeline '
                                               'with its StageContext and required no-op '
                                               'escalation consumer; signatures and Dispatch stay '
                                               'unchanged.'},
 'rework-activation': {'chupa/runner.py': 'CALLER CLOSURE: production split/over-bound dispatch, '
                                          'held-lock retirement, bootstrap dependency admission '
                                          'and dead-dependency writer.',
                       'chupa/drain.py': 'CALLER CLOSURE: updated ticket re-offer, retry SHA '
                                         'accounting, all-successor eligibility and '
                                         'latest-transition seam consistency after rejected split retirement.',
                       'chupa/scheduler.py': 'CALLER CLOSURE: production selection must fold '
                                             'transitive successor leaves.',
                       'tests/test_ladder.py': 'CONTRADICTED TESTS: split case of '
                                               'test_reject_verdicts_auto_keep_once_and_draw_down '
                                               'pins Reject routing; retain reject/abandon-human '
                                               'cases.',
                       'tests/test_drain.py': 'CALLER CLOSURE: real drain re-entry, '
                                              'retry-before-running and terminal checks exercise '
                                              'changed ticket/application and dependency '
                                              'projections.',
                       'tests/test_scheduler.py': 'CALLER CLOSURE: production eligibility tests '
                                                  'call the selection path whose dependency '
                                                  'projection changes.',
                       'tests/test_reject_queue.py': 'CONTRADICTED TESTS/CALLER CLOSURE: '
                                                     'test_over_bound_premise_draws_nothing and '
                                                     'existing dead-dependency/reject mutation '
                                                     'callers; retain no-cap/no-Reject behavior.',
                       'tests/test_diagnose.py': 'CONTRADICTED TESTS: over-bound case of '
                                                 'test_missing_workspace_and_no_call_short_circuits '
                                                 'pins no model call; migrate only that case to '
                                                 'Rework without diagnosis.',
                       'tests/test_mergequeue.py': 'CONTRADICTED TESTS: '
                                                   'test_merge_queue_is_reachable_from_production pins '
                                                   'the predecessor dormancy this activation flips.'},
 'phase3-continue-07': {}}

AUTHORING_HEAD = '661689030678216d264a65c68c02f75f40e758e8'
MERGED_IDIOM = "tests/test_seeded_phase3_core.py"
MERGED_IDIOM_BLOB = '2feb2512789adbf84d57e9153d77d6a7a06edb8a'
HEADROOM_CHARS = 300_000  # 400,000 x 0.75, including maximum effort
IMPLEMENT_SPEC_CHARS = 4316
RENDER_OVERHEAD = 2_000  # conservative Context headers, separators and placeholders
PLAN_CHARS = {'19.I': 1811,
 '19.P3.merge-queue-activation': 7557,
 '19.P3.rework-activation': 18107,
 '19.L': 19167,
 '19.P3': 16053,
 '13': 19104,
 '19.P3.background-consumers': 5751,
 '19.P3.control-inbox': 8797,
 '20': 4367,
 '19.P3.dispatch-pause-boundary': 6074,
 '19.P3.pause-resume-activation': 7703,
 '19.P3.admission-holds-activation': 8124}
FILE_CHARS = {'chupa/merge.py': 12783,
 'tests/test_merge.py': 12936,
 'tests/test_mergequeue.py': 41202,
 'tests/test_daemon_composition.py': 34952,
 'chupa/runner.py': 27913,
 'chupa/daemon.py': 3082,
 'chupa/rework.py': 12278,
 'chupa/mergequeue.py': 15499,
 'tests/test_rework.py': 30007,
 'chupa/drain.py': 21251,
 'chupa/scheduler.py': 2253,
 'tests/test_ladder.py': 8853,
 'tests/test_drain.py': 18852,
 'tests/test_scheduler.py': 15289,
 'tests/test_reject_queue.py': 7929,
 'tests/test_diagnose.py': 9505,
 'tests/test_seeded_phase3_core.py': 5425}
DELIMITER_FREE_AT_AUTHORING = frozenset(FILE_CHARS)


@dataclass(frozen=True)
class Authored:
    chars: int
    plan: tuple[str, ...]
    context: tuple[str, ...]
    fenced_existing: tuple[str, ...]
    measured_render: int
    on_demand: tuple[str, ...] = ()


AUTHORED = {
    'merge-queue-activation': Authored(
        10083,
        ('19.I', '19.P3.merge-queue-activation'),
        ('chupa/merge.py', 'tests/test_merge.py', 'tests/test_mergequeue.py', 'tests/test_daemon_composition.py', 'chupa/runner.py'),
        ('chupa/merge.py', 'tests/test_merge.py', 'tests/test_mergequeue.py', 'tests/test_daemon_composition.py', 'chupa/runner.py'),
        153635,
    ),
    'rework-activation': Authored(
        23076,
        ('19.I', '19.P3.rework-activation'),
        ('chupa/daemon.py', 'chupa/rework.py', 'chupa/mergequeue.py', 'tests/test_rework.py', 'tests/test_daemon_composition.py', 'chupa/runner.py', 'chupa/drain.py', 'chupa/scheduler.py', 'tests/test_ladder.py', 'tests/test_drain.py', 'tests/test_scheduler.py', 'tests/test_reject_queue.py', 'tests/test_diagnose.py', 'tests/test_mergequeue.py'),
        ('chupa/daemon.py', 'chupa/rework.py', 'chupa/mergequeue.py', 'tests/test_rework.py', 'tests/test_daemon_composition.py', 'chupa/runner.py', 'chupa/drain.py', 'chupa/scheduler.py', 'tests/test_ladder.py', 'tests/test_drain.py', 'tests/test_scheduler.py', 'tests/test_reject_queue.py', 'tests/test_diagnose.py', 'tests/test_mergequeue.py'),
        255124,
    ),
    'phase3-continue-07': Authored(
        23469,
        ('19.L', '19.I', '19.P3', '13', '19.P3.background-consumers', '19.P3.control-inbox', '20', '19.P3.dispatch-pause-boundary', '19.P3.pause-resume-activation', '19.P3.admission-holds-activation'),
        ('tests/test_seeded_phase3_core.py',),
        (),
        130143,
    ),
}


OBLIGATIONS = {
    "merge-queue-activation": (
        "test_production_pipeline_composes_merge_queue",
        "test_merge_queue_composition_has_no_side_effects",
        "test_composed_merge_queue_admits_reviewed_candidate",
        "test_merge_queue_is_reachable_from_production",
        "test_inline_admission_does_not_use_merge_queue",
        "test_bootstrap_pipeline_keeps_inline_admission",
    ),
    "rework-activation": (
        "test_production_composes_rework_without_running_it",
        "test_production_consumes_conflict_handoff_after_unwind",
        "test_production_applies_reviewed_rework_orders",
        "test_production_refuses_failed_rework_publication",
        "test_rework_is_reachable_from_production",
        "test_admission_never_invokes_rework_inline",
        "test_split_dispatches_reviewed_rework",
        "test_rework_escalation_preserves_starting_capability_and_caps",
        "test_rework_update_reenters_on_fresh_content",
        "test_rework_split_successors_release_original_dependents",
        "test_rework_split_preserves_dispatch_terminal_invariant",
        "test_render_over_bound_dispatches_rework_without_diagnosis",
        "test_superseded_dependencies_require_all_successor_leaves",
        "test_dead_dependencies_resolve_through_supersedes",
        "test_render_over_bound_calls_rework_but_not_diagnosis",
    ),
}
TRANSITIONS = {
    "merge-queue-activation": {
        "test_merge_queue_is_dormant": "tests/test_mergequeue.py",
    },
    "rework-activation": {
        "test_rework_is_dormant": "tests/test_rework.py",
        "test_reject_verdicts_auto_keep_once_and_draw_down": "tests/test_ladder.py",
        "test_missing_workspace_and_no_call_short_circuits": "tests/test_diagnose.py",
        "test_over_bound_premise_draws_nothing": "tests/test_reject_queue.py",
    },
}
VERIFICATION = {
    "merge-queue-activation": (
        "uv", "run", "pytest", "tests/test_merge.py", "tests/test_mergequeue.py",
        "tests/test_daemon_composition.py", "tests/test_cli.py", "tests/test_drain.py",
    ),
    "rework-activation": (
        "uv", "run", "pytest", "tests/test_rework.py", "tests/test_daemon_composition.py",
        "tests/test_mergequeue.py", "tests/test_ladder.py", "tests/test_drain.py",
        "tests/test_scheduler.py", "tests/test_reject_queue.py", "tests/test_merge.py",
        "tests/test_diagnose.py", "tests/test_cli.py",
    ),
}
PRESERVATION = {
    "merge-queue-activation": ("tests/test_cli.py", "tests/test_drain.py"),
    "rework-activation": ("tests/test_merge.py", "tests/test_cli.py"),
}
# Fixed evidence obligations, read from the complete own-entry contracts at authoring.
RECORD_FACTS = {
    "merge-queue-activation": (
        "compose_pipeline(ctx, *, escalate) -> MergeQueue",
        "bind(checkout, llm)", "synchronous no-op escalation consumer",
        "compose_pipeline(ctx, escalate=consumer)", "Checkout", "Dispatch",
        "pending: {}", "active: None", "paused: false", "red_stems: []",
        "offer(ticket, *, attempt)", "list[StageResult | ConflictHandoff]",
        'CONFLICT_FACTS = "merge_conflict_facts"',
        "{kind, conflicted_paths, resolving_rung: none | mechanical | rework, strategy_paths, integration_red_paths}",
        'RED_STREAK = "merge_red_streak"', "{kind, stems, limit: 3}", "RED_STREAK_LIMIT = 3",
        'TREE_MISMATCH = "merge_tree_mismatch"', "{kind, checked_tree, main_tree}",
        "EventType.SIGNAL", "null key", "merge.write_squash", "merge/<stem>/<attempt>",
        "{to: merged, commit, reviewed_sha}", "sole squash Effect and merged-transition writer",
        "original `reviewed_sha`", "approval_invalidated: true",
        "exact context and consumer received", "returns that same queue",
        "no callable attribute or StageContext/driver slot is added",
        "no offer/process, git/verification, event, escalation, or background task",
        "inline `merge(ctx, ticket, *, attempt)`", "no-conflict-facts",
        "approval carry, seed safety, base-red policy, lifted ticket-plane restore, and conflict abort",
    ),
    "rework-activation": (
        "ConflictHandoff",
        "{stem: str, reviewed_sha: str, conflicted_paths: list[str], findings: list[Finding], approval_invalidated: true}",
        "committed text", "sorted and unique", "starting capability and source",
        "effective tier/effort", "starting `agent_tier`", "starting `agent_effort`",
        "ReworkOrder", "existing artifact provenance",
        "{stem: nonblank str, attempt: nonnegative int, action: update | split | escalate, tickets: list[{stem: nonblank str, ticket: nonblank str}]}",
        'REWORK_ORDER = "rework_order"', "{signal: rework_order, attempt: int, action: update | split | escalate}",
        "sole writer", "Accepted orders alone", "key: null", "EventType.SIGNAL",
        "exact reviewed", "section 10 ticket-plane Git/Effects lane",
        'SUPERSEDES = "supersedes"', "{signal: supersedes, successors: list[str]}",
        "split publishes every successor before calling existing `record_supersedes`",
        "Failed or partial publication writes no map and does not retire the original",
        "conflicting replacement, self-edge, or transitive cycle refuses",
        "supersedes_maps", "successor_leaves", "settled_dependencies", "dead_dependencies",
        "every transitive leaf", "`merged` or `already_satisfied`", "`rejected` or `abandoned`",
        "{signal: dead_dependency, dead: <stem>}", "failure_report",
        "never call the lock-acquiring `verdict` entrypoint",
        "producing run terminal before the separate retirement transition",
        "next_rung", "cap_consumed", "{cap: retry, ticket_sha: <committed ticket blob SHA>, rung: {tier, effort}}",
        "{to: <producing outcome>, stage: <producing stage>, reason: <finding codes or outcome>}",
        "successfully published split omits `dispatch`, `routed`, and `rung`",
        "update records `dispatch: retry`, with no `routed` or `rung`",
        "record `dispatch: escalate` and `rung: {tier, effort}`, with no `routed`",
        "record `dispatch: reject_queue` and `routed: reject_queue`",
        "terminal remains `to: premise_failed`", "`render_over_bound` reason",
        "omits `dispatch`, `routed`, and `rung` for every Rework result",
        "without a rung, cap draw, map, retirement, or Reject arrival",
        "No `dispatch: rework` value", "Spent caps continue to bypass Rework",
        "aborted the unfinished rebase", "cleared its active candidate", "released the serial admission slot",
        "original findings and conflict context unchanged", "fresh Implement, Check, and Review",
        "harvest -> dispatch -> journal -> wipe", "draws one existing `retry`",
        "updated committed ticket blob SHA", "premise_failed", "draws no retry unit",
        "Content edits reset neither budgets nor capability", "never real-model calls or wall-clock waits",
    ),
}
NEXT_OBLIGATIONS = (
    "test_construction_is_idle", "test_run_owns_three_concurrent_consumers",
    "test_consumer_failure_cancels_and_awaits_siblings", "test_run_cancellation_awaits_all_cleanup",
    "test_watcher_debounce_tasks_do_not_outlive_owner",
    "test_overlapping_run_is_refused_until_cleanup_finishes", "test_merge_results_remain_consumer_owned",
    "test_background_consumers_are_dormant", "test_request_shape_and_identity_fail_closed",
    "test_publication_is_durable_and_never_overwrites", "test_publication_crash_points",
    "test_publisher_never_writes_journal", "test_decision_precedes_application",
    "test_request_is_decided_once", "test_decision_crash_reconstructs_projection",
    "test_lifecycle_identity_never_retargets", "test_resume_matches_only_its_hold",
    "test_latest_accepted_pause_resume_wins", "test_control_inbox_is_dormant",
)


def render_chars(a: Authored, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + a.chars + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a.plan)
            + sum(FILE_CHARS[path] for path in (*a.context, *extra)))


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, siblings=BATCH)


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("merge-queue-activation", "rework-activation", "phase3-continue-07")
    assert len(set(BATCH)) == 3
    assert set(EDGES) == set(START) == set(AUTHORED_STATE) == set(BATCH)
    assert set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)
    assert len(BATCH) <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = _ticket(stem).frontmatter
    assert AUTHORED_STATE[stem] == "confirmed"
    assert fm.source == "seed" and fm.state in (AUTHORED_STATE[stem], "rejected")
    assert (fm.priority, fm.kind) == ("P1", "feature")
    assert (fm.agent_tier, fm.agent_effort) == START[stem] == ("medium", "medium")
    assert not fm.gate_bypass


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    t = _ticket(stem)
    assert 0 < t.expected_minutes < t.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize("stem", BATCH)
def test_dependencies_as_authored(stem):
    assert set(_ticket(stem).depends) == EDGES[stem]


@pytest.mark.parametrize("stem", BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    t = _ticket(stem)
    assert set(t.scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert all(FENCE_ADDITIONS[stem].values())
    if stem in PAYLOADS:
        assert set(TRANSITIONS[stem].values()) <= set(t.scope_fence) & set(t.context)
        assert "tests/test_daemon_composition.py" in t.scope_fence
        assert all(reason.startswith(("CALLER CLOSURE:", "CONTRADICTED TESTS:"))
                   or reason.startswith("CONTRADICTED TESTS/CALLER CLOSURE:")
                   for reason in FENCE_ADDITIONS[stem].values())


@pytest.mark.parametrize("stem", PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    assert t.plan_contract == AUTHORED[stem].plan == ("19.I", f"19.P3.{stem}")
    scope = t.sections["Scope in / Scope out"]
    assert all(f"- **{part}:**" in scope for part in ("Owner", "Records", "Observable", "Tests"))
    assert len(OBLIGATIONS[stem]) == (6 if stem == PAYLOADS[0] else 15)
    for fact in (*OBLIGATIONS[stem], *TRANSITIONS[stem], *RECORD_FACTS[stem]):
        assert fact in scope, fact
    assert "production" in scope
    if stem == PAYLOADS[1]:
        assert "parallel" in scope
    assert "tests/test_daemon_composition.py" in scope
    assert "bootstrap" in scope.lower() and "inline" in scope


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket("phase3-continue-07")
    assert t.plan_contract == AUTHORED[t.stem].plan
    assert set(t.plan_contract) == {
        "19.L", "19.I", "19.P3", "13", "20", "19.P3.background-consumers",
        "19.P3.control-inbox", "19.P3.dispatch-pause-boundary", "19.P3.pause-resume-activation",
        "19.P3.admission-holds-activation",
    }
    assert t.context == (MERGED_IDIOM,)
    assert t.scope_fence == ("tickets", "tests/test_seeded_phase3_07.py")
    assert len(AUTHORING_HEAD) == len(MERGED_IDIOM_BLOB) == 40
    assert MERGED_IDIOM_BLOB == "2feb2512789adbf84d57e9153d77d6a7a06edb8a"
    assert "admissions[7:]" in t.sections["Goal / Why"]
    scope = t.sections["Scope in / Scope out"]
    for fact in (*NEXT_OBLIGATIONS,
        "entry_unit_gap", "resolve_plan_contract", "section 11.4", "premise_failed",
        "BEGIN_REGISTRY_P3", "END_REGISTRY_P3", "admissions[8:]", "admissions[9:]",
        "control-inbox seed explicitly depends on its background-consumers sibling",
        "depending on both background-consumers and control-inbox",
        "pause-resume-activation seed explicitly depends on its dispatch-pause-boundary sibling",
        "exact phase3-continue-08 Plan contract is 19.L, 19.I, 19.P3, section 13, section 20, "
        "19.P3.dispatch-pause-boundary, 19.P3.pause-resume-activation and 19.P3.admission-holds-activation",
        "tests/test_seeded_phase3_08.py", "tests/test_seeded_phase3_core.py",
        "Both construction payloads leave chupa/__main__.py and tests/test_daemon_composition.py unedited",
        "Daemon import absence is no longer evidence", "300,000-character headroom",
        "Prompt-specs and delimiter-bearing sources are never Context",
        "file sizes, ticket sizes and plan-unit lengths recorded IN that test",
        "terminal phase3-exit as its sole payload with no successor",
        "seeding.max_seeds_per_admission", "Deep rows start high/high; other rows medium/medium",
        "keep previously approved seeds verbatim", "ticket_sha",
        "chupa(phase3-continue-07): seeds", "Commit only this ticket's new test",
        "DaemonTasks", "watcher", "merge_queue", "box_consumer", "tasks",
        "publish(path, data: bytes) -> None", "FileSystem", "LocalFileSystem",
        "{request_id: str, lifecycle_id: str, verb: pause | resume | kill, hold_id: str | null}",
        'CONTROL_DECISION = "control_decision"',
        "{kind: control_decision, request_id: str, lifecycle_id: str | null, verb: pause | resume | kill | null, hold_id: str | null, decision: accepted | stale | rejected, reason: str}",
        "sole writer", "without overwriting", "fsync", "before invoking any application callback",
        "old-lifecycle", "idempotent", "latest accepted pause/resume",
    ):
        assert fact.lower() in scope.lower(), fact
    assert t.verification == (
        ("uv", "run", "pytest", "-q", "tests/test_seeded_phase3_07.py"),
        ("uv", "run", "pytest", "-q"),
    )


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a, t = AUTHORED[stem], _ticket(stem)
    assert t.context == a.context and t.on_demand == a.on_demand == ()
    created = set() if stem in PAYLOADS else {"tickets", "tests/test_seeded_phase3_07.py"}
    assert set(a.fenced_existing) == set(t.scope_fence) - created
    assert set(a.fenced_existing) <= set(a.context) | set(a.on_demand)
    assert not created & (set(a.context) | set(a.on_demand))
    assert not set(a.context) & set(a.on_demand)
    assert set(a.context) <= DELIMITER_FREE_AT_AUTHORING
    assert not any(p.startswith("specs/") for p in (*a.context, *a.on_demand))
    assert all(FILE_CHARS[p] > 0 for p in (*a.context, *a.on_demand))
    assert all(PLAN_CHARS[pid] > 0 for pid in a.plan)
    assert 0 < a.measured_render <= render_chars(a) <= HEADROOM_CHARS
    for path in a.on_demand:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize("stem", PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification == (VERIFICATION[stem], ("uv", "run", "pytest", "-q"))
    assert set(PRESERVATION[stem]) <= set(VERIFICATION[stem])
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))


# Entire Owner/Records/Observable/Tests contracts resolved at authoring, including
# the handoff terminal writer/markers and split dispatch return invariant.
OWN_ENTRY_SHA256 = {'merge-queue-activation': 'cf239b98c6a88acfad30ec6fa976ad11e5dd74cad4030630adb7dd068d85b8a3',
 'rework-activation': 'e3e51d8dfbd8bd1ac19ddc16dcd1281db38648f3223bf21a56d1c1f13aa3fb5c'}


@pytest.mark.parametrize("stem", PAYLOADS)
def test_complete_own_entry_contract_is_carried_verbatim(stem):
    scope = _ticket(stem).sections["Scope in / Scope out"]
    entry = scope.split("\n\nCALLER CLOSURE", 1)[0].strip()
    assert hashlib.sha256(entry.encode()).hexdigest() == OWN_ENTRY_SHA256[stem]
