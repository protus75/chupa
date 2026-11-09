---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- implement-spec-base-red-not-premise

## Context
- tests/unit/test_specs.py

## On-demand
- chupa/specs/implement.md
- docs/how-chupa-works.md

## Goal / Why
Implement claimed `## Verification` commands passed when it had run them overlapping other test runs, or only a subset of the suites. On serve-self-upgrade, attempt 2 ran only two test files and then failed at merge verification. Attempt 3 said "Overlapping test runs caused timing failures; both required commands passed when run without overlapping suites", then failed Check on `test_report_consumer_is_sequential`. Attempt 4 reported a full-suite run that overlapped a second test command. Diagnosis repeated "run one command at a time, in sequence" three times, and each cycle cost about $1 of Implement spend. Since `parallel-tests` merged, suites run under xdist and depend on timing, so overlapping runs give results that do not match Check. `chupa/specs/implement.md` step 3 says only "Run every `## Verification` command yourself and make each one exit 0". After this change it requires running each command whole, one after another, with no other test process running, and reporting that final sequential result. The rule guards against overcorrection: parallelism inside one command (host-configured xdist workers) stays allowed, one final sequential pass is enough with no repeated full-suite reruns, and a timing failure is verified on the base commit and filed in `second_problems`, not fixed out of scope.

## Scope in / Scope out
- In: `chupa/specs/implement.md`: extend Task step 3 with the sequential-run rule above, including the exact sentence "A timing failure that appears only when test runs overlap is verified on the base commit and reported in `second_problems`", and bump `version` to the next minor above its value at the base commit ("2.4" when drafted; sibling spec tickets may have bumped it since).
- In: `tests/unit/test_specs.py`: the implement version pins move to that new version, plus assertions that the rule text is in the rendered Task.
- In: `tests/integration/test_stages.py`: the `spec: implement` pin in the run-record assertion moves to that new version.
- In: `docs/how-chupa-works.md` section 4.2: one sentence stating that Implement runs each Verification command whole and in sequence and reports that final result.
- Out: Check code, `chupa/stages.py`, the packing-slip schema, every other spec, the base-red rule owned by `implement-spec-base-red-not-premise`.

## Scope fence
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `chupa/specs/implement.md` is at a version one minor above its value at the base commit and its rendered Task contains the phrases `one after another`, `no other test process` and `whole command`. `./dev.py test tests/unit/test_specs.py` asserts each phrase, which rules out the base spec that only says "make each one exit 0".
2. The rule keeps parallelism inside a single command and limits the check to one final sequential pass. `./dev.py test tests/unit/test_specs.py` asserts the phrases `inside a single command` and `one final sequential pass`, which rules out a rule that bans xdist workers or asks for repeated full-suite reruns.
3. The rule sends a timing failure to the base commit and `second_problems`. `./dev.py test tests/unit/test_specs.py` asserts the exact sentence `A timing failure that appears only when test runs overlap is verified on the base commit and reported in`, which the base spec does not contain and which rules out a rule that omits timing-failure routing or has Implement fix out-of-scope timing code.
4. The run-record assertion pins the new `spec: implement` version. `./dev.py test tests/integration/test_stages.py` rules out a stale pin.
5. `docs/how-chupa-works.md` states that Verification commands are run whole and in sequence, in section 4.2 Implement.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected
The rule bans parallelism inside a single command or asks for repeated full-suite reruns; a timing failure is fixed outside the fence instead of verified on the base commit and filed; the base-red rule from `implement-spec-base-red-not-premise` is weakened; the implement spec's major version changes; the packing-slip schema or finding codes change; any other spec changes.

## Time budget
- expected: 20m
- stuck: 45m
