"""Phase 3 admission 02: structure over permanent authoring-time render snapshots.

Only the payload and its successor belong to this batch. A later rejected stamp is
lifecycle history; render assertions never measure the live files or plan again.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
BATCH = ("rework-stage", "phase3-continue-03")
EDGES = {
    "rework-stage": frozenset({"phase3-continue-02"}),
    "phase3-continue-03": frozenset({"rework-stage"}),
}
# Authoring parsed deep: true for Rework directly from the current plan registry.
# Its Driver, grammar/review, journal and admission seams earn the high/high start.
START = {"rework-stage": ("high", "high"), "phase3-continue-03": ("medium", "medium")}
AUTHORED_STATE = {stem: "confirmed" for stem in BATCH}
FENCE_FLOORS = {
    "rework-stage": ("chupa/rework.py", "specs/rework.md", "chupa/mergequeue.py",
                     "tests/test_rework.py"),
    "phase3-continue-03": ("tickets", "tests/test_seeded_phase3_03.py"),
}
# 19.L rules 2-5 earn no additions: construction flips no assertions or production
# callers/signatures. rework.py owns the new schema, stage and supersedes folds.
# Authoring greps found ConflictHandoff consumers only in the dormant queue tests,
# split-to-Reject in runner/ladder, and no existing Rework public-surface allowlist.
# Those existing assertions stay valid; their suites are preservation, not edits.
FENCE_ADDITIONS = {stem: {} for stem in BATCH}

# Section 8's bound is identical at maximum effort: 400,000 x 0.75.
HEADROOM_CHARS = 300_000
IMPLEMENT_SPEC_CHARS = 4_437
RENDER_OVERHEAD = 2_000  # conservative data-block and Context-header allowance
PLAN_CHARS = {
    "19.I": 1_811, "19.P3.rework-stage": 9_256,
    "4": 1_896, "9": 19_656, "11": 26_806,
    "19.L": 19_167, "19.P3": 16_053, "19.P3.thresh-runtime": 9_849,
    "19.P3.dispatch-admission-boundary": 4_771,
    "19.P3.dispatch-config-snapshot": 5_953, "13": 19_104,
}
FILE_CHARS = {
    "chupa/mergequeue.py": 15_227, "chupa/artifacts.py": 6_436,
    "chupa/driver.py": 11_549, "chupa/requisition.py": 7_342,
    "tests/test_seeded_phase3_core.py": 5_425,
}


@dataclass(frozen=True)
class Authored:
    chars: int
    plan: tuple[str, ...]
    context: tuple[str, ...]
    measured_render: int
    on_demand: tuple[str, ...] = ()
    fenced_existing: tuple[str, ...] = ()


AUTHORED = {
    "rework-stage": Authored(
        14_014, ("19.I", "19.P3.rework-stage", "4", "9", "11"),
        ("chupa/mergequeue.py", "chupa/artifacts.py", "chupa/driver.py",
         "chupa/requisition.py"), 118_352,
        fenced_existing=("chupa/mergequeue.py",),
    ),
    "phase3-continue-03": Authored(
        6_984, ("19.L", "19.I", "19.P3", "19.P3.thresh-runtime",
                "19.P3.dispatch-admission-boundary", "19.P3.dispatch-config-snapshot", "13"),
        ("tests/test_seeded_phase3_core.py",), 93_415,
    ),
}


def render_chars(a: Authored, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + a.chars + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a.plan)
            + sum(FILE_CHARS[path] for path in (*a.context, *extra)))


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("rework-stage", "phase3-continue-03")
    assert len(set(BATCH)) == 2
    assert set(EDGES) == set(START) == set(AUTHORED_STATE) == set(BATCH)
    assert set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = _ticket(stem).frontmatter
    assert AUTHORED_STATE[stem] == "confirmed"
    assert fm.source == "seed"
    assert fm.state in (AUTHORED_STATE[stem], "rejected")
    assert (fm.priority, fm.kind) == ("P1", "feature")
    assert (fm.agent_tier, fm.agent_effort) == START[stem]
    assert not fm.gate_bypass


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    assert _ticket(stem).stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize("stem", BATCH)
def test_dependencies_as_authored(stem):
    assert set(_ticket(stem).depends) == EDGES[stem]


@pytest.mark.parametrize("stem", BATCH)
def test_fence_contains_its_floor_and_only_earned_additions(stem):
    assert set(_ticket(stem).scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert all(FENCE_ADDITIONS[stem].values())


def test_deep_payload_cites_exactly_its_own_entry_and_row_contract():
    t = _ticket("rework-stage")
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("high", "high")
    assert t.plan_contract == AUTHORED[t.stem].plan
    assert t.plan_contract == ("19.I", "19.P3.rework-stage", "4", "9", "11")
    assert "19.P3" not in t.plan_contract


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket("phase3-continue-03")
    assert t.plan_contract == AUTHORED[t.stem].plan
    assert t.context == ("tests/test_seeded_phase3_core.py",)
    assert t.scope_fence == FENCE_FLOORS[t.stem]


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a = AUTHORED[stem]
    t = _ticket(stem)
    assert t.context == a.context
    assert t.on_demand == a.on_demand
    assert set(a.fenced_existing) <= set(a.context) | set(a.on_demand)
    assert not set(a.context) & set(a.on_demand)
    created = (set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])) - set(a.fenced_existing) - {"tickets"}
    assert not created & (set(a.context) | set(a.on_demand))
    assert not any(p.startswith("specs/") for p in (*a.context, *a.on_demand))
    assert 0 < a.measured_render <= render_chars(a) <= HEADROOM_CHARS
    assert a.chars > 0
    assert all(FILE_CHARS[p] > 0 for p in (*a.context, *a.on_demand))
    assert all(PLAN_CHARS[pid] > 0 for pid in a.plan)
    for path in a.on_demand:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


def test_rework_runs_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket("rework-stage")
    preservation = {"tests/test_mergequeue.py", "tests/test_ladder.py", "tests/test_drain.py",
                    "tests/test_merge.py", "tests/test_driver.py", "tests/test_requisition.py",
                    "tests/test_tickets.py", "tests/test_specs.py"}
    assert preservation <= {arg for argv in t.verification for arg in argv}
    assert not preservation & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
