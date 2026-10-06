---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: high
agent_effort: high
---

## Depends on
- phase3-continue

## Context
- chupa/merge.py
- chupa/git.py
- chupa/config.py
- tests/test_git.py

## Plan contract
- 19.L
- 19.P3
- section 9
- section 10

## Goal / Why
Add the Phase 3 dormant serial merge-admission queue in `chupa/mergequeue.py`.  It owns post-rebase mechanical regating, the ticket Verification integration check on the rebased worktree, conflict facts, the two typed conflict-resolution rungs, the red-streak pause, and the post-squash tree-hash assertion.  It stays unreachable from the production import closure until `merge-queue-activation`.

`chupa/merge.py` exposes its existing gate tuples for queue reuse only: `merge()`, `Candidate`, `MERGE_GATES`, and `PostRebaseGate` retain their signatures and behavior. `chupa/git.py` adds exactly three public operations: stop-at-conflict rebase, conflicted-path listing, and rebase-continue. `rebase()` retains its existing abort-before-`RebaseRefused` behavior; no public `rebase_abort` is added.

## Scope in / Scope out
- In: the registry row's dormant queue and the three stated public Git operations, with direct tests.
- In: rung 1 is mechanical Git merge plus only host-declared `merge.strategies` paths parsed by `chupa/config.py`; an undeclared path fails closed. Rung 2 returns a named typed unresolved-conflict handoff containing the stem and conflicted paths, and never invokes Rework inline.
- In: a red streak pauses at the shipped engine constant K=3 consecutive distinct integration-red tickets; a re-red of the same ticket does not advance it. A squash tree-hash mismatch escalates immediately and does not journal normal `to: merged`.
- Out: Rework, production composition or activation, daemon admission, and every later Phase 3 row.

## Scope fence
- chupa/mergequeue.py
- chupa/merge.py
- chupa/git.py
- tests/test_mergequeue.py
- tests/test_git.py

## Acceptance criteria
1. `uv run pytest -q tests/test_mergequeue.py` proves the 19.L transitive `chupa.*` import-closure scan rooted at `chupa/__main__.py`, recognizing both `import chupa.x` and `from chupa import x`; it proves `chupa.mergequeue` is dormant and fails when that module is made reachable, including through an import in `chupa/merge.py`.
2. `uv run pytest -q tests/test_mergequeue.py` drives a real repository through each refusal: mechanical rung refusal, undeclared strategy path, and both rungs refusing. In every case the worktree is not mid-rebase, HEAD is the pre-admission branch head, and `status --porcelain` is empty. It also proves declared strategy paths select rung 1, unresolved conflicts select the typed stem-and-paths handoff from rung 2, and Rework is never called inline.
3. `uv run pytest -q tests/test_mergequeue.py` proves post-rebase regating and integration Verification run on the rebased worktree; the red-streak K=3 constant pauses after three consecutive distinct integration-red tickets but not after the same ticket re-reds; and a post-squash tree-hash mismatch escalates rather than journaling `to: merged`.
4. `uv run pytest -q tests/test_git.py` proves the only new public Git operations are stop-at-conflict rebase, conflicted-path listing, and rebase-continue, while the existing refused-rebase abort and successful-rebase no-abort behavior remain green. `uv run pytest -q tests/test_merge.py tests/test_shakeout.py` keeps the existing merge and shakeout behavior unchanged.

## Verification
```
uv run pytest -q tests/test_mergequeue.py tests/test_git.py
uv run pytest -q tests/test_merge.py tests/test_shakeout.py
```

## Definition of rejected
Reject if `chupa.mergequeue` becomes production-reachable, a refusal leaves a worktree mid-rebase or dirty, Rework runs inline, a fourth public Git operation is added, or a required change falls outside this fence.

## Time budget
- expected: 60m
- stuck: 90m
