---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- covgate

## Context
- pyproject.toml
- docs/how-chupa-works.md

## Goal / Why
Unit tests must be fast and must not touch the network or spawn processes, and a unit suite that grows past its time budget must be noticed and fixed. Today nothing enforces either rule. After this change chupa ships a pytest plugin, `chupa.testguard`, that a Python host enables only on its unit run (`pytest tests/unit -p chupa.testguard ...`). Its integration run leaves it off.
- While a test's setup, call or teardown runs, spawning a process or opening a network connection raises an error naming the paved road. The test fails.
- When the whole session's wall time exceeds the `[unit] budget_seconds` of `test-gate.toml`, the run exits nonzero and lists the slowest tests.

The plugin is enabled by argv, so the host's protected `config.yaml` declares the unit and integration checks with different behavior and no host pyproject setting is involved.

## Scope in / Scope out
- In: new `chupa/testguard.py`, a pytest plugin module.
  - Guarded calls: wrapper hooks around `pytest_runtest_setup`, `pytest_runtest_call` and `pytest_runtest_teardown` replace these for the duration of each phase only, and restore them afterwards:
    - `subprocess.Popen._execute_child`, which also covers `subprocess.run` and `asyncio.create_subprocess_exec`;
    - `os.system`, `os.posix_spawn`, `os.posix_spawnp`;
    - `socket.socket.connect`, `socket.socket.connect_ex`, `socket.socket.bind`, `socket.getaddrinfo`.

    Outside those phases nothing is patched, so pytest-xdist can still start its workers. `asyncio.run` keeps working, because its self-pipe uses `socket.socketpair`, which is not guarded.
  - A guarded call raises `UnitIOBlocked` (a `RuntimeError` subclass defined in the module). Its message names the call and the paved road: inject the process-exec or network seam (or a fake) instead, or move the test to the integration suite.
  - Budget:
    - In `pytest_configure`, read `test-gate.toml` at pytest's rootdir and call `chupa.covgate.parse_gate(text).budget_seconds`. Use 60 when the file is absent. Convert `chupa.covgate.GateInvalid` into `pytest.UsageError`, whose message names the file and the exception's `key`.
    - Measure the session's wall time from `pytest_sessionstart` to `pytest_sessionfinish` with a module-level clock function, defaulting to `time.monotonic`, that tests replace. Under xdist the controller receives every worker's reports and enforces the budget.
    - Per-test durations are the sum of each nodeid's setup, call and teardown report durations from `pytest_runtest_logreport`.
    - Over budget:
      - Print the elapsed time, the budget, and up to 10 nodeids with the longest durations, slowest first, each with its duration.
      - Print the paved road: speed the listed tests by faking IO and the clock; when no single test dominates, run the unit suite with `-n auto`.
      - Set `session.exitstatus` to `pytest.ExitCode.TESTS_FAILED`.
  - Disk IO is not guarded.
- In: new `tests/test_testguard.py`, driving inner runs through `pytester` (enable it with `pytest_plugins = ["pytester"]` in the test module).
- In: `docs/how-chupa-works.md` section 12: one bullet saying `chupa.testguard` is the unit-run pytest plugin, what it blocks and the budget.
- Out: blocking disk IO; any change to `chupa/covgate.py`'s grammar or behavior; `pyproject.toml`; any `config.yaml`; moving or changing existing tests; flaky-test handling.

## Scope fence
- chupa/testguard.py
- tests/test_testguard.py
- docs/how-chupa-works.md

## Acceptance criteria
1. Under `-p chupa.testguard`, each inner test below fails, and the inner output names `UnitIOBlocked` for each. A failure from `ConnectionRefusedError` or any other error does not count.
   - one calling `subprocess.run(["true"])`;
   - one using `asyncio.create_subprocess_exec("true")`;
   - one calling `os.system("true")`;
   - one calling `socket.socket().connect(("127.0.0.1", 9))` (a numeric address, so `getaddrinfo` is not reached);
   - one calling `socket.getaddrinfo("localhost", 80)`;
   - one calling `os.posix_spawn("/bin/true", ["true"], {})`;
   - one calling `os.posix_spawnp("true", ["true"], {})`;
   - one calling `socket.socket().connect_ex(("127.0.0.1", 9))`;
   - one calling `socket.socket().bind(("127.0.0.1", 0))`.

   An inner test calling `asyncio.run` on a coroutine that only sleeps passes. The guard message contains `move the test to the integration suite`. Checked by `uv run pytest tests/test_testguard.py`.
2. Setup and teardown are guarded too. An inner test whose fixture runs `subprocess.run(["true"])` before its `yield` reports an error at setup, and one whose fixture runs it after the `yield` reports an error at teardown. Each error names `UnitIOBlocked`, and the inner outcomes are `passed=1, errors=2` (pytest reports setup and teardown exceptions as errors, and the teardown-case test itself passes). A test fails if either fixture's `subprocess.run` succeeds. Checked by `uv run pytest tests/test_testguard.py`.
3. Guards are scoped to test phases. A subprocess started from an inner `conftest.py` `pytest_configure` hook succeeds. After the inner run, `subprocess.Popen._execute_child`, `os.system`, `socket.socket.connect` and `socket.getaddrinfo` are the original functions again. A test fails if any stays patched. Checked by `uv run pytest tests/test_testguard.py`.
4. Budget enforcement. With `test-gate.toml` setting `budget_seconds = 5`, run an all-passing inner session of 12 tests: one sleeps 0.2s, one sleeps 0.1s, and ten do nothing.
   - A fake clock advancing 6 seconds over the session returns `ExitCode.TESTS_FAILED`. The output lists the 0.2s test's nodeid before the 0.1s test's, and lists no more than 10 nodeids.
   - The same run with the clock advancing 4 seconds returns `ExitCode.OK`.

   A test fails if an over-budget run exits 0, an in-budget run fails, the order is wrong, or 11 or more nodeids are listed. Checked by `uv run pytest tests/test_testguard.py`.
5. Under xdist, an inner run with `-n 2`, `budget_seconds = 5` and the fake clock advancing 6 seconds returns `ExitCode.TESTS_FAILED`, and its output lists nodeids that ran in the workers. A test fails if the controller does not enforce the budget. Checked by `uv run pytest tests/test_testguard.py`.
6. With no `test-gate.toml`, the budget is 60 seconds: a fake 59-second session passes and a 61-second one fails. With `test-gate.toml` setting `[unit] budget_seconds = 0`, the inner run returns `ExitCode.USAGE_ERROR` and its output contains `unit.budget_seconds`. Checked by `uv run pytest tests/test_testguard.py`.
7. `docs/how-chupa-works.md` section 12 names `chupa.testguard`.
8. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_testguard.py
uv run pytest -q
```

## Definition of rejected
A guard stays installed outside a test phase; the plugin patches anything at import or in `pytest_configure`; the budget is read from anywhere but `test-gate.toml` via `parse_gate` (or the 60-second default); `chupa/covgate.py` behavior changes; existing tests move.

## Time budget
- expected: 45m
- stuck: 120m
