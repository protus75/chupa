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

When this ticket is done, both phases write a start and an end event to `engine.log`, and Recent Steps shows them as engine rows (`Preflight start`, `Preflight end (ok)`, `Retro check start`, `Retro check end (not due)`).

## Scope in / Scope out
- In: two new `engine.log` events, `phase_start` and `phase_end`, each with `phase` from the closed set `preflight` and `retro_check`. `phase_end` adds `outcome`:
  - `preflight`: `ok` or `failed`.
  - `retro_check`: `not_due`, `ran`, or `failed`.
  - An exception ends the phase with `failed` and still propagates.
- In: `chupa/runner.py::prepare_pipeline` logs the `preflight` pair around `llm.preflight()`. That covers drain, run and serve, and a cached `prepare()` that skips preflight logs nothing.
- In: `chupa/drain.py::_Drain._run_retro` and `chupa/serve.py::Serve.check_retro` log the `retro_check` pair. When the retro then runs a retro stage, its existing `stage_start` and `stage_end` sit inside the pair, and the outcome is `ran`.
- In: `chupa/observe.py::recent_steps` renders the events as engine rows with `stem` `None`. The text is `Preflight start`, `Preflight end (<outcome>)`, `Retro check start` or `Retro check end (<outcome with _ as a space>)`. The kinds are `phase_start`, `phase_ok` (for `ok` and `not_due`) and `phase_failed` (for `failed`; `ran` is `phase_ok`). Names come from a Python table next to `STEP_NAMES`.
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
- tests/unit/test_phase_events.py

## Acceptance criteria
1. `tests/unit/test_phase_events.py`, with fake providers and a recording engine log:
   - A `prepare_pipeline` whose preflight passes logs exactly `phase_start` then `phase_end` with `phase` `preflight` and `outcome` `ok`.
   - A failing preflight logs `phase_end` with `outcome` `failed`, and `prepare_pipeline` still raises its `Refusal`.
   - A drain retro check with no trigger logs `retro_check` ending `not_due`. One that runs a retro logs `ran`, with the retro's `stage_start` and `stage_end` between the pair.
   - Serve's `check_retro` with no trigger logs `retro_check` ending `not_due`.
2. `tests/integration/test_watch.py`: `recent_steps` renders a `preflight` pair as `Preflight start` and `Preflight end (ok)`, with kinds `phase_start` and `phase_ok` and `stem` `None`. It renders a `retro_check` end with outcome `not_due` as `Retro check end (not due)`, not the raw `phase_end` or `retro_check` text.
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
