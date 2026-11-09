---
id: declined-box-000361-1e0f1d0a
kind: declined
link: box-000361-1e0f1d0a
reopen_after_days: 30
---
During the review-unmerged-provisional Implement run, an agent reported that running ticket lint across the whole repository from its worktree fails, because many existing tickets have invalid sections or name paths that do not exist. It filed this as a second problem.

The report names no ticket, no lint finding code, no path, and no command output, and it does not say whether the same failure happens on main or only in that worktree. It shows no runtime harm: tickets that fail lint are refused at intake or review, and nothing shows a drain, a merge, or a ticket run going wrong because of them. Old merged tickets can fail current lint rules after a section is renamed or a file is deleted; that is history, not a current behavior gap. 'Fix numerous tickets' is also not bounded to one buildable ticket. Two open tickets already cover the lint rule changes that could relate here: context-rejects-directory and lint-fence-refuses-decisions. Reopen if a report names an open (unmerged) ticket that fails `chupa lint <stem>` on main, or shows that an engine path such as drain, intake, review, or Implement input rendering crashes or refuses because an open ticket's section or path is invalid. The report should include the lint output and the base commit.

- The message has class suggestion, origin review-unmerged-provisional, stage implement, outcome premise_failed, and report null, so it carries no lint output, stems, or paths.
- review-unmerged-provisional is in the merged set, so the run that hit this went on to land.
- Open tickets context-rejects-directory and lint-fence-refuses-decisions already cover specific lint and path checks.
- The summary says 'numerous existing tickets', which is unbounded cleanup across many files rather than one repair.

Message: box-000361-1e0f1d0a
