---
priority: P2
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/seams.py
- chupa/providers.py
- tests/test_providers.py

## Plan contract
- section 6
- section 9

## Goal / Why
A provider call whose stdout-line consumer raises still leaves the call's full captured stdout and stderr in its `events.jsonl` and `stderr.txt` (section 6: the attempt spool tees each call's full output). Today an exception raised by `on_stdout_line` escapes `_read_pipe` (`chupa/seams.py`) out of `ProcessExec.run`, so `CliAdapter.invoke` (`chupa/providers.py`) never writes the capture: plan-gap-13's crashed review left only `prompt.md`, and the event that crashed it was unrecoverable from the spool.

## Scope in / Scope out
- In: when the `on_stdout_line` callback raises, `ProcessExec.run` still reads the stream to EOF and waits for the child, then re-raises the callback's first exception carrying the captured stdout and stderr; `CliAdapter.invoke` writes the scrubbed `events.jsonl` and `stderr.txt` before the exception propagates.
- In: `tests/test_providers.py` adds `test_raising_line_callback_still_drains_and_reaps` and `test_consumer_error_keeps_call_capture` (a consumer that raises on its first event still leaves the full events and stderr on disk, and the call raises).
- Out: the watchdog consumer, the event-stream contract, timeouts, and group-kill behavior.

## Scope fence
- chupa/seams.py
- chupa/providers.py
- tests/test_providers.py

## Acceptance criteria
1. `uv run pytest -q tests/test_providers.py` exits 0, including `test_raising_line_callback_still_drains_and_reaps` and `test_consumer_error_keeps_call_capture`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_providers.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_providers.py -k test_consumer_error_keeps_call_capture
```
- carries: tests/test_providers.py

## Definition of rejected
Reject the branch if a consumer exception is swallowed, if a call with a raising consumer returns a result, if timeout or group-kill behavior changes, or if the regression test passes on the merge base.

## Time budget
- expected: 30m
- stuck: 90m
