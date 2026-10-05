---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- shakeout-drain

## Context
- chupa/reconcile.py
- tests/test_reconcile.py

## Plan contract
- 19.L
- 19.P2
- section 11

## Goal / Why
The fifth shakeout battery group pins reconcile-on-entry (`chupa/reconcile.py`, section 11.2) with one member: engine death mid-call. It runs through the production drain on the bench with a FakeLLM and zero human input. Its Check run re-confirms every prior entry and machine-produces the cumulative report into its OUTBOX.

Why: an interrupted drain must self-heal on the next invocation (section 18). The orphan must be reaped, harvested, and re-entered findings-fed on a fresh run sequence, never replayed and never silently retried.

Owners (19.P2 Emits): this group fences ONLY `chupa/reconcile.py`, plus `eval/shakeout/` and `tests/test_shakeout.py`. A defect it exposes in reconcile is fixed here. A defect anywhere else is filed as a second problem and the ticket replies `premise_failed`, naming it.

## Scope in / Scope out
- In: `eval/shakeout/recovery.py` with `MEMBERS`:
  - `engine_death_mid_call`: (1) the bench's first drain dies inside the Implement call: the scripted call raises an exception that escapes the drain, leaving a `running` with no terminal and an `effect_intent` with no completion. (2) The next drain journals `abandoned` for that run, commits its `attempts/<n>/harvest.json`, removes the orphan worktree, and re-runs the stem under a fresh run sequence whose implement request key differs from the dead one, and the stem merges. (3) The orphan's harvest.
- In: `eval/shakeout/run.py`: `GROUPS` gains `"recovery"` after `"drain"`.
- In: `tests/test_shakeout.py`: one test asserting the member's observable through `run_member`.
- Out: the Phase 3 restart-reconcile and orphan sweeper, members owned by other modules, any production change outside `chupa/reconcile.py`, and any runner, bench, or schema edit beyond `GROUPS`.

## Scope fence
- chupa/reconcile.py
- eval/shakeout/
- tests/test_shakeout.py

## Acceptance criteria
1. The `python -m eval.shakeout.run --group recovery` command in `## Verification` exits 0 and writes `tickets/shakeout-recovery/shakeout-report.json` holding every prior member re-confirmed plus `engine_death_mid_call`, each `green`.
2. `uv run pytest -q tests/test_shakeout.py` passes with a test asserting the member's named observable.
3. `uv run pytest -q tests/test_reconcile.py` passes with no edit.
4. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m eval.shakeout.run --group recovery --prior tickets/shakeout-drain/shakeout-report.json --out tickets/shakeout-recovery/shakeout-report.json
uv run pytest -q tests/test_shakeout.py
uv run pytest -q tests/test_reconcile.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- The member's re-run replays the dead run's recorded result.
- The report is written by anything but `write_report`, or committed on the branch.
- The diff touches a file outside the fence.

## Time budget
- expected: 45m
- stuck: 90m
