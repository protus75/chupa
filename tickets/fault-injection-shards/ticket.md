---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- tests/test_fault_injection.py
- pyproject.toml

## Goal / Why
`./dev.py test` runs on every core (`-n auto`), but one test sets the suite's wall time. `tests/test_fault_injection.py::test_crash_at_every_write_point_tolerates_torn_tail_and_keeps_once_semantics[fresh]` took 46.2s in a full run on 2026-11-07. The whole suite took 67s of wall time but only about 170s of CPU on 20 workers. The test loops serially over every crash case (each write point times each landed-byte prefix, more than 400 cases) inside one test function, so xdist cannot spread it. `tickets/pytest-timeout` recorded the same test at 16s alone and 40-52s under load, and once over a 60s limit.

After this change the crash cases are split across separate parametrized tests that xdist runs on different workers. Every case still runs exactly once per starting state, with the same assertions.

## Scope in / Scope out
- In: `tests/test_fault_injection.py`:
  - a module constant `SHARDS = 8` and a helper `shard_cases(cases, shard)` that returns the `(n, (i, landed))` entries of `enumerate(cases)` with `n % SHARDS == shard`, in order;
  - `test_crash_at_every_write_point_tolerates_torn_tail_and_keeps_once_semantics` gains `@pytest.mark.parametrize("shard", range(SHARDS))`. It still builds the full `cases` list and keeps `assert len(cases) > 4 * 100` over that full list. It then runs the existing per-case body unchanged for `shard_cases(cases, shard)` only, keeping `case-{n}` directory names from the unfiltered index `n`. It asserts that its shard is not empty;
  - new `test_shards_partition_every_crash_case`: for a case list longer than `SHARDS`, the concatenation of `shard_cases` over every shard, sorted by `n`, equals `list(enumerate(cases))`. This rules out a dropped case, a case run in two shards, and an empty shard.
- Out: `FaultyOS`, `World`, `scenario`, `crash_points`, `write_points`, the `start` fixture and its params, every per-case assertion, the other tests in the file, `pyproject.toml` (xdist and timeout settings), and every other slow test.

## Scope fence
- tests/test_fault_injection.py

## Acceptance criteria
1. `./dev.py test tests/test_fault_injection.py` exits 0. It collects 16 `test_crash_at_every_write_point_tolerates_torn_tail_and_keeps_once_semantics` items (8 shards for each of `fresh` and `rolled-history`), not 2.
2. `test_shards_partition_every_crash_case` passes. It would fail if any case were missing, duplicated, or if any shard were empty.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_fault_injection.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a per-case assertion is removed or weakened, or the byte-exhaustive enumeration in `crash_points` changes;
- `len(cases) > 4 * 100` is asserted over one shard rather than the full list;
- `pyproject.toml` or any file other than `tests/test_fault_injection.py` changes.

## Time budget
- expected: 15m
- stuck: 45m
