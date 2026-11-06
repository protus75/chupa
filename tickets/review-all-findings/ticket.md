---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- none

## Runs before
- test-rules-prompt

## Context
- eval/harness.py
- tests/test_drain_reentry.py
- docs/how-chupa-works.md

## On-demand
- specs/review.md
- chupa/stages.py
- tests/test_specs.py
- tests/test_stages.py

## Goal / Why
Review tends to report one finding per pass, so a ticket with several weak tests takes one attempt per test. Review also cannot tell which of its findings were already raised before, so a flaw that survives a retry looks new. After this change, the review prompt tells the reviewer to report every defect in one reply, listing each instance of a repeated flaw, and gives it the previous review's findings so it marks any that are still open.

## Scope in / Scope out
- In: `specs/review.md`: add to Task: report every defect in this one reply and never stop at the first; when the same flaw appears in several places (for example several tests that cannot fail), list each place as its own finding. Add a data block `prior_review`: "Findings from this ticket's previous review (`none` when there is none)". A finding that restates one of those starts its `message` with "Still open: ". Bump `version` to "1.3" (minor: the review baseline binds only the major).
- In: `chupa/stages.py`: `review_stage` takes the prior-review text and passes it as `prior_review`; `review` reads the canonical `tickets/<stem>/review.md` before writing its own, and passes its findings (one line per finding, as `findings_text` formats them) when that review was a `snag`, else "none".
- In: `eval/harness.py`: its `review_stage` passes `prior_review: "none"`.
- In: `tests/test_specs.py`: the review inputs tuples and version pins in `test_review_spec_read_only` and `test_review_spec_checks_docs`; assert the new Task rules are in the body.
- In: `tests/test_stages.py`: the `spec_version == "1.2"` pin.
- In: `tests/test_drain_reentry.py`: in the snag-then-retry test, assert the second Review prompt contains `SNAG["message"]` inside the `prior_review` block and the first Review prompt's block is `none`.
- In: `docs/how-chupa-works.md` section 4.4: Review also gets the previous review's findings and reports every defect in one pass.
- Out: the `ReviewVerdict`/`Finding` schema, review codes, the baseline fixtures, every other spec.

## Scope fence
- specs/review.md
- chupa/stages.py
- eval/harness.py
- tests/test_specs.py
- tests/test_stages.py
- tests/test_drain_reentry.py
- docs/how-chupa-works.md

## Acceptance criteria
1. On a retry after a snag, the second Review prompt's `prior_review` block contains the first review's finding message, and the first Review prompt's block is `none` (the test fails if prior findings are dropped or leak into a first review), checked by `uv run pytest tests/test_drain_reentry.py`.
2. `uv run pytest tests/test_specs.py` exits 0 with the review spec at version "1.3" and inputs `("ticket", "diff", "prior_review", "retry_findings")`.
3. `docs/how-chupa-works.md` section 4.4 states both behaviors.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_drain_reentry.py tests/test_specs.py
uv run pytest -q
```

## Definition of rejected
The review spec's major version changes; `Finding` or `ReviewVerdict` changes; baseline fixtures change.

## Time budget
- expected: 40m
- stuck: 90m
