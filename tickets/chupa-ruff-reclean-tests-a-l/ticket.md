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

## Goal / Why
`chupa-ruff-tests-a-k` and `chupa-ruff-tests-l-z` left `tests/` ruff-clean on 2026-11-06. Later merges reintroduced lint findings and format drift, because nothing checks ruff on merge yet. `chupa-test-gates` adds that check but cannot pass while the repo is dirty. This ticket cleans the first half of the dirty test files; `chupa-ruff-reclean-tests-m-z` cleans the rest, so each diff stays under the diff budget.

## Scope in / Scope out
- In: run `uv run ruff check --fix` and `uv run ruff format` on the fenced files, then fix the remaining findings by hand without changing what any test asserts. Known ones: E501 (line over 200) in `tests/integration/test_ask.py`. Find all of them with `uv run ruff check` on the fenced files.
- Out: every other file under `tests/`; `chupa/`, `eval/`, `pyproject.toml` and its ruff settings; every `.md` file; any change to what a test checks.

## Scope fence
- tests/approval.py
- tests/regress_graph_lanes.py
- tests/regress_serve_reoffer_rule.py
- tests/regress_shared_hold_rule.py
- tests/regress_vscode_task_identity.py
- tests/integration/test_ask.py
- tests/integration/test_box.py
- tests/integration/test_cli.py
- tests/integration/test_config.py
- tests/integration/test_control_cli.py
- tests/integration/test_covmap.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_daemon_soak_runner.py
- tests/integration/test_dev.py
- tests/integration/test_drain.py
- tests/integration/test_hostfiles.py
- tests/integration/test_kill_cli_activation.py
- tests/integration/test_ladder.py

## Acceptance criteria
1. `uv run ruff check` on every fenced file exits 0 (first Verification command).
2. `uv run ruff format --check` on every fenced file exits 0 (second Verification command).
3. `./dev.py test` exits 0.

## Verification
```
uv run ruff check tests/approval.py tests/regress_graph_lanes.py tests/regress_serve_reoffer_rule.py tests/regress_shared_hold_rule.py tests/regress_vscode_task_identity.py tests/integration/test_ask.py tests/integration/test_box.py tests/integration/test_cli.py tests/integration/test_config.py tests/integration/test_control_cli.py tests/integration/test_covmap.py tests/integration/test_daemon_composition.py tests/integration/test_daemon_soak_runner.py tests/integration/test_dev.py tests/integration/test_drain.py tests/integration/test_hostfiles.py tests/integration/test_kill_cli_activation.py tests/integration/test_ladder.py
uv run ruff format --check tests/approval.py tests/regress_graph_lanes.py tests/regress_serve_reoffer_rule.py tests/regress_shared_hold_rule.py tests/regress_vscode_task_identity.py tests/integration/test_ask.py tests/integration/test_box.py tests/integration/test_cli.py tests/integration/test_config.py tests/integration/test_control_cli.py tests/integration/test_covmap.py tests/integration/test_daemon_composition.py tests/integration/test_daemon_soak_runner.py tests/integration/test_dev.py tests/integration/test_drain.py tests/integration/test_hostfiles.py tests/integration/test_kill_cli_activation.py tests/integration/test_ladder.py
./dev.py test
```

## Definition of rejected
A finding is silenced with `noqa` or a new ignore instead of fixed; a file outside the fence changes; a test's assertions or inputs change.

## Time budget
- expected: 25m
- stuck: 75m
