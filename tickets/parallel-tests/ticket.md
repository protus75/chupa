---
priority: P1
kind: chore
source: human
state: confirmed
agent_tier: high
agent_effort: high
---

## Depends on
none

## Context
- pyproject.toml
- tests/test_serve.py
- tests/test_provider_cooldown_failover.py
- tests/test_git.py
- tests/test_providers.py
- tests/test_notify.py
- tests/test_restart_timers.py
- docs/how-chupa-works.md

## On-demand
- uv.lock

## Goal / Why
`uv run pytest -q` runs 3,884 tests on one core in about 7 minutes, and every ticket attempt runs it two or three times (Check, then again at merge), so most of each attempt is spent waiting on the suite. The machine has 20 cores. A trial with `uv run --with pytest-xdist pytest -q -n auto` passed in 75 seconds, then failed `tests/test_provider_cooldown_failover.py::test_escalated_drought_uses_effective_route[codex-drain]` on the next run: tests that bound a wait by an iteration count, rather than by time, give up before real subprocess work finishes when every core is busy. The suite must run in parallel by default and pass reliably, and no test may wait on a fixed sleep.

## Scope in / Scope out
- In: add `pytest-xdist` to the `dev` dependency group (`pyproject.toml`, `uv.lock`) and `-n auto` to `[tool.pytest.ini_options]` `addopts`, so `uv run pytest -q` (every ticket's Verification and `./dev.py test`) runs in parallel.
- In: fix every test that fails or flakes under parallel runs at the root cause, never by retrying, skipping, marking serial, or lengthening a bound. Known cause: wait loops bounded by iteration count while real git or subprocess work runs, starting with `until` in `tests/test_serve.py` (shared by six other test files) and the counted loops in `tests/test_serve.py`, `tests/test_notify.py`, and `tests/test_restart_timers.py`. They wait on the condition itself against a wall-clock deadline of at least 60 seconds, yielding to the event loop between checks, so a fast machine returns as soon as the condition holds and a loaded one still has time.
- In: remove every fixed `time.sleep` from the tests. The process-group kill tests in `tests/test_git.py` (around lines 251-299) and `tests/test_providers.py` (around lines 829-882) need real child processes; they wait for the observable event (the marker file appearing, the process group being gone) with a wall-clock deadline instead of sleeping a fixed time. Sleeps inside a spawned child's own script that make it hang until killed stay.
- In: any shared state found under parallel runs (environment variables, working directory, fixed paths, ports, module globals) is made per-test through `tmp_path` or `monkeypatch`.
- In: update `docs/how-chupa-works.md` section 2.2 to say `./dev.py test` runs the suite in parallel.
- Out: converting tests to mocks, moving tests into unit and integration directories, and any change to `chupa/` production code. Those are separate tickets.

## Scope fence
- pyproject.toml
- uv.lock
- tests/
- docs/how-chupa-works.md

## Acceptance criteria
1. `pyproject.toml` lists `pytest-xdist` in the `dev` group and `-n auto` in `addopts`.
2. `uv run pytest -q` exits 0 three times in a row, each run under 120 seconds on this machine.
3. `tests/` contains no `time.sleep(` call outside a spawned child process's own script text.
4. `docs/how-chupa-works.md` section 2.2 says `./dev.py test` runs the suite in parallel.

## Verification
```
uv run pytest -q
uv run pytest -q
uv run pytest -q
```

## Definition of rejected
Reject the branch if any test is skipped, retried, marked serial, or given a longer bound to pass; if a fixed sleep remains outside a child's own script; if `chupa/` changes; or if any test is deleted.

## Time budget
- expected: 60m
- stuck: 120m
