---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- none

## Context
- pyproject.toml

## Goal / Why
The PyPI page for chupa (https://pypi.org/project/chupa/) has no "Project links" sidebar entry for the source repository, because `pyproject.toml` has no `[project.urls]` table. A reader on PyPI cannot find https://github.com/protus75/chupa from package metadata. After this change, the built package's metadata names the repository, and PyPI shows it under Project links on the next publish.

## Scope in / Scope out
- In: add a `[project.urls]` table to `pyproject.toml`, directly after the `[project]` table's keys and before `[project.scripts]`, holding exactly one key: `Repository = "https://github.com/protus75/chupa"`.
- Out:
  - the `version`, `readme`, and every other existing key in `pyproject.toml`;
  - `uv.lock`, `README.md`, docs, and code;
  - publishing to PyPI.

## Scope fence
- pyproject.toml

## Acceptance criteria
1. `uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['urls'])"` prints `{'Repository': 'https://github.com/protus75/chupa'}`, not a `KeyError` and not a dict with other keys.
2. `git diff main -- pyproject.toml` on the branch adds only the `[project.urls]` header and the `Repository` line, plus at most one blank line.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any file other than `pyproject.toml` changes;
- an existing `pyproject.toml` key changes, including `version`;
- `[project.urls]` holds a key other than `Repository`.

## Time budget
- expected: 5m
- stuck: 30m
