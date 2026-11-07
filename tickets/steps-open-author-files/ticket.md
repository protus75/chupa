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
- chupa/box.py
- chupa/author.py
- tests/integration/test_watch.py
- vscode-chupa/extension.js

## On-demand
- docs/how-chupa-works.md

## Goal / Why
Clicking an Author row in the extension's Recent Steps view opens nothing (2026-11-07). The Author stage logs its `stage_start` and `stage_end` events with `stem: "author"` and `attempt: <box message seq>`. `snapshot` in `chupa/observe.py` therefore points each Author row at `tickets/author/ticket.md`, which never exists, so `chupa.openTicket` has nothing to open.

After this change, each Author row's snapshot `path` names the file the operator wants:
- `Author start` opens the Suggestion Box message being authored.
- `Author end (ok)` opens the ticket that was produced.
- `Author end (<failure>)` opens the decision record the failure wrote (`tickets/decisions/declined-box-...md`), or the Suggestion Box message when no record exists.

## Scope in / Scope out
- In: `chupa/observe.py`.
  - `recent_steps` keeps the log event's `attempt` on stage rows. `snapshot` pops it, as it already pops `surface`, so it never reaches the extension.
  - In `snapshot`'s steps loop, an `author` surface row looks up the box message whose `seq` equals that attempt. It reuses the message `path` and resolution `link` that the box rows already compute, moving the box load above the steps loop.
    - start row: the message's `path`.
    - end row: the message's resolution `link` when that file exists, otherwise the message's `path`. When the outcome is `ok`, the link is the ticket. When the outcome is a failure, it is the declined record.
    - no matching message: `path` is `None`, so the row stays unclickable rather than pointing at a missing file.
  - Rows for other surfaces keep their current paths.
- In: `tests/integration/test_watch.py` adds `test_snapshot_author_steps_open_box_ticket_or_decision`.
- In: `docs/how-chupa-works.md`. Where it says Recent Steps opens each step's file, add that an Author row opens its Suggestion Box message, its authored ticket, or its decision record.
- Out:
  - `vscode-chupa/extension.js` (it already opens `step.path`);
  - the engine log event shape;
  - `chupa/author.py`;
  - Triage rows;
  - watch's text view.

## Scope fence
- chupa/observe.py
- tests/integration/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_watch.py::test_snapshot_author_steps_open_box_ticket_or_decision` passes. Its fixture has three box messages, each with an Author `stage_start` and `stage_end` pair in `engine.log` whose `attempt` is the message's `seq`:
   - message A resolves to ticket `alpha`, which exists, and its end outcome is `ok`. Its start row's `path` is A's box file, and its end row's `path` is `tickets/alpha/ticket.md`.
   - message B resolves to declined record `declined-box-...`, whose file exists, and its end outcome is `gate_failed`. Its end row's `path` is that `tickets/decisions/<id>.md`.
   - message C is unresolved and its end outcome is `gate_failed`. Its end row's `path` is C's box file.

   The test also asserts:
   - no Author row's path is `tickets/author/ticket.md`;
   - no step row carries an `attempt` key.

   It rules out the current unopenable path, and an `ok` row that opens the message instead of the ticket.
2. `./dev.py test tests/integration/test_watch.py` exits 0. `test_snapshot_step_files_and_mechanical_kinds` still passes unchanged.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_watch.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of these is true:
- `vscode-chupa/extension.js` changes;
- JavaScript derives the Author path;
- the engine log event shape changes;
- an Author row's path names a file that does not exist;
- the paths of non-Author rows change.

## Time budget
- expected: 25m
- stuck: 75m
