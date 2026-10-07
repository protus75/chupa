"""Admission 04: dispatch construction and one successor, pinned at authoring.

Confirmed seed birth persists even if a later rejected stamp records lifecycle
history. Render sizes below are permanent snapshots, never live measurements.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ("dispatch-admission-boundary", "dispatch-config-snapshot")
BATCH = (*PAYLOADS, "phase3-continue-05")
EDGES = {
    "dispatch-admission-boundary": frozenset({"phase3-continue-04"}),
    "dispatch-config-snapshot": frozenset({"phase3-continue-04", "dispatch-admission-boundary"}),
    "phase3-continue-05": frozenset(PAYLOADS),
}
START = {stem: ("medium", "medium") for stem in BATCH}
AUTHORED_STATE = {stem: "confirmed" for stem in BATCH}
FENCE_FLOORS = {
    "dispatch-admission-boundary": ("chupa/daemon.py", "tests/test_daemon_admission.py"),
    "dispatch-config-snapshot": ("chupa/daemon.py", "chupa/config.py", "tests/test_daemon_config.py"),
    "phase3-continue-05": ("tickets", "tests/test_seeded_phase3_05.py"),
}
# Authoring parsed admission[4] directly from the plan. 19.L rules 2-5 earn
# no additions: rg across chupa/, eval/ and tests/ for DaemonAdmission,
# snapshot_config, snapshot_dispatch, Dispatch, model_dump, __all__, public
# allowlists, daemon import absence and not hasattr found no new-seam caller,
# config-operation allowlist or old assertion that dormant construction flips.
# Existing mutable Config behavior, max_unmerged=2, schema=1 and API/null
# refusals stay unchanged. No public signature or constructor arity changes.
# Activation (a later batch) earns the negative-fixture migrations, not these
# constructions. Each future earned path must have a reason in this mapping.
FENCE_ADDITIONS = {stem: {} for stem in BATCH}

# Verified through git.py at authoring: main and HEAD share this idiom blob.
MERGED_IDIOM = "tests/test_seeded_phase3_core.py"
MERGED_IDIOM_BLOB = "2feb2512789adbf84d57e9153d77d6a7a06edb8a"
AUTHORING_HEAD = "b28f4b5510ed8a6685dbf6e8dc7a9479ee5bf3ab"
# Section 8's bound applies at maximum effort too: 400,000 x 0.75.
HEADROOM_CHARS = 300_000
IMPLEMENT_SPEC_CHARS = 4_316
RENDER_OVERHEAD = 2_000  # conservative headers, separators and placeholders
PLAN_CHARS = {
    "19.I": 1_811, "19.P3.dispatch-admission-boundary": 4_771, "9": 19_656,
    "19.P3.dispatch-config-snapshot": 5_953, "15": 17_090,
    "19.L": 19_167, "19.P3": 16_053, "13": 19_104,
    "19.P3.scheduler-activation": 7_232,
    "19.P3.merge-queue-activation": 5_955, "19.P3.rework-activation": 11_211,
}
FILE_CHARS = {
    "chupa/config.py": 10_776, "chupa/runner.py": 27_688,
    "chupa/__main__.py": 5_498, "chupa/seams.py": 4_322,
    "tests/test_seeded_phase3_core.py": 5_425,
}
DELIMITER_FREE_AT_AUTHORING = frozenset(FILE_CHARS)


@dataclass(frozen=True)
class Authored:
    chars: int
    plan: tuple[str, ...]
    context: tuple[str, ...]
    measured_render: int
    on_demand: tuple[str, ...] = ()
    fenced_existing: tuple[str, ...] = ()
    sibling_created: tuple[str, ...] = ()


AUTHORED = {
    "dispatch-admission-boundary": Authored(
        6_355, ("19.I", "19.P3.dispatch-admission-boundary", "9"),
        ("chupa/runner.py", "chupa/__main__.py", "chupa/seams.py"), 74_427,
    ),
    "dispatch-config-snapshot": Authored(
        7_986, ("19.I", "19.P3.dispatch-config-snapshot", "15"),
        ("chupa/config.py", "chupa/runner.py", "chupa/__main__.py", "chupa/seams.py"), 85_472,
        fenced_existing=("chupa/config.py",), sibling_created=("chupa/daemon.py",),
    ),
    "phase3-continue-05": Authored(
        10_872, ("19.L", "19.I", "19.P3", "13", "19.P3.scheduler-activation",
                 "19.P3.merge-queue-activation", "19.P3.rework-activation"),
        (MERGED_IDIOM,), 101_128,
    ),
}
OBLIGATIONS = {
    "dispatch-admission-boundary": (
        "test_admission_is_idle_until_dispatch",
        "test_dispatch_owns_task_and_returns_terminal",
        "test_concurrent_dispatch_is_single_flight",
        "test_dispatch_exception_unwinds_and_releases_slot",
        "test_cancelled_waiter_never_dispatches",
        "test_active_cancellation_awaits_cleanup_before_release",
        "test_daemon_admission_is_dormant",
    ),
    "dispatch-config-snapshot": (
        "test_snapshot_preserves_all_validated_config_values",
        "test_snapshot_is_recursively_immutable_and_detached",
        "test_dispatch_captures_once_and_keeps_snapshot_until_completion",
        "test_next_dispatch_observes_valid_config_edits",
        "test_waiting_dispatch_captures_after_admission",
        "test_invalid_reload_never_binds_or_uses_stale_config",
        "test_snapshot_dispatch_unwinds_failures_and_cancellation",
        "test_config_snapshot_is_dormant",
    ),
}
PRESERVATION = {
    "dispatch-admission-boundary": (
        "tests/test_scheduler.py", "tests/test_cli.py", "tests/test_drain.py",
    ),
    "dispatch-config-snapshot": (
        "tests/test_daemon_admission.py", "tests/test_config.py", "tests/test_cli.py", "tests/test_drain.py",
    ),
}


def render_chars(a: Authored, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + a.chars + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a.plan)
            + sum(FILE_CHARS[path] for path in (*a.context, *extra)))


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, siblings=BATCH)


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("dispatch-admission-boundary", "dispatch-config-snapshot", "phase3-continue-05")
    assert len(set(BATCH)) == 3
    assert set(EDGES) == set(START) == set(AUTHORED_STATE) == set(BATCH)
    assert set(FENCE_FLOORS) == set(FENCE_ADDITIONS) == set(AUTHORED) == set(BATCH)
    assert set(OBLIGATIONS) == set(PRESERVATION) == set(PAYLOADS)
    assert len(BATCH) <= load_config(None, cwd=ROOT).seeding.max_seeds_per_admission


@pytest.mark.parametrize("stem", BATCH)
def test_seed_passes_intake_lint_with_confirmed_seed_birth(stem):
    fm = _ticket(stem).frontmatter
    assert AUTHORED_STATE[stem] == "confirmed"
    assert fm.source == "seed"
    assert fm.state in (AUTHORED_STATE[stem], "rejected")
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
    assert set(_ticket(stem).scope_fence) == set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])
    assert all(FENCE_ADDITIONS[stem].values())


@pytest.mark.parametrize("stem", PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    assert t.plan_contract == AUTHORED[stem].plan
    row_cite = "9" if stem == "dispatch-admission-boundary" else "15"
    assert t.plan_contract == ("19.I", f"19.P3.{stem}", row_cite)
    assert "19.P3" not in t.plan_contract
    assert all(name in t.sections["Scope in / Scope out"] for name in OBLIGATIONS[stem])


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket("phase3-continue-05")
    assert t.plan_contract == AUTHORED[t.stem].plan
    assert set(t.plan_contract) == {
        "19.L", "19.I", "19.P3", "13", "19.P3.scheduler-activation",
        "19.P3.merge-queue-activation", "19.P3.rework-activation",
    }
    assert t.context == (MERGED_IDIOM,)
    assert t.scope_fence == ("tickets", "tests/test_seeded_phase3_05.py")
    assert len(MERGED_IDIOM_BLOB) == len(AUTHORING_HEAD) == 40
    assert "admissions[5:]" in t.sections["Goal / Why"]
    scope = t.sections["Scope in / Scope out"]
    assert "phase3-continue-06" in scope and "admissions[6:]" in scope
    assert "tests/test_daemon_config.py" in scope
    assert "Rework seed explicitly depends on its merge-queue-activation sibling" in scope


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a = AUTHORED[stem]
    t = _ticket(stem)
    assert t.context == a.context
    assert t.on_demand == a.on_demand
    assert set(a.fenced_existing) <= set(a.context) | set(a.on_demand)
    assert not set(a.context) & set(a.on_demand)
    future = (set(FENCE_FLOORS[stem]) | set(FENCE_ADDITIONS[stem])) - set(a.fenced_existing) - {"tickets"}
    assert not future & (set(a.context) | set(a.on_demand))
    assert set(a.sibling_created) <= future
    assert not any(p.startswith("specs/") for p in (*a.context, *a.on_demand))
    assert set(a.context) <= DELIMITER_FREE_AT_AUTHORING
    assert 0 < a.measured_render <= render_chars(a) <= HEADROOM_CHARS
    assert a.chars > 0
    assert all(FILE_CHARS[p] > 0 for p in (*a.context, *a.on_demand))
    assert all(PLAN_CHARS[pid] > 0 for pid in a.plan)
    for path in a.on_demand:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path
    if stem == "dispatch-config-snapshot":
        assert a.fenced_existing == ("chupa/config.py",)
        assert a.sibling_created == ("chupa/daemon.py",)
        assert "Read chupa/daemon.py from the worktree after dispatch-admission-boundary merges" in t.sections["Scope in / Scope out"]


@pytest.mark.parametrize("stem", PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    own_test = "tests/test_daemon_admission.py" if stem == "dispatch-admission-boundary" else "tests/test_daemon_config.py"
    assert t.verification == (
        ("uv", "run", "pytest", own_test, *PRESERVATION[stem]),
        ("uv", "run", "pytest", "-q"),
    )
    assert not set(PRESERVATION[stem]) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
