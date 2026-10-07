"""Admission 03: exactly two seeds, pinned at authoring rather than live render sizes.

Later rejected stamps are lifecycle history. Sizes and plan lengths below are
permanent fixtures measured before this batch's Check, never remeasured here.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
BATCH = ("thresh-runtime", "phase3-continue-04")
EDGES = {
    "thresh-runtime": frozenset({"phase3-continue-03"}),
    "phase3-continue-04": frozenset({"thresh-runtime"}),
}
# Parsed directly from admission[3]'s deep: true row at authoring. Provider,
# journal and Effects boundaries earn high/high; the continuation is medium.
START = {"thresh-runtime": ("high", "high"), "phase3-continue-04": ("medium", "medium")}
AUTHORED_STATE = {stem: "confirmed" for stem in BATCH}
FENCE_FLOORS = {
    "thresh-runtime": ("chupa/thresh.py", "chupa/providers.py", "chupa/config.py",
                       "tests/test_thresh.py", "tests/test_providers.py"),
    "phase3-continue-04": ("tickets", "tests/test_seeded_phase3_04.py"),
}
# 19.L rules 2-5 earn no additions. Greps across chupa/, eval/ and tests/ for
# concurrency, CircuitBreaker, cooldown_minutes, Served, ProviderCallError,
# AUTH_MARKERS, LOGIN_ROAD, resolve, the new signals and public allowlists found
# no assertion flipped or caller/signature changed by dormant construction.
# Existing tests pin concurrency > 0, breaker defaults 3/10, first-candidate
# routing, auth errors and abort; all remain valid. No provider/config public
# operation allowlist requires migration. thresh.py owns its new operations.
FENCE_ADDITIONS = {stem: {} for stem in BATCH}

# Section 8's bound applies at maximum effort as well: 400,000 x 0.75.
HEADROOM_CHARS = 300_000
IMPLEMENT_SPEC_CHARS = 4_316
RENDER_OVERHEAD = 2_000  # conservative headers, separators and placeholders
PLAN_CHARS = {
    "19.I": 1_811, "19.P3.thresh-runtime": 12_153, "6": 36_580,
    "19.L": 19_167, "19.P3": 16_053,
    "19.P3.dispatch-admission-boundary": 4_771,
    "19.P3.dispatch-config-snapshot": 5_953,
    "19.P3.scheduler-activation": 7_232,
    "19.P3.merge-queue-activation": 5_955,
    "19.P3.rework-activation": 11_211, "13": 19_104,
}
FILE_CHARS = {
    "chupa/providers.py": 16_329, "chupa/config.py": 10_776,
    "tests/test_providers.py": 17_097, "chupa/effects.py": 3_229,
    "chupa/journal.py": 8_656, "chupa/llm.py": 2_858,
    "chupa/seams.py": 4_322, "chupa/redact.py": 1_474,
    "tests/test_seeded_phase3_core.py": 5_425,
}
# Authoring checked every embedded file for the engine data delimiter. The
# immutable inventory avoids inspecting later versions for historical closure.
DELIMITER_FREE_AT_AUTHORING = frozenset(FILE_CHARS)


@dataclass(frozen=True)
class Authored:
    chars: int
    plan: tuple[str, ...]
    context: tuple[str, ...]
    measured_render: int
    on_demand: tuple[str, ...] = ()
    fenced_existing: tuple[str, ...] = ()


AUTHORED = {
    "thresh-runtime": Authored(
        15_713, ("19.I", "19.P3.thresh-runtime", "6"),
        ("chupa/providers.py", "chupa/config.py", "tests/test_providers.py",
         "chupa/effects.py", "chupa/journal.py", "chupa/llm.py",
         "chupa/seams.py", "chupa/redact.py"), 135_442,
        fenced_existing=("chupa/providers.py", "chupa/config.py", "tests/test_providers.py"),
    ),
    "phase3-continue-04": Authored(
        9_534, ("19.L", "19.I", "19.P3", "19.P3.dispatch-admission-boundary",
                "19.P3.dispatch-config-snapshot", "19.P3.scheduler-activation",
                "19.P3.merge-queue-activation", "19.P3.rework-activation", "13"),
        ("tests/test_seeded_phase3_core.py",), 110_514,
    ),
}


def render_chars(a: Authored, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + a.chars + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a.plan)
            + sum(FILE_CHARS[path] for path in (*a.context, *extra)))


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, siblings=BATCH)


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("thresh-runtime", "phase3-continue-04")
    assert len(set(BATCH)) == 2
    assert set(EDGES) == set(START) == set(AUTHORED_STATE) == set(BATCH)
    assert set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)
    assert len(BATCH) <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission


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
    t = _ticket("thresh-runtime")
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("high", "high")
    assert t.plan_contract == AUTHORED[t.stem].plan
    assert t.plan_contract == ("19.I", "19.P3.thresh-runtime", "6")
    assert "19.P3" not in t.plan_contract


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket("phase3-continue-04")
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
    assert set(a.context) <= DELIMITER_FREE_AT_AUTHORING
    assert 0 < a.measured_render <= render_chars(a) <= HEADROOM_CHARS
    assert a.chars > 0
    assert all(FILE_CHARS[p] > 0 for p in (*a.context, *a.on_demand))
    assert all(PLAN_CHARS[pid] > 0 for pid in a.plan)
    for path in a.on_demand:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


def test_thresh_runs_preservation_suites_without_fencing_or_embedding_them():
    t = _ticket("thresh-runtime")
    assert t.verification == (
        ("uv", "run", "pytest", "tests/test_thresh.py", "tests/test_providers.py",
         "tests/test_config.py", "tests/test_driver.py"),
        ("uv", "run", "pytest", "-q"),
    )
    preservation = {"tests/test_config.py", "tests/test_driver.py"}
    assert not preservation & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
