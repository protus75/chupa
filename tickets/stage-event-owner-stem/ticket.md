---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- requisition-events-owner-stem

## Context
- chupa/requisition.py::review_ticket
- chupa/stages.py::run_stages
- chupa/runner.py::drive
- docs/how-chupa-works.md#10. State on disk

## On-demand
- chupa/driver.py
- tests/unit/test_requisition_stage_events.py

## Goal / Why
`stage_start` and `stage_end` reach `engine.log` from four places, and each one writes `driver.log.event` by hand: `Driver._run`, `review_ticket` in `chupa/requisition.py`, Check in `chupa/stages.py`, and merge in `chupa/runner.py`. Nothing keeps a writer from logging a stage while another stage is already open on the same driver. Ticket `requisition-stage-events` did exactly that. Requisition reviews nested inside the running `author` and `rework` stages logged their own stage events under each candidate's stem, so Recent Steps showed Requisition steps for stems that were never tickets (fixed for that one site by `requisition-events-owner-stem`). The next stage or gate that adds its own events by hand can repeat the mistake.

When this ticket is done, stage events have one writer: a `Driver` context manager. It refuses to open a stage while another is open on the same driver, so a nested stage event fails loudly in tests instead of reaching Recent Steps. A test also rules out any other writer.

## Scope in / Scope out
- In: `chupa/driver.py` gains `Driver.stage(*, stem, attempt, surface, **start_fields)`, a context manager:
  - On entry it raises `ValueError` naming the open stage's `stem` and `surface` if a stage is already open on this driver. Otherwise it marks the stage open and logs `stage_start` with `stem`, `attempt`, `surface` and `start_fields`.
  - The value it yields has `end(outcome, **end_fields)`, which logs `stage_end` with the same `stem`, `attempt` and `surface`, plus `outcome` and `end_fields`.
  - On exit it clears the open mark on every path, including exceptions and cancellation. It never writes a `stage_end` itself, because an aborted stage writes none today (`tests/integration/test_kill_executor_abort.py` pins this).
- In: `Driver._run`, `review_ticket`, Check in `chupa/stages.py` and merge in `chupa/runner.py` log stage events only through `Driver.stage`. Every event keeps exactly its current fields and values, so `chupa/observe.py` and the existing event tests stay unchanged.
- In: `docs/how-chupa-works.md`, section 10, the `engine.log` row says stages do not nest on one driver and a gate run inside a stage logs under that stage.
- In: new `tests/unit/test_stage_events_seam.py`.
- Out:
  - Changing any event's fields or the surfaces that log them.
  - Logging `stage_end` for aborted stages.
  - `chupa/observe.py` and the extension.

## Scope fence
- chupa/driver.py
- chupa/requisition.py
- chupa/stages.py
- chupa/runner.py
- docs/how-chupa-works.md
- tests/unit/test_stage_events_seam.py
- tests/unit/test_requisition_stage_events.py

## Acceptance criteria
1. `tests/unit/test_stage_events_seam.py` parses every `chupa/*.py` file with `ast` and asserts that the only call passing the literal `"stage_start"` or `"stage_end"` as an event name is inside `chupa/driver.py`'s `Driver.stage`. It fails at base, where `chupa/requisition.py`, `chupa/stages.py` and `chupa/runner.py` hold such calls.
2. `tests/unit/test_stage_events_seam.py`, with a `Driver` whose log records events:
   - Entering `Driver.stage` while another `Driver.stage` is open raises `ValueError`, and no second `stage_start` is logged.
   - After a `Driver.stage` body raises (and after one is cancelled), a new `Driver.stage` opens without error, and no `stage_end` was logged for the one that raised. A stuck open mark would block every later stage.
   - `end("ok", calls=2)` logs a `stage_end` with `stem`, `attempt`, `surface`, `outcome` `ok` and `calls` `2`.
3. `tests/integration/test_driver.py`, `tests/integration/test_step_events.py`, `tests/integration/test_kill_executor_abort.py`, `tests/integration/test_requisition.py` and `tests/integration/test_watch.py` pass unchanged. They pin the current event fields and the no-`stage_end`-on-abort behavior.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- Any event field, value, or the set of surfaces that log stage events changes.
- The seam logs `stage_end` for an aborted or cancelled stage.
- Nested stages are allowed by a flag or parameter instead of being refused.

## Time budget
- expected: 45m
- stuck: 90m
