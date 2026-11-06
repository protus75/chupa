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
- chupa/rework.py
- chupa/llmeffect.py
- chupa/runner.py
- chupa/__main__.py
- tests/test_author.py
- tests/test_rework.py

## Goal / Why
On 2026-11-06, `chupa review engine-lifecycle-log` snagged three times in a row with "invalid requisition review reply: 1 schema error(s)" and no findings. The reviewer's reply (spooled at `review-engine-lifecycle-log/14579/0/requisition_review/call-01/output.txt`) was a valid snag. It was preceded by one sentence of prose, so `unwrap_fence` found no whole-reply fence and `RequisitionReply.model_validate_json` failed. `requisition.review_ticket` makes one call and turns any invalid reply into a mechanical snag. Other model calls go through the driver, which re-prompts with the findings up to `caps.retry`.

After this change, `review_ticket` re-asks on an invalid reply, passing the parse error through the spec's existing `retry_findings` input, up to `driver.retry_cap` re-asks. Only when every reply is invalid does it return today's `invalid reply` snag.

## Scope in / Scope out
- In: `chupa/requisition.py` `review_ticket`: the call, spool, and parse steps loop.
  - The first call renders `retry_findings` as `"none"`, as today.
  - On a `ValidationError`, it renders `retry_findings` with the error. The text says the reply must be only the JSON object, and includes `str(exc)`. Then it calls again with the next `call_seq` (`call_seq + 1`, ...), so each call has its own effect key (`llmeffect.llm_key`) and spool directory.
  - At most `driver.retry_cap` re-asks. If the last reply is still invalid, it returns the existing mechanical snag (`mechanical="invalid reply"`).
  - The timeout, provider-error, and render-bound paths are unchanged.
- In: `RequisitionVerdict` gets `calls: int`, the number of model calls the review made: 0 on the no-call snag paths, and 1 plus the re-asks otherwise.
- In: callers that make several reviews under one key prefix advance by `calls`, so no two calls share a key.
  - `chupa/rework.py`: `review_seq` moves forward by `verdict.calls` instead of by 1, and each review starts at the next unused `call_seq`.
  - `chupa/author.py`: the requisition review stops passing the Author call's `call_seq`. It keeps its own review counter for the pass, starting at 1 and advanced by `verdict.calls`.
  - When no review re-asks, every key value equals today's, so existing key-pinning tests are unchanged.
  - Unchanged: `chupa/runner.py` (one review per dispatch attempt) and the `review` verb in `chupa/__main__.py` (its own `run_seq` per invocation).
- In: tests.
  - `tests/test_requisition.py` `test_invalid_reply_is_reprompted_then_accepted`: the first scripted reply is prose followed by a fenced valid snag, and the second is the bare valid snag. The verdict is that snag with its findings, `calls == 2`, there are 2 requests, and the second request's prompt contains the parse error.
  - Update `tests/test_requisition.py` `test_snag_and_invalid_reply`: when every reply is invalid, the result is the `invalid reply` mechanical snag, with `calls == 1 + retry_cap` and that many requests.
  - `tests/test_rework.py` `test_split_reviews_keep_unique_keys_when_one_reasks`: with two proposals whose first review re-asks once, the journal's `requisition_review` effect keys are all distinct.
  - `tests/test_author.py` `test_author_reviews_keep_unique_keys_when_one_reasks`: with two Author calls whose first requisition review re-asks once, the journal's `requisition_review` effect keys are all distinct.
- Out: making the parser accept prose around the JSON, the driver, the spec text, the reply schema, and key values when no review re-asks.

## Scope fence
- chupa/requisition.py
- chupa/rework.py
- chupa/author.py
- tests/test_requisition.py
- tests/test_rework.py
- tests/test_author.py

## Acceptance criteria
1. `uv run pytest -q tests/test_requisition.py tests/test_rework.py tests/test_author.py` exits 0, including the new and updated tests.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_requisition.py tests/test_rework.py tests/test_author.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- an invalid reply is still turned into a snag without a re-ask;
- the parser is loosened to accept prose around the JSON;
- any two model calls share an effect key;
- the re-ask count exceeds `driver.retry_cap`;
- a key value changes when no review re-asks.

## Time budget
- expected: 30m
- stuck: 90m
