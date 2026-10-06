---
priority: P1
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/stages.py
- tests/test_seed_path.py

## Plan contract
- section 13.3

## Goal / Why
`chupa/stages.py` validates every seed a seeding ticket authors against main, the repo the seed lands in, never the seeding ticket's worktree. A seed whose `## Context` or `## On-demand` names a file that only the seeding branch creates snags at Check with a finding naming that path, instead of passing review and failing the merge regate.

Why: section 13.3 requires each `Context` path to EXIST, and a lifted seed lives on main. `_review_one` (`chupa/stages.py`) today calls `validate_ticket(seed_stem, ..., worktree)` and `review_ticket(..., repo=worktree, ...)`, so a path present only on the branch passes, and the seed fails only after its lift, when the merge regate validates main.

## Scope in / Scope out
- In: `_review_one` in `chupa/stages.py` validates and reviews each seed with `ctx.repo` (main) as the repo, for ticket lint and for the base Implement render.
- Out: validation of non-seed tickets, the Author path, intake, and every other stage.

## Scope fence
- chupa/stages.py
- tests/test_seed_path.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seed_path.py` exits 0, including a new `test_seed_context_must_exist_on_main`: the seeding implementer commits `tests/new_idiom.py` on its branch and writes a seed listing it under `## Context`; that seed snags at Check with a finding whose message names `tests/new_idiom.py`, and no `requisition_review` call is made for it.
2. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_seed_path.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_seed_path.py -k test_seed_context_must_exist_on_main
```
- carries: tests/test_seed_path.py

## Definition of rejected
Reject the branch if it changes validation for any ticket that is not a seed under review, or if the new test passes on the merge base.

## Time budget
- expected: 30m
- stuck: 60m
