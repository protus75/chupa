---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- box-verbs
- observe-verbs-host-extension

## Context
- chupa/box.py
- chupa/status.py
- chupa/ask.py
- chupa/observe.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- vscode-chupa/media/view.js
- vscode-chupa/media/detail.js
- vscode-chupa/media/view.css
- tests/test_watch.py
- docs/how-chupa-works.md

## Goal / Why
The Suggestion Box holds 327 pending messages, and the extension has no view of them (2026-11-06). The operator wants to read the messages in VS Code and settle them by hand, one or many at a time. Triage runs only when the operator asks; nothing here triages on its own.

`box-verbs` adds the engine side (`status` block, `triage [ID ...]`, `dismiss`, `prompt box`, `Box.path`). This ticket adds the snapshot data and the view that drive them.

After this change the extension has a **Suggestion Box** view directly below Tickets. It looks and behaves like the Tickets view without the graph: one row per message, hover shows it in Details, click pins, and right-click acts on one message or a multi-selection.

## Scope in / Scope out
- In: the snapshot (`chupa snapshot`, built in `chupa/observe.py`):
  - A `box` list of every message, newest first (descending `seq`). Each entry has:
    - `id`;
    - `seq`;
    - `messageClass`;
    - `state`: closed, `pending` or `resolved`;
    - `status`: the `<class> · <label>` text the row shows, with the label `status` uses;
    - `summary`: the first line, cut as in `status`;
    - `fields`: `[label, text]` pairs for Details. Always Summary (full text) and Origin; then, when set, Stage (`<stage>: <outcome>`), Re-reports, Recorded verdict (`<verdict>: <rationale>`), Resolution (`<kind> -> <link>`), Fixed failure, Overcorrection risk, Retro report, and Proposed specs;
    - `path`: the message file (from `Box.path`) relative to the workspace root, or null when the state dir is outside it;
    - `link`: for a resolved message, `tickets/<stem>/ticket.md` (kind `ticket`) or `tickets/decisions/<record>.md`; otherwise null.
  - `boxCounts`: `pending`, `author`, `tombstone`, `decision`.
- In: `vscode-chupa/package.json`:
  - A webview view `chupa.box`, named `Suggestion Box`, placed directly after `chupa.tickets`. A view that must stay last (the planned Stats view) still goes after it.
  - Right-click (`webview/context`, `webviewId == 'chupa.box'`), in this order:
    - **Open message file**: shown when the row has a `path`.
    - **Open ticket/record**: shown when the row has a `link`.
    - **Triage** and **Dismiss**: shown when the right-clicked row is pending. Like Review and Run on tickets, they are disabled while an engine holds the lock, or hidden under `chupa.unavailableMenuItems: hide`.
    - **Ask Claude: discuss**: always shown.
  - **Bulk Triage** in the Tickets view's title overflow menu, beside Drain, Stop, Kill and Status: it runs `triage` with no ids.
  - The new commands are hidden from the command palette, like the ticket commands.
- In: `vscode-chupa/extension.js`:
  - `BoxView`, following `TicketsView`.
  - Details shows the box message or the ticket that was last hovered or pinned, falling back to the other view's pin, then to the running ticket.
  - Triage (`triage <ids>`), Dismiss (`dismiss <ids>`), and Bulk Triage (`triage`) run through the configured chupa command, as the other engine actions do. Ask Claude: discuss runs `prompt box <ids>` and opens the Claude Code chat the way the ticket Ask Claude items do.
  - The state-dir file watcher also watches `box/*.json`.
- In: new `vscode-chupa/media/box.js`, plus `media/detail.js` and `media/view.css`.
  - Rows use the Tickets row style: the summary is colored and the `status` follows it in description color. `state` maps through a lookup table: `pending` to `--chupa-queued` (blue), `resolved` to `--chupa-merged` (purple).
  - The header line shows `<pending> pending · <author> author · <tombstone> tombstone · <decision> decision`, plus `· <n> selected` when more than one row is selected.
  - Mouse and keys:
    - hover shows the row in Details;
    - click selects and pins the row, and a second click on the only selected row clears both;
    - Ctrl/Cmd-click toggles a row in the selection, and Shift-click selects the range from the last clicked row;
    - Ctrl/Cmd-A selects all, and Escape clears;
    - double-click opens the message file;
    - right-click on an unselected row selects only it.
  - A menu command acts on every selected row when the right-clicked row is selected, else on that row alone. The ids go to the command in order; the engine skips resolved ones.
  - Details for a box message shows a class badge, the id, each `fields` pair as a section, and open links for `path` and `link`.
- In: `tests/test_watch.py`: snapshot `box` order is newest first, not oldest first; a resolved message has `state: resolved`, its label, and a `link`; `path` names an existing file; the counts match.
- In: `docs/how-chupa-works.md`: the `vscode-chupa/` paragraph describes the Suggestion Box view.
- Out:
  - the CLI verbs, `status`, and `Box.path` (ticket `box-verbs`);
  - automatic triage of any kind;
  - deleting box files;
  - the Tickets view's rows, graph, and existing menu entries;
  - the extension version (`./dev.py vscode` bumps it).

## Scope fence
- chupa/observe.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- vscode-chupa/media/box.js
- vscode-chupa/media/detail.js
- vscode-chupa/media/view.css
- tests/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/test_watch.py` exits 0, including every test listed in Scope in.
2. `node --check vscode-chupa/extension.js`, `node --check vscode-chupa/media/box.js`, and `node --check vscode-chupa/media/detail.js` exit 0.
3. `vscode-chupa/package.json` lists `chupa.box` immediately after `chupa.tickets` in the `chupa` views array.
4. `grep -n "sort\|filter" vscode-chupa/media/box.js` prints nothing: row order and selection ids come from the snapshot order, not from JavaScript sorting or filtering.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_watch.py
node --check vscode-chupa/extension.js
node --check vscode-chupa/media/box.js
node --check vscode-chupa/media/detail.js
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- anything triages without an operator command naming it (Triage or Bulk Triage);
- the snapshot writes anything;
- the extension's JavaScript sorts or filters rows, derives a state, label, or color choice beyond the lookup table, or copies a chupa constant;
- the Tickets view's existing rows, or its existing right-click or title-menu entries, change (adding Bulk Triage to the title overflow menu is required).

## Time budget
- expected: 75m
- stuck: 150m
