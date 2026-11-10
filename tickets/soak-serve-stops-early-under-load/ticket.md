---
state: confirmed
source: human
priority: P1
kind: chore
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

So the `conflict_resolution_rungs` member's production `serve` task exits with code 1 before `until` sees its predicate. Because the full suite is the Check gate, each flake fails an unrelated ticket and the engine redoes Implement and Check (2026-11-09: `vscode-command-not-found` attempt 0; earlier `retro-request-serve`, Suggestion Box 000359). After this change the member no longer stops early under parallel load, and the cause is named.

Suspects to test first, not conclusions: the member's real-subprocess `Git(..., timeout=30)` and `exec.run(..., timeout=30)` calls (eval/daemon_soak.py:174, :252) exceeding their timeout under load; and `until`'s wall-clock `time.monotonic() + 60` loop (eval/daemon_soak.py:311) interleaving with the fake clock's `advance(serve.SERVE_POLL_S)`.

## Scope in / Scope out
- In: reproduce the early stop under load (for example by running the member with CPU contention, or by injecting a slow or timing-out subprocess at the `ProcessExec` seam), read why `serve` returned 1 from the member's journal and engine log, and name that cause in the run record with the evidence line that shows it.
- In: fix the cause in `eval/daemon_soak.py` or `tests/integration/test_daemon_soak_runner.py`, whichever owns it.
- In: a deterministic test in `tests/integration/test_daemon_soak_runner.py` named `test_conflict_rungs_member_survives_slow_subprocess` that forces the identified condition through an injected seam (no reliance on real machine load) and fails on the base commit.
- Out: raising a timeout, retrying the member, or marking the test flaky/skipped as the fix (each hides the cause); changing `chupa/` production code. If the cause is in `chupa/serve.py` or another `chupa/` module, reply `premise_failed` naming the file and the cause.
- Out: other soak members, unless the same named cause affects them; then list them in the run record only.

## Scope fence
- eval/daemon_soak.py
- tests/integration/test_daemon_soak_runner.py

## Acceptance criteria
1. The run record names why `serve` exited 1 and quotes the journal, engine-log, or captured line that shows it. Checked at Review.
2. `./dev.py test tests/integration/test_daemon_soak_runner.py -k test_conflict_rungs_member_survives_slow_subprocess` exits 0, and the test fails on the base commit, ruling out a test that never forces the condition. Checked by Review against the run record's base result.
3. `./dev.py test tests/integration/test_daemon_soak_runner.py` exits 0.
4. No timeout in `eval/daemon_soak.py` is raised, no retry is added, and the test is not skipped or marked flaky. Checked at Review against the diff.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_daemon_soak_runner.py -k test_conflict_rungs_member_survives_slow_subprocess
./dev.py test tests/integration/test_daemon_soak_runner.py
./dev.py test
```

## Definition of rejected
The flake is hidden rather than fixed (a raised timeout, a retry, a skip or flaky mark); the cause is not named with evidence; the new test passes on the base commit; or any `chupa/` file changes.

## Time budget
- expected: 60m
- stuck: 90m
