---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- none

## Context
- chupa/requisition.py::review_ticket
- chupa/observe.py::STEP_NAMES
- chupa/observe.py::current_step
- chupa/observe.py::recent_steps
- chupa/driver.py::Driver._run
- docs/how-chupa-works.md#10. State on disk

## On-demand
- vscode-chupa/extension.js
- tests/integration/test_requisition.py
- tests/integration/test_watch.py

## Goal / Why
`docs/how-chupa-works.md` says `engine.log` carries "stage start/end events for every stage". Requisition review is the one stage that writes none. `review_ticket` calls the provider through `llm_call` directly instead of through `Driver._run`, which is the only place that logs `stage_start` and `stage_end`. Recent Steps (the extension view and `watch`) and the in-flight current step are built only from those events, so a ticket in requisition review looks idle, and a requisition snag that ends the run leaves no trace there.

On 2026-11-11 a drain spent about 4.5 minutes on commit-lock's requisition review, then parked it `premise_failed`. The whole time, Recent Steps showed only "drain started", and `engine.log` held nothing between `engine_start` and `engine_stop` (see `evidence/drain-requisition-invisible.txt`). The operator asked why the drain had started but the ticket never showed as started.

When this ticket is done, every requisition review writes one `stage_start` and one `stage_end` to `engine.log`. Recent Steps then shows it as a named step with its own icon. This covers the drain's dispatch, author, rework and the `review` verb, because all four call `review_ticket`.

## Scope in / Scope out
- In: `chupa/requisition.py::review_ticket` logs, through `driver.log.event`, one `stage_start` before its first provider call and one `stage_end` when it returns or raises.
  - Both events carry `stem=stem` (the ticket stem, not `stem_slot`), `attempt=attempt`, `surface="requisition_review"` and `run_seq=run_seq`. `stage_end` also carries `outcome` and `calls`.
  - `outcome` is `ok` for an `approve` verdict, `timeout` for the stuck-budget snag, `infra_error` when the provider fails (a snag after a provider error, or a raised `ProviderDrought` or `ProviderCallError`, which still propagates), and `gate_failed` for any other `snag` or `rma` verdict.
  - The early snags that return before any provider call (render over headroom, missing or invalid coverage map) log no events, because no stage ran.
- In: `chupa/observe.py`: `STEP_NAMES` gains `"requisition_review": "Requisition"`, so Recent Steps rows read `Requisition start` and `Requisition end (<outcome>)` with kinds `requisition_review_start`, `requisition_review_ok` and `requisition_review_failed`. `current_step`'s after-stage map gains `"requisition_review": "Implement"`.
- In: `vscode-chupa/extension.js`: the Recent Steps icon lookup table gains the three new kinds, using the `law` codicon with the same pass and fail colors as the other stages. Without them `icons[step.kind]` is undefined and the row fails to render.
- In: the carried reproducer `tests/regress_requisition_stage_events.py` (see Regression). It is self-contained: it builds its own temp repository, config and `FakeLLM` driver, and imports nothing from `tests/`.
- Out:
  - Moving `review_ticket` onto `Driver._run`.
  - Events for any other stage, and the journal.
  - The snapshot's step `path`: a requisition row already falls through to `tickets/<stem>/ticket.md`, which is the file to open.
  - `docs/how-chupa-works.md`, which already promises events for every stage.
  - Whether re-running only requisition should consume a retry cap.

## Scope fence
- chupa/requisition.py
- chupa/observe.py
- vscode-chupa/extension.js
- tests/integration/test_requisition.py
- tests/integration/test_watch.py
- tests/regress_requisition_stage_events.py

## Acceptance criteria
1. `tests/integration/test_requisition.py`, through `review_ticket` with a `FakeLLM` and the driver's real engine log under the config's `state_dir`:
   - An `approve` reply leaves exactly two `engine.log` events with `surface` `requisition_review`, in order: `stage_start` then `stage_end` with `outcome` `ok`. Both carry the ticket `stem` (not `stem_slot`), the passed `attempt`, and `run_seq`. A run that logs none, logs only the start, or logs them reversed fails.
   - A `snag` reply with a finding ends with `stage_end` `outcome` `gate_failed`, not `ok`.
   - A coverage-map snag (missing map) logs no `requisition_review` events.
2. `tests/integration/test_watch.py`: `recent_steps` renders a `requisition_review` `stage_start` and `stage_end` as `Requisition start` and `Requisition end (gate_failed)`, with kinds `requisition_review_start` and `requisition_review_failed`, not `stage_*` and not the raw surface name.
3. `vscode-chupa/extension.js`'s `icons` table has the keys `requisition_review_start`, `requisition_review_ok` and `requisition_review_failed`.
4. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch, and prints `defect` with a non-zero exit at the merge base.
5. `./dev.py test` exits 0.

## Regression
```
uv run python tests/regress_requisition_stage_events.py
```
- carries: tests/regress_requisition_stage_events.py

## Verification
```
./dev.py test
```

## Definition of rejected
- A requisition review that calls the provider can finish without a `stage_end` in `engine.log`.
- The events are written to the journal.
- The extension derives the step name or kind in JavaScript instead of reading the snapshot's `text` and `kind`.

## Time budget
- expected: 30m
- stuck: 60m
