---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
none

## Context
- chupa/requisition.py
- chupa/driver.py
- tests/test_requisition.py
- chupa/author.py
- chupa/runner.py
- chupa/__main__.py

## Goal / Why
On 2026-11-06, `chupa review engine-lifecycle-log` snagged three times in a row with "invalid requisition review reply: 1 schema error(s)" and no findings. The reviewer's reply (spooled at `review-engine-lifecycle-log/14579/0/requisition_review/call-01/output.txt`) was a valid snag. It was preceded by one sentence of prose, so `unwrap_fence` found no whole-reply fence and `RequisitionReply.model_validate_json` failed. `requisition.review_ticket` makes one call and turns any invalid reply into a mechanical snag. Other model calls go through the driver, which re-prompts with the findings up to `caps.retry`.

After this change, `review_ticket` re-asks on an invalid reply, passing the parse error through the spec's existing `retry_findings` input, up to `driver.retry_cap` re-asks. Only when every reply is invalid does it return today's `invalid reply` snag.

## Scope in / Scope out
- In: `chupa/requisition.py` `review_ticket`: the call, spool, and parse steps loop.
  - The first call renders `retry_findings` as `"none"`, as today.
  - On a `ValidationError`, it renders `retry_findings` with the error. The text says the reply must be only the JSON object, and includes `str(exc)`. Then it calls again with the next `call_seq`, so each call has its own effect key and spool directory.
  - At most `driver.retry_cap` re-asks. If the last reply is still invalid, it returns the existing mechanical snag (`mechanical="invalid reply"`).
  - The timeout, provider-error, and render-bound paths are unchanged.
- In: every caller that passes `call_seq` (`chupa/author.py`, the `review` verb in `chupa/__main__.py`, and the dispatch review in `chupa/runner.py`) keeps unique effect keys with the extra calls. If one would collide, change it only as far as needed, and say so in the run record.
- In: tests in `tests/test_requisition.py`.
  - `test_invalid_reply_is_reprompted_then_accepted`: the first scripted reply is prose followed by a fenced valid snag, and the second is the bare valid snag. The verdict is that snag with its findings, there are 2 requests, and the second request's prompt contains the parse error.
  - Update `test_snag_and_invalid_reply`: when every reply is invalid, the result is the `invalid reply` mechanical snag after exactly `1 + retry_cap` requests.
- Out: making the parser accept prose around the JSON, the driver, the spec text, and the verdict schema.

## Scope fence
- chupa/requisition.py
- tests/test_requisition.py

## Acceptance criteria
1. `uv run pytest -q tests/test_requisition.py` exits 0, including the new and updated tests.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_requisition.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- an invalid reply is still turned into a snag without a re-ask;
- the parser is loosened to accept prose around the JSON;
- two calls in one review share an effect key;
- the re-ask count exceeds `driver.retry_cap`.

## Time budget
- expected: 30m
- stuck: 90m
