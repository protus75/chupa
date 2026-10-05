---
state: confirmed
source: human
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
---

## Depends on
none

## Context
- tests/test_terminal.py
- tests/test_stages.py

## Goal / Why
tests/test_terminal.py imports the shared test `CONFIG` from tests.test_stages instead of string-splitting that module's source.

Splitting another test file's source on `CONFIG = """` breaks silently the moment test_stages.py reformats that literal; the module already imports its other fixtures from tests.test_stages, so the config should arrive the same way.

## Scope in / Scope out
- In: the `repo` fixture in tests/test_terminal.py writes `config.yaml` from an imported `CONFIG`.
- Out: any change to tests/test_stages.py, to engine code, or to what the terminal tests assert.

## Scope fence
- tests/test_terminal.py

## Acceptance criteria
1. `tests.test_terminal.CONFIG` is the same object as `tests.test_stages.CONFIG` (checked by the `python -c` command in `## Verification`).
2. tests/test_terminal.py no longer reads test_stages.py's source text (no `read_text().split` on it; checked by the same `python -c` command).
3. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "import pathlib, tests.test_stages as s, tests.test_terminal as t; assert t.CONFIG is s.CONFIG; assert 'test_stages.py' not in pathlib.Path('tests/test_terminal.py').read_text()"
uv run pytest -q
```

## Definition of rejected
The diff touches any file other than tests/test_terminal.py, changes a test's assertions, or leaves a source-text split of test_stages.py in place.

## Time budget
- expected: 10m
- stuck: 30m
