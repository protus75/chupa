---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- chupa-ruff-src

## Context
- pyproject.toml
- tests/test_host_contract.py
- tests/test_journal.py
- tests/test_kill_cli_activation.py
- tests/test_gates.py

## Goal / Why
`chupa-ruff-src` committed the ruff configuration and cleaned the non-test tree. This ticket cleans the first half of the test tree: every file matching `tests/test_[a-k]*.py`. The rest of `tests/` is cleaned by `chupa-ruff-tests-l-z`. The split keeps each diff under the diff budget.

## Scope in / Scope out
- In: fix by hand every ruff finding and `ruff format` change in files matching `tests/test_[a-k]*.py`. Known ones (line numbers as of `e99990cb`):
  - E731 in `tests/test_host_contract.py:325`: rewrite the lambda as `def`.
  - E741 in `tests/test_journal.py:31,142`: rename `l`.
  - F841 in `tests/test_kill_cli_activation.py:820,842`: drop the unused binding and keep the call.
  - E402 in `tests/test_gates.py:316`: move the import to the top, unless the late import is deliberate. In that case add `# noqa: E402` with a comment saying why.
  - Any finding a later merge added in these files.
- Out: `pyproject.toml` and the ruff configuration; any other `tests/` file (`regress_*.py`, `waiting.py`, `test_[l-z]*.py`); any other lint rule or behavior change; every `.md` file; the text-matching tests (ticket `source-graph-ast`).

## Scope fence
- tests

## Acceptance criteria
1. `uv run ruff check tests --extend-exclude 'tests/test_[l-z]*.py,tests/regress_*.py,tests/waiting.py'` exits 0.
2. `uv run ruff format --check tests --extend-exclude 'tests/test_[l-z]*.py,tests/regress_*.py,tests/waiting.py'` exits 0.
3. Only files matching `tests/test_[a-k]*.py` change.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run ruff check tests --extend-exclude 'tests/test_[l-z]*.py,tests/regress_*.py,tests/waiting.py'
uv run ruff format --check tests --extend-exclude 'tests/test_[l-z]*.py,tests/regress_*.py,tests/waiting.py'
uv run pytest -q
```

## Definition of rejected
The ruff configuration changes; a finding is silenced by a blanket ignore or noqa instead of fixed (beyond a justified E402 noqa); a file outside `tests/test_[a-k]*.py` changes; test behavior changes.

## Time budget
- expected: 30m
- stuck: 90m