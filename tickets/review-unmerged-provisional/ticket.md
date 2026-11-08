---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/__main__.py::_review
- chupa/runner.py::drive
- tests/integration/test_review_command.py
- docs/how-chupa-works.md#2.1 Verbs
- docs/host-authoring.md#Workflow

## Goal / Why
`chupa review <stem>` refuses a ticket with an unmerged dependency before any model call. The extension offers Review on every queued and blocked row, so the operator keeps launching reviews that fail on that refusal (2026-11-08). The operator wants a preflight that finds as much as possible while the dependency is still in flight, with the verdict that counts still coming after the dependency merges.

After this change, reviewing a ticket with an unmerged dependency runs the full review and prints the verdict and findings. It journals no `requisition_verdict`, because the drain skips its pre-run review when an `approve` for the same ticket blob exists (`chupa/runner.py::drive`). An approve recorded against a main that lacks the dependency's code would skip the binding review.

## Scope in / Scope out
- In: `chupa/__main__.py` `_review`.
  - Replace the unmerged-depends `Refusal` with a list `unmerged` of dependencies whose state is not `merged`. The review runs as for any other ticket.
  - When `unmerged` is non-empty, skip the `requisition_verdict` journal append. Before the verdict line, print `review <stem>: provisional, not recorded -- depends on unmerged <a, b>; the drain reviews it again before its first run`.
  - Verdict line, findings and exit code are unchanged: 0 on approve, 1 otherwise.
  - Add a one-line why-comment that a journaled verdict would let an approval skip the drain's review.
- In: `tests/integration/test_review_command.py`.
  - `test_review_refuses_without_a_model_call` drops the `dependency`/`candidate` stems and keeps `missing` and `merged`. Its `confirmed("dependency")` was not a `- ` bullet, so it was refused as invalid and never exercised the depends path.
  - Add a test: commit `dependency` and `candidate` with `confirmed("- dependency")`. Reviewing `candidate` with a FakeLLM approve exits 0, prints the provisional line and `review candidate: approve`, and journals no `requisition_verdict`.
- In: docs.
  - `docs/how-chupa-works.md` 2.1 Verbs, `review <stem>` row: drop "dependency-blocked" from the refusals, and state that a ticket with an unmerged dependency gets a provisional review that is printed but not journaled, so the drain still reviews it before its first run.
  - `docs/host-authoring.md` Workflow step 4: replace "Review tickets with unmerged dependencies after they merge." with the provisional behavior. Authors repair what it finds; the drain reviews again after the dependencies merge.
- Out: `run`'s unmerged-depends refusal, the drain's pre-run review, the snapshot's review status, the extension menus, and the managed conduct block in `chupa/hostfiles.py`. Its "after dependencies have merged" rule still names the binding review.

## Scope fence
- chupa/__main__.py
- tests/integration/test_review_command.py
- docs/how-chupa-works.md
- docs/host-authoring.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_review_command.py` passes, including a test where reviewing a ticket with an unmerged dependency makes one model call, exits 0 on approve, prints `provisional, not recorded`, and leaves zero `requisition_verdict` events in the journal, not one.
2. `./dev.py test tests/integration/test_review_command.py` still shows `missing` and `merged` stems refused with exit 2 and no model call.
3. `./dev.py test tests/integration/test_requisition_gate.py` passes unchanged.
4. `docs/how-chupa-works.md` no longer lists dependency-blocked tickets among `review`'s refusals, and `docs/host-authoring.md` no longer says to wait for dependencies to merge before reviewing.

## Verification
```
./dev.py test tests/integration/test_review_command.py tests/integration/test_requisition_gate.py
./dev.py lint
```

## Definition of rejected
A provisional review journals a `requisition_verdict`, or `run` stops refusing unmerged dependencies.

## Time budget
- expected: 15m
- stuck: 40m
