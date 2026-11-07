---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/observe.py
- vscode-chupa/extension.js
- tests/test_watch.py
- docs/how-chupa-works.md

## Goal / Why
When the engine is running, the chupa Activity Bar icon shows a small blue number: the count of queued plus running tickets, the same kind of badge Source Control shows for changed files. The operator can see from any sidebar that the engine is working and how much work is queued, without opening the chupa views. The operator asked for this (2026-11-07).

Today nothing appears on the icon. Also, `Snapshot.refresh()` returns early unless a chupa view is visible. A badge set from that snapshot would freeze as soon as the operator switches to another sidebar.

## Scope in / Scope out
- In: `chupa/observe.py` `snapshot()` returns a `badge` field:
  - When the engine is alive (`alive`) and `counts["queued"] + counts["running"]` is greater than 0, the field is `{"value": <that sum>, "tooltip": "<running> running, <queued> queued"}`.
  - Otherwise it is `None`. Blocked and merged tickets never count.
- In: `vscode-chupa/extension.js`:
  - A snapshot listener sets `stepsView.badge` to `snapshot.snap?.badge ?? undefined`. VS Code shows a view's badge on its container's Activity Bar icon. The JavaScript does no counting and no engine-state check.
  - `Snapshot.refresh()` no longer skips when no chupa view is visible, so the file watchers and the `refreshSeconds` timer keep the badge current while the sidebar is hidden. Remove the `views` list that only that check reads, along with its `push` calls.
  - `activate` calls `snapshot.refresh()` once, so the badge appears without opening the sidebar.
- In: `tests/test_watch.py`: a new test built like `test_snapshot_display_fields` (one running row, one queued row, one merged row, and one blocked row if the fixture allows) asserts the following:
  - With `lock_holder` returning a datetime, `snap["badge"] == {"value": 2, "tooltip": "1 running, 1 queued"}`, not 3 or 4, which would mean merged or blocked rows were counted.
  - With `lock_holder` returning `None`, `snap["badge"] is None`, not a badge shown while the engine is dead.
  - With the engine alive and no queued or running rows, `snap["badge"] is None`, not `{"value": 0, ...}`.
- In: `docs/how-chupa-works.md` section 2: the `vscode-chupa/` paragraph gets one sentence on the Activity Bar badge and when it shows.
- Out:
  - Any other snapshot field.
  - `chupa/graph.py`.
  - The webviews and `media/*.js`.
  - `package.json`.
  - Any new setting.

## Scope fence
- chupa/observe.py
- vscode-chupa/extension.js
- tests/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/test_watch.py` exits 0, including the new badge test that rules out counting merged or blocked rows, showing a badge while the engine is dead, and showing a zero badge.
2. `vscode-chupa/extension.js` sets `stepsView.badge` from `snapshot.snap?.badge` and has no `this.views.some(v => v.visible)` check.
3. The `vscode-chupa/` paragraph in `docs/how-chupa-works.md` names the Activity Bar badge.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_watch.py
./dev.py test
```

## Definition of rejected
Reject the branch if the JavaScript computes the count or checks engine state, if the badge shows while the engine is not alive, or if the change adds a setting.

## Time budget
- expected: 25m
- stuck: 75m
