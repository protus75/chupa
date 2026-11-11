---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/runner.py::prepare_pipeline
- chupa/drain.py::_Drain._run_retro
- chupa/serve.py::Serve.check_retro
- chupa/observe.py::STEP_NAMES
- chupa/observe.py::recent_steps
- docs/how-chupa-works.md#10. State on disk

## On-demand
- vscode-chupa/extension.js
- tests/integration/test_watch.py

## Goal / Why
Over the 21 drain starts on 2026-11-10 and 2026-11-11, `engine.log` had nothing between `engine_start` and the first `stage_start` for 82s to 355s. Recent Steps showed "drain started", then nothing, while two pieces of work ran:

- Provider preflight: a `--version` and `pnpm view` per provider CLI, then one probe call per routed (provider, model) pair. Six serial probes took 28s on 2026-11-11 at 10:13.
- The retro check: it decides whether a retro is due. When none is due it returns without a stage, so it logs nothing. It took about 52s, mostly journal re-reads.

The operator asked what the drain was doing for two minutes, and finding out took a profiler. Any later slowness in these phases would be just as invisible.

When this ticket is done, both phases write a start and an end event to `engine.log`, and Recent Steps shows them as engine rows (`Preflight start`, `Preflight end (ok)`, `Retro check start`, `Retro check end (no report)`).

## Scope in / Scope out
- In: two new `engine.log` events, `phase_start` and `phase_end`, each with `phase` from the closed set `preflight` and `retro_check`. `phase_end` adds `outcome`:
  - `preflight`: `ok` or `failed`.
  - `retro_check` in drain: `ran` when `Retro.__call__` returns a report, `no_report` when it returns `None` (not due, suppressed, a caught retro failure, or a kill), and `failed` when it raises. `Retro.__call__` does not distinguish more cases, and `chupa/retro.py` stays outside this ticket.
  - `retro_check` in serve: `due` when `select_trigger` fires (serve only marks the retro due; `run_retro` runs it later), `not_due` otherwise, and `failed` when it raises.
  - An exception ends the phase with `failed` and still propagates.
- In: `tests/integration/test_daemon_composition.py`: `test_production_core_uses_real_snapshot_pipeline` and `test_production_core_awaits_preflight_inside_admission` check the exact preparation trace (around lines 769-770 and 796). The `EngineLog` that `prepare_pipeline` now builds (with `Redactor.from_config`, as `chupa/runner.py` already does for `run_ticket`) adds a `redactor` entry, so only those trace assertions change to the new order.
- In: `chupa/runner.py::prepare_pipeline` logs the `preflight` pair around `llm.preflight()`. That covers drain, run and serve, and a cached `prepare()` that skips preflight logs nothing.
- In: `chupa/drain.py::_Drain._run_retro` and `chupa/serve.py::Serve.check_retro` log the `retro_check` pair. When the drain's retro runs a retro stage, its existing `stage_start` and `stage_end` sit inside the pair.
- In: `chupa/observe.py::recent_steps` renders the events as engine rows with `stem` `None`. The text is `Preflight start`, `Preflight end (<outcome>)`, `Retro check start` or `Retro check end (<outcome with _ as a space>)`. The kinds are `phase_start`, `phase_failed` for outcome `failed`, and `phase_ok` for every other outcome. Names come from a Python table next to `STEP_NAMES`.
- In: `vscode-chupa/extension.js`'s `icons` lookup table gains `phase_start`, `phase_ok` and `phase_failed` (the `pulse` codicon with the same pass and fail colors as other rows). Nothing else in JavaScript changes.
- In: `docs/how-chupa-works.md`, section 10, the `engine.log` row names the two phase events.
- Out:
  - Making preflight or the retro check faster (tickets `retro-reemit-skip` and `journal-incremental-read`).
  - Phase events for reconcile, intake or ticket selection: no measured gap names them.
  - The journal: these are diagnostics only.

## Scope fence
- chupa/runner.py
- chupa/drain.py
- chupa/serve.py
- chupa/observe.py
- vscode-chupa/extension.js
- docs/how-chupa-works.md
- tests/integration/test_watch.py
- tests/integration/test_daemon_composition.py
- tests/unit/test_phase_events.py

## Acceptance criteria
1. `tests/unit/test_phase_events.py`, with fake providers and a recording engine log:
   - A `prepare_pipeline` whose preflight passes logs exactly `phase_start` then `phase_end` with `phase` `preflight` and `outcome` `ok`.
   - A failing preflight logs `phase_end` with `outcome` `failed`, and `prepare_pipeline` still raises its `Refusal`.
   - A fake provider whose `preflight` raises logs `phase_end` with `preflight` and `failed`, and the exception propagates.
   - A drain retro hook returning `None` logs `retro_check` ending `no_report`. One returning a report logs `ran`. One that raises logs `failed` and re-raises.
   - Serve's `check_retro` logs `not_due` with no trigger and `due` with a firing trigger. When its journal or evidence read raises, it logs `failed` and re-raises.
2. `tests/integration/test_watch.py`: `recent_steps` renders a `preflight` pair as `Preflight start` and `Preflight end (ok)`, with kinds `phase_start` and `phase_ok` and `stem` `None`. It renders a `retro_check` end with outcome `no_report` as `Retro check end (no report)`, not the raw `phase_end` or `retro_check` text. A `failed` end renders kind `phase_failed`.
3. `vscode-chupa/extension.js`'s `icons` table has the keys `phase_start`, `phase_ok` and `phase_failed`.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- Phase events are written to the journal.
- The extension derives a phase row's text or kind instead of reading the snapshot's.
- A cached `prepare()` that runs no preflight logs a `preflight` pair.

## Time budget
- expected: 45m
- stuck: 90m
