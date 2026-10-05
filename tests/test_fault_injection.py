"""Crash-point / fault-injection harness on the state layer (CHUPA_PLAN.md 19.P0, section 15 rung 2).

A scenario is run once under a recorder to enumerate its durable write points (every `os.write`
and `os.fsync` the journal issues). It is then re-run from the same starting state once per
crash point -- for writes, once per landed-byte prefix -- dying there; a restarted engine must read
the survivor (torn-tail tolerance), finish the scenario, and leave each effect executed exactly
once if its completion survived the crash, re-executed if not.
"""

import asyncio
import os
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import chupa.journal as journal_mod
from chupa.effects import Effects
from chupa.journal import EventType, Journal, JournalCorruption, _parse_segment

T0 = datetime(2026, 10, 5, tzinfo=UTC)
KEYS = ("a", "b")


class Crash(BaseException):
    """The process dying: BaseException so no engine `except Exception` can swallow it."""


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        self.now += timedelta(seconds=1)
        return self.now


class FaultyOS:
    """Stands in for `os` inside chupa.journal: counts write points, dies at the chosen one."""

    def __init__(self, crash_at: int | None = None, landed: int = 0) -> None:
        self.crash_at, self.landed = crash_at, landed
        self.points: list[tuple[str, int]] = []  # (verb, bytes) per write point, in order

    def __getattr__(self, name):
        return getattr(os, name)

    def write(self, fd: int, data: bytes) -> int:
        if self._dies(("write", len(data))):
            os.write(fd, data[: self.landed])
            raise Crash
        return os.write(fd, data)

    def fsync(self, fd: int) -> None:
        if self._dies(("fsync", 0)):
            raise Crash
        os.fsync(fd)

    def _dies(self, point: tuple[str, int]) -> bool:
        self.points.append(point)
        return len(self.points) - 1 == self.crash_at


class World:
    """External side effects; each execution's result differs, so replay is distinguishable."""

    def __init__(self) -> None:
        self.executions: dict[str, int] = {}
        self.crash_in_action: str | None = None

    def action(self, key: str):
        async def act():
            self.executions[key] = self.executions.get(key, 0) + 1
            if self.crash_in_action == key:
                raise Crash
            return {"key": key, "execution": self.executions[key]}

        return act


async def scenario(state: Path, world: World, keys=KEYS) -> dict[str, object]:
    effects = Effects(Journal(state, Clock()))
    return {k: await effects.run(world.action(k), key=k, ticket="t-1") for k in keys}


def completed(state: Path) -> dict[str, object]:
    return {e.key: e.body["result"] for e in Journal(state, Clock()).read() if e.type == EventType.EFFECT_COMPLETION}


def seed_rolled_history(state: Path) -> None:
    """Two pre-existing segments: a rolled one holding a completed `seed` effect, and the active one."""
    asyncio.run(scenario(state, World(), keys=("seed",)))
    (state / "journal" / "000002-20261005.jsonl").touch()


def assert_fully_valid(state: Path) -> None:
    """After a resumed run no segment may carry a torn or malformed line, even read as rolled."""
    for path in sorted((state / "journal").glob("*.jsonl")):
        _parse_segment(path, active=False)


def write_points(start: Path, tmp: Path, monkeypatch) -> list[tuple[str, int]]:
    probe = tmp / "probe"
    shutil.copytree(start, probe)
    faulty = FaultyOS()
    monkeypatch.setattr(journal_mod, "os", faulty)
    asyncio.run(scenario(probe, World()))
    monkeypatch.setattr(journal_mod, "os", os)
    return faulty.points


def crash_points(points: list[tuple[str, int]]):
    for i, (verb, size) in enumerate(points):
        for landed in range(size + 1) if verb == "write" else (0,):
            yield i, landed


@pytest.fixture(params=["fresh", "rolled-history"])
def start(request, tmp_path) -> Path:
    state = tmp_path / "start"
    state.mkdir()
    if request.param == "rolled-history":
        seed_rolled_history(state)
    return state


def test_scenario_has_the_expected_write_points(start, tmp_path, monkeypatch):
    points = write_points(start, tmp_path, monkeypatch)
    verbs = [v for v, _ in points]
    # Per event: write then fsync. A fresh journal also fsyncs its directory once on segment creation.
    per_events = ["write", "fsync"] * 4
    assert verbs in (per_events, ["fsync"] + per_events)


def test_crash_at_every_write_point_tolerates_torn_tail_and_keeps_once_semantics(start, tmp_path, monkeypatch):
    points = write_points(start, tmp_path, monkeypatch)
    cases = list(crash_points(points))
    assert len(cases) > 4 * 100  # byte-exhaustive over every journal record

    for n, (i, landed) in enumerate(cases):
        state = tmp_path / f"case-{n}"
        shutil.copytree(start, state)
        world = World()
        monkeypatch.setattr(journal_mod, "os", FaultyOS(crash_at=i, landed=landed))
        with pytest.raises(Crash):
            asyncio.run(scenario(state, world))
        monkeypatch.setattr(journal_mod, "os", os)
        where = f"crash at write point {i} {points[i]} with {landed} bytes landed"

        # Torn-tail tolerance: the survivor reads; a torn record is dropped, never surfaced as an event.
        survived = completed(state)
        pre_crash = dict(world.executions)

        restarted = asyncio.run(scenario(state, world, keys=("seed", *KEYS) if "seed" in survived else KEYS))
        assert_fully_valid(state)

        for key in KEYS:
            if key in survived:
                assert world.executions[key] == 1, where
                assert restarted[key] == survived[key], where
            else:
                # Completion lost: intent-only re-executes (reconcile owns that window, section 11).
                assert world.executions[key] == pre_crash.get(key, 0) + 1, where
                assert restarted[key] == {"key": key, "execution": world.executions[key]}, where
        assert "seed" not in world.executions, where  # a rolled-segment completion always replays

        events = Journal(state, Clock()).read()
        for key in KEYS:
            mine = [e.type for e in events if e.key == key]
            assert mine.count(EventType.EFFECT_COMPLETION) == 1, where
            assert mine[-1] == EventType.EFFECT_COMPLETION, where
            assert set(mine[:-1]) == {EventType.EFFECT_INTENT}, where


@pytest.mark.parametrize("key", KEYS)
def test_crash_inside_the_action_reexecutes_on_restart_and_completes_once(start, tmp_path, key):
    world = World()
    world.crash_in_action = key
    with pytest.raises(Crash):
        asyncio.run(scenario(start, world))
    world.crash_in_action = None

    result = asyncio.run(scenario(start, world))
    again = asyncio.run(scenario(start, world))

    assert world.executions[key] == 2
    assert result == again  # completed effects now replay
    assert sum(world.executions.values()) == len(KEYS) + 1
    assert_fully_valid(start)


def test_crash_after_every_effect_completes_replays_everything(start, tmp_path):
    world = World()
    first = asyncio.run(scenario(start, world))
    assert asyncio.run(scenario(start, world)) == first
    assert world.executions == {k: 1 for k in KEYS}


def test_torn_tail_in_a_rolled_segment_is_never_tolerated(tmp_path):
    seed_rolled_history(tmp_path)
    rolled = tmp_path / "journal" / "000001-20261005.jsonl"
    rolled.write_bytes(rolled.read_bytes()[:-5])
    with pytest.raises(JournalCorruption, match="rolled segment"):
        completed(tmp_path)
