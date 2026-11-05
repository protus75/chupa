---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
none

## Context
- docs/host-authoring.md
- tests/test_author.py

## On-demand
- specs/author.md

## Goal / Why
Implementers write tests that confirm the code runs, not tests that would fail if it were wrong, and reviews then catch those tests one per attempt. Much of this starts in the ticket: a criterion like "`foo` is tested" never says what wrong result the test must catch. After this change, every acceptance criterion that a test checks names the wrong result that test rules out, for both hand-written tickets (the authoring guide) and machine-written ones (the Author prompt).

## Scope in / Scope out
- In: `docs/host-authoring.md`, the `Acceptance criteria` bullet: add that a criterion checked by a test names the wrong result the test rules out, with one example (for example: "`parse('')` returns `[]`, not `None`"); a test that would also pass on the wrong result checks nothing.
- In: `specs/author.md` Task: the same rule, added to the preflight list. Bump `version` to "1.1" (minor: the review baseline binds only the major).
- In: `tests/test_author.py`: a test asserting the rule's text is in the loaded `specs/author.md` body.
- Out: the requisition review, the Rework prompt, ticket lint, every other spec.

## Scope fence
- docs/host-authoring.md
- specs/author.md
- tests/test_author.py

## Acceptance criteria
1. `specs/author.md` loads at version "1.1" and its body contains the rule (the test fails if the rule text is removed), checked by `uv run pytest tests/test_author.py`.
2. `docs/host-authoring.md` `Acceptance criteria` bullet states the rule with an example.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_author.py
uv run pytest -q
```

## Definition of rejected
The author spec's major version changes; ticket lint or requisition review changes.

## Time budget
- expected: 20m
- stuck: 45m
