---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- none

## Context
- tests/unit/test_specs.py

## On-demand
- chupa/specs/implement.md
- tests/integration/test_stages.py

## Goal / Why
Implement replied `ok` when tests named by acceptance criteria were missing, sat in a different file from the one the criterion names, or checked less than the criterion requires. Each case cost an acceptance snag, a Diagnose and a retry (retro/42). On retro-finding-recurrence attempt 1, criterion 2's test existed only in tests/integration/test_retro.py, not the named tests/unit/test_retro_recurrence.py. Criterion 3 covered one of three listed emit_proposals cases. On journal-incremental-read attempt 2, criterion 2 required the same-instance read() to equal a fresh Journal's read() by value and order, but the test compared only body['n']. Both Diagnoses had to tell Implement to map every criterion to a test in the exact file it names. `chupa/specs/implement.md` has rules on suite placement and assertion strength but no step that matches each criterion to a test before `ok`.

After this change Task in the implement spec has a step before the commit step: before replying `ok`, match each acceptance criterion that names a test to a committed test in the file it names, covering every case it lists and making the comparison it states. Overcorrection guards: one parametrized test may cover several cases or criteria, so no test per bullet is required; and a criterion that names the wrong suite for the test's kind is reported in `surprises` or as a premise finding, never followed by putting the test in the wrong suite.

## Scope in / Scope out
- In: `chupa/specs/implement.md`: add the criteria-to-tests step to Task, immediately before the commit step, and bump `version` to the next minor above its value at the base commit (sibling spec tickets may have bumped it since).
- In: `tests/unit/test_specs.py`: the implement version pins (the loop over spec versions and `test_implement_spec_consumer_read`) move to the new version, plus assertions that the new step's phrases are in the spec's Task.
- In: `tests/integration/test_stages.py`: the `spec: implement` pin in the run-record assertion moves to the new version.
- Out: Check code, `chupa/stages.py`, the Review and Diagnose specs, the packing-slip schema, every other spec, and the existing test-placement and assertion-strength paragraphs.

## Scope fence
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py

## Acceptance criteria
1. `chupa/specs/implement.md` is at a version one minor above its value at the base commit, and its Task contains a step before the commit step with the phrases `committed test in the file it names`, `every case it lists` and `the comparison it states`. `./dev.py test tests/unit/test_specs.py` asserts each phrase, which rules out the base spec that has no such step.
2. The spec Task states that one parametrized test may cover several cases or criteria, and that a criterion naming the wrong suite is reported in `surprises` or as a premise finding, never followed by placing the test in the wrong suite. `./dev.py test tests/unit/test_specs.py` asserts both, which rules out a step that demands one test per criterion bullet or a test in the wrong suite.
3. The run-record assertion pins the new `spec: implement` version. `./dev.py test tests/integration/test_stages.py` rules out a stale pin.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected
The step requires one test per criterion bullet; it tells Implement to place a test in a suite that does not fit its kind because a criterion names it; it is placed after the commit step; existing sequential-run, base-red, or assertion-strength rules are weakened; the implement spec's major version changes; the packing-slip schema or finding codes change; any other spec changes.

## Time budget
- expected: 20m
- stuck: 45m
