---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- chupa/tickets.py::intake
- chupa/tickets.py::IntakeResult
- chupa/tickets.py::_porcelain
- chupa/tickets.py::_pending
- chupa/tickets.py::_intake_claims
- chupa/tickets.py::validate_ticket
- chupa/tickets.py::lint_findings
- chupa/tickets.py::evidence_findings
- tests/unit/test_git_commit.py

## Goal / Why
This is the first of three successors of `menu-mirrors-verb-admission`. The goal is that the VS Code menu mirrors exactly what each chupa verb allows. `run` and `review` decide a pending stem by intake's own decision. Today that decision is inlined in `intake` (`chupa/tickets.py`) together with its commits, so `snapshot` cannot reuse it. It would have to copy it, and copies are the drift the parent ticket removes. This ticket extracts intake's decision into a non-committing helper that `intake` itself uses. A later successor (`menu-table-run-review-admission`) has `snapshot` call the same helper. This ticket changes no behavior.

## Scope in / Scope out
In:
- Extract from `intake` in `chupa/tickets.py` a non-committing helper that gets the porcelain entries (`_porcelain` output), the per-stem regular evidence path listings (as `intake` builds `evidence` today), the journal's last states, and the `stems` filter. It returns: the stray staged paths (staged outside the pending ticket files and their regular evidence files, intake's `allowed` rule, including staged deletions); and, for each selected pending stem, the claimed text from `_intake_claims` plus either its findings or its validated `Ticket`. A settled or rejected stem (`merged`, `already_satisfied`, `rejected`) validates with `_settled=True` and gets no lint or evidence findings. Every other stem gets `lint_findings` plus `evidence_findings` over its listed evidence paths, exactly as today. The helper reads ticket text from disk but runs no git and writes nothing. It may be one function, or a stray function plus a per-stem function in the same module.
- `intake` keeps its commit lock and its git calls (`status_porcelain`, then one `ls-files` per pending stem) in today's order. When the stray list is non-empty it raises `IntakeRefused` with today's message and paved road and commits nothing. It writes stamped text and commits each clean stem from the helper's result, journaling the same intake signal. Its committed and refused results are unchanged for every input.

Out:
- `chupa/observe.py`, every verb, and every menu: later successors.
- Any change to what intake accepts, refuses, stamps, or commits.

## Scope fence
- chupa/tickets.py
- tests/unit/test_intake_plan.py

## Acceptance criteria
1. `tests/unit/test_intake_plan.py` calls the helper with the porcelain entries, evidence listings, and last states passed in, with ticket files under `tmp_path` and no git. It asserts: a staged file outside `tickets/` is returned as stray; a pending stem's staged regular evidence file is not stray; a new human `state: draft` stem's claimed text is stamped `source: human` and `state: confirmed`; a pending stem with a lint finding returns that finding; and a settled pending stem validates with `_settled=True` and gets no lint or evidence findings.
2. `tests/unit/test_intake_plan.py` runs `intake` with git faked the way `tests/unit/test_git_commit.py` fakes it. It asserts that intake's committed stems, refused findings, and `IntakeRefused` match the helper's result for the same entries, evidence listings, and states.
3. `./dev.py test` exits 0, with `tests/integration/test_tickets.py` and `tests/unit/test_git_commit.py` unchanged.

## Verification
```
./dev.py test
```

## Definition of rejected
- `intake` commits, refuses, stamps, or raises differently for any input than before this change.
- The helper runs git or writes a file.
- Any file outside the scope fence changes.

## Time budget
- expected: 45m
- stuck: 90m