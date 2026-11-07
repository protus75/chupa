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
  - `tests/integration/test_serve.py`: a `gate_failed` run in serve is re-dispatched through the dispatch `finally` path (not a manual `update`) and journals one machine keep and one `retry` draw before `running`. A re-dispatch after `premise_failed` journals no `retry`.
  - `tests/integration/test_scheduler.py` and `tests/integration/test_daemon_composition.py`: the `actor: machine` keep case is rewritten. A `reject-held` stem with a spent cap stays held after a machine keep; a Reject-queue stem with caps left dispatches with no keep at all.
  - New carried reproducer `tests/regress_serve_reoffer_dispatch.py`, in the style of `tests/regress_graph_lanes.py`. It builds a `Scheduler` over journal events for a `gate_failed` Reject-queue ticket with caps left and calls `dispatch_next`. It prints exactly one `{"regression_result": ...}` line: `pass` (exit 0) when that ticket is dispatched, `defect` (exit 1) when it is held or `Scheduler` takes no `caps`, and `error` (exit 2) for any other failure.
- In: `eval/daemon_soak.py` and `eval/reliability_battery.py`: serve does not re-offer the evals' deliberate failures, so their single-attempt expectations (`daemon_soak.py:620`, `reliability_battery.py:315-332`, `test_daemon_soak_runner.py:84-85,150`) hold unchanged:
  - Mechanism: before serve starts, the harness seeds the member journal with `cap_consumed` `retry` events for the stem, as many as the member's configured `retry` cap, so `reofferable` is false after its one failure. A config cap cannot do this: `Count` refuses `retry: 0`, and `attempts: 1` changes the battery's terminals today (9 battery tests fail with it on main).
  - Soak: the `semantic` member's stem gets the seeded draws. `test_daemon_soak_runner.py:169` asserts no `retry` draw only for other stems and is unchanged.
  - Battery: the quota fault stems (`m.fault` and `cooling-second` in the quota members) get the seeded draws. `reliability_battery.py:297`, `:343` and `:360` are rewritten to count only `cap_consumed` events journaled after the seed, so they still assert `[]` for quota members and `["infra"]` for the unknown-failure member.
  - `tests/integration/test_watchdog_activation.py::test_production_hard_timeout_group_kill_is_harvested`: before serve starts, the test seeds the `work` stem with `retry` draws up to its configured cap, the same mechanism, so its one `timeout` is not re-offered and its worktree wait and teardown are unchanged.
  - The unknown-failure member needs no seed: its `caps: {infra: 1}` is spent by its one failure, so `reofferable` is already false.
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
