---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/mergequeue.py
- chupa/stages.py
- chupa/config.py
- tests/test_mergequeue.py

## Plan contract
- section 9.4
- section 9.5

## Goal / Why
`MergeQueue._command` (`chupa/mergequeue.py`) records every configured safety or integration command as a `CommandResult`, including when the command comes from a production config snapshot. Today it passes `argv` through unchanged; `snapshot_config` (`chupa/config.py`) stores command argv as tuples while `CommandResult.argv` (`chupa/stages.py`) is `list[str]`, so every snapshot-configured command raises a `ValidationError` (`list_type`), even `['true']` exiting 0, and the merge queue cannot admit anything under a real snapshot.

## Scope in / Scope out
- In: `MergeQueue._command` builds its `CommandResult` with `argv=list(argv)`, so tuple and list argv both record as a list; a regression test in `tests/test_mergequeue.py` runs a configured command taken from real `snapshot_config` output through the queue's command path and asserts a `CommandResult` with list argv and the command's exit code.
- Out: `snapshot_config`, `CommandResult`, and every other caller.

## Scope fence
- chupa/mergequeue.py
- tests/test_mergequeue.py

## Acceptance criteria
1. `uv run pytest -q tests/test_mergequeue.py` exits 0, including the new `test_snapshot_configured_command_records_list_argv`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_mergequeue.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_mergequeue.py -k test_snapshot_configured_command_records_list_argv
```
- carries: tests/test_mergequeue.py

## Definition of rejected
Reject the branch if it changes `snapshot_config` or `CommandResult`, converts argv anywhere but the `CommandResult` boundary in `MergeQueue._command`, or if the regression test passes on the merge base.

## Time budget
- expected: 30m
- stuck: 90m
