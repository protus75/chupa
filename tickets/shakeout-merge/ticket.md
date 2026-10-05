---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- shakeout-recovery

## Context
- chupa/merge.py
- tests/test_merge.py

## Plan contract
- 19.L
- 19.P2
- section 9
- section 10

## Goal / Why
The sixth shakeout battery group pins merge admission (`chupa/merge.py`) with one member: a conflicted rebase. It runs through the production drain on the bench with a FakeLLM and zero human input. Its Check run re-confirms every prior entry and machine-produces the cumulative report into its OUTBOX.

Why: a refused rebase must leave the branch re-runnable (sections 9, 10). A worktree left mid-rebase strands the very branch the refusal tells the operator to re-run.

Owners (19.P2 Emits): this group fences ONLY `chupa/merge.py`, plus `eval/shakeout/` and `tests/test_shakeout.py`. A defect it exposes in admission is fixed here. A defect anywhere else, `chupa/git.py` included, is filed as a second problem and the ticket replies `premise_failed`, naming it.

## Scope in / Scope out
- In: `eval/shakeout/merge.py` with `MEMBERS`:
  - `conflicted_rebase`: (1) after the ticket's Review approves, main gains a commit editing the same line of the same file the branch edits. (2) The admission is refused `gate_failed` at `merge` with a `post_rebase_regate` finding, main's HEAD is unchanged, and the ticket's worktree has no rebase in progress (`git status` reports no rebase and the branch head equals the reviewed SHA). (3) The harvested `post_rebase_regate` finding.
- In: `eval/shakeout/run.py`: `GROUPS` gains `"merge"` after `"recovery"`.
- In: `tests/test_shakeout.py`: one test asserting the member's observable through `run_member`.
- Out: the Phase 3 resolution rungs and serial merge queue, members owned by other modules, any production change outside `chupa/merge.py`, and any runner, bench, or schema edit beyond `GROUPS`.

## Scope fence
- chupa/merge.py
- eval/shakeout/
- tests/test_shakeout.py

## Acceptance criteria
1. The `python -m eval.shakeout.run --group merge` command in `## Verification` exits 0 and writes `tickets/shakeout-merge/shakeout-report.json` holding every prior member re-confirmed plus `conflicted_rebase`, each `green`.
2. `uv run pytest -q tests/test_shakeout.py` passes with a test asserting the member's named observable.
3. `uv run pytest -q tests/test_merge.py` passes with no edit.
4. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m eval.shakeout.run --group merge --prior tickets/shakeout-recovery/shakeout-report.json --out tickets/shakeout-merge/shakeout-report.json
uv run pytest -q tests/test_shakeout.py
uv run pytest -q tests/test_merge.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- The member passes with a rebase left in progress or main moved.
- The report is written by anything but `write_report`, or committed on the branch.
- The diff touches a file outside the fence.

## Time budget
- expected: 45m
- stuck: 90m
