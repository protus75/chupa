---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/rework.py
- chupa/runner.py
- chupa/llmeffect.py
- chupa/journal.py
- tests/test_rework.py

## Goal / Why
When a ticket is dispatched without an approval, `runner.drive` reviews it with `review_ticket(..., stem_slot=ticket.stem, run_seq=attempt, attempt=attempt, call_seq=1)`. That records effect key `llm/<stem>/<A>/requisition_review/<A>/1`. If that attempt later reaches Rework, `chupa/rework.py` reviews each proposal under the same `stem_slot`, `run_seq` and `attempt`, with `review_seq` starting at 0 (first call 1). Its first proposal review gets the same key and replays the pre-run review's recorded answer instead of reviewing the proposal. Found by review on 2026-11-06.

After this change, Rework starts its review numbering after every `requisition_review` key already recorded for that ticket and attempt.

## Scope in / Scope out
- In: `chupa/rework.py`. Where `review_seq = 0` is set today, set `review_seq` to the highest `call_seq` among journal effect keys that start with `llm/<stem>/<attempt>/requisition_review/<attempt>/`, or 0 when there are none. Read it from `ctx.driver.journal.read()`, and parse the key's last part. `<stem>` and `<attempt>` are the values Rework already passes to `review_ticket`.
- In: `tests/test_rework.py` `test_split_reviews_after_pre_run_review_use_new_keys`: a ticket whose pre-run review recorded `.../requisition_review/<A>/1` is split by Rework in the same attempt. Every `requisition_review` effect key in the journal is distinct, and each proposal's review gets its own scripted reply.
- Out: `runner.py`, `review_ticket`, the key format, and Author.

## Scope fence
- chupa/rework.py
- tests/test_rework.py

## Acceptance criteria
1. `uv run pytest -q tests/test_rework.py` exits 0, including the test above.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_rework.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- a Rework review can reuse a key already in the journal;
- the starting number is passed in from another module instead of read from the journal;
- the key format changes.

## Time budget
- expected: 30m
- stuck: 90m
