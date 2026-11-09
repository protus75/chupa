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
- tests/unit/test_specs.py::test_review_spec_checks_docs

## On-demand
- chupa/specs/review.md

## Goal / Why
Review handled a break that the diff causes in a consumer outside the fence inconsistently. On attempts-cap, the `premise_bounce` default flip broke the real `eval/shakeout/drain.py` member, and a test patch in the diff hid the break. Attempt 3's review called it not blocking and said to file it, so Diagnose told the implementer to leave it alone. Attempt 4's review blocked on the same break as a `snag` that needed a human to widen the fence. `chupa/specs/review.md` defines `snag` as a defect fixable within the ticket and limits `rma` to unsatisfiable or self-contradictory criteria. Its Admissibility rule does not say whether such a break blocks. Two more attempts were spent and the stem parked on the `premise_bounce` cap.

After this change the review spec says four things. A break the diff causes in an out-of-fence consumer blocks and is never a non-blocking note. A criterion met only because the diff patches a test to hide such a break is an `acceptance` finding. When the fix needs a path outside `## Scope fence`, the verdict is `rma` with a `ticket` finding naming that path. The rule requires a traced causal link from a changed line to the broken consumer, so pre-existing problems stay non-blocking.

## Scope in / Scope out
- In: `chupa/specs/review.md`. In `## Task`, extend the `rma` bullet to cover a diff-caused defect whose only fix needs a path outside `## Scope fence`. After the Admissibility paragraph, add a paragraph containing the exact phrase "Out-of-fence breakage the diff causes". It says the following. A consumer outside the fence counts as broken by the diff only when you can trace a changed line to it by reading it, and then it is never a non-blocking note. If the fix fits inside the fence, `snag` it. If the fix needs a path outside the fence, reply `rma` with a `ticket` finding naming that path. Use `rma` only when no reading keeps the fix inside the fence. A criterion met only because the diff patches a test to hide the break is an `acceptance` finding. A test configuration that does not hide a break is not masking. A problem with no traced link from a changed line stays non-blocking. The spec stays within the 200-line `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: add one test asserting the new phrase and rules.
- Out: engine code, the `version` field, the Output format and On-failure sections, `eval/` fixtures, and other specs.

## Scope fence
- chupa/specs/review.md
- tests/unit/test_specs.py

## Acceptance criteria
1. `chupa/specs/review.md` contains `Out-of-fence breakage the diff causes` and states that it requires a traced link from a changed line to the broken consumer.
2. `tests/unit/test_specs.py` has a test that asserts the phrase, the `rma` routing for a fix outside the fence, and the `acceptance` finding for a test patch that hides the break. It passes under `./dev.py test tests/unit/test_specs.py` and fails on a spec lacking them, so a spec that lets the break pass as a non-blocking note is ruled out.
3. The same test, run by `./dev.py test tests/unit/test_specs.py`, asserts the spec still says pre-existing problems the diff does not touch never block, so a rule that blocks on any out-of-fence problem is ruled out.
4. The same test, run by `./dev.py test tests/unit/test_specs.py`, asserts the spec says `rma` is only for a fix that cannot be made inside the fence, so a rule that escalates every fixable defect to `rma` is ruled out.
5. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test
```

## Definition of rejected
The change edits engine code, other specs or eval fixtures, lets a defect with no traced link from a changed line block, sends fixable defects to `rma`, keeps diff-caused out-of-fence breakage non-blocking, or alters the Output format or On-failure sections.

## Time budget
- expected: 10m
- stuck: 30m
