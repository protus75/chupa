---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- implement-test-rules
- autofix-file-globs
- covgate-runs-tests
- review-all-findings
- covgate
- testguard
- testreport
- flake-check
- flake-edit-coverage

## Context
- docs/host-contract.md
- tests/test_host_contract.py

## On-demand
- specs/implement.md
- specs/review.md
- tests/test_specs.py
- tests/test_stages.py
- docs/how-chupa-works.md

## Goal / Why
Chupa now has the tools for its test rules: covgate, testguard, testreport, flaky-test classification and autofix. But nothing tells the implementing agent the rules, and a Python host has no single place showing how to switch the tools on.

After this change:
- The Implement prompt states the test rules for every host:
  - unit tests are separate from integration tests;
  - unit tests never touch disk, network or a subprocess;
  - integration tests cover seams with bounded, parallel-safe fixtures;
  - a flaky test is a failure to fix;
  - a coverage threshold or time budget is never lowered unless the ticket requires it.
- The Review prompt flags the one rule no tool enforces: unit-test disk IO and other nondeterminism.
- `docs/host-contract.md` carries a copyable Python host setup that the tests load, so it cannot rot.

## Scope in / Scope out
- In: `specs/implement.md`, inside `## Task` (spec lint allows only the five fixed headings): a tests paragraph stating these rules:
  - Put each test in the suite its kind belongs to, as the host lays them out (for a Python host, `tests/unit/` and `tests/integration/`).
  - A unit test checks one unit with fakes for the clock, filesystem, processes and network. It never reads or writes disk, opens a network connection or starts a process, and it runs in milliseconds.
  - An integration test checks a seam: an API, a command-line interface, a process boundary or real files. It uses fixtures or simulators so it finishes in bounded time and can run in parallel with other tests.
  - A test that can both pass and fail on the same code is broken. Remove the nondeterminism (fake time, fixed ordering, isolated state); never add retries.
  - Never lower a coverage threshold or a test time budget unless an acceptance criterion requires it. When a gate cannot be met, reply `premise_failed` naming it.

  Bump `version` one minor step above its value on main when this runs. The dependencies leave it at "2.1", so this makes it "2.2".
- In: `specs/review.md`, in the `logic` bullet: also snag a unit test that reads or writes disk, opens a network connection, starts a process, or depends on wall-clock time or test order, and a lowered coverage threshold or time budget the ticket does not require. No new finding code. Bump `version` one minor step above its value on main when this runs ("1.3" to "1.4" after `review-all-findings`).
- In: `tests/test_specs.py`: update the implement and review version pins, and assert that the five implement rules and the review addition are in the loaded spec bodies.
- In: `tests/test_stages.py`: update the `spec: implement` and review `spec_version` pins to the bumped versions.
- In: `docs/host-contract.md`: new section `## Python host test setup`.
  - A fenced `yaml python-host` block that a host merges into its `config.yaml`:
    - `review.autofix`: `ruff-fix` `[uv, run, ruff, check, --fix, --exit-zero]` and `ruff-format` `[uv, run, ruff, format]`, each with `files: ["*.py"]`. Ruff parses every file it is given as Python, so it must never receive YAML, lock or ignore files.
    - `review.mechanical`, all `trigger: always`, `severity: hard`:
      - `unit`: `[uv, run, python, -m, chupa, covgate, --, python, -m, pytest, tests/unit, -p, chupa.testguard, -p, chupa.testreport, --chupa-results, .chupa/results/unit.json, --cov=<package>, --cov-branch, --cov-context=test, --cov-report=json:coverage.json, -n, auto]`, with `results: .chupa/results/unit.json` and `coverage: coverage.json`. covgate runs the unit tests and then gates coverage, so one entry does both and its base rerun measures the base's own coverage;
      - `integration`: exactly `[uv, run, python, -m, pytest, tests/integration, -p, chupa.testreport, --chupa-results, .chupa/results/integration.json, -n, auto]`, with `results: .chupa/results/integration.json`;
      - `lint`: `[uv, run, ruff, check, .]`;
      - `format`: `[uv, run, ruff, format, --check, .]`.
    - `engine_plane_safety_inventory` listing `config.yaml` and `test-gate.toml`.
  - A fenced `toml test-gate` block: `[coverage] default = 90`, plus one commented example each of a package and a file entry, and `[unit] budget_seconds = 60`.
  - Prose giving the remaining host setup:
    - dev dependencies `chupa`, `pytest`, `pytest-cov`, `pytest-xdist`, `ruff`;
    - `[tool.coverage.run] core = "ctrace"` and `[tool.coverage.json] show_contexts = true` in `pyproject.toml` (Python 3.14's default `sysmon` core drops per-test contexts);
    - gitignore `coverage.json` and `.chupa/`.
  - Prose on how drift is caught: the whole-repo `lint` and `format` entries fail at the merge base too when main drifts, and Check files that as `base_red` for a fix ticket.
  - Prose explaining that listing `test-gate.toml` in the inventory sends any ticket that would lower a threshold to a human.
- In: `tests/test_host_contract.py`: new test. The `python-host` block deep-merged into the `host-example` block loads with `config.load_config`. The `test-gate` block parses with `chupa.covgate.parse_gate` to `default` 90 and `budget_seconds` 60.
- In: `docs/how-chupa-works.md`: section 4.2 says the Implement prompt carries the test rules. Section 12 points Python hosts to `## Python host test setup`.
- Out: chupa's own `config.yaml`, `pyproject.toml` and `tests/` layout (ticket for chupa adopting the rules); `CLAUDE.md`, `AGENTS.md` and the core template; every other spec; review finding codes; any engine code.

## Scope fence
- specs/implement.md
- specs/review.md
- tests/test_specs.py
- tests/test_stages.py
- tests/test_host_contract.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. The loaded `specs/implement.md` body contains each of the five test rules. Its version is one minor step above the prior one and its major is unchanged. A test fails if any rule is removed or the version is left unchanged. Checked by `uv run pytest tests/test_specs.py`.
2. The loaded `specs/review.md` body's `logic` bullet names unit-test disk, network and process use, wall-clock or order dependence, and lowered thresholds or budgets. Its version is one minor step above the prior one. Its finding codes are unchanged. A test fails if the addition is missing or a new code appears. Checked by `uv run pytest tests/test_specs.py`.
3. The `python-host` YAML block, deep-merged into `host-example`, loads with `config.load_config`, and `test-gate.toml` is in the inventory. The test asserts:
   - `unit.argv` starts with `[uv, run, python, -m, chupa, covgate, --]` and contains `-p chupa.testguard`, `-p chupa.testreport` and `--cov-context=test`;
   - the value after `--chupa-results` equals `unit.results`, and the `--cov-report=json:` path equals `unit.coverage`;
   - `integration.argv` contains `--chupa-results` followed by `integration.results`, and does not contain `chupa.testguard`;
   - no entry has the code `coverage`;
   - the `review.autofix` codes are `ruff-fix` and `ruff-format`, each with `files == ["*.py"]`;
   - `integration.argv` equals exactly `[uv, run, python, -m, pytest, tests/integration, -p, chupa.testreport, --chupa-results, .chupa/results/integration.json, -n, auto]`.

   The `test-gate` TOML block parses with `parse_gate` to `default` 90 and `budget_seconds` 60. A test fails if either block is missing or refused, or if any of these drift. Checked by `uv run pytest tests/test_host_contract.py`.
4. `uv run pytest tests/test_stages.py` exits 0 with the bumped version pins.
5. `docs/how-chupa-works.md` section 4.2 states the test rules.
6. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_specs.py tests/test_host_contract.py tests/test_stages.py
uv run pytest -q
```

## Definition of rejected
A spec gains a heading outside Role/Task/Inputs/Output format/On-failure; a spec's major version changes; a review finding code is added; chupa's own `config.yaml`, `pyproject.toml` or `tests/` layout changes; engine code changes.

## Time budget
- expected: 45m
- stuck: 120m
