"""The LLM call as an effect (CHUPA_PLAN.md sections 2 and 6).

Keyed `llm/<stem>/<run_seq>/<surface>/<attempt>/<call_seq>`: one cost-bearing completion per call,
and a same-key re-entry (no intervening terminal, so the same run_seq) replays the recorded result
instead of calling. The driver reaches the model only through `llm_call`.
"""

from dataclasses import asdict, replace
from typing import Any

from chupa.effects import effect
from chupa.llm import LLM, LLMRequest
from chupa.redact import Redactor


def llm_key(stem: str, run_seq: int, surface: str, attempt: int, call_seq: int) -> str:
    return "/".join(("llm", stem, str(run_seq), surface, str(attempt), str(call_seq)))


def _cost(result: dict[str, Any]) -> dict[str, Any]:
    return {k: result[k] for k in ("usd", "input_tokens", "output_tokens", "provider", "model")}


@effect(
    key=lambda llm, req, redactor, *, stem, run_seq, attempt, call_seq: llm_key(
        stem, run_seq, req.surface, attempt, call_seq
    ),
    cost=_cost,
)
async def llm_call(
    llm: LLM, req: LLMRequest, redactor: Redactor, *, stem: str, run_seq: int, attempt: int, call_seq: int
) -> dict[str, Any]:
    result = await llm.call(req)
    # Scrubbed once, before it becomes the completion record: execute and replay return the same bytes.
    return asdict(replace(result, text=redactor.scrub(result.text)))
