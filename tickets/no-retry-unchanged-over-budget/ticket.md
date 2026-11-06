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
- tests/test_drain.py
- docs/how-chupa-works.md

## Goal / Why
`specs-in-package` ended `gate_failed` on `diff_budget` (43 files against 30) and its Rework split failed. The drain then re-offered the same unchanged `ticket.md` with a machine keep, spending a retry cap and a full implement attempt that could only hit the same budget again (2026-11-06).

A `diff_budget` failure is a property of the ticket, not of the attempt. After this change a stem whose last terminal is `gate_failed` with reason `diff_budget` is held, like a premise park, until its `ticket.md` changes or the operator runs `confirm`.

## Scope in / Scope out
- In: `chupa/drain.py`: the `held` set includes a stem whose last terminal is `gate_failed` with `diff_budget` in its reason and whose last run's `ticket_sha` equals the current `ticket.md` sha, reusing the `premise_parked` shape. An operator keep (`confirm`) releases it, as for a premise park.
- In: `tests/test_drain.py`:
  - new `test_diff_budget_failure_holds_until_ticket_changes`: an unchanged ticket is not re-dispatched and journals no machine `reject_verdict`;
  - the same ticket with an edited `ticket.md` is re-dispatched.
- In: `docs/how-chupa-works.md`: the sentence describing the premise park also covers a `diff_budget` failure.
- Out: other gate failures; the diff budget values; Rework.

## Scope fence
- chupa/drain.py
- tests/test_drain.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `test_diff_budget_failure_holds_until_ticket_changes` passes: an unchanged ticket's dispatches stay at one, not two.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- a gate failure other than `diff_budget` is newly held;
- the hold has no release through `ticket.md` change or `confirm`.

## Time budget
- expected: 45m
- stuck: 120m
