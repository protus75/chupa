---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
- bug-evidence-intake

## Context
- chupa/__main__.py
- chupa/tickets.py
- chupa/status.py
- dev.py
- docs/how-chupa-works.md
- docs/host-authoring.md

## Goal / Why
No command checks ticket files without running anything. Hosts import `chupa.tickets.validate_ticket` into their own wrapper scripts to lint tickets, a second copy of the entry point that drifts. A read-only `lint` verb gives every host the same check intake applies, without a lock and without running a ticket.

## Scope in / Scope out
- In: `chupa lint [stem ...]` in `chupa/__main__.py`. It validates `tickets/<stem>/ticket.md` with `validate_ticket` plus the evidence check from `chupa/tickets.py`. With no stems it checks every ticket that is not settled or rejected per the journal (every ticket when there is no journal yet).
- In: it takes no lock, creates no state directory, and writes no file, journal event, or git state.
- In: output is one line per finding, `<path>: <message> (<paved road>)`, then `lint: <valid>/<total> tickets valid`. Exit 0 when all are valid, 1 when any is invalid, 2 for a named stem with no ticket file or an unreadable tickets directory, never a traceback.
- In: `./dev.py lint [STEM...]` runs it.
- In: `tests/test_lint_verb.py`: `test_lint_all_valid`, `test_lint_reports_findings_and_exits_1`, `test_lint_flags_bug_without_evidence`, `test_lint_skips_settled_tickets`, `test_lint_named_stems_and_missing_stem`, and `test_lint_is_read_only_and_lock_free` (succeeds while another process holds the lock; no file, journal, or git change).
- In: update `docs/how-chupa-works.md` sections 2.1 and 2.2 and the Workflow in `docs/host-authoring.md` to name `chupa lint`.
- Out: the ticket grammar, intake, and the evidence check itself.

## Scope fence
- chupa/__main__.py
- dev.py
- tests/test_lint_verb.py
- docs/how-chupa-works.md
- docs/host-authoring.md

## Acceptance criteria
1. `uv run pytest -q tests/test_lint_verb.py` exits 0 with every test named above.
2. `docs/how-chupa-works.md` sections 2.1 and 2.2 and `docs/host-authoring.md` describe `chupa lint` and `./dev.py lint`.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_lint_verb.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if `lint` writes anything, takes the lock, applies different rules from intake, or re-judges settled tickets.

## Time budget
- expected: 30m
- stuck: 60m
