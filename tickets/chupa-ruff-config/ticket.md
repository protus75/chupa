---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- pyproject.toml
- chupa/serve.py
- eval/daemon_soak.py
- eval/host_loop.py
- eval/shakeout/runner.py
- eval/shakeout/stages.py

## Goal / Why
Commit `e99990cb` bulk-applied ruff lint fixes and formatting from the command line with explicit flags, but the repo has no ruff configuration. So `uv run ruff check` and `uv run ruff format` give different results from that run, and ruff is not a dev dependency. Chupa's autofix and lint checks (a later ticket) need both. After this change `pyproject.toml` holds the same settings, ruff is a pinned dev dependency, and the 14 findings ruff could not fix itself (beyond the two long-line files it now ignores) are fixed. `uv run ruff check .` and `uv run ruff format --check .` then both exit 0.

## Scope in / Scope out
- In: `pyproject.toml`.
  - Add `ruff==0.17.3` to the `dev` dependency group, updating `uv.lock` with `uv lock`.
  - Add `[tool.ruff]` with `line-length = 200` and `extend-exclude = ["*.md"]`. Markdown is excluded because ruff 0.17 formats code blocks in markdown, and `CHUPA_PLAN.md` is frozen.
  - Add `[tool.ruff.lint]` with `select = ["E", "F", "I"]`.
  - Add `[tool.ruff.lint.per-file-ignores]`, each with a short comment giving the reason:
    - `"tests/*" = ["F401", "F811"]`: tests import shared fixtures by name, and removing those imports breaks pytest;
    - `"chupa/__main__.py" = ["I001"]`: tests match its import lines as text;
    - `"chupa/hostfiles.py" = ["E501"]` and `"tests/test_hostfiles.py" = ["E501"]`: the core template and its expected bytes are long by design.
- In: fix the remaining findings by hand:
  - E731 (lambda assigned to a name) in `chupa/serve.py:417`, `eval/daemon_soak.py:469`, `eval/host_loop.py:317`, `eval/shakeout/runner.py:95`, `eval/shakeout/stages.py:104,121,138`, `tests/test_host_contract.py:325` and `tests/test_serve.py:1723`: rewrite as `def`.
  - E741 in `tests/test_journal.py:31,142`: rename `l`.
  - F841 in `tests/test_kill_cli_activation.py:820,842`: drop the unused binding and keep the call.
  - E402 in `tests/test_gates.py:316`: move the import to the top, unless the late import is deliberate. In that case add `# noqa: E402` with a comment saying why.

  - Findings that merges after `e99990cb` added: I001 and three E501 in `chupa/stages.py`, and `ruff format` changes in `chupa/stages.py` and `tests/test_testreport.py`.

  Line numbers are as of `e99990cb`; find them with `uv run ruff check .`.
- Out: any other lint rule or behavior change; `CHUPA_PLAN.md` and every `.md` file; chupa's `config.yaml` checks (a later ticket); the text-matching tests (ticket `source-graph-ast`).

## Scope fence
- pyproject.toml
- uv.lock
- chupa/serve.py
- eval/daemon_soak.py
- eval/host_loop.py
- eval/shakeout/runner.py
- eval/shakeout/stages.py
- tests/test_host_contract.py
- tests/test_serve.py
- tests/test_journal.py
- tests/test_kill_cli_activation.py
- tests/test_gates.py
- chupa/stages.py
- tests/test_testreport.py

## Acceptance criteria
1. `uv run ruff check .` exits 0 with the committed configuration. It fails if a finding remains or a needed ignore is missing.
2. `uv run ruff format --check .` exits 0, and no file outside the fence is reformatted. `CHUPA_PLAN.md` is unchanged.
3. `pyproject.toml` pins `ruff==0.17.3` in the `dev` group, and `uv.lock` agrees: `uv lock --check` exits 0.
4. `uv run pytest -q` exits 0.

## Verification
```
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

## Definition of rejected
A rule other than E, F or I is selected; a finding is silenced by a blanket ignore instead of fixed (beyond the five listed per-file ignores and a justified E402 noqa); a markdown file changes; behavior changes.

## Time budget
- expected: 30m
- stuck: 90m
