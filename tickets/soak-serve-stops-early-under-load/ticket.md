---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- eval/daemon_soak.py
- tests/integration/test_daemon_soak_runner.py

## Goal / Why
`tests/integration/test_daemon_soak_runner.py::test_daemon_soak_runs_production_serve` fails intermittently in the full parallel suite and passes alone. Every recorded failure is the `conflict_resolution_rungs` member raising `SoakRefused: ... serve stopped early (1)` in `_Member.until`, then `serve cleanup exited 1` from `_Member.stop`, called by the `finally` in `_member_lifetime` (excerpts in `evidence/soak-stops-early.txt`). Each flake fails an unrelated ticket's Check and costs a full retry.

Attempts 0 and 1 of this stem (2026-11-10) did not reproduce it under load: the full suite passed and 27 member runs passed. In attempt 0, an injected Git timeout inside the scripted model callback made serve log `worker_failure` and return 1. That is a plausible cause, but nothing ties it to the recorded flakes. The exit reason is lost because both refusals report only serve's exit code, and the member's `.chupa/state/engine.log` lives in a temp directory deleted after the run. This ticket does not chase the cause. It makes the next natural failure carry its own evidence: both refusals include the tail of that member's engine log, which records why serve stopped (for example a `worker_failure` event and its `error`). A later fix ticket is built from that evidence.

## Scope in / Scope out
- In: `eval/daemon_soak.py`: when `_Member.until` raises `serve stopped early (<code>)` and when `_Member.stop` raises `serve cleanup exited <code>`, append to the `SoakRefused` detail the last 20 lines of `<member root>/.chupa/state/engine.log`, introduced by `; engine.log tail:` and a newline. When the file does not exist, append `; engine.log absent` instead. Read the file once at refusal time; add no new seam or config.
- In: `tests/integration/test_daemon_soak_runner.py`: `test_soak_refusal_carries_engine_log_tail` makes a member's serve task finish early with a nonzero code after a known line is written to its engine log, and asserts that the `SoakRefused` message contains that line, ruling out a refusal that still reports only the exit code. It also asserts the `engine.log absent` wording when no log exists.
- Unaffected: the existing `pytest.raises(soak.SoakRefused, match=...)` assertions in `tests/integration/test_daemon_soak_runner.py` match on text the refusal keeps as a prefix. `tests/integration/test_daemon_soak.py` and `eval/reliability_battery.py` do not read refusal text, so they are unchanged.
- Out: finding or fixing the root cause of the flake; raising timeouts, adding retries, skips or flaky marks; `chupa/` code; other members' refusal wording; `eval/host_loop.py`'s similar `LoopRefused`.

## Scope fence
- eval/daemon_soak.py
- tests/integration/test_daemon_soak_runner.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_daemon_soak_runner.py -k test_soak_refusal_carries_engine_log_tail` exits 0. The test asserts that the known engine-log line appears in the refusal message, and that the absent-log wording appears when there is no log.
2. `./dev.py test tests/integration/test_daemon_soak_runner.py` exits 0, so the existing `match=` assertions on `SoakRefused` messages still hold.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_daemon_soak_runner.py -k test_soak_refusal_carries_engine_log_tail
./dev.py test tests/integration/test_daemon_soak_runner.py
./dev.py test
```

## Definition of rejected
A refusal still carries only the exit code; a timeout is raised, a retry added, or a test skipped or marked flaky; or any file outside the fence changes.

## Time budget
- expected: 30m
- stuck: 60m
