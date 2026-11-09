"""Committed conduct preflight without filesystem or subprocess access."""

from pathlib import Path

import pytest

from chupa import hostfiles, providers
from chupa.git import GitError


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ["current", "drifted", "missing", "absent"])
async def test_stale_core(state, monkeypatch):
    repo = Path("/repo")
    monkeypatch.setattr(providers, "routed_conduct_paths", lambda config, checkout: (checkout / "CLAUDE.md",))
    current = hostfiles.render(b"project rules\n").decode()
    files = {"HEAD:CLAUDE.md": {"current": current, "drifted": current.replace("## Engine conduct", "## Old conduct", 1), "missing": "project rules\n"}.get(state)}

    class FakeGit:
        async def _run(self, checkout, verb, ref):
            assert checkout == repo and verb == "show" and ref == "HEAD:CLAUDE.md"
            if files[ref] is None:
                raise GitError(["git", "show", ref], 1, "", "missing")
            return files[ref]

    messages = await hostfiles.stale_core(repo, object(), FakeGit())
    if state == "current":
        assert messages == []
    else:
        expected = "missing" if state == "absent" else state
        assert len(messages) == 1
        assert f"CLAUDE.md: chupa core is {expected}" in messages[0]
        assert "run `chupa core`" in messages[0]
