# Review: approve

The diff removes the default from `review_ticket`'s `prior`, adds `FIRST_REVIEW` and returns it from `prior_review` instead of `none`, and makes `author.py` pass `prior=FIRST_REVIEW`. It updates the spec text and bumps its version to 3.9, makes every listed test and script caller pass `prior=FIRST_REVIEW`, and updates the first-review assertions. The production callers in `__main__.py`, `runner.py` and `rework.py` already pass `prior`, and no file outside the scope fence changes.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "cbffd8cf9068c785ede0d72e96dd3c1ba3a2edd2",
  "stem": "requisition-prior-required",
  "reviewed_sha": "cbffd8cf9068c785ede0d72e96dd3c1ba3a2edd2",
  "summary": "The diff removes the default from `review_ticket`'s `prior`, adds `FIRST_REVIEW` and returns it from `prior_review` instead of `none`, and makes `author.py` pass `prior=FIRST_REVIEW`. It updates the spec text and bumps its version to 3.9, makes every listed test and script caller pass `prior=FIRST_REVIEW`, and updates the first-review assertions. The production callers in `__main__.py`, `runner.py` and `rework.py` already pass `prior`, and no file outside the scope fence changes.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
