---
state: rejected
source: human
priority: P1
kind: feature
---

## Depends on
- review-reprompt-invalid-reply

## Context
- chupa/runner.py
- chupa/requisition.py
- chupa/drain.py
- chupa/caps.py
- tests/test_requisition_gate.py

## Goal / Why
On 2026-11-05, fungo ticket `s9-pa-count-reconcile` was parked `premise_failed` at stage `requisition` with reason "[requisition_review] invalid requisition review reply: 1 schema error(s)". The reviewer's reply failed the schema check. The ticket content was fine. `drain.premise_parked` holds a `premise_failed` stem until its committed `ticket.md` changes, so this tooling failure could only be cleared by a human editing the ticket.

`review-reprompt-invalid-reply` makes `review_ticket` re-ask on an invalid reply, but leaves `chupa/runner.py` unchanged. When every re-ask is invalid, `drive` still turns the mechanical snag into `premise_failed`. The same happens for the `timeout` and `provider error` snags.

After this change, a dispatch requisition review that ends in a tool-failure snag ends the run `infra_error`, not `premise_failed`. The stem is retried under the existing caps and no ticket edit is needed.

## Scope in / Scope out
- In: `chupa/runner.py` `drive`, the requisition branch. When `review.mechanical` is `"invalid reply"`, `"timeout"`, or `"provider error"`, build `run` with an `infra_error` `StageResult` carrying `review.findings`, as the `ProviderCallError` branch does. Do not journal a `premise_failed` transition. The run then continues through the existing failure path (`harvest_failure`, caps).
- In: the `requisition_verdict` signal is still journaled for these snags, unchanged.
- In: the `render over headroom` and `review render over bound` snags and every non-mechanical snag or `rma` keep today's behavior: they are about ticket content and park `premise_failed`.
- In: tests in `tests/test_requisition_gate.py`:
  - `test_invalid_reply_ends_infra_error_not_premise_park`: every scripted reply is invalid (`1 + retry_cap` replies). `dispatch` does not return `premise_failed`; the last state transition is `infra_error`; `drain.premise_parked` is false for the unchanged ticket sha; no `implement` request was made.
  - `test_snag_parks_before_implement` is unchanged and still passes.
- Out: changing `review_ticket`, the re-ask loop, the reply schema, `drain.premise_parked`, cap values, and the Author and Rework requisition paths.

## Scope fence
- chupa/runner.py
- tests/test_requisition_gate.py

## Acceptance criteria
1. `uv run pytest -q tests/test_requisition_gate.py` exits 0, including the new test.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_requisition_gate.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- an `invalid reply`, `timeout`, or `provider error` requisition snag still journals `premise_failed`;
- a content snag (non-mechanical snag, `rma`, or a render-bound snag other than `render_feasibility`) no longer parks `premise_failed`;
- the change touches `review_ticket` or `drain.premise_parked`.

## Time budget
- expected: 20m
- stuck: 60m
