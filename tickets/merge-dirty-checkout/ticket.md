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
- chupa/drain.py
- chupa/git.py
- chupa/tickets.py
- tests/test_merge.py
- tests/test_drain.py
- docs/how-chupa-works.md

## Goal / Why
On 2026-11-06 at 16:55Z a drain crashed with an uncaught `GitError` in `merge.write_squash`. A chat session had left an uncommitted edit to `docs/how-chupa-works.md` in the main checkout. The squash of `implement-all-premise-findings` also changed that file, so `git merge --squash` refused ("Your local changes ... would be overwritten") and the traceback ended the drain mid-merge. The only record was the drain's terminal.

A dirty main checkout is an operator condition, so the engine should catch it before work is spent, and never crash on it. Resuming a half-merged run is out of reach: stage results live only in memory, and reconcile reaps the stranded run. So this ticket guards the run at both ends:
- the drain does not start a ticket while the main checkout has tracked local changes inside that ticket's `## Scope fence`;
- merge refuses through its existing refusal path, never an exception, if such changes appear during the run.

## Scope in / Scope out
- In: `chupa/drain.py` `_Drain._run_one`, before anything is journaled for the pick (before the reoffer handling and the `running` transition):
  - read the main checkout's tracked changes with `git status --porcelain`, excluding untracked `??` entries;
  - when any changed path falls under one of the ticket's `scope_fence` prefixes, raise `Refusal("main checkout has local changes to <paths> inside <stem>'s scope fence", "commit or revert those edits in the main checkout, then run `drain` again")`.

  The drain then ends as other refusals do: exit 2, lock released, and no `running` transition, terminal, cap, or effect journaled for the stem.
- In: `chupa/merge.py` `merge`, before `write_squash`:
  - compute the overlap between `diff_names(repo, MAIN, stem)` and the main checkout's tracked changes;
  - when the overlap is non-empty, return `_refused([Finding(code="dirty_checkout", message="main checkout has local changes to <paths> that the squash would overwrite", paved_road="commit or revert those edits in the main checkout; the ticket re-runs through the normal retry path")], cost)`.

  This is the existing merge-refusal path, so `write_squash`'s effect is never entered.
- In: tests.
  - `tests/test_drain.py` `test_drain_refuses_dirty_fence_before_dispatch`: a tracked edit to a fenced file makes `drain` return 2 with that path in the message. There is no dispatch call, and no `running` transition, terminal, or `cap_consumed` for the stem.
  - `tests/test_drain.py` `test_drain_ignores_dirty_files_outside_the_fence`: an unrelated tracked edit lets the ticket run and merge.
  - `tests/test_merge.py` `test_merge_refuses_dirty_overlap_instead_of_raising`: a tracked overlapping edit appears after Review. `merge` returns `gate_failed` with a `dirty_checkout` finding, main is unchanged, and no `merge/` effect intent is journaled.
- In: `docs/how-chupa-works.md`: one bullet in section 4.5 (Merge) for the `dirty_checkout` refusal, and one in section 7.1 for the pre-dispatch check.
- Out: stashing, resetting, or rebasing the operator's changes; untracked files; resuming a half-merged run; `serve` beyond what it inherits from `merge`.

## Scope fence
- chupa/merge.py
- chupa/drain.py
- tests/test_merge.py
- tests/test_drain.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_drain.py tests/test_merge.py` exits 0, including the three tests above.
2. `docs/how-chupa-works.md` sections 4.5 and 7.1 describe both checks.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_drain.py tests/test_merge.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- a dirty overlapping file still raises an uncaught exception;
- the pre-dispatch refusal journals anything for the ticket or consumes a cap;
- an unrelated dirty file blocks a ticket;
- the engine stashes, resets, or overwrites the operator's changes.

## Time budget
- expected: 45m
- stuck: 120m
