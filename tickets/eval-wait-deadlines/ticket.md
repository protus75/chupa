---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- none

## Context
- eval/reliability_battery.py
- eval/daemon_soak.py
- tests/test_reliability_battery.py
- tests/test_serve.py
- tests/test_daemon_soak.py
- tests/test_daemon_soak_runner.py

## Goal / Why
`tests/test_reliability_battery.py::test_all_candidates_cooling_recovery` fails intermittently under full-suite load with `BatteryRefused: all_candidates_cooling_recovery: recovery merge offer missing`. It passes alone in under a second. On 2026-11-05 it failed `serve-self-upgrade`'s last attempt and an `implement-test-rules` attempt, and it failed a run of unmodified `main` in a scratch copy.

The cause: three eval harness waits are bounded by an event-loop turn count (`for _ in range(100000)`), not by time:
- `eval/reliability_battery.py:220`;
- `eval/reliability_battery.py:240`;
- `eval/daemon_soak.py:308` (`until`).

When every core is busy, the real git and subprocess work they wait on takes longer than 100000 turns. `tests/test_serve.py`'s `until` already uses a wall-clock deadline (`time.monotonic() + 60`). After this change all three harness waits do the same, so load cannot fail them.

## Scope in / Scope out
- In: `eval/reliability_battery.py` and `eval/daemon_soak.py`: replace each `for _ in range(100000)` bound with a `time.monotonic()` deadline of 60 seconds, as `tests/test_serve.py` `until` does.
  - Keep each loop body unchanged, including `daemon_soak`'s fake-time advance every 20 turns.
  - Keep each refusal message unchanged.
  - Add one why-comment: a turn count is not a time bound under load.
- In: `tests/test_reliability_battery.py`: a test that runs the member-1 battery with each loop turn slowed, for example by patching `_turn` to also `await asyncio.sleep(0.001)`, so that 100000 turns would not be enough under the old bound. It still observes `EXPECTED[1]`.
- Out: the engine; the battery and soak scenarios; their expected observations; any other wait.

## Scope fence
- eval/reliability_battery.py
- eval/daemon_soak.py
- tests/test_reliability_battery.py

## Acceptance criteria
1. `eval/reliability_battery.py` and `eval/daemon_soak.py` contain no `range(100000)` wait. Each of the three waits is bounded by a `time.monotonic()` deadline.
2. The slowed-turn test passes, and it fails on the old turn-count bound. Checked by `uv run pytest tests/test_reliability_battery.py`.
3. `uv run pytest tests/test_reliability_battery.py tests/test_daemon_soak.py tests/test_daemon_soak_runner.py` passes.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_reliability_battery.py tests/test_daemon_soak.py tests/test_daemon_soak_runner.py
uv run pytest -q
```

## Definition of rejected
A larger turn count instead of a time bound; a changed scenario, expected observation or refusal message; a retry or skip on the flaky test.

## Time budget
- expected: 20m
- stuck: 60m
