---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/journal.py
- docs/how-chupa-works.md#10. State on disk

## Goal / Why
`Journal.read()` re-reads and re-parses every segment on every call: 24k events in 12 segments, 0.13s per call on 2026-11-11. Callers treat it as cheap and call it in loops (storm breaker, re-report, control fold, retro, drain selection). A profiled drain start made 491 `read()` calls, and they took 157s of the run's 164s (96%; see `evidence/drain-start-journal-rereads.txt`). `append()` also re-parses the whole active segment on every write, only to check the segment's first timestamp for the roll-age rule. Both costs grow with every event ever written.

The journal is append-only: rolled segments are immutable, and the active segment only grows (`_truncate_torn_tail` removes only bytes after the last newline). So a `Journal` instance can keep what it has parsed and parse only what was appended since.

When this ticket is done, a `Journal` instance keeps its parsed events in memory. `read()` parses only complete lines appended since its last read, and `append()` reads only the active segment's first line for the roll-age check. The JSONL files stay the only source of truth: a fresh process starts with a full parse, and nothing is persisted besides the segments.

## Scope in / Scope out
- In: `chupa/journal.py`:
  - A `Journal` instance caches each rolled segment's parsed events and byte size the first time it reads that segment. Every `read()` stats each cached rolled segment. If its size changed, it re-parses that segment in full, so a torn or bad line raises `JournalCorruption` as today, never silently serving the cache. `tests/integration/test_journal_roll.py::test_roll_preserves_records_and_read_laws` pins this.
  - For the active segment it keeps the byte offset just past the last complete line it parsed, plus the line count. `read()` parses only the bytes from that offset to the last newline. An unterminated tail is left for a later read, as today. If the file is shorter than the offset, or the segment is no longer the newest, it re-parses that segment in full: the newly rolled segment is validated as immutable, then cached.
  - Other writers (another process's `Journal`, or this instance's own `append`) are seen on the next `read()` through the same offset logic. There is no in-process shortcut that could disagree with the files.
  - `read()` returns a new list on each call, so a caller that mutates its list cannot corrupt the cache. `read_segments()` keeps its contract.
  - `JournalCorruption` messages keep their file path and correct line numbers.
  - `append()`'s roll-age check reads only the first line of the active segment, not all of it.
  - `append()` still raises `JournalCorruption` before writing when the active segment holds a malformed complete line, as `tests/integration/test_journal_roll.py` requires. It checks the segment through the instance's own incremental read: a fresh instance's first `append()` parses the active segment once, and each later `append()` parses only lines it has not cached. It never calls `_parse_segment` on the whole active segment per write.
  - The new read path calls a pure helper with no I/O: given a segment's bytes from an offset, it returns the parsed events of the complete lines, the new offset and the line count, leaving an unterminated tail unparsed. It is what the unit suite covers: the coverage gate measures only `tests/unit`, and `test-gate.toml` sets `chupa/journal.py` to 20.
- In: `docs/how-chupa-works.md`, section 10: one sentence saying a `Journal` instance parses each byte of the journal once and re-reads only appended lines.
- In: new `tests/unit/test_journal_incremental.py` (the pure helper only, no disk), new `tests/integration/test_journal_incremental.py` (every disk scenario), and the carried reproducer `tests/regress_journal_incremental_read.py`.
- Out:
  - Persisted checkpoints or snapshots of folded state.
  - A database (DuckDB, SQLite) or any new dependency.
  - Callers that fold the journal (storm, box, control, retro, drain). They benefit unchanged.
  - `chupa/observe.py`'s separate raw journal reader.
  - Detecting a same-length in-place rewrite of a segment this handle already cached. Rolled segments are immutable by contract and the journal is never hand-edited, so only a size change is checked.

## Scope fence
- chupa/journal.py
- docs/how-chupa-works.md
- tests/unit/test_journal_incremental.py
- tests/integration/test_journal_incremental.py
- tests/regress_journal_incremental_read.py

## Acceptance criteria
1. `tests/unit/test_journal_incremental.py`, with in-memory bytes only: the helper parses exactly the complete lines after the offset, returns the offset just past the last newline, leaves an unterminated tail for later, and numbers lines from the passed count. Bytes ending mid-line return the tail's start as the new offset, not the end of the bytes.
2. `tests/integration/test_journal_incremental.py`, counting `chupa.journal._parse_line` calls through a monkeypatched wrapper:
   - A second `read()` with no appends in between parses 0 lines, not the whole journal again.
   - After `k` appends by a second `Journal` on the same directory, the next `read()` parses exactly `k` lines. After `k` appends by the same instance since its last read, the next `read()` parses only lines this instance has not yet parsed: exactly 1, because each `append()` already parsed the line before it. In both cases the result equals a fresh `Journal`'s `read()`, compared by value and order.
   - An `append()` by an instance that has already read the active segment's `n` lines parses at most 1 existing line, not `n`. At base it parses `n`.
3. `tests/integration/test_journal_incremental.py`, correctness:
   - An unterminated tail line is excluded. Once a later write completes it, the next `read()` includes it exactly once.
   - When the active segment rolls between two reads, the second `read()` returns every event once, in write order, with the old segment's remaining lines included.
   - Mutating the list returned by `read()` does not change the next `read()`'s result.
   - A torn final line in a rolled segment still raises `JournalCorruption` naming the path and line, including when it is appended to a rolled segment this handle has already cached.
4. `tests/integration/test_journal.py` and `tests/integration/test_journal_roll.py` pass without edits.
5. `tests/regress_journal_incremental_read.py` builds its own temporary journal of 500 events and imports nothing from `tests/`. It counts `_parse_line` calls during a second `read()` on the same `Journal` and prints `pass` only when the count is 0. At base it is 500.
6. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch. At the merge base it prints `defect` and exits non-zero.
7. `./dev.py test` exits 0.

## Regression
```
uv run python tests/regress_journal_incremental_read.py
```
- carries: tests/regress_journal_incremental_read.py

## Verification
```
./dev.py test
```

## Definition of rejected
- Any state other than the JSONL segments is persisted, or a new dependency is added.
- For segments changed only by appends, or by any change to a rolled segment's size, `read()` returns an event that a fresh `Journal`'s `read()` of the same files would not, or omits one it would return.
- A torn line or bad JSON in a rolled segment whose size changed stops raising `JournalCorruption`.

## Time budget
- expected: 45m
- stuck: 90m
