"""Artifact base model and stage result types (CHUPA_PLAN.md sections 4, 5)."""

from dataclasses import dataclass
from typing import Annotated, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

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
