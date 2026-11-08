---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- review-unmerged-provisional

## Runs before
- vscode-snapshot-display
- vscode-graph-segments

## Context
- chupa/observe.py::snapshot
- chupa/control.py::ControlInbox.consume
- chupa/__main__.py::_verdict
- chupa/__main__.py::_review
- chupa/__main__.py::_order
- tests/integration/test_watch.py::test_snapshot_display_fields
- vscode-chupa/media/view.js
- vscode-chupa/media/box.js
- vscode-chupa/package.json

## Goal / Why
The extension's right-click menus decide when each action shows, and whether it is greyed out, in `package.json` `when` and `enablement` clauses. Those clauses copy chupa's rules: the section regex `^(queued|blocked)$`, `!= 'merged'`, and which verbs need the writer lock (`!chupaEngine`). The thin-wrapper rule bans this, and the copies are wrong:
- On 2026-11-08 the owner could not confirm a held ticket from the menu while `serve` ran. The engine accepts confirm and reject for any known stem (`ControlInbox.consume`), and `chupa confirm`/`reject` hands the request to the running engine (`_verdict`).
- Review is offered on invalid rows, which `review` refuses at intake.

After this change, Python decides every ticket and box menu action. Each snapshot row carries a `menu` object of context keys, each set to `on`, `locked` (possible but the writer lock is held) or `off`. The extension passes `menu` through unchanged, and `package.json` only maps those values and the `chupa.unavailableMenuItems` setting to show, grey or hide.

## Scope in / Scope out
- In: `chupa/observe.py` `snapshot`. Every row in `rows` and every row in `box` gains `menu: dict[str, str]`, each value one of `on`, `locked`, `off`. "Engine alive" is the snapshot's existing `engine` value. A row is "invalid" when it is one of the `invalid:` rows. Ticket rows:
  - `chupaReview`: `off` unless the section is `queued` or `blocked` and the row is not invalid; then `locked` when the engine is alive, else `on`. (This ticket depends on `review-unmerged-provisional`, so unmerged dependencies no longer block review.)
  - `chupaLint`: `on` for every row whose section is not `merged`, else `off`.
  - `chupaRun`: `off` unless `runnable`; then `locked` when the engine is alive, else `on`.
  - `chupaConfirm` and `chupaReject`: `on` when the row is a draft or held, and is committed or the engine is not alive; else `off`. They are never `locked`: a running engine accepts them.
  - `chupaAskDiagnose`: `on` when the section is not `merged`, else `off`. `chupaAskReview`: `on` for `queued` or `blocked` rows, else `off`.
  - `chupaPriority` and `chupaRunsBefore`: `on` for `queued` or `blocked` rows that are not invalid, else `off`. `order` edits the working tree and takes no lock.
- In: box rows. `chupaTriage` and `chupaDismiss` are `off` unless the message is pending; then `locked` when the engine is alive, else `on`.
- In: `vscode-chupa/media/view.js` and `vscode-chupa/media/box.js`.
  - The row's `vscodeContext` becomes `{...r.menu, chupaStem: r.stem, preventDefaultContextMenuItems: true}` in `view.js`, and `{...row.menu, chupaIds, chupaPath, chupaLink, preventDefaultContextMenuItems: true}` in `box.js`.
  - Drop `chupaSection`, `chupaHeld`, `chupaDraft`, `chupaRunnable`, `chupaCommitted`, `chupaEngine` and `chupaState`.
- In: `vscode-chupa/package.json`. For each action key `K` above, the `webview/context` entry's `when` is the view check plus `(K == 'on' || K == 'locked' && config.chupa.unavailableMenuItems != 'hide')`, and the command's `enablement` is `K == 'on'`. `chupa.ticket.open`, `chupa.box.open`, `chupa.box.link` and `chupa.box.discuss` keep their presence checks (`chupaStem`, `chupaPath`, `chupaLink`, `chupaIds`). The `view/title` entries are unchanged.
- In: `tests/integration/test_watch.py`. A snapshot test asserts `menu` for each of these cases:
  - a held committed row while the engine is alive: `chupaConfirm` `on`, `chupaRun` `off`;
  - the same held row with an uncommitted edit (stem in `dirty`, not in `new`): with the engine alive, `chupaConfirm` and `chupaReject` `off`; with no engine, both `on`;
  - a queued runnable row with no engine (`chupaRun`/`chupaReview` `on`) and with an engine (`locked`);
  - an invalid row: `chupaReview` and `chupaPriority` `off`;
  - a merged row: `chupaLint` `off`;
  - a pending box message with an engine: `chupaTriage` `locked`.
- Out: the `view/title` menu, the CLI verbs, the rest of the extension's JavaScript (`vscode-snapshot-display` and `vscode-graph-segments` cover it), and `chupa.unavailableMenuItems` itself.

## Scope fence
- chupa/observe.py
- vscode-chupa/media/view.js
- vscode-chupa/media/box.js
- vscode-chupa/package.json
- tests/integration/test_watch.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_watch.py` passes. It includes a held committed row whose `menu["chupaConfirm"]` is `on` while the engine is alive, not `off`, the same held row with an uncommitted edit whose `menu["chupaConfirm"]` is `off` while the engine is alive, not `on`, and an invalid row whose `menu["chupaReview"]` is `off`, not `on`.
2. No `when` or `enablement` in `vscode-chupa/package.json` mentions `chupaSection`, `chupaHeld`, `chupaDraft`, `chupaRunnable`, `chupaCommitted`, `chupaEngine` or `chupaState`, checked by reading the file.
3. `vscode-chupa/media/view.js` and `vscode-chupa/media/box.js` build `vscodeContext` by spreading the row's `menu`, with no condition, checked by reading the files.

## Verification
```
./dev.py test tests/integration/test_watch.py
```

## Definition of rejected
Any menu `when` or `enablement` decides availability from anything but a snapshot `menu` value and the `chupa.unavailableMenuItems` setting, or JavaScript computes a `menu` value.

## Time budget
- expected: 30m
- stuck: 75m
