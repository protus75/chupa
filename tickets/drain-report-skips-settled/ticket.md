---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
none

## Context
- chupa/drain.py
- tests/test_drain.py
- chupa/__main__.py
- chupa/status.py

## On-demand
- docs/how-chupa-works.md

## Goal / Why
The drain report lists every ticket file that fails to parse under "invalid committed tickets", including tickets the journal shows as merged, `already_satisfied` or rejected. Those tickets are history: their `## Context` paths go stale as later tickets delete or rename files, and nothing can make them run again. Commit `a153c353` deleted `tests/test_seeded_phase*.py`, and every drain since lists 52 merged `phase*` tickets plus the rejected `plan-gap-44`. That noise hides real invalid tickets. `chupa lint` already skips settled and rejected stems (`chupa/__main__.py`, `_lint`); the drain report should apply the same rule. After this change a settled or rejected ticket whose file no longer parses is left out of "invalid committed tickets", and an unsettled one is still listed.

## Scope in / Scope out
- In: `chupa/drain.py` `_Drain._scan`: when `parse_ticket` raises `TicketInvalid` for a stem whose latest journal state (`last_states`) is in `SETTLED | {"rejected"}`, skip it without adding it to `invalid`. Parsing, the dirty-file skip, `tickets`, and `drafts` are unchanged.
- In: `tests/test_drain.py`: add `test_drain_report_omits_invalid_settled_and_rejected_tickets`: commit three tickets whose `## Context` names a missing file; journal one as `merged`, one as `rejected`, and leave one unsettled; the drain report's "invalid committed tickets" block names only the unsettled stem (it fails if a settled or rejected stem is listed).
- In: `docs/how-chupa-works.md` section 7.1 step 5: the report's invalid tickets exclude those settled or rejected in the journal.
- Out: `chupa lint`, ticket grammar in `chupa/tickets.py`, the content of any existing ticket file, and the scheduler's pick order.

## Scope fence
- chupa/drain.py
- tests/test_drain.py
- docs/how-chupa-works.md

## Acceptance criteria
1. A drain over a merged, a rejected, and an unsettled ticket that all fail to parse reports only the unsettled one as invalid, checked by `uv run pytest tests/test_drain.py -k drain_report_omits_invalid_settled_and_rejected_tickets`.
2. The full suite passes: `uv run pytest -q`.

## Verification
```
uv run pytest tests/test_drain.py -k drain_report_omits_invalid_settled_and_rejected_tickets
uv run pytest -q
```

## Definition of rejected
The change needs a ticket file edited, the ticket grammar changed, or an unsettled invalid ticket hidden from the report.

## Time budget
- expected: 30m
- stuck: 90m
