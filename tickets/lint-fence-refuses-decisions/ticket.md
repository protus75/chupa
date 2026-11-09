---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: draft
---

## Depends on
- none

## Context
- chupa/tickets.py
- chupa/merge.py
- tests/unit/test_tickets_context.py
- docs/host-authoring.md

## Goal / Why
`parse_ticket` in `chupa/tickets.py` admits a `## Scope fence` entry that names the engine-owned decision records under `tickets/decisions`. The code lane cannot commit there: `PostRebaseGate.check` in `chupa/merge.py` fails every committed `tickets/` path, so a branch that edits a committed record fails at merge. box-declined-verdict lost a run this way (it fenced committed `tickets/decisions` records). After this change `chupa lint` refuses such a fence entry with a paved road. Seeding tickets that fence `tickets` and report producers that fence `tickets/<stem>/<report>.json` write uncommitted ticket-plane output that an engine lift commits; they stay valid and are not touched. The coverage-dependent integration tests that run `chupa/tickets.py` (test_tickets.py, test_lint_verb.py, test_merge.py, test_watch.py and the rest) are unaffected: the new finding fires only on a `## Scope fence` item equal to or under `tickets/decisions`, and no existing ticket or test fixture has such a fence entry (fixtures that mention `tickets/decisions` in test_watch.py, test_box.py, test_retro.py and test_host_contract.py write record files, not fence entries), so none of them changes outcome.

## Scope in / Scope out
- In: in the `## Scope fence` loop of `parse_ticket` in `chupa/tickets.py` (around line 388), add a finding for an item equal to `tickets/decisions` or starting with `tickets/decisions/`. The message says decision records are engine-written and the code lane cannot commit them; the paved road says to drop the entry from the fence and have the operator or the engine edit the record. Add unit tests in `tests/unit/test_tickets_fence.py`. Add one sentence to the `Scope fence` bullet in `docs/host-authoring.md`: `tickets/decisions` records are engine-owned and never fenced.
- Out: any other `tickets/` fence entry (`tickets`, `tickets/<stem>/...`); `lift_outbox`; `chupa/merge.py`; the implement spec; the `## Context` and `## On-demand` checks; tickets already committed.

## Scope fence
- chupa/tickets.py
- tests/unit/test_tickets_fence.py
- docs/host-authoring.md

## Acceptance criteria
1. `tests/unit/test_tickets_fence.py::test_fence_refuses_decisions_records` exits 0: `parse_ticket` on an in-memory ticket whose `## Scope fence` lists `tickets/decisions/declined-x.md` raises `TicketInvalid` with a finding mentioning `tickets/decisions`. The wrong result it rules out is the entry being admitted with no such finding.
2. `tests/unit/test_tickets_fence.py::test_fence_keeps_seeding_and_report_paths` exits 0: tickets fencing `tickets` (with a seeding-style Scope in) and `tickets/soak-run/daemon-soak-report.json` produce no finding mentioning `tickets/decisions`. The wrong result it rules out is the lint refusing the sanctioned uncommitted-output pattern.
3. `./dev.py test` exits 0, so every existing ticket shape still validates.
4. `docs/host-authoring.md` contains the text `tickets/decisions`.

## Verification
```
./dev.py test tests/unit/test_tickets_fence.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a `## Scope fence` item under `tickets/decisions` still passes `parse_ticket`;
- a fence item `tickets` or `tickets/<stem>/<report>.json` is refused;
- any file outside `## Scope fence` changes.

## Time budget
- expected: 15m
- stuck: 40m
