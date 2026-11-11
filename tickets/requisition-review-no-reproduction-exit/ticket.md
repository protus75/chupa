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
- tests/unit/test_specs.py::test_requisition_review_spec_snags_non_protocol_regression
- tests/unit/test_specs.py::test_spec_lint_accepts_the_implement_and_requisition_specs

## On-demand
- chupa/specs/requisition_review.md

## Goal / Why
Requisition review approved `soak-serve-stops-early-under-load` twice (ticket shas 72a4e53e and 5485b0e4). The ticket asked the implementer to fix an intermittent failure but named no deterministic trigger and no exit for when the failure does not reproduce. Both Implement attempts returned `premise_failed` (cause not established; no reproduction in 27 runs). That spent the `premise_bounce` cap and sent the ticket to the Reject queue (retro report `retro/37`). A later review of the same unchanged text snagged it with code `no-reproduction-exit`, a code that appears nowhere in `chupa/specs/requisition_review.md`. Catching this defect therefore depends on reviewer improvisation, which the two approvals show is unreliable.

After this change the spec tells the reviewer to snag a ticket whose own evidence says the failure is intermittent or did not reproduce, and which states neither a deterministic trigger nor an exit for the no-reproduction case.

## Scope in / Scope out
- In: `chupa/specs/requisition_review.md`. Add one bullet to the `snag` list in `## Task`: when the ticket's own evidence or Goal says the failure is intermittent, flaky, load-dependent, or did not reproduce, and the ticket names neither a deterministic trigger (a command, fixture, or seed that reproduces it) nor an exit for when the failure does not reproduce (for example, file an instrumentation ticket and stop), raise a `snag` finding with code `no-reproduction-exit` naming the missing trigger or exit. The bullet contains the exact phrase "names neither a deterministic trigger" and states that a ticket whose evidence pins the cause or whose failure reproduces reliably is not a hit.
- In: bump the spec `version` from `3.9` to `3.10`.
- In: `tests/unit/test_specs.py`: the pinned `requisition_review` version becomes `3.10`, and a new test asserts the rendered Task contains the new phrases, including the not-a-hit limit.
- Out: any change to `chupa/requisition.py`, the data blocks the reviewer receives, other spec bullets, and `docs/`.

## Scope fence
- chupa/specs/requisition_review.md
- tests/unit/test_specs.py

## Acceptance criteria
1. `chupa/specs/requisition_review.md` contains `version: "3.10"`, not `3.9`, and the new bullet with code `no-reproduction-exit`.
2. `./dev.py test tests/unit/test_specs.py` passes. The new test asserts `names neither a deterministic trigger` and the not-a-hit limit in the rendered Task, so it fails on the unchanged spec; the version pin rules out a missed bump.
3. `./dev.py test tests/unit/test_specs.py` includes a new assertion on the not-a-hit limit phrase (evidence that pins the cause or reliably reproduces), which rules out a bullet that would snag every bug ticket lacking a scripted trigger.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test
```

## Definition of rejected
The change edits `chupa/requisition.py` or the reviewer's data blocks, or the new bullet applies to bug tickets whose evidence does not say the failure is intermittent or non-reproducing.

## Time budget
- expected: 15m
- stuck: 40m
