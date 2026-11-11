import json
from datetime import UTC, datetime

import pytest

from chupa import journal as module
from chupa.journal import Journal, JournalCorruption

NOW = datetime(2026, 8, 4, 12, tzinfo=UTC)


def clock():
    return NOW


def append(journal, n):
    return journal.append("timer_armed", {"n": n})


def test_incremental_reads_and_appends(tmp_path, monkeypatch):
    j = Journal(tmp_path, clock)
    for n in range(4):
        append(j, n)
    expected = j.read()
    calls = []
    parse = module._parse_line

    def counted(path, lineno, raw):
        calls.append((path, lineno))
        return parse(path, lineno, raw)

    monkeypatch.setattr(module, "_parse_line", counted)
    assert j.read() == expected
    assert len(calls) == 0
    other = Journal(tmp_path, clock)
    for n in range(4, 7):
        append(other, n)
    calls.clear()
    actual = j.read()
    assert len(calls) == 3
    assert actual == Journal(tmp_path, clock).read()
    calls.clear()
    append(j, 7)
    assert len(calls) <= 1
    for n in (8, 9):
        append(j, n)
    calls.clear()
    actual = j.read()
    assert len(calls) == 1
    assert actual == Journal(tmp_path, clock).read()
    actual.clear()
    assert j.read() == Journal(tmp_path, clock).read()


def test_tail_completion_and_roll(tmp_path, monkeypatch):
    j = Journal(tmp_path, clock)
    first = append(j, 1)
    path = next(j.dir.glob("*.jsonl"))
    raw = json.dumps({"v": 1, "type": "timer_armed", "ts": NOW.isoformat(), "ticket": None, "key": None, "body": {"n": 2}}).encode()
    with path.open("ab") as f:
        f.write(raw[:20])
    assert j.read() == [first]
    with path.open("ab") as f:
        f.write(raw[20:] + b"\n")
    assert [e.body["n"] for e in j.read()] == [1, 2]
    append(j, 3)
    monkeypatch.setattr(module, "ROLL_BYTES", 1)
    fourth = append(Journal(tmp_path, clock), 4)
    assert j.read() == Journal(tmp_path, clock).read()
    assert [e.body["n"] for e in j.read()] == [1, 2, 3, 4]
    assert j.read()[-1] == fourth


def test_cached_rolled_corruption_and_active_only_append(tmp_path, monkeypatch):
    j = Journal(tmp_path, clock)
    append(j, 1)
    monkeypatch.setattr(module, "ROLL_BYTES", 1)
    append(j, 2)
    assert len(j.read()) == 2
    rolled = sorted(j.dir.glob("*.jsonl"))[0]
    with rolled.open("ab") as f:
        f.write(b"partial")
    with pytest.raises(JournalCorruption, match=r"000001-20260804.jsonl.*line 2"):
        j.read()
    calls = []
    parse = module._parse_line

    def counted(path, lineno, raw):
        calls.append(path)
        return parse(path, lineno, raw)

    monkeypatch.setattr(module, "_parse_line", counted)
    append(Journal(tmp_path, clock), 3)
    assert calls and rolled not in calls
