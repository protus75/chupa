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
- chupa/runner.py
- tests/integration/test_serve.py
- docs/how-chupa-works.md

## Goal / Why
After `retro-request-drain`, `chupa retro` with an engine running sends a `retro` control request, and a drain runs it between tickets. Serve accepts the request but never runs it, and serve runs no retros at all. The operator starts serve from the extension and wants Retro to queue there too (2026-11-07).

After this change, a running serve that accepts a retro request stops admitting new tickets. Work in progress finishes, the forced retro runs once, and admission resumes.

## Scope in / Scope out
- In: `chupa/serve.py` `Serve`.
  - It keeps the in-memory id of the last retro request it served, starting as `None`.
  - While `control.projection.retro_id` differs from the served id, `select` admits no new ticket. A ticket already in `self.writers` continues, matching the existing `stop_requested` clause.
  - Once `upgrade_idle()` holds, the main loop runs a forced retro, `Retro(...)(forced=True)`, under `self.mutations()`. It then records the id as served, and admission resumes on the next loop.
  - The Retro's pipeline comes from `self.prepare` on a config snapshot, the way drain's `PreparedDispatch.prepare` in `chupa/runner.py` builds `stages`.
  - A kill during the retro aborts it through `Retro.abort_current`.
  - A stop pending at the same time wins, and serve exits without running the retro.
  - As in drain, a re-run of the same request after a lifecycle-reusing handoff commits nothing, so no durable served marker is needed.
- In: `docs/how-chupa-works.md`: sections 7.2 and 9.5 say that serve runs a requested retro once idle, then resumes admission.
- Out:
  - automatic (threshold-triggered) retros under serve;
  - `chupa/control.py`, `chupa/__main__.py`, `chupa/drain.py`, `vscode-chupa/`;
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
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_serve.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- serve runs a requested retro while any writer, admission, or merge-queue work is active;
- admission stays blocked after the retro returns;
- serve gains automatic retros, or the change adds a journal event kind, config key, or durable marker.

## Time budget
- expected: 60m
- stuck: 150m
