"""Phase 3's first admission: identity and structure, with authoring-time render snapshots.

The three seeds were already lifted by phase3-core on an earlier attempt (19.L RE-RUN).
Sizes and plan-unit lengths below are permanent fixtures, never measured again by these tests.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ("daemon-scheduler", "seed-successor-proof")
BATCH = (*PAYLOADS, "phase3-continue")
EDGES = {
    "daemon-scheduler": frozenset({"phase3-core"}),
    "seed-successor-proof": frozenset({"phase3-core"}),
    "phase3-continue": frozenset(PAYLOADS),
}
FENCE_FLOORS = {
    "daemon-scheduler": ("chupa/scheduler.py", "chupa/watcher.py", "tests/test_scheduler.py"),
    "seed-successor-proof": ("tests/test_seed_successor.py",),
    "phase3-continue": ("tickets", "tests/test_seeded_phase3_01.py"),
}
# Both construction rows create their entire fence; no closure rule earns an addition.
FENCE_ADDITIONS = {stem: () for stem in BATCH}

# Section 8's single bound applies at max effort too: 400,000 x 0.75.
HEADROOM_CHARS = 300_000
IMPLEMENT_SPEC_CHARS = 4_316
# Conservative allowance for Context headers, separators, and placeholder replacement.
RENDER_OVERHEAD = 2_000
PLAN_CHARS = {
    "19.I": 1_811,
    "19.P3.daemon-scheduler": 5_229,
    "9": 19_656,
    "19.P3.seed-successor-proof": 5_236,
    "19.L": 19_167,
    "19.P3": 16_053,
    "19.P3.merge-queue": 12_747,
    "19.P3.rework-stage": 9_256,
    "13": 18_935,
}
FILE_CHARS = {
    "chupa/drain.py": 21_251,
    "chupa/tickets.py": 28_679,
    "chupa/status.py": 3_606,
    "chupa/seams.py": 4_322,
    "chupa/__main__.py": 5_498,
    "chupa/runner.py": 27_688,
    "chupa/stages.py": 50_092,
    "chupa/merge.py": 11_791,
    "chupa/git.py": 5_232,
    "chupa/llm.py": 2_858,
    "tests/test_seeded_phase2.py": 11_288,
}


@dataclass(frozen=True)
class Authored:
    chars: int
    plan: tuple[str, ...]
    context: tuple[str, ...]
    on_demand: tuple[str, ...] = ()
    fenced_existing: tuple[str, ...] = ()


AUTHORED = {
    "daemon-scheduler": Authored(
        4_624, ("19.I", "19.P3.daemon-scheduler", "9"),
        ("chupa/drain.py", "chupa/tickets.py", "chupa/status.py", "chupa/seams.py"),
    ),
    "seed-successor-proof": Authored(
        4_883, ("19.I", "19.P3.seed-successor-proof"),
        ("chupa/__main__.py", "chupa/runner.py", "chupa/stages.py", "chupa/merge.py",
         "chupa/drain.py", "chupa/tickets.py", "chupa/git.py", "chupa/llm.py", "chupa/seams.py"),
    ),
    "phase3-continue": Authored(
        5_628, ("19.L", "19.I", "19.P3", "19.P3.merge-queue", "19.P3.rework-stage", "13"),
        ("tests/test_seeded_phase2.py",),
    ),
}


def render_chars(a: Authored, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + a.chars + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a.plan)
            + sum(FILE_CHARS[path] for path in (*a.context, *extra)))


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def test_named_stems_cover_exactly_the_core_admission_and_continuation():
    assert BATCH == ("daemon-scheduler", "seed-successor-proof", "phase3-continue")
    assert len(set(BATCH)) == 3
    assert set(EDGES) == set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_authored_frontmatter(stem):
    fm = _ticket(stem).frontmatter
    assert (fm.source, fm.state) == ("seed", "confirmed")
    assert (fm.agent_tier, fm.agent_effort) == ("medium", "medium")


@pytest.mark.parametrize("stem", BATCH)
def test_stuck_budget_fits_the_drain_envelope(stem):
    assert _ticket(stem).stuck_minutes <= load_config(None, cwd=ROOT).drain.max_ticket_minutes


@pytest.mark.parametrize("stem", BATCH)
def test_dependencies_as_authored(stem):
    assert set(_ticket(stem).depends) == EDGES[stem]


@pytest.mark.parametrize("stem", BATCH)
def test_fence_covers_its_floor_and_only_recorded_additions(stem):
    assert set(_ticket(stem).scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])


@pytest.mark.parametrize("stem", PAYLOADS)
def test_implementing_seed_cites_only_its_entry_and_row_contract(stem):
    cited = set(_ticket(stem).plan_contract)
    assert cited == set(AUTHORED[stem].plan)
    assert {"19.I", f"19.P3.{stem}"} <= cited
    assert "19.P3" not in cited


def test_continuation_cites_the_next_admission_and_uses_a_merged_earlier_idiom():
    t = _ticket("phase3-continue")
    assert set(t.plan_contract) == set(AUTHORED[t.stem].plan)
    assert t.context == ("tests/test_seeded_phase2.py",)


@pytest.mark.parametrize("stem", BATCH)
def test_authored_context_partition_and_render_feasibility(stem):
    a = AUTHORED[stem]
    t = _ticket(stem)
    assert t.context == a.context
    assert t.on_demand == a.on_demand
    assert set(a.fenced_existing) <= set(a.context) | set(a.on_demand)
    assert not set(a.context) & set(a.on_demand)
    created = set(FENCE_FLOORS[stem]) - set(a.fenced_existing) - {"tickets"}
    assert not created & (set(a.context) | set(a.on_demand))
    assert render_chars(a) <= HEADROOM_CHARS
    for path in a.on_demand:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path
