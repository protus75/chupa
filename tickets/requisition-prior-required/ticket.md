---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- requisition-prior-review

## Context
- chupa/requisition.py::review_ticket
- chupa/author.py

## On-demand
- tests/unit/test_specs.py
- tests/unit/test_requisition_stage_events.py
- tests/integration/test_requisition.py
- tests/integration/test_requisition_gate.py
- tests/integration/test_review_command.py
- tests/integration/test_rework.py
- tests/integration/test_watchdog_activation.py
- tests/integration/test_provider_cooldown_failover.py
- tests/regress_requisition_stage_events.py

## Goal / Why
`chupa/requisition.py::review_ticket` declares `prior: str = "none"`. A caller that forgets to pass the prior review silently sends `none`, which is the same text a genuine first review gets. When `remove-seeding` (fcefd4f5) deleted the only caller that passed it, nothing failed. Every requisition review then ran without its earlier findings for days, and `commit-lock` spent five attempts on reviews that never converged. `requisition-prior-review` wires the two real callers. This ticket makes that class impossible to repeat silently.

When this ticket is done:
- `review_ticket` has no default for `prior`, so a caller that omits it fails at once with `TypeError`.
- A first review is sent as the distinct text `first review: no earlier review recorded`, never a bare `none`. A reader of a prompt can then tell "no earlier review exists" apart from an empty input.

## Scope in / Scope out
- In: `chupa/requisition.py`:
  - Add the constant `FIRST_REVIEW = "first review: no earlier review recorded"`.
  - `review_ticket`'s `prior` parameter keeps its keyword-only position and loses its default.
  - `prior_review` (added by `requisition-prior-review`) returns `FIRST_REVIEW` wherever it returned `none`.
- In: `chupa/author.py`: its `review_ticket` call passes `prior=FIRST_REVIEW`. `chupa/rework.py` already passes its own `prior` and does not change.
- In: `chupa/specs/requisition_review.md`:
  - The `prior_review` input line reads "Your prior review of this ticket and the diff from the text it judged (`first review: no earlier review recorded` on a first review):".
  - `version` goes from "3.8" to "3.9".
- In: every test or script that calls `review_ticket` passes `prior=FIRST_REVIEW` (imported from `chupa.requisition`). These are `tests/integration/test_requisition.py` (3 calls), `tests/integration/test_watchdog_activation.py` (3), `tests/integration/test_provider_cooldown_failover.py` (1), `tests/integration/test_rework.py` (1), `tests/unit/test_requisition_stage_events.py` (1) and `tests/regress_requisition_stage_events.py` (1).
- In: tests from `requisition-prior-review` that expect a first review's `prior_review` block to read `none` now expect `FIRST_REVIEW`. These are `tests/unit/test_requisition_prior_review.py`, `tests/integration/test_requisition_gate.py` and `tests/integration/test_review_command.py`.
- In: `tests/unit/test_specs.py` pins `requisition_review` at "3.9".
- Out:
  - Other specs' `none` inputs, such as `retry_findings` and `coverage_dependents`.
  - `chupa/rework.py`.
  - How `prior_review` finds or formats a recorded review.

## Scope fence
- chupa/requisition.py
- chupa/author.py
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- tests/unit/test_requisition_stage_events.py
- tests/unit/test_requisition_prior_review.py
- tests/integration/test_requisition.py
- tests/integration/test_requisition_gate.py
- tests/integration/test_review_command.py
- tests/integration/test_rework.py
- tests/integration/test_watchdog_activation.py
- tests/integration/test_provider_cooldown_failover.py
- tests/regress_requisition_stage_events.py

## Acceptance criteria
1. `tests/unit/test_requisition_prior_review.py`:
   - `inspect.signature(review_ticket).parameters["prior"].default is inspect.Parameter.empty`, not `"none"`.
   - `prior_review` with no recorded verdict for the stem returns `FIRST_REVIEW`, not `none`.
2. `tests/integration/test_requisition_gate.py::test_edit_releases_and_reviews_the_new_content` and the `requisition-prior-review` test in `tests/integration/test_review_command.py` assert that the first request's `prior_review` block equals `FIRST_REVIEW`, not `none`.
3. `tests/unit/test_specs.py` asserts `requisition_review` is version "3.9".
4. `grep -rn 'prior: str = "none"' chupa` finds nothing.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- `review_ticket`'s `prior` keeps any default.
- A requisition prompt renders a bare `none` in its `prior_review` block.
- `chupa/rework.py` changes.

## Time budget
- expected: 20m
- stuck: 45m
