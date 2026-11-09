---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- set-membership-fence-closure

## Context
- tests/unit/test_specs.py

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
Requisition review approved `drain-upgrade-own-source` twice, and both approvals said every test that expects a handoff was fenced. Implement attempt 1 then hit `premise_failed`: `tests/test_daemon_composition.py:1613` expects a spawned child after a merge in a temp host repo, and the new repo-equals-ENGINE guard blocks that. The test never names the changed symbol, so a closure traced by reference alone missed it. `chupa/specs/requisition_review.md` traces the reference closure, the recorded-value closure and listed coverage dependents, and none of them asks whether a test asserts an outcome that a narrowed condition now blocks. After this change the fence bullet adds a behavioral closure. When Scope in narrows or widens a condition that gates an observable outcome (a journaled signal, a spawn count, a return value), search all of `tests/` for assertions on that outcome, and fence every test whose assertion would fail under the changed condition. The rule is limited to tests whose assertion would fail. A test that only touches the outcome and still passes, such as a drain that asserts only exit 0, is not a hit.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`: add the behavioral closure to the first fence bullet of Task with the stated limit, and bump `version` from "3.4" to "3.5" (3.4 is set by `set-membership-fence-closure`).
- In: `tests/unit/test_specs.py`: the `requisition_review` version pin moves to "3.5", plus an assertion that the new closure phrases are in the spec body.
- Out: every other spec, Check and requisition code, `docs/`, and any lint that enforces the rule.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py

## Acceptance criteria
1. `chupa/specs/requisition_review.md` is at version "3.5" and its body contains the phrases `narrows or widens a condition` and `assertions on the observable outcome`. `./dev.py test tests/unit/test_specs.py` asserts both, which rules out the 3.4 spec that traces only symbols, bumped values and set members.
2. The body also contains the phrase `whose assertion would fail`, asserted by `./dev.py test tests/unit/test_specs.py`, which rules out a rule with no stated limit that fences every test touching the outcome.
3. The version pin in `tests/unit/test_specs.py` reads "3.5" for `requisition_review`, so `./dev.py test tests/unit/test_specs.py` fails on a spec left at 3.4.

## Verification
```
./dev.py test tests/unit/test_specs.py
```

## Definition of rejected
The rule lacks the stated limit and sweeps in every test touching the outcome; the version is not bumped or the pin keeps the old value; the existing reference-closure, recorded-value, or set-membership text is weakened; any file outside `## Scope fence` changes.

## Time budget
- expected: 15m
- stuck: 40m
