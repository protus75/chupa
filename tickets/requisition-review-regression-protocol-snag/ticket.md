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
- tests/unit/test_specs.py
- chupa/stages.py::regression_result

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
Requisition review approved `shared-hold-rule` with a `## Regression` command of `./dev.py test ... -k test_snapshot_holds_a_parked_ticket`. That command prints dev.py's `$` line and pytest text. The bug_evidence gate needs stdout to be exactly one `{"regression_result": ...}` JSON object (`stages.regression_result`), from a carried reproducer. Attempt 0 passed all tests but failed bug_evidence. Attempt 1 spent a retry and a `premise_bounce` unit rediscovering the defect, and the ticket reached the Reject queue twice. `chupa/specs/requisition_review.md` says nothing about `## Regression`, so the reviewer cannot snag this before Implement.

After this change the requisition review Task has one more snag bullet that applies only to tickets with a `## Regression` section.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`: add one bullet to the Task snag list. When the ticket has `## Regression`, its command must run a reproducer that sits under a `- carries:` path prefix (which must be a test or fixture path) and under a `## Scope fence` prefix. That reproducer must print only one `{"regression_result": ...}` JSON object and use the exit code that `stages.regression_result` pairs with it: `pass` with exit 0 at head, and `defect` with nonzero exit on the base overlaid with the carried files, using only code that exists at base. A `pass` printed with a nonzero exit, or a `defect` printed with exit 0, decodes to nothing and is a snag. A command that runs a test runner whose own output reaches stdout (`./dev.py test`, pytest) is a snag. Bump the spec `version` to the next minor above its value at the base commit ("3.3" when drafted; sibling spec tickets may have bumped it since).
- In: `tests/unit/test_specs.py`: update the pinned requisition_review version and add one test that the rendered Task holds the new bullet.
- Out: tickets with no `## Regression` section (the bullet must not apply to them), lint, `chupa/stages.py`, the bug_evidence gate, other specs.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py

## Acceptance criteria
1. The requisition_review spec Task carries the new bullet naming `regression_result`, `carries`, `## Scope fence`, the exit-code pairing (`pass` with exit 0, `defect` with nonzero exit), and the limit to tickets that have `## Regression`. `test_requisition_review_spec_snags_non_protocol_regression` in `tests/unit/test_specs.py` asserts these phrases, including the exit-code pairing, and fails on the base spec, which lacks them.
2. The spec version is one minor above its value at the base commit. `test_spec_lint_accepts_the_implement_and_requisition_specs` asserts the new version and fails if the version is unbumped.
3. `./dev.py test tests/unit/test_specs.py` exits 0, so the spec still lints and renders within the size budget.

## Verification
```
./dev.py test tests/unit/test_specs.py
```

## Definition of rejected
Reject the branch if any of the following holds:
- the bullet snags tickets that have no `## Regression` section;
- the bullet describes a protocol different from `stages.regression_result` (exactly one `regression_result` key; `pass` with exit 0, `defect` with nonzero exit, or `error`);
- a file outside `## Scope fence` changes.

## Time budget
- expected: 20m
- stuck: 45m
