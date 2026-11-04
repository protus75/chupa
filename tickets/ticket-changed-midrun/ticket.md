---
priority: P1
kind: feature
source: human
state: confirmed
---

## Depends on
none

## Context
- docs/how-chupa-works.md
- chupa/runner.py
- chupa/stages.py
- chupa/drain.py
- chupa/status.py
- tests/test_drain.py

## Goal / Why
A run takes its ticket's content at dispatch, but nothing notices when `tickets/<stem>/ticket.md` changes while that run is in flight. An agent session edited `phase7-continue`'s ticket mid-run; the run carried on against a ticket it had not started with, and the edit broke a pinned test on main. A ticket changed under a running attempt must stop and wait for a human.

## Scope in / Scope out
- In: at dispatch the runner records the ticket's committed blob sha on main (the drain already journals it as `ticket_sha` on the `running` transition; `run` and `serve` record it the same way).
- In: before each stage starts and before merge admission, the runner compares that sha with the current committed blob on main AND with the bytes of `tickets/<stem>/ticket.md` in the main checkout. Any difference ends the attempt: terminal `gate_failed`, finding code `ticket_changed`, message naming the stem, paved road "review the change to tickets/<stem>/ticket.md, then keep (./dev.py confirm <stem>) or kill (./dev.py reject <stem>)", routed straight to the Reject queue with no diagnosis call, no Rework, and no cap draw.
- In: an operator keep re-runs the stem from its changed ticket as a fresh attempt; a kill rejects it as any Reject-queue kill does.
- In: changes the engine itself writes under `tickets/<stem>/` other than `ticket.md` (run record, `checks.json`, `review.md`, attempts) never trigger it; Rework's ticket updates between attempts are not mid-run.
- In: tests add `test_ticket_edit_mid_run_holds` (an edit committed between Implement and Check stops before Check with `ticket_changed`, makes no further model call, draws no cap, and lands in the Reject queue), `test_uncommitted_ticket_edit_mid_run_holds` (an uncommitted edit in the main checkout does the same), and `test_engine_artifacts_do_not_trigger` (ticket-plane lifts of `run.md` and `checks.json` during the run do not).
- In: update `docs/how-chupa-works.md` sections 3.2 and 6.7 (a `ticket.md` changed during a run stops it with `ticket_changed` and holds it), so the doc matches the code when this merges.
- In: if `uv run pytest -q` fails only on tests that also fail on the merge base, those failures are pre-existing: Check excuses them (base-red). Commit the work and list them in the run record; never stop with `premise_failed` for them.
- Out: the closed outcome vocabulary, cap values, the verdict verbs, and the plan text.

## Scope fence
- docs/how-chupa-works.md
- chupa/runner.py
- chupa/stages.py
- chupa/drain.py
- chupa/serve.py
- chupa/gates.py
- tests/

## Acceptance criteria
1. `uv run pytest -q tests/test_drain.py` exits 0, including `test_ticket_edit_mid_run_holds`, `test_uncommitted_ticket_edit_mid_run_holds`, and `test_engine_artifacts_do_not_trigger`.
2. `uv run pytest -q` exits 0.
3. `docs/how-chupa-works.md` sections 3.2 and 6.7 describe the `ticket_changed` stop and hold.

## Verification
```
uv run pytest -q tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if a run continues past a stage boundary or merge after its `ticket.md` changed, if the hold makes a model call or draws a cap, if engine-written ticket artifacts trigger it, or if the outcome vocabulary grows.

## Time budget
- expected: 60m
- stuck: 120m
