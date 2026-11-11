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
- chupa/artifacts.py

## On-demand

- chupa/specs/diagnose.md

## Goal / Why

`chupa/specs/diagnose.md` states the 300-character lesson cap only at the end, in `## Output format`, far below the lesson-writing guidance in `## Task`. That guidance asks lessons to cite tickets or merged code and to restate the work to redo, and both push lessons longer. The schema enforces the cap with `max_length=DIAGNOSIS_LESSON_CHARS` (300) in `chupa/artifacts.py`. Drafts keep going over it. Commit-lock attempt 6 made four Diagnose calls without a schema-valid verdict, ended `invalid_artifact`, was forced to abandon-human, and went to the Reject queue. Its retry/split/escalate guidance was lost. drain-sighup-graceful-stop and stale-running-after-kill also needed extra Diagnose calls for the same reason (retro/40).

After this change the spec states the limit next to the lesson-writing instruction. It also says that a lesson needing more detail is split into separate lessons within the 1 to 5 count, rather than packing many paths into one.

Overcorrection risk: lessons must not become too short to act on. They must keep the concrete fixture, file and caller names that made drain-sighup attempt 2 succeed. Splitting must not exceed 5 lessons.

## Scope in / Scope out

Scope in:

- In `## Task` of `chupa/specs/diagnose.md`, directly after the lesson-writing sentences, add guidance that each lesson is at most 300 characters. It says a lesson that needs more detail is split into separate lessons, one fact or file group each, keeping the total at 5 or fewer. It also says to keep the concrete file, fixture and caller names that the next attempt needs, and to drop prose around them instead.
- Bump the spec `version` from "1.4" to "1.5".
- Update the pinned version in `tests/unit/test_specs.py` and add a test pinning the new guidance.

Scope out:

- Changing `DIAGNOSIS_LESSON_CHARS` or the 1 to 5 lesson count.
- Verdict-choice or paved-road rules (covered by the open diagnose-spec-* tickets).
- Any retry-on-invalid-lessons machinery.

## Scope fence

- chupa/specs/diagnose.md
- tests/unit/test_specs.py

## Acceptance criteria

- `chupa/specs/diagnose.md` `## Task` contains the 300-character limit and the split-into-separate-lessons instruction, at most 5 in total. `./dev.py test tests/unit/test_specs.py` fails if the limit sentence is moved back out of `## Task`, so a spec that states the cap only under `## Output format` is ruled out.
- The spec front matter reads `version: "1.5"`, and `./dev.py test tests/unit/test_specs.py` fails if it is still "1.4".
- `./dev.py test tests/unit/test_specs.py` fails when the guidance does not tell the agent to keep concrete file and caller names, so a spec that only says "be brief" is ruled out.
- `./dev.py test tests/unit/test_specs.py` exits 0, which includes `lint_spec(text) == []` for the diagnose spec.
- `./dev.py test tests/integration/test_closed_sets.py` exits 0, showing `DIAGNOSIS_LESSON_CHARS` stays 300.

## Verification

```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_closed_sets.py
./dev.py test tests/integration/test_diagnose.py
```

## Definition of rejected

Rejected if the spec limit is changed to a number other than 300 or the count other than 1 to 5, if the limit sentence appears only under `## Output format`, if the guidance tells the agent to drop file or caller names, or if any file outside the fence changes.

## Time budget

- expected: 20m
- stuck: 60m
