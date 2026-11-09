---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- chupa/merge.py::dirty_overlap
- chupa/merge.py::write_squash
- chupa/git.py
- tests/integration/test_merge.py
- tests/integration/test_mergequeue.py
- docs/how-chupa-works.md

## Goal / Why
`write_squash` in `chupa/merge.py` runs `ctx.git.commit(ctx.repo, squash_message(...))` with no `only`, so git commits the whole index of the main checkout. The only guard, `dirty_overlap`, refuses only when dirty paths intersect `diff_names(MAIN, stem)`. A path staged in the main checkout but outside the branch diff passes the guard and rides into the squash commit. The main checkout is shared with interactive sessions and with hand-authored ticket intake, which can leave staged files, so this can happen in normal operation. Code that no Check or Review saw then lands on main under a `chupa-ticket` trailer naming the wrong ticket. After this change `dirty_overlap` also refuses when anything is staged in the main checkout, so both admission paths (inline `merge` and the merge queue) refuse before the squash instead of sweeping it in.

Simplest approach: reuse the existing `dirty_overlap` guard and `dirty_checkout` finding (one place, both admission paths call it). Rejected: passing `only=` the diff path set to `Git.commit`, because `diff_names` reports a rename by its new path only, so the old path's staged deletion would be dropped from the commit and left staged.

## Scope in / Scope out
- In: `chupa/merge.py` `dirty_overlap`: also collect every path whose porcelain index status (first character of the record) is not a space and not `?`. Treat renames and copies as in the current loop. When any staged path exists, return one `Finding(code="dirty_checkout", ...)` naming the staged paths, with the message saying the squash commit would sweep them in and the paved road `commit or unstage those changes in the main checkout; the ticket re-runs through the normal retry path`. The existing overlap finding keeps its behavior; when both apply, return both findings.
- In: `tests/unit/test_merge_dirty.py` drives `dirty_overlap` with a fake `ctx.git` whose `status_porcelain` returns canned `-z` records and whose `diff_names` returns a fixed list. Tests: `test_staged_only_path_outside_diff_is_refused` (one `dirty_checkout` finding naming the path); `test_unstaged_path_outside_diff_is_not_refused` (` M` record, no finding); `test_staged_rename_collects_both_paths` (`R  new\0old`, both paths named, `old` not misread as a record); `test_staged_and_overlapping_paths_give_both_findings`.
- In: `tests/integration/test_merge.py` test `test_merge_refuses_staged_path_outside_diff`: with `chupa/other.py` modified and staged (`git add`) in the main checkout, `merge` returns `gate_failed` with a `dirty_checkout` finding, main does not move, and `chupa/other.py` is still staged afterward.
- In: `tests/integration/test_mergequeue.py` test `test_queue_refuses_staged_path_outside_diff`: the same case through the queue, with no admission receipt and main unchanged.
- In: `docs/how-chupa-works.md`: extend the two existing `dirty_checkout` bullets (merge, merge queue) to say staged changes outside the branch also refuse.
- Out: changing `Git.commit`, `write_squash`, or untracked-file handling; `lift_outbox`; crash recovery around the squash.

## Scope fence
- chupa/merge.py
- tests/unit/test_merge_dirty.py
- tests/integration/test_merge.py
- tests/integration/test_mergequeue.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/unit/test_merge_dirty.py` exits 0; the tests rule out a staged-only path outside the diff returning no finding, an unstaged ` M` path outside the diff returning a finding, and a staged rename's old path being misread as a status record.
2. `./dev.py test tests/integration/test_merge.py -k staged_path_outside_diff` exits 0; the test rules out `merge` returning `ok` and committing the staged `chupa/other.py` into the squash.
3. `./dev.py test tests/integration/test_mergequeue.py -k staged_path_outside_diff` exits 0; the test rules out the queue admitting the ticket with the staged `chupa/other.py` swept into main.
4. `./dev.py test tests/integration/test_merge.py tests/integration/test_mergequeue.py` exits 0, so the existing unstaged-unrelated case (`test_merge_refuses_dirty_overlap_instead_of_raising` with `overlap` false) still admits.

## Verification
```
./dev.py test tests/unit/test_merge_dirty.py
./dev.py test tests/integration/test_merge.py -k staged_path_outside_diff
./dev.py test tests/integration/test_mergequeue.py -k staged_path_outside_diff
./dev.py test tests/integration/test_merge.py tests/integration/test_mergequeue.py
```

## Definition of rejected
Reject the branch if either admission path can still commit a path staged outside the branch diff into the squash, or if it unstages, resets, or stashes the operator's staged changes.

## Time budget
- expected: 30m
- stuck: 90m
