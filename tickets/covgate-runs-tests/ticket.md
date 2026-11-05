---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- covgate

## Context
- chupa/__main__.py
- chupa/seams.py

## On-demand
- docs/how-chupa-works.md

## Goal / Why
`chupa covgate` only reads a `coverage.json` that an earlier check wrote, so as a `review.mechanical` entry it can never block a ticket. When it fails, Check reruns that one entry alone in a fresh worktree at the merge base. The report is missing there, so covgate refuses (exit 2), Check marks the failure base-red, and drops it from the verdict. After this change covgate runs the unit-test command itself, `chupa covgate [--gate P] [--report P] -- <argv...>`, then evaluates the report that command just wrote. One entry both tests and gates coverage, and its base rerun measures the base's own coverage.

## Scope in / Scope out
Read `chupa/covgate.py` and `tests/test_covgate.py` from the worktree first; they exist once `covgate` merges.

- In: `chupa/covgate.py`: a function `run_gate(argv, *, gate_path, report_path, run)` that:
  1. deletes `report_path` if present, so a stale report is never evaluated;
  2. calls `run(argv)` and gets its exit code;
  3. returns that exit code unchanged when it is nonzero, so failing tests fail the check with the test runner's own code;
  4. otherwise reads the gate file and the report and evaluates them exactly as today. A missing report after a zero exit is a refusal (exit 2) whose road says the command must write `--cov-report=json:<report>`.
- In: `chupa/__main__.py`: `covgate` requires an argv after `--`. Without one it refuses with exit 2 and the road "name the unit-test command after --". This replaces the report-only mode; there is no second mode. The production `run` is `subprocess.run(argv, cwd=repo, env=env).returncode`, using main's `cwd` and `env`, with inherited stdio and no new session. A missing executable (`FileNotFoundError`) is a refusal with exit 2: `chupa covgate: <argv0> not found -- install it or correct the command after --`. A comment says why this does not use the `ProcessExec` seam: the seam starts each child in its own session, so Check's timeout group-kill of covgate would orphan the test run, whereas covgate's own process group carries the kill to it.
- In: `tests/test_covgate.py`: update the CLI tests to the new form. Add `run_gate` tests with a fake `run` that writes or omits the report.
- In: `docs/how-chupa-works.md` section 2.1: the `covgate` row gives the new form and exit codes.
- Out: the gate grammar and evaluation; `parse_gate`; config; Check; testguard.

## Scope fence
- chupa/covgate.py
- chupa/__main__.py
- tests/test_covgate.py
- docs/how-chupa-works.md

## Acceptance criteria
1. With a fake `run` that writes a passing report and returns 0, `run_gate` returns 0. With one that writes a below-minimum report and returns 0, it returns 1. A test fails if the report is not evaluated after the run. Checked by `uv run pytest tests/test_covgate.py`.
2. With a fake `run` that returns 1 (tests failed) after writing a passing report, `run_gate` returns 1. With one that returns 2, it returns 2. A test fails if a failing test run is masked by a passing coverage evaluation. Checked by `uv run pytest tests/test_covgate.py`.
3. A stale report present before the run, with a fake `run` that returns 0 and writes nothing, is a refusal (exit 2). A test fails if the stale report is evaluated. Checked by `uv run pytest tests/test_covgate.py`.
4. `tmp_path` holds a valid `test-gate.toml` and a passing `coverage.json`, so report-only evaluation would exit 0. In it, `main(["covgate"], cwd=tmp_path)` without `--` and an argv exits 2, and its output contains `name the unit-test command after --`. A test fails if it exits 0 or evaluates the existing report. Checked by `uv run pytest tests/test_covgate.py`.
5. In a `tmp_path` with a valid `test-gate.toml` and no `config.yaml`, `main(["covgate", "--", sys.executable, "-c", <script>], cwd=tmp_path)` exits 0. The script records `os.getpgrp()` and writes a passing report to the relative path `coverage.json`. The recorded pgid equals the test process's `os.getpgrp()`. A test fails if the child runs outside the `cwd` passed to `main`, or in its own process group. `main(["covgate", "--", "no-such-binary-xyz"], cwd=tmp_path)` exits 2 with the not-found road, not 1 and not a traceback. Checked by `uv run pytest tests/test_covgate.py`.
6. `docs/how-chupa-works.md` section 2.1 shows `covgate ... -- <argv>`.
7. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_covgate.py
uv run pytest -q
```

## Definition of rejected
covgate keeps a report-only mode; a stale report can be evaluated; a nonzero test-run exit becomes 0; the child runs in a new session; the gate grammar or evaluation changes.

## Time budget
- expected: 30m
- stuck: 90m
