---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- chupa-ruff-reclean
- chupa-ruff-reclean-tests-a-l

## Context
- pyproject.toml

## Goal / Why
Finishes the ruff re-cleanup that `chupa-ruff-reclean` and `chupa-ruff-reclean-tests-a-l` start, and leaves the whole repo passing `uv run ruff check .` and `uv run ruff format --check .`. `chupa-test-gates` adds those whole-repo checks to chupa's own Check and cannot pass until they hold.

## Scope in / Scope out
- In: run `uv run ruff check --fix` and `uv run ruff format` on `tests/`, then fix the remaining findings by hand without changing what any test asserts. Known ones in `tests/integration/`: E501 (line over 200) in `test_requisition.py`, `test_requisition_gate.py`, `test_rework.py`, `test_stats.py`, `test_status.py`, `test_triage.py`; E731 (lambda assigned to a name) in `test_watch.py`, rewritten as a `def`. Files `chupa-ruff-reclean-tests-a-l` already cleaned need no change.
- Out: `chupa/`, `eval/`, `pyproject.toml` and its ruff settings; every `.md` file; any change to what a test checks.

## Scope fence
- tests

## Acceptance criteria
1. `uv run ruff check .` exits 0.
2. `uv run ruff format --check .` exits 0.
3. `./dev.py test` exits 0.

## Verification
```
uv run ruff check .
uv run ruff format --check .
./dev.py test
```

## Definition of rejected
A finding is silenced with `noqa` or a new ignore instead of fixed; a file outside `tests/` changes; a test's assertions or inputs change.

## Time budget
- expected: 25m
- stuck: 75m
