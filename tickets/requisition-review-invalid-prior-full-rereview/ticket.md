---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: confirmed
---

## Depends on
- requisition-review-bare-json-reply

## Context
- tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs
- tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
The `## Task` rule in `chupa/specs/requisition_review.md` says "Raise a NEW finding only against text the diff shows changed since that review." It has no exception for a prior review whose reply failed the schema check. In `core-drift-activation`, attempt 7 found a real snag: `tests/test_serve.py` was missing from the fence, and that file imports the `repository()` constructor used in `test_restart_timers.py`. The reply put prose before its JSON, so it failed the schema and the snag was discarded. At attempt 8 the ticket text was unchanged, so the reviewer ruled the earlier finding a schema error only and approved. Implement then failed three times with `premise_failed` on that constructor, which produced `plan-gap-31` and `plan-gap-32` and ended in the Reject queue.

After this change the `## Task` rule says that when the prior review is invalid (its finding reads "invalid requisition review reply"), that review clears nothing and judges nothing. The reviewer then reviews the whole ticket again, including the transitive import and composition closure of the fence. The new-finding-only-against-the-diff limit still applies to every other prior review, so approved seeds are not re-reviewed each round. The success measure for later retro windows: no `approve` requisition_verdict directly follows a schema-invalid requisition_verdict on an unchanged ticket unless the whole ticket was reviewed again.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`. In `## Task`, directly after the sentence ending "Raise a NEW finding only against text the diff shows changed since that review.", add a sentence containing the exact phrase "A prior review reporting an invalid requisition review reply clears nothing". That sentence says such a review has no findings to rule on, so review the whole ticket again, including the transitive import and composition closure of the fence, and the changed-text limit does not apply. Bump `version` to the next minor above the version on `main` when this runs (`3.7` today, so `3.8`). The spec stays within the 200-line `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: the pinned `requisition_review` version becomes `3.8`.
- In: `tests/integration/test_requisition.py::test_spec_loads_and_names_finding_keys`: also assert the exact phrase above is in the spec source.
- Out: any change to `chupa/requisition.py` (reply parser, schema, retry loop), the other `## Task` rules, the Output format and On-failure sections, and how `prior_review` is built.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py
- tests/integration/test_requisition.py

## Acceptance criteria
1. `chupa/specs/requisition_review.md` contains `A prior review reporting an invalid requisition review reply clears nothing` and `version: "3.8"`, not `3.7`.
2. `tests/integration/test_requisition.py` asserts the phrase, and `./dev.py test tests/unit/test_specs.py tests/integration/test_requisition.py` passes; the asserting test fails on a spec lacking the phrase, so a spec still carrying only the changed-text-limit rule is ruled out.
3. `tests/unit/test_specs.py` pins `3.8` as the `requisition_review` version, so a spec left at `3.7` fails it.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py tests/integration/test_requisition.py
./dev.py test
```

## Definition of rejected
The change edits `chupa/requisition.py` or any other engine code, removes the changed-text limit for prior reviews that are schema-valid, or alters the Output format or On-failure sections.

## Time budget
- expected: 15m
- stuck: 40m
