---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/drain.py::parked_blob
- docs/how-chupa-works.md#6.7
- tests/regress_requisition_park_not_attempt.py

## On-demand
- tests/integration/test_drain.py

## Goal / Why
`docs/how-chupa-works.md` section 6.7 says an Implement `premise_failed`, with the default `premise_bounce: 1`, "spends the cap and routes to the Reject queue via `premise_bounce cap spent`; only an operator `confirm` releases it." The confirm does not release it. `confirm` journals an operator `reject_verdict` keep, which resets the caps and empties the Reject queue entry. But `chupa/drain.py::parked_blob` looks only at state transitions. It still returns the blob of the last run, so the drain, serve (`chupa/scheduler.py`) and the snapshot (`chupa/observe.py`) all treat the stem as "parked until its committed ticket.md changes". The operator sees `kept <stem>`, and the ticket never runs.

On 2026-11-11 the owner confirmed `commit-lock` after two Implement give-ups that were not the ticket's fault. The output was `kept commit-lock`. The next drain still reported "commit-lock: premise_failed at implement; parked until its committed ticket.md changes" and ran nothing (see `evidence/confirm-does-not-release.txt`). It ran only after a session added a sentence to the ticket to change its blob.

When this ticket is done, an operator keep journaled after a stem's last `premise_failed` transition releases that stem's premise park, as section 6.7 says. A machine keep still does not.

## Scope in / Scope out
- In: `chupa/drain.py::parked_blob`: while scanning the stem's events, an operator keep (`signal` `reject_verdict`, `verdict` `keep`, `actor` `operator`) that comes after the last `premise_failed` transition makes it return `None`. A later `running` transition starts a new run, and a later `premise_failed` sets a new hold as today. The `gate_failed` `diff_budget` hold and every other case are unchanged.
- In: the carried reproducer `tests/regress_premise_park_keep.py` (see Regression). It is self-contained and imports nothing from `tests/`. It builds in-memory `Event`s for one stem: `running` with `ticket_sha` `B`, then `premise_failed` at stage `implement`, then an operator `reject_verdict` keep. It prints `pass` (exit 0) when `parked_blob(events, stem)` is `None`, and `defect` (exit 1) when it is `B`.
- Out:
  - `chupa/scheduler.py` and `chupa/observe.py`, which call `parked_blob` and need no change.
  - The `diff_budget` hold, Reject queue routing, caps, and the `confirm` verb's output.
  - `docs/how-chupa-works.md`, which already describes this behavior.

## Scope fence
- chupa/drain.py
- tests/unit/test_premise_park_keep.py
- tests/integration/test_drain.py
- tests/regress_premise_park_keep.py

## Acceptance criteria
1. New `tests/unit/test_premise_park_keep.py` calls `parked_blob` on in-memory `Event` lists and keeps the `test-gate.toml` unit floor for `chupa/drain.py`:
   - `running` (`B`), then `premise_failed`, then an operator keep returns `None`, not `B`.
   - The same with a keep whose `actor` is `machine` returns `B`.
   - An operator keep, then `running` (`C`), then `premise_failed` returns `C`. The old keep does not release the new hold.
   - `running` (`B`), then `premise_failed` with no keep still returns `B`.
2. `tests/integration/test_drain.py`: a stem whose Implement attempt ends `premise_failed` (routed to the Reject queue), then gets an operator keep on the unchanged committed ticket, is dispatched by the next drain. Without the keep it is not dispatched.
3. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch, and prints `defect` with a non-zero exit at the merge base.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- A machine keep releases a premise park.
- A ticket edit no longer releases a premise park.
- Code outside `chupa/drain.py` changes to special-case the keep.

## Time budget
- expected: 25m
- stuck: 50m

## Regression
```
uv run python tests/regress_premise_park_keep.py
```
- carries: tests/regress_premise_park_keep.py
