"""Single-writer lockfile: one advisory flock per checkout.

Correctness comes from `flock` alone: the kernel frees the lock when the holder
dies, so there is no liveness protocol and no stale-pid reclaim. The recorded
identity is diagnostics for the refusal message, never read for a decision.
"""

import asyncio
import fcntl
import json
import os
import socket
from pathlib import Path
from typing import Any

from chupa.journal import render_ts
from chupa.seams import Clock, Sleep


class LockHeld(Exception):
    """Another process holds the checkout's writer lock."""

    def __init__(self, path: Path, holder: dict[str, Any] | None) -> None:
        who = json.dumps(holder) if holder else "unknown holder (identity not yet written)"
        super().__init__(f"{path} is held by {who}; wait for that process to exit or stop it -- the kernel frees the lock when it dies, so never delete the lockfile")
        self.path = path
        self.holder = holder


class Lockfile:
    def __init__(self, state_dir: Path, *, instance_id: str, clock: Clock) -> None:
        self.state_dir = Path(state_dir)
        self.path = self.state_dir / "chupa.lock"
        self._instance_id = instance_id
        self._clock = clock
        self._fd: int | None = None

    @property
    def held(self) -> bool:
        return self._fd is not None

    def acquire(self) -> None:
        """Take the lock before any write; refuse (LockHeld) if another open holds it."""
        if self._fd is not None:
            raise RuntimeError(f"{self.path} is already held by this Lockfile; release it first")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        # os.open fds are non-inheritable, so a spawned child (the self-upgrade handoff) cannot pin the lock.
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            holder = _read_holder(fd)
            os.close(fd)
            raise LockHeld(self.path, holder) from None
        except BaseException:
            os.close(fd)
            raise
        identity = {
            "instance_id": self._instance_id,
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "state_dir": str(self.state_dir),
            "started_at": render_ts(self._clock()),
        }
        try:
            os.ftruncate(fd, 0)
            os.pwrite(fd, json.dumps(identity).encode(), 0)
            os.fsync(fd)
        except BaseException:
            os.close(fd)
            raise
        self._fd = fd

    def release(self) -> None:
        """Free the lock; the drain's self-upgrade handoff calls this before spawning its child."""
        if self._fd is None:
            raise RuntimeError(f"{self.path} is not held by this Lockfile; nothing to release")
        fd, self._fd = self._fd, None
        os.close(fd)


def _read_holder(fd: int) -> dict[str, Any] | None:
    # The holder writes its identity after taking the lock; a contender can race that write.
    try:
        holder = json.loads(os.pread(fd, 65536, 0) or b"null")
    except ValueError:
        return None
    return holder if isinstance(holder, dict) else None


COMMIT_LOCK_WAIT_S = 60


class CommitLockTimeout(Exception):
    def __init__(self, path: Path, holder: dict[str, Any] | None) -> None:
        who = json.dumps(holder) if holder else "unknown holder (identity not yet written)"
        super().__init__(f"{path} is held by {who}; retry once that process finishes its commit; never delete the lockfile")


class CommitLock:
    def __init__(self, state_dir: Path, *, clock: Clock, sleep: Sleep) -> None:
        self.state_dir = Path(state_dir)
        self.path = self.state_dir / "commit.lock"
        self._clock, self._sleep = clock, sleep
        self._owner = None
        self._fd = None

    async def __aenter__(self):
        task = asyncio.current_task()
        if self._owner is task:
            raise RuntimeError(f"{self.path} is already held by this task")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        deadline = self._clock().timestamp() + COMMIT_LOCK_WAIT_S
        try:
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    remaining = deadline - self._clock().timestamp()
                    if remaining <= 0:
                        raise CommitLockTimeout(self.path, _read_holder(fd)) from None
                    await self._sleep(min(0.1, remaining))
            identity = {"pid": os.getpid(), "host": socket.gethostname(), "state_dir": str(self.state_dir), "started_at": render_ts(self._clock())}
            os.ftruncate(fd, 0)
            os.pwrite(fd, json.dumps(identity).encode(), 0)
            os.fsync(fd)
        except BaseException:
            os.close(fd)
            raise
        self._owner, self._fd = task, fd
        return self

    async def __aexit__(self, exc_type, exc, tb):
        fd, self._fd, self._owner = self._fd, None, None
        try:
            os.ftruncate(fd, 0)
        finally:
            os.close(fd)
