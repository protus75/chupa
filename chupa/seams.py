"""Injectable seams (CHUPA_PLAN.md section 15): engine code never calls these raw."""

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

Clock = Callable[[], datetime]


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
class FileSystem(Protocol):
    def write(self, path: Path, data: bytes) -> None:
        """Atomic: temp file, fsync, rename."""
        ...

    def replace(self, src: Path, dst: Path) -> None: ...

