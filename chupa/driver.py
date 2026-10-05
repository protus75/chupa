"""The one LLM-stage driver (CHUPA_PLAN.md section 5 invariant 2, section 6).

render -> spool prompt -> call (raced against the stuck budget) -> spool output -> unwrap one
fence -> validate -> gates -> on hard failure re-prompt the SAME workspace with the findings,
bounded by the retry cap. Stages differ only in spec (render), artifact type, and gate list.
"""

import asyncio
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from chupa.artifacts import Cost, Finding, Outcome, StageResult
from chupa.config import Config, Severity
from chupa.enginelog import EngineLog
from chupa.gates import Gate, merge_severity, run_gates
from chupa.llm import LLM, AgentEffort, AgentTier, LLMRequest, LLMResult
from chupa.redact import Redactor
from chupa.seams import Clock, FileSystem, LocalFileSystem, Sleep

# Closed allowlist of tree-writing surfaces (section 6): every other surface is called read-only.
WRITING_SURFACES = frozenset({"implement"})

_FENCE = re.compile(r"\A\s*(`{3,})[\w+-]*[ \t]*\n(.*)\n\1[ \t]*\s*\Z", re.DOTALL)


def unwrap_fence(text: str) -> str:
    """Strip exactly ONE surrounding markdown code fence (optionally language-tagged)."""
    m = _FENCE.match(text)
    return m.group(2) if m else text


@dataclass(frozen=True)
class LlmStage:
    surface: str
    emits: type[BaseModel]
    gates: Sequence[Gate]
    render: Callable[[Any, list[Finding]], str]  # (consumed artifact, re-prompt findings) -> prompt


class Spool:
    """Per-attempt capture at `<root>/<stem>/<attempt>/`; every byte passes the redactor."""

    def __init__(self, root: Path, redactor: Redactor, fs: FileSystem) -> None:
        self.root = root
        self._redactor = redactor
        self._fs = fs

    def write(self, stem: str, attempt: int, name: str, text: str) -> None:
        self._fs.write(self.root / stem / str(attempt) / name, self._redactor.scrub(text).encode())


class _StuckBudget(Exception):
    pass


@dataclass
class _Tally:
    calls: int = 0
    tokens: int | None = None
    usd: float = 0.0
    last: LLMResult | None = None
    findings: list[Finding] = field(default_factory=list)

    def add(self, r: LLMResult) -> None:
        self.last = r
        self.usd += r.usd
        used = [t for t in (r.input_tokens, r.output_tokens) if t is not None]
        if used:
            self.tokens = (self.tokens or 0) + sum(used)


class Driver:
    def __init__(
        self,
        *,
        llm: LLM,
        spool: Spool,
        log: EngineLog,
        clock: Clock,
        sleep: Sleep,
        severity: Mapping[str, Severity],
        retry_cap: int,
    ) -> None:
        self.llm = llm
        self.spool = spool
        self.log = log
        self.clock = clock
        self.sleep = sleep
        self.severity = severity
        self.retry_cap = retry_cap

    @classmethod
    def from_config(
        cls,
        config: Config,
        *,
        llm: LLM,
        env: Mapping[str, str],
        clock: Clock,
        sleep: Sleep,
        fs: FileSystem | None = None,
    ) -> "Driver":
        """The production wiring: the redactor is built from config BEFORE any writer exists."""
        redactor = Redactor.from_config(config, env)
        return cls(
            llm=llm,
            spool=Spool(config.state_dir / "spools", redactor, fs or LocalFileSystem()),
            log=EngineLog(config.state_dir / "engine.log", redactor, clock),
            clock=clock,
            sleep=sleep,
            severity=merge_severity(config),
            retry_cap=config.caps.retry,
        )

    async def run(
        self,
        stage: LlmStage,
        consumed: Any,
        *,
        ticket: str | None,
        attempt: int,
        workspace: Path,
        tier: AgentTier,
        effort: AgentEffort,
        stuck_budget: float,
    ) -> StageResult:
        """Run one stage attempt; `attempt` is the run sequence (section 6), stuck_budget in seconds."""
        stem = ticket or stage.surface  # ticketless surfaces spool under their surface name
        started = self.clock()
        deadline = started.timestamp() + stuck_budget
        ctx = {"stem": stem, "attempt": attempt, "surface": stage.surface}
        tally = _Tally()
        self.log.event("stage_start", **ctx, stuck_budget=stuck_budget)

        def done(outcome: Outcome, artifact: BaseModel | None = None) -> StageResult:
            seconds = (self.clock() - started).total_seconds()
            self.log.event("stage_end", **ctx, outcome=outcome, calls=tally.calls)
            last = tally.last
            cost = Cost(
                tokens=tally.tokens,
                seconds=seconds,
                attempts=tally.calls,
                usd=tally.usd,
                provider=last.provider if last else None,
                model=last.model if last else None,
            )
            return StageResult(outcome=outcome, artifact=artifact, findings=tally.findings, cost=cost)

        outcome: Outcome = "ok"
        for call_seq in range(1, self.retry_cap + 2):  # the first call plus retry_cap re-prompts
            call = {**ctx, "call_seq": call_seq}
            name = f"call-{call_seq:02d}"
            prompt = stage.render(consumed, tally.findings)
            req = LLMRequest(
                surface=stage.surface,
                rendered=prompt,
                tier=tier,
                effort=effort,
                ticket=ticket,
                worktree=workspace if stage.surface in WRITING_SURFACES else None,
            )
            # Before the call: a call that raises or hangs must leave exactly what was sent on disk.
            self.spool.write(stem, attempt, f"{name}/prompt.md", prompt)
            self.log.event("llm_call", **call)
            tally.calls += 1
            try:
                result = await self._race(req, deadline - self.clock().timestamp())
            except _StuckBudget:
                self.log.event("stuck_budget_kill", **call)
                tally.findings = []
                return done("timeout")
            except Exception as e:
                self.spool.write(stem, attempt, f"{name}/error.txt", f"{type(e).__name__}: {e}")
                self.log.event("llm_error", **call, error=f"{type(e).__name__}: {e}")
                tally.findings = []  # unclassified: no finding (section 6)
                return done("infra_error")
            tally.add(result)
            self.spool.write(stem, attempt, f"{name}/output.txt", result.text)

            try:
                artifact = stage.emits.model_validate_json(unwrap_fence(result.text))
            except ValidationError as e:
                outcome = "invalid_artifact"
                tally.findings = [_invalid(stage, e)]
                self.log.event("artifact_invalid", **call, errors=e.error_count())
                continue

            gated = run_gates(stage.gates, artifact, workspace, severity=self.severity)
            if gated.passed:
                tally.findings = gated.findings  # soft only
                return done("ok", artifact)
            outcome = "gate_failed"
            tally.findings = [f for r in gated.hard_failures for f in r.findings]
            self.log.event("gate_failed", **call, codes=[r.code for r in gated.hard_failures])
        return done(outcome)

    async def _race(self, req: LLMRequest, remaining: float) -> LLMResult:
        if remaining <= 0:
            raise _StuckBudget
        call = asyncio.ensure_future(self.llm.call(req))
        timer = asyncio.ensure_future(self.sleep(remaining))
        try:
            await asyncio.wait({call, timer}, return_when=asyncio.FIRST_COMPLETED)
        except BaseException:
            await self._kill(call, timer)
            raise
        if call.done():
            timer.cancel()
            return call.result()
        await self._kill(call, timer)
        raise _StuckBudget

    async def _kill(self, call: asyncio.Future, timer: asyncio.Future) -> None:
        # abort_current FIRST: cancelling alone leaves a hung writer's process group alive in the worktree.
        self.llm.abort_current()
        timer.cancel()
        call.cancel()
        await asyncio.wait({call, timer})
        if not call.cancelled():
            call.exception()  # retrieved: the aborted call's error is expected, not a leak


def _invalid(stage: LlmStage, e: ValidationError) -> Finding:
    detail = "; ".join(f"{'.'.join(map(str, err['loc'])) or '<root>'}: {err['msg']}" for err in e.errors())
    return Finding(
        code="invalid_artifact",
        message=f"output is not a valid {stage.emits.__name__}: {detail}",
        paved_road=f"reply with ONLY one JSON object matching the {stage.emits.__name__} schema, no prose",
    )
