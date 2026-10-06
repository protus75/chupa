"""Direct proofs for the dormant scheduler and watcher."""

import ast
import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path

from chupa.scheduler import PendingTicket, Scheduler
from chupa.watcher import TicketWatcher


class Journal:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, str], str | None]] = []

    def append(self, type: str, body: dict[str, str], *, ticket: str | None = None, key: str | None = None) -> None:
        self.events.append((type, body, ticket))


class Sleep:
    def __init__(self) -> None:
        self.waiters: list[asyncio.Future[None]] = []

    async def __call__(self, seconds: float) -> None:
        waiter: asyncio.Future[None] = asyncio.get_running_loop().create_future()
        self.waiters.append(waiter)
        await waiter

    def release(self, n: int = 0) -> None:
        self.waiters[n].set_result(None)


def ticket(stem: str, priority: str, authored_at: str) -> PendingTicket:
    return PendingTicket(stem, priority, authored_at)


def test_single_flight_defers_new_p0_until_active_ticket_finishes():
    async def exercise() -> None:
        started = asyncio.Event()
        finish = asyncio.Event()
        runs: list[str] = []

        async def dispatch(item: PendingTicket) -> None:
            runs.append(item.stem)
            started.set()
            await finish.wait()

        scheduler = Scheduler(dispatch)
        scheduler.consider(ticket("old-p2", "P2", "2026-01-01T00:00:00+00:00"))
        active = asyncio.create_task(scheduler.dispatch_one())
        await started.wait()
        scheduler.consider(ticket("new-p0", "P0", "2026-01-02T00:00:00+00:00"))

        assert scheduler.active is not None and scheduler.active.stem == "old-p2"
        assert await scheduler.dispatch_one() is None
        assert runs == ["old-p2"]
        finish.set()
        await active
        assert (await scheduler.dispatch_one()).stem == "new-p0"
        assert runs == ["old-p2", "new-p0"]

    asyncio.run(exercise())


def test_watcher_debounces_and_reorders_pending_by_priority_age_then_stem():
    async def exercise() -> None:
        async def dispatch(_: PendingTicket) -> None:
            return None

        sleep = Sleep()
        journal = Journal()
        scheduler = Scheduler(dispatch)

        def parse(stem: str, text: str) -> PendingTicket:
            priority, authored_at = text.split(",")
            return ticket(stem, priority, authored_at)

        watcher = TicketWatcher(scheduler, parse, journal, sleep, debounce=0.1)
        half_written = asyncio.create_task(watcher.changed("first", lambda: "P2,broken"))
        await asyncio.sleep(0)
        complete = asyncio.create_task(watcher.changed("first", lambda: "P2,2026-01-01T00:00:00+00:00"))
        await asyncio.sleep(0)
        sleep.release(0)
        assert await half_written is False
        sleep.release(1)
        assert await complete is True

        for stem, contents in (("z-old", "P2,2026-01-01T00:00:00+00:00"),
                               ("a-old", "P2,2026-01-01T00:00:00+00:00"),
                               ("urgent", "P0,2026-01-03T00:00:00+00:00")):
            changed = asyncio.create_task(watcher.changed(stem, lambda contents=contents: contents))
            await asyncio.sleep(0)
            sleep.release(-1)
            assert await changed is True

        assert [item.stem for item in scheduler.pending] == ["urgent", "a-old", "first", "z-old"]
        assert journal.events == []

    asyncio.run(exercise())


def test_malformed_existing_ticket_keeps_position_new_ticket_is_ineligible_and_failures_journal():
    async def exercise() -> None:
        async def dispatch(_: PendingTicket) -> None:
            return None

        journal = Journal()

        def parse(stem: str, text: str) -> PendingTicket:
            if text == "bad":
                raise ValueError("frontmatter is incomplete")
            return ticket(stem, "P2", text)

        scheduler = Scheduler(dispatch)
        watcher = TicketWatcher(scheduler, parse, journal, lambda _: asyncio.sleep(0), debounce=0)
        assert await watcher.changed("existing", lambda: "2026-01-01T00:00:00+00:00")
        assert not await watcher.changed("existing", lambda: "bad")
        assert not await watcher.changed("new-invalid", lambda: "bad")

        assert [item.stem for item in scheduler.pending] == ["existing"]
        assert [(body["signal"], stem) for _, body, stem in journal.events] == [
            ("ticket_parse_failed", "existing"), ("ticket_parse_failed", "new-invalid")
        ]

    asyncio.run(exercise())


def _imports(source: str) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names if alias.name.startswith("chupa."))
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            if node.module == "chupa":
                found.update(f"chupa.{alias.name}" for alias in node.names)
            elif node.module.startswith("chupa."):
                found.add(node.module)
    return found


def import_closure(sources: dict[str, str], root: str = "chupa.__main__") -> set[str]:
    seen: set[str] = set()
    pending = [root]
    while pending:
        module = pending.pop()
        if module in seen:
            continue
        seen.add(module)
        pending.extend(_imports(sources.get(module, "")) - seen)
    return seen


def test_scheduler_modules_are_outside_production_import_closure_and_both_import_forms_are_detected():
    root = Path(__file__).parents[1]
    sources = {f"chupa.{path.stem}": path.read_text() for path in (root / "chupa").glob("*.py")}
    sources["chupa.__main__"] = (root / "chupa" / "__main__.py").read_text()

    closure = import_closure(sources)
    assert "chupa.scheduler" not in closure
    assert "chupa.watcher" not in closure
    assert "chupa.scheduler" in import_closure({"chupa.__main__": "import chupa.scheduler"})
    assert "chupa.watcher" in import_closure({"chupa.__main__": "from chupa import watcher"})
