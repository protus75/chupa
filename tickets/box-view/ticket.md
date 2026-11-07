---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- observe-verbs-host-extension

## Context
- chupa/box.py
- chupa/triage.py
- chupa/status.py
- chupa/ask.py
- chupa/specs/ask/review.md
- chupa/__main__.py
- dev.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- vscode-chupa/media/view.js
- vscode-chupa/media/detail.js
- vscode-chupa/media/view.css
- tests/test_status.py
- tests/test_triage.py
- tests/test_ask.py
- tests/test_dev.py
- tests/test_watch.py
- tests/test_host_running.py
- docs/how-chupa-works.md
- docs/host-running.md

## Goal / Why
The Suggestion Box holds 327 pending messages, and the operator cannot see any of them: `status` does not list the box, and the extension has no view of it (2026-11-06). The operator wants to read the messages in VS Code and settle them by hand, one or many at a time. Triage runs only when the operator asks; nothing here triages on its own.

After this change:
- `status` lists every Suggestion Box message and its state.
- `chupa triage [ID ...]` triages only the named messages, or every pending one when no id is given.
- `chupa dismiss ID ...` settles messages as operator decisions without a model call.
- `chupa prompt box ID ...` prints a Claude prompt for discussing the named messages.
- The extension has a **Suggestion Box** view directly below Tickets. It looks and behaves like the Tickets view without the graph: one row per message, hover shows it in Details, click pins, and right-click acts on one message or a multi-selection.

## Scope in / Scope out
- In: `chupa/box.py`: rename `Box._path` to `Box.path` (public) and update its callers, so the snapshot names a message's file without copying the filename rule.
- In: `chupa/status.py`:
  - `Status` gains the box messages, in arrival (`seq`) order, oldest first. Each has: id, class, a state label, and the summary's first line cut to 120 characters (`...` marks a cut).
  - The state label is `pending`, `reopened` (pending with `reopen: true`), `author -> <stem>` (resolution kind `ticket`), `tombstone -> <link>`, or `decision`.
  - `render` adds the block `Suggestion Box (<N> pending, <M> resolved):` after the Reject queue, with one line per message: `<id>: <class>: <label>: <summary>`. An empty box renders `(none)`, as the other blocks do.
- In: `chupa/triage.py`:
  - `triage_pass(checkout, llm, ids=frozenset())`. With ids, it settles only those pending messages; a named message that is already resolved is skipped. An id the box does not hold raises `BoxError` before the pass journals its `triage_pass` signal or makes any call.
  - New `dismiss(checkout, ids) -> list[str]`, with no model call. Every id is checked before anything is written; an unknown id raises `BoxError` and settles none of them. Each pending message gets a decision record `decision-<id>` (link: the message id; `reopen_after_days: 30`; body says it was dismissed by the operator), committed through the same Effects-keyed `ticket-plane/decisions/<record>` commit triage uses, then resolved as `decision`. An already-resolved id prints `<id>: already resolved -> <link>` and writes nothing.
- In: `chupa/ask.py` and new `chupa/specs/ask/box.md`: a `box` prompt kind. It names each message's id and its file under the state dir, and asks Claude to read them and report in plain English, ending with a "Recommendation" section of exact `./dev.py triage`, `./dev.py dismiss`, or ticket-authoring steps, matching the other ask prompts.
- In: `chupa/__main__.py`:
  - `triage` takes optional ids; `dismiss` takes one or more ids. Both hold the writer lock like `triage` does today.
  - `prompt box ID ...` takes one or more ids and takes no lock. The ticket kinds still take exactly one stem.
  - An unknown id refuses with exit 2: `chupa <verb>: unknown box id <id> -- name ids that chupa status lists`.
- In: `dev.py`: `triage [ID ...]` and `dismiss ID ...`, each passing every id to one chupa call (one triage pass, not one per id), with docstring lines.
- In: the snapshot (`chupa snapshot`, built in `chupa/observe.py` by `observe-verbs-host-extension`):
  - A `box` list of every message, newest first (descending `seq`). Each entry has:
    - `id`;
    - `seq`;
    - `messageClass`;
    - `state`: closed, `pending` or `resolved`;
    - `status`: the `<class> · <label>` text the row shows;
    - `summary`: the first line, cut as in `status`;
    - `fields`: `[label, text]` pairs for Details. Always Summary (full text) and Origin; then, when set, Stage (`<stage>: <outcome>`), Re-reports, Recorded verdict (`<verdict>: <rationale>`), Resolution (`<kind> -> <link>`), Fixed failure, Overcorrection risk, Retro report, and Proposed specs;
    - `path`: the message file relative to the workspace root, or null when the state dir is outside it;
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
  - Triage, Dismiss, and Bulk Triage run through the configured chupa command, as the other engine actions do. Ask Claude: discuss runs `prompt box <ids>` and opens the Claude Code chat the way the ticket Ask Claude items do.
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
- In: tests:
  - `tests/test_status.py`: the block lists pending and resolved messages oldest first with their labels; a multi-line summary renders as its first line only, not the whole text; a 200-character summary is cut to 117 characters plus `...`; an empty box renders `(none)`.
  - `tests/test_triage.py`:
    - `triage <id>` with two pending messages settles the named one only and makes one model call, not two;
    - an unknown id exits 2 with no model call and no `triage_pass` signal;
    - `dismiss` of two ids commits two decision records with no model call;
    - a repeated dismiss prints `already resolved` and adds no commit;
    - `dismiss <pending> <unknown>` exits 2 and leaves the pending message pending.
  - `tests/test_ask.py`: the `box` prompt names every requested id and its file under a non-default state dir.
  - `tests/test_watch.py`: snapshot `box` order is newest first, not oldest first; a resolved message has `state: resolved`, its label, and a `link`; `path` names an existing file; the counts match.
  - `tests/test_dev.py`: `triage` and `dismiss` pass every id to a single chupa call.
  - The `Box.path` rename updates `tests/test_box.py`, `tests/test_daemon_soak.py`, and `tests/test_storm_notification_activation.py`.
- In: docs.
  - `docs/how-chupa-works.md`:
    - section 2.1: `triage [id ...]`, `dismiss`, and `prompt box`;
    - section 2.2: `./dev.py triage` and `./dev.py dismiss`;
    - section 9.2: dismiss;
    - section 10.3: the Suggestion Box block;
    - the `vscode-chupa/` paragraph: the Suggestion Box view.
  - `docs/host-running.md`: a `dismiss` row in the verb table (works while serve runs: No), which `tests/test_host_running.py::test_verb_table_matches_parser` requires; the `triage` and `prompt` rows mention ids.
- Out:
  - `serve`'s background triage loop (a separate ticket removes it);
  - automatic triage of any kind;
  - bulk dismissal from the CLI with no ids;
  - deleting box files;
  - a new resolution kind;
  - the Tickets view's rows, graph, and existing menus;
  - the extension version (`./dev.py vscode` bumps it).

## Scope fence
- chupa/box.py
- chupa/status.py
- chupa/triage.py
- chupa/ask.py
- chupa/specs/ask/box.md
- chupa/__main__.py
- chupa/observe.py
- dev.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- vscode-chupa/media/box.js
- vscode-chupa/media/detail.js
- vscode-chupa/media/view.css
- tests/test_status.py
- tests/test_triage.py
- tests/test_ask.py
- tests/test_watch.py
- tests/test_dev.py
- tests/test_box.py
- tests/test_daemon_soak.py
- tests/test_storm_notification_activation.py
- docs/how-chupa-works.md
- docs/host-running.md

## Acceptance criteria
1. `./dev.py test tests/test_status.py tests/test_triage.py tests/test_ask.py tests/test_watch.py tests/test_dev.py` exits 0, including every test listed in Scope in.
2. `./dev.py test tests/test_host_running.py` exits 0: the verb table lists `dismiss`.
3. `node --check vscode-chupa/extension.js`, `node --check vscode-chupa/media/box.js`, and `node --check vscode-chupa/media/detail.js` exit 0.
4. `vscode-chupa/package.json` lists `chupa.box` immediately after `chupa.tickets` in the `chupa` views array.
5. `grep -n "sort\|filter" vscode-chupa/media/box.js` prints nothing: row order and selection ids come from the snapshot order, not from JavaScript sorting or filtering.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_status.py tests/test_triage.py tests/test_ask.py tests/test_watch.py tests/test_dev.py
./dev.py test tests/test_host_running.py
node --check vscode-chupa/extension.js
node --check vscode-chupa/media/box.js
node --check vscode-chupa/media/detail.js
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- anything triages without an operator command naming it (`triage`, Triage, or Bulk Triage);
- `dismiss` makes a model call, or deletes or rewrites a box file other than through `Box.resolve`;
- an unknown id settles any message;
- `status` or the snapshot writes anything;
- the extension's JavaScript sorts or filters rows, derives a state, label, or color choice beyond the lookup table, or copies a chupa constant;
- the Tickets view's existing rows or menus change.

## Time budget
- expected: 90m
- stuck: 180m
