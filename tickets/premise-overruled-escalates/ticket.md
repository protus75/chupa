---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- none

## Context
- chupa/drain.py::parked_blob
- chupa/runner.py::drive
- chupa/drain.py::record_reoffer
- chupa/caps.py::capability
- docs/how-chupa-works.md#6. When a run fails

## On-demand
- tests/integration/test_drain.py
- tests/integration/test_caps.py

## Goal / Why
When Implement returns `premise_failed` (it claims the ticket cannot be done as written), Diagnose reads the attempt. If Diagnose disagrees and returns `retry` (the ticket is buildable and the implementer misread it), routing journals `dispatch: retry`. But `chupa/drain.py::parked_blob` holds every `premise_failed` stem until its committed `ticket.md` changes, whatever the dispatch. So the stem sits parked waiting for an edit nobody knows is needed, and the drain goes quiescent. On 2026-11-11, `journal-incremental-read` attempt 1 did exactly this (see `evidence/premise-retry-parked.txt`).

Re-running the same model as-is invites the same wrong "impossible" claim. A premise claim that Diagnose overrules is a capability signal, which the existing ladder already answers.

When this ticket is done, a `premise_failed` at Implement whose Diagnose verdict is `retry` is routed as `escalate`: one rung up through `next_rung`, re-offered without a ticket edit, and carrying Diagnose's lessons. At the top rung, or with a spent cap, it goes to the Reject queue as today.

This applies only when `premise_bounce` leaves budget after the first bounce (this repo sets `premise_bounce: 2`). Under the default of 1, the first bounce spends the cap and routes to the Reject queue without Diagnose, as today.

## Scope in / Scope out
- In: `chupa/runner.py` terminal routing: when the terminal is `premise_failed` at stage `implement` and the Diagnose verdict is `retry`, route it exactly as an `escalate` verdict (`next_rung`, `terminal["rung"]`, Reject queue when there is no rung). Spent caps still route to the Reject queue first, as today.
- In: `chupa/drain.py::parked_blob`: a `premise_failed` terminal whose `dispatch` is `escalate` holds nothing, so the drain, serve's scheduler and the status view re-offer it at its new rung. Every other `premise_failed`, including requisition-stage parks and ones with no dispatch, is held until `ticket.md` changes, as today.
- In: `chupa/drain.py::record_reoffer`: for a `premise_failed` terminal whose `dispatch` is `escalate`, draw `retry` with the terminal's `rung`, so `chupa/caps.py::capability` runs the re-offer at the new rung. Every other `premise_failed` still draws nothing.
- In: `docs/how-chupa-works.md` section 6: the 6.4 retry-cap row, the 6.6 machine-keep text, and the premise-park text describe the overruled-premise escalation and its retry draw.
- In: shakeout members that pin the old park move to the overruled-premise escalation. `tests/harness/shakeout/runner.py::_premise_false` observes the routing: one `premise_bounce` draw, `dispatch` `escalate` with the next rung (observation `overruled_premise_routed_escalate`). `tests/harness/shakeout/drain.py::_premise_park_release` observes the re-offer: a second drain runs Implement again at that rung with no `ticket.md` change and merges (observation `overruled_premise_reoffered_without_edit`). `tests/integration/test_shakeout.py` updates both observation names. Requisition-stage park-then-release stays covered by `tests/integration/test_requisition_gate.py`.
- In: new `tests/unit/test_premise_overruled.py` and the carried reproducer `tests/regress_premise_overruled_escalates.py`.
- Out:
  - Switching provider when the ladder runs out.
  - Diagnose's own verdict logic and its spec.
  - Requisition-stage premise parks, which still release on a ticket edit.

## Scope fence
- chupa/runner.py
- chupa/drain.py
- docs/how-chupa-works.md
- tests/integration/test_drain.py
- tests/integration/test_caps.py
- tests/unit/test_premise_overruled.py
- tests/regress_premise_overruled_escalates.py
- tests/harness/shakeout/runner.py
- tests/harness/shakeout/drain.py
- tests/integration/test_shakeout.py

## Acceptance criteria
1. `tests/unit/test_premise_overruled.py`, on in-memory journal events:
   - `parked_blob` returns `None` for a stem whose last terminal is `premise_failed` with `dispatch` `escalate`, not the ran ticket sha.
   - It still returns the ran sha for a `premise_failed` with `dispatch` `retry`, `reject_queue`, or none, and for a requisition-stage `premise_failed`.
   - `record_reoffer` journals a `retry` cap draw carrying the terminal's `rung` for a `premise_failed` with dispatch `escalate`, and no draw for any other `premise_failed`.
   - `runner.failure_terminal`, driven with an in-memory journal and fake context, routes an implement `premise_failed` with Diagnose verdict `retry` to dispatch `escalate` with the next rung, and to `reject_queue` when there is no next rung.
2. `tests/integration/test_drain.py` (or `tests/integration/test_caps.py`), through a drain with fake stages with the fixture's caps set to `premise_bounce: 2`: an Implement `premise_failed` with Diagnose verdict `retry` and caps left journals `dispatch` `escalate` with a `rung` one above the attempt's tier. The drain then runs the stem again at that rung without any `ticket.md` change, instead of reporting it parked.
3. The same flow at the top rung, with the fixture's caps set to `premise_bounce: 2`, journals `dispatch` `reject_queue`, not `escalate`.
4. `tests/regress_premise_overruled_escalates.py` builds its own journal events and imports nothing from `tests/`. It prints `pass` only when `parked_blob` returns `None` for an overruled premise routed `escalate`. At base, where `parked_blob` holds every `premise_failed`, it prints `defect`.
5. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch. At the merge base it prints `defect` and exits non-zero.
6. `./dev.py test` exits 0.

## Regression
```
uv run python tests/regress_premise_overruled_escalates.py
```
- carries: tests/regress_premise_overruled_escalates.py

## Verification
```
./dev.py test
```

## Definition of rejected
- An overruled premise is re-run at the same tier and effort.
- A requisition-stage park is released without a ticket edit.
- Caps or the attempts limit stop bounding the escalations.

## Time budget
- expected: 40m
- stuck: 90m
