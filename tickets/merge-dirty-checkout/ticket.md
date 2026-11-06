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
- chupa/git.py
- tests/test_merge.py
- docs/how-chupa-works.md

## Goal / Why
On 2026-11-06 at 16:55Z a drain crashed with an uncaught `GitError` in `merge.write_squash`. The main checkout had an uncommitted edit to `docs/how-chupa-works.md`, and the squash of `implement-all-premise-findings` also changed that file, so `git merge --squash` refused and the exception ended the drain. After this change merge refuses that case through its existing refusal path instead of crashing.

## Scope in / Scope out
- In: `chupa/merge.py` `merge`, before `write_squash`:
  - compute the overlap between `diff_names(repo, MAIN, stem)` and the main checkout's tracked changes (`git status --porcelain`, excluding `??`);
  - when the overlap is non-empty, return `_refused([Finding(code="dirty_checkout", message="main checkout has local changes to <paths> that the squash would overwrite", paved_road="commit or revert those edits in the main checkout; the ticket re-runs through the normal retry path")], cost)`.
- In: `tests/test_merge.py` `test_merge_refuses_dirty_overlap_instead_of_raising`: with a tracked edit to a file the branch changes, `merge` returns `gate_failed` with a `dirty_checkout` finding, main is unchanged, and no `merge/` effect intent is journaled.
- In: `docs/how-chupa-works.md` section 4.5: one bullet for the `dirty_checkout` refusal.
- Out: everything else.

## Scope fence
- chupa/merge.py
- tests/test_merge.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_merge.py` exits 0, including the test above.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_merge.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if a dirty overlapping file still raises, or if merge stashes, resets, or overwrites the operator's changes.

## Time budget
- expected: 45m
- stuck: 120m
