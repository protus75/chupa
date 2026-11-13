---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- none

## Context
- tests/unit/test_specs.py::test_implement_spec_consumer_read
- tickets/implement-spec-base-red-not-premise/ticket.md

## On-demand
- chupa/specs/implement.md

## Goal / Why
Implement treated an intermittent failure outside its diff as a premise failure. On lint-requisition-decidable-rules attempt 2, `./dev.py test` failed only on `tests/integration/test_serve_dispatch.py::test_kill_aborts_requested_retro` with a timeout in `serve_rig.until`. The same command passed on the base commit, and the candidate's own integration gate later passed it. Implement left finished work uncommitted and replied `premise_failed`, citing the Task step 3 sentence "A failure that passes on the base commit and requires an edit outside `## Scope fence` remains a `premise_failed` finding." That spent a `premise_bounce` cap, four Diagnose calls (all gave the same correction) and a rung escalation on a buildable ticket. Attempt 3 built the same scope and merged (retro/44, Suggestion Box message box-000428-96d00473).

The spec's only flake carve-out covers timing failures that appear when test runs overlap. A sequential intermittent timeout is not covered, so every red that is green on base is read as deterministic. `implement-spec-base-red-not-premise` covers reds that are red on base, not green-on-base flakes. The flake-check, flake-detection and flake-release tickets are engine-side Check machinery and do not change Implement's reply rule.

The repair is one isolated-rerun step. Before applying the base-passes clause, Implement reruns each such failing test alone on the candidate. If it passes there and the diff does not reach the test's scenario, it is an intermittent failure: commit, reply `ok`, and report it in `second_problems` and `surprises`. A failure that reproduces on the isolated rerun stays `premise_failed`. One isolated rerun is the only evidence allowed; rerunning the full suite until it passes proves nothing.

Task step 2 says to verify that a failure you did not cause also fails on the base commit before reporting it. An intermittent failure that is green on base cannot meet that check, so the new paragraph says it overrides step 2 for this case. Step 2 itself stays unchanged, and this ticket adds the assertion that pins it; no test pins it today.

This rule governs every host's Implement runs. Its single home is the prompt spec; no `CLAUDE.md`, `AGENTS.md` or `CORE_TEMPLATE` change is needed.

The Author stage drafted this ticket from box-000428-96d00473 and ran out of calls one finding short of approval; this ticket is that draft with the last review finding repaired.

## Scope in / Scope out
- In: add one paragraph to `chupa/specs/implement.md` Task step 3, directly after the sentence ending "remains a `premise_failed` finding." That sentence stays byte-identical. The paragraph says: when a failing test is green on the base commit and fixing it would need an edit outside `## Scope fence`, first rerun that test alone on the candidate. If it passes alone and the diff does not reach the test's scenario (no changed file is imported, called or exercised by that test), treat it as an intermittent failure: commit, reply `ok`, and report it in `second_problems` and `surprises`. For this case only, this paragraph overrides step 2's requirement that a failure also fails on the base commit before you report it. One isolated rerun is the only evidence; never rerun the full suite until it passes and count that as proof. A failure that reproduces on the isolated rerun, or a test whose scenario the diff reaches, stays a `premise_failed` finding.
- In: bump the spec's `version` to the next minor above the version on main, and update every test pin for it.
- In: `tests/unit/test_specs.py::test_implement_spec_consumer_read` gains the assertions the criteria name, including a new verbatim assertion of the unchanged step 2 sentence.
- Out: engine-side flake detection, Check machinery, and every other spec (diagnose, review, requisition_review).
- Out: any change to the wording of step 2 or of the existing step 3 base-passes sentence.

## Scope fence
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py

## Acceptance criteria
1. `tests/unit/test_specs.py::test_implement_spec_consumer_read` asserts verbatim, in the whitespace-normalized rendered task, the new sentence holding the isolated-rerun step with the condition that the diff does not reach the test's scenario, and that the intermittent failure is committed with reply `ok` and reported in `second_problems` and `surprises`. This rules out a spec that omits the scenario condition.
2. `tests/unit/test_specs.py::test_implement_spec_consumer_read` asserts verbatim the sentence saying a failure that reproduces on the isolated rerun, or a test whose scenario the diff reaches, stays a `premise_failed` finding. This rules out a step that excuses every out-of-fence red.
3. `tests/unit/test_specs.py::test_implement_spec_consumer_read` asserts verbatim the sentence containing "never rerun the full suite until it passes and count that as proof". This rules out a step that accepts a passing full-suite rerun as evidence.
4. `tests/unit/test_specs.py::test_implement_spec_consumer_read` asserts verbatim the sentence saying this paragraph overrides step 2's base-fail requirement for this case. This rules out two instructions that cannot both hold and leave Implement refusing to report the flake.
5. `tests/unit/test_specs.py::test_implement_spec_consumer_read` gains a new verbatim assertion, against the whitespace-normalized rendered task, of the step 2 sentence "Before reporting a failure you did not cause, verify that it also fails on the base commit." This is the test that rules out rewording or removing step 2. The existing assertion of the step 3 sentence ending "remains a `premise_failed` finding." still passes unchanged, which rules out rewording that sentence.
6. The `version` in `chupa/specs/implement.md` is the next minor above the version on main. `tests/unit/test_specs.py` (both `test_spec_lint_accepts_the_implement_and_requisition_specs` and `test_implement_spec_consumer_read`) and the `spec: implement` line in `tests/integration/test_stages.py` pin the new version, which rules out a bump that leaves a stale pin.
7. `./dev.py test tests/unit/test_specs.py tests/integration/test_stages.py` exits 0.

## Verification
```
./dev.py test tests/unit/test_specs.py tests/integration/test_stages.py
```

## Definition of rejected
- The step lets Implement commit past a failure that reproduces on the isolated rerun, or past a test whose scenario the diff reaches.
- The step accepts a full-suite rerun that happens to pass as proof, or the full-suite ban sentence can be dropped without a test failing.
- The new paragraph does not state that it overrides step 2 for this case, leaving step 2 and step 3 contradictory.
- The step 2 sentence or the existing base-passes sentence is reworded or removed, or the step 2 sentence can be reworded without a test failing.
- A new assertion would also pass on a spec without the sentence it names.
- The version is bumped to anything other than the next minor above main, or a pin is left stale.

## Time budget
- expected: 15m
- stuck: 45m
