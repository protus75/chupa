---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/tickets.py
- chupa/__main__.py
- chupa/stages.py
- docs/how-chupa-works.md
- docs/host-authoring.md

## Goal / Why
A `kind: bug` ticket must have at least one file under `tickets/<stem>/evidence/`, but only the `bug_evidence` gate at Check enforces it (`_gather_bug` in `chupa/stages.py`), after an Implement run has been paid for. Intake does not check it, and intake commits only `ticket.md`, so evidence the author wrote beside the ticket is not committed with it. The rule belongs in the ticket checker, so `chupa new`, intake, and `chupa lint` all report it before any run.

## Scope in / Scope out
- In: one function in `chupa/tickets.py` returning the evidence findings for a ticket: for `kind: bug`, at least one regular, non-symlink file under `tickets/<stem>/evidence/` in the given repo, else one finding with the paved road "add the observed failure (output, log excerpt, or captured command output) as a file under tickets/<stem>/evidence/". Non-bug tickets get none.
- In: intake applies it to every ticket it admits (new or changed) and refuses one that fails it, leaving the files on disk uncommitted. `chupa new` prints it with the other lint findings.
- In: intake commits the admitted stem's new or changed files under `tickets/<stem>/evidence/` in the same `chupa(<stem>): ticket` commit as `ticket.md`.
- In: the check is never applied to tickets already settled or rejected; existing merged bug tickets without evidence stay as they are.
- In: tests in `tests/test_tickets.py`: `test_bug_without_evidence_refused_at_intake` (refused, nothing committed, files left on disk), `test_bug_evidence_committed_with_ticket` (one commit holds `ticket.md` and the evidence file), `test_feature_needs_no_evidence`, and `test_symlink_is_not_evidence`.
- In: update `docs/how-chupa-works.md` sections 3.2 and 5.2 (intake refuses a bug ticket without evidence and commits its evidence with it) and the Evidence part of `docs/host-authoring.md`.
- In: if `uv run pytest -q` fails only on tests that also fail on the merge base, those failures are pre-existing: Check excuses them (base-red). Commit the work and list them in the run record; never stop with `premise_failed` for them.
- Out: the `bug_evidence` gate at Check, the regression protocol, and `chupa lint` (a separate ticket uses this function).

## Scope fence
- chupa/tickets.py
- chupa/__main__.py
- tests/test_tickets.py
- docs/how-chupa-works.md
- docs/host-authoring.md

## Acceptance criteria
1. `uv run pytest -q tests/test_tickets.py` exits 0, including `test_bug_without_evidence_refused_at_intake`, `test_bug_evidence_committed_with_ticket`, `test_feature_needs_no_evidence`, and `test_symlink_is_not_evidence`.
2. `docs/how-chupa-works.md` sections 3.2 and 5.2 and `docs/host-authoring.md` say intake refuses a bug ticket with no evidence file and commits its evidence with the ticket.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_tickets.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if a bug ticket without evidence can be admitted, if evidence is committed separately from its ticket, if a settled ticket is re-judged, or if the Check gate changes.

## Time budget
- expected: 45m
- stuck: 90m
