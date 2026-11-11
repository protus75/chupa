---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: rejected
---

## Depends on
- none

## Context
- tests/unit/test_specs.py

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
Spec line 29 of `chupa/specs/requisition_review.md` only asks for one sentence explaining why the change does not affect a coverage dependent. On `stage-event-owner-stem` the reviewer cleared dependents by saying the new nesting refusal "does not fire on any merged path". Implement then hit `premise_failed`: `tests/integration/test_provider_cooldown_failover.py::test_mid_run_drought_is_harvested_without_spine_draws` monkeypatches `stages.check` to run `Driver.run` and `review_ticket` inside the open Check stage, so the test's own patching reached the new refusal. That cost an Implement attempt, a `premise_bounce` unit and three Diagnose calls, and all three named the same fence gap.

After this change the spec states that a test whose own monkeypatch or fake reaches a newly added refusal, raise, or precondition in a way that violates it is a fence hit, even when no merged production path triggers it. The rule is limited to patched behavior that actually breaks the new precondition; a patch that never reaches it, or whose behavior satisfies it, is not a hit.

This is distinct from the open behavioral-closure idea, which searches for assertions on a gated outcome. This rule is about a test's setup (patch or fake) reaching the new refusal while its assertion is about something else. Both edit the same spec and version pin; whichever merges second bumps from the then-current version.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`:
  - Add one `## Task` bullet after the coverage-dependents bullet: when Scope in adds a refusal, raise, or new precondition, grep `tests/` for monkeypatches or fakes of the functions that reach it. A test whose patched or faked behavior violates the new precondition is a fence hit that must be fenced, even if no merged production path triggers it, and a clearance reasoning only about merged production paths is not valid for it. A patch that never reaches the precondition, or whose behavior satisfies it, is not a hit.
  - `version` goes from "3.9" to "3.10".
- In: `tests/unit/test_specs.py` moves the `requisition_review` pin from "3.9" to "3.10" and adds assertions that the rendered Task contains the new rule and its limit.
- Out: any other spec, engine code, and the existing coverage-dependents bullet text.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py

## Acceptance criteria
1. `tests/unit/test_specs.py` asserts `requisition_review` is version "3.10", not "3.9".
2. `tests/unit/test_specs.py` asserts the rendered Task contains the phrases "monkeypatches or fakes", "even if no merged production path triggers it", "a clearance reasoning only about merged production paths is not valid", and "A patch that never reaches the precondition, or whose behavior satisfies it, is not a hit". The last two appear only in the new bullet, so a spec that lacks the clearance-invalidation clause or the limit fails; the generic phrase "is not a hit" is not asserted because the spec already contains it elsewhere.
3. `./dev.py test tests/unit/test_specs.py` exits 0.

## Verification
```
./dev.py test tests/unit/test_specs.py
```

## Definition of rejected
- The new bullet fences every test that patches a nearby function, with no limit to patched behavior that violates the new precondition.
- `version` stays "3.9" or the pin in `tests/unit/test_specs.py` is not updated.
- Any file outside the fence changes.

## Time budget
- expected: 10m
- stuck: 25m
