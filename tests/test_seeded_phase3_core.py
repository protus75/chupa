"""Historical pins for the three Phase 3 core seeds (19.L SEEDING TESTS)."""

from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
STEMS = ("daemon-scheduler", "seed-successor-proof", "phase3-continue")
EDGES = {
    "daemon-scheduler": {"phase2-exit"},
    "seed-successor-proof": {"phase2-exit"},
    "phase3-continue": {"daemon-scheduler", "seed-successor-proof"},
}
FENCE_FLOORS = {
    "daemon-scheduler": {"chupa/scheduler.py", "chupa/watcher.py", "tests/test_scheduler.py"},
    "seed-successor-proof": {"tests/test_seed_successor.py"},
    "phase3-continue": {"tickets", "tests/test_seeded_phase3_01.py"},
}
PLAN = {
    "daemon-scheduler": ("19.L", "19.P3", "9"),
    "seed-successor-proof": ("19.L", "19.P3"),
    "phase3-continue": ("19.L", "19.P3", "13"),
}

# These paths existed before the seeds were lifted. All three fences create only new paths.
CONTEXT = {
    "daemon-scheduler": ("chupa/__main__.py",),
    "seed-successor-proof": ("tests/test_seed_path.py", "tests/test_drain.py", "chupa/drain.py"),
    "phase3-continue": ("tests/test_seeded_phase2.py",),
}
ON_DEMAND = {stem: () for stem in STEMS}
FENCED_EXISTING = {stem: () for stem in STEMS}

# Authoring-time character snapshots. Never recalculate them from live files.
HEADROOM_CHARS = 120_000  # section 8: 0.75 * max-effort 160,000-character bound
RENDER_OVERHEAD = 2_000
IMPLEMENT_SPEC_CHARS = 4_437
TICKET_CHARS = {"daemon-scheduler": 2_463, "seed-successor-proof": 1_935,
                "phase3-continue": 3_716}  # main's corrected, committed blob
PLAN_CHARS = {"19.L": 20_359, "19.P3": 16_045, "9": 19_312, "13": 18_033}
FILE_CHARS = {"chupa/__main__.py": 5_498, "tests/test_seed_path.py": 10_960,
              "tests/test_drain.py": 15_276, "chupa/drain.py": 19_801,
              "tests/test_seeded_phase2.py": 11_288}


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def _render_chars(stem: str, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + TICKET_CHARS[stem] + RENDER_OVERHEAD
            + sum(PLAN_CHARS[part] for part in PLAN[stem])
            + sum(FILE_CHARS[path] for path in (*CONTEXT[stem], *extra)))


def test_named_core_admission_and_continuation_only():
    assert len(set(STEMS)) == len(STEMS) == 3
    assert set(EDGES) == set(FENCE_FLOORS) == set(PLAN) == set(CONTEXT) == set(STEMS)


@pytest.mark.parametrize("stem", STEMS)
def test_seed_intake_frontmatter_edges_and_fence(stem):
    seed = _ticket(stem)
    assert seed.frontmatter.source == "seed"
    assert seed.frontmatter.state in ("confirmed", "rejected")
    assert (seed.frontmatter.agent_tier, seed.frontmatter.agent_effort) == ("medium", "medium")
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
