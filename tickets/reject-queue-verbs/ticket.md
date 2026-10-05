---
state: confirmed
source: seed
priority: P1
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- second-problems-filing
- suggestion-box

## Context
- chupa/status.py
- chupa/__main__.py
- chupa/runner.py
- tests/test_drain_upgrade.py

## On-demand
- chupa/drain.py
- chupa/stages.py
- chupa/tickets.py

## Plan contract
- 19.L
- 19.P2
- section 11
- section 13

## Goal / Why
A stem whose spine cap is spent terminates to the Reject queue: its single terminal `state_transition` carries `routed: reject_queue`. The queue is a journal-derived projection shown by `status` and the drain report, and every item names its release: the operator's `confirm <stem>` (keep) or `reject <stem>` (kill). The same deliverable lands the `premise_bounce` cap and its draw. A hold never lands before its release verbs (section 2), so the marker, the verbs, and the bounce cap ship together, and the escalation ladder that routes diagnosis verdicts here comes after.

Why: today a spent cap parks the stem with the road "author a successor stem". That is a re-author, which section 11.2 calls dead as recovery for a live lineage. There is no keep that re-arms caps, and no kill that retires a lineage and tells its dependents. `premise_failed` draws nothing, so an Author<->Implement premise loop has no named budget (section 11.1). The drain's "drafts awaiting confirm" line names a verb that does not exist.

Owners (section 9 ownership law, 19.P2): `chupa/runner.py` owns the terminal handler and therefore the `premise_bounce` draw and the routing marker. It also owns the verbs' resolutions, which journal through it. `chupa/stages.py` is the stage layer whose outcomes feed the terminal. `chupa/caps.py` owns the cap vocabulary and the fold that an operator keep bounds. `chupa/status.py` owns the Reject-queue projection (it writes nothing). `chupa/drain.py` owns eligibility and the report. `chupa/__main__.py` is the CLI entry. `chupa/tickets.py` owns frontmatter stamping. `chupa/box.py` is called for dead-dependency reports, never changed.

## Scope in / Scope out
- In: `chupa/caps.py`:
  - `CAPS` becomes `("diagnosis", "retry", "infra", "premise_bounce")`.
  - `draws` counts only the stem's `cap_consumed` events journaled AFTER its latest operator keep: a `signal` with body `{"signal": "reject_verdict", "verdict": "keep", "actor": "operator", ...}`. A keep with `"actor": "machine"` never bounds the fold.
- In: `chupa/runner.py` `drive`, at the cap-draw step (beside the infra draw, before diagnosis and the terminal):
  - A `premise_failed` terminal draws one `premise_bounce` unit, except an over-bound render (`render_over_bound` finding), which draws nothing (section 11.3).
  - After every draw for this terminal, when `spent(...)` names a cap, the terminal body gains `"routed": "reject_queue"`. The diagnosis record's mechanical reason already names that cap verbatim.
- In: `chupa/status.py`:
  - `reject_queue(events) -> dict[str, Mapping]`: each stem awaiting a verdict, mapped to the terminal body that routed it.
  - A stem awaits a verdict when its latest terminal carries the marker, or a `reject_arrival` signal follows that terminal, and no `reject_verdict` signal follows either. This is the section 9 Reject fold.
  - `status` renders a new `Reject queue` block after the existing blocks, each line `<stem>: <to> at <stage> -- confirm <stem> after editing, or reject <stem>`. Every existing block and its wording is unchanged.
- In: `chupa/drain.py`:
  - A stem awaiting a verdict is never re-offered.
  - At settle, a parked stem with a spent cap whose latest terminal lacks the marker (a terminal journaled before this seed) gets ONE `{"signal": "reject_arrival"}` signal, so no lineage is left releaseless (section 11.2).
  - Every parked stem awaiting a verdict keeps its existing reason text (for example `retry cap spent (6/6)`). Its paved road becomes: `edit tickets/<stem>/ticket.md (or fix the plan and regenerate it), then uv run python -m chupa confirm <stem>; or retire it with uv run python -m chupa reject <stem>`.
  - A re-offer whose latest terminal is `premise_failed` (its park released by a ticket change) draws NO `retry` unit, because the terminal already drew `premise_bounce`. This supersedes the Phase 1 behavior that `tests/test_drain_upgrade.py` covers (19.P2 SUPERSEDED BEHAVIOR).
- In: `chupa/tickets.py` renames `_stamp` to the public `stamp` in place, with every call site updated.
- In: two CLI verbs in `chupa/__main__.py`, `confirm <stem>` and `reject <stem>`, implemented in `chupa/runner.py`. Each validates the stem with `stem_findings`, acquires the single-writer lock (contention exits 2 like `run`), and runs intake first, so an operator's uncommitted ticket edit commits before the verdict. Each resolves the stem by JOURNAL identity: any journal event naming it, or an existing `tickets/<stem>/ticket.md`. Neither stem is known: refuse with exit 2.
- In: `confirm <stem>`, in order:
  1. When the committed ticket is `state: draft`, stamp `state: confirmed` and make one ticket-plane commit `chupa(<stem>): confirmed` of that path only. Then journal `{"signal": "draft_confirmed", "commit": <sha>}` and print `confirmed draft <stem>`. This is the draft gate's release (section 13 touchpoint 2).
  2. Otherwise, when the stem awaits a verdict, journal `{"signal": "reject_verdict", "verdict": "keep", "actor": "operator", "ticket_sha": <committed blob sha or null>}` and print `kept <stem>`. A dirless stem is still keepable. Refuse with exit 2 when the stem's latest operator keep carries the same `ticket_sha` as now, with the paved road `edit the ticket (or fix the plan and regenerate it) before re-enqueueing` (section 13 touchpoint 3's double-confirm refusal).
  3. Otherwise refuse with exit 2: the stem is neither a draft nor in the Reject queue, and `status` lists the queue.
- In: `reject <stem>`. It refuses a settled stem (`merged` or `already_satisfied`) with exit 2. Otherwise it completes, idempotently and in order:
  1. When `tickets/<stem>/ticket.md` exists and is not already `state: rejected`, stamp `state: rejected` and make one ticket-plane commit `chupa(<stem>): rejected`.
  2. For every committed `confirmed` ticket whose `## Depends on` names the stem, that is not settled, and that has no `dead_dependency` signal naming this stem yet: journal `{"signal": "dead_dependency", "dead": <stem>}` on the dependent. Then enqueue one `failure_report` with origin the dependent, stage `depends`, outcome `rejected`, and summary `<dependent> depends on <stem>, which was rejected; re-wire, re-scope, or reject it`.
  3. Unless the stem's latest state is already `rejected`, journal `{"signal": "reject_verdict", "verdict": "kill", "actor": "operator"}` and then the terminal `{"to": "rejected"}`.
  A dirless ghost gets steps 2-3 only (a journal-only `rejected`). A second `reject` completes any missing step and prints `already rejected`.
- Out: routing diagnosis verdicts (`split`, `reject`, `abandon-human`, an exhausted ladder) to the queue, the capability ladder, the identical-terminal short-circuit, and the pre-daemon auto-keep. That is the `escalation-ladder` seed. Until it lands, every arrival here has a spent cap, which only the operator's keep re-arms.
- Out: a `--successor` option and the supersedes map (Rework, Phase 3), notification push (Phase 4), the daemon-era control inbox, the supervised-merge hold (Phase 6), and any `confirm`/`reject` of a running stem.

## Scope fence
- chupa/caps.py
- tests/test_caps.py
- chupa/runner.py
- chupa/stages.py
- chupa/status.py
- chupa/drain.py
- chupa/__main__.py
- chupa/tickets.py
- tests/test_reject_queue.py
- tests/test_drain_upgrade.py

## Acceptance criteria
1. The `python -c` command in `## Verification` exits 0: `chupa.caps.CAPS` ends with `premise_bounce` and `chupa.tickets` exposes `stamp`.
2. `tests/test_reject_queue.py` drives `chupa.__main__.main(["run", ...])` with a FakeLLM to `premise_failed` twice, with a ticket edit committed between, under `caps: {premise_bounce: 2}`. Each terminal is preceded by one `premise_bounce` `cap_consumed`. The second terminal carries `routed: reject_queue`, and `status` lists the stem under `Reject queue`. An over-bound-render `premise_failed` draws no `premise_bounce` unit.
3. `tests/test_reject_queue.py` proves the fold and the keep. After an operator `confirm` of a queued stem, `remaining` is back to the full cap for every cap, and the stem leaves the queue. A machine-actor keep signal leaves `draws` unchanged. A second `confirm` with no `ticket.md` change exits 2 naming the edit road. A `confirm` after a committed edit succeeds.
4. `tests/test_reject_queue.py` proves the drain. A queued stem is never re-offered, and its report line keeps the reason and names both `confirm` and `reject`. A pre-existing spent-cap terminal without the marker gets exactly one `reject_arrival` across two drains and is then confirmable.
5. `tests/test_reject_queue.py` proves `reject`. The stem's `ticket.md` on main reads `state: rejected` in a `chupa(<stem>): rejected` commit. The journal shows the kill verdict, then a `rejected` terminal. Its confirmed dependent gets one `dead_dependency` signal and one `failure_report` box message. A second `reject` adds no event and no message. A dirless journal-only stem rejects with no commit. A merged stem is refused with exit 2.
6. `tests/test_reject_queue.py` proves draft confirm: a committed `state: draft` ticket becomes `state: confirmed` in a `chupa(<stem>): confirmed` commit with a `draft_confirmed` signal, and the next drain dispatches it.
7. `tests/test_drain_upgrade.py` adds an assertion that a premise park released by a ticket edit re-runs with zero `retry` draws, every other assertion unchanged. `tests/test_caps.py` adapts only its vocabulary assertion.
8. `uv run pytest -q tests/test_drain.py tests/test_cli.py tests/test_terminal.py tests/test_tickets.py` passes with no edit to those files.
9. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "import chupa.caps as c, chupa.tickets as t; assert c.CAPS[-1] == 'premise_bounce' and callable(t.stamp)"
uv run pytest -q tests/test_reject_queue.py tests/test_caps.py tests/test_drain_upgrade.py
uv run pytest -q tests/test_drain.py tests/test_cli.py tests/test_terminal.py tests/test_tickets.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- Queue code (`chupa/status.py`, `chupa/drain.py`) writes a terminal `state_transition`.
- A machine-actor keep, a ticket edit, or a `ticket_sha` change refills a cap.
- A held stem's paved road names a verb this diff does not build.
- A second cap fold or `cap_consumed` writer exists outside `chupa/caps.py`.
- `reject` deletes a ticket dir or a journal event.
- An existing `tests/test_drain.py` or `tests/test_cli.py` assertion changes.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
