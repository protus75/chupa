"""Artifact base model and stage result types (CHUPA_PLAN.md sections 4, 5)."""

from dataclasses import dataclass
import re
from typing import Annotated, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

ARTIFACT_SCHEMA_VERSION = 1

Outcome = Literal[
    "ok",
    "already_satisfied",
    "invalid_artifact",
    "gate_failed",
    "premise_failed",
    "timeout",
    "infra_error",
    "budget_exceeded",
]
OUTCOMES: frozenset[str] = frozenset(get_args(Outcome))

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class _Strict(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class Finding(_Strict):
    code: NonBlank
    path: str | None = None
    line: Annotated[int, Field(ge=1)] | None = None
    message: NonBlank
    paved_road: NonBlank  # required: a finding that cannot say what to do instead fails gate-lint
    # Section 7: a requisition_review finding names whether the spec or the authoring is at fault.
    kind: Literal["spec_gap", "authoring_error"] | None = None
    unit: str | None = None

    @model_validator(mode="after")
    def _unit_only_for_spec_gap(self) -> "Finding":
        if self.unit is not None and self.kind != "spec_gap":
            raise ValueError("unit is non-null only for kind spec_gap")
        return self


class Harvest(_Strict):
    """The closed, ticket-plane record extracted from one failed run."""

    attempt: Annotated[int, Field(ge=0)]
    stage: Literal["implement", "check", "review", "merge"] | None
    terminal: str
    findings: list[Finding]
    reason: str | None
    diff_stat: str
    stage_log_tail: str
    events_tail: str
    wall_seconds: float | None
    usd: float | None
    run_record: str | None

    @field_validator("terminal")
    @classmethod
    def _terminal_state(cls, value: str) -> str:
        from chupa.journal import TERMINAL_STATES

        if value not in TERMINAL_STATES:
            raise ValueError(f"terminal {value!r} is not one of {sorted(TERMINAL_STATES)}")
        return value

    @model_validator(mode="after")
    def _reason_only_without_findings(self) -> "Harvest":
        if self.findings and self.reason is not None:
            raise ValueError("reason is set only when findings is empty")
        return self


class Artifact(_Strict):
    """Base of every stage-emitted artifact except the ticket (section 5 versioning policy)."""

    artifact_schema_version: Annotated[int, Field(ge=0)] = ARTIFACT_SCHEMA_VERSION
    produced_by_spec_version: int
    produced_at_sha: NonBlank

    @field_validator("artifact_schema_version")
    @classmethod
    def _refuse_newer(cls, v: int) -> int:
        if v > ARTIFACT_SCHEMA_VERSION:
            raise ValueError(
                f"artifact_schema_version {v} is newer than this engine's {ARTIFACT_SCHEMA_VERSION};"
                " upgrade chupa to a release that reads it"
            )
        return v


SHAKEOUT_REPORT = "shakeout-report.json"
SHAKEOUT_SPEC_VERSION = 1


class ShakeoutEntry(_Strict):
    member: NonBlank
    group: NonBlank
    planted_fault: NonBlank
    expected: NonBlank
    observed: NonBlank
    producing_run: NonBlank
    auditor: list[NonBlank]
    green: bool

    @model_validator(mode="after")
    def _consistent(self) -> "ShakeoutEntry":
        if not re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*", self.member):
            raise ValueError("member must be a snake-case id")
        if not re.fullmatch(r"[a-z][a-z0-9_-]*/[0-9]+", self.producing_run):
            raise ValueError("producing_run must be <bench stem>/<run seq>")
        if self.green != (self.observed == self.expected and not self.auditor):
            raise ValueError("green must match the observation and empty auditor")
        return self


class ShakeoutReport(Artifact):
    entries: list[ShakeoutEntry]

    @model_validator(mode="after")
    def _unique_members(self) -> "ShakeoutReport":
        ids = [entry.member for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("member ids must be unique")
        return self


DAEMON_SOAK_REPORT = "daemon-soak-report.json"
DAEMON_SOAK_SPEC_VERSION = 1
DAEMON_SOAK_MEMBERS = (
    "worker_killed_mid_run",
    "conflict_resolution_rungs",
    "semantic_conflict_integration_red",
)
_DAEMON_SOAK_EXPECTED = {
    "worker_killed_mid_run": ("abandoned_alerted_then_merged", "alert"),
    "conflict_resolution_rungs": ("mechanical_and_rework_main_green", "resolved"),
    "semantic_conflict_integration_red": ("integration_red_main_green", "refused"),
}


class DaemonSoakEntry(_Strict):
    """One closed member's observation (CHUPA_PLAN.md 19.P3.daemon-soak)."""

    member: Literal["worker_killed_mid_run", "conflict_resolution_rungs",
                    "semantic_conflict_integration_red"]
    planted_fault: NonBlank
    expected: NonBlank
    observed: NonBlank
    disposition: Literal["alert", "resolved", "refused"]
    producing_run: str
    auditor: list[NonBlank]
    green: bool

    @model_validator(mode="after")
    def _consistent(self) -> "DaemonSoakEntry":
        from chupa.tickets import stem_findings

        stem, separator, sequence = self.producing_run.rpartition("/")
        if not separator or not re.fullmatch(r"[0-9]+", sequence) or stem_findings(stem):
            raise ValueError("producing_run must be <ticket stem>/<nonnegative run sequence>")
        if (self.expected, self.disposition) != _DAEMON_SOAK_EXPECTED[self.member]:
            raise ValueError(f"{self.member} requires expected/disposition {_DAEMON_SOAK_EXPECTED[self.member]}")
        if self.green != (self.observed == self.expected and not self.auditor):
            raise ValueError("green must match the observation and empty auditor")
        return self


class DaemonSoakReport(Artifact):
    entries: list[DaemonSoakEntry]

    @model_validator(mode="after")
    def _ordered_members(self) -> "DaemonSoakReport":
        if tuple(entry.member for entry in self.entries) != DAEMON_SOAK_MEMBERS:
            raise ValueError(f"entries must contain exactly {DAEMON_SOAK_MEMBERS}, in order")
        return self


@dataclass(frozen=True)
class Cost:
    tokens: int | None = None  # None when a cli stream reports no usage
    seconds: float = 0.0
    attempts: int = 0
    usd: float = 0.0
    provider: str | None = None  # None for non-LLM effects
    model: str | None = None


@dataclass(frozen=True)
class StageResult:
    outcome: Outcome
    artifact: Artifact | None
    findings: list[Finding]
    cost: Cost

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"outcome {self.outcome!r} is not one of {sorted(OUTCOMES)}")


ReviewVerdictName = Literal["approve", "snag", "rma"]
DiagnosisVerdictName = Literal["retry", "escalate", "split", "reject", "abandon-human"]
DIAGNOSIS_VERDICTS = get_args(DiagnosisVerdictName)
DIAGNOSIS_MAX_LESSONS = 5
DIAGNOSIS_LESSON_CHARS = 300


class DiagnosisReply(_Strict):
    verdict: DiagnosisVerdictName
    lessons: Annotated[list[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1,
                                                              max_length=DIAGNOSIS_LESSON_CHARS)]],
                       Field(min_length=1, max_length=DIAGNOSIS_MAX_LESSONS)]


class Diagnosis(Artifact):
    stem: NonBlank
    attempt: Annotated[int, Field(ge=0)]
    terminal: str
    stage: str | None
    verdict: DiagnosisVerdictName
    lessons: list[str]
    mechanical: str | None
    spec_version: NonBlank
    provider: str | None
    model: str | None


# specs/review.md's closed finding codes: `ticket` is the rma code, the rest are snag codes.
REVIEW_SNAG_CODES = frozenset({"logic", "acceptance", "scope", "leak"})


class ReviewVerdict(_Strict):
    """The review surface's model-facing reply (specs/review.md); the stage stamps provenance around it."""

    verdict: ReviewVerdictName
    summary: NonBlank
    findings: list[Finding]

    @model_validator(mode="after")
    def _findings_match_verdict(self) -> "ReviewVerdict":
        codes = {f.code for f in self.findings}
        if self.verdict == "approve" and self.findings:
            raise ValueError("approve carries an empty findings list; reply snag to block on a finding")
        if self.verdict == "snag" and not (codes and codes <= REVIEW_SNAG_CODES):
            raise ValueError(f"snag needs at least one finding, every code one of {sorted(REVIEW_SNAG_CODES)}")
        if self.verdict == "rma" and not (codes and codes <= {"ticket"}):
            raise ValueError("rma needs at least one finding, every code `ticket`")
        return self
