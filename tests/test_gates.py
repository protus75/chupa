import textwrap
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from pydantic import ValidationError

from chupa.artifacts import ARTIFACT_SCHEMA_VERSION, OUTCOMES, Artifact, Cost, Finding, StageResult
from chupa.config import load_config
from chupa.gates import (
    DEFAULT_GATE_SEVERITY,
    ENGINE_GATE_CODES,
    GateContractError,
    GateReport,
    lint_gate,
    merge_severity,
    run_gates,
)


class Slip(Artifact):
    branch: str


def slip(branch: str = "ticket/x") -> Slip:
    return Slip(produced_by_spec_version=1, produced_at_sha="a" * 40, branch=branch)


class StubGate:
    """Fails any artifact whose branch is not under ticket/."""

    code = "scope_fence"

    def check(self, artifact: Slip, workspace: Path) -> GateReport:
        if artifact.branch.startswith("ticket/"):
            return GateReport(code=self.code, verdict="pass")
        return GateReport(
            code=self.code,
            verdict="fail",
            findings=[
                Finding(
                    code=self.code,
                    message=f"branch {artifact.branch!r} is outside ticket/",
                    paved_road="rename the branch to ticket/<stem>",
                )
            ],
        )


class RoadlessGate(StubGate):
    """A gate that bypasses Finding validation to ship a finding with no paved road."""

    def check(self, artifact: Slip, workspace: Path) -> GateReport:
        report = super().check(artifact, workspace)
        if report.verdict == "fail":
            bad = Finding.model_construct(code=self.code, path=None, line=None, message="bad", paved_road="")
            return GateReport.model_construct(code=self.code, verdict="fail", findings=[bad], autofix_applied=False)
        return report


class SilentFailGate(StubGate):
    def check(self, artifact: Slip, workspace: Path) -> GateReport:
        return GateReport(code=self.code, verdict="fail")


SAMPLES = [slip("ticket/ok"), slip("feature/bad")]


# --- artifacts -------------------------------------------------------------


def test_outcome_vocab_is_closed_and_includes_already_satisfied():
    assert OUTCOMES == {
        "ok",
        "already_satisfied",
        "invalid_artifact",
        "gate_failed",
        "premise_failed",
        "timeout",
        "infra_error",
        "budget_exceeded",
    }


def test_finding_requires_nonblank_paved_road_and_allows_null_path_line():
    f = Finding(code="ticket_schema", message="missing kind", paved_road="add kind: feature")
    assert f.path is None and f.line is None
    with pytest.raises(ValidationError):
        Finding(code="ticket_schema", message="missing kind")
    with pytest.raises(ValidationError):
        Finding(code="ticket_schema", message="missing kind", paved_road="   ")


def test_artifact_carries_version_and_provenance():
    s = slip()
    assert s.artifact_schema_version == ARTIFACT_SCHEMA_VERSION
    assert s.produced_by_spec_version == 1 and s.produced_at_sha == "a" * 40
    with pytest.raises(ValidationError):
        Slip(produced_by_spec_version=1, branch="ticket/x")  # provenance is required


def test_artifact_reader_refuses_newer_tolerates_older_and_rejects_unknown_keys():
    raw = slip().model_dump()
    with pytest.raises(ValidationError, match="newer"):
        Slip.model_validate({**raw, "artifact_schema_version": ARTIFACT_SCHEMA_VERSION + 1})
    assert Slip.model_validate({**raw, "artifact_schema_version": 0}).artifact_schema_version == 0
    with pytest.raises(ValidationError):
        Slip.model_validate({**raw, "surprise": 1})


def test_stage_result_is_frozen_and_validates_outcome():
    r = StageResult(outcome="already_satisfied", artifact=None, findings=[], cost=Cost())
    with pytest.raises(FrozenInstanceError):
        r.outcome = "ok"  # type: ignore[misc]
    with pytest.raises(ValueError, match="outcome"):
        StageResult(outcome="done", artifact=None, findings=[], cost=Cost())  # type: ignore[arg-type]


def test_cost_defaults_are_the_non_llm_shape():
    c = Cost()
    assert (c.usd, c.provider, c.model) == (0.0, None, None)


# --- gate-lint -------------------------------------------------------------


def test_gate_lint_passes_stub_gate(tmp_path):
    assert lint_gate(StubGate(), SAMPLES, tmp_path) == []


def test_gate_lint_rejects_paved_road_less_gate(tmp_path):
    problems = lint_gate(RoadlessGate(), SAMPLES, tmp_path)
    assert problems and any("paved_road" in p for p in problems)


def test_gate_lint_rejects_fail_without_findings(tmp_path):
    problems = lint_gate(SilentFailGate(), SAMPLES, tmp_path)
    assert any("no findings" in p for p in problems)


def test_gate_lint_requires_a_failing_sample(tmp_path):
    problems = lint_gate(StubGate(), [slip("ticket/ok")], tmp_path)
    assert any("failing sample" in p for p in problems)


def test_gate_lint_rejects_code_outside_closed_vocab(tmp_path):
    class Rogue(StubGate):
        code = "vibes"

    problems = lint_gate(Rogue(), SAMPLES, tmp_path)
    assert any("vibes" in p for p in problems)


def test_gate_lint_rejects_report_code_mismatch(tmp_path):
    class Liar(StubGate):
        def check(self, artifact, workspace):
            return GateReport(code="diff_budget", verdict="pass")

    problems = lint_gate(Liar(), SAMPLES, tmp_path)
    assert any("diff_budget" in p for p in problems)


# --- runner + severity -----------------------------------------------------


def test_default_severity_is_all_hard_over_engine_codes():
    assert set(DEFAULT_GATE_SEVERITY) == ENGINE_GATE_CODES
    assert set(DEFAULT_GATE_SEVERITY.values()) == {"hard"}
    assert merge_severity(None) == DEFAULT_GATE_SEVERITY


def test_runner_defaults_to_all_hard(tmp_path):
    result = run_gates([StubGate()], slip("feature/bad"), tmp_path)
    assert not result.passed
    assert [r.code for r in result.hard_failures] == ["scope_fence"]
    assert result.soft_failures == []
    assert result.findings[0].paved_road == "rename the branch to ticket/<stem>"


def test_runner_passes_clean_artifact(tmp_path):
    result = run_gates([StubGate()], slip(), tmp_path)
    assert result.passed and result.hard_failures == [] and result.soft_failures == []


def test_runner_applies_soft_severity_from_config(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        textwrap.dedent(
            """\
            schema_version: 1
            state_dir: .chupa
            providers:
              - name: claude
                kind: cli
                models_by_tier: {low: a, medium: b, high: c, max: d}
                limits: {concurrency: 1, est_cost_per_call_usd: 0.25}
            routing:
              - {tier: medium, surface: implement, candidates: [{provider: claude, model: b}]}
            review:
              gate_severity: {scope_fence: soft}
            merge: {}
            engine_plane_safety_inventory: []
            """
        )
    )
    severity = merge_severity(load_config(cfg_path, cwd=tmp_path))
    assert severity["scope_fence"] == "soft" and severity["diff_budget"] == "hard"
    result = run_gates([StubGate()], slip("feature/bad"), tmp_path, severity=severity)
    assert result.passed
    assert [r.code for r in result.soft_failures] == ["scope_fence"]


def test_runner_refuses_gate_without_severity(tmp_path):
    with pytest.raises(GateContractError, match="scope_fence"):
        run_gates([StubGate()], slip(), tmp_path, severity={"diff_budget": "hard"})


def test_runner_fails_closed_on_paved_road_less_report(tmp_path):
    with pytest.raises(GateContractError, match="paved_road"):
        run_gates([RoadlessGate()], slip("feature/bad"), tmp_path)
