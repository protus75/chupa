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
- tests/unit/test_specs.py

## On-demand
- chupa/specs/implement.md
- docs/how-chupa-works.md

## Goal / Why
Implement replied `premise_failed` and left finished, scoped work uncommitted when the only red in a full-suite `## Verification` command was already red on the base commit. This happened on phase7-continue attempt 9 and on attempt 0 of attempts-cap, bug-evidence-intake, review-surfaces-refused, ticket-changed-midrun and verdict-human-only, and each attempt was then re-run or parked. `chupa/specs/implement.md` step 3 ("make each one exit 0") and its On-failure text ("reply `premise_failed` naming the command") tell it to do this. Neither says that Check attributes base-confirmed red to main and does not fail the ticket for it. After this change the spec says that failures verified on the base commit are not a premise failure: the implementer commits, replies `ok`, and lists them in `second_problems` and `surprises`. The rule guards against overcorrection: failing tests are compared with the base run by name, any failure not on the base list is fixed, and `premise_failed` stays for criteria-forced edits outside the fence.

## Scope in / Scope out
- In: `chupa/specs/implement.md`: add one rule to Task step 3 and one sentence to On-failure. The rule: when a Verification command still fails after your work, rerun it on the base commit and compare the failing tests by name. A failure that also fails on the base commit is not a premise failure; commit, reply `ok`, and report each such failure in `second_problems` and `surprises`. A failure not on the base list is yours to fix. Never label a failure base-red without running it on the base commit. A failure that passes on the base commit and needs an edit outside `## Scope fence` stays a `premise_failed` finding. Bump `version` to "2.4".
- In: `tests/unit/test_specs.py`: the implement version pins ("2.3" to "2.4") in both places, and an assertion that the new rule text is in the rendered Task.
- In: `tests/integration/test_stages.py`: the `spec: implement 2.3` pin in the run-record assertion.
- In: `docs/how-chupa-works.md` Implement section: one sentence that failures reproduced on the base commit are reported as second problems, not `premise_failed`.
- Out: Check attribution code (`chupa/stages.py`), the packing-slip schema, finding codes, every other spec.

## Scope fence
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `chupa/specs/implement.md` is at version "2.4", lints clean, stays within the line limit, and its rendered Task contains the base-red rule. `./dev.py test tests/unit/test_specs.py` checks this. The test asserts the rule's exact text, which rules out the 2.3 spec, where a base-red failure was still told to end in `premise_failed`.
2. The rule requires comparing failing tests by name with the base run, fixing any failure not on the base list, and keeping `premise_failed` for forced edits outside the fence. `./dev.py test tests/unit/test_specs.py` asserts each of the three phrases, which rules out a rule that excuses every red command.
3. The run-record assertion pins `spec: implement 2.4`. `./dev.py test tests/integration/test_stages.py` rules out the stale 2.3 pin.
4. `docs/how-chupa-works.md` states that base-confirmed failures are reported as second problems rather than `premise_failed`.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected
The rule lets Implement skip a failure without comparing it by name against a base run; `premise_failed` is no longer used for fence walls; the implement spec's major version changes; the packing-slip schema or finding codes change; any other spec changes.

## Time budget
- expected: 20m
- stuck: 45m
