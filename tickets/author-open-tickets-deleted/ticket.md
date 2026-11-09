---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
none

## Context
- chupa/author.py::_open_tickets
- chupa/triage.py::_committed
- tests/regress_status_optional_locks.py

## Goal / Why
`chupa triage` crashes with `FileNotFoundError` whenever a tracked `tickets/<stem>/ticket.md` is deleted in the working tree but the deletion is not committed (`evidence/triage-traceback.txt`). `author._open_tickets` lists stems from `git ls-files` (the index) but reads each ticket's text from the working tree, so an index entry with no file on disk aborts the whole triage pass, not just one message.

Triage's own open-ticket list (`chupa/triage.py`, the `open_tickets` loop in `_settle_pass`) globs the working tree and so already skips such a file. After this change `_open_tickets` skips it too, and triage completes with a deleted-but-uncommitted ticket in the tree.

## Scope in / Scope out
- In: `chupa/author.py` `_open_tickets` skips an index path whose file is absent from the working tree; every other entry is listed exactly as today.
- In: new `tests/regress_author_open_tickets_deleted.py`, the carried reproducer. Like `tests/regress_status_optional_locks.py`, it puts the repo root on `sys.path` and imports `chupa.author`. In a temporary directory it writes `tickets/live/ticket.md` whose `## Goal / Why` first line is `live goal`, and leaves `tickets/gone/` absent. It calls `asyncio.run(author._open_tickets(checkout))` with a `types.SimpleNamespace` checkout: `repo` is the temp dir, `git.ls_files` is an async function returning `["tickets/gone/ticket.md", "tickets/live/ticket.md"]`, and `journal.read` returns `[]`.
  - Returns exactly `"live: live goal"`: prints `{"regression_result": "pass"}` and exits 0.
  - Raises `FileNotFoundError`: prints `{"regression_result": "defect"}` and exits 1.
  - Anything else (import failure, another exception, a different string): the traceback or value goes to stderr, and it prints `{"regression_result": "error"}` and exits 2.
- Out: triage's own `open_tickets` loop; the other `ls_files` callers in `chupa/author.py` and `chupa/daemon.py`; merging the author and triage open-ticket lists into one helper.

## Scope fence
- chupa/author.py
- tests/regress_author_open_tickets_deleted.py

## Acceptance criteria
1. `uv run python tests/regress_author_open_tickets_deleted.py` prints `{"regression_result": "pass"}` and exits 0 on the branch head; it prints `defect`, not `pass`, when `gone` raises `FileNotFoundError`, and `error`, not `pass`, when `live` is missing from the result.
2. `./dev.py test` exits 0.

## Verification
```
uv run python tests/regress_author_open_tickets_deleted.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `_open_tickets` catches `FileNotFoundError` or any broader exception instead of checking the path;
- a ticket file present on disk and in the index is dropped from the list;
- the reproducer prints `pass` on the merge base.

## Time budget
- expected: 15m
- stuck: 45m

## Regression
```
uv run python tests/regress_author_open_tickets_deleted.py
```
- carries: tests/regress_author_open_tickets_deleted.py
