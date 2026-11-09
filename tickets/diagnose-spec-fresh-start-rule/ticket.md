---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- none

## Context
- tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs

## On-demand
- chupa/specs/diagnose.md

## Goal / Why
`prepare_worktree` in `chupa/stages.py` deletes any leftover worktree and branch and recreates the branch from the merge base on every run, so no earlier diff carries over. `chupa/specs/diagnose.md` asks for lessons for a later attempt but never says what state that attempt starts from. In one run the attempt-6 lessons said to keep the rest of the attempt-6 diff and to change only `hostfiles.py`. Attempt 7 found its branch at the merge base with that diff gone. It narrowed its scope to the blob-read fix and bounced on a premise instead of redoing the wiring.

After this change the diagnose spec states that a retry starts from the merge base. Lessons must not tell the next attempt to keep, build on, or change only part of a previous diff. They restate the work that has to be redone, and may still say which parts of an earlier approach review found sound, as guidance for redoing them.

## Scope in / Scope out
- In: `chupa/specs/diagnose.md`. In `## Task`, after the paragraph beginning "Write concrete lessons", add a sentence containing the exact phrase "Every attempt starts from the merge base". The sentence says no earlier diff survives, so a lesson never says to keep or build on a previous diff and instead restates the work to redo. It also says a lesson may name which parts of an earlier approach review found sound. Bump `version` from `1.2` to `1.3`. The spec stays within the 200-line `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: the pinned `diagnose` version becomes `1.3`, and the file gains a test asserting the exact phrase is in `chupa/specs/diagnose.md`.
- Out: any change to `chupa/stages.py`, the verdict list, the Output format and On-failure sections, the 5-lesson and 300-character limits, and `eval/` fixtures.

## Scope fence
- chupa/specs/diagnose.md
- tests/unit/test_specs.py

## Acceptance criteria
1. `chupa/specs/diagnose.md` contains `Every attempt starts from the merge base` and `version: "1.3"`, not `1.2`.
2. `tests/unit/test_specs.py` has a test that asserts the phrase and passes under `./dev.py test tests/unit/test_specs.py`; it fails on a spec that lacks the phrase, so a spec still silent about the attempt's starting state is ruled out.
3. `tests/unit/test_specs.py` pins `1.3` as the `diagnose` version, so a spec left at `1.2` fails it.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test
```

## Definition of rejected
The change edits engine code, adds a rule that stops lessons from crediting sound parts of an earlier approach, or alters the Output format, On-failure, or lesson limits.

## Time budget
- expected: 10m
- stuck: 30m
