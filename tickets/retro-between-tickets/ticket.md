---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- chupa/drain.py
- chupa/retro.py
- chupa/status.py
- tests/test_drain.py
- tests/test_retro.py

## On-demand
- docs/how-chupa-works.md

## Goal / Why
The drain checks retro triggers at the top of every loop (`chupa/drain.py`, `_run_retro(forced=False)`), and a retry of the same ticket is a new loop. On 2026-11-05 a gate-failure spike retro ran between `serve-self-upgrade` attempts 5 and 6, in the middle of that ticket's retry cycle. To the operator, one ticket's attempts are one process, and a retro inside it is unexpected. After this change the unforced retro check runs only between tickets: before the first dispatch of an invocation, or after the last dispatched ticket has settled (`merged` or `already_satisfied`), been routed to the Reject queue, or been held.

## Scope in / Scope out
- In: `chupa/drain.py`:
  - track the stem the invocation dispatched last;
  - at the loop top, call `_run_retro(forced=False)` only when no stem has been dispatched yet, or when that stem's latest terminal is settled, it is in `reject_queue`, or it is held (premise park, storm, drought or spec-gap hold);
  - otherwise skip the check, so the next pick, a retry of that stem, runs first;
  - leave the forced retro at quiescence and before `phase<N>-exit` stems unchanged;
  - add one why-comment at the check.
- In: `tests/test_drain.py`: a test where a ticket ends `gate_failed` with retry budget while a retro trigger is due. The retro does not run before that ticket's next attempt, and it does run after the ticket merges (or lands in the Reject queue) and before the next stem's first dispatch. The existing `test_drain_retro_due_quiescence_and_pre_exit` scenarios keep passing unchanged.
- In: `docs/how-chupa-works.md` section 9.5: the retro runs between tickets, never between attempts of one ticket.
- Out: `chupa/retro.py` trigger rules (`select_trigger`); the forced retros; serve (it runs no retro); the `retro` verb.

## Scope fence
- chupa/drain.py
- tests/test_drain.py
- tests/test_retro.py
- tests/test_daemon_composition.py
- docs/how-chupa-works.md

## Acceptance criteria
1. With a retro trigger due and ticket `a` ending `gate_failed` with `retry` budget, `a`'s next attempt dispatches before any retro request. A test fails if a retro runs between the two attempts. Checked by `uv run pytest tests/test_drain.py`.
2. After `a` merges, the due retro runs before the next stem's first dispatch. A test fails if it is skipped until quiescence. Checked by `uv run pytest tests/test_drain.py`.
3. `tests/test_drain.py::test_drain_retro_due_quiescence_and_pre_exit` passes for every scenario, unchanged.
4. `docs/how-chupa-works.md` section 9.5 states that the retro runs between tickets.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_drain.py tests/test_retro.py
uv run pytest -q
```

## Definition of rejected
A retro between attempts of one ticket; a change to `select_trigger` or the forced retros; a due retro deferred past the next settled ticket; a config knob.

## Time budget
- expected: 30m
- stuck: 90m
