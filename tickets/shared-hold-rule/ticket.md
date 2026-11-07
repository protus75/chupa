---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
none

## Context
- chupa/drain.py
- chupa/scheduler.py
- chupa/observe.py
- chupa/status.py
- tests/test_drain.py
- tests/test_scheduler.py
- tests/test_watch.py
- docs/how-chupa-works.md

## Goal / Why
On 2026-11-07 the extension showed `box-view` as "ready" in the queue while the drain held it: its last run ended `premise_failed` at the pre-run review against the ticket's current committed text, and the drain holds such a ticket until that text changes.

The cause is a hold rule written in more than one place:
- the drain composes `premise_parked` and `budget_parked` at `chupa/drain.py:346` and again at `chupa/drain.py:386`;
- serve's scheduler composes them a third time at `chupa/scheduler.py:59-63`;
- the snapshot and `watch` (`chupa/observe.py`) never check either park. Their `held()` is a hand-copied fold of `status.reject_queue` over raw dicts, so they list a parked ticket as ready.

`observe.py` also redefines `SETTLED`, which `chupa/status.py` already owns.

After this change one function decides a content park, and every caller uses it. The snapshot and `watch` show a parked ticket as held, matching what drain and serve do.

## Scope in / Scope out
- In: `chupa/drain.py`:
  - New `parked(events, stem, ticket_sha) -> bool`: true when `premise_parked` or `budget_parked` holds for that stem and committed `ticket.md` blob.
  - The held set in `Drain.run` (line 346) and the check in `_between_tickets` (line 386) call `parked`. The `last.get(s) == PREMISE and` guard goes: `premise_parked` already requires the last transition to be `premise_failed`.
- In: `chupa/scheduler.py`: `dispatch_next` calls `parked(events, stem, await self.ticket_sha(stem))` for each candidate that has ended a run (its last transition exists and is not `running`). The inline `premise_failed` / `diff_budget` pre-filter goes. It duplicates the checks inside the two park functions. A never-run candidate has no committed blob to look up and cannot be parked.
- In: `chupa/observe.py`:
  - Delete `held()`. The held set is `reject_queue(history)` from `chupa/status.py` plus every stem `s` in `blobs` where `parked(history, s, blobs[s])` holds. A stem with no committed blob has never run, so it is never parked. `blobs` comes from `committed_ticket_shas(ctx)`, and `history` is the `SimpleNamespace` event list `snapshot` already builds.
  - Both `snapshot` and `queue` use that held set.
  - In `snapshot`, a parked ticket's `why_blocked` text is `held until the ticket changes (last: <terminal>)`. A Reject-queue ticket keeps its current text.
  - In `queue`, a parked ticket's text is `held until the ticket changes`. A Reject-queue ticket keeps its current texts.
  - Delete the local `SETTLED` and import it from `chupa.status`.
- In: tests:
  - `tests/test_scheduler.py`:
    - a ticket whose last run ended `premise_failed` against its current blob is not dispatched; after its blob changes it is. This mirrors `test_scheduler_holds_diff_budget_failure`;
    - a never-run candidate dispatches without a `ticket_sha` call.
  - `tests/test_watch.py`, in `test_snapshot_holds_a_parked_ticket`:
    - `snapshot` lists a confirmed ticket in `blocked` with `held: true` when its last run ended `premise_failed` against the blob `committed_ticket_shas` returns.
    - With a different blob, the same ticket is in `queued`.
    - The same pair of cases for a `gate_failed` run whose reason includes `diff_budget`.
    - `queue` reports the premise-parked ticket as `held until the ticket changes`, not `ready`.
    - An uncommitted ticket that the stubbed `committed_ticket_shas` leaves out still builds a snapshot and is not held.
- In: `docs/how-chupa-works.md`: the `chupa snapshot` paragraph (the line beginning "`chupa snapshot` builds its data read-only") says the snapshot holds tickets by the drain's `parked` rule and the Reject queue.
- Out:
  - Process-local holds (storm, provider drought, quarantine, the stuck-time ceiling). They live in a running engine's memory, not the journal, so the snapshot cannot see them.
  - The difference between drain and serve for a Reject-queue ticket with cap budget left: the drain re-offers it, and serve holds it until a verdict.
  - `chupa status`'s `blocked` block.
  - `stats.py`'s own `SETTLED`, which also counts `rejected` and is a different set.
  - Any JavaScript in `vscode-chupa/`. The extension already draws `held` and `section` from the snapshot.

## Scope fence
- chupa/drain.py
- chupa/scheduler.py
- chupa/observe.py
- tests/test_drain.py
- tests/test_scheduler.py
- tests/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/test_scheduler.py tests/test_watch.py tests/test_drain.py tests/test_requisition_gate.py` exits 0, including every test listed in Scope in.
2. `grep -n "premise_parked\|budget_parked" chupa/drain.py chupa/scheduler.py chupa/observe.py` shows each name only at its own definition and inside `parked`.
3. `grep -n "^def held\|^SETTLED" chupa/observe.py` prints nothing.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_scheduler.py tests/test_watch.py tests/test_drain.py tests/test_requisition_gate.py
./dev.py test
```

## Regression
```
./dev.py test tests/test_watch.py -k test_snapshot_holds_a_parked_ticket
```
- carries: tests/test_watch.py

## Definition of rejected
Reject the branch if any of the following holds:
- a hold rule for premise or diff-budget failures is written anywhere other than `premise_parked`, `budget_parked`, and `parked` in `chupa/drain.py`;
- drain or serve dispatches a ticket it held before this change, or holds a ticket it dispatched before;
- `snapshot` or `queue` writes anything;
- any file under `vscode-chupa/` changes.

## Time budget
- expected: 45m
- stuck: 90m
