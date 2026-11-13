---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: rejected
---

## Depends on

- none

## Context

- tests/unit/test_specs.py::test_diagnose_spec_lesson_length_guidance

## On-demand

- chupa/specs/diagnose.md

## Goal / Why

The 300-character lesson limit, the split-into-separate-lessons rule and the general keep-names rule already merged in `diagnose-spec-lesson-length`. `chupa/specs/diagnose.md` lines 28-30 read: "Each lesson is at most 300 characters. If a lesson needs more detail, split it into separate lessons, one fact or file group each, keeping the total to 5 or fewer. Keep the concrete file, fixture and caller names the next attempt needs; drop prose around them instead." `tests/unit/test_specs.py::test_diagnose_spec_lesson_length_guidance` pins those sentences. This ticket does not repeat them.

The remaining gap is the overcorrection risk raised in retro 40. When a lesson is split, a piece can carry a fact but name no file, fixture or caller, so it cannot be acted on alone (drain-sighup-graceful-stop attempt 2 passed because its lessons named the exact fixture to copy). The existing sentence is about names in general and says nothing about each piece of a split.

The retro rationale says the limit is already stated. Reopen the limit itself only if a retro window that begins after `diagnose-spec-lesson-length` merged still records Diagnose lessons over 300 characters that cause re-prompts or `invalid_artifact` verdicts.

## Scope in / Scope out

Scope in:

- Add one sentence in `chupa/specs/diagnose.md` directly after the existing sentence "Keep the concrete file, fixture and caller names the next attempt needs; drop prose around them instead." The new sentence: "Each piece of a split lesson names the file, fixture or caller it acts on, so no piece relies on another to say where to act." The existing sentence stays unchanged, so its pin in `tests/unit/test_specs.py` stays valid.
- Bump the spec `version` to the next minor above the version on main, and update the version pin for `diagnose` in `tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs` to match.
- Add a test `test_diagnose_spec_split_lessons_name_targets` in `tests/unit/test_specs.py` that asserts the new sentence in the rendered Task text.

Scope out:

- Changing the 300-character limit, the 1 to 5 lesson count, or the existing keep-names sentence.
- Any engine code or validator change.

## Scope fence

- chupa/specs/diagnose.md
- tests/unit/test_specs.py

## Acceptance criteria

- `./dev.py test tests/unit/test_specs.py` exits 0 with `test_diagnose_spec_split_lessons_name_targets` included. The test asserts the exact phrase `Each piece of a split lesson names the file, fixture or caller it acts on`, which does not appear in the merged `chupa/specs/diagnose.md`, so the test fails on that unchanged file. The general keep-names sentence does not satisfy it.
- The `version` of `chupa/specs/diagnose.md` is the next minor above its version on main, and the `diagnose` pin in `tests/unit/test_specs.py` matches it, checked by `./dev.py test tests/unit/test_specs.py`.
- `Each lesson is at most 300 characters.` and `Give 1 to 5 non-blank lessons, each no more than 300 characters.` remain in `chupa/specs/diagnose.md`, and `test_diagnose_spec_lesson_length_guidance` still passes unchanged.

## Verification

```
./dev.py test tests/unit/test_specs.py
```

## Definition of rejected

- The change edits any file outside the fence.
- The change alters the 300-character limit, the lesson count, or the existing keep-names sentence, or adds a validator.
- The new text restates the general keep-names rule instead of requiring each split piece to name its own target.
- The new text asks for longer lessons.

## Time budget

- expected: 20m
- stuck: 40m
