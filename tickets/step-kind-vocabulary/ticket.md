---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- none

## Context
- chupa/observe.py::STEP_NAMES
- chupa/observe.py::PHASE_NAMES
- chupa/observe.py::recent_steps
- tests/vscode_task_identity.js
- tests/regress_vscode_task_identity.py
- tests/integration/test_vscode_command_not_found.py
- vscode-chupa/extension.js
- docs/how-chupa-works.md#2. Commands

## Goal / Why
Recent Steps icons have collapsed four times on the same surface: retro and rework, the mechanical check and merge stages, author, and now preflight and retro check (`evidence/recurrence.txt`, `evidence/evidence.txt`). Each fix added one kind to `recent_steps` in `chupa/observe.py` and one entry to the hand-written `icons` table in `StepsTree.getTreeItem` in `vscode-chupa/extension.js`. Nothing checks the whole set of kinds the snapshot can emit against that table. So a new journal surface or phase reaches the extension either as a generic kind that shares an icon, or as a kind with no table entry, which throws in `icons[step.kind]` and blanks the Steps view.

After this change, `chupa/observe.py` owns a closed step-kind vocabulary derived from `STEP_NAMES` and `PHASE_NAMES`. A test drives the real extension code over every kind in that vocabulary and fails when a kind has no icon or when two different steps share one. The next new surface or phase fails `./dev.py test` until it gets its own icon.

## Scope in / Scope out
- In: `chupa/observe.py`. Add a module constant `STEP_KINDS: dict[str, str]` that maps every step-row `kind` that `recent_steps` can emit to the step it belongs to:
  - for each key of `STEP_NAMES` and `PHASE_NAMES`, and for the `stage` fallback, `<key>_start`, `<key>_ok`, and `<key>_failed` map to `<key>`;
  - `engine_start`, `engine_stop`, and `engine_lost` each map to themselves.
  Build it from those dicts, not as a hand-copied list, so a new surface or phase extends it automatically. `recent_steps` keeps its current output.
- In: new `tests/vscode_step_icons.js`, a node harness modeled on `tests/vscode_task_identity.js`. It loads `vscode-chupa/extension.js` with a mocked `vscode`, captures the `chupa.steps` tree data provider from `createTreeView`, and calls `getTreeItem` for each kind in a JSON list passed on argv. It prints one JSON object that maps each kind to its `ThemeIcon` id, or to `null` when `getTreeItem` throws.
- In: new `tests/integration/test_step_icons.py`, which runs that harness with `list(STEP_KINDS)` and asserts:
  - every kind maps to a non-null icon id;
  - kinds of the same step share one icon id, and no two steps share one;
  - `recent_steps`, fed a log with one start, ok, and failed event for every `STEP_NAMES` surface and every `PHASE_NAMES` phase, emits only kinds that are in `STEP_KINDS`.
- In: new `tests/regress_step_kind_icons.py`, which speaks the regression protocol and follows `tests/regress_vscode_task_identity.py`. It imports `STEP_KINDS` and runs the harness. It reports:
  - `defect` when `chupa.observe` has no `STEP_KINDS` (the base commit has no closed vocabulary, which is the defect), when a kind has no icon, or when two steps share an icon;
  - `pass` otherwise;
  - `error` when node is missing, the harness fails, or `chupa.observe` itself cannot be imported.
- In: `docs/how-chupa-works.md` section 2 (Commands), in the paragraph on the extension's views. Add one sentence: Recent Steps row kinds are the closed vocabulary `STEP_KINDS` in `chupa/observe.py`, and a test fails until each step in it has its own icon.
- Out: the journal event shape, row `text`, stage and phase names, and icon choices for existing kinds. Out: the instance fix for preflight and retro check, which is `phase-step-icons`. Out: any change to `vscode-chupa/extension.js`. If the new test finds a kind with no icon or a shared icon, that is a second problem: file it with `chupa suggest` and do not fix it here.

## Scope fence
- chupa/observe.py
- tests/vscode_step_icons.js
- tests/integration/test_step_icons.py
- tests/regress_step_kind_icons.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_step_icons.py` passes. It includes a check that fails when two different steps share an icon id (for example, `preflight_ok` and `retro_check_ok` both mapping to `pulse`), not only when a kind is missing from the table.
2. `./dev.py test tests/integration/test_watch.py` still passes unchanged.
3. `uv run python tests/regress_step_kind_icons.py` prints `{"regression_result": "pass"}` and exits 0.
4. Reading `chupa/observe.py` shows that `STEP_KINDS` is computed from `STEP_NAMES` and `PHASE_NAMES`, not written out as literal kind strings.
5. Reading `docs/how-chupa-works.md` shows the section 2 sentence naming `STEP_KINDS` and its icon test.

## Verification
```
./dev.py test tests/integration/test_step_icons.py tests/integration/test_watch.py
uv run python tests/regress_step_kind_icons.py
```

## Definition of rejected
Reject the branch if any of the following holds:
- `STEP_KINDS` is a hand-written literal list, so adding a key to `STEP_NAMES` or `PHASE_NAMES` does not extend it;
- the icon test reads `extension.js` as text instead of running `getTreeItem`;
- `vscode-chupa/extension.js` changes;
- `recent_steps` output changes.

## Time budget
- expected: 30m
- stuck: 75m

## Regression
```
uv run python tests/regress_step_kind_icons.py
```
- carries: tests/regress_step_kind_icons.py
- carries: tests/vscode_step_icons.js
