---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- none

## Context
- pyproject.toml
- uv.lock
- tests/test_scaffold.py
- chupa/stages.py

## On-demand
- docs/how-chupa-works.md

## Goal / Why
A single hung test holds a ticket for the ticket's whole stuck budget. On 2026-11-05 `serve-self-upgrade`'s merge-time `uv run pytest -q` hung in the daemon-soak scenario `worker_killed_mid_run` for 41 minutes, until an operator killed the worker by hand. The suite has no per-test timeout, and chupa bounds a verification command only by `stuck_minutes` (`chupa/stages.py`, 180 minutes for that ticket).

After this change every test has a hard limit. A hung test fails in at most two minutes, the output names it, and its stack shows where it hung.

## Scope in / Scope out
- In: `pyproject.toml`:
  - add `pytest-timeout==2.5.0` to the `dev` dependency group, and update `uv.lock` with `uv lock`;
  - in `[tool.pytest.ini_options]`, add `timeout = 120` and `timeout_method = "thread"`, with a short comment giving the reasons below.

  Measured 2026-11-05 on the full suite at `-n auto` under concurrent drain load:
  - the slowest test, `tests/test_fault_injection.py::test_crash_at_every_write_point_tolerates_torn_tail_and_keeps_once_semantics[fresh]`, took 40-52s (16s serial), and at a 60s limit it timed out once;
  - 120s gives that test about twice its worst observed time;
  - `thread` ends the stuck worker even when the test is blocked outside Python bytecode (a lock or futex wait). It dumps every thread's stack, and xdist replaces the worker and reports the test by name.
- In: `tests/test_scaffold.py`: one test asserting that the `dev` group pins `pytest-timeout`, and that `[tool.pytest.ini_options]` has `timeout = 120` and `timeout_method = "thread"`.
- In: `docs/how-chupa-works.md` section 2.2: one sentence saying each test has a 120-second hard limit.
- Out: per-test `@pytest.mark.timeout` overrides (none is needed at 120s); chupa's verification timeouts in `chupa/stages.py`; the hung serve code itself (ticket `serve-self-upgrade`); host test setups.

## Scope fence
- pyproject.toml
- uv.lock
- tests/test_scaffold.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv lock --check` exits 0, and `uv.lock` resolves `pytest-timeout` 2.5.0.
2. `uv run pytest tests/test_scaffold.py` passes. The new test fails if `timeout` is not 120, `timeout_method` is not `thread`, or the `dev` group lacks `pytest-timeout`.
3. `uv run pytest -q` exits 0 with the timeout active, and no test is reported as `Timeout`.
4. `docs/how-chupa-works.md` section 2.2 states the 120-second per-test limit.

## Verification
```
uv lock --check
uv run pytest tests/test_scaffold.py
uv run pytest -q
```

## Definition of rejected
A limit above 120s or a `signal` method; a per-test override or skip added to make the suite pass; any other dependency added; any change to chupa engine code.

## Time budget
- expected: 20m
- stuck: 60m
