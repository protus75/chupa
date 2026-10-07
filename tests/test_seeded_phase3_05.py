"""Admission 05: production-core activation and its successor.

Authoring parsed the registry directly and gap-checked/resolved admissions 5-8
before writing. Sizes here are permanent authoring fixtures, never live reads.
Confirmed birth survives a later rejected stamp as lifecycle history.
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

from chupa.config import load_config
from chupa.tickets import ticket_path, validate_ticket

ROOT = Path(__file__).resolve().parent.parent
PAYLOADS = ("scheduler-activation",)
BATCH = (*PAYLOADS, "phase3-continue-06")
EDGES = {
    "scheduler-activation": frozenset({"phase3-continue-05"}),
    "phase3-continue-06": frozenset(PAYLOADS),
}
START = {"scheduler-activation": ("high", "high"), "phase3-continue-06": ("medium", "medium")}
AUTHORED_STATE = {stem: "confirmed" for stem in BATCH}
# rg across chupa/, eval/ and tests/ covered Scheduler, Watcher, DaemonAdmission,
# snapshot_dispatch, pipeline/bind/Checkout, StageContext, Driver.from_config,
# ProviderLLM/resolve/Served/child_env, Redactor.from_config, merge_severity,
# cap/rung reads, both import idioms, not hasattr and public-operation allowlists.
# No component constructor arity or bootstrap Pipeline contract changes. Mutable
# Config schema/max_unmerged=2 stays unchanged; config tests are preservation.
# Other callers accept the widened read-only types unchanged; this flip earns no
# test migration beyond the three predecessor negatives. Queue/Rework absence
# assertions remain for their own rows. No additional forced path was found.
FENCE_FLOORS = {
    "scheduler-activation": (
        "chupa/daemon.py",
        "chupa/scheduler.py",
        "chupa/watcher.py",
        "chupa/__main__.py",
        "tests/test_scheduler.py",
        "tests/test_daemon_admission.py",
        "tests/test_daemon_composition.py",
    ),
    "phase3-continue-06": ("tickets", "tests/test_seeded_phase3_06.py"),
}
FENCE_ADDITIONS = {
    "scheduler-activation": {
        "tests/test_daemon_config.py": "ACTIVATION/CONTRADICTED TESTS: test_config_snapshot_is_dormant asserts daemon import absence; migrate only that closure assertion.",
        "chupa/runner.py": "CALLER CLOSURE: root factors pipeline preparation and passes the admitted snapshot through Checkout and bind.",
        "chupa/stages.py": "CALLER CLOSURE: StageContext consumes the dispatch-local ConfigSnapshot.",
        "chupa/driver.py": "CALLER CLOSURE: Driver.from_config accepts the same snapshot before constructing its writers.",
        "chupa/providers.py": "CALLER CLOSURE: ProviderLLM, resolve, Served, adapters and child_env consume immutable provider records, mappings and tuples.",
        "chupa/redact.py": "CALLER CLOSURE: Driver/provider construction calls Redactor.from_config with the snapshot.",
        "chupa/gates.py": "CALLER CLOSURE: Driver.from_config and check consume snapshot merge severity through merge_severity.",
        "chupa/caps.py": "CALLER CLOSURE: cap and rung reads use snapshot caps/provider records without mutation.",
    },
    "phase3-continue-06": {},
}

# git.py verified HEAD and main share this already merged idiom blob.
MERGED_IDIOM = "tests/test_seeded_phase3_core.py"
MERGED_IDIOM_BLOB = "2feb2512789adbf84d57e9153d77d6a7a06edb8a"
AUTHORING_HEAD = "e1db8ab86a828135f6f54663133bcba8e7adc058"
HEADROOM_CHARS = 300_000  # 400,000 x 0.75 at every effort, including max
IMPLEMENT_SPEC_CHARS = 4_316
RENDER_OVERHEAD = 2_000  # conservative headers, separators and placeholders
PLAN_CHARS = {
    "19.I": 1811,
    "19.P3.scheduler-activation": 11920,
    "19.L": 19167,
    "19.P3": 16053,
    "13": 19104,
    "19.P3.merge-queue-activation": 5955,
    "19.P3.rework-activation": 11211,
    "19.P3.background-consumers": 5751,
    "19.P3.control-inbox": 8797,
    "19.P3.dispatch-pause-boundary": 6074,
    "19.P3.pause-resume-activation": 7703,
    "20": 4367,
}
FILE_CHARS = {
    "chupa/daemon.py": 1849,
    "chupa/scheduler.py": 2261,
    "chupa/watcher.py": 2807,
    "chupa/__main__.py": 5498,
    "tests/test_scheduler.py": 15180,
    "tests/test_daemon_admission.py": 9262,
    "tests/test_daemon_config.py": 15735,
    "chupa/runner.py": 27688,
    "chupa/stages.py": 50649,
    "chupa/driver.py": 11549,
    "chupa/providers.py": 18378,
    "chupa/redact.py": 1474,
    "chupa/gates.py": 4912,
    "chupa/caps.py": 3551,
    "tests/test_seeded_phase3_core.py": 5425,
}
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
    "scheduler-activation": Authored(
        15962,
        ("19.I", "19.P3.scheduler-activation"),
        (
            "chupa/daemon.py",
            "chupa/scheduler.py",
            "chupa/watcher.py",
            "chupa/__main__.py",
            "tests/test_scheduler.py",
            "tests/test_daemon_admission.py",
            "tests/test_daemon_config.py",
            "chupa/runner.py",
            "chupa/stages.py",
            "chupa/driver.py",
            "chupa/providers.py",
            "chupa/redact.py",
            "chupa/gates.py",
            "chupa/caps.py",
        ),
        (
            "chupa/daemon.py",
            "chupa/scheduler.py",
            "chupa/watcher.py",
            "chupa/__main__.py",
            "tests/test_scheduler.py",
            "tests/test_daemon_admission.py",
            "tests/test_daemon_config.py",
            "chupa/runner.py",
            "chupa/stages.py",
            "chupa/driver.py",
            "chupa/providers.py",
            "chupa/redact.py",
            "chupa/gates.py",
            "chupa/caps.py",
        ),
        205094,
    ),
    "phase3-continue-06": Authored(
        10878,
        (
            "19.L",
            "19.I",
            "19.P3",
            "13",
            "19.P3.merge-queue-activation",
            "19.P3.rework-activation",
            "19.P3.background-consumers",
            "19.P3.control-inbox",
            "19.P3.dispatch-pause-boundary",
            "19.P3.pause-resume-activation",
            "20",
        ),
        ("tests/test_seeded_phase3_core.py",),
        (),
        126594,
    ),
}

OBLIGATIONS = (
    "test_production_core_uses_real_snapshot_pipeline",
    "test_production_core_awaits_preflight_inside_admission",
    "test_production_core_unwinds_preflight_refusal_and_cancellation",
    "test_production_root_builds_daemon_core_without_running_work",
    "test_production_core_dispatches_through_admission_and_snapshot",
    "test_production_core_reprioritizes_without_preemption",
    "test_production_core_preserves_last_good_and_removes_tickets",
    "test_production_core_preserves_eligibility_order_and_backpressure",
    "test_production_core_reloads_config_only_after_admission",
    "test_production_core_unwinds_errors_and_cancellation",
    "test_daemon_core_is_reachable_from_cli",
)
TRANSITION_FILES = {
    "test_scheduler_and_watcher_are_dormant": "tests/test_scheduler.py",
    "test_daemon_admission_is_dormant": "tests/test_daemon_admission.py",
    "test_config_snapshot_is_dormant": "tests/test_daemon_config.py",
}
PRESERVATION = (
    "tests/test_config.py",
    "tests/test_cli.py",
    "tests/test_drain.py",
    "tests/test_providers.py",
    "tests/test_driver.py",
    "tests/test_stages.py",
    "tests/test_gates.py",
    "tests/test_caps.py",
)
ACTIVATION_TESTS = (
    "tests/test_daemon_composition.py",
    "tests/test_scheduler.py",
    "tests/test_daemon_admission.py",
    "tests/test_daemon_config.py",
)


def render_chars(a: Authored, extra: tuple[str, ...] = ()) -> int:
    return (IMPLEMENT_SPEC_CHARS + a.chars + RENDER_OVERHEAD
            + sum(PLAN_CHARS[pid] for pid in a.plan)
            + sum(FILE_CHARS[path] for path in (*a.context, *extra)))


def _ticket(stem: str):
    return validate_ticket(stem, (ROOT / ticket_path(stem)).read_text(), ROOT, siblings=BATCH)


def test_named_stems_cover_exactly_this_admission_and_successor():
    assert BATCH == ("scheduler-activation", "phase3-continue-06")
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
    if stem == "scheduler-activation":
        assert set(TRANSITION_FILES.values()) <= set(t.scope_fence)
        assert set(TRANSITION_FILES.values()) <= set(t.context)
        assert "ACTIVATION/CONTRADICTED TESTS" in FENCE_ADDITIONS[stem]["tests/test_daemon_config.py"]
        assert all("CALLER CLOSURE" in reason for path, reason in FENCE_ADDITIONS[stem].items()
                   if path.startswith("chupa/"))


@pytest.mark.parametrize("stem", PAYLOADS)
def test_implementing_seeds_cite_exactly_their_own_entry_and_row_contract(stem):
    t = _ticket(stem)
    assert t.plan_contract == AUTHORED[stem].plan == ("19.I", "19.P3.scheduler-activation")
    scope = t.sections["Scope in / Scope out"]
    assert len(OBLIGATIONS) == 11  # eight core plus three real preparation obligations
    assert all(name in scope for name in (*OBLIGATIONS, *TRANSITION_FILES))
    for fact in (
        "chupa/daemon.py", "chupa/__main__.py", "chupa/scheduler.py", "chupa/watcher.py",
        "chupa/config.py", "chupa/runner.py", "chupa/stages.py", "chupa/driver.py",
        "chupa/providers.py", "chupa/redact.py", "chupa/gates.py", "chupa/caps.py",
        "Watcher.publish", "Scheduler.update", "Watcher.remove", "Scheduler.remove",
        "Scheduler.dispatch", "DaemonAdmission.dispatch", "snapshot_dispatch(load, bind)",
        "dataclasses.replace(checkout, config=snapshot)", "runner.prepare_pipeline",
        "Config | ConfigSnapshot", "load_config", "--config", "config.yaml",
        "WATCHER_PARSE_FAILURE", "watcher_parse_failure", "EventType.SIGNAL",
        "key: null", "{signal: watcher_parse_failure, path: tickets/<stem>/ticket.md, reason: <nonempty diagnostic>}",
        "state_transition", "ticket_intake", "scheduler.max_unmerged", "default `2`",
        "Clock", "Sleep", "seconds", "text or `None`", "single-flight", "last-known-good",
        "invalid reload", "no preparation at construction", "no stage work starts",
        "no surviving owned task", "never real-model calls, host work, or wall-clock waits",
    ):
        assert fact in scope, fact


def test_successor_cites_next_admission_and_embeds_merged_earlier_idiom():
    t = _ticket("phase3-continue-06")
    assert t.plan_contract == AUTHORED[t.stem].plan
    assert set(t.plan_contract) == {
        "19.L", "19.I", "19.P3", "13", "20",
        "19.P3.merge-queue-activation", "19.P3.rework-activation",
        "19.P3.background-consumers", "19.P3.control-inbox",
        "19.P3.dispatch-pause-boundary", "19.P3.pause-resume-activation",
    }
    assert t.context == (MERGED_IDIOM,)
    assert t.scope_fence == ("tickets", "tests/test_seeded_phase3_06.py")
    assert len(MERGED_IDIOM_BLOB) == len(AUTHORING_HEAD) == 40
    assert "admissions[6:]" in t.sections["Goal / Why"]
    scope = t.sections["Scope in / Scope out"]
    for fact in (
        "phase3-continue-07", "admissions[7:]", "phase3-continue-08", "admissions[8:]",
        "tests/test_seeded_phase3_07.py", "tests/test_seeded_phase3_core.py",
        "Rework seed explicitly depends on its merge-queue-activation sibling",
        "depending on both merge-queue-activation and rework-activation",
        "control-inbox seed explicitly depends on its background-consumers sibling",
        "entry_unit_gap", "resolve_plan_contract", "section 11.4", "premise_failed",
        "chupa/runner.py", "chupa/drain.py", "chupa/scheduler.py", "tests/test_ladder.py",
        "tests/test_drain.py", "tests/test_scheduler.py", "tests/test_reject_queue.py",
        "tests/test_diagnose.py", "ConflictHandoff", "ReworkOrder", "REWORK_ORDER", "SUPERSEDES",
        "publication-before-supersedes-before-retirement", "producing-terminal-before-retirement",
        "fresh Implement/Check/Review approvals", "transitive successor dependency folds",
        "test_merge_queue_is_dormant", "seeding.max_seeds_per_admission",
        "terminal phase3-exit as its sole payload with no successor",
        "keep previously approved seeds verbatim", "ticket_sha",
    ):
        assert fact in scope, fact


@pytest.mark.parametrize("stem", BATCH)
def test_context_closure_and_max_effort_render_use_authoring_snapshots(stem):
    a = AUTHORED[stem]
    t = _ticket(stem)
    assert t.context == a.context
    assert t.on_demand == a.on_demand == ()  # all existing fenced paths fit embedded
    assert set(a.fenced_existing) == set(t.scope_fence) - {"tickets"} - (
        {"tests/test_daemon_composition.py"} if stem in PAYLOADS else {"tests/test_seeded_phase3_06.py"})
    assert set(a.fenced_existing) <= set(a.context) | set(a.on_demand)
    created = set(t.scope_fence) - set(a.fenced_existing) - {"tickets"}
    assert not created & (set(a.context) | set(a.on_demand))
    assert not set(a.context) & set(a.on_demand)
    assert not any(p.startswith("specs/") for p in (*a.context, *a.on_demand))
    assert set(a.context) <= DELIMITER_FREE_AT_AUTHORING
    assert all(FILE_CHARS[p] > 0 for p in (*a.context, *a.on_demand))
    assert all(PLAN_CHARS[pid] > 0 for pid in a.plan)
    assert 0 < a.measured_render <= render_chars(a) <= HEADROOM_CHARS
    for path in a.on_demand:
        assert render_chars(a, (path,)) > HEADROOM_CHARS, path


@pytest.mark.parametrize("stem", PAYLOADS)
def test_payloads_run_preservation_suites_without_fencing_or_embedding_them(stem):
    t = _ticket(stem)
    assert t.verification == (
        ("uv", "run", "pytest", *ACTIVATION_TESTS, *PRESERVATION),
        ("uv", "run", "pytest", "-q"),
    )
    assert not set(PRESERVATION) & (set(t.scope_fence) | set(t.context) | set(t.on_demand))
