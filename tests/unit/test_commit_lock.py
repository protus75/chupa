import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from chupa import lockfile
from chupa.git import Git
from chupa.lockfile import CommitLock, CommitLockTimeout, LockHeld


class Memory:
    O_RDWR = 1
    O_CREAT = 2
    LOCK_EX = 1
    LOCK_NB = 2

    def __init__(self):
        self.now = datetime(2026, 1, 1, tzinfo=UTC)
        self.data = json.dumps({"pid": 729}).encode()
        self.holder = 99
        self.next_fd = 1
        self.calls = []
        self.on_sleep = lambda: None

    def clock(self):
        return self.now

    async def sleep(self, seconds):
        self.now += timedelta(seconds=seconds)
        self.on_sleep()
        await asyncio.sleep(0)

    def open(self, *args):
        self.calls.append("open")
        fd = self.next_fd
        self.next_fd += 1
        return fd

    def flock(self, fd, flags):
        self.calls.append("flock")
        if self.holder is not None:
            raise BlockingIOError
        self.holder = fd

    def close(self, fd):
        if self.holder == fd:
            self.holder = None

    def pread(self, fd, length, offset):
        return self.data

    def pwrite(self, fd, data, offset):
        self.data = data

    def ftruncate(self, fd, length):
        self.data = b""

    def fsync(self, fd):
        pass

    def getpid(self):
        return 123


@pytest.fixture
def memory(monkeypatch):
    fake = Memory()
    monkeypatch.setattr(lockfile, "os", fake)
    monkeypatch.setattr(lockfile, "fcntl", fake)
    monkeypatch.setattr(Path, "mkdir", lambda *args, **kwargs: None)
    return fake


def test_wait_and_identity_clear(memory):
    lock = CommitLock(Path("/state"), clock=memory.clock, sleep=memory.sleep)
    assert memory.calls == []
    memory.on_sleep = lambda: setattr(memory, "holder", None)

    async def run():
        async with lock:
            assert memory.now > datetime(2026, 1, 1, tzinfo=UTC)
            assert json.loads(memory.data)["pid"] == 123
            assert "instance_id" not in json.loads(memory.data)
        assert memory.data == b""

    asyncio.run(run())


def test_timeout_names_holder(memory):
    lock = CommitLock(Path("/state"), clock=memory.clock, sleep=memory.sleep)

    async def run():
        with pytest.raises(CommitLockTimeout) as exc:
            async with lock:
                pytest.fail("acquired a held lock")
        assert not isinstance(exc.value, LockHeld)
        assert "729" in str(exc.value) and "retry" in str(exc.value)
        assert memory.now == datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=60)

    asyncio.run(run())


def test_tasks_wait_and_reentry_fails(memory):
    memory.holder = None
    lock = CommitLock(Path("/state"), clock=memory.clock, sleep=memory.sleep)

    async def run():
        async with lock:
            with pytest.raises(RuntimeError):
                async with lock:
                    pass
            entered = asyncio.Event()

            async def contender():
                async with lock:
                    entered.set()

            task = asyncio.create_task(contender())
            await asyncio.sleep(0)
            assert not entered.is_set()
        await task
        assert entered.is_set()

    asyncio.run(run())


def test_git_holds_one_lock_per_write():
    class Lock:
        enters = 0
        active = False

        async def __aenter__(self):
            self.enters += 1
            self.active = True

        async def __aexit__(self, *args):
            self.active = False

    lock = Lock()
    calls = []

    class Exec:
        async def run(self, argv, **kwargs):
            calls.append((argv[3], lock.enters, lock.active))
            return (1 if argv[3] == "diff" else 0), "sha\n", ""

    git = Git(Exec(), env={}, timeout=1, commit_lock=lock)

    async def run():
        await git.commit(Path("/repo"), "x", only=["a"])
        await git.merge_squash(Path("/repo"), "branch", "x")
        await git.add(Path("/repo"), ["a"])
        await git.restore(Path("/repo"), ["a"], source="HEAD")
        lock.active = True
        await git.rev_parse(Path("/repo"), "HEAD")
        await git.rebase(Path("/repo"), "branch")

    asyncio.run(run())
    assert calls == [
        ("update-index", 1, True),
        ("diff", 1, True),
        ("commit", 1, True),
        ("rev-parse", 1, True),
        ("merge", 2, True),
        ("commit", 2, True),
        ("rev-parse", 2, True),
        ("add", 3, True),
        ("restore", 4, True),
        ("rev-parse", 4, True),
        ("rebase", 4, True),
    ]


def test_cli_handles_timeout(monkeypatch, capsys):
    from chupa import __main__

    monkeypatch.setattr(__main__, "load_config", lambda *args, **kwargs: (_ for _ in ()).throw(CommitLockTimeout(Path("/state/commit.lock"), {"pid": 729})))
    assert __main__.main(["status"], cwd=Path("/repo"), env={}, clock=lambda: datetime.now(UTC)) == 2
    output = capsys.readouterr()
    assert "729" in output.err and "Traceback" not in output.err
