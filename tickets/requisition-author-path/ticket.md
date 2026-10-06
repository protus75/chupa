---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- requisition-review
- author-stage

## Context
- chupa/driver.py
- tests/test_driver.py

## Plan contract
- 19.L
- 19.P2
- section 7
- section 11
- section 12

## Goal / Why
Every box-authored ticket is feasibility-reviewed before it commits (section 7): a `snag` re-authors within the Author driver's local allowance, an `rma` ends the invocation at once with a decision record, and only an `approve` commits. The verdict is journaled on the committed stem, so a draft carries its verdict and the later human `confirm` re-runs nothing.

Why: `author-stage` commits on grammar alone. A grammar-valid ticket that cannot be built becomes eligible work that parks at its first Implement. `requisition-review` built the call with no consumer; this is the first.

Owners (19.P2 REQUISITION WIRING, section 9 ownership law): `chupa/driver.py` owns the gate loop and gains the generic hooks. `chupa/author.py` owns the Author stage and wires the review into it. `tests/test_triage.py` is fenced because every triage script that reaches Author now supplies the mandatory review reply. `chupa/requisition.py` is called, never changed.

## Scope in / Scope out
- In: `chupa/driver.py`, `LlmStage` gains two generic fields:
  - `review: Callable[[BaseModel, int], Awaitable[GateReport]] | None = None`. After the synchronous gates run (whether or not they pass), the driver awaits `review(artifact, call_seq)`, raced against the same stuck deadline. A `fail` report is a hard failure fed back exactly like a hard gate (the review surface is a gate, section 11.1).
  - `terminal_findings: frozenset[str] = frozenset()`. When any hard finding of a call carries a code in this set, the driver returns `gate_failed` at once with EVERY hard finding of that call (the sync gates' and the review's), with no further re-prompt.
  - Every existing stage leaves both unset and behaves byte-identically.
- In: `chupa/author.py`: the author `LlmStage` sets `review` to a hook calling `review_ticket` on the stamped candidate with `stem_slot="author"`, `run_seq=<pass>`, `attempt=<message seq>`, `call_seq=<the author call_seq>`, at `routing_default_tier`, so the review is keyed `llm/author/<pass>/requisition_review/<seq>/<call_seq>` and never collides with the author call. An `rma` verdict's findings are re-coded `requisition_rma`, and `terminal_findings` is `{"requisition_rma"}`.
  - `approve`: commit as today, then journal `{"signal": "requisition_verdict", "verdict": "approve", "ticket_sha": ..., "provider": ..., "model": ..., "spec_version": ...}` on the stem.
  - `snag`: the findings re-prompt Author within its existing allowance.
  - `rma`, or an exhausted allowance: no ticket commits, and the failure decision record carries the review findings as evidence.
- In: `tests/test_triage.py`: each FakeLLM script that reaches Author gains a requisition reply after each author reply. Assertions on exact request counts, request lists, and LLM effect keys (e.g. `test_three_verdicts_and_second_pass_and_stale_author`) change only to include exactly the added `requisition_review` call and key; no other assertion changes.
- Out: the seed path (the next seed), any `chupa/requisition.py` or `chupa/triage.py` change, and a review at the human `confirm` flip.

## Scope fence
- chupa/driver.py
- tests/test_driver.py
- chupa/author.py
- tests/test_author.py
- tests/test_triage.py

## Acceptance criteria
1. `tests/test_driver.py` proves the hooks on a fake stage: a failing `review` report re-prompts with its findings; a finding whose code is in `terminal_findings` returns `gate_failed` after ONE call carrying both the sync gate's and the review's findings; a stage with neither hook makes the same requests as before.
2. `tests/test_author.py` proves an `approve` commits the ticket and journals one `requisition_verdict` signal, with the review keyed `llm/author/0/requisition_review/<seq>/1`.
3. `tests/test_author.py` proves a `snag` then `approve` sequence commits after two author calls, the second rendering the snag findings, and an `rma` commits nothing, makes exactly one author and one review request, and writes a `decision-<id>` record whose body names the rma findings.
4. `uv run pytest -q tests/test_triage.py` passes with only FakeLLM script additions and the request-count/request-list/key assertion edits for the added review call.
5. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_driver.py tests/test_author.py
uv run pytest -q tests/test_triage.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A box-authored ticket commits without an `approve` verdict for its committed text.
- The hooks change any existing stage's requests, keys, or outcomes.
- A second review call path, or a review keyed on an author call's key, exists.
- The diff touches a file outside the fence.

## Time budget
- expected: 75m
- stuck: 150m
