---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- shared-hold-rule

## Runs before
- serve-reoffer-dispatch
- tests-split

## Context
- chupa/drain.py
- chupa/caps.py
- chupa/status.py
- chupa/observe.py
- tests/test_drain.py
- tests/test_watch.py
- tests/regress_shared_hold_rule.py
- docs/how-chupa-works.md

## Goal / Why
Drain and serve each decide on their own whether to run a ticket again after a failed run, and they disagree (2026-11-07, see `evidence/`):
- **Retries left in the Reject queue.** The drain runs the ticket again and journals a machine keep (`reject_verdict keep actor: machine`). Serve holds every Reject-queue ticket until an operator verdict.
- **Retry draws.** The drain draws a `retry` cap each time it runs a failed ticket again, unless the failure was `premise_failed` or a provider drought. Serve never draws one.
- **Spent caps.** The drain never runs a failed ticket again once a cap is spent. Serve does not check caps.
- **The snapshot.** It shows every Reject-queue ticket as held and waiting on the operator, so a ticket the drain will run again shows as held.

The drain's rule is the documented one (`docs/how-chupa-works.md` section 6.6, "Machine keep"). This ticket moves that rule into three functions in `chupa/drain.py`; the drain and the snapshot call them. Serve adopts them in `serve-reoffer-dispatch`.

## Scope in / Scope out
- In: `chupa/drain.py`:
  - New pure `awaiting_operator(events, stem, caps_config) -> bool`: the stem is in `reject_queue(events)` and either its queued terminal's `reason` codes include `ticket_changed`, or `caps.spent(caps_config, events, stem)` is not None.
  - New pure `reofferable(events, stem, caps_config) -> bool`, for a stem whose last transition is a terminal: not `awaiting_operator`, and `caps.spent` is None. The `parked_blob` hold from `shared-hold-rule` stays a separate check.
  - New `record_reoffer(journal, events, stem, sha)`, moved out of `Drain._run_one`. It journals the machine keep when the stem is in `reject_queue(events)`, then draws `retry` (with the terminal's `rung`) unless the last terminal is `premise_failed` or carries `provider_drought`.
  - `Drain._select` decides re-offers through `awaiting_operator` and `reofferable` instead of its inline `ticket_changed`, `awaiting and not budget`, and `not in held and budget` tests. The storm and provider-drought branches keep their current conditions.
  - `Drain._run_one` calls `record_reoffer` when `reoffer` is true.
- In: `chupa/observe.py`:
  - `held(history, blobs)` keeps its two-argument signature and returns only content-park stems (the `parked_blob` rule).
  - `queue()` and `snapshot` compute the awaiting-operator stems once, as the stems in `history` for which `awaiting_operator(history, stem, caps)` holds, where `caps` is the `caps` section of the config at `ctx.config`. That set replaces `reject_queue(history)` in `held_stems`, in `queue()`'s `waiting_on_person`, and in `snapshot`'s `reject_stems`.
  - A Reject-queue ticket with caps left and no `ticket_changed` reason therefore shows as queued, not held or waiting on the operator.
- In: tests:
  - `tests/test_drain.py`: unit tests for `awaiting_operator`, `reofferable`, and `record_reoffer` covering a `gate_failed` Reject-queue stem with caps left, the same stem with a spent cap, a `ticket_changed` stem, and a `premise_failed` re-offer that draws no `retry`.
  - `tests/test_watch.py`: the snapshot lists a Reject-queue ticket with caps left as `queued` and one with a spent cap as held; the existing `watch.held(history, {"work": "B"})` test still passes.
  - New carried reproducer `tests/regress_serve_reoffer_rule.py`, in the style of `tests/regress_graph_lanes.py`. It imports `reofferable` and `awaiting_operator` from `chupa.drain` and builds journal events for a `gate_failed` Reject-queue ticket. It prints exactly one `{"regression_result": ...}` line: `pass` (exit 0) when that ticket is `reofferable` with caps left and `awaiting_operator` with a spent cap, `defect` (exit 1) when either check is wrong or the functions cannot be imported, and `error` (exit 2) for any other failure.
- In: `docs/how-chupa-works.md` section 6.6 "Machine keep": the rule lives in `awaiting_operator`, `reofferable`, and `record_reoffer`, and the snapshot shows a Reject-queue ticket as held only when it awaits the operator.
- Out:
  - `chupa/scheduler.py`, `chupa/serve.py`, `chupa/daemon.py`: serve adopts the rule in `serve-reoffer-dispatch`.
  - `chupa/status.py`: `./dev.py status` keeps listing the whole Reject queue, since every entry there accepts `confirm` or `reject`.
  - `chupa run`'s single-ticket dispatch (`chupa/runner.py`), an operator-chosen run.
  - The content-park rule itself (`shared-hold-rule`).
  - Storm holds, provider droughts, quarantine, and the drain's stuck-time ceiling.
  - Changing which caps exist or their defaults.
- Coverage: The other test files that run `chupa/drain.py` or `chupa/observe.py` are unaffected: the drain must dispatch and hold exactly as before (Definition of rejected), and the observe change only narrows which Reject-queue stems display as held. The drain tests most likely to notice a journaling-order change (`test_drain_reentry`, `test_caps`, `test_ladder`, `test_reject_queue`) are fenced in case a fixture needs updating.

## Scope fence
- chupa/drain.py
- chupa/observe.py
- tests/test_drain.py
- tests/test_watch.py
- tests/test_drain_reentry.py
- tests/test_caps.py
- tests/test_ladder.py
- tests/test_reject_queue.py
- tests/regress_serve_reoffer_rule.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/test_drain.py tests/test_watch.py tests/test_drain_reentry.py tests/test_caps.py tests/test_ladder.py tests/test_reject_queue.py` exits 0, including every test listed in Scope in.
2. `grep -n -e "reject_queue(" -e "caps.spent" chupa/observe.py` prints nothing: observe reaches the rule only through `awaiting_operator`.
3. `uv run python tests/regress_shared_hold_rule.py` exits 0.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_drain.py tests/test_watch.py tests/test_drain_reentry.py tests/test_caps.py tests/test_ladder.py tests/test_reject_queue.py
uv run python tests/regress_shared_hold_rule.py
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
- `held` changes signature, or `snapshot` writes anything;
- any file under `vscode-chupa/` changes.

## Time budget
- expected: 60m
- stuck: 120m
