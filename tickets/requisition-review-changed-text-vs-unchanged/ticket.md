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
- tests/unit/test_specs.py::test_requisition_review_spec_snags_non_protocol_regression
- tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
A requisition re-review checked changed ticket text only against merged code, not against the unchanged parts of the same ticket, and approved a ticket that could not be satisfied. On `journal-incremental-read` the 16:06 re-review (ticket f4d5111e) found that the changed text held up against merged code. The change added a Scope-in rule: `append()` checks the active segment through the instance's own incremental read, parsing only lines it has not cached. That rule makes the unchanged criterion 2 same-instance clause ("the next read() parses exactly k lines") false for every k >= 2. Attempt 2 Review snagged and attempt 3 Review returned `rma` on exactly that contradiction. Diagnose then rejected the ticket, it went to the Reject queue, and an operator had to keep it. The cost was two Implement runs, three Reviews and three Diagnoses (retro/42).

The `## Task` rule in `chupa/specs/requisition_review.md` limits new findings to "text the diff shows changed since that review". The first-review bullet on contradicting statements covers pairs inside one ticket, but nothing says the limit still lets a changed statement be checked against the unchanged text it interacts with.

After this change the limit sentence is followed by a sentence saying: the changed-text limit still applies, and the reviewer checks each changed statement against every unchanged criterion, Definition-of-rejected clause and preservation test it interacts with, and raises any contradiction the changed text creates as a finding against the changed text. Unchanged text that no changed statement touches is not reviewed again. Measurable result: a re-review given a prior review and a diff that adds a statement contradicting an unchanged criterion returns a `snag` naming that contradiction. Overcorrection guard: the rule covers only contradictions the changed text creates; it is not permission to re-review the whole ticket.

Class prevention: the spec test added here pins the sentence, including the guard against whole-ticket re-review, so a later edit cannot drop either half silently.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`. In `## Task`, directly after the sentence ending "Raise a NEW finding only against text the diff shows changed since that review.", add the sentence described in Goal, containing the exact phrases "check each changed statement against every unchanged criterion, Definition-of-rejected clause, and preservation test it interacts with", "against the changed text" and "Unchanged text that no changed statement touches is not reviewed again." Bump `version` to the next minor above the version on `main` when this runs. The spec stays within `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: update the pinned `requisition_review` version to the bumped one, and add `test_requisition_review_spec_checks_changed_text_against_unchanged`, which renders the spec as the neighbouring tests do and asserts the three phrases above are in the whitespace-normalized `## Task`.
- Out: any change to `chupa/requisition.py`, how `prior_review` is built, the other `## Task` bullets, the invalid-prior full re-review sentence, and the Output format and On-failure sections.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py

## Acceptance criteria
1. `chupa/specs/requisition_review.md` contains the phrase `check each changed statement against every unchanged criterion, Definition-of-rejected clause, and preservation test it interacts with` and its `version` is the next minor above the version on main.
2. `test_requisition_review_spec_checks_changed_text_against_unchanged` in `tests/unit/test_specs.py` asserts the three phrases from Scope in and passes under `./dev.py test tests/unit/test_specs.py`. It fails on a spec that keeps only the changed-text limit, so a spec that never checks changed text against unchanged criteria is ruled out. It also fails on a spec lacking `Unchanged text that no changed statement touches is not reviewed again.`, so a spec that licenses a whole-ticket re-review is ruled out.
3. `test_spec_lint_accepts_the_implement_and_requisition_specs` in `tests/unit/test_specs.py` pins the bumped version, so a spec left at the old version fails it.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py tests/integration/test_requisition.py
./dev.py test
```

## Definition of rejected
The change edits `chupa/requisition.py` or any other engine code, removes or loosens the changed-text limit so the whole ticket is reviewed again on every round, drops the invalid-prior full re-review sentence, or alters the Output format or On-failure sections.

## Time budget
- expected: 15m
- stuck: 40m
