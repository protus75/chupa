---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/observe.py::snapshot
- tests/integration/test_watch.py::test_snapshot_display_fields
- vscode-chupa/extension.js
- vscode-chupa/media/detail.js

## Goal / Why
The thin-wrapper rule says the extension only draws snapshot fields. A 2026-11-08 audit found `vscode-chupa` still owns chupa knowledge and display decisions:
- It hard-codes chupa's file layout in its refresh watchers: `tickets/*/ticket.md`, and `{journal/*.jsonl,queue.json,engine.log,box/*.json}` under the state directory. A layout change silently stops the views refreshing.
- The Engine quick pick copies chupa's verb list and its descriptions.
- It parses error text, keeping only the last line of stderr (`.trim().split('\n').pop()`) for the snapshot and stats errors.
- `detail.js` decides which ticket fields to show by testing `section === 'merged'` and composing meta lines.
- `orderTicket` works out which priority is current and which runs-before stems are ticked.
- It duplicates the `refreshSeconds` default (`get('refreshSeconds', 15)`).

After this change, the snapshot supplies each of these, and the extension only displays them and wires them to VS Code.

## Scope in / Scope out
- In: `chupa/observe.py` `snapshot`.
  - Top-level `watch`: a list of `{"base": <absolute path>, "glob": <pattern>}`. It holds `tickets/*/ticket.md` under the repo root, and `{journal/*.jsonl,queue.json,engine.log,box/*.json}` under the resolved state directory: the patterns the extension uses today, now owned here.
  - Top-level `engineVerbs`: a list of `{"label", "detail", "verb"}` with exactly the six entries the Engine quick pick shows today (Drain, Serve, Stop after the running ticket, Kill (drain or serve), Status, Retro), with the same text.
  - Each row gains `priorityChoices`: a list of `{"label": <priority>, "description": "current" | ""}` over the `priorities` list.
  - Each row's `runsBeforeChoices` becomes a list of `{"label": <stem>, "picked": <stem in runsBefore>}` over the same stems as today.
  - Each row gains `detail`: an ordered list of `{"heading": str | None, "text": str}`. A `None` heading is a meta line; any other is a titled section. It reproduces what `detail.js` shows today, in the same order:
    - the status line, with ` · <priority>` when set;
    - `review: <review>` when non-empty;
    - for a merged row: section `Commit` with the subject and a meta line `<short> · <author> · <dateAgo> (<dateDisplay>)`, or the meta line `no commit on main`, then `settled <mergedAtAgo> (<mergedAtDisplay>)` when settled;
    - otherwise: sections `Goal / Why` (text or `(none)`) and `Runs before` (comma-joined or `(none)`);
    - then section `Depends on` when non-empty.
- In: `vscode-chupa/extension.js`.
  - Watchers come from `snapshot.snap.watch`. They are re-created whenever the list's entries change, and none are created before the first snapshot. Remove both hard-coded globs.
  - The `chupa.engine` quick pick shows `snapshot.snap.engineVerbs` (label, detail) and runs the chosen `verb`.
  - The snapshot and stats errors show the whole trimmed stderr, with no splitting.
  - `orderTicket` passes `row.priorityChoices` (label, description) and `row.runsBeforeChoices` (label, picked) straight to `showQuickPick`.
  - Use `get('refreshSeconds')`, with no fallback; `package.json` owns the default.
- In: `vscode-chupa/media/detail.js` `content(row)`. Keep the title (section badge and stem), draw each `row.detail` entry in order (meta line or titled section, as `boxContent` draws `fields`), then the open link. Remove the `section === 'merged'` branch and every reference to `goal`, `runsBefore`, `depends`, `commit`, `mergedAt*` and `review`.
- In: `tests/integration/test_watch.py::test_snapshot_display_fields` and a new snapshot test. Assert:
  - `watch` holds both patterns with absolute bases;
  - `engineVerbs` holds six entries, Drain first;
  - `priorityChoices` marks only the row's own priority `current`;
  - `runsBeforeChoices` entries carry `picked`; update the existing `["waiting"]` and `["live"]` assertions to the new shape over the same stems;
  - a merged row's `detail` has the `Commit` section and the settled meta line;
  - an open row's `detail` has `Goal / Why` and `Runs before`, with `(none)` when empty.
- Out:
  - `chupaRoot()`, which finds the repo before any snapshot can run;
  - the menu `when`/`enablement` clauses (`vscode-verdict-menu`);
  - graph drawing (`vscode-graph-segments`);
  - the header count text in `view.js` and `box.js`;
  - the existing row fields other consumers read.

## Scope fence
- chupa/observe.py
- vscode-chupa/extension.js
- vscode-chupa/media/detail.js
- tests/integration/test_watch.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_watch.py` passes. It asserts `watch` holds both patterns and `engineVerbs` six entries, not zero, and that a merged row's `detail` carries the `Commit` section while an open row's carries `Goal / Why`, not the reverse.
2. `vscode-chupa/extension.js` contains no `tickets/*/ticket.md`, no `journal/*.jsonl`, no `split('\n')` and no verb label strings such as `Run every eligible ticket`, checked by reading the file.
3. `vscode-chupa/media/detail.js` contains no `section === 'merged'` and no `mergedAt`, checked by reading the file.

## Verification
```
./dev.py test tests/integration/test_watch.py
```

## Definition of rejected
The extension still hard-codes a chupa path pattern, verb list or display rule that this ticket moves, or the Details view shows different text than before for the same ticket.

## Time budget
- expected: 30m
- stuck: 75m
