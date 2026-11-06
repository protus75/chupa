---
state: confirmed
source: human
priority: P3
kind: chore
---

## Depends on
- specs-move

## Context
- tests/test_specs.py

## On-demand
- chupa/specs.py

## Goal / Why
After `specs-move`, `chupa/specs.py` (the spec loader module) sits beside `chupa/specs/` (the spec files). Python imports the module over the plain directory, so it works, but two things named `chupa.specs` side by side confuse readers and packaging (2026-11-06).

After this change `chupa/specs/` is one package: the loader code is `chupa/specs/__init__.py` and the `.md` specs sit beside it. `from chupa.specs import ...` and `from chupa import specs` keep working unchanged, so no importer moves.

## Scope in / Scope out
- In: `git mv chupa/specs.py chupa/specs/__init__.py`. Its code is unchanged.
- In: `tests/test_specs.py` `test_engine_source_never_spells_the_raw_delimiter` reads `chupa/specs/__init__.py`.
- Out:
  - importers of `chupa.specs` (the import path is unchanged);
  - spec `.md` files; `pyproject.toml` (`pypi-package`).

## Scope fence
- chupa/specs.py
- chupa/specs/__init__.py
- tests/test_specs.py

## Acceptance criteria
1. `chupa/specs.py` does not exist and `chupa.specs` imports from `chupa/specs/__init__.py`. The first Verification command checks both.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run python -c "from pathlib import Path; import chupa.specs as s; assert not Path('chupa/specs.py').exists() and Path(s.__file__).resolve() == Path('chupa/specs/__init__.py').resolve()"
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- the loader's code changes beyond the move;
- any importer of `chupa.specs` changes.

## Time budget
- expected: 15m
- stuck: 45m
