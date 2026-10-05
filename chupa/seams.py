"""Injectable seams (CHUPA_PLAN.md section 15): engine code never calls these raw."""

import asyncio
import os
import shutil
import signal
import subprocess
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
    ) -> tuple[int, str, str]:
        if shutil.which(argv[0], path=env.get("PATH", "")) is None:
            raise ExecutableNotFound(argv[0])
        with open(stdin_path, "rb") if stdin_path else open(os.devnull, "rb") as stdin:
            proc = await asyncio.create_subprocess_exec(
                *argv,
                cwd=cwd,
                env=dict(env),
                stdin=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            try:
                async with asyncio.timeout(timeout):
                    out, err = await proc.communicate()
            except BaseException:
                # Timeout and outer cancellation alike: grandchildren must not outlive the call.
                await _kill_and_wait(proc)
                raise
        return proc.returncode or 0, out.decode(errors="replace"), err.decode(errors="replace")


async def _kill_and_wait(proc: asyncio.subprocess.Process) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    await proc.wait()


@runtime_checkable
class FileSystem(Protocol):
    def write(self, path: Path, data: bytes) -> None:
        """Atomic: temp file, fsync, rename."""
        ...

    def replace(self, src: Path, dst: Path) -> None: ...



class LocalFileSystem:
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
