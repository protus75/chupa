---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- serve-reoffer-rule

## Runs before
- tests-split

## Context
- chupa/drain.py
- chupa/scheduler.py
- chupa/serve.py
- chupa/daemon.py
- chupa/caps.py
- tests/integration/test_scheduler.py
- tests/integration/test_serve.py
- docs/how-chupa-works.md

## Goal / Why
Serve does not follow the drain's re-offer rule (2026-11-07, `tickets/serve-reoffer-rule/evidence/`). It holds every Reject-queue ticket until an operator verdict, never draws a `retry` cap, and never checks spent caps. It also never re-offers a failed ticket at all: `Scheduler.dispatch_next` drops a dispatched ticket from `pending`, and after a failed terminal nothing puts it back unless the ticket text changes.

`serve-reoffer-rule` moved the rule into `awaiting_operator`, `reofferable`, and `record_reoffer` in `chupa/drain.py`. After this change serve uses them too, so drain and serve re-offer the same tickets and journal the same keep and `retry` events.

## Scope in / Scope out
- In: `chupa/scheduler.py`:
  - `Scheduler` takes a new keyword `caps: Callable[[], Caps]`.
  - `dispatch_next` no longer holds the whole Reject queue. A candidate whose last transition is a terminal is eligible only when `reofferable(events, stem, self.caps())` holds and it is not parked.
  - Quarantine, drought, `max_unmerged`, supersedes, and dependency checks are unchanged.
- In: `chupa/daemon.py`: `daemon_core` passes `caps=lambda: load().caps` to `Scheduler`.
- In: `chupa/serve.py`:
  - The serve dispatch calls `record_reoffer(local.journal, local.journal.read(), stem, sha)` before journaling the `running` transition, when the stem's last transition is a terminal.
  - The dispatch `finally` calls `self.core.scheduler.update(ticket)` when the latest transition is a failed terminal, as it already does for `provider_drought`, so `dispatch_next` decides through `reofferable` whether it runs again.
  - `Serve.merge` calls `self.core.scheduler.update(ticket)` after `owner.consume_result(...)` when the stem's latest transition is a failed terminal. Merge-stage failures (integration red, post-rebase regate, conflict handoff) are journaled there after the dispatch callback has returned, so the dispatch `finally` never sees them.
- In: tests:
  - `tests/integration/test_scheduler.py`:
    - New `test_serve_scheduler_follows_the_drain_reoffer_rule`:
      - a `gate_failed` Reject-queue ticket with caps left is dispatched;
      - the same ticket with a spent cap is held until an operator keep;
      - a `ticket_changed` Reject-queue ticket is held until an operator keep;
      - a failed ticket that is not in the Reject queue and has a spent cap is not dispatched.
    - `test_eligibility_and_hold_release` and the other `Scheduler(...)` constructions pass `caps`. Where a test means "held until a verdict", its `reject-held` ticket gets a spent cap.
  - `tests/integration/test_requisition_gate.py`: its `Scheduler(...)` construction passes `caps`.
  - `tests/integration/test_daemon_composition.py`: the `reject-held` case near line 410 gets a spent cap, so it still tests a hold that needs a verdict.
  - `tests/integration/test_serve.py`: a `gate_failed` run in serve is re-dispatched through the dispatch `finally` path (not a manual `update`) and journals one machine keep and one `retry` draw before `running`. A re-dispatch after `premise_failed` journals no `retry`. A merge-stage `gate_failed` with caps left is re-dispatched through the `Serve.merge` path and journals one `retry` draw before `running`.
  - `tests/integration/test_scheduler.py` and `tests/integration/test_daemon_composition.py`: the `actor: machine` keep case is rewritten. A `reject-held` stem with a spent cap stays held after a machine keep; a Reject-queue stem with caps left dispatches with no keep at all.
  - New carried reproducer `tests/regress_serve_reoffer_dispatch.py`, in the style of `tests/regress_graph_lanes.py`. It builds a `Scheduler` over journal events for a `gate_failed` Reject-queue ticket with caps left and calls `dispatch_next`. It prints exactly one `{"regression_result": ...}` line: `pass` (exit 0) when that ticket is dispatched, `defect` (exit 1) when it is held or `Scheduler` takes no `caps`, and `error` (exit 2) for any other failure.
- In: `eval/daemon_soak.py`, `eval/reliability_battery.py` and their tests: serve does not re-offer the evals' deliberate failures. Measured on main with this change applied (2026-11-07); with exactly these edits, all 108 tests in `test_daemon_soak.py`, `test_daemon_soak_runner.py`, `test_reliability_battery.py` and `test_watchdog_activation.py` pass:
  - Mechanism: before the fault is dispatched, the harness journals `caps.consume(journal, stem, "retry", "seed")` once per the member's configured `retry` cap, so `reofferable` is false after its one failure. Seeded draws carry `ticket_sha: "seed"`. A config cap cannot do this: `Count` refuses `retry: 0`, and `attempts: 1` changes the battery's terminals.
  - Soak: `eval/daemon_soak.py` seeds `semantic` just before `self.moves["semantic"]` is set. `test_daemon_soak_runner.py:169` is rewritten to expect exactly one `retry` draw for `worker` (its `abandoned` re-offer after the restart) and for `unresolved` (its attempt-0 merge-stage `gate_failed` re-offer), and none for every other receipt stem. `semantic` has no regate receipt, so its seeds never reach that check. No other soak assertion changes; `test_daemon_soak_runner.py:84-85` holds.
  - Battery: only the cooling member (`RELIABILITY_BATTERY_MEMBERS[1]`) is seeded, at the top of `exercise`, for `self.fault` and `cooling-second`. Without seeds, serve re-offers `cooling-fault` after the drought clears, ahead of `cooling-recovery`, and 4 battery tests fail. The quota and unknown-failure members need no seed.
  - `_observe` keeps `events = m.journal.read()` (the hold-prefix check at `:370` compares against the full journal) and adds `drawn`, the `cap_consumed` events whose `ticket_sha` is not `"seed"`. The cap checks at `:297`, `:338` and `:386` read `drawn` in place of filtering `events`.
  - `:343`: the cooling member's quota terminal now carries `routed: reject_queue` (spent cap, no `dispatch` key); the check expects `routed` equal to `reject_queue` for index 1 and absent otherwise, and still requires no `dispatch` key and no drawn cap.
  - `tests/integration/test_reliability_battery.py` `test_reliability_battery_requires_member_local_evidence`: the `required` set excludes `cap_consumed` events with `ticket_sha: "seed"`.
  - `tests/integration/test_watchdog_activation.py` needs no change: its `caps: {infra: 1}` is spent by its one `timeout`.
- In: `docs/how-chupa-works.md`:
  - section 6.4 cap table: `retry` is drawn by each drain or serve re-offer;
  - section 6.6 "Machine keep": both drain and serve re-offer a Reject-queue stem whose caps have budget;
  - section 7.2 `serve`: serve draws `retry` on a re-offer and puts a failed ticket back for the rule to decide, as the drain does;
  - section 7.2 Dispatch hold list: only Reject-queue stems awaiting an operator are held.
- Out:
  - the rule functions in `chupa/drain.py` and the snapshot (`serve-reoffer-rule`);
  - `chupa run`'s single-ticket dispatch (`chupa/runner.py`);
  - storm holds, provider droughts, quarantine;
  - changing which caps exist or their defaults.
- Coverage: Other test files that build serve or the daemon core are unaffected unless they hold a Reject-queue stem with caps left, end a serve run in a failed terminal with caps left, or count journal events around a serve re-dispatch. The ones that do (`test_control_cli`, `test_reject_queue`, `test_storm_notification_activation`, `test_daemon_soak`, `test_daemon_soak_runner`, `test_reliability_battery`, `test_watchdog_activation`) are fenced.

## Scope fence
- tests/integration/test_watchdog_activation.py
- eval/daemon_soak.py
- eval/reliability_battery.py
- tests/integration/test_daemon_soak.py
- tests/integration/test_daemon_soak_runner.py
- tests/integration/test_reliability_battery.py
- chupa/scheduler.py
- chupa/serve.py
- chupa/daemon.py
- tests/integration/test_scheduler.py
- tests/integration/test_requisition_gate.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_serve.py
- tests/integration/test_control_cli.py
- tests/integration/test_reject_queue.py
- tests/integration/test_storm_notification_activation.py
- tests/regress_serve_reoffer_dispatch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_scheduler.py tests/integration/test_requisition_gate.py tests/integration/test_daemon_composition.py tests/integration/test_serve.py tests/integration/test_control_cli.py tests/integration/test_reject_queue.py tests/integration/test_storm_notification_activation.py tests/integration/test_daemon_soak.py tests/integration/test_daemon_soak_runner.py tests/integration/test_reliability_battery.py` exits 0, including every test listed in Scope in.
2. `grep -n -e "reject_queue(" -e "caps.spent" -e "consume(" chupa/scheduler.py chupa/serve.py` prints nothing: they reach the rule only through `reofferable` and `record_reoffer`.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_scheduler.py tests/integration/test_requisition_gate.py tests/integration/test_daemon_composition.py tests/integration/test_serve.py tests/integration/test_control_cli.py tests/integration/test_reject_queue.py tests/integration/test_storm_notification_activation.py tests/integration/test_daemon_soak.py tests/integration/test_daemon_soak_runner.py tests/integration/test_reliability_battery.py
./dev.py test
```

## Regression
```
uv run python tests/regress_serve_reoffer_dispatch.py
```
- carries: tests/regress_serve_reoffer_dispatch.py

## Definition of rejected
Reject the branch if any of the following holds:
- serve or the scheduler decides a re-offer, or journals a keep or `retry`, other than through `reofferable` and `record_reoffer`;
- the drain's behavior changes;
- any file under `vscode-chupa/` or `chupa/drain.py` changes.

## Time budget
- expected: 60m
- stuck: 120m
