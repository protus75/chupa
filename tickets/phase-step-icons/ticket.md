---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- step-kind-vocabulary

## Context
- chupa/observe.py::PHASE_NAMES
- chupa/observe.py::recent_steps
- tests/integration/test_watch.py::test_recent_steps_phase_events
- tests/regress_graph_lanes.py

## On-demand
- vscode-chupa/extension.js

## Goal / Why
In the extension's Recent Steps view, Preflight rows and Retro check rows show the same icon (`pulse`), so the operator cannot tell them apart at a glance (`evidence/evidence.txt`, operator report 2026-11-11). The cause is in `recent_steps` in `chupa/observe.py`: every `phase_start`/`phase_end` event gets the generic kind `phase_start`, `phase_ok`, or `phase_failed`, whatever its phase. The extension's `StepsTree.getTreeItem` icon table in `vscode-chupa/extension.js` can map only those three kinds.

After this change each phase has its own kind, `<phase>_start`, `<phase>_ok`, and `<phase>_failed` (`preflight_ok`, `retro_check_failed`, and so on), and the extension draws a different icon for each phase.

## Scope in / Scope out
- In: `chupa/observe.py` `recent_steps`. A phase row's `kind` is `f"{phase}_{suffix}"`, where `phase` is the event's `phase` value and `suffix` is `start`, `ok`, or `failed` under the existing outcome rule (`failed` when the outcome is `failed`, else `ok`). Row `text` stays as it is.
- In: `vscode-chupa/extension.js`, the `icons` lookup table in `StepsTree.getTreeItem`. Replace the three `phase_*` entries with `preflight_start`/`_ok`/`_failed` using codicon `rocket` and `retro_check_start`/`_ok`/`_failed` using codicon `calendar`. The `_ok`/`_failed` entries keep the `testing.iconPassed`/`testing.iconFailed` colors that every other step uses. The table stays a plain lookup: no string parsing or derived keys in JavaScript.
- In: `tests/integration/test_watch.py` `test_recent_steps_phase_events`. Change the expected kinds to `retro_check_failed`, `retro_check_ok`, `preflight_ok`, `preflight_start`. Change nothing else in the file.
- In: new `tests/regress_phase_step_kinds.py`, which speaks the regression protocol. It feeds `chupa.observe.recent_steps` one `phase_end` `ok` event for `preflight` and one for `retro_check`. It reports `defect` when the two rows share a `kind`, `pass` when their kinds differ, and `error` when `chupa.observe` cannot be imported or the call raises.
- Out: the journal event shape (`phase_start`/`phase_end` with `phase`), `PHASE_NAMES`, stage rows, engine rows, every other icon entry, and any closed-vocabulary test or harness covering all step kinds. That work belongs to `step-kind-vocabulary`.

## Scope fence
- chupa/observe.py
- vscode-chupa/extension.js
- tests/integration/test_watch.py
- tests/regress_phase_step_kinds.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_watch.py` passes. `test_recent_steps_phase_events` asserts the kinds `retro_check_failed`, `retro_check_ok`, `preflight_ok`, `preflight_start`, not the generic `phase_*` kinds.
2. `uv run python tests/regress_phase_step_kinds.py` prints `{"regression_result": "pass"}` and exits 0.
3. Reading `vscode-chupa/extension.js` shows that the `icons` table has entries for all six keys `preflight_start`, `preflight_ok`, `preflight_failed`, `retro_check_start`, `retro_check_ok`, `retro_check_failed`, that it has no `phase_` key, and that the preflight icon differs from the retro_check icon.

## Verification
```
./dev.py test tests/integration/test_watch.py
uv run python tests/regress_phase_step_kinds.py
```

## Definition of rejected
Reject the branch if any of the following holds:
- Preflight and Retro check rows still share a `kind` or an icon;
- `recent_steps` emits a phase kind that has no entry in the extension's `icons` table (the `icons[step.kind]` destructure would throw and blank the Steps view);
- the JavaScript derives the icon by parsing or splitting `step.kind`;
- the journal event shape or row `text` changes.

## Time budget
- expected: 15m
- stuck: 45m

## Regression
```
uv run python tests/regress_phase_step_kinds.py
```
- carries: tests/regress_phase_step_kinds.py
