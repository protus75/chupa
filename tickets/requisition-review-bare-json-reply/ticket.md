---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: confirmed
---

## Depends on
- none

## Context
- tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs
- tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
The requisition reviewer sometimes wraps its verdict JSON in a prose paragraph and a ```json code fence. That breaks the 'ONLY one JSON object' contract in `chupa/specs/requisition_review.md`. In the retro window, 11 `requisition_verdict` events carry the finding 'invalid requisition review reply: 1 schema error(s)' (for example seeding `phase3-continue-02`, `-09` and `-12`). The `phase3-continue-12` attempt 1 reply opens with prose and then fences an otherwise valid approve object. Each such failure becomes a `requisition_review` gate_failed retry on a ticket the reviewer judged buildable, which costs an extra attempt.

After this change the Output format and On-failure sections state concretely that the first character of the reply is `{` and the last is `}`, with no prose, markdown or code fence around it, that reasoning belongs in `summary`, and that a schema error reported in `retry_findings` is fixed by re-emitting the same verdict as bare JSON. The success measure is a lower share of `requisition_verdict` events carrying the 'invalid requisition review reply' finding in later retro windows.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`. In `## Output format`, after the first line, add a sentence containing the exact phrase "The first character of your reply is `{` and the last is `}`" and stating that no prose, markdown or code fence surrounds the object and that the reasoning goes in `summary`. In `## On-failure`, add a sentence containing the exact phrase "re-emit the same verdict as bare JSON" saying that when `retry_findings` reports an invalid reply schema, the reply repeats the same verdict and findings without changing them. Bump `version` to the next minor above its value at the base commit (`3.3` when drafted; sibling spec tickets may have bumped it since). The spec stays within the 200-line `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: the pinned `requisition_review` version moves to that new version.
- In: `tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys`: also assert both exact phrases are in the spec source.
- Out: any change to the engine reply parser or schema in `chupa/requisition.py` (it must not be loosened to accept fenced replies), the allowed verdicts and finding fields, the `## Task` rules, and the routing of tool-failure snags (ticket `requisition-tool-failure-retries`).

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- tests/integration/test_requisition.py

## Acceptance criteria
1. `chupa/specs/requisition_review.md` contains both new phrases and a `version` one minor above its value at the base commit.
2. `tests/integration/test_requisition.py` asserts both phrases, and `./dev.py test tests/unit/test_specs.py tests/integration/test_requisition.py` passes; the asserting test fails on the unchanged spec, which lacks the phrases.
3. `tests/unit/test_specs.py` pins the new `requisition_review` version, so a spec left at its base-commit version fails it.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py tests/integration/test_requisition.py
./dev.py test
```

## Definition of rejected
The change edits `chupa/requisition.py` or any other engine code, loosens the reply parser to accept fenced replies, changes the allowed verdicts or finding fields, or alters the `## Task` rules.

## Time budget
- expected: 15m
- stuck: 40m
