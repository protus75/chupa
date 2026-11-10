---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- eval-drop-host-loop-report
- eval-drop-soak-battery-reports
- eval-move-shakeout

## Context
- eval/host_loop.py
- eval/reliability_battery.py
- tests/integration/test_vocabularies.py::_engine_signal_names
- hosts/fixture/README.md

## On-demand
- eval/daemon_soak.py

## Goal / Why
`eval/daemon_soak.py`, `eval/reliability_battery.py` and `eval/host_loop.py` are end-to-end scenario harnesses. Once `eval-drop-host-loop-report` and `eval-drop-soak-battery-reports` remove their report commands, they are used only by `tests/integration/test_daemon_soak.py`, `test_daemon_soak_runner.py`, `test_reliability_battery.py` and `test_host_loop.py`. This is test code that lives outside `tests/`.

After this change the three modules live in `tests/harness/` (created by `eval-move-shakeout`) as `tests/harness/daemon_soak.py`, `tests/harness/reliability_battery.py` and `tests/harness/host_loop.py`. They are imported as `tests.harness.*` and run unchanged. They move together because `reliability_battery` imports `_Time` and `_turn` from `daemon_soak`.

Simplest approach: a move with import-path edits only, plus fixing the one path computed from the file's own location.

## Scope in / Scope out
- In: move the three modules to `tests/harness/` under the same names. Their content stays unchanged except for the edits below.
- In: `reliability_battery.py` imports `from tests.harness.daemon_soak import _Time, _turn`.
- In: `host_loop.py`'s `ROOT = Path(__file__).resolve().parents[1]` becomes `parents[2]`. It still names the repository root, which it passes as `PYTHONPATH` to the fixture host, so `hosts.fixture` stays importable there.
- In: the four test files import `daemon_soak`, `reliability_battery` and `host_loop` from `tests.harness` instead of `eval`, keeping their existing local aliases (`soak`, `battery`).
- In: `hosts/fixture/README.md`: `eval/host_loop.py` becomes `tests/harness/host_loop.py`.
- Unaffected: no other file outside the fence imports these modules. With the report tests gone after the two dependencies, a grep for `eval.daemon_soak`, `eval.reliability_battery`, `eval.host_loop` and `from eval import` (daemon_soak, reliability_battery, host_loop) finds only the moved modules, the four fenced tests, and ticket history. `tests/integration/test_vocabularies.py` already scans `tests/harness` after `eval-move-shakeout`, so the moved modules stay in its signal check.
- Out: `eval/diagnose.py` (ticket `eval-move-diagnose`); `eval/harness.py` and `eval/fixtures/`; behavior changes to any member; the soak flake (ticket `soak-serve-stops-early-under-load`); ticket history under `tickets/`.

## Scope fence
- eval/daemon_soak.py
- eval/reliability_battery.py
- eval/host_loop.py
- tests/harness/daemon_soak.py
- tests/harness/reliability_battery.py
- tests/harness/host_loop.py
- tests/integration/test_daemon_soak.py
- tests/integration/test_daemon_soak_runner.py
- tests/integration/test_reliability_battery.py
- tests/integration/test_host_loop.py
- hosts/fixture/README.md

## Acceptance criteria
1. `uv run python -c "from pathlib import Path; assert not any(Path('eval', n).exists() for n in ('daemon_soak.py','reliability_battery.py','host_loop.py')); import tests.harness.daemon_soak as d, tests.harness.reliability_battery as r, tests.harness.host_loop as h; assert h.ROOT == Path.cwd().resolve(); d.produce; r.produce; h.produce"` exits 0. This rules out a copy left in `eval/`, a module that does not import, and a `ROOT` that points at `tests/` instead of the repository root.
2. `./dev.py test tests/integration/test_daemon_soak.py tests/integration/test_daemon_soak_runner.py tests/integration/test_reliability_battery.py tests/integration/test_host_loop.py` exits 0 with every existing test collected, including `test_host_loop_drives_supervised_fixture_serve`. That test fails if the fixture host cannot import `hosts.fixture` from the `PYTHONPATH` that `ROOT` sets.
3. `./dev.py test tests/integration/test_vocabularies.py` exits 0.
4. `./dev.py test` exits 0.

## Verification
```
uv run python -c "from pathlib import Path; assert not any(Path('eval', n).exists() for n in ('daemon_soak.py','reliability_battery.py','host_loop.py')); import tests.harness.daemon_soak as d, tests.harness.reliability_battery as r, tests.harness.host_loop as h; assert h.ROOT == Path.cwd().resolve(); d.produce; r.produce; h.produce"
./dev.py test tests/integration/test_daemon_soak.py tests/integration/test_daemon_soak_runner.py tests/integration/test_reliability_battery.py tests/integration/test_host_loop.py
./dev.py test tests/integration/test_vocabularies.py
./dev.py test
```

## Definition of rejected
Any of the three modules remains in `eval/`; a member's behavior changes; a harness test is deleted; or any file outside the fence changes.

## Time budget
- expected: 25m
- stuck: 50m
