---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- docs/how-chupa-works.md
- chupa/seams.py

## Goal / Why
Chupa cannot tell which test failed in a host check, because Check sees only the command's exit code. Flaky-test handling needs per-test results: which tests failed on the first run and passed on a rerun. Pytest's junit XML loses the test file and full test ID (a method becomes classname `tests.test_m.TestC`). After this change chupa ships a pytest plugin, `chupa.testreport`. A host adds `-p chupa.testreport --chupa-results PATH` to a test command, and the plugin writes one JSON file of per-test outcomes keyed by pytest node ID, such as `tests/test_m.py::TestC::test_c`. The same module gives the engine a strict reader for that file. Node IDs match coverage.py's per-test context names, which a later ticket relies on.

## Scope in / Scope out
- In: new `chupa/testreport.py`, standard library only at import time: plain hook functions, no `import pytest`, so the engine can import the reader without pytest installed.
  - `pytest_addoption`: option `--chupa-results PATH`.
  - `pytest_runtest_logreport`: per node ID, the outcome is `failed` if any phase report failed, else `skipped` if any phase was skipped, else `passed`.
  - `pytest_sessionfinish`: when the option is set and the process is not an xdist worker (`config.workerinput` absent), write `{"schema_version": 1, "tests": {<nodeid>: <outcome>}}` with keys sorted, through `LocalFileSystem().write` from `chupa/seams.py`. Under xdist the controller receives every worker's reports and writes the one file.
  - `read_results(text) -> dict[str, str]`: parse and validate that shape. `schema_version` must be the integer 1; `tests` maps nonblank strings to one of `passed`, `failed`, `skipped`; no other keys. Anything else raises `ResultsInvalid(ValueError)` naming what is wrong.
- In: new `tests/test_testreport.py`, driving inner runs through `pytester` (enable it with `pytest_plugins = ["pytester"]` in the test module).
- In: `docs/how-chupa-works.md` section 12: one bullet naming `chupa.testreport`, its option and the file format.
- Out: any change to Check, config or flake code (ticket `flake-check`); collection errors (they produce no test entry; the engine treats a failing command with no failed tests as an ordinary failure); junit.

## Scope fence
- chupa/testreport.py
- tests/test_testreport.py
- docs/how-chupa-works.md

## Acceptance criteria
1. An inner run under `-p chupa.testreport --chupa-results r.json` has four tests: one passing, one failing, one skipped, and one whose fixture raises after its `yield`. It writes `r.json` whose `tests` map gives the method test's full node ID (`test_a.py::TestC::test_m`) and outcomes `passed`, `failed`, `skipped` and `failed`. A test fails if the teardown error is recorded as `passed`, or the method's ID is the junit classname form. Checked by `uv run pytest tests/test_testreport.py`.
2. The same run with `-n 2` writes one file containing all four node IDs. A test fails if a worker's tests are missing or the file is written by a worker and so lacks the others' tests. Checked by `uv run pytest tests/test_testreport.py`.
3. Without `--chupa-results`, no file is written. Calling `pytest_sessionfinish` directly with a stub session whose config has `workerinput` set and `--chupa-results` pointing at a tmp path creates no file; a test fails if any process with `workerinput` writes the file. Checked by `uv run pytest tests/test_testreport.py`.
4. `read_results` returns the map for a valid file. It raises `ResultsInvalid` for each of these, never returning a partial map:
   - `schema_version` 2 or `"1"`;
   - an outcome `error`;
   - a blank node ID;
   - an extra top-level key.

   Checked by `uv run pytest tests/test_testreport.py`.
5. `chupa/testreport.py` has no top-level `import pytest`: `uv run python -c "import sys, chupa.testreport; assert 'pytest' not in sys.modules"` exits 0.
6. `docs/how-chupa-works.md` section 12 names `chupa.testreport`.
7. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_testreport.py
uv run python -c "import sys, chupa.testreport; assert 'pytest' not in sys.modules"
uv run pytest -q
```

## Definition of rejected
The module imports pytest at import time; the results file uses junit or another format; Check, config or flake code changes; an xdist worker writes the results file.

## Time budget
- expected: 30m
- stuck: 90m
