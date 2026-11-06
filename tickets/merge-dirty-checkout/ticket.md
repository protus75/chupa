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
- chupa/drain.py
- chupa/runner.py
- chupa/effects.py
- chupa/reconcile.py
- tests/test_merge.py
- docs/how-chupa-works.md

## Goal / Why
On 2026-11-06 at 16:55Z a drain crashed with an uncaught `GitError` in `merge.write_squash`. A chat session had left an uncommitted edit to `docs/how-chupa-works.md` in the main checkout. The squash of `implement-all-premise-findings` also changed that file, so `git merge --squash` refused ("Your local changes ... would be overwritten") and the traceback ended the drain mid-merge. The only record was the drain's terminal. The ticket's branch, worktree, and an unfinished `merge/<stem>/0` effect intent were left behind.

A dirty main checkout is an operator condition, not a ticket failure. After this change, merge checks for it before the squash. When it finds an overlap, the drain stops cleanly with a refusal that names the files and the fix. It does not crash, and it does not charge the ticket. The next drain merges the already-reviewed branch.

## Scope in / Scope out
- In: `chupa/merge.py`, in `merge` before `write_squash`:
  - compute the overlap between the files the squash changes (`diff_names(repo, MAIN, stem)`) and the main checkout's tracked changes (`git status --porcelain`, excluding untracked `??` entries);
  - when the overlap is non-empty, raise `runner.Refusal("main checkout has local changes to <files> that the <stem> merge would overwrite", "commit or revert those local edits in the main checkout, then run `drain` again; <stem> merges without re-running its stages")`.
- In: the refusal ends the drain as other engine refusals do (exit 2, `chupa drain: <message> -- <road>`, lock released). It must leave the following untouched:
  - no `merge/<stem>/<attempt>` effect intent is written;
  - no terminal is journaled for the ticket;
  - no cap is consumed;
  - the ticket's branch and worktree stay in place.
- In: confirm and document how the next drain resumes that ticket. Through `reconcile`/`harvest_orphan` as they stand, it must reach merge again without re-running Implement, Check, or Review. If they re-run stages instead, change them only as far as this case needs and say so in the run record.
- In: tests in `tests/test_merge.py`:
  - `test_merge_refuses_dirty_overlap_without_charging`: a tracked edit to a file the branch also changes makes `drain` return 2. The message names the file. The journal has no new terminal, cap, or `merge/` effect intent for the stem. Main is unchanged.
  - `test_merge_ignores_dirty_files_outside_the_squash`: a tracked edit to an unrelated file does not block the merge.
  - `test_merge_resumes_after_dirty_checkout_is_cleaned`: after the edit is committed, the next `drain` merges the stem without a new Implement call.
- In: `docs/how-chupa-works.md` section 4.5 (Merge): one bullet on this refusal and its road.
- Out: rebasing or stashing the operator's changes; untracked files; `serve`'s merge queue, beyond whatever it inherits from `merge`.

## Scope fence
- chupa/merge.py
- chupa/reconcile.py
- chupa/runner.py
- tests/test_merge.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_merge.py` exits 0, including the three tests above.
2. `docs/how-chupa-works.md` section 4.5 describes the dirty-checkout refusal.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_merge.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- a dirty overlapping file still raises an uncaught exception;
- the refusal consumes a cap or journals a terminal for the ticket;
- an unrelated dirty file blocks a merge;
- the engine stashes, resets, or overwrites the operator's changes;
- the resumed ticket re-runs Implement.

## Time budget
- expected: 45m
- stuck: 120m
