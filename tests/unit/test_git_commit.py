import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from chupa import tickets
from chupa.git import Git, GitError, NothingToCommit


class FakeLock:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeExec:
    def __init__(self, *results):
        self.results = list(results)
        self.calls = []

    async def run(self, argv, *, cwd, env, timeout):
        self.calls.append(argv[3:])
        return self.results.pop(0)


def run(coro):
    return asyncio.run(coro)


def test_commit_stages_paths_and_returns_head():
    process = FakeExec((0, "", ""), (1, "", ""), (0, "", ""), (0, "new-sha\n", ""))
    git = Git(process, env={}, timeout=1, commit_lock=FakeLock())
    assert run(git.commit(Path("/repo"), "message", only=["a"])) == "new-sha"
    assert process.calls == [
        ["update-index", "--add", "--remove", "--", "a"],
        ["diff", "--cached", "--quiet", "HEAD", "--", "a"],
        ["commit", "-m", "message", "--only", "--", "a"],
        ["rev-parse", "--verify", "HEAD"],
    ]


def test_commit_unchanged_raises_without_commit():
    process = FakeExec((0, "", ""), (0, "", ""))
    with pytest.raises(NothingToCommit) as error:
        run(Git(process, env={}, timeout=1, commit_lock=FakeLock()).commit(Path("/repo"), "message", only=["a"]))
    assert isinstance(error.value, GitError)
    assert process.calls == [["update-index", "--add", "--remove", "--", "a"], ["diff", "--cached", "--quiet", "HEAD", "--", "a"]]


def test_commit_without_paths_and_squash():
    process = FakeExec((0, "", ""), (0, "first\n", ""), (0, "", ""), (0, "", ""), (0, "second\n", ""))
    git = Git(process, env={}, timeout=1, commit_lock=FakeLock())
    assert run(git.commit(Path("/repo"), "first")) == "first"
    assert run(git.merge_squash(Path("/repo"), "b", "squashed")) == "second"
    assert process.calls == [["commit", "-m", "first"], ["rev-parse", "--verify", "HEAD"], ["merge", "--squash", "b"], ["commit", "-m", "squashed"], ["rev-parse", "--verify", "HEAD"]]


def test_intake_skips_concurrent_commit(monkeypatch):
    calls = []

    class CountingLock:
        def __init__(self):
            self.entries = 0
            self.held = False

        async def __aenter__(self):
            self.entries += 1
            self.held = True

        async def __aexit__(self, *args):
            self.held = False

    class FakeGit:
        def __init__(self):
            self._commit_lock = CountingLock()

        async def status_porcelain(self, repo):
            assert self._commit_lock.held
            return "?? tickets/one/ticket.md\n"

        async def _run(self, repo, *args):
            return ""

        async def _commit(self, repo, message, *, only):
            assert self._commit_lock.held
            calls.append((message, only))
            raise NothingToCommit(["git"], 0, "", "")

    class Journal:
        def read(self):
            return []

        def append(self, *args, **kwargs):
            pytest.fail("intake must not journal a concurrent commit")

    monkeypatch.setattr(Path, "read_text", lambda self: "ticket")
    monkeypatch.setattr(tickets, "_intake_claims", lambda *args: ("ticket", []))
    monkeypatch.setattr(tickets, "validate_ticket", lambda *args: SimpleNamespace(frontmatter=SimpleNamespace(source="human", state="confirmed")))
    monkeypatch.setattr(tickets, "evidence_findings", lambda *args, **kwargs: [])
    monkeypatch.setattr(tickets, "lint_findings", lambda *args, **kwargs: [])
    git = FakeGit()
    result = run(tickets.intake(Path("/repo"), git, Journal(), SimpleNamespace(), stems=None))
    assert git._commit_lock.entries == 1 and not git._commit_lock.held
    assert result.committed == () and result.refused == {}
    assert calls == [("chupa(one): ticket", ["tickets/one/ticket.md"])]


@pytest.mark.parametrize("stems,expected", [({"one"}, ("one",)), (None, ("one", "two"))])
def test_intake_stem_scope(monkeypatch, stems, expected):
    calls = []

    class FakeGit:
        _commit_lock = FakeLock()

        async def status_porcelain(self, repo):
            return "?? tickets/one/ticket.md\n?? tickets/two/ticket.md\n"

        async def _run(self, repo, *args):
            return ""

        async def _commit(self, repo, message, *, only):
            calls.append((message, only))
            return "sha"

    class Journal:
        def read(self):
            return []

        def append(self, *args, **kwargs):
            pass

    monkeypatch.setattr(Path, "read_text", lambda self: "ticket")
    monkeypatch.setattr(tickets, "_intake_claims", lambda *args: ("ticket", []))
    monkeypatch.setattr(tickets, "validate_ticket", lambda *args: SimpleNamespace(frontmatter=SimpleNamespace(source="human", state="confirmed")))
    monkeypatch.setattr(tickets, "evidence_findings", lambda *args, **kwargs: [])
    monkeypatch.setattr(tickets, "lint_findings", lambda *args, **kwargs: [])
    result = run(tickets.intake(Path("/repo"), FakeGit(), Journal(), SimpleNamespace(), stems=stems))
    assert calls == [(f"chupa({stem}): ticket", [f"tickets/{stem}/ticket.md"]) for stem in expected]
    assert result.committed == expected
    assert "two" not in result.refused
