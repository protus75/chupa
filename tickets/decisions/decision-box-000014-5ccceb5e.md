---
id: decision-box-000014-5ccceb5e
kind: decision
link: box-000014-5ccceb5e
reopen_after_days: 60
---
`Git.rebase` and `Git._rebase_step` in `chupa/git.py` run `rebase --abort` without checking whether it worked, then raise `RebaseRefused`. This is deliberate, because a rebase that git refused before it started has nothing to abort. The note says that if an abort ever failed while a rebase was in progress, the worktree would stay mid-rebase even though `RebaseRefused` says the rebase was aborted. It suggests adding a check for an in-progress rebase only if the merge queue ever sees this happen.

The code still behaves as the note describes, but no failure has been seen. No journal entry, failure report or merge-queue incident shows a failed abort that left a worktree mid-rebase. The note itself makes the fix depend on the merge queue observing the problem. A refused rebase leads to a re-run of `run <stem>`, and Implement then re-branches from current main, so the work is redone from a fresh branch. This is speculative hardening with no evidence that it causes harm at runtime today.

- chupa/git.py:103-108 `rebase` runs an unchecked `rebase --abort`, with a why-comment explaining the case of a rebase refused before it starts, then raises RebaseRefused
- chupa/git.py:125-131 `_rebase_step` runs the same unchecked abort when there are no conflicted paths
- chupa/mergequeue.py:297-300 and chupa/merge.py:285-287 turn RebaseRefused into a refusal whose paved road is re-running `run <stem>`
- No open ticket, merged stem or decision covers this, and no failure report was supplied

Message: box-000014-5ccceb5e
