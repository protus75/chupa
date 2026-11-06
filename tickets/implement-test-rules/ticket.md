---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- prompts-drop-plan

## Runs before
- test-rules-prompt
- review-all-findings

## Context
- docs/how-chupa-works.md

## On-demand
- specs/implement.md
- tests/test_specs.py

## Goal / Why
The Implement prompt says nothing about how to write tests, so implementers write tests that pass whether the code is right or wrong. Review is the only place weak tests get caught, one per attempt, and test-heavy tickets loop for many cycles. After this change, the Implement prompt tells the implementer how to write a test that would fail on a wrong implementation, and to recheck every assertion on a retry, not only the flagged one.

## Scope in / Scope out
- In: `specs/implement.md` Task: add a paragraph on tests (inside Task; spec lint allows only the five fixed headings). It says:
  - For each assertion, name the likely wrong implementation it rules out; the fixture must give a different value under that wrong version. Examples: the right copy vs the wrong copy, innings 1-5 vs all 9, one row vs duplicates.
  - Never assert a value that a default, a zero, or a shared fixture would produce anyway.
  - On a retry, check every assertion this way, not only the one a finding names.
  Bump `version` from "2.0" to "2.1".
- In: `tests/test_specs.py`: update the implement version pins; assert each of the three rules is in the loaded implement spec body.
- In: `tests/test_stages.py`: update the `spec: implement 2.0` pin in the run.md assertion to the bumped version.
- In: `docs/how-chupa-works.md` section 4.2: the Implement prompt carries these test-writing rules.
- Out: every other spec, the retry block in `chupa/stages.py`, review.

## Scope fence
- specs/implement.md
- tests/test_specs.py
- tests/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. The loaded `specs/implement.md` body contains all three rules and the version is one minor step above the prior one (the test fails if any rule is removed or the version is left unchanged), checked by `uv run pytest tests/test_specs.py`.
2. `docs/how-chupa-works.md` section 4.2 states the rules.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_specs.py
uv run pytest -q
```

## Definition of rejected
The spec gains a heading outside Role/Task/Inputs/Output format/On-failure; any other spec changes; the implement major version changes.

## Time budget
- expected: 20m
- stuck: 45m
