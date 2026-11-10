---
priority: P2
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
- config.yaml

## On-demand
- chupa/specs/implement.md
- docs/how-chupa-works.md

## Goal / Why
Implement replied `ok` after running only the ticket's `## Verification` commands, and Check then failed on gates it never ran. spec-base-measurement-method attempt 0 failed the lint gate (ruff E501 at tests/unit/test_specs.py:86) although both Verification commands passed. reoffer-infra-no-retry-draw attempt 3 failed the integration gate on tests/integration/test_shakeout.py, a test outside the fenced Verification set, and cost a reject-queue keep. Task step 3 of `chupa/specs/implement.md` already tells Implement to run hard coverage gates once after its last edit. It says nothing about the other hard `trigger: always` host checks (in this repo `lint`, `format`, `unit`, `integration`). After this change, step 3 also requires Implement to run each hard always-trigger host Check entry once after its last edit and before replying `ok`, and says Check runs all of them on the candidate. Overcorrection guards: the run is one pass after the last edit, not after every edit; a failure outside `## Scope fence` is reported as a forced file or in `second_problems`, never edited; formatter and lint fixes apply only to files the ticket changed.

## Scope in / Scope out
- In: `chupa/specs/implement.md`: extend Task step 3 with the hard-check rule, including the exact sentence "Run each hard always-trigger host Check entry (a `review.mechanical` entry with `trigger: always` and `severity: hard`, such as lint, format and the full test suites) once after your last edit and before replying `ok`, because Check runs every one of them on the candidate." and the exact sentence "A failure in a file outside `## Scope fence` is reported as a forced file or in `second_problems`, never edited; apply lint and format fixes only to files the ticket changed." Bump `version` from "2.8" to "2.9".
- In: `tests/unit/test_specs.py`: the implement version pins (two, lines 25 and 71) move to "2.9", plus assertions that both sentences are in the rendered Task.
- In: `tests/integration/test_stages.py`: the `spec: implement 2.8` pin in the run-record assertion moves to 2.9.
- In: `docs/how-chupa-works.md` section 4.2: one sentence stating Implement runs the host's hard always-trigger checks once after its last edit.
- Out: Check code, `chupa/stages.py`, `config.yaml`, other specs, the packing-slip schema, ruff config, coverage measurement.

## Scope fence
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `chupa/specs/implement.md` is at version `2.9` and its rendered Task contains the exact sentence "Run each hard always-trigger host Check entry (a `review.mechanical` entry with `trigger: always` and `severity: hard`, such as lint, format and the full test suites) once after your last edit and before replying `ok`, because Check runs every one of them on the candidate." `./dev.py test tests/unit/test_specs.py` asserts it, which rules out the base spec that asks only for Verification commands and coverage gates.
2. The rendered Task contains the exact sentence "A failure in a file outside `## Scope fence` is reported as a forced file or in `second_problems`, never edited; apply lint and format fixes only to files the ticket changed." `./dev.py test tests/unit/test_specs.py` asserts it, which rules out a rule that lets Implement edit or reformat unrelated files to turn the tree green.
3. The run-record assertion pins `spec: implement 2.9`. `./dev.py test tests/integration/test_stages.py` rules out a stale 2.8 pin.
4. `docs/how-chupa-works.md` section 4.2 states that Implement runs the hard always-trigger host checks once after its last edit.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected
The rule asks for a check run after every edit; permits edits outside `## Scope fence` or reformatting of files the ticket did not change; weakens the coverage-gate, sequential-run or base-red rules; changes the implement spec's major version, the packing-slip schema or finding codes; or changes any other spec.

## Time budget
- expected: 20m
- stuck: 45m
