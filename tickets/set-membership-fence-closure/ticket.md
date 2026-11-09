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
- tests/integration/test_author.py

## On-demand
- chupa/specs/requisition_review.md
- chupa/specs/author.md

## Goal / Why
Three of the five gate-failure rejects in the retro/27 window had one cause: a ticket added or moved one member of a set that a test checks in full, and the fence left out the doc or test that pins that set. `order-verb` and `ask-prompt-verb` each added a parser verb without fencing `docs/host-running.md`, whose verb table `tests/unit/test_host_running.py` requires to match the parser's subcommands. `specs-in-package` moved `specs/` without fencing `tests/test_policy.py`, which hardcodes `ROOT / "specs"`. Requisition review approved all three, because `chupa/specs/requisition_review.md` traces only the symbol reference closure and the recorded values of bumped constants. After this change both the author spec and the requisition review spec carry a third closure: when Scope in adds, removes, renames, or moves a member of a set (CLI subcommand, file or directory path, spec name), grep `tests/` and `docs/` for files that list that set or hardcode the old path, and fence every hit. The rule is limited to files that assert against the changed set or hardcode the moved path. A mere textual mention, a path built under `tmp_path`, or a historical form the ticket keeps valid is not a hit.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`: add a fence bullet for the set-membership closure with the stated limit, and bump `version` from "3.3" to "3.4".
- In: `chupa/specs/author.md`: add the same closure to the fence-listing sentence of Task, and bump `version` from "1.3" to "1.4".
- In: `tests/unit/test_specs.py`: the `requisition_review` version pin moves to "3.4", plus an assertion that the new closure phrases are in the spec body.
- In: `tests/integration/test_author.py`: the author version pin moves to "1.4", plus an assertion that the new closure phrases are in the spec body.
- Out: every other spec, Check and requisition code, `docs/`, and any lint that enforces the rule.

## Scope fence
- chupa/specs/requisition_review.md
- chupa/specs/author.md
- tests/unit/test_specs.py
- tests/integration/test_author.py

## Acceptance criteria
1. `chupa/specs/requisition_review.md` is at version "3.4" and its body contains the phrases `adds, removes, renames, or moves a member of a set` and `asserts against the changed set or hardcodes the moved path`. `./dev.py test tests/unit/test_specs.py` asserts both, which rules out the 3.3 spec that traces only symbols and bumped values.
2. `chupa/specs/author.md` is at version "1.4" and its body contains the same two phrases. `./dev.py test tests/integration/test_author.py` asserts both, which rules out the 1.3 author spec with no set-membership grep.
3. The limit phrase `asserts against the changed set or hardcodes the moved path` is asserted present in both specs by `./dev.py test tests/unit/test_specs.py` and `./dev.py test tests/integration/test_author.py`, which rules out a rule with no stated limit that fences every loose grep hit.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_author.py
```

## Definition of rejected
The rule lacks the stated limit and sweeps in every loose grep hit; only one of the two specs gains the closure; a version is not bumped or a version pin keeps the old value; the existing symbol-closure or recorded-value-closure text is weakened; any file outside `## Scope fence` changes.

## Time budget
- expected: 20m
- stuck: 45m
