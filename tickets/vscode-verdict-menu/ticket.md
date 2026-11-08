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
- chupa/control.py::ControlInbox.consume
- chupa/__main__.py::_verdict
- tests/integration/test_watch.py::test_snapshot_display_fields
- vscode-chupa/media/view.js
- vscode-chupa/package.json

## Goal / Why
With an engine running, the extension greys out or hides Confirm and Reject on a held ticket (`premise_failed`, Reject queue). The CLI does the same thing successfully: `chupa confirm`/`reject` hands the request to the running engine (`_verdict` in `chupa/__main__.py`), and the engine accepts a confirm or reject for any known stem (`ControlInbox.consume` in `chupa/control.py`). On 2026-11-08 the owner could not confirm `core-drift-preflight` from the tickets view while `serve` ran. The menu gate is also a policy choice made in `package.json` `when`/`enablement` clauses, which the thin-wrapper rule bans.

After this change, each snapshot row carries `verdict`, true when the ticket can take a confirm or reject now. The extension shows Confirm and Reject, enabled, exactly when `verdict` is true, and never greys them out while an engine runs.

## Scope in / Scope out
- In: `chupa/observe.py` `snapshot`. Each row gains `verdict: bool`, which is true when both of these hold:
  - the row is a committed draft or held (`draft or held`);
  - it is committed, or no engine is alive (`committed or not engine`).

  An uncommitted ticket cannot reach a running engine's verdict. With no engine, the CLI takes the lock and runs intake itself.
- In: `vscode-chupa/media/view.js`: add `chupaVerdict: r.verdict` to the row's `vscodeContext`.
- In: `vscode-chupa/package.json`.
  - The `chupa.tickets` context-menu entries for `chupa.ticket.confirm` and `chupa.ticket.reject` use `"when": "webviewId == 'chupa.tickets' && chupaVerdict"`.
  - Both commands drop their `enablement` key, so they are never greyed.
  - Remove `chupaEngine`, `chupaDraft`, `chupaHeld`, `chupaCommitted` and `config.chupa.unavailableMenuItems` from those two entries only.
- In: `tests/integration/test_watch.py`: a snapshot test covering these cases:
  - a held, committed row has `verdict` true both with and without a live engine;
  - an uncommitted new ticket has `verdict` false with a live engine and true without one;
  - a queued, not-held ticket has `verdict` false.
- Out: every other menu item (Review and Run need the lock and stay gated), `chupa.unavailableMenuItems` for other items, and the CLI verbs.

## Scope fence
- chupa/observe.py
- vscode-chupa/media/view.js
- vscode-chupa/package.json
- tests/integration/test_watch.py

## Acceptance criteria
1. `./dev.py test tests/integration/test_watch.py` passes, including a held committed row whose `verdict` is true while the engine is alive, not false.
2. `vscode-chupa/package.json` has no `enablement` on `chupa.ticket.confirm` or `chupa.ticket.reject`, and both tickets-view menu entries are gated only by `chupaVerdict`, checked by reading the file.
3. `vscode-chupa/media/view.js` passes `chupaVerdict: r.verdict` in the row context, checked by reading the file.

## Verification
```
./dev.py test tests/integration/test_watch.py
```

## Definition of rejected
JavaScript or `package.json` decides verdict availability from anything but the snapshot's `verdict`, or Confirm/Reject are shown for a ticket the engine would refuse.

## Time budget
- expected: 20m
- stuck: 50m
