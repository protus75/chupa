"""Phase 3 admission 01: identity and structure over fixed authoring-time measurements.

Only these two seeds belong to this admission. Render assertions never measure the live
tree or plan; a later rejected stamp records lifecycle history, not authored seed drift.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
BATCH = ("merge-queue", "phase3-continue-02")
EDGES = {
    "merge-queue": frozenset({"phase3-continue"}),
    "phase3-continue-02": frozenset({"merge-queue"}),
}
START = {"merge-queue": ("high", "high"), "phase3-continue-02": ("medium", "medium")}
AUTHORED_STATE = {stem: "confirmed" for stem in BATCH}
FENCE_FLOORS = {
    "merge-queue": ("chupa/mergequeue.py", "chupa/merge.py", "chupa/git.py",
                    "tests/test_mergequeue.py", "tests/test_git.py"),
    "phase3-continue-02": ("tickets", "tests/test_seeded_phase3_02.py"),
}
# 19.L rule 4 / section 9.5, explicitly earned by 19.P3.merge-queue's Owner:
# stages owns the safety-evidence extraction; its tests prove one metadata producer.
# No activation, signature change, or contradicted assertion earns another path.
FENCE_ADDITIONS = {
    "merge-queue": {
        "chupa/stages.py": "rule 4: stage-owned safety evidence extraction, section 9.5",
        "tests/test_stages.py": "rule 4: prove safety extraction and full gatherer reuse",
    },
    "phase3-continue-02": {},
}

# Permanent authoring snapshots: section 8's 400,000 bound x 0.75 at max effort.
HEADROOM_CHARS = 300_000
IMPLEMENT_SPEC_CHARS = 4_437
RENDER_OVERHEAD = 2_000  # conservative data-block and Context-header allowance
PLAN_CHARS = {
    "19.L": 19_167, "19.I": 1_811, "19.P3": 16_053,
    "19.P3.merge-queue": 18_217, "19.P3.rework-stage": 9_256,
    "19.P3.thresh-runtime": 9_849, "9": 19_656, "10": 6_636, "13": 19_104,
}
FILE_CHARS = {
    "chupa/merge.py": 11_791, "chupa/git.py": 5_232, "tests/test_git.py": 13_592,
    "chupa/stages.py": 50_236, "tests/test_stages.py": 21_954,
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
    "merge-queue": Authored(
        21_086, ("19.I", "19.P3.merge-queue", "9", "10"),
        ("chupa/merge.py", "chupa/git.py", "tests/test_git.py", "chupa/stages.py",
         "tests/test_stages.py"), 174_583,
        fenced_existing=("chupa/merge.py", "chupa/git.py", "tests/test_git.py",
                         "chupa/stages.py", "tests/test_stages.py"),
    ),
    "phase3-continue-02": Authored(
        6_377, ("19.L", "19.I", "19.P3", "19.P3.rework-stage", "19.P3.thresh-runtime", "13"),
        ("tests/test_seeded_phase3_core.py",), 91_340,
    ),
}


def render_chars(a: Authored, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + a.chars + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a.plan)
            + sum(FILE_CHARS[path] for path in (*a.context, *extra)))


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("merge-queue", "phase3-continue-02")
    assert len(set(BATCH)) == 2
    assert set(EDGES) == set(START) == set(AUTHORED_STATE) == set(BATCH)
    assert set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = _ticket(stem).frontmatter
    assert AUTHORED_STATE[stem] == "confirmed"
    assert fm.source == "seed"
    assert fm.state in (AUTHORED_STATE[stem], "rejected")
    assert (fm.agent_tier, fm.agent_effort) == START[stem]


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
    t = _ticket("merge-queue")
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("high", "high")
    # Authoring parsed deep: true from the registry; cross-module seams earn this start.
    assert t.plan_contract == AUTHORED[t.stem].plan
    assert "19.P3" not in t.plan_contract


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket("phase3-continue-02")
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
    created = set(FENCE_FLOORS[stem]) - set(a.fenced_existing) - {"tickets"}
    assert not created & (set(a.context) | set(a.on_demand))
    assert a.measured_render <= render_chars(a) <= HEADROOM_CHARS
    assert a.chars > 0
    assert all(FILE_CHARS[p] > 0 for p in (*a.context, *a.on_demand))
    assert all(PLAN_CHARS[pid] > 0 for pid in a.plan)
    for path in a.on_demand:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path
