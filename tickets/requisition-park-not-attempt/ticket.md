---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/caps.py
- chupa/drain.py::_Drain._settle
- docs/how-chupa-works.md#6.4
- docs/how-chupa-works.md#6.7
- tests/regress_requisition_stage_events.py

## On-demand
- tests/integration/test_caps.py

## Goal / Why
`docs/how-chupa-works.md` section 6.7 says: "Premise park: a requisition-stage `premise_failed` draws no cap, makes no Diagnose call, and is not routed to the Reject queue. Edit the committed ticket to release it; no `confirm` is needed." The code does not do this. `caps.failed_attempt` counts every `premise_failed` terminal, including those with `stage: requisition`. After five requisition snags, `caps.spent` returns `attempts`, and `_Drain._settle` journals `reject_arrival` and routes the stem to the Reject queue. The owner then has to `confirm` a ticket that never reached Implement.

On 2026-11-10 and 11, `commit-lock` was edited and re-reviewed five times. Each requisition snag was a `premise_failed` with `stage: requisition`. After the fifth, the drain routed it to the Reject queue with "confirm commit-lock after editing, or reject commit-lock" (see `evidence/requisition-snags-hit-reject-queue.txt`). Section 6.4 says failed attempts are "`gate_failed`, `premise_failed`, `infra_error`, and `timeout` terminals" and does not exempt requisition. The two sections contradict each other, and 6.7 is the specific rule for this case.

A requisition snag costs one review call and parks the stem until its committed `ticket.md` changes. It re-runs only after a human edit, so the attempts cap bounds nothing there.

When this ticket is done, a requisition-stage `premise_failed` is not a failed attempt. A ticket parked at requisition is released by editing it, as section 6.7 says.

## Scope in / Scope out
- In: `chupa/caps.py::failed_attempt` returns `False` for a terminal with `to: premise_failed` and `stage: requisition`. Every other terminal counts as today, including `premise_failed` from any other stage or with no `stage`. The change stays inside the existing `return` expression.
- In: `docs/how-chupa-works.md` section 6.4: the sentence listing what does not count ("An `infra_error` with reason `provider_drought`, ...") adds "a requisition-stage `premise_failed`".
- In: the carried reproducer `tests/regress_requisition_park_not_attempt.py` (see Regression). It is self-contained and imports nothing from `tests/`. It builds an in-memory list of five `Event` state transitions `{"to": "premise_failed", "stage": "requisition"}` for one stem, each after a `running` transition. It passes when `caps.spent(Caps(), events, stem)` is `None` and `caps.failed_attempts(events, stem)` is 0.
- Out:
  - Stems already in the Reject queue, such as `commit-lock`. Their journaled `reject_arrival` stays, and they still need `confirm`.
  - The `premise_bounce` and `retry` caps, which already exempt requisition snags.
  - `chupa/drain.py`, which reads `caps.spent` and needs no change.

## Scope fence
- chupa/caps.py
- docs/how-chupa-works.md
- tests/integration/test_caps.py
- tests/unit/test_caps_requisition_park.py
- tests/regress_requisition_park_not_attempt.py

## Acceptance criteria
1. New `tests/unit/test_caps_requisition_park.py` uses in-memory `Event` lists only, with no disk, and keeps the `test-gate.toml` floor of 25 for `chupa/caps.py`:
   - `failed_attempt({"to": "premise_failed", "stage": "requisition"})` is `False`.
   - `failed_attempt({"to": "premise_failed", "stage": "implement"})` and `failed_attempt({"to": "premise_failed"})` are `True`.
   - Five requisition-stage `premise_failed` terminals for one stem give `failed_attempts == 0` and `spent(Caps(), events, stem)` is `None`, not `attempts`.
   - Four requisition snags plus five `gate_failed` terminals give `spent == "attempts"`, so other failures still count.
2. `tests/integration/test_caps.py::test_attempts_cap_counts_every_failed_terminal` adds `{"to": "premise_failed", "stage": "requisition"}` to the list of bodies that leave `failed_attempts(j.read(), "red") == 0`.
3. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch, and prints `defect` with a non-zero exit at the merge base.
4. `docs/how-chupa-works.md` section 6.4 names a requisition-stage `premise_failed` among the terminals that do not count.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- A `premise_failed` from any stage other than `requisition` stops counting as a failed attempt.
- A requisition-stage `premise_failed` routes a stem to the Reject queue.
- Code outside `chupa/caps.py` changes to special-case requisition snags.

## Time budget
- expected: 20m
- stuck: 45m

## Regression
```
uv run python tests/regress_requisition_park_not_attempt.py
```
- carries: tests/regress_requisition_park_not_attempt.py
