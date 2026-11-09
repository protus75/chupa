---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- config.yaml
- test-gate.toml
- chupa/covgate.py
- chupa/testguard.py
- pyproject.toml

## Goal / Why
The `unit` check in `config.yaml` is a hard, always-on gate: `chupa covgate -- pytest tests/unit ... --cov=chupa --cov-branch --cov-context=test -n auto`. `test-gate.toml` holds per-file floors (`chupa/covgate.py` = 23). In chupa-test-gates attempt 2, `chupa/covgate.py` measured 19% on one run and 23% on the next, on unchanged code. A floor set from one run can therefore fail a later unchanged run, so the hard gate fails tickets at random. One suspect is `-p chupa.testguard`, which imports `chupa.covgate` as a plugin, so import-time lines may be recorded or lost depending on whether coverage tracing has started in that process (controller or xdist worker). After this change the per-file coverage of the `unit` command is the same on repeated runs of unchanged code, for every file.

## Scope in / Scope out
- In: reproduce the variance, name the cause in the run record, and fix it in coverage or pytest configuration in `pyproject.toml` only (`[tool.coverage.*]` or `[tool.pytest.ini_options]`, for example how xdist workers and early-imported plugin modules are measured, or plugin load order such as loading `pytest_cov` before `chupa.testguard`). If the cause cannot be fixed in `pyproject.toml`, reply `premise_failed` and name the file that would need to change. The `unit` argv in `config.yaml` stays exactly as it is, so the `## Verification` commands run the same command the gate runs. `chupa/covgate.py` and `chupa/testguard.py` gain no new statements and no new tests.
- In: if the stable measured value of a file is above its floor in `test-gate.toml`, the floor may be raised to it; never lowered.
- Out: lowering any floor; changing `config.yaml`; changing gate grammar or evaluation; the `integration` check; adding tests. The tests that exercise `chupa/covgate.py` and `chupa/testguard.py` (`tests/integration/test_covgate.py`, `tests/integration/test_host_contract.py`, `tests/integration/test_testguard.py`) use in-memory or temp-dir data and pin parse/evaluate behavior this change does not touch, so they stay unfenced.

## Scope fence
- pyproject.toml
- test-gate.toml
- docs/how-chupa-works.md

## Acceptance criteria
1. Two consecutive runs of the `unit` command exit 0, so a floor does not flip between runs. Checked by the two `uv run python -m chupa covgate` commands in `## Verification`; a single passing run does not satisfy this.
2. The two runs report the same `covered_lines` for every file, not only `chupa/covgate.py`. Checked by `assert f('coverage.json')==f('.chupa/first-coverage.json')`, which fails if any file's count differs between runs.
3. `config.yaml` is unchanged, so the `unit` argv matches the one pinned in `## Verification`. Checked by `git diff --exit-code config.yaml`.
4. No floor in `test-gate.toml` is lower than at the base commit. Checked at Review.
5. The set of files in `coverage.json` matches the base commit's measured set: no chupa file or line is newly excluded from measurement. Checked at Review against the `pyproject.toml` diff.

## Verification
```
uv run python -m chupa covgate -- python -m pytest tests/unit -p chupa.testguard -p chupa.testreport --chupa-results .chupa/results/unit.json --cov=chupa --cov-branch --cov-context=test --cov-report=json:coverage.json -n auto
uv run python -c "import shutil; shutil.copy('coverage.json', '.chupa/first-coverage.json')"
uv run python -m chupa covgate -- python -m pytest tests/unit -p chupa.testguard -p chupa.testreport --chupa-results .chupa/results/unit.json --cov=chupa --cov-branch --cov-context=test --cov-report=json:coverage.json -n auto
uv run python -c "import json; f=lambda p:{k:v['summary']['covered_lines'] for k,v in json.load(open(p))['files'].items()}; assert f('coverage.json')==f('.chupa/first-coverage.json')"
git diff --exit-code config.yaml
./dev.py test
```

## Definition of rejected
A floor is lowered; `config.yaml` is edited; a chupa file or line is newly excluded from measurement (`omit`, `exclude_lines`, `exclude_also`, or a narrowed `source`); the variance is hidden by a retry or rerun; the cause is not named in the run record; `covered_lines` for any file still differs between two runs.

## Time budget
- expected: 45m
- stuck: 120m
