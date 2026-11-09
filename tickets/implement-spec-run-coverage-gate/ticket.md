---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- implement-spec-sequential-final-run
- implement-spec-docs-sync-step

## Context
- tests/unit/test_specs.py
- config.yaml

## On-demand
- chupa/specs/implement.md
- docs/how-chupa-works.md

## Goal / Why
Implement replied `ok` after running only the ticket's `## Verification` commands, and the hard coverage gate (`unit`) then failed at Check. This happened on results-schema-2-reader attempt 0, review-lock-only-for-intake attempt 0 and core-drift-preflight attempt 2. A diagnosis said "That command passed while the unit gate failed." `chupa/specs/implement.md` forbids lowering a coverage threshold but never tells the agent to run the coverage gate. Each miss costs a full Check cycle and a Diagnose call. After this change, Task step 3 also requires Implement to run, once after its last edit, each hard coverage gate the host's Check configures (the `review.mechanical` entries that carry a `coverage` report), whenever the diff changes a file that gate measures. The rule guards against two overcorrections: (1) it is one run after the last edit, not a run per attempt step or per edit, and it is skipped when the diff touches no measured file; (2) a floor miss is fixed only by adding a test inside `## Scope fence`, or reported as `premise_failed` naming the file and floor when the fence blocks the needed test. Implement never restructures production code to dodge coverage.

## Scope in / Scope out
- In: `chupa/specs/implement.md`: extend Task step 3 with the coverage-gate rule above, including the exact sentence "A coverage floor miss is fixed with a test inside `## Scope fence`, or reported as `premise_failed` naming the file and its floor; never restructure production code to avoid coverage.", and bump `version` to the next minor above its value at the base commit ("2.6" when drafted; sibling spec tickets may have bumped it since).
- In: `tests/unit/test_specs.py`: the implement version pins (two) move to that new version, plus assertions that the rule text is in the rendered Task.
- In: `tests/integration/test_stages.py`: the `spec: implement` pin in the run-record assertion moves to that new version.
- In: `docs/how-chupa-works.md` section 4.2: one sentence stating that Implement runs the host's hard coverage gates once after its last edit.
- Out: Check code, `chupa/stages.py`, `config.yaml`, `test-gate.toml`, the packing-slip schema, every other spec, the sequential-run rule owned by `implement-spec-sequential-final-run`, the docs-sync step owned by `implement-spec-docs-sync-step`, flaky coverage measurement (`covgate-repeatable-unit-coverage`).

## Scope fence
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `chupa/specs/implement.md` is at a version one minor above its value at the base commit and its rendered Task contains the phrases `hard coverage gate`, `once after your last edit` and `touches no file that gate measures`. `tests/unit/test_specs.py` asserts each phrase, which rules out the base spec that runs only `## Verification` commands.
2. The rendered Task contains the exact sentence "A coverage floor miss is fixed with a test inside `## Scope fence`, or reported as `premise_failed` naming the file and its floor; never restructure production code to avoid coverage." `tests/unit/test_specs.py` asserts it, which rules out a rule that permits reshaping production code to dodge the floor or that omits the `premise_failed` road.
3. The rule limits the run to one pass and to diffs touching measured files. `tests/unit/test_specs.py` asserts the phrase `not after every edit`, which rules out a rule that asks for a gate run per edit or per attempt step.
4. The run-record assertion pins the new `spec: implement` version. `tests/integration/test_stages.py` rules out a stale pin.
5. `docs/how-chupa-works.md` section 4.2 states that Implement runs the hard coverage gates once after its last edit.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected
The rule asks for a gate run after every edit or when the diff touches no measured file; a floor miss may be fixed by restructuring production code, lowering a threshold, or editing a file outside the fence; the sequential-run or base-red rules are weakened; the implement spec's major version changes; the packing-slip schema or finding codes change; any other spec changes.

## Time budget
- expected: 20m
- stuck: 45m
