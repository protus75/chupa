---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- shared-hold-rule

## Context
- chupa/drain.py
- chupa/scheduler.py
- chupa/serve.py
- chupa/daemon.py
- chupa/caps.py
- chupa/status.py
- chupa/observe.py
- tests/test_scheduler.py
- docs/how-chupa-works.md

## Goal / Why
Drain and serve each decide on their own whether to run a ticket again after a failed run, and they disagree (2026-11-07, see `evidence/`):
- **Retries left in the Reject queue.** The drain runs the ticket again and journals a machine keep (`reject_verdict keep actor: machine`). Serve holds every Reject-queue ticket until an operator verdict.
- **Retry draws.** The drain draws a `retry` cap each time it runs a failed ticket again, unless the failure was `premise_failed` or a provider drought. Serve never draws one.
- **Spent caps.** The drain never runs a failed ticket again once a cap is spent. Serve does not check caps.
- **The snapshot.** It shows every Reject-queue ticket as held, so a ticket the drain will run again shows as held.

The drain's rule is the documented one (`docs/how-chupa-works.md` section 6.6, "Machine keep"). After this change the rule lives once in `chupa/drain.py`, and the drain, serve, and the snapshot all call it.

## Scope in / Scope out
- In: `chupa/drain.py`:
  - New pure `awaiting_operator(events, stem, caps_config) -> bool`: the stem is in `reject_queue(events)` and either its queued terminal's `reason` codes include `ticket_changed`, or `caps.spent(caps_config, events, stem)` is not None.
  - New pure `reofferable(events, stem, caps_config) -> bool`, for a stem whose last transition is a terminal: not `awaiting_operator`, and `caps.spent` is None. The `parked_blob` hold from `shared-hold-rule` stays a separate check.
  - New `record_reoffer(journal, events, stem, sha)`, moved out of `Drain._run_one`. It journals the machine keep when the stem is in `reject_queue(events)`, then draws `retry` (with the terminal's `rung`) unless the last terminal is `premise_failed` or carries `provider_drought`.
  - `Drain._select` decides re-offers through `awaiting_operator` and `reofferable` instead of its inline `ticket_changed`, `awaiting and not budget`, and `not in held and budget` tests. The storm and provider-drought branches keep their current conditions.
  - `Drain._run_one` calls `record_reoffer` when `reoffer` is true.
- In: `chupa/scheduler.py`:
  - `Scheduler` takes a new keyword `caps: Callable[[], Caps]`.
  - `dispatch_next` no longer holds the whole Reject queue. A candidate whose last transition is a terminal is eligible only when `reofferable(events, stem, self.caps())` holds and it is not parked.
  - Quarantine, drought, `max_unmerged`, supersedes, and dependency checks are unchanged.
- In: `chupa/daemon.py`: `daemon_core` passes `caps=lambda: load().caps` to `Scheduler`.
- In: `chupa/serve.py`: the serve dispatch calls `record_reoffer(local.journal, local.journal.read(), stem, sha)` before journaling the `running` transition (line 145), when the stem's last transition is a terminal.
- In: `chupa/observe.py`: the held set replaces `reject_queue(history)` with the stems where `awaiting_operator(history, stem, caps)` holds. `caps` is the `caps` section of the config at `ctx.config`.
- In: tests:
  - `tests/test_scheduler.py`:
    - New `test_serve_scheduler_follows_the_drain_reoffer_rule`:
      - a `gate_failed` Reject-queue ticket with caps left is dispatched, and a machine keep is journaled;
      - the same ticket with a spent cap is held until an operator keep;
      - a `ticket_changed` Reject-queue ticket is held until an operator keep;
      - a failed ticket that is not in the Reject queue and has a spent cap is not dispatched.
    - `test_eligibility_and_hold_release` and the other `Scheduler(...)` constructions pass `caps`. Where a test means "held until a verdict", its `reject-held` ticket gets a spent cap.
  - `tests/test_requisition_gate.py`: its `Scheduler(...)` construction passes `caps`.
  - `tests/test_daemon_composition.py`: the `reject-held` case near line 410 gets a spent cap, so it still tests a hold that needs a verdict.
  - `tests/test_serve.py`: a serve re-dispatch of a `gate_failed` ticket journals one `retry` draw before `running`. A re-dispatch after `premise_failed` journals none.
  - `tests/test_watch.py`: the snapshot lists a Reject-queue ticket with caps left as `queued`, and one with a spent cap as held.
  - New carried reproducer `tests/regress_serve_reoffer_rule.py`, in the style of `tests/regress_graph_lanes.py`. It imports `reofferable` and `awaiting_operator` from `chupa.drain` and builds journal events for a `gate_failed` Reject-queue ticket. It prints exactly one `{"regression_result": ...}` line: `pass` (exit 0) when that ticket is `reofferable` with caps left and `awaiting_operator` with a spent cap, `defect` (exit 1) when either check is wrong or the functions cannot be imported, and `error` (exit 2) for any other failure.
- In: `docs/how-chupa-works.md`:
  - section 6.6 "Machine keep": both drain and serve re-offer a Reject-queue stem whose caps have budget;
  - section 7.2 `serve`: serve draws `retry` on a re-offer, as the drain does.
- Out:
  - `chupa run`'s single-ticket dispatch (`chupa/runner.py`), an operator-chosen run.
  - The content-park rule (`shared-hold-rule`).
  - Storm holds, provider droughts, quarantine, and the drain's stuck-time ceiling.
  - Changing which caps exist or their defaults.

## Scope fence
- chupa/drain.py
- chupa/scheduler.py
- chupa/serve.py
- chupa/daemon.py
- chupa/observe.py
- tests/test_scheduler.py
- tests/test_requisition_gate.py
- tests/test_daemon_composition.py
- tests/test_serve.py
- tests/test_watch.py
- tests/test_drain.py
- tests/regress_serve_reoffer_rule.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/test_scheduler.py tests/test_requisition_gate.py tests/test_daemon_composition.py tests/test_serve.py tests/test_watch.py tests/test_drain.py` exits 0, including every test listed in Scope in.
2. `grep -n "reject_queue\|caps.spent\|consume(" chupa/scheduler.py chupa/serve.py chupa/observe.py` prints nothing: they reach the rule only through `awaiting_operator`, `reofferable`, and `record_reoffer`.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_scheduler.py tests/test_requisition_gate.py tests/test_daemon_composition.py tests/test_serve.py tests/test_watch.py tests/test_drain.py
./dev.py test
```

## Regression
```
uv run python tests/regress_serve_reoffer_rule.py
```
- carries: tests/regress_serve_reoffer_rule.py

## Definition of rejected
Reject the branch if any of the following holds:
- a rule deciding whether a failed ticket runs again, or what a re-offer journals, is written anywhere other than `awaiting_operator`, `reofferable`, and `record_reoffer` in `chupa/drain.py`;
- the drain dispatches or holds a ticket differently than before this change;
- `snapshot` writes anything;
- any file under `vscode-chupa/` changes.

## Time budget
- expected: 75m
- stuck: 150m
