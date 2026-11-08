---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- retro-request-drain

## Context
- chupa/serve.py
- chupa/control.py
- chupa/retro.py
- chupa/drain.py
- chupa/__main__.py
- chupa/runner.py
- docs/how-chupa-works.md

## On-demand
- tests/integration/test_serve.py

## Goal / Why
After `retro-request-drain`, `chupa retro` with an engine running sends a `retro` control request, and a drain runs it between tickets. Serve accepts the request but never runs it. Serve also never runs automatic retros: only the drain branch of `chupa/__main__.py` wires a `Retro`, so under serve the `retro:` thresholds (`every_merges`, `every_days`, `spike_count`) are never checked. The operator starts serve from the extension, wants Retro to queue there too, and expects the same periodic retros a drain gives (2026-11-07).

After this change, a running serve that accepts a retro request stops admitting new tickets. Work in progress finishes, the forced retro runs once, and admission resumes. A serve whose `retro:` thresholds come due after a ticket settles does the same with an automatic retro.

## Scope in / Scope out
- In: `chupa/serve.py` `Serve`.
  - It keeps the in-memory id of the last retro request it served, starting as `None`.
  - While `control.projection.retro_id` differs from the served id, `select` admits no new ticket. A ticket already in `self.writers` continues, matching the existing `stop_requested` clause.
  - Once `upgrade_idle()` holds, the main loop runs a forced retro, `Retro(...)(forced=True)`, under `self.mutations()`. It then records the id as served, and admission resumes on the next loop.
  - The Retro's pipeline comes from `self.prepare` on a config snapshot, the way drain's `PreparedDispatch.prepare` in `chupa/runner.py` builds `stages`.
  - Automatic retros: after each ticket reaches a terminal state, serve checks whether a retro is due. A retro is due when `select_trigger(project_window(events), await production_evidence(window, checkout), clock(), config.retro, forced=False)` is not `None` and `suppressing_failure(window)` is `None`, using the existing `chupa/retro.py` functions. It never checks on every poll.
  - A due automatic retro blocks admission and waits for `upgrade_idle()` exactly like a pending request, then runs `Retro(...)(forced=False)` and clears the due flag. A pending request and a due automatic retro at the same idle point run one forced retro, which serves both.
  - `retro.enabled: false` stops automatic retros (as `select_trigger` already does) and never stops a requested one.
  - A retro that fails journals `retro_failed` through the existing `Retro` path. `suppressing_failure` then keeps the same window from coming due again, so serve never blocks admission in a loop.
  - A kill during the retro aborts it through `Retro.abort_current`.
  - A stop pending at the same time wins, and serve exits without running the retro.
  - As in drain, a re-run of the same request after a lifecycle-reusing handoff commits nothing, so no durable served marker is needed.
- In: `docs/how-chupa-works.md`: sections 7.2 and 9.5 say that serve runs requested retros, and automatic retros once the `retro:` thresholds come due after a ticket settles, at its next idle point, then resumes admission.
- Out:
  - `chupa/retro.py` behavior, `chupa/control.py`, `chupa/__main__.py`, `chupa/drain.py`, `vscode-chupa/`;
  - any new journal event kind, config key, or durable marker.

## Scope fence
- chupa/serve.py
- tests/integration/test_serve.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/integration/test_serve.py::test_requested_retro_waits_for_idle_then_resumes` passes. With one ticket running under serve and a second queued, an accepted retro request leads to these results, in order:
   - the second ticket is not admitted while the first runs;
   - exactly one forced retro call happens after the first ticket settles;
   - the second ticket is admitted after the retro returns.
   It rules out running the retro while a writer is active, never resuming admission, and running it twice.
2. `tests/integration/test_serve.py::test_kill_aborts_requested_retro` passes: a kill accepted while the requested retro runs calls `Retro.abort_current`, and serve exits killed.
3. `tests/integration/test_serve.py::test_automatic_retro_runs_at_idle_when_due` passes. With `retro.every_merges: 1`, one ticket merges under serve while a second is queued. Exactly one `forced=False` retro call happens after the first ticket settles and before the second ticket is admitted. The second ticket is admitted after it returns. It rules out serve never checking the thresholds, running the retro while a writer is active, and blocking admission afterwards.
4. `tests/integration/test_serve.py::test_automatic_retro_off_when_disabled` passes: with `retro.enabled: false` and `every_merges: 1`, a merged ticket leads to no retro call and no admission block.
5. `tests/integration/test_serve.py::test_failed_retro_does_not_reblock` passes: an automatic retro that journals `retro_failed` is not run again for the same window, and the next queued ticket is admitted.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_serve.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- serve runs a requested retro while any writer, admission, or merge-queue work is active;
- admission stays blocked after the retro returns;
- serve checks retro thresholds on every poll instead of after a ticket settles;
- the change adds a journal event kind, config key, or durable marker.

## Time budget
- expected: 90m
- stuck: 180m
