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
- chupa/__main__.py
- tests/test_drain.py
- tests/test_requisition_gate.py
- tests/test_scheduler.py
- tests/test_watch.py
- tests/test_daemon_composition.py
- docs/how-chupa-works.md

## Goal / Why
On 2026-11-07 the extension showed `box-view` as "ready" in the queue while the drain held it: its last run ended `premise_failed` at the pre-run review against the ticket's current committed text, and the drain holds such a ticket until that text changes.

The cause is a hold rule written in more than one place:
- `chupa/drain.py` has two park predicates, `premise_parked` and `budget_parked`, each taking the current blob;
- the drain composes them at `chupa/drain.py:346` and again at `chupa/drain.py:386`;
- serve's scheduler composes them a third time at `chupa/scheduler.py:59-63`, behind its own copy of the "could this be parked" test;
- the snapshot and `watch` (`chupa/observe.py`) never check either park. Their `held()` is a hand-copied fold of `status.reject_queue` over raw dicts, so they list a parked ticket as ready.

`observe.py` also redefines `SETTLED`, which `chupa/status.py` already owns.

After this change one pure function owns the content-park rule, and every caller uses it. The snapshot and `watch` show a parked ticket as held, matching what drain and serve do.

## Scope in / Scope out
- In: `chupa/drain.py`:
  - New `parked_blob(events, stem) -> str | None`. It returns the `ticket_sha` of the stem's last `running` transition when its last transition is `premise_failed`, or `gate_failed` with `diff_budget` among its comma-separated `reason` codes. Otherwise it returns None. A stem is parked exactly when its committed `ticket.md` blob equals the returned value.
  - Delete `premise_parked` and `budget_parked`. `parked_blob` replaces both, with the same semantics.
  - The held set in `Drain.run` (line 346) and the check in `_between_tickets` (line 386) compare `parked_blob(events, s)` to the stem's blob. The `last.get(s) == PREMISE and` guard goes.
- In: `chupa/scheduler.py`: `dispatch_next` replaces its inline `premise_failed` / `diff_budget` test with `(blob := parked_blob(events, stem)) is not None and blob == await self.ticket_sha(stem)`. `ticket_sha` is still called only for a stem `parked_blob` names, as today, so a never-run or otherwise-failed candidate makes no git call.
- In: `chupa/observe.py`:
  - Delete `held()`. New module-level `held(history, blobs) -> set[str]`: the keys of `reject_queue(history)` from `chupa/status.py`, plus every stem `s` with `parked_blob(history, s)` not None and equal to `blobs.get(s)`. A stem with no committed blob is never parked.
  - `snapshot` builds the set from its `history` and `committed_ticket_shas(ctx)`.
  - `queue` takes the held set as a new parameter. `text_snapshot` computes it from `committed_ticket_shas(ctx)` and passes it in.
  - In `snapshot`, a parked ticket's `why_blocked` text is `held until the ticket changes (last: <terminal>)`. A Reject-queue ticket keeps its current text.
  - In `queue`, a parked ticket's text is `held until the ticket changes`. A Reject-queue ticket keeps its current texts.
  - Delete the local `SETTLED` and import it from `chupa.status`.
- In: tests:
  - `tests/test_drain.py` and `tests/test_requisition_gate.py`: the `premise_parked` assertions become `parked_blob` assertions (`== blob` for a park, `!= sha` after an edit releases it).
  - `tests/test_scheduler.py`:
    - a ticket whose last run ended `premise_failed` against its current blob is not dispatched; after its blob changes it is. This mirrors `test_scheduler_holds_diff_budget_failure`;
    - a candidate whose last run ended `infra_error` dispatches without a `ticket_sha` call.
  - `tests/test_watch.py`:
    - New `test_snapshot_holds_a_parked_ticket`:
      - `snapshot` lists a confirmed ticket in `blocked` with `held: true` when its last run ended `premise_failed` against the blob the stubbed `committed_ticket_shas` returns;
      - with a different blob, the same ticket is in `queued`;
      - the same pair of cases for a `gate_failed` run whose reason includes `diff_budget`;
      - an uncommitted ticket that the stub leaves out still builds a snapshot and is not held.
    - `queue` reports a premise-parked ticket as `held until the ticket changes`, not `ready`.
    - `test_queue_projection_and_fallback`, `test_queue_counts_a_split_dependency_met_by_its_successors`, and `test_recent_steps_merges_engine_and_stage_events` build a `Context` with `git=None`. They pass the new `queue` parameter or stub `committed_ticket_shas`.
- In: `docs/how-chupa-works.md`: the `chupa snapshot` paragraph (the line beginning "`chupa snapshot` builds its data read-only") says the snapshot holds tickets by the Reject queue and the drain's `parked_blob` rule.
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
- tests/test_requisition_gate.py
- tests/test_scheduler.py
- tests/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/test_scheduler.py tests/test_watch.py tests/test_drain.py tests/test_requisition_gate.py tests/test_daemon_composition.py` exits 0, including every test listed in Scope in.
2. `grep -rn "premise_parked\|budget_parked" chupa tests` prints nothing.
3. `grep -n "diff_budget\|PREMISE\|premise_failed" chupa/scheduler.py chupa/observe.py` prints nothing.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_scheduler.py tests/test_watch.py tests/test_drain.py tests/test_requisition_gate.py tests/test_daemon_composition.py
./dev.py test
```

## Regression
```
./dev.py test tests/test_watch.py -k test_snapshot_holds_a_parked_ticket
```
- carries: tests/test_watch.py

## Definition of rejected
Reject the branch if any of the following holds:
- a premise or diff-budget park rule is written anywhere other than `parked_blob` in `chupa/drain.py`;
- drain or serve dispatches a ticket it held before this change, or holds a ticket it dispatched before;
- serve calls `ticket_sha` for a stem that `parked_blob` does not name;
- `snapshot` or `queue` writes anything;
- any file under `vscode-chupa/` changes.

## Time budget
- expected: 45m
- stuck: 90m
