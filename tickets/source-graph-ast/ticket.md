---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- chupa-ruff-config

## Context
- tests/test_daemon_composition.py
- tests/test_mergequeue.py
- pyproject.toml

## Goal / Why
Several reachability tests prove the daemon and merge queue are wired into production by removing one import and checking that reachability breaks. They find that import by exact text: `"from chupa.daemon import DaemonCore, PauseConsumer, daemon_core" in source`. They remove it by replacing each line that starts `from chupa.daemon import` with `pass`. Ruff's import sorting merged that import with another, which broke 8 tests. A wrapped multi-line import would also leave its continuation lines behind and not parse. So `chupa/__main__.py` is exempt from import sorting only to keep these tests passing. After this change both helpers work on the parsed syntax tree: formatting and import order cannot break them, and the exemption is removed.

## Scope in / Scope out
- In: `tests/test_daemon_composition.py` `without_core_import(material)`:
  - Assert with `ast` that `chupa.__main__` has an `ImportFrom` of module `chupa.daemon` whose names include `DaemonCore`, `PauseConsumer` and `daemon_core`.
  - Return the material with every `Import` or `ImportFrom` of `chupa.daemon`, in every module and at any depth, replaced by `ast.Pass`, re-rendered with `ast.unparse`.

  Its callers in `tests/test_daemon_admission.py`, `tests/test_daemon_config.py` and `tests/test_scheduler.py` stay unchanged.
- In: `tests/test_mergequeue.py` `test_merge_queue_is_reachable_from_production`: the same change for `from chupa.mergequeue import MergeQueue` in `chupa.merge`. Assert the `ImportFrom` with `ast`, and remove every `Import`/`ImportFrom` of `chupa.mergequeue` via the syntax tree.
- In: `tests/test_daemon_composition.py`: a test that feeds `without_core_import` a material whose `chupa.__main__` imports `from chupa.daemon import (\n    DaemonCore,\n    PauseConsumer,\n    StartupBoundary,\n    daemon_core,\n)`. The assertion passes and the result has no `chupa.daemon` import left.
- In: `pyproject.toml`: drop the `"chupa/__main__.py" = ["I001"]` per-file ignore and its comment.
- In: `chupa/__main__.py`: imports sorted by `uv run ruff check --fix --select I chupa/__main__.py`, and nothing else changed.
- Out: the `import_closure` walkers (already `ast`-based); any other test; production code beyond import order in `chupa/__main__.py`.

## Scope fence
- tests/test_daemon_composition.py
- tests/test_mergequeue.py
- pyproject.toml
- chupa/__main__.py

## Acceptance criteria
1. With the multi-line merged `chupa.daemon` import, `without_core_import` asserts presence and leaves no `chupa.daemon` import in any module. A test fails if the helper raises on the merged form or leaves an import behind. Checked by `uv run pytest tests/test_daemon_composition.py`.
2. The reachability tests pass with `chupa/__main__.py`'s imports sorted, checked by `uv run pytest tests/test_daemon_composition.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_scheduler.py tests/test_mergequeue.py`.
3. `pyproject.toml` has no per-file ignore for `chupa/__main__.py`, and `uv run ruff check .` exits 0.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_daemon_composition.py tests/test_daemon_admission.py tests/test_daemon_config.py tests/test_scheduler.py tests/test_mergequeue.py
uv run ruff check .
uv run pytest -q
```

## Definition of rejected
A reachability test is weakened or deleted; the helpers still match import text; production behavior changes; the `__main__` ignore stays.

## Time budget
- expected: 30m
- stuck: 90m
