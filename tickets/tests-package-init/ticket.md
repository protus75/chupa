---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- none

## Context
- pyproject.toml
- docs/how-chupa-works.md
- tests/integration/test_testreport.py

## Goal / Why
`tests/`, `tests/unit/` and `tests/integration/` have no `__init__.py`, so pytest's default import mode names each test module by its file name alone, and two test files with the same name in different directories fail collection with "import file mismatch". `results-schema-2-reader` attempt 2 (2026-11-08) hit this: its mandated `tests/unit/test_testreport.py` collided with `tests/integration/test_testreport.py`, and `./dev.py test` failed. The unit coverage gate keeps pushing tickets to add unit tests, and those tests take the name of the matching integration test, so the collision will recur. After this change pytest names each module by its package path (`tests.unit.test_x`, `tests.integration.test_x`), so same-named files can coexist. Existing `from tests.integration.<module> import ...` imports resolve to the same modules as before.

## Scope in / Scope out
- In: add empty `tests/__init__.py`, `tests/unit/__init__.py` and `tests/integration/__init__.py`.
- In: `docs/how-chupa-works.md` section 2.2 says a unit test file may share its name with an integration test file.
- Out: pytest import mode or any other `pyproject.toml` setting, renaming existing test files, and any engine or review check for test file names.

## Scope fence
- tests/__init__.py
- tests/unit/__init__.py
- tests/integration/__init__.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test` exits 0 with the three `__init__.py` files present and empty.
2. `./dev.py test tests/unit` and `./dev.py test tests/integration` each exit 0.

## Verification
```
./dev.py test tests/unit
./dev.py test tests/integration
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- an `__init__.py` it adds has content;
- it changes `pyproject.toml` or renames or edits an existing test file;
- `./dev.py test` collects fewer tests than on the base commit.

## Time budget
- expected: 10m
- stuck: 30m
