---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- none

## Context
- tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs

## On-demand
- chupa/specs/diagnose.md

## Goal / Why
Diagnose gave opposite verdicts on the same cause: a `premise_failed` terminal whose only finding was red tests already red on the base commit (`tests/test_seeded_phase7_core.py`). It chose `retry` for phase7-continue attempt 9, bug-evidence-intake, review-surfaces-refused and ticket-changed-midrun, but `reject` for attempts-cap attempt 0 and verdict-human-only. Those two buildable tickets went to the Reject queue. `chupa/specs/diagnose.md` defines `reject` as criteria that "cannot be satisfied" and never says how a base-verified failure counts.

After this change the diagnose spec states that a failure verified on the base commit, outside the diff, does not make a ticket unsatisfiable. It is filed, and the verdict is decided on the remaining findings. The rule applies only to a failure the material shows verified on the base commit; an unverified base-red claim in a run record does not qualify. Any other premise finding (a fence wall, a contradiction) is judged on its merits and can still earn `reject`.

This is a different surface from `implement-spec-base-red-not-premise`, which stops Implement from bouncing. This ticket governs how Diagnose judges a bounce that still reaches it.

## Scope in / Scope out
- In: `chupa/specs/diagnose.md`. In `## Task`, after the verdict list, add a paragraph containing the exact phrase "Failures verified on the base commit". It says: a failure the material shows verified on the base commit and outside the diff does not make criteria unsatisfiable, so it never alone earns `reject`; it is filed and the verdict is decided on the remaining findings; an unverified claim of base-red does not qualify; any other premise finding, such as a fence wall or contradicting criteria, is still judged on its merits and can earn `reject`. The spec stays within the 200-line `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: add one test asserting that `chupa/specs/diagnose.md` contains the exact phrase, the sentence that unverified claims do not qualify, and that `lint_spec` returns `[]` for it.
- Out: any engine code, the verdict list wording, the Output format and On-failure sections, the lesson limits, the `version` field, `chupa/specs/implement.md`, and `eval/` fixtures.

## Scope fence
- chupa/specs/diagnose.md
- tests/unit/test_specs.py

## Acceptance criteria
1. `chupa/specs/diagnose.md` contains `Failures verified on the base commit` and states that an unverified base-red claim does not qualify.
2. `tests/unit/test_specs.py` has a test that asserts both statements and passes under `./dev.py test tests/unit/test_specs.py`; it fails on a spec lacking them, so a spec still silent on base-verified failures is ruled out.
3. The same test asserts the spec still says other premise findings can earn `reject`, so a rule that makes every premise failure `retry` is ruled out.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test
```

## Definition of rejected
The change edits engine code, other specs or eval fixtures, lets an unverified base-red claim steer the verdict, removes the ability to `reject` on a true fence wall or contradiction, or alters the Output format, On-failure, or lesson limits.

## Time budget
- expected: 10m
- stuck: 30m
