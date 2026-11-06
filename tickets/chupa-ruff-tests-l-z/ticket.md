---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- chupa-ruff-tests-a-k

## Context
- pyproject.toml
- tests/test_serve.py
- tests/test_testreport.py

## Goal / Why
`chupa-ruff-src` committed the ruff configuration and cleaned the non-test tree, and `chupa-ruff-tests-a-k` cleaned `tests/test_[a-k]*.py`. This ticket cleans the rest of `tests/`, so that `uv run ruff check .` and `uv run ruff format --check .` both exit 0 for the whole repo, which chupa's later lint checks need.

## Scope in / Scope out
- In: fix by hand every ruff finding and `ruff format` change in files under `tests/` that do not match `tests/test_[a-k]*.py` (that is `tests/test_[l-z]*.py`, `tests/regress_*.py`, `tests/waiting.py`). Known ones (line numbers as of `e99990cb`):
  - E731 in `tests/test_serve.py:1723`: rewrite the lambda as `def`.
  - `ruff format` changes in `tests/test_testreport.py`.
  - Any finding a later merge added in these files.
- In: if a later merge added a finding anywhere else in the Python tree, fix it by hand here so the whole-repo commands pass.
- Out: `pyproject.toml` and the ruff configuration; any other lint rule or behavior change; every `.md` file; the text-matching tests (ticket `source-graph-ast`).

## Scope fence
- tests
- chupa
- eval
- dev.py
- watch.py

## Acceptance criteria
1. `uv run ruff check .` exits 0.
2. `uv run ruff format --check .` exits 0. `CHUPA_PLAN.md` is unchanged.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

## Definition of rejected
The ruff configuration changes; a finding is silenced by a blanket ignore or noqa instead of fixed; a markdown file changes; behavior changes.

## Time budget
- expected: 30m
- stuck: 90m