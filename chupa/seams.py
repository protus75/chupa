"""Injectable seams (CHUPA_PLAN.md section 15): engine code never calls these raw."""

import asyncio
import os
import shutil
import signal
import subprocess
import tempfile
from collections.abc import Awaitable, Callable, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

Clock = Callable[[], datetime]
# Every timed wait races its work against this to a clock-derived deadline, so tests wait zero wall-clock.
Sleep = Callable[[float], Awaitable[None]]


@runtime_checkable
class ProcessExec(Protocol):
    async def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        timeout: float | None,
        stdin_path: Path | None = None,
    ) -> tuple[int, str, str]: ...


@runtime_checkable
class GroupExec(ProcessExec, Protocol):
    """Process exec that publishes each child's process group, for a synchronous kill (`abort_current`)."""

    async def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        timeout: float | None,
        stdin_path: Path | None = None,
        on_spawn: Callable[[int], None] | None = None,
    ) -> tuple[int, str, str]: ...

    def kill_group(self, pgid: int) -> None:
        """Signal-not-reap: returns once the group is SIGKILLed; the spawner's `run` still reaps."""
        ...


class ExecutableNotFound(Exception):
    """argv[0] does not resolve: a config/setup refusal, never a raw FileNotFoundError."""

    def __init__(self, binary: str) -> None:
        super().__init__(f"executable not found: {binary!r} (install it or fix PATH in the child env)")
        self.binary = binary


class SubprocessExec:
    """Real process-exec seam: every child in its own process group, every kill a group kill."""

    async def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        timeout: float | None,
        stdin_path: Path | None = None,
        on_spawn: Callable[[int], None] | None = None,
    ) -> tuple[int, str, str]:
        if shutil.which(argv[0], path=env.get("PATH", "")) is None:
            raise ExecutableNotFound(argv[0])
        # The one unbounded caller -- the drain's self-upgrade handoff child -- streams to the operator through
        # INHERITED stdio; its out/err come back empty (section 15).
        stream = None if timeout is None else subprocess.PIPE
        with open(stdin_path, "rb") if stdin_path else open(os.devnull, "rb") as stdin:
            proc = await asyncio.create_subprocess_exec(
                *argv,
                cwd=cwd,
                env=dict(env),
                stdin=stdin,
                stdout=stream,
                stderr=stream,
                start_new_session=True,
            )
            if on_spawn is not None:
                on_spawn(proc.pid)  # start_new_session: the child's pid IS its pgid
            try:
                async with asyncio.timeout(timeout):
                    out, err = await proc.communicate()
            except BaseException:
                # Timeout and outer cancellation alike: grandchildren must not outlive the call.
                await _kill_and_wait(proc)
                raise
        return proc.returncode or 0, (out or b"").decode(errors="replace"), (err or b"").decode(errors="replace")

    def kill_group(self, pgid: int) -> None:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass


async def _kill_and_wait(proc: asyncio.subprocess.Process) -> None:
    SubprocessExec().kill_group(proc.pid)
    await proc.wait()


@runtime_checkable
class FileSystem(Protocol):
    def publish(self, path: Path, data: bytes) -> None:
        """Durable atomic publication; an existing destination is never overwritten."""
        ...

    def write(self, path: Path, data: bytes) -> None:
        """Atomic: temp file, fsync, rename."""
        ...

    def replace(self, src: Path, dst: Path) -> None: ...


class LocalFileSystem:
    def publish(self, path: Path, data: bytes) -> None:
        # Sync every ancestor edge, including directories another publisher just created.
        path.parent.mkdir(parents=True, exist_ok=True)
        for directory in (path.parent, *path.parent.parents):
            self._sync_directory(directory)
        fd, name = tempfile.mkstemp(prefix=".control-", suffix=".tmp", dir=path.parent)
        temporary = Path(name)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            # link is atomic and refuses an existing name, unlike rename/replace.
            os.link(temporary, path)
            temporary.unlink()
            self._sync_directory(path.parent)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _sync_directory(path: Path) -> None:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def write(self, path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.tmp")
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def replace(self, src: Path, dst: Path) -> None:
        os.replace(src, dst)
