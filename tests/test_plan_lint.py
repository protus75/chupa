"""PLAN LINT (section 8): green over the real plan, and each check proven able to fail."""

from pathlib import Path

import pytest

from chupa.specs import lint_plan

PLAN = (Path(__file__).parent.parent / "CHUPA_PLAN.md").read_text()


def codes(findings):
    return {f.code for f in findings}


def test_real_plan_is_green():
    assert lint_plan(PLAN) == []


ENTRY = "- **Owner:** o\n- **Records:** r\n- **Observable:** b\n- **Tests:** t\n"


def build(*, section=10, registry: str | None = None, entries: str = "", extra="") -> str:
    parts = ["# Plan\n\n"]
    for n in range(1, 19):
        parts.append(f"## {n}. S{n}\n\n{'s' * (section if n == 1 else 10)}\n\n")
        if n == 11:
            parts.append("### 11.4 Dispatch\n\nd\n\n")
    parts.append("## 19. Phases\n\n### 19.L Laws\n\nl\n\n### 19.I Implementation laws\n\ni\n\n")
    for p in range(7):
        parts.append(f"### 19.P{p} Phase {p}\n\np\n\n")
        if p == 3 and registry is not None:
            parts.append("```yaml\n# BEGIN_REGISTRY_P3\n" + registry + "\n# END_REGISTRY_P3\n```\n\n" + entries)
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


def test_no_size_caps():
    # The per-ticket render is bounded at authoring (requisition), never by plan-side caps.
    assert lint_plan(build(section=100_000)) == []


def test_missing_and_unknown_units():
    assert "plan_unit" in codes(lint_plan(build().replace("### 19.P4 Phase 4", "### Phase 4")))
    assert "plan_unit" in codes(lint_plan(build().replace("### 19.P4 Phase 4", "### 19.P4b Phase 4")))
    assert "plan_unit" in codes(lint_plan(build().replace("## 7. S7", "## Seven")))
    assert "plan_unit" in codes(lint_plan(build().replace("### 19.I Implementation laws\n\ni\n\n", "")))


def test_subsection_must_sit_in_its_own_section():
    assert "plan_unit" in codes(lint_plan(build().replace("### 11.4 Dispatch", "### 12.4 Dispatch")))


def test_entry_unit_must_name_a_row_of_its_phase():
    good = build(registry=GOOD_REGISTRY, entries="### 19.P3.a Row a\n\n" + ENTRY + "\n")
    assert lint_plan(good) == []
    assert "plan_unit" in codes(lint_plan(good.replace("### 19.P3.a ", "### 19.P3.zz ")))
    assert "plan_unit" in codes(lint_plan(good.replace("### 19.P3.a ", "### 19.P4.a ")))


@pytest.mark.parametrize("part", ["Owner", "Records", "Observable", "Tests"])
def test_entry_unit_carries_every_spec_depth_part(part):
    lines = ENTRY.splitlines()
    for thin in ([ln for ln in lines if not ln.startswith(f"- **{part}:**")],  # part absent
                 [f"- **{part}:**" if ln.startswith(f"- **{part}:**") else ln for ln in lines]):  # part empty
        plan = build(registry=GOOD_REGISTRY, entries="### 19.P3.a Row a\n\n" + "\n".join(thin) + "\n\n")
        assert "plan_entry" in codes(lint_plan(plan))


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


@pytest.mark.parametrize("cite", ["[22]", "[19]", "[0]", "[21]", "[99]", "['9']", "[11.4]", "['11.9']", "['19.P3']"])
def test_registry_cites_must_resolve(cite):
    assert "registry_cite" in codes(lint_plan(build(registry=GOOD_REGISTRY.replace("[9, 20]", cite))))


@pytest.mark.parametrize("cite", ["['11.4']", "['19.L', 9]"])
def test_registry_cites_subsections_and_build_laws(cite):
    assert lint_plan(build(registry=GOOD_REGISTRY.replace("[9, 20]", cite))) == []


def test_real_plan_registries_are_linted():
    # Coverage-break the real P4 registry: lint must notice, proving the real blocks are parsed.
    broken = PLAN.replace("  - [watchdog-event-stream, notify-transport]\n", "  - [watchdog-event-stream]\n", 1)
    assert broken != PLAN
    assert "registry_coverage" in codes(lint_plan(broken))
