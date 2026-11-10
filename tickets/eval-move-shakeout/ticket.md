---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- eval-drop-shakeout-report

## Context
- eval/shakeout/run.py
- eval/shakeout/bench.py
- tests/integration/test_shakeout.py
- tests/integration/test_vocabularies.py::_engine_signal_names

## Goal / Why
`eval/shakeout/` holds the shakeout scenarios: fake-model scripts that drive a real drain and record what the engine did. Once `eval-drop-shakeout-report` removes the report command, only `tests/integration/test_shakeout.py` uses this code. It is test code, but it lives outside `tests/`. That hides it from anyone looking at the test suite and from reviewers judging which tests a change can break.

After this change the scenarios live under `tests/harness/shakeout/`. They are imported as `tests.harness.shakeout.*` and run unchanged. Nothing remains under `eval/shakeout/`.

Simplest approach: a move with import-path edits only. Rejected: merging the scenario modules into the test file, which would mix 1,000 lines of scenario scripts into the suite file.

## Scope in / Scope out
- In: move each of `eval/shakeout/bench.py`, `run.py`, `stages.py`, `driver.py`, `runner.py`, `drain.py`, `recovery.py`, `merge.py` and `providers.py` to `tests/harness/shakeout/` under the same name, content unchanged except import paths.
- In: change every `eval.shakeout.` import in the moved files to `tests.harness.shakeout.`, including the dynamic `importlib.import_module(f"eval.shakeout.{group}")` in `run.py`.
- In: add empty `tests/harness/__init__.py` and `tests/harness/shakeout/__init__.py`. Module names there do not start with `test_`, so pytest does not collect them as tests.
- In: `tests/integration/test_shakeout.py`: import from `tests.harness.shakeout.*`, and change the `"eval.shakeout.first"` and `"eval.shakeout.second"` keys in `test_produce_requires_complete_matching_prior_and_returns_cumulative` to `"tests.harness.shakeout.first"` and `"tests.harness.shakeout.second"`.
- In: `tests/integration/test_vocabularies.py`: `_engine_signal_names` scans `("chupa", "eval", "tests/harness")` instead of `("chupa", "eval")`, so signal names emitted by moved harness code stay in the closed-vocabulary check.
- Unaffected: no file outside the fence imports `eval.shakeout`. A grep of `chupa/`, `eval/`, `tests/`, `dev.py`, `config.yaml`, `pyproject.toml` and `test-gate.toml` finds only the moved modules, `test_shakeout.py` and ticket history. `pyproject.toml`'s `tests/*` ruff ignores and `testpaths = ["tests"]` already cover the new location. `config.yaml`'s `--cov=eval` coverage-map command keeps measuring the eval code that remains.
- Out: the daemon soak, reliability battery, host loop and diagnose harnesses (tickets `eval-move-soak-battery-host-loop` and `eval-move-diagnose`); `eval/harness.py` and `eval/fixtures/`; behavior changes to any scenario; ticket history under `tickets/`.

## Scope fence
- eval/shakeout
- tests/harness
- tests/integration/test_shakeout.py
- tests/integration/test_vocabularies.py

## Acceptance criteria
1. `uv run python -c "from pathlib import Path; assert not [p for p in Path('eval/shakeout').rglob('*.py')]; import tests.harness.shakeout.run as r; r.produce; r.GROUPS"` exits 0, ruling out a copy left behind or a moved package that does not import.
2. `./dev.py test tests/integration/test_shakeout.py` exits 0 with every scenario test still collected. It still runs `test_produce_stages_returns_six_green_entries` and `test_planted_secret_member_observes_redacted_run_record`, ruling out a dynamic group import still pointing at `eval.shakeout`.
3. `./dev.py test tests/integration/test_vocabularies.py` exits 0.
4. `./dev.py test` exits 0.

## Verification
```
uv run python -c "from pathlib import Path; assert not [p for p in Path('eval/shakeout').rglob('*.py')]; import tests.harness.shakeout.run as r; r.produce; r.GROUPS"
./dev.py test tests/integration/test_shakeout.py
./dev.py test tests/integration/test_vocabularies.py
./dev.py test
```

## Definition of rejected
- Any `.py` file remains under `eval/shakeout/`.
- A scenario's behavior or member list changes.
- A shakeout test is deleted.
- Any file outside the fence changes.

## Time budget
- expected: 25m
- stuck: 50m
