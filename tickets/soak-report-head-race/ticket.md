---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
none

## Context
- eval/daemon_soak.py
- eval/reliability_battery.py
- chupa/git.py
- tests/test_daemon_soak.py
- tests/test_daemon_soak_runner.py
- tests/test_reliability_battery.py

## Goal / Why
Three tests fail whenever the repo's `main` gets a commit while they run, and a running drain or serve commits to `main` all the time. Both `eval/daemon_soak.py` `produce` and `eval/reliability_battery.py` `produce` stamp `produced_at_sha` with the live checkout's `HEAD` (`rev_parse(Path.cwd(), "HEAD")`) when they start, then run for 10-25s. The tests then compare that SHA to `HEAD` read again later, or compare two reports produced at different times:

- `tests/test_daemon_soak.py::test_daemon_soak_command_writes_report_only_on_green` compares `produced_at_sha` to `HEAD` read after `main` returns. It also compares the `uv run python -m eval.daemon_soak` subprocess report byte for byte with the in-process report.
- `tests/test_daemon_soak_runner.py::test_daemon_soak_is_rederivable` compares two `produce` results byte for byte.
- `tests/test_reliability_battery.py::test_reliability_battery_command_writes_only_on_green` compares the subprocess report's `produced_at_sha` to `HEAD` read after the subprocess exits.

Observed 2026-11-07 while a drain was running: the first assertion failed with `56ec0eb ≠ 871331f`, two intake commits that landed during the test. The rederivable test failed in another full run that day. Both tests pass when run alone. The engine runs `./dev.py test` in Check while it drains, so these tests can fail an unrelated ticket's Check.

After this change the tests pass while `main` advances. They still prove that each report is stamped with the `HEAD` of the checkout that produced it. The eval modules do not change: stamping the `HEAD` at start is correct.

## Scope in / Scope out
- In: in each of the three tests, a SHA comparison with a later `HEAD` read becomes a bracket check. Read `before = HEAD` before the report is produced and `after = HEAD` after it is produced. Then require that `before` is an ancestor of or equal to `produced_at_sha`, and that `produced_at_sha` is an ancestor of or equal to `after`. Check ancestry with `Git.merge_base` (`merge_base(dir, a, b) == a` means `a` is an ancestor of or equal to `b`). Add no git verb.
- In: `test_daemon_soak_command_writes_report_only_on_green` compares the subprocess report with the in-process report with `produced_at_sha` excluded, field for field. Both SHAs must fall inside one bracket that spans both runs, and the in-process SHA must be an ancestor of or equal to the subprocess SHA.
- In: `test_daemon_soak_is_rederivable` compares the two reports with `produced_at_sha` excluded, and requires that the first report's SHA is an ancestor of or equal to the second's.
- Out: `eval/daemon_soak.py`, `eval/reliability_battery.py`, `chupa/git.py`, every other assertion in these tests, and other tests.

## Scope fence
- tests/test_daemon_soak.py
- tests/test_daemon_soak_runner.py
- tests/test_reliability_battery.py

## Acceptance criteria
1. `./dev.py test tests/test_daemon_soak.py tests/test_daemon_soak_runner.py tests/test_reliability_battery.py` exits 0.
2. Each bracket check would fail if `produced_at_sha` were a commit outside `before..after`, for example the parent of `before`. An equality-only check against `after` would fail when `main` moves, and a check that drops `produced_at_sha` entirely would pass on any SHA; both are wrong.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_daemon_soak.py tests/test_daemon_soak_runner.py tests/test_reliability_battery.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a test stops checking `produced_at_sha` against the producing checkout's history;
- a test retries, sleeps, or skips to avoid the race;
- `eval/daemon_soak.py`, `eval/reliability_battery.py`, or `chupa/git.py` changes;
- an entry, spec-version, or report-bytes assertion other than the SHA is weakened or removed.

## Time budget
- expected: 20m
- stuck: 60m
