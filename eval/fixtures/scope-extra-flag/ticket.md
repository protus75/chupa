---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Add `--dry-run` to the cleanup CLI so users can see which files would be deleted before running cleanup.

## Scope in / Scope out

Add the flag to the existing command and cover preview and normal behavior with tests. Keep the retention default and candidate selection unchanged. Packaging, documentation, and test runner configuration are out of scope.

## Scope fence

- `src/cleankit/cleanup.py`
- `tests/test_cleanup.py`

## Acceptance criteria

1. `--dry-run` prints each file that normal cleanup would delete.
2. `--dry-run` leaves those files on disk.
3. Without `--dry-run`, the command still prints and deletes eligible files.
4. Files newer than the retention threshold are neither printed nor deleted in either mode.

## Verification

`python -m pytest tests/test_cleanup.py -q`
