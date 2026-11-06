---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/caps.py

## On-demand
- chupa/drain.py
- chupa/scheduler.py
- tests/test_drain.py
- tests/test_scheduler.py
- docs/how-chupa-works.md

## Goal / Why
`specs-in-package` ended `gate_failed` on `diff_budget` (43 files against 30) and its Rework split failed. The drain then re-offered the same unchanged `ticket.md` with a machine keep, spending a retry cap and a full implement attempt that could only hit the same budget again (2026-11-06).

A `diff_budget` failure is a property of the ticket, not of the attempt. After this change a stem whose last terminal is `gate_failed` with `diff_budget` in its reason is held until its committed `ticket.md` changes, in both the drain and the daemon scheduler. The release is the same as a premise park's: a `ticket.md` content change (by hand or by Rework); `./dev.py reject <stem>` retires it.

## Scope in / Scope out
- In: `chupa/drain.py`: a new predicate `budget_parked(events, stem, ticket_sha)` beside `premise_parked`: true when the stem's last state transition is `gate_failed` with `diff_budget` among its comma-separated `reason` values and its last `running` transition's `ticket_sha` equals `ticket_sha`. `premise_parked` is unchanged.
- In: the drain's `held` set and the scheduler's `held` set (`chupa/scheduler.py`) each also include stems where `budget_parked` holds.
- In: `_settle` reports a held `diff_budget` stem with the road "split or shrink the ticket under the diff budget and commit the `ticket.md` change, or retire it with `./dev.py reject <stem>`", not the premise road.
- In: tests:
  - `tests/test_drain.py` new `test_diff_budget_failure_holds_until_ticket_changes`: after a `diff_budget` `gate_failed`, an unchanged ticket is not re-dispatched, journals no machine `reject_verdict`, and its parked road names the diff budget; after a committed `ticket.md` edit it is re-dispatched;
  - `tests/test_drain.py` new `test_other_gate_failure_is_still_reoffered`: a `gate_failed` with reason `verification` at the unchanged sha is re-dispatched;
  - `tests/test_scheduler.py` new `test_scheduler_holds_diff_budget_failure`: the scheduler does not pick an unchanged `diff_budget` stem.
- In: `docs/how-chupa-works.md`: the sentence describing the premise park also covers a `diff_budget` failure.
- Out: `confirm`/`reject` behavior (`chupa/runner.py`); other gate failures; the diff budget values; Rework.

## Scope fence
- chupa/drain.py
- chupa/scheduler.py
- tests/test_drain.py
- tests/test_scheduler.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `test_diff_budget_failure_holds_until_ticket_changes` passes: the unchanged ticket's dispatches stay at one, and the edited ticket's reach two.
2. `test_other_gate_failure_is_still_reoffered` passes: a `verification` gate failure is dispatched twice.
3. `test_scheduler_holds_diff_budget_failure` passes.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_drain.py tests/test_scheduler.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- a gate failure other than `diff_budget` is newly held;
- `premise_parked` behavior changes;
- the hold has no release through a committed `ticket.md` change.

## Time budget
- expected: 45m
- stuck: 120m
