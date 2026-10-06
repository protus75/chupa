"""Historical pins for the Phase 3 merge-queue admission (19.L SEEDING TESTS)."""

from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
STEMS = ("merge-queue", "phase3-continue-02")
EDGES = {
    "merge-queue": {"phase3-continue"},
    "phase3-continue-02": {"merge-queue"},
}
TIERS = {
    "merge-queue": ("high", "high"),
    "phase3-continue-02": ("medium", "medium"),
}
FENCE_FLOORS = {
    "merge-queue": {"chupa/mergequeue.py", "chupa/merge.py", "chupa/git.py", "tests/test_mergequeue.py", "tests/test_git.py"},
    "phase3-continue-02": {"tickets", "tests/test_seeded_phase3_02.py"},
}
PLAN = {
    "merge-queue": ("19.L", "19.P3", "9", "10"),
    "phase3-continue-02": ("19.L", "19.P3", "13"),
}
CONTEXT = {
    "merge-queue": ("chupa/merge.py", "chupa/git.py", "chupa/config.py", "tests/test_git.py"),
    "phase3-continue-02": ("tests/test_seeded_phase3_core.py",),
}
ON_DEMAND = {stem: () for stem in STEMS}
FENCED_EXISTING = {
    "merge-queue": ("chupa/merge.py", "chupa/git.py", "tests/test_git.py"),
    "phase3-continue-02": (),
}

# Authoring-time character snapshots. Never recalculate them from live files.
HEADROOM_CHARS = 120_000
RENDER_OVERHEAD = 2_000
IMPLEMENT_SPEC_CHARS = 4_437
TICKET_CHARS = {"merge-queue": 3_918, "phase3-continue-02": 3_420}
PLAN_CHARS = {"19.L": 20_359, "19.P3": 16_045, "9": 19_312, "10": 6_511, "13": 18_033}
FILE_CHARS = {
    "chupa/merge.py": 11_791, "chupa/git.py": 5_232, "chupa/config.py": 10_263,
    "tests/test_git.py": 13_592,
    "tests/test_seeded_phase3_core.py": 3_594,
}


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def _render_chars(stem: str, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + TICKET_CHARS[stem] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[part] for part in PLAN[stem])
            + sum(FILE_CHARS[path] for path in (*CONTEXT[stem], *extra)))


def test_named_admission_and_continuation_only():
    assert len(set(STEMS)) == len(STEMS) == 2
    assert set(EDGES) == set(TIERS) == set(FENCE_FLOORS) == set(PLAN) == set(CONTEXT) == set(STEMS)


@pytest.mark.parametrize("stem", STEMS)
def test_seed_intake_frontmatter_edges_and_registry_floor(stem):
    seed = _ticket(stem)
    assert seed.frontmatter.source == "seed"
    assert seed.frontmatter.state in ("confirmed", "rejected")
    assert (seed.frontmatter.agent_tier, seed.frontmatter.agent_effort) == TIERS[stem]
    assert seed.stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes
    assert set(seed.depends) == EDGES[stem]
    assert FENCE_FLOORS[stem] <= set(seed.scope_fence)
    assert set(PLAN[stem]) <= set(seed.plan_contract)


@pytest.mark.parametrize("stem", STEMS)
def test_authoring_time_context_closure_and_render_feasibility(stem):
    seed = _ticket(stem)
    assert tuple(seed.context) == CONTEXT[stem]
    assert tuple(seed.on_demand) == ON_DEMAND[stem]
    assert set(FENCED_EXISTING[stem]) <= set(CONTEXT[stem]) | set(ON_DEMAND[stem])
    assert not set(CONTEXT[stem]) & set(ON_DEMAND[stem])
    assert _render_chars(stem) <= HEADROOM_CHARS
    for path in ON_DEMAND[stem]:
        assert _render_chars(stem, (path,)) > HEADROOM_CHARS, path
