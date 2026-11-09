---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: rejected
---

## Depends on
- none

## Context
- tests/unit/test_specs.py

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
The `check-test-timing` ticket can never pass Check (2026-11-08, attempts 1 and 2). It changes the format of the testreport results file that the candidate writes. The running engine's `read_results` on main reads that file when it judges the candidate, and it accepts only schema 1. The candidate's schema-2 output is therefore rejected by main's reader. Two paid attempts went to a premise that was already false when requisition review approved the ticket. The `results-schema-2-reader` ticket exists to put the reader first. `chupa/specs/requisition_review.md` says nothing about a file that the candidate writes and the running engine reads. Existing open tickets cover test files that read reshaped data, tests that assert gated outcomes, and enumerated sets. None of them covers a format read across the engine/candidate version boundary. After this change the spec carries one Task bullet: when Scope in changes the format of a file that the candidate writes and the running engine on main reads (for example testreport results), and no prior merged ticket makes the engine reader accept the new format, the reviewer raises a `snag` naming the engine-read file and the missing reader-first ticket. The rule is limited to formats the running engine reads. A file only the candidate's own tests read, a change that stays backward compatible with the reader on main, and a reader that is already merged are not hits.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`: add one Task bullet for the engine-read format rule with the stated limit. The `version` stays unchanged, because sibling spec tickets bump it and a second bump would collide.
- In: `tests/unit/test_specs.py`: a new test asserts the rule phrases are in the spec body.
- Out: every other spec, `chupa/tickets.py` and every lint, and `docs/`.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py

## Acceptance criteria
1. The spec body contains the phrases `the running engine reads` and `no prior merged ticket makes the engine reader accept the new format`. `./dev.py test tests/unit/test_specs.py` asserts both in `test_requisition_review_spec_flags_engine_read_format_flip`, which rules out a spec with no engine-read format rule.
2. The spec body contains the phrase `naming the engine-read file and the missing reader-first ticket`. `./dev.py test tests/unit/test_specs.py` asserts it, which rules out a rule that snags without telling the author the reader-first road.
3. The spec body contains the limit phrase `a change the reader on main already accepts is not a hit`. `./dev.py test tests/unit/test_specs.py` asserts it, which rules out a rule that snags every format change, including backward compatible ones.
4. The spec still lints clean and loads at its current version: `./dev.py test tests/unit/test_specs.py` still runs `test_spec_lint_accepts_the_implement_and_requisition_specs`, which rules out a malformed edit or an accidental version bump.

## Verification
```
./dev.py test tests/unit/test_specs.py
```

## Definition of rejected
The rule lacks the stated limit and snags backward compatible changes; the rule does not name the engine-read file and the reader-first ticket; the version is bumped; existing Task bullets are weakened; any file outside `## Scope fence` changes.

## Time budget
- expected: 20m
- stuck: 45m
