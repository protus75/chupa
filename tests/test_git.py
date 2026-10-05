import asyncio
import os
import sys
import time
from pathlib import Path

import pytest

from chupa.git import Git, GitError, RebaseRefused
from chupa.seams import ExecutableNotFound, ProcessExec, SubprocessExec

ENV = {"PATH": "/usr/bin"}
REPO = Path("/repo")


class FakeExec:
    """Scripted process-exec seam: pops one (rc, out, err) per call, records argv."""

    def __init__(self, *results: tuple[int, str, str]) -> None:
        self.results = list(results)
        self.calls: list[tuple[list[str], Path, dict[str, str], float | None]] = []

    async def run(self, argv, *, cwd, env, timeout, stdin_path=None):
        self.calls.append((list(argv), cwd, dict(env), timeout))
        return self.results.pop(0) if self.results else (0, "", "")

    @property
    def argvs(self) -> list[list[str]]:
        return [c[0] for c in self.calls]


def run(coro):
    return asyncio.run(coro)


def git(*results: tuple[int, str, str]) -> tuple[Git, FakeExec]:
    exec_ = FakeExec(*results)
    return Git(exec_, env=ENV, timeout=30.0), exec_


def test_fake_satisfies_seam_protocol():
    assert isinstance(FakeExec(), ProcessExec)
    assert isinstance(SubprocessExec(), ProcessExec)


def test_env_and_timeout_are_required_keywords():
    with pytest.raises(TypeError):
        Git(FakeExec())  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        Git(FakeExec(), ENV, 30.0)  # type: ignore[misc]


def test_every_call_is_dir_pinned_and_passes_env_and_timeout():
    g, exec_ = git()
    run(g.status_porcelain(REPO))
    argv, cwd, env, timeout = exec_.calls[0]
    assert argv == ["git", "-C", "/repo", "status", "--porcelain"]
    assert cwd == REPO
    assert env == ENV
    assert timeout == 30.0


@pytest.mark.parametrize(
    "call, argv",
    [
        (lambda g: g.init(REPO, branch="main"), ["init", "-b", "main"]),
        (lambda g: g.rev_parse(REPO, "HEAD"), ["rev-parse", "--verify", "HEAD"]),
        (lambda g: g.diff(REPO, "main", "t-1"), ["diff", "main...t-1"]),
        (lambda g: g.add(REPO, ["a.py", "b c.py"]), ["add", "--", "a.py", "b c.py"]),
        (lambda g: g.commit(REPO, "msg\n\nchupa-ticket: t"), ["commit", "-m", "msg\n\nchupa-ticket: t"]),
        (lambda g: g.branch(REPO, "t-1", "main"), ["branch", "t-1", "main"]),
        (lambda g: g.branch_delete(REPO, "t-1"), ["branch", "-D", "t-1"]),
        (
            lambda g: g.worktree_add(REPO, Path("/wt/t-1"), "t-1", "main"),
            ["worktree", "add", "-b", "t-1", "/wt/t-1", "main"],
        ),
        (lambda g: g.worktree_prune(REPO), ["worktree", "prune"]),
        (lambda g: g.rebase(REPO, "main"), ["rebase", "main"]),
        (
            lambda g: g.restore(REPO, ["tickets"], source="main"),
            ["restore", "--source", "main", "--staged", "--worktree", "--", "tickets"],
        ),
        (lambda g: g.merge_squash(REPO, "t-1"), ["merge", "--squash", "t-1"]),
        (lambda g: g.describe(REPO), ["describe", "--tags", "--always", "--dirty"]),
    ],
)
def test_op_argv(call, argv):
    g, exec_ = git()
    run(call(g))
    assert exec_.argvs == [["git", "-C", "/repo", *argv]]


def test_rev_parse_and_describe_strip_output():
    g, _ = git((0, "abc123\n", ""), (0, "v1.0-3-gabc-dirty\n", ""))
    assert run(g.rev_parse(REPO, "HEAD")) == "abc123"
    assert run(g.describe(REPO)) == "v1.0-3-gabc-dirty"


def test_diff_names_parses_lines():
    g, exec_ = git((0, "a.py\nsub/b.py\n", ""))
    assert run(g.diff_names(REPO, "main", "t-1")) == ["a.py", "sub/b.py"]
    assert exec_.argvs[0][3:] == ["diff", "--name-only", "main...t-1"]


def test_diff_names_empty():
    g, _ = git((0, "", ""))
    assert run(g.diff_names(REPO, "main", "t-1")) == []


def test_nonzero_exit_raises_git_error_with_argv_and_stderr():
    g, _ = git((128, "", "fatal: bad revision\n"))
    with pytest.raises(GitError) as exc:
        run(g.rev_parse(REPO, "nope"))
    assert exc.value.rc == 128
    assert exc.value.argv == ["git", "-C", "/repo", "rev-parse", "--verify", "nope"]
    assert "bad revision" in str(exc.value)


@pytest.mark.parametrize("ref", ["-x", "--exec=evil", ""])
def test_option_shaped_or_empty_refs_are_refused_before_exec(ref):
    g, exec_ = git()
    with pytest.raises(ValueError):
        run(g.branch(REPO, ref, "main"))
    with pytest.raises(ValueError):
        run(g.rebase(REPO, ref))
    assert exec_.calls == []


def test_worktree_remove_is_remove_then_prune():
    g, exec_ = git()
    run(g.worktree_remove(REPO, Path("/wt/t-1")))
    assert exec_.argvs == [
        ["git", "-C", "/repo", "worktree", "remove", "--force", "/wt/t-1"],
        ["git", "-C", "/repo", "worktree", "prune"],
    ]


def test_refused_rebase_is_aborted_before_refusal_returns():
    g, exec_ = git((1, "", "CONFLICT (content)\n"), (0, "", ""))
    with pytest.raises(RebaseRefused) as exc:
        run(g.rebase(REPO, "main"))
    assert exec_.argvs[-1] == ["git", "-C", "/repo", "rebase", "--abort"]
    assert "CONFLICT" in str(exc.value)


def test_rebase_success_does_not_abort():
    g, exec_ = git((0, "", ""))
    run(g.rebase(REPO, "main"))
    assert len(exec_.calls) == 1


# --- real process-exec seam ---------------------------------------------------


def test_subprocess_exec_unresolvable_binary_fails_closed():
    with pytest.raises(ExecutableNotFound, match="no-such-binary-chupa"):
        run(SubprocessExec().run(["no-such-binary-chupa"], cwd=Path("."), env=dict(os.environ), timeout=5))


def test_subprocess_exec_feeds_stdin_path_and_captures(tmp_path):
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("hello")
    rc, out, err = run(
        SubprocessExec().run(
            [sys.executable, "-c", "import sys; d=sys.stdin.read(); print(d.upper()); sys.exit(3)"],
            cwd=tmp_path,
            env=dict(os.environ),
            timeout=10,
            stdin_path=prompt,
        )
    )
    assert (rc, out, err) == (3, "HELLO\n", "")


def _spawns_grandchild(marker: Path) -> list[str]:
    # The grandchild outlives a direct-child kill; only a group kill stops it writing.
    grandchild = "import sys, time; time.sleep(1.0); open(sys.argv[1], 'w').close()"
    script = (
        "import subprocess, sys, time\n"
        "subprocess.Popen([sys.executable, '-c', sys.argv[1], sys.argv[2]])\n"
        "time.sleep(30)\n"
    )
    return [sys.executable, "-c", script, grandchild, str(marker)]


def test_subprocess_exec_timeout_kills_the_process_group(tmp_path):
    marker = tmp_path / "grandchild-alive"
    started = time.monotonic()
    with pytest.raises(TimeoutError):
        run(SubprocessExec().run(_spawns_grandchild(marker), cwd=tmp_path, env=dict(os.environ), timeout=0.3))
    assert time.monotonic() - started < 5
    time.sleep(1.5)
    assert not marker.exists()


def test_subprocess_exec_outer_cancellation_kills_the_process_group(tmp_path):
    marker = tmp_path / "grandchild-alive"
    call = SubprocessExec().run(_spawns_grandchild(marker), cwd=tmp_path, env=dict(os.environ), timeout=None)
    with pytest.raises(TimeoutError):
        run(asyncio.wait_for(call, 0.3))
    time.sleep(1.5)
    assert not marker.exists()


# --- real repository ----------------------------------------------------------


def test_ticket_lifecycle_against_real_repo(tmp_path):
    env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    g = Git(SubprocessExec(), env=env, timeout=30.0)
    repo = tmp_path / "repo"
    repo.mkdir()
    wt = tmp_path / "wt" / "t-1"

    async def scenario():
        await g.init(repo, branch="main")
        (repo / "a.txt").write_text("one\n")
        (repo / "tickets").mkdir()
        (repo / "tickets" / "t-1.md").write_text("ticket\n")
        await g.add(repo, ["a.txt", "tickets"])
        await g.commit(repo, "base")
        base = await g.rev_parse(repo, "HEAD")
        assert await g.describe(repo) == base[:7]

        await g.worktree_add(repo, wt, "t-1", "main")
        (wt / "b.txt").write_text("two\n")
        (wt / "tickets" / "t-1.md").unlink()
        await g.add(wt, ["b.txt"])
        await g.commit(wt, "work")
        assert await g.diff_names(repo, "main", "t-1") == ["b.txt"]
        assert "+two" in await g.diff(repo, "main", "t-1")

        # main moves; a conflicting branch is refused and left un-rebased
        (repo / "a.txt").write_text("main\n")
        await g.add(repo, ["a.txt"])
        await g.commit(repo, "main moves")
        await g.branch(repo, "t-2", "HEAD~1")
        wt2 = tmp_path / "wt" / "t-2"
        await g.worktree_add(repo, wt2, "t-3", "t-2")
        (wt2 / "a.txt").write_text("conflict\n")
        await g.add(wt2, ["a.txt"])
        await g.commit(wt2, "clash")
        head = await g.rev_parse(wt2, "HEAD")
        with pytest.raises(RebaseRefused):
            await g.rebase(wt2, "main")
        assert await g.rev_parse(wt2, "HEAD") == head
        assert await g.status_porcelain(wt2) == ""
        await g.worktree_remove(repo, wt2)
        assert not wt2.exists()

        # restore the ticket plane, rebase, squash-merge, clean up
        assert " D tickets/t-1.md" in await g.status_porcelain(wt)
        await g.restore(wt, ["tickets"], source="main")
        assert await g.status_porcelain(wt) == ""
        await g.rebase(wt, "main")
        await g.merge_squash(repo, "t-1")
        await g.commit(repo, "chupa(t-1): work\n\nchupa-ticket: t-1")
        assert (repo / "b.txt").read_text() == "two\n"
        await g.worktree_remove(repo, wt)
        await g.branch_delete(repo, "t-1")
        assert not wt.exists()
        assert await g.status_porcelain(repo) == ""
        assert not (await g.describe(repo)).endswith("-dirty")
        (repo / "a.txt").write_text("dirty\n")
        assert (await g.describe(repo)).endswith("-dirty")

    run(scenario())
