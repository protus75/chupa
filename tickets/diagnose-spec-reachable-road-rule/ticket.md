---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- diagnose-spec-fresh-start-rule

## Context
- tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs

## On-demand
- chupa/specs/diagnose.md

## Goal / Why
In one run a review finding offered more than one road. The attempt-6 diagnosis told implement to "use a bytes-returning git.py seam if merged code has one; if it has none, report that missing fact". `chupa/specs/diagnose.md` allows this, because it says "when clearing a finding needs one, say which fact is missing and nothing more". Implement took the missing-fact clause as permission to bounce, and attempt 7 returned `premise_failed` on a fence wall (`git.py`/`seams.py`). A road inside the fence was available: fail closed, or read worktree bytes with `Path.read_bytes()` through `gates.run_gates`. The bounce spent a capped `premise_bounce` attempt for nothing.

After this change the diagnose spec tells the diagnosis to check each road a finding states against merged code and the ticket's fence. It steers the lesson to a road reachable inside the fence. A missing-fact lesson is reserved for the case where no stated road is reachable inside the fence. The rule must not invent a workaround the finding does not state. When every stated road needs a file outside the fence, the lesson still says so, so implement can bounce early.

## Scope in / Scope out
- In: `chupa/specs/diagnose.md`. In `## Task`, after the paragraph beginning "Write concrete lessons" (and after the sentence added by `diagnose-spec-fresh-start-rule`), add a sentence containing the exact phrase "reachable inside the fence". It says that when a finding states more than one road, the lesson names a stated road reachable inside the fence, checked against merged code and the ticket's `## Scope fence`. It also says the missing-fact lesson is for when no stated road is reachable inside the fence, and that a lesson never invents a road the finding does not state. Bump `version` from `1.3` to `1.4`. The spec stays within the 200-line `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: the pinned `diagnose` version becomes `1.4`, and the file gains a test asserting the exact phrase is in `chupa/specs/diagnose.md`.
- Out: any change to `chupa/stages.py`, the verdict list, the Output format and On-failure sections, the 5-lesson and 300-character limits, the fresh-start sentence, and `eval/` fixtures.

## Scope fence
- chupa/specs/diagnose.md
- tests/unit/test_specs.py

## Acceptance criteria
1. `chupa/specs/diagnose.md` contains `reachable inside the fence` and `version: "1.4"`, not `1.3`.
2. `tests/unit/test_specs.py` has a test that asserts the phrase and passes under `./dev.py test tests/unit/test_specs.py`; it fails on a spec that lacks the phrase, so a spec that still lets a missing-fact lesson stand while a stated road is reachable is ruled out.
3. `tests/unit/test_specs.py` pins `1.4` as the `diagnose` version, so a spec left at `1.3` fails it.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test
```

## Definition of rejected
The change edits engine code, removes the early-bounce path when every stated road needs an out-of-fence file, tells diagnosis to invent roads the finding does not state, or alters the Output format, On-failure, or lesson limits.

## Time budget
- expected: 10m
- stuck: 30m
