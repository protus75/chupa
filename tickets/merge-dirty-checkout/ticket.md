---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
none

## Context
- chupa/merge.py
- chupa/mergequeue.py
- chupa/git.py
- tests/test_merge.py
- tests/test_mergequeue.py
- docs/how-chupa-works.md

## Goal / Why
On 2026-11-06 at 16:55Z a drain crashed with an uncaught `GitError` in `merge.write_squash`. The main checkout had an uncommitted edit to `docs/how-chupa-works.md`, and the squash of `implement-all-premise-findings` also changed that file, so `git merge --squash` refused and the exception ended the drain. `serve`'s merge queue squashes through the same `write_squash` and would crash the same way. After this change both admission paths refuse that case through their existing refusal path instead of crashing.

## Scope in / Scope out
- In: `chupa/merge.py`: a helper `dirty_overlap(ctx, stem) -> list[Finding]`.
  - It intersects `diff_names(repo, MAIN, stem)` with the main checkout's tracked changes (`git status --porcelain`, excluding `??`).
  - When the intersection is non-empty, it returns one `Finding(code="dirty_checkout", message="main checkout has local changes to <paths> that the squash would overwrite", paved_road="commit or revert those edits in the main checkout; the ticket re-runs through the normal retry path")`.
  - Otherwise it returns `[]`.
- In: `chupa/merge.py` `merge` (inline `run`/`drain` admission): just before `write_squash`, if `dirty_overlap` returns findings, return `_refused(findings, cost)`.
- In: `chupa/mergequeue.py` (`serve` admission): just before the admission-receipt effect (`Effects(...).run(receipt_action, ...)`), if `merge.dirty_overlap` returns findings, return the queue's existing `refused(findings)`.
- In: tests.
  - `tests/test_merge.py` `test_merge_refuses_dirty_overlap_instead_of_raising`: with a tracked edit to a file the branch changes, `merge` returns `gate_failed` with a `dirty_checkout` finding. Main is unchanged, and no `merge/` effect intent is journaled.
  - `tests/test_mergequeue.py` `test_queue_refuses_dirty_overlap_instead_of_raising`: the same case through the queue. The result is `gate_failed` with a `dirty_checkout` finding, no admission receipt, and main unchanged.
- In: `docs/how-chupa-works.md`: one bullet in section 4.5 (Merge) and one in section 7.2.1 (Merge queue) for the `dirty_checkout` refusal.
- Out: everything else.

## Scope fence
- chupa/merge.py
- chupa/mergequeue.py
- tests/test_merge.py
- tests/test_mergequeue.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_merge.py tests/test_mergequeue.py` exits 0, including the two tests above.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_merge.py tests/test_mergequeue.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if either admission path still raises on a dirty overlapping file, or if either stashes, resets, or overwrites the operator's changes.

## Time budget
- expected: 45m
- stuck: 120m
