---
state: confirmed
source: seed
priority: P1
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- spine-harvest

## Context
- chupa/reconcile.py
- chupa/runner.py
- chupa/drain.py
- tests/test_reconcile.py
- tests/test_terminal.py

## Plan contract
- 19.L
- 19.P2
- section 11

## Goal / Why
Reconcile-on-entry harvests each orphaned in-flight run's worktree before it reaps the run. Harvest goes first, then the `abandoned` terminal is journaled, then the worktree is removed. The orphan's material lands in `tickets/<stem>/attempts/<n>/harvest.json` like any other non-ok terminal's.

Why: section 11.2 says orphan worktrees are harvested before removal, and that before the daemon exists the same reconcile runs on entry ("Phase 1 reaps bare; Phase 2 folds in this harvest"). An engine death mid-call is exactly the case where the dying worktree and the attempt spool hold the only record of what happened. A bare reap destroys it, and the re-run repeats the dead end blind. The run-terminal harvest (`spine-harvest`) already owns the extraction, the `Harvest` schema, the ticket-plane commit, and the prior-attempts render. This ticket only routes the orphan path through that ONE harvest function. It is never a second extraction.

Owners (section 9 ownership law): `chupa/reconcile.py` owns the orphan reap and its journal -> wipe order. `chupa/runner.py` owns the harvest function, which it hands to reconcile. Reconcile receives it as an injected callable, because importing the runner from reconcile would be circular. `chupa/drain.py` and `chupa/runner.py` are reconcile's two production callers.

## Scope in / Scope out
- In: `reconcile` takes the harvest as an injected callable. For each orphan whose worktree exists, in order:
  1. Harvest it, with `terminal: "abandoned"`, `stage: null`, empty `findings`, `wall_seconds: null`, and `usd: null`. The attempt `<n>` is the reaped run's sequence, `run_seq` before the `abandoned` is journaled. The diff stat is of the stem's branch against `main` when the branch exists. Tails are cut from that run's attempt spool.
  2. Journal `abandoned`.
  3. Remove the worktree, then prune (unchanged).
- In: the harvest commit is the same one-commit `chupa(<stem>): harvest` ticket-plane commit the run terminal makes.
- In: harvest stays SOFT. A harvest error journals the same `harvest_failed` signal and the reap proceeds. SETUP-DEATH short-circuit: an orphan with no worktree is reaped bare, exactly as today.
- In: both production callers (`run_ticket` in `chupa/runner.py`, the drain's entry in `chupa/drain.py`) pass the production harvest. A reconcile with no orphans stays a no-op with no commit.
- Out: any change to the `Harvest` schema, the extraction, the render, or the run-terminal handler.
- Out: the Phase 3 orphan sweeper and restart-reconcile.
- Out: diagnosis of an orphan.

## Scope fence
- chupa/reconcile.py
- chupa/runner.py
- chupa/drain.py
- tests/test_reconcile.py
- tests/test_harvest_orphans.py

## Acceptance criteria
1. `tests/test_harvest_orphans.py` pre-seeds a journal `running` with no terminal plus a live worktree on the stem's branch carrying a committed edit and a spooled `error.txt`, then invokes `chupa.__main__.main(["run", ...])`. Main then carries `tickets/<stem>/attempts/<n>/harvest.json` (with `<n>` the reaped run's sequence) in a `chupa(<stem>): harvest` commit. It validates as `Harvest` with `terminal == "abandoned"`, its `diff_stat` names the edited file, and its `reason` carries the spooled error text.
2. `tests/test_harvest_orphans.py` proves the order from the journal: the harvest ticket-plane effect completion precedes the `abandoned` `state_transition`, and the worktree dir is gone afterwards.
3. `tests/test_harvest_orphans.py` proves the re-run after the reap renders that orphan harvest's `reason` inside the prior-attempts block of its Implement prompt.
4. `tests/test_harvest_orphans.py` proves an orphan with no worktree is reaped bare with no harvest commit, and that a raising harvest journals `harvest_failed` while the reap still journals `abandoned` and removes the worktree.
5. `tests/test_reconcile.py` keeps every existing assertion, adapted only to pass the harvest callable.
6. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_harvest_orphans.py tests/test_reconcile.py
uv run pytest -q tests/test_harvest.py tests/test_terminal.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- The orphan path copies or re-implements extraction or commit logic instead of calling the run-terminal harvest function.
- The worktree is removed before `abandoned` is journaled, or `abandoned` is journaled before harvest.
- A harvest error blocks the reap.
- The diff touches a file outside the fence.

## Time budget
- expected: 45m
- stuck: 90m
