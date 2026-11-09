---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/runner.py::run_ticket
- chupa/drain.py::drain
- chupa/observe.py::lock_holder
- chupa/observe.py::recent_steps
- tests/integration/test_watch.py::test_recent_steps_merges_engine_and_stage_events
- tests/integration/test_drain.py::test_lifecycle_log_precedes_lock_release
- tests/integration/test_cli.py::test_run_dispatches_the_locked_validated_stem_to_the_stage_seam

## Goal / Why
RECENT STEPS and TICKETS disagree when a `chupa run` dies. On 2026-11-08 a non-drain process started `lint-worktree-journal` at 1:44 PM and died about a minute later, and a `chupa review` took the lock at 1:57 PM. TICKETS correctly showed the ticket as "interrupted", because `running_stems` treats a `running` entry older than the live lock holder as stale. RECENT STEPS still showed `lint-worktree-journal  Implement start` as its newest row. Nothing showed that the process had started or died: only drain and serve write `engine_start`/`engine_stop`, and the `engine_lost` row ("ended without a stop record (killed?)") appears only when no live process holds the lock.

When done:
- `run_ticket` writes `engine_start`/`engine_stop` lines with `verb="run"`, as drain does.
- `recent_steps` adds the `engine_lost` row when the newest lifecycle event is an `engine_start` whose pid is not the live lock holder's pid. A dead run followed by a live `review` or drain then shows "run ended without a stop record (killed?)" above its orphaned stage start, matching the "interrupted" row in TICKETS.

## Scope in / Scope out
- In: `chupa/runner.py::run_ticket`. Open an `EngineLog` the way `drain` does. After `lock.acquire()`, write `engine_start` with `verb="run"` and `pid=os.getpid()`. Before `lock.release()`, write `engine_stop` with `verb="run"`, the same pid, and `outcome`: the dispatch terminal state, a short reason when it returns before dispatch (for example `"parked"` on the drought return), or `error: <ExceptionType>` on an exception, matching drain's error form.
- In: `chupa/observe.py::recent_steps`. The `engine_lost` condition becomes: the newest lifecycle event is an `engine_start`, and either no live process holds the lock or the live holder's pid in `chupa.lock` differs from that `engine_start`'s pid. Reading the holder's pid may change `lock_holder`'s return or add a read beside it, but every existing caller of `lock_holder` keeps its behavior.
- In: `tests/integration/test_watch.py`. Update `test_recent_steps_merges_engine_and_stage_events`: its final check monkeypatches `lock_holder` to a pid-less object and expects 6 rows. Make it cover a live holder whose pid matches the newest `engine_start` (no `engine_lost`, 6 rows) and one whose pid differs (`engine_lost` present, 7 rows).
- In: `tests/integration/test_cli.py`. Add a test that `run` writes exactly one `engine_start` and one `engine_stop` with `verb="run"` and the same pid, and `outcome="merged"`, to `.chupa/state/engine.log` on the merged path.
- In: `docs/how-chupa-works.md`. In the `engine.log` row of the state-files table, say that drain, serve and run write `engine_start`/`engine_stop`.
- Out: `vscode-chupa/`. The extension already draws `engine_start`, `engine_stop` and `engine_lost` kinds. Out: the `review`, `confirm` and `reject` verbs, which run no stages. Out: closing or annotating individual orphaned `stage_start` rows.

## Scope fence
- chupa/runner.py
- chupa/observe.py
- tests/integration/test_watch.py
- tests/integration/test_cli.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_cli.py` passes with a test where `run` on a merged ticket leaves exactly `[("engine_start", "run", pid, None), ("engine_stop", "run", pid, "merged")]` as the lifecycle events in `engine.log`, not an empty list.
2. `./dev.py test tests/integration/test_watch.py` passes with a case where the live lock holder's pid differs from the newest `engine_start` pid, and `recent_steps` includes the row `(None, "serve ended without a stop record (killed?)")` with kind `engine_lost`, not 6 rows without it. The same test shows that a live holder whose pid matches yields no `engine_lost` row.
3. `./dev.py test tests/integration/test_drain.py` passes unchanged, including `test_lifecycle_log_precedes_lock_release`.
4. `docs/how-chupa-works.md` names `run` among the verbs that write `engine_start`/`engine_stop` in the `engine.log` row.

## Verification
```
./dev.py test tests/integration/test_cli.py tests/integration/test_watch.py tests/integration/test_drain.py tests/integration/test_serve_lifecycle.py
```

## Definition of rejected
- `engine_start`/`engine_stop` for run go to the journal instead of `engine.log`.
- `engine_lost` appears while the process that wrote the newest `engine_start` still holds the lock.
- Any JavaScript under `vscode-chupa/` changes.

## Time budget
- expected: 30m
- stuck: 75m
