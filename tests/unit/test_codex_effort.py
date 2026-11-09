import pytest

from chupa.providers import CodexAdapter


def test_codex_max_effort():
    adapter = CodexAdapter.__new__(CodexAdapter)
    argv = CodexAdapter.argv(adapter, "model", "max", False)
    assert "model_reasoning_effort=high" in argv
    assert "model_reasoning_effort=max" not in argv
    with pytest.raises(KeyError):
        CodexAdapter.argv(adapter, "model", "unknown", False)
