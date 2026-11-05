---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/config.py
- tests/test_host_mechanical.py
- docs/host-contract.md
- tests/test_host_contract.py

## On-demand
- chupa/stages.py
- docs/how-chupa-works.md

## Goal / Why
`check_autofix` (`chupa/stages.py`) appends every changed file outside `tickets/` to each `review.autofix` argv. Formatters parse every file they are given as their own language. With ruff 0.17.3, `ruff format cfg.yaml gi` (copies of this repo's `config.yaml` and `.gitignore`) exits 2 with "Failed to parse". `ruff check --fix` can delete lines from non-Python files. So once a host declares ruff autofix, every ticket that changes a YAML, lock, JSON or ignore file fails Check, or has that file silently rewritten. No host declares autofix yet, so nothing is broken today.

After this change each autofix entry must declare `files`, an allowlist of `fnmatch` patterns. Only changed files matching one of the patterns are appended. An entry with no matching files is skipped.

## Scope in / Scope out
- In: `chupa/config.py`: `AutofixCommand.files`, a required nonempty `list[str]`. The allowlist is required, so an entry cannot run on unknown file types.
- In: `chupa/stages.py` `check_autofix`:
  - each entry gets only the existing changed files outside `tickets/` for which `fnmatch.fnmatch(path, pattern)` holds for some pattern in `entry.files` (`*` also matches `/`, so `*.py` matches `chupa/x.py`);
  - an entry with no matching files is not run;
  - the byte snapshot, the commit set and the restore-on-failure cover the union of files selected for any entry, computed before the first entry runs.
- In: `docs/host-contract.md`:
  - the `config-fields` `AutofixCommand` row requires `files`;
  - the `host-example` autofix entry gains `files: ["*.py"]`;
  - the autofix paragraph states the allowlist and the skip.
- In: `docs/how-chupa-works.md` section 4.3: autofix passes only files matching each entry's `files`.
- In: `tests/test_host_mechanical.py`: update existing autofix tests for the required field, and add the tests below.
- Out: mechanical checks; any tool presets; a denylist; detecting file types by content.

## Scope fence
- chupa/config.py
- chupa/stages.py
- tests/test_host_mechanical.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. Selection. A branch changes `a.py`, `config.yaml` and `.gitignore`. An entry with `files: ["*.py"]` receives exactly `a.py`, and an entry with `files: ["*.yaml"]` receives exactly `config.yaml`. A test fails if a non-matching file is appended. Checked by `uv run pytest tests/test_host_mechanical.py`.
2. Skip. On a branch changing only `config.yaml`, an entry with `files: ["*.py"]` makes no command call and Check passes. A test fails if the entry runs with no files. Checked by `uv run pytest tests/test_host_mechanical.py`.
3. Fail closed. An autofix entry without `files`, or with `files: []`, is refused at config load naming the key. Checked by `uv run pytest tests/test_host_mechanical.py tests/test_host_contract.py`.
4. The existing autofix behaviors (commit of changed bytes only, restore on failure, no run for `already_satisfied`) still pass. Checked by `uv run pytest tests/test_host_mechanical.py`.
5. Union coverage, checked by `uv run pytest tests/test_host_mechanical.py`. Two entries are used: `files: ["*.py"]` rewriting `a.py`, then `files: ["*.yaml"]` rewriting `config.yaml`.
   - When both succeed, the single `chupa(<stem>): autofix` commit contains both files.
   - When the `*.yaml` entry exits nonzero after the `*.py` entry rewrote `a.py`, both files match the branch head and no autofix commit exists.

   A test fails if only one entry's files are snapshotted, committed or restored.
6. `docs/host-contract.md` stays in lockstep with `chupa/config.py`, checked by `uv run pytest tests/test_host_contract.py`.
7. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_host_mechanical.py tests/test_host_contract.py
uv run pytest -q
```

## Definition of rejected
`files` is optional or has a default; a denylist is used; any file not matching an entry's patterns reaches that entry's argv; the engine names a tool.

## Time budget
- expected: 30m
- stuck: 90m
