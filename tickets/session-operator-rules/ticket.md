---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
- verdict-human-only

## Context
- AGENTS.md
- CLAUDE.md
- dev.py

## Goal / Why
The **Supervising session** rule in `CLAUDE.md` (section B) lets an agent running the drain edit tickets after a plan fix and leaves keep/kill only loosely to the user. An agent session used that latitude to hand-rewrite a lifted seed, edit an in-flight ticket, and run `confirm` twice. Sessions should keep the queue moving with small obvious fixes, never force failed work back in, and hand the user `./dev.py` commands instead of raw module invocations.

## Scope in / Scope out
- In: replace the **Supervising session** bullet in `CLAUDE.md` section B with this rule set, keeping the file's bullet + `Why:` shape:
  - A session may, unasked: fix a ticket's lint/format errors, add a file missing from its `## Scope fence` or `## Context`, correct a stale path, make a simple wording update, and run or restart the drain.
  - A session may not: run `confirm` or `reject`; retry or re-feed a stem whose caps are spent; edit a ticket while it is running; change a ticket's goal or scope; hand-rewrite a ticket the engine authored. Those go to the user.
  - Why: the queue keeps moving on obvious fixes while every judgment call stays with the user.
- In: add a rule to `CLAUDE.md` section B: commands a session runs or gives the user are `./dev.py` subcommands, never raw `uv run python -m chupa ...`; a missing command becomes a new `./dev.py` subcommand. Commands for the user to run are given in a copy/paste code block. Why: one memorable command surface.
- In: no new paragraph opens with `chupa` followed by a directive ("chupa must ..."): the `core_drift` gate (`chupa/hostfiles.py` `classify_core`) refuses such a paragraph outside the managed block. Write the rules with "A session" as the subject.
- In: outside the managed `chupa:core` block, `CLAUDE.md` stops treating `CHUPA_PLAN.md` as current: the **Read first** line says `docs/how-chupa-works.md` describes the code and is maintained by tickets, and `CHUPA_PLAN.md` is the frozen bootstrap design record; section A's **The plan is the seed** and **Generated files** rules and section B's **Plan prose is pure spec** rule are rewritten to match (a ticket updates the docs its change affects; the plan is never edited). Do not edit `CHUPA_PLAN.md`; it is history, not a spec this change must keep in step with.
- In: this ticket replaces the rules that would otherwise forbid it. In `CLAUDE.md` section A, **Generated files** says CLAUDE.md and AGENTS.md are authored from plan section 17 and changed only by editing the plan; rewrite it to say they are edited directly by tickets, as is any other doc. The intro line saying a rule change touches both files stays: apply it, making the same plan-reference changes in `AGENTS.md` (its **Read first** line and **Generated files** rule) in this change. Do not edit `CHUPA_PLAN.md`.
- Out: section A engine conduct, the managed `chupa:core` block, `CHUPA_PLAN.md`, and any code.

## Scope fence
- CLAUDE.md
- AGENTS.md

## Acceptance criteria
1. `CLAUDE.md` section B contains the replaced **Supervising session** rule and the `./dev.py` rule.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q
```

## Definition of rejected
Reject the branch if `CLAUDE.md` still lets a session run `confirm`/`reject`, re-feed a spent stem, or edit a running ticket, or if anything outside the named rules and the plan references above changes, or if the managed block changes.

## Time budget
- expected: 20m
- stuck: 45m
