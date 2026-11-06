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
- chupa/stages.py
- eval/daemon_soak.py
- eval/host_loop.py
- eval/shakeout/runner.py
- eval/shakeout/stages.py

## Goal / Why
Commit `e99990cb` bulk-applied ruff lint fixes and formatting from the command line with explicit flags, but the repo has no ruff configuration, so `uv run ruff check` and `uv run ruff format` give different results from that run, and ruff is not a dev dependency. Chupa's autofix and lint checks (a later ticket) need both. This ticket adds the configuration and the pinned dependency, and makes the non-test Python tree (`chupa/`, `eval/`, `dev.py`, `watch.py`) clean. The test tree is cleaned by the follow-up tickets `chupa-ruff-tests-a-k` and `chupa-ruff-tests-l-z`; together they keep each diff under the diff budget.

## Scope in / Scope out
- In: `pyproject.toml`.
  - Add `ruff==0.17.3` to the `dev` dependency group, updating `uv.lock` with `uv lock`.
  - Add `[tool.ruff]` with `line-length = 200` and `extend-exclude = ["*.md"]`. Markdown is excluded because ruff 0.17 formats code blocks in markdown, and `CHUPA_PLAN.md` is frozen.
  - Add `[tool.ruff.lint]` with `select = ["E", "F", "I"]`.
  - Add `[tool.ruff.lint.per-file-ignores]`, each with a short comment giving the reason:
    - `"tests/*" = ["F401", "F811"]`: tests import shared fixtures by name, and removing those imports breaks pytest;
    - `"chupa/__main__.py" = ["I001"]`: tests match its import lines as text;
    - `"chupa/hostfiles.py" = ["E501"]` and `"tests/test_hostfiles.py" = ["E501"]`: the core template and its expected bytes are long by design.
- In: fix by hand every finding and format change under `chupa/` and `eval/`, and in `dev.py` and `watch.py`. Known ones:
  - E731 (lambda assigned to a name) in `chupa/serve.py:417`, `eval/daemon_soak.py:469`, `eval/host_loop.py:317`, `eval/shakeout/runner.py:95`, `eval/shakeout/stages.py:104,121,138`: rewrite as `def`.
  - I001 and three E501 in `chupa/stages.py`, and `ruff format` changes in `chupa/stages.py`.
  - Any finding a later merge added in these paths.
  Line numbers are as of `e99990cb`; find them with `uv run ruff check chupa eval dev.py watch.py`.
- Out: every file under `tests/` (tickets `chupa-ruff-tests-a-k` and `chupa-ruff-tests-l-z`); any other lint rule or behavior change; `CHUPA_PLAN.md` and every `.md` file; chupa's `config.yaml` checks (a later ticket); the text-matching tests (ticket `source-graph-ast`).

## Scope fence
- pyproject.toml
- uv.lock
- chupa
- eval
- dev.py
- watch.py

## Acceptance criteria
1. `uv run ruff check chupa eval dev.py watch.py` exits 0 with the committed configuration.
2. `uv run ruff format --check chupa eval dev.py watch.py` exits 0. No file outside the fence changes; `CHUPA_PLAN.md` is unchanged.
3. `pyproject.toml` pins `ruff==0.17.3` in the `dev` group, and `uv.lock` agrees: `uv lock --check` exits 0.
4. `uv run pytest -q` exits 0.

## Verification
```
uv lock --check
uv run ruff check chupa eval dev.py watch.py
uv run ruff format --check chupa eval dev.py watch.py
uv run pytest -q
```

## Definition of rejected
A rule other than E, F or I is selected; a finding is silenced by a blanket ignore instead of fixed (beyond the five listed per-file ignores); a file under `tests/` or a markdown file changes; behavior changes.

## Time budget
- expected: 30m
- stuck: 90m