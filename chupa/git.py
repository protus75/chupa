"""All git access (CHUPA_PLAN.md section 10, D1): argv lists, dir-pinned, through the process-exec seam."""

from collections.abc import Mapping, Sequence
from pathlib import Path

from chupa.seams import ProcessExec


class GitError(Exception):
    def __init__(self, argv: list[str], rc: int, out: str, err: str) -> None:
        super().__init__(f"{argv} exited {rc}: {err.strip()}")
        self.argv = argv
        self.rc = rc
        self.out = out
        self.err = err


class RebaseRefused(GitError):
    """The rebase failed and was aborted: the worktree sits on its own branch head. Re-run after main settles."""


def _ref(name: str) -> str:
    # A ref is a positional argv element; an option-shaped one would be parsed as a flag.
    if not name or name.startswith("-"):
        raise ValueError(f"refusing ref {name!r}: empty or option-shaped; pass a branch, tag, or sha")
    return name


class Git:
    def __init__(self, exec_: ProcessExec, *, env: Mapping[str, str], timeout: float | None) -> None:
        self._exec = exec_
        self._env = env
        self._timeout = timeout

    async def _call(self, dir: Path, *args: str) -> tuple[list[str], int, str, str]:
        argv = ["git", "-C", str(dir), *args]
        rc, out, err = await self._exec.run(argv, cwd=dir, env=self._env, timeout=self._timeout)
        return argv, rc, out, err

    async def _run(self, dir: Path, *args: str) -> str:
        argv, rc, out, err = await self._call(dir, *args)
        if rc != 0:
            raise GitError(argv, rc, out, err)
        return out

    async def init(self, dir: Path, *, branch: str) -> None:
        await self._run(dir, "init", "-b", _ref(branch))

    async def status_porcelain(self, dir: Path) -> str:
        return await self._run(dir, "status", "--porcelain")

    async def rev_parse(self, dir: Path, rev: str) -> str:
        return (await self._run(dir, "rev-parse", "--verify", _ref(rev))).strip()

    async def diff_names(self, dir: Path, base: str, stem: str) -> list[str]:
        out = await self._run(dir, "diff", "--name-only", f"{_ref(base)}...{_ref(stem)}")
        return out.splitlines()

    async def diff(self, dir: Path, base: str, stem: str) -> str:
        return await self._run(dir, "diff", f"{_ref(base)}...{_ref(stem)}")

    async def diff_stat(self, dir: Path, base: str, stem: str) -> str:
        return await self._run(dir, "diff", "--stat", f"{_ref(base)}...{_ref(stem)}")

    async def add(self, dir: Path, paths: Sequence[str]) -> None:
        await self._run(dir, "add", "--", *paths)

    async def commit(self, dir: Path, message: str, *, only: Sequence[str] = ()) -> None:
        # `only` limits the commit to those paths, whatever else is staged.
        await self._run(dir, "commit", "-m", message, *(("--only", "--", *only) if only else ()))

    async def branch(self, dir: Path, name: str, start: str) -> None:
        await self._run(dir, "branch", _ref(name), _ref(start))

    async def branch_delete(self, dir: Path, name: str) -> None:
        await self._run(dir, "branch", "-D", _ref(name))

    async def worktree_add(self, dir: Path, path: Path, branch: str, start: str) -> None:
        await self._run(dir, "worktree", "add", "-b", _ref(branch), str(path), _ref(start))

    async def worktree_remove(self, dir: Path, path: Path) -> None:
        """Cleanup is remove + prune, never rm -rf: a bare delete orphans the worktree metadata."""
        await self._run(dir, "worktree", "remove", "--force", str(path))
        await self.worktree_prune(dir)

    async def worktree_prune(self, dir: Path) -> None:
        await self._run(dir, "worktree", "prune")

    async def rebase(self, dir: Path, onto: str) -> None:
        argv, rc, out, err = await self._call(dir, "rebase", _ref(onto))
        if rc != 0:
            # Unchecked: a rebase refused before starting (e.g. dirty tree) has nothing to abort.
            await self._call(dir, "rebase", "--abort")
            raise RebaseRefused(argv, rc, out, err)

    async def restore(self, dir: Path, paths: Sequence[str], *, source: str) -> None:
        await self._run(dir, "restore", "--source", _ref(source), "--staged", "--worktree", "--", *paths)

    async def merge_squash(self, dir: Path, branch: str) -> None:
        await self._run(dir, "merge", "--squash", _ref(branch))

    async def describe(self, dir: Path) -> str:
        """Diagnostics only: derives the lockfile instance_id for an untagged dev instance (section 6)."""
        return (await self._run(dir, "describe", "--tags", "--always", "--dirty")).strip()
