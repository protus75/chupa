---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- results-schema-2-reader

## Context
- chupa/testreport.py
- chupa/config.py::MechanicalCheck
- chupa/config.py::_check_references
- chupa/covgate.py::evaluate
- chupa/gates.py::GateReport
- chupa/stages.py::run_host_command
- chupa/stages.py::CommandResult
- chupa/stages.py::_check_host_results
- chupa/stages.py::check_hosts
- chupa/stages.py::Invoice
- tests/integration/test_testreport.py
- tests/unit/test_testreport_reader.py
- tests/integration/test_host_contract.py::test_host_contract_seam_inventory
- tests/integration/test_host_mechanical.py
- tests/integration/test_fixture_host.py::test_fixture_profile_loads
- docs/how-chupa-works.md#5.4 Host checks
- test-gate.toml

## On-demand
- tests/integration/test_covgate.py
- docs/host-contract.md

## Goal / Why
Check runs the host test suites but keeps only each test's outcome. How long a suite or a test took, and how covered the changed files are, is lost when the worktree is retired. A later retro cannot see slow tests or files whose coverage stays low (2026-11-08). After this change, each `checks.json` gate report for a mechanical entry with `results` records:
- the command's wall time;
- outcome counts;
- the slowest tests, bounded by the entry's configured floor and cap (defaults: at least 1 second, at most 100 tests);
- when the entry declares `coverage` and the report is readable: repository coverage and the coverage of each changed file.

## Scope in / Scope out
- In: `chupa/config.py` `MechanicalCheck` gains `slow_test_seconds: Annotated[float, Field(gt=0)] = 1.0` and `slow_test_limit: Count = 100`. Per entry, because a unit suite and an integration suite need different floors. `_check_references` refuses either key set explicitly (in `model_fields_set`) on an entry without `results`, with key `review.mechanical.<i>.<field>` and the fix `declare results`, like `coverage`.
- In: `chupa/testreport.py`.
  - The results document becomes `{"schema_version": 2, "tests": {nodeid: outcome}, "seconds": {nodeid: float}}`. A test's seconds is the sum of its setup, call and teardown `report.duration`.
  - `read_results` accepts only schema 2, requires the `seconds` keys to equal the `tests` keys and each value to be a finite float `>= 0`, and returns a frozen `Results(tests, seconds)` dataclass. Schema 1 is refused like any other version.
  - Every caller in `chupa/stages.py` reads `.tests` where it used the old dict.
  - Add `slow_tests(seconds: dict[str, float], floor: float, limit: int) -> dict[str, float]`: tests with seconds `>= floor`, highest first, ties by node ID, at most `limit`. `_check_host_results` calls it; it does not reimplement the selection.
- In: `chupa/covgate.py`.
  - Extract `percentages(report) -> tuple[float, dict[str, float]]`, the repository percent and per-file percent using the formula `evaluate` uses today: covered lines plus covered branches over statements plus branches; 100.0 when the total is 0.
  - It raises `ValueError` on the same invalid reports. `evaluate` calls it, so its results are unchanged.
- In: `chupa/gates.py`. Add strict, frozen models:
  - `TestTiming`: `seconds: float`, `passed: int`, `failed: int`, `skipped: int`, `slow: dict[str, float]`;
  - `TestCoverage`: `percent: float`, `files: dict[str, float]`.

  `GateReport` gains `timing: TestTiming | None` and `coverage: TestCoverage | None`, both default `None` with `exclude_if=lambda v: v is None` like `bug_evidence`. Existing reports therefore serialize byte-identically, and old `checks.json` files still parse.
- In: `chupa/stages.py`.
  - `run_host_command` times the command with `ctx.driver.clock()` and sets `CommandResult.seconds`, as `gather_evidence` does for Verification. A timeout or a missing executable records the elapsed time too.
  - `_check_host_results` attaches `timing` to the returned report, built from the first run's command seconds and results: outcome counts, and `slow` holding the tests with seconds `>= entry.slow_test_seconds`, highest first, at most `entry.slow_test_limit`. Ties break by node ID.
  - When `entry.coverage` is set and the report parses through `covgate.percentages`, it also attaches `coverage`: the repository percent, and `files` limited to changed files present in the report. A missing or invalid coverage report records no coverage and adds no finding; the existing flaky-classification refusal is unchanged.
  - When results are missing or invalid, no timing is attached.
- In: tests.
  - `tests/integration/test_testreport.py`:
    - Results carry `seconds` for every node ID; a schema-1 document, a seconds/tests key mismatch and a negative duration are each refused.
    - `read_results` returns `.tests` and `.seconds`.
  - `tests/integration/test_host_mechanical.py`:
    - Every fake results writer emits schema 2 with `seconds`.
    - New `test_results_record_timing`: with durations `{a: 0.5, b: 3.0, c: 1.0}`, `slow` is `{b: 3.0, c: 1.0}` in that order, not including `a` and not ascending, and the counts match the outcomes.
    - New `test_slow_tests_capped`: 150 tests at 2.0s record exactly 100 with defaults.
    - New `test_slow_test_bounds_configured`: with `slow_test_seconds: 2.5` and `slow_test_limit: 1`, durations `{a: 2.0, b: 3.0, c: 4.0}` record only `{c: 4.0}`, not the default-bounded `{c, b, a}`.
    - `test_coverage_requires_results` gains cases: `slow_test_seconds` or `slow_test_limit` set without `results` raises `ConfigError` with key `review.mechanical.0.slow_test_seconds` / `review.mechanical.0.slow_test_limit`.
    - New `test_coverage_recorded_for_changed_files`: only changed files appear in `coverage.files`, and an unreadable coverage report leaves `coverage` unset with the report verdict unchanged.
  - `tests/unit/test_testreport_reader.py`: `test_valid_results` covers schema 2 only and asserts `.tests` and `.seconds`; a schema-1 document joins the refused cases.
  - New `tests/unit/test_check_timing.py`: `slow_tests` floor, cap, descending order and node-ID tie-break; the schema-2 writer sums setup, call and teardown durations; `slow_test_seconds` / `slow_test_limit` without `results` raise `ConfigError`; a `GateReport` with and without `timing`/`coverage` dumps as specified; `run_host_command` sets `CommandResult.seconds` from a fake clock. Keep `chupa/testreport.py`, `chupa/config.py`, `chupa/gates.py` and `chupa/stages.py` at or above their `test-gate.toml` floors under the configured `unit` check. Do not lower a floor.
  - New `tests/unit/test_covgate.py`: unit tests for `percentages` and `evaluate` that keep `chupa/covgate.py` at or above its `test-gate.toml` floor under the configured `unit` check. Do not lower the floor.
  - `tests/integration/test_covgate.py`: `percentages` gives the weighted repository and per-file values that `test_aggregates_are_weighted` expects.
  - `tests/integration/test_host_contract.py::test_host_contract_seam_inventory`: its fake `driver` gains a `clock`.
  - `tests/integration/test_fixture_host.py::test_fixture_profile_loads`: its exact `MechanicalCheck.model_dump()` assertion gains `"slow_test_seconds": 1.0` and `"slow_test_limit": 100`. Do not exclude the new fields from the dump to keep the old assertion.
- In: docs.
  - `docs/how-chupa-works.md` section 5.4 describes the recorded timing and coverage and their bounds; the `chupa.testreport` bullet in section 12 describes schema 2.
  - `docs/host-contract.md`'s `results` paragraph names schema 2, the recorded timing and coverage, and the two keys. The `MechanicalCheck` row in `config-fields` gains `slow_test_seconds: 1.0` and `slow_test_limit: 100` defaults.
- Out: the retro reading these fields, retro config, the `testguard` budget, coverage gating, and merge-time host checks beyond the `seconds` field.

## Scope fence
- chupa/config.py
- chupa/testreport.py
- chupa/covgate.py
- chupa/gates.py
- chupa/stages.py
- tests/integration/test_testreport.py
- tests/integration/test_host_mechanical.py
- tests/integration/test_covgate.py
- tests/unit/test_covgate.py
- tests/unit/test_testreport_reader.py
- tests/unit/test_check_timing.py
- tests/integration/test_host_contract.py
- tests/integration/test_fixture_host.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_testreport.py tests/integration/test_covgate.py` exits 0; a schema-1 results document raises `ResultsInvalid`, not a silent parse.
2. `./dev.py test tests/integration/test_host_mechanical.py` exits 0, including `test_results_record_timing`, `test_slow_tests_capped`, `test_slow_test_bounds_configured`, `test_coverage_requires_results` and `test_coverage_recorded_for_changed_files`. They rule out recording sub-second tests, more than 100 tests, ignored config bounds, ascending order, and unchanged files.
3. A `GateReport` without timing or coverage dumps the same JSON as before; `./dev.py test tests/integration/test_gates.py` exits 0.
4. `docs/how-chupa-works.md` section 5.4 and `docs/host-contract.md` name `slow_test_seconds` and `slow_test_limit` with their defaults; `./dev.py test tests/integration/test_host_contract.py` exits 0.
5. `./dev.py test` exits 0.
6. `./dev.py test tests/unit/test_covgate.py` exits 0; it fails if `percentages` returns an unweighted mean of file percents instead of covered over total, or not 100.0 for an empty report.

## Verification
```
./dev.py test tests/unit
./dev.py test tests/integration/test_testreport.py tests/integration/test_covgate.py tests/unit/test_covgate.py
./dev.py test tests/integration/test_host_mechanical.py tests/integration/test_gates.py tests/integration/test_host_contract.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- an unreadable coverage report changes a gate verdict;
- schema-1 results are still accepted;
- every test duration is recorded instead of the bounded slow list;
- the slow-test floor or cap is hard-coded instead of read from the entry.

## Time budget
- expected: 60m
- stuck: 150m
