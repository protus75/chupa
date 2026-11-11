from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from chupa import drain, runner, serve


class RecordingLog:
    def __init__(self, *args):
        self.events = []

    def event(self, event, **fields):
        self.events.append((event, fields))


def install_log(monkeypatch, module):
    log = RecordingLog()
    monkeypatch.setattr(module, "EngineLog", lambda *args: log)
    monkeypatch.setattr(module.Redactor, "from_config", lambda *args: None)
    return log


def events(phase, outcome):
    return [("phase_start", {"phase": phase}), ("phase_end", {"phase": phase, "outcome": outcome})]


@pytest.mark.asyncio
@pytest.mark.parametrize("result,outcome", [([], "ok"), (["bad provider"], "failed"), (RuntimeError("probe"), "failed")])
async def test_preflight_events(monkeypatch, result, outcome):
    log = install_log(monkeypatch, runner)
    config = SimpleNamespace(state_dir=Path("/state"))
    checkout = SimpleNamespace(config=config, exec_=None, fs=None, env={}, repo=Path("/repo"), control=SimpleNamespace(providers=None), clock=None)
    provider = SimpleNamespace(preflight=AsyncMock(side_effect=result if isinstance(result, Exception) else None, return_value=result), preflight_notices=[])
    monkeypatch.setattr(runner, "ProviderLLM", lambda *args, **kwargs: provider)
    monkeypatch.setattr(runner, "call_timeout", lambda config: 1)
    bound = object()
    monkeypatch.setattr(runner, "bind", lambda checkout, llm: bound)
    if isinstance(result, Exception):
        with pytest.raises(RuntimeError, match="probe"):
            await runner.prepare_pipeline(checkout)
    elif result:
        with pytest.raises(runner.Refusal, match="bad provider"):
            await runner.prepare_pipeline(checkout)
    else:
        assert await runner.prepare_pipeline(checkout) is bound
    assert log.events == events("preflight", outcome)


@pytest.mark.asyncio
@pytest.mark.parametrize("result,outcome", [(None, "no_report"), (object(), "ran"), (RuntimeError("retro"), "failed")])
async def test_drain_retro_events(monkeypatch, result, outcome):
    log = install_log(monkeypatch, drain)
    d = object.__new__(drain._Drain)
    d.c = SimpleNamespace(config=SimpleNamespace(state_dir=Path("/state")), env={}, clock=None, sleep=None, control=None)
    d.retro = AsyncMock(side_effect=result if isinstance(result, Exception) else None, return_value=result)
    d.retro.abort_current = AsyncMock()
    if isinstance(result, Exception):
        with pytest.raises(RuntimeError, match="retro"):
            await d._run_retro(forced=False)
    else:
        await d._run_retro(forced=False)
    assert log.events == events("retro_check", outcome)


@dataclass
class Checkout:
    config: object
    journal: object
    clock: object


@pytest.mark.asyncio
@pytest.mark.parametrize("trigger,outcome", [(None, "not_due"), (object(), "due")])
async def test_serve_retro_events(monkeypatch, trigger, outcome):
    s = object.__new__(serve.Serve)
    s.log = RecordingLog()
    config = SimpleNamespace(retro=object())
    s.checkout = Checkout(config, SimpleNamespace(read=lambda: ["journal"]), lambda: "now")
    s.control = SimpleNamespace(load_config=lambda: config)
    s.retro_due = False
    monkeypatch.setattr(serve, "snapshot_config", lambda value: value)
    monkeypatch.setattr(serve, "project_window", lambda value: value)
    monkeypatch.setattr(serve, "suppressing_failure", lambda value: None)
    monkeypatch.setattr(serve, "production_evidence", AsyncMock(return_value="evidence"))
    monkeypatch.setattr(serve, "select_trigger", lambda *args, **kwargs: trigger)
    await s.check_retro()
    assert s.retro_due is (trigger is not None)
    assert s.log.events == events("retro_check", outcome)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["journal", "evidence"])
async def test_serve_retro_failure(monkeypatch, failure):
    s = object.__new__(serve.Serve)
    s.log = RecordingLog()
    config = SimpleNamespace(retro=object())

    def read():
        if failure == "journal":
            raise RuntimeError("journal")
        return ["journal"]

    s.checkout = Checkout(config, SimpleNamespace(read=read), lambda: "now")
    s.control = SimpleNamespace(load_config=lambda: config)
    monkeypatch.setattr(serve, "snapshot_config", lambda value: value)
    monkeypatch.setattr(serve, "project_window", lambda value: value)
    monkeypatch.setattr(serve, "suppressing_failure", lambda value: None)
    monkeypatch.setattr(serve, "production_evidence", AsyncMock(side_effect=RuntimeError("evidence")))
    with pytest.raises(RuntimeError, match=failure):
        await s.check_retro()
    assert s.log.events == events("retro_check", "failed")
