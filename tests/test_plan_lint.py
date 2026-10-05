"""PLAN LINT (section 8): green over the real plan, and each check proven able to fail."""

from pathlib import Path

import pytest

from chupa.specs import SEED_RENDER_BUDGET, lint_plan

PLAN = (Path(__file__).parent.parent / "CHUPA_PLAN.md").read_text()


def codes(findings):
    return {f.code for f in findings}


def test_real_plan_is_green():
    assert lint_plan(PLAN) == []


def test_seed_render_budget_is_half_the_max_bound():
    assert SEED_RENDER_BUDGET == 80_000


def build(*, laws=10, phase=10, section=10, registry: str | None = None, extra="") -> str:
    parts = ["# Plan\n\n"]
    for n in range(1, 19):
        parts.append(f"## {n}. S{n}\n\n{'s' * (section if n == 1 else 10)}\n\n")
    parts.append("## 19. Phases\n\n### 19.L Laws\n\n" + "l" * laws + "\n\n")
    for p in range(7):
        parts.append(f"### 19.P{p} Phase {p}\n\n{'p' * (phase if p == 0 else 10)}\n\n")
        if p == 3 and registry is not None:
            parts.append("```yaml\n# BEGIN_REGISTRY_P3\n" + registry + "\n# END_REGISTRY_P3\n```\n\n")
    parts.append("## 20. Open\n\nx\n\n## 21. Appendix\n\nx\n\n## 22. Why\n\nx\n" + extra)
    return "".join(parts)


GOOD_REGISTRY = """phase: 3
admissions:
  - [a, b]
  - [c]
seeds:
  a: {cite: [9], fence: [x]}
  b: {fence: [y]}
  c: {cite: [9, 20], exit: true, fence: [z]}"""


def test_fixture_plan_is_green():
    assert lint_plan(build(registry=GOOD_REGISTRY)) == []


def test_unit_caps():
    assert lint_plan(build(laws=21_900)) == []
    assert "plan_size" in codes(lint_plan(build(laws=22_001)))
    assert lint_plan(build(phase=25_900)) == []
    assert "plan_size" in codes(lint_plan(build(phase=26_001)))
    assert lint_plan(build(section=35_900)) == []
    assert "plan_size" in codes(lint_plan(build(section=36_001)))


def test_section_22_is_excluded_from_budgets():
    plan = build().replace("## 22. Why\n\nx\n", "## 22. Why\n\n" + "w" * 100_000 + "\n")
    assert lint_plan(plan) == []


def test_synthetic_seed_render_budget():
    # Each under its own cap, but 19.L + largest phase + largest section breaches 80,000.
    findings = lint_plan(build(laws=21_000, phase=25_000, section=35_000))
    assert codes(findings) == {"plan_seed_render"}
    assert lint_plan(build(laws=20_000, phase=20_000, section=30_000)) == []


def test_missing_and_unknown_units():
    assert "plan_unit" in codes(lint_plan(build().replace("### 19.P4 Phase 4", "### Phase 4")))
    assert "plan_unit" in codes(lint_plan(build().replace("### 19.P4 Phase 4", "### 19.P4b Phase 4")))
    assert "plan_unit" in codes(lint_plan(build().replace("## 7. S7", "## Seven")))


def test_duplicate_heading():
    assert "plan_heading" in codes(lint_plan(build(extra="\n## 3. Again\n\nx\n")))


def test_registry_must_parse():
    assert "registry_parse" in codes(lint_plan(build(registry="admissions: [a, [")))
    assert "registry_parse" in codes(lint_plan(build(registry="admissions: [a]\nseeds: {a: {}}")))
    unclosed = build(registry=GOOD_REGISTRY).replace("# END_REGISTRY_P3", "# END_REGISTRY_P4")
    assert "registry_parse" in codes(lint_plan(unclosed))


@pytest.mark.parametrize(
    "registry",
    [
        GOOD_REGISTRY.replace("  - [c]\n", ""),  # c declared, never admitted
        GOOD_REGISTRY.replace("[c]", "[c, d]").replace("[a, b]", "[a]\n  - [b]"),  # d admitted, undeclared
        GOOD_REGISTRY.replace("[c]", "[c, a]").replace("[a, b]", "[a]\n  - [b]"),  # a admitted twice
    ],
)
def test_registry_admissions_cover_seeds_exactly(registry):
    assert "registry_coverage" in codes(lint_plan(build(registry=registry)))


def test_registry_admission_payload_cap():
    three = GOOD_REGISTRY.replace("  - [a, b]\n  - [c]", "  - [a, b, c]")
    assert "registry_admission" in codes(lint_plan(build(registry=three)))


@pytest.mark.parametrize("cite", ["[22]", "[19]", "[0]", "[21]", "[99]", "['9']"])
def test_registry_cites_must_resolve(cite):
    assert "registry_cite" in codes(lint_plan(build(registry=GOOD_REGISTRY.replace("[9, 20]", cite))))


def test_real_plan_registries_are_linted():
    # Coverage-break the real P4 registry: lint must notice, proving the real blocks are parsed.
    broken = PLAN.replace("  - [watchdog-event-stream, notify-transport]\n", "  - [watchdog-event-stream]\n", 1)
    assert broken != PLAN
    assert "registry_coverage" in codes(lint_plan(broken))
