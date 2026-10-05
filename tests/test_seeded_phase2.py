"""The seeded Phase 2 queue (CHUPA_PLAN.md 19.P2, section 0 prompts 14-17): named stems only.

Pin grain (19.L SEEDING TESTS): identity and structure -- the named stem set, `depends` edges, frontmatter
values, grammar validity -- never prose. A later `rejected` stamp is lifecycle history, not drift, and no
assertion here reads the live queue. Every size is the AUTHORING-TIME value recorded below, never re-read.
"""

from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent

# Prompts 14-16, in authoring order.
EARLIER = (
    "plan-contract-section-render", "spine-caps", "spine-harvest", "spine-harvest-orphans",
    "spine-diagnosis", "diagnosis-eval-harness", "diagnosis-eval-run",
    "suggestion-box", "second-problems-filing", "reject-queue-verbs", "escalation-ladder",
    "box-start-policy", "box-triage",
)
PROMPT16 = ("suggestion-box", "second-problems-filing", "reject-queue-verbs", "escalation-ladder",
            "box-start-policy", "box-triage")
# Prompt 17's battery groups, in `eval/shakeout/run.py` GROUPS order; the last holds the cumulative report.
BATTERY = ("shakeout-stages", "shakeout-driver", "shakeout-runner", "shakeout-drain", "shakeout-recovery",
           "shakeout-merge", "shakeout-providers")
# Prompt 17's stated deliverable order: Author, requisition_review x3, the auditor, the report lane, the
# battery groups, then LAST the exit.
ORDER = ("author-stage", "requisition-review", "requisition-author-path", "requisition-seed-path",
         "invariant-auditor", "shakeout-report-lane", *BATTERY, "phase2-exit")

# This batch's `## Depends on`, as authored.
EDGES: dict[str, frozenset[str]] = {
    "author-stage": frozenset({"box-triage", "box-start-policy"}),
    "requisition-review": frozenset({"author-stage"}),
    "requisition-author-path": frozenset({"requisition-review", "author-stage"}),
    "requisition-seed-path": frozenset({"requisition-author-path"}),
    "invariant-auditor": frozenset({"requisition-seed-path"}),
    "verification-base-attribution": frozenset({"box-triage"}),
    "shakeout-report-lane": frozenset({"invariant-auditor"}),
    "shakeout-stages": frozenset({"shakeout-report-lane", "verification-base-attribution"}),
    "shakeout-driver": frozenset({"shakeout-stages"}),
    "shakeout-runner": frozenset({"shakeout-driver"}),
    "shakeout-drain": frozenset({"shakeout-runner"}),
    "shakeout-recovery": frozenset({"shakeout-drain"}),
    "shakeout-merge": frozenset({"shakeout-recovery"}),
    "shakeout-providers": frozenset({"shakeout-merge"}),
    "phase2-exit": frozenset({"shakeout-providers", "diagnosis-eval-run"}),
}
BATCH = tuple(EDGES)
PHASE2 = EARLIER + BATCH

# Starting capability. The ladder has merged before every batch stem dispatches, so the pre-ladder HIGH
# rule no longer binds; requisition-seed-path is known-deep (two seams) and phase2-exit plan-named
# known-hard (19.L), each citing its evidence in-ticket.
TIERS: dict[str, tuple[str, str]] = {stem: ("medium", "medium") for stem in BATCH}
TIERS["requisition-seed-path"] = ("high", "high")
TIERS["phase2-exit"] = ("high", "high")
KNOWN_HARD = "phase2-exit"

# --- authoring-time material (permanent fixture; never re-read from live files) -------------------

HEADROOM_CHARS = 120_000  # REQ_RENDER_HEADROOM 0.75 x RENDER_BOUND_CHARS["max"] 160,000 (section 8)
RENDER_OVERHEAD = 2_000  # data-block delimiters and Context path headers around the embedded material
IMPLEMENT_SPEC_CHARS = 3_924
PLAN_CHARS = {"19.L": 20_359, "19.P2": 9_470, "19.P3": 16_045, "5": 8_816, "6": 35_394, "7": 7_536,
              "8": 8_326, "9": 19_312, "10": 6_511, "11": 24_861, "12": 19_974, "13": 18_033, "15": 16_970,
              "18": 13_277}
FILE_CHARS = {
    "chupa/artifacts.py": 3_298, "chupa/driver.py": 9_611, "chupa/drain.py": 18_357, "chupa/gates.py": 4_912,
    "chupa/git.py": 4_429, "chupa/journal.py": 8_656, "chupa/llmeffect.py": 1_364, "chupa/merge.py": 8_160,
    "chupa/providers.py": 12_673, "chupa/reconcile.py": 2_087, "chupa/runner.py": 6_382,
    "chupa/stages.py": 28_242, "tests/test_drain.py": 14_572, "tests/test_drain_reentry.py": 3_937,
    "tests/test_driver.py": 13_601, "tests/test_eval_harness.py": 8_071, "tests/test_git.py": 10_815,
    "tests/test_merge.py": 9_344, "tests/test_reconcile.py": 4_341, "tests/test_seeded_phase2.py": 11_288,
    "tests/test_stages.py": 12_783,
}


class Authored:
    def __init__(self, chars: int, plan: tuple[str, ...], context: tuple[str, ...], on_demand: tuple[str, ...],
                 fenced_existing: tuple[str, ...]) -> None:
        self.chars, self.plan, self.context, self.on_demand = chars, plan, context, on_demand
        self.fenced_existing = fenced_existing


AUTHORED: dict[str, Authored] = {
    "author-stage": Authored(9_224, ("19.L", "19.P2", "8", "12", "13"),
                             ("chupa/git.py", "tests/test_git.py", "tests/test_eval_harness.py"), (),
                             ("chupa/git.py", "tests/test_git.py", "tests/test_eval_harness.py")),
    "requisition-review": Authored(7_571, ("19.L", "19.P2", "7", "8", "9", "13"),
                                   ("chupa/gates.py", "chupa/driver.py", "chupa/llmeffect.py"), ("chupa/stages.py",),
                                   ("chupa/stages.py", "chupa/driver.py")),
    "requisition-author-path": Authored(4_735, ("19.L", "19.P2", "7", "11", "12"),
                                        ("chupa/driver.py", "tests/test_driver.py"), (),
                                        ("chupa/driver.py", "tests/test_driver.py")),
    "requisition-seed-path": Authored(6_484, ("19.L", "19.P2", "7", "9", "10"),
                                      ("chupa/merge.py", "tests/test_merge.py", "tests/test_stages.py"),
                                      ("chupa/stages.py",),
                                      ("chupa/stages.py", "tests/test_stages.py", "chupa/merge.py", "tests/test_merge.py")),
    "invariant-auditor": Authored(4_247, ("19.L", "19.P2", "6", "15"), ("chupa/journal.py", "chupa/artifacts.py"),
                                  (), ()),
    "verification-base-attribution": Authored(
        5_272, ("19.L", "19.P2", "7", "10"),
        ("chupa/git.py", "tests/test_git.py", "tests/test_stages.py", "tests/test_merge.py",
         "tests/test_drain_reentry.py"), ("chupa/stages.py",),
        ("chupa/stages.py", "tests/test_stages.py", "chupa/git.py", "tests/test_git.py", "tests/test_merge.py",
         "tests/test_drain_reentry.py")),
    "shakeout-report-lane": Authored(8_079, ("19.L", "19.P2", "10", "15"),
                                     ("chupa/artifacts.py", "chupa/runner.py", "tests/test_stages.py",
                                      "tests/test_drain.py"), ("chupa/stages.py",),
                                     ("chupa/artifacts.py", "chupa/stages.py", "tests/test_stages.py")),
    "shakeout-stages": Authored(4_557, ("19.L", "19.P2", "7", "11"), ("chupa/stages.py",), (), ("chupa/stages.py",)),
    "shakeout-driver": Authored(3_437, ("19.L", "19.P2", "5", "11"), ("chupa/driver.py",), (), ("chupa/driver.py",)),
    "shakeout-runner": Authored(3_583, ("19.L", "19.P2", "11"), ("chupa/runner.py",), (), ("chupa/runner.py",)),
    "shakeout-drain": Authored(3_425, ("19.L", "19.P2", "18"), ("chupa/drain.py", "tests/test_drain.py"), (),
                               ("chupa/drain.py",)),
    "shakeout-recovery": Authored(3_171, ("19.L", "19.P2", "11"), ("chupa/reconcile.py", "tests/test_reconcile.py"),
                                  (), ("chupa/reconcile.py",)),
    "shakeout-merge": Authored(3_039, ("19.L", "19.P2", "9", "10"), ("chupa/merge.py", "tests/test_merge.py"), (),
                               ("chupa/merge.py",)),
    "shakeout-providers": Authored(5_186, ("19.L", "19.P2", "6"), ("chupa/providers.py", "chupa/driver.py"), (),
                                   ("chupa/providers.py", "chupa/driver.py")),
    # The whole-plane `tickets` fence is a directory prefix (section 9's seeding exception), never Context.
    "phase2-exit": Authored(6_865, ("19.L", "19.P2", "19.P3", "13"),
                            ("chupa/artifacts.py", "tests/test_seeded_phase2.py"), (), ()),
}


def render_chars(a: Authored, extra: tuple[str, ...] = ()) -> int:
    """The base Implement render at `max` effort: spec + ticket + Plan contract + embedded Context."""
    return (IMPLEMENT_SPEC_CHARS + a.chars + RENDER_OVERHEAD + sum(PLAN_CHARS[p] for p in a.plan)
            + sum(FILE_CHARS[p] for p in (*a.context, *extra)))


# --- live structure ------------------------------------------------------------------------------


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT)


def _closure(stem: str) -> set[str]:
    seen: set[str] = set()
    stack = [stem]
    while stack:
        for dep in _ticket(stack.pop()).depends:
            if dep not in seen:
                seen.add(dep)
                stack.append(dep)
    return seen


def test_named_stems_are_distinct_and_cover_the_batch():
    assert len(set(PHASE2)) == len(PHASE2) == 28
    assert set(ORDER) | {"verification-base-attribution"} == set(BATCH)
    assert set(AUTHORED) == set(BATCH)


@pytest.mark.parametrize("stem", PHASE2)
def test_seed_passes_intake_lint_as_a_seed(stem):
    fm = _ticket(stem).frontmatter
    assert fm.source == "seed"
    assert fm.state in ("confirmed", "rejected")  # authored confirmed; a later reject kill is history


@pytest.mark.parametrize("stem", PHASE2)
def test_stuck_budget_fits_the_drain_envelope(stem):
    ceiling = load_config(None, cwd=ROOT).drain.max_ticket_minutes
    assert _ticket(stem).stuck_minutes <= ceiling


@pytest.mark.parametrize("stem", BATCH)
def test_batch_edges_as_authored(stem):
    assert set(_ticket(stem).depends) == EDGES[stem]


def test_edges_realize_the_stated_deliverable_order():
    for i, stem in enumerate(ORDER):
        assert set(ORDER[:i]) <= _closure(stem), stem
    assert set(PROMPT16) <= _closure("author-stage")
    assert "verification-base-attribution" in _closure(BATTERY[0])
    assert set(PHASE2) - {"phase2-exit"} <= _closure("phase2-exit")


@pytest.mark.parametrize("stem", BATCH)
def test_starting_capability_and_plan_units(stem):
    t = _ticket(stem)
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == TIERS[stem]
    assert {"19.L", "19.P2"} <= set(t.plan_contract)


def test_known_hard_exit_cites_its_evidence():
    t = _ticket(KNOWN_HARD)
    assert (t.frontmatter.agent_tier, t.frontmatter.agent_effort) == ("high", "high")
    assert "19.L" in t.plan_contract  # the unit naming the phase-exit seed known-hard


def test_exit_fence_is_the_seeding_exception():
    assert "tickets" in _ticket(KNOWN_HARD).scope_fence


@pytest.mark.parametrize("stem", BATCH)
def test_authored_context_closure_and_render_feasibility(stem):
    a = AUTHORED[stem]
    assert set(a.fenced_existing) <= set(a.context) | set(a.on_demand)
    assert not set(a.context) & set(a.on_demand)
    assert render_chars(a) <= HEADROOM_CHARS
    for path in a.on_demand:  # on-demand only where embedding would breach the headroom
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path
