import asyncio
import json
from types import SimpleNamespace

import pytest

from chupa import requisition
from chupa.driver import _StuckBudget
from chupa.providers import ProviderCallError


class MemoryPath:
    def __truediv__(self, name):
        return self

    def read_text(self):
        return "spec"


@pytest.mark.parametrize("case,outcome", [("approve", "ok"), ("snag", "gate_failed"), ("error", "infra_error"), ("timeout", "timeout"), ("provider", "infra_error")])
def test_stage_events(monkeypatch, case, outcome):
    events = []
    monkeypatch.setattr(requisition, "review_target", lambda *args: SimpleNamespace(scope_fence=()))
    monkeypatch.setattr(requisition, "_base_render", lambda *args: "base")
    monkeypatch.setattr(requisition, "load_spec", lambda text: SimpleNamespace(meta=SimpleNamespace(version="1.0", effort="high")))
    monkeypatch.setattr(requisition, "render", lambda *args: "prompt")

    async def call(*args, **kwargs):
        if case == "error":
            raise ValueError("bad provider")
        if case == "provider":
            raise ProviderCallError("fake", "failed", rc=2, stderr_tail="bad")
        findings = [{"code": "scope", "message": "missing", "paved_road": "add file"}] if case == "snag" else []
        return dict(text=json.dumps(dict(verdict=case, summary="reviewed", findings=findings)), input_tokens=1, output_tokens=2, provider="fake", model="m", usd=0.1)

    monkeypatch.setattr(requisition, "llm_call", call)

    async def race(fn, timeout):
        if case == "timeout":
            raise _StuckBudget()
        return await fn()

    driver = SimpleNamespace(
        retry_cap=0,
        spool=SimpleNamespace(write=lambda *args: None),
        _active=True,
        race=race,
        effects=None,
        watched_llm=lambda: None,
        redactor=None,
        log=SimpleNamespace(event=lambda event, **kw: events.append((event, kw))),
    )

    async def run():
        return await requisition.review_ticket(
            driver,
            repo=MemoryPath(),
            stem="actual",
            text="ticket",
            specs_dir=MemoryPath(),
            coverage_map=None,
            tier="high",
            stem_slot="slot",
            run_seq=7,
            attempt=3,
            call_seq=1,
            expected_budget="surface",
        )

    if case == "provider":
        with pytest.raises(ProviderCallError):
            asyncio.run(run())
    else:
        asyncio.run(run())
    context = dict(stem="actual", attempt=3, surface="requisition_review", run_seq=7)
    assert events == [("stage_start", context), ("stage_end", {**context, "outcome": outcome, "calls": 1})]
