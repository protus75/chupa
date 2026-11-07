---
state: confirmed
source: human
priority: P3
kind: feature
---

## Depends on
- none

## Context
- chupa/observe.py
- tests/integration/test_watch.py
- vscode-chupa/media/view.js
- vscode-chupa/media/view.css

## On-demand
- docs/how-chupa-works.md

## Goal / Why
The Tickets view lists running and queued tickets without their priority. The snapshot already carries `priority` on every row, but only the Details pane shows it. The operator wants to see each running or queued ticket's priority in the list itself (2026-11-07). Choosing which rows show the priority is a policy choice, so per the extension rule in CLAUDE.md it lives in the snapshot, and JavaScript only draws it.

## Scope in / Scope out
- In: `chupa/observe.py`. `snapshot`'s ticket rows gain a `priorityTag` field: the row's `priority` (for example `P1`) when `section` is `running` or `queued`, and `""` otherwise.
- In: `tests/integration/test_watch.py` adds `test_snapshot_priority_tag_on_running_and_queued`.
- In: `vscode-chupa/media/view.js`. When `r.priorityTag` is non-empty, `render` appends `el('span', 'priority', r.priorityTag)` before the stem span. It does no comparison and no lookup.
- In: `vscode-chupa/media/view.css` adds a `.priority` rule styled like `.status`: `--vscode-descriptionForeground` and `font-size: 0.9em`, with `margin-left: 4px` and `flex: none`.
- In: `docs/how-chupa-works.md`. The Tickets view description says running and queued rows show their priority.
- Out:
  - Recent Steps, Details, and the Suggestion Box view;
  - priority colors;
  - sorting;
  - `chupa/graph.py`.

## Scope fence
- chupa/observe.py
- tests/integration/test_watch.py
- vscode-chupa/media/view.js
- vscode-chupa/media/view.css
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_watch.py::test_snapshot_priority_tag_on_running_and_queued` passes. Its fixture has a `P1` running ticket, a `P2` queued ticket, a `P0` blocked ticket, and a `P3` merged ticket. The test asserts `priorityTag` values `P1`, `P2`, `""`, and `""`. It rules out a tag on blocked or merged rows and an empty tag on running or queued rows.
2. `./dev.py test` exits 0.
3. `vscode-chupa/media/view.js` reads `priorityTag` and never compares `r.section` to decide whether to draw it.

## Verification
```
./dev.py test tests/integration/test_watch.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of these is true:
- JavaScript decides which sections show priority;
- JavaScript copies the priority vocabulary;
- existing snapshot row fields change;
- any view other than Tickets changes.

## Time budget
- expected: 15m
- stuck: 45m
