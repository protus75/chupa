import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import chupa
from chupa import providers
from chupa.config import Limits, ModelsByTier, Provider
from chupa.providers import ClaudeAdapter, ProviderSetupError, QwenAdapter


def provider(name="qwen", base_url="http://h:11434/v1"):
    return Provider(name=name, kind="cli", package="pkg", base_url=base_url, models_by_tier=ModelsByTier(low="a", medium="b", high="c", max="d"), limits=Limits(concurrency=1, est_cost_per_call_usd=0))


def adapter(p):
    return QwenAdapter(p, config=SimpleNamespace(providers=[p]), exec_=Mock(), fs=Mock(), redactor=Mock(), env={"PATH": "/bin"}, cwd=Path("/repo"), capture_dir=Path("/capture"), timeout=120)


def test_qwen_argv_and_env():
    a = adapter(provider())
    expected = [
        "qwen",
        "--auth-type",
        "openai",
        "--openai-base-url",
        "http://h:11434/v1",
        "--openai-api-key",
        "ollama",
        "-m",
        "qwen3-coder:30b",
        "-o",
        "stream-json",
        "--approval-mode",
        "plan",
        "--chat-recording",
        "false",
    ]
    assert a.argv("qwen3-coder:30b", "low", False) == expected
    expected[expected.index("plan")] = "yolo"
    assert a.argv("qwen3-coder:30b", "low", True) == expected
    path = Path(a.call_env()["QWEN_CODE_SYSTEM_SETTINGS_PATH"])
    assert path.is_absolute() and path == Path(chupa.__file__).parent / "qwen-settings.json"
    assert json.loads(path.read_text()) == {"context": {"fileName": "CLAUDE.md"}}
    assert a.call_env()["PATH"] == "/bin"


def test_parse_recorded_stream():
    events = [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "tool1"}]}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "draft"}]}},
        {"type": "result", "subtype": "success", "is_error": False, "result": "finished", "usage": {"input_tokens": 7, "cache_read_input_tokens": 3, "output_tokens": 2}},
    ]
    result = adapter(provider()).parse("\n".join(map(json.dumps, events)))
    assert (result.text, result.input_tokens, result.usd) == ("finished", 10, None)


def test_setup_and_conduct():
    with pytest.raises(ProviderSetupError, match="set base_url"):
        adapter(provider(base_url=None))
    p = provider("claude")
    with pytest.raises(ProviderSetupError, match="remove base_url"):
        ClaudeAdapter(p, config=Mock(), exec_=Mock(), fs=Mock(), redactor=Mock(), env={}, cwd=Path("/"), capture_dir=Path("/"), timeout=1)
    assert providers.ADAPTERS["qwen"] is QwenAdapter and not QwenAdapter.reports_cost
    p = provider()
    route = SimpleNamespace(tier="low", surface="implement", candidates=[SimpleNamespace(provider="qwen", model=None)])
    assert providers.routed_conduct_paths(SimpleNamespace(providers=[p], routing=[route]), Path("/checkout")) == (Path("/checkout/CLAUDE.md"),)
