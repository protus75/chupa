---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/control.py
- chupa/__main__.py
- chupa/drain.py
- tests/integration/test_control.py
- tests/integration/test_control_cli.py
- tests/integration/test_drain.py
- tests/integration/test_kill_signal_journal.py
- docs/how-chupa-works.md

## Goal / Why
The operator picked "Retro (run now)" in the extension's Engine… picker while a drain was running. `chupa retro` refused with exit 2 because the drain held the writer lock (2026-11-07). The operator wanted the retro queued, not refused. Today the only way to get one is to stop the engine and then run `chupa retro`.

After this change, `chupa retro` run while an engine holds the lock sends a `retro` control request to that engine and exits 0. A running drain runs the requested retro at its next between-tickets point. With no engine running, `chupa retro` runs the report right away, as it does today. Serve support is the follow-up ticket `retro-request-serve`.

## Scope in / Scope out
- In: `chupa/control.py`.
  - `Verb` gains `retro`. A retro request has a null `hold_id`, like pause, kill, and stop. `validate_request`, `_SHAPE`, and the decision fold accept it.
  - `ControlProjection` gains `retro_id: str | None = None`, the request id of the latest accepted retro request for this lifecycle. `ControlInbox._fold` sets it.
- In: `chupa/__main__.py` `retro` verb.
  - When the lock is free, behavior is unchanged.
  - When the lock is held (`LockHeld`), the command reads the active lifecycle with `control.read_active` and publishes `ControlRequest(uuid4().hex, lifecycle, "retro", None)` with `control.publish_request`, following the live branch of `_control`. It prints `retro submitted: <request_id>; the running engine runs it between tickets` and returns 0. An unavailable control identity refuses with the same road `_control` gives.
  - The `retro` subparser help says it runs a retro now, or queues one on the running engine.
- In: `chupa/drain.py` `_Drain`.
  - It keeps the in-memory id of the last retro request it served, starting as `None`.
  - At the existing retro point (after intake, gated by `_between_tickets`), a `projection.retro_id` that differs from the served id runs `dispatch.prepare()` (when present) and then `_run_retro(forced=True)`. The id is recorded as served, and the automatic `forced=False` check is skipped for that iteration.
  - An unserved request also runs before the drain returns quiescent, so a request accepted during the last ticket is not dropped.
  - A stop or kill returns without running it.
  - A forced retro with no merge since the last report commits nothing (`select_trigger`). So a drain handoff that reuses the lifecycle and runs the same request again is harmless; no durable served marker is needed.
  - `retro.enabled: false` does not suppress a requested retro, just as it does not suppress `chupa retro`.
- In: `tests/integration/test_kill_signal_journal.py`: its pinned `SHAPE` constant is updated to the new `_SHAPE` text.
- In: `vscode-chupa/extension.js`: the picker item becomes label `Retro`, detail `Run a retro report now, or after the running ticket when an engine is running.`, still verb `retro`.
- In: `docs/how-chupa-works.md`:
  - the `retro` row in section 2.1 notes that it queues on a running engine;
  - section 7.3 lists `retro` among the control requests;
  - section 9.5 says that a requested retro runs at the drain's next between-tickets point;
  - the section 2.2 extension paragraph keeps "retro" in the picker list.
- Out:
  - `chupa/serve.py`: serve running requested retros is `retro-request-serve`. Until it merges, serve accepts a retro request and does not run it.
  - automatic retros under serve;
  - any new journal event kind, config key, or durable served marker;
  - `chupa/retro.py` behavior;
  - `vscode-chupa/package.json`.
- Other coverage dependents of `chupa/control.py`, `chupa/drain.py`, and `chupa/__main__.py` need no change. A trailing defaulted `ControlProjection.retro_id` leaves positional and keyword construction and equality unchanged. The added `retro` verb leaves pause, resume, kill, stop, and verdict decisions unchanged. Serve only receives the extra projection field through its existing apply call.

## Scope fence
- chupa/control.py
- chupa/__main__.py
- chupa/drain.py
- vscode-chupa/extension.js
- tests/integration/test_control.py
- tests/integration/test_closed_sets.py
- tests/integration/test_control_cli.py
- tests/integration/test_drain.py
- tests/integration/test_kill_signal_journal.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/integration/test_closed_sets.py` asserts `control.Verb` is `{"kill", "pause", "resume", "retro", "stop"}`.
2. `tests/integration/test_control.py`:
   - a retro request with a non-null `hold_id` is rejected;
   - a current-lifecycle retro is accepted and sets `projection.retro_id` to its request id;
   - a retro naming another lifecycle is stale and leaves `retro_id` `None`.
3. `tests/integration/test_control_cli.py::test_retro_publishes_when_live` passes. With the lock held and discovery publishing lifecycle `retro-life`, `invoke(root, "retro")` returns 0 and writes exactly one inbox request with verb `retro`, lifecycle `retro-life`, and null `hold_id`. Stdout contains `retro submitted:`. It rules out the old `LockHeld` refusal (exit 2).
4. The existing `retro` CLI tests in `tests/integration/test_cli.py` (`test_retro_no_merge`, `test_retro_success`) pass unchanged: with the lock free, `chupa retro` still runs the report directly.
5. `tests/integration/test_drain.py::test_requested_retro_runs_between_tickets_once` passes. In a drain over two queued tickets, a retro request accepted while the first ticket runs leads to exactly one forced retro call. That call comes after the first ticket's terminal and before the second ticket dispatches. No second forced call follows for the same request id. It rules out running mid-ticket, running twice per request, and ignoring the request.
6. `tests/integration/test_drain.py::test_requested_retro_runs_before_quiescent_exit` passes. A retro request accepted while the last queued ticket runs gets one forced retro call before `drain` returns quiescent.
7. `node --check vscode-chupa/extension.js` exits 0, and the picker's `retro` item has label `Retro`.
8. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_control.py tests/integration/test_closed_sets.py tests/integration/test_control_cli.py tests/integration/test_drain.py tests/integration/test_cli.py
node --check vscode-chupa/extension.js
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a requested retro can run between attempts of one ticket, or while a ticket is running;
- `chupa retro` with the lock held still exits non-zero when a control identity is published;
- the change adds a journal event kind, config key, or a durable served-retro file;
- `chupa/serve.py` is changed.

## Time budget
- expected: 45m
- stuck: 120m
