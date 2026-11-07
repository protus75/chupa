---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Runs before
- requisition-coverage-dependents
- tests-split
- fault-injection-shards
- dev-test-leading-options

## Context
- chupa/driver.py
- chupa/stages.py
- chupa/runner.py
- chupa/observe.py
- vscode-chupa/extension.js
- tests/test_watch.py
- docs/how-chupa-works.md

## Goal / Why
The extension's Recent Steps view shows only model-driven stages, and clicking any row opens `ticket.md` (2026-11-07). The engine log gets `stage_start`/`stage_end` only from `Driver` (`chupa/driver.py`), so the mechanical Check and merge steps never appear. `StepsTree.getTreeItem` in `vscode-chupa/extension.js` builds the `tickets/<stem>/ticket.md` path in JavaScript, which breaks the thin-wrapper rule in CLAUDE.md. A Review or Diagnose row should open the file that step wrote.

After this change:
- Check and merge write start/end events to the engine log.
- `chupa snapshot` reports each step with the file to open and a kind for its icon.
- Recent Steps shows Check and merge rows with their own icons and opens each step's file.

## Scope in / Scope out
- In: `chupa/stages.py`, `run_stages`: around the `check` stage, log `stage_start` and `stage_end` through `ctx.driver.log.event`. Use the fields `Driver` uses (`stem`, `attempt`, `surface="check"`); `stage_end` adds `outcome` from the Check `StageResult`.
- In: `chupa/runner.py`, the merge call in `drive` (`stage, result = "merge", await (admission(...) if admission is not None else merge(...))`): log the same pair with `surface="merge"`. This one call site covers the inline and serve admission paths. A `ConflictHandoff` result logs `outcome="conflict"`.
- In: `chupa/observe.py`:
  - `STEP_NAMES` gains `check: "Check"` and `merge: "Merge"`; drop the comment saying Check and merge leave no stage events.
  - `recent_steps` gives check and merge rows the kinds `check_start`/`check_ok`/`check_failed` and `merge_start`/`merge_ok`/`merge_failed`. Every other stage keeps `stage_start`/`stage_ok`/`stage_failed`.
  - `current_step` returns `None` as the surface for a running check or merge, so `watch` prints no tier or model line for a mechanical step. Its after-map gains `check: "Review"`.
  - `snapshot` adds `path` to every step that has a stem: `tickets/<stem>/<file>`, where the file is `run.md` for implement, `checks.json` for check, `review.md` for review, and `diagnosis.json` for diagnose. Use `tickets/<stem>/ticket.md` for every other surface, or when that file does not exist under `ctx.root`.
- In: `vscode-chupa/extension.js`, `StepsTree.getTreeItem`:
  - The click command opens `step.path` when present and no longer builds a path.
  - The icon table maps the new kinds through a lookup: check kinds to ThemeIcon `checklist`, merge kinds to `git-merge`. `*_ok` uses ThemeColor `testing.iconPassed`, `*_failed` uses `testing.iconFailed`, and `*_start` has no color.
- In: `docs/how-chupa-works.md`:
  - section 10.1, the `engine.log` row: stage start/end events for every stage, including check and merge;
  - section 2.2, the `vscode-chupa/` paragraph: Recent Steps opens each step's file.
- Out: the journal, `chupa/mergequeue.py`, `chupa/merge.py`, Driver's own events, other views, and the extension version (`./dev.py vscode` bumps it).

## Scope fence
- chupa/stages.py
- chupa/runner.py
- chupa/observe.py
- vscode-chupa/extension.js
- tests/test_watch.py
- tests/test_step_events.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/test_step_events.py` runs a ticket through `run_stages` with a scope-fence violation. The engine log holds `stage_start` then `stage_end` with `surface: "check"` and `outcome: "gate_failed"`, not zero check events.
2. `tests/test_step_events.py` drives a passing ticket to merged through `runner.drive`. The engine log holds `stage_start` then `stage_end` with `surface: "merge"` and `outcome: "ok"`.
3. `tests/test_watch.py`: a snapshot step for an implement row whose `tickets/<stem>/run.md` exists has `path` `tickets/<stem>/run.md`. With the file absent, `path` is `tickets/<stem>/ticket.md`, not a missing file.
4. `tests/test_watch.py`: a check `stage_start` row has text `Check start`, kind `check_start`, and `path` `tickets/<stem>/checks.json` when that file exists. `current_step` for a running merge returns surface `None`.
5. `node --check vscode-chupa/extension.js` exits 0, and `extension.js` contains no `ticket.md` path template inside `StepsTree`.
6. `./dev.py test` exits 0.

## Verification
```
node --check vscode-chupa/extension.js
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the journal gains any event for check or merge start/end;
- `extension.js` derives a step's file path or kind;
- merge events are logged in only one of the inline or serve admission paths;
- any file outside the fence changes.

## Time budget
- expected: 40m
- stuck: 120m
