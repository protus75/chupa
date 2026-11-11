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
- docs/how-chupa-works.md#4.2 Implement

## On-demand
- chupa/specs/implement.md

## Goal / Why
Implement replied `ok` after checking a ticket's carried regression reproducer only at head, and the engine's `bug_evidence` gate then failed it at Check. The gate (`chupa/stages.py`, around lines 1329-1348) requires `record.base.regression_result == "defect"` and `rc > 0` at the overlaid base. On drain-sighup-graceful-stop attempt 1 the reproducer exited 2 with `error` at base instead of 1 with `defect`, because base drain raised ValueError when the scripted dispatch returned a terminal it never journaled. That cost a full attempt, three Diagnose calls and a retry cap (retro/40). Attempt 2 passed only after a Diagnose lesson told Implement to run the reproducer in a base-commit worktree with only the reproducer overlaid. `chupa/specs/implement.md` Task step 3 already tells Implement to run Verification commands, hard always-trigger checks and hard coverage gates, but never mentions the carried reproducer or its base behavior.

After this change Task step 3 also requires: when the ticket carries a regression reproducer (a `kind: bug` ticket with a `## Regression` section), run the carried reproducer once after your last edit in a base-commit git worktree with only the carried files overlaid (every `- carries:` path, as the gate overlays them), and confirm it prints `defect` and exits nonzero there, and prints `pass` and exits 0 at head, before replying `ok`. Two overcorrections are guarded: the step applies only to tickets that carry a reproducer, and when the base result is wrong Implement edits only the carried files, never production code, to get the base outcome it needs.

Class prevention: the spec rule is the paved road for the class (an agent-run check that mirrors an engine gate). A mechanical lint is not cheap or in scope here; it is not filed.

## Scope in / Scope out
- In: `chupa/specs/implement.md`: extend Task step 3 with the carried-reproducer rule, including the exact sentence "When the base result is wrong, edit only the carried files; never change production code to produce the base result.", and bump `version` to the next minor above its value at the base commit ("2.10" when drafted; sibling spec tickets may have bumped it since). Keep the file within `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: the implement version pins (two) move to that new version, plus assertions that the rule text is in the rendered Task.
- In: `tests/integration/test_stages.py`: the `spec: implement` pin in the run-record assertion moves to that new version.
- In: `docs/how-chupa-works.md` section 4.2: one sentence stating that Implement runs a carried regression reproducer once at base and once at head.
- Out: `chupa/stages.py` and the `bug_evidence` gate, Check code, the packing-slip schema, every other spec, the other step 3 rules (sequential run, hard checks, coverage gate, base-red rerun), and any gate that enforces this rule.

## Scope fence
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `chupa/specs/implement.md` is at a version one minor above its value at the base commit, and its rendered Task contains the phrases `carries a regression reproducer`, `base-commit git worktree`, `only the carried files overlaid`, `prints `defect` and exits nonzero` and `prints `pass` and exits 0`. `tests/unit/test_specs.py` asserts each phrase, which rules out the base spec that never mentions the reproducer's base behavior or checks it only at head.
2. The rendered Task contains the exact sentence "When the base result is wrong, edit only the carried files; never change production code to produce the base result." `tests/unit/test_specs.py` asserts it, which rules out a rule that lets Implement edit production code to satisfy the base check.
3. The rule is limited to tickets that carry a reproducer: the rendered Task contains the phrase `a ticket without a reproducer skips this step`, and `tests/unit/test_specs.py` asserts it, which rules out a rule that asks every ticket to run a base check.
4. The run-record assertion pins the new `spec: implement` version. `tests/integration/test_stages.py` rules out a stale pin.
5. `docs/how-chupa-works.md` section 4.2 states that Implement runs a carried regression reproducer once at base and once at head.
6. The reproducer rule itself says to run once after the last edit: the rendered Task contains the phrase `run the carried reproducer once after your last edit`, and `tests/unit/test_specs.py` asserts that exact phrase, which rules out a rule that asks for the base run after every edit (the older `once after your last edit` wording in the hard-check rule would not satisfy it).

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected
The rule applies to tickets that carry no reproducer; it permits editing production code to obtain the base result; it asks for the base run after every edit rather than once after the last edit, or runs the reproducer with anything but the carried files overlaid on the base commit; the other step 3 rules are weakened; the implement spec's major version changes; the packing-slip schema or finding codes change; any other spec, `chupa/stages.py` or the `bug_evidence` gate changes.

## Time budget
- expected: 20m
- stuck: 45m
