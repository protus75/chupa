---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- none

## Context
- eval/daemon_soak.py
- tests/integration/test_daemon_soak_runner.py
- chupa/serve.py

## Goal / Why
`tests/integration/test_daemon_soak_runner.py::test_daemon_soak_runs_production_serve` fails intermittently in the full parallel suite (`./dev.py test`, ~3,300 tests under `-n auto`) and passes when run alone on unchanged code (3 of 3 isolated runs on main, 2026-11-09). Every recorded failure has the same signature, from `.chupa/state/spools/retro-request-serve/1/check/host-02.txt` and `.chupa/state/spools/vscode-command-not-found/0/check/verify-02.txt`:

```
eval/daemon_soak.py:317: SoakRefused
E   eval.daemon_soak.SoakRefused: conflict_resolution_rungs: serve stopped early (1); repair this member's production behavior/evidence and rerun uv run python -m eval.daemon_soak --out <path>
```

The full captured excerpts are in `evidence/soak-stops-early.txt`. So the `conflict_resolution_rungs` member's production `serve` task exits with code 1 before `until` sees its predicate. Because the full suite is the Check gate, each flake fails an unrelated ticket and the engine redoes Implement and Check (2026-11-09: `vscode-command-not-found` attempt 0; earlier `retro-request-serve`, Suggestion Box 000359). After this change the member no longer stops early under parallel load, and the cause is named.

Suspects to test first, not conclusions: the member's real-subprocess `Git(..., timeout=30)` and `exec.run(..., timeout=30)` calls (eval/daemon_soak.py:174, :252) exceeding their timeout under load; and `until`'s wall-clock `time.monotonic() + 60` loop (eval/daemon_soak.py:311) interleaving with the fake clock's `advance(serve.SERVE_POLL_S)`.

## Scope in / Scope out
- In: reproduce the early stop under load (for example by running the member with CPU contention, or by injecting a slow or timing-out subprocess at the `ProcessExec` seam), read why `serve` returned 1 from the member's journal and engine log, and name that cause in the run record with the evidence line that shows it.
- In: fix the cause in `eval/daemon_soak.py` or `tests/integration/test_daemon_soak_runner.py`, whichever owns it.
- In: a deterministic test in `tests/integration/test_daemon_soak_runner.py` named `test_conflict_rungs_member_survives_slow_subprocess` that forces the identified condition through an injected seam (no reliance on real machine load) and fails on the base commit.
- In: a carried reproducer `tests/regress_soak_slow_subprocess.py`, shaped like `tests/regress_dev_test_args.py`. It runs `pytest.main(["tests/integration/test_daemon_soak_runner.py", "-k", "test_conflict_rungs_member_survives_slow_subprocess", "-q", "-p", "no:cacheprovider"])` in-process with stdout redirected to stderr, then prints exactly one JSON object: `{"regression_result": "pass"}` with exit 0 when pytest returns 0, `{"regression_result": "defect"}` with exit 1 when pytest returns 1, and `{"regression_result": "error"}` with exit 2 otherwise (including no test collected) or on any exception. It uses only code present at the base commit.
- Out: raising a timeout, retrying the member, or marking the test flaky/skipped as the fix (each hides the cause); changing `chupa/` production code. If the cause is in `chupa/serve.py` or another `chupa/` module, reply `premise_failed` naming the file and the cause.
- Out: other soak members, unless the same named cause affects them; then list them in the run record only.

## Scope fence
- eval/daemon_soak.py
- tests/integration/test_daemon_soak_runner.py
- tests/regress_soak_slow_subprocess.py

## Acceptance criteria
1. `tickets/soak-serve-stops-early-under-load/run.md` names why `serve` exited 1 and quotes the journal, engine-log, or captured line that shows it.
2. `uv run python tests/regress_soak_slow_subprocess.py` prints only `{"regression_result": "pass"}` and exits 0 on the fixed code, and prints only `{"regression_result": "defect"}` with a nonzero exit on the base commit with the carried files, which rules out a test that never forces the condition.
3. `./dev.py test tests/integration/test_daemon_soak_runner.py` exits 0.
4. The diff to `eval/daemon_soak.py` raises no timeout, adds no retry, and adds no `skip`, `xfail` or `flaky` mark; checked by reading `git diff` of the fenced files.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_daemon_soak_runner.py -k test_conflict_rungs_member_survives_slow_subprocess
uv run python tests/regress_soak_slow_subprocess.py
./dev.py test tests/integration/test_daemon_soak_runner.py
./dev.py test
```

## Regression
```
uv run python tests/regress_soak_slow_subprocess.py
```
- carries: tests/integration/test_daemon_soak_runner.py
- carries: tests/regress_soak_slow_subprocess.py

## Definition of rejected
The flake is hidden rather than fixed (a raised timeout, a retry, a skip or flaky mark); the cause is not named with evidence; the new test passes on the base commit; or any `chupa/` file changes.

## Time budget
- expected: 60m
- stuck: 90m
