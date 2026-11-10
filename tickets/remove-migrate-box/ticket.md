---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- dev.py
- tests/integration/test_dev.py::test_migrate_box_forwards
- tests/integration/test_cli.py::test_migrate_box_lock_and_repeat
- tests/integration/test_box.py::test_migrate_box_preserves_other_messages
- tests/unit/test_host_running.py
- chupa/docs/host-running.md

## On-demand
- chupa/__main__.py
- docs/how-chupa-works.md

## Goal / Why
`migrate-box` was a one-shot migration added by box-declined-verdict to rewrite stored box resolutions from `decision` to `declined`. The operator ran it on 2026-11-07, and no file under `.chupa/state/box/` still has `"kind": "decision"` (checked 2026-11-10: 0 of 390). The command now always reports `migrate-box: 0 migrated`. After this change the verb, its `./dev.py` forwarder, its tests, and its doc rows are gone, so the command surface lists only verbs that do something.

## Scope in / Scope out
- In: `chupa/__main__.py`: delete the `migrate-box` subparser and the `if args.verb == "migrate-box":` branch with its `migrate_box` coroutine. Delete any import left unused by that deletion.
- In: `dev.py`: delete the `migrate-box` docstring line and its `sub.add_parser("migrate-box", ...)` line.
- In: tests: delete `test_migrate_box_lock_and_repeat` (test_cli.py), `test_migrate_box_preserves_other_messages` (test_box.py), and `test_migrate_box_forwards` (test_dev.py). Delete any import left unused in those files.
- In: `chupa/docs/host-running.md`: delete the `migrate-box` verb-table row, and drop `migrate-box` from the "Stop serve before ..." list, so `tests/unit/test_host_running.py::test_verb_table_matches_parser` passes.
- In: `docs/how-chupa-works.md`: delete the `migrate-box` rows from the section 2.1 verb table and the section 2.2 `./dev.py` table.
- Out:
  - the `declined` verdict, `Resolution`, `Verdict`, `DecisionRecord`, and every other box model;
  - every file under `tickets/` (past ticket, review, retro, and decision records keep their history);
  - `CHUPA_PLAN.md`.

## Scope fence
- chupa/__main__.py
- dev.py
- chupa/docs/host-running.md
- docs/how-chupa-works.md
- tests/integration/test_cli.py
- tests/integration/test_box.py
- tests/integration/test_dev.py

## Acceptance criteria
1. `git grep -n -e migrate-box -e migrate_box -- chupa dev.py docs tests` prints nothing.
2. `./dev.py test tests/unit/test_host_running.py tests/integration/test_cli.py tests/integration/test_box.py tests/integration/test_dev.py` exits 0: the host-running verb table matches the parser with no `migrate-box` row and no `migrate-box` verb.
3. `uv run python -m chupa migrate-box` exits 2 with argparse's `invalid choice` error, not 0.
4. The branch changes no file under `tickets/`.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/unit/test_host_running.py tests/integration/test_cli.py tests/integration/test_box.py tests/integration/test_dev.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any box model, verdict value, or reader changes;
- `migrate-box` survives as a hidden, deprecated, or no-op verb instead of being deleted;
- any file under `tickets/` changes.

## Time budget
- expected: 15m
- stuck: 45m
