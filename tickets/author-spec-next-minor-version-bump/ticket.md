---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: draft
---

## Depends on
- none

## Context
- chupa/docs/host-authoring.md
- tests/integration/test_author.py::test_author_spec_requires_criteria_to_name_wrong_results

## On-demand
- chupa/specs/author.md

## Goal / Why
Tickets that bump a prompt spec name a literal target version (for example 3.4 to 3.5). When another ticket bumps the same spec first, that number is stale and requisition parks the ticket. Examples: requisition-review-invalid-prior-full-rereview wrote 3.5 while main was at 3.7. Open tickets now collide in the same way: requisition-review-no-reproduction-exit and requisition-review-patched-path-fence both go 3.9 to 3.10, and diagnose-spec-lesson-length and spec-paved-road-no-shim both go 1.4 to 1.5. After this change, the author spec and the host ticket-authoring guide tell authors to state a spec version bump as the next minor above the version on main, and never to name a literal target version. Implement reads the version on main and computes the number.

## Scope in / Scope out
Scope in:
- In `chupa/specs/author.md` Task, add one sentence: a ticket that bumps a prompt spec's `version` states it as "the next minor above the version on main", never a literal target such as `3.4 -> 3.5`, and a test pin follows the bumped file. Bump the author spec's own `version` by one minor.
- In `chupa/docs/host-authoring.md`, add the same rule to the `Scope fence` or `Acceptance criteria` bullet under "What each section is for".
- In `tests/integration/test_author.py`, update the author spec version pin to the bumped version, add assertions on the new sentence in the spec body, and add an assertion that the test reads `chupa/docs/host-authoring.md` and that it contains "the next minor above the version on main".

Scope out:
- Any other spec, the requisition review spec, lint or gate code, and open tickets that already name literal versions.

## Scope fence
- chupa/specs/author.md
- chupa/docs/host-authoring.md
- tests/integration/test_author.py

## Acceptance criteria
- `tests/integration/test_author.py` asserts that the author spec body contains the text "the next minor above the version on main" and the text "never a literal target". A spec that still lets authors write a fixed target such as "bump to 1.5" fails these assertions.
- `chupa/docs/host-authoring.md` contains the text "the next minor above the version on main", checked by `./dev.py test tests/integration/test_author.py`. A guide without the rule fails.
- The author spec `version` in `chupa/specs/author.md` is one minor above 1.4, and the pin in `tests/integration/test_author.py` matches it. A pin left at 1.4 fails `./dev.py test tests/integration/test_author.py`.

## Verification
```
./dev.py test tests/integration/test_author.py tests/unit/test_specs.py tests/unit/test_docs_verb.py
```

## Definition of rejected
- The spec or guide tells authors to write a fixed target version for a spec bump (a counter-example quoted after "never" is allowed).
- Any file outside the scope fence changes.
- The author spec stays at 1.4 or gains more than one minor.

## Time budget
- expected: 20m
- stuck: 45m
