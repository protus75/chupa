---
priority: P0
kind: bug
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- chupa/drain.py::_Drain._run_one
- chupa/drain.py::_Drain._await_controlled
- chupa/drain.py::reofferable
- chupa/drain.py::awaiting_operator
- chupa/caps.py::failed_attempt
- chupa/caps.py::spent
- tests/integration/test_drain.py::Script
- tests/integration/test_drain.py::make_root
- tests/integration/test_drain.py::drain
- tests/regress_drain_deadline.py
- tests/unit/test_drain_reoffer.py

## Goal / Why
An unexpected exception inside one ticket's dispatch stops the whole drain instead of parking that ticket. `_Drain._run_one` awaits the dispatch task through `_await_controlled`, which returns `task.result()`, so any non-cancellation exception propagates out of `Drain.run`. It has happened twice: `context-rejects-directory` (IsADirectoryError) and `context-lint-renders` (UnicodeDecodeError, 2026-11-10). Both merged tickets fixed only the instance by tightening lint, and `context-lint-renders` left drain containment out of scope as a separate design item. This ticket is that item: no ticket owns it. After this change, an exception raised by one dispatch task ends that ticket with a single journaled `infra_error` terminal that names the exception, and the drain continues with the next ticket. The hold ships with its release through existing machinery. `infra_error` without a `rung` is re-offered without a retry draw, and it counts as a failed attempt in `caps.failed_attempt`. At the `attempts` cap, `caps.spent` returns `attempts`, `awaiting_operator` is true, and the stem is held in the Reject queue, where `chupa confirm` releases it. `caps.poison` stays unwired. Failures of the control monitor or of kill cleanup are not dispatch failures and keep propagating.

## Scope in / Scope out
- In: `chupa/drain.py`. In `_Drain._run_one`, keep a reference to the dispatch task and wrap the `_await_controlled(...)` call in `except Exception as exc`. Contain the exception only when all of these hold: `not self._stopping()`, `task.done()`, `not task.cancelled()`, and `task.exception() is exc` (the exception is the dispatch task's own). Re-raise everything else, including control-monitor failures (`monitor.result()`), kill-cleanup failures (`apply_kill` in `cleanup()`), `asyncio.CancelledError` and other `BaseException`s. In the handler, read the stem's latest `STATE_TRANSITION` from the journal. If it is not already a terminal after this run's `running` (the dispatch raised before journaling one), append `{"to": "infra_error", "stage": "dispatch", "reason": "dispatch_exception", "error": "<ExceptionType>: <message>"}` for the stem, and return the normal `infra_error` flow: no report merge, no upgrade check. If the dispatch had already journaled a terminal, append nothing, so the stem has a single terminal. The `ValueError` seam-contract checks after the await are unchanged and still raise.
- In: `tests/integration/test_drain_containment.py` (new). It subclasses or wraps `Script` from `tests/integration/test_drain.py` so the dispatch for ticket `aaa-boom` raises `IsADirectoryError`. It uses only helpers and `chupa` code that exist at base. Three tests: `test_dispatch_raises_is_contained` (the drain journals `infra_error` for `aaa-boom` with error text naming `IsADirectoryError`, dispatches the next ticket `bbb-ok` to `merged`, and exits normally with 0); `test_dispatch_raises_after_terminal_keeps_one_terminal` (the dispatch journals a terminal and then raises, and the stem has exactly one terminal transition after its `running`); `test_dispatch_raises_every_offer_reaches_reject_queue` (the dispatch raises on every offer, the stem is re-offered until the `attempts` cap, ends in the Reject queue with `caps.spent(...) == "attempts"`, and is not dispatched again).
- In: `tests/unit/test_drain_containment.py` (new). Fake-driven unit tests that run both handler branches in `chupa/drain.py` without a real dispatch: `test_handler_appends_infra_error_when_no_terminal_follows_running` and `test_handler_appends_nothing_when_terminal_follows_running`. A third test, `test_handler_reraises_non_dispatch_exception`, has a failure that is not the dispatch task's own exception (a control-monitor style failure) and asserts it propagates.
- In: `tests/integration/test_daemon_composition.py`. The `failure` case of `test_control_lifecycle_cleanup_on_exit_and_handoff` (around line 1663) drives the real drain with a dispatch raising `ValueError("stage failure")` and asserts `pytest.raises(ValueError, match="stage failure")`. Change it to assert that the drain returns normally, journals `infra_error` for `work`, and still ends its trace with `[("discovery", None), "unlock"]`. No other case in that file changes.
- In: `tests/regress_drain_containment.py` (new), the carried reproducer shaped like `tests/regress_drain_deadline.py`. It runs `tests/integration/test_drain_containment.py` with `-k raises` through pytest, so it selects the three `test_dispatch_raises_*` tests. It prints `defect` when the drain lets the exception escape (pytest exit 1) and `pass` when it is contained, and `error` for any other pytest exit.
- In: `docs/how-chupa-works.md`. Where the drain loop is described, add one sentence: a dispatch exception is journaled as an `infra_error` terminal, re-offered, and held in the Reject queue at the attempts cap. The `poison` row stays "read by nothing".
- Out: wiring `caps.poison`, a new cap or a new terminal state, exception handling in `chupa/runner.py` or `chupa/serve.py`, handling for `_run_retro`, changes to the `ValueError` seam-contract checks, changes to control-monitor or kill-cleanup error handling, and `Exception` handling that hides `KeyboardInterrupt` or cancellation.

## Scope fence
- chupa/drain.py
- tests/integration/test_drain_containment.py
- tests/unit/test_drain_containment.py
- tests/integration/test_daemon_composition.py
- tests/regress_drain_containment.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_drain_containment.py` passes. `test_dispatch_raises_is_contained` asserts the drain exits 0, the failing stem's last transition is `infra_error` with an error text naming `IsADirectoryError`, and `bbb-ok` reaches `merged`. Without the fix the exception escapes `Drain.run` and the test fails.
2. `test_dispatch_raises_after_terminal_keeps_one_terminal` in `tests/integration/test_drain_containment.py` asserts that a dispatch which journals `gate_failed` and then raises leaves exactly one terminal transition after the last `running`. A handler that always appends `infra_error` would leave two, and the test fails on that.
3. `test_dispatch_raises_every_offer_reaches_reject_queue` in `tests/integration/test_drain_containment.py` asserts that a dispatch which raises on every offer reaches `caps.spent(...) == "attempts"`, appears in `reject_queue`, and is not dispatched again in that invocation. An unreleasable hold would fail this test.
4. `./dev.py test tests/unit/test_drain_containment.py` passes. It runs both handler branches of `chupa/drain.py` (append `infra_error` when no terminal follows `running`; append nothing when one does) and the re-raise branch, so the `chupa/drain.py` floor in `test-gate.toml` holds from `tests/unit` alone. A handler that always appends fails the append-nothing test.
5. `./dev.py test tests/integration/test_kill_cli_activation.py` passes unchanged, so `test_kill_cleanup_is_atomic_and_failures_propagate` still sees control-monitor and kill-path failures (`executor-refused`, `decision`, `executor`, `dispatch`, `application`) propagate out of the drain. A handler that contains them fails that test.
6. `./dev.py test tests/integration/test_daemon_composition.py` passes with the updated `failure` exit case, which expects a normal return, an `infra_error` for `work`, and the trace ending `unlock`.
7. `uv run python tests/regress_drain_containment.py` prints `{"regression_result": "pass"}` and exits 0.
8. `./dev.py test tests/integration/test_drain.py` passes unchanged, so the `ValueError` seam-contract tests still raise.
9. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_drain_containment.py
./dev.py test tests/unit/test_drain_containment.py
./dev.py test tests/integration/test_kill_cli_activation.py
./dev.py test tests/integration/test_daemon_composition.py
./dev.py test tests/integration/test_drain.py
uv run python tests/regress_drain_containment.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the handler catches `BaseException`, or swallows `asyncio.CancelledError`;
- the handler appends a second terminal for a stem whose dispatch already journaled one;
- the change reads `config.caps.poison` or adds a cap, a terminal state, or a config knob;
- the exception is hidden: the journaled terminal lacks the exception type;
- the held stem has no release, meaning it is not in the Reject queue once `attempts` is spent;
- the change adds exception handling in `chupa/runner.py` or `chupa/serve.py`;
- a control-monitor or kill-path failure no longer propagates out of the drain.

## Time budget
- expected: 40m
- stuck: 80m

## Regression
```
uv run python tests/regress_drain_containment.py
```
- carries: tests/regress_drain_containment.py
- carries: tests/integration/test_drain_containment.py
