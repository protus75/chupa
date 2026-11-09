---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- chupa/hostfiles.py
- tests/integration/test_hostfiles.py

## Goal / Why
On 2026-11-08 a chat session wrote `vscode-pypi-identity` after reading only what the managed rule "Read ticket authoring docs before creating tickets" lists: the `chupa new` skeleton, lint findings, and `docs/host-authoring.md`. It never read the Author and Requisition review specs that define what `chupa review` checks, so the ticket broke two Author-spec rules (`Depends on` not written as `- none`, and a criterion naming no Verification substring) and missed a test for its printed line. `chupa review` was then blocked by the drain's lock, and the session handed the ticket over without saying it was unreviewed. The rule's "minimum reading" let a session meet it without opening the specs that set the bar.

After this change, the rule's minimum reading names the Author and Requisition review specs and the host's `test-gate.toml` coverage floors, and says a ticket whose `chupa review` could not run is reported as unreviewed.

## Scope in / Scope out
- In: `chupa/hostfiles.py` `CORE_TEMPLATE`, in "### CRITICAL: Read ticket authoring docs before creating tickets". Replace the paragraph beginning "Minimum reading for any single ticket:" with: "Minimum reading for any single ticket: the `chupa new` skeleton; the Author and Requisition review specs (`specs/author.md` and `specs/requisition_review.md` in the installed chupa package), which set the bar `chupa review` applies; the host's `test-gate.toml` coverage floors for any fenced file; the `chupa lint` and `chupa review` findings; and the host's own ticket authoring docs. When `chupa review` cannot run, say in the hand-off that the ticket is unreviewed." No other template text changes.
- In: re-render the managed block in `CLAUDE.md`, `AGENTS.md` and `hosts/fixture/CLAUDE.md` with `hostfiles.render` (what `chupa core` runs). Text outside the markers stays byte-identical.
- In: `tests/integration/test_hostfiles.py` `test_core_template_is_host_neutral`: assert the template contains "`specs/requisition_review.md` in the installed chupa package" and "say in the hand-off that the ticket is unreviewed".
- Out: any other template rule; `docs/host-authoring.md`; the specs themselves; intake's auto-confirm of new drafts; the `core_drift` gate.

## Scope fence
- chupa/hostfiles.py
- CLAUDE.md
- AGENTS.md
- hosts/fixture/CLAUDE.md
- tests/integration/test_hostfiles.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_hostfiles.py` passes; the new assertions fail if the template keeps the old minimum-reading paragraph without the specs or the unreviewed hand-off sentence.
2. The `chupa:core` blocks in `CLAUDE.md`, `AGENTS.md` and `hosts/fixture/CLAUDE.md` equal `hostfiles.render` output, so `tests/integration/test_fixture_host.py` sees `current`, not `drifted`, and the `core_drift` gate passes.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_hostfiles.py tests/integration/test_fixture_host.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a managed block differs from `hostfiles.render` output;
- any other template rule changes;
- project text outside the markers changes.

## Time budget
- expected: 15m
- stuck: 45m
