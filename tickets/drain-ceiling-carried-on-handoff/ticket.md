---
priority: P1
kind: bug
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- chupa/drain.py::drain
- chupa/drain.py::_Drain
- chupa/drain.py::reexec_argv
- chupa/__main__.py
- tests/integration/test_drain_upgrade.py
- docs/how-chupa-works.md

## Goal / Why
`drain.max_runtime_hours` is documented as the overall drain ceiling, a runaway backstop on unattended spend (`docs/how-chupa-works.md` section 7.1: "halts it (exit 1)"). `_Drain.__init__` computes `self.deadline = clock() + max_runtime_hours` from its own process start. A self-upgrading merge hands off to a child drain, and the child computes a fresh deadline. Each handoff therefore re-arms the ceiling, and a drain that hands off after time T halts at T + `max_runtime_hours` instead of at the parent's original deadline. Self-upgrading merges are a normal event when chupa drains its own tree.

After this change the parent passes its deadline to the child on the handoff argv (`--deadline <ISO timestamp>`, next to `--parked`), and the child's `_Drain` uses it instead of computing a fresh one. Every process in a handoff chain halts at the first process's deadline.

Simplest approach: one new `drain` CLI option and one new keyword on `drain()`/`_Drain`, mirroring how `--parked` already rides the handoff. Rejected: a journal-derived start time (a second authority for a value the argv can carry), and pinning in section 18 that the ceiling is per-process (it contradicts the documented backstop).

## Scope in / Scope out
- In: add `--deadline` to the `drain` subparser in `chupa/__main__.py` (parsed with `datetime.fromisoformat`, default none) and pass it to `drain.drain` as a new keyword `deadline`. `drain()` forwards it to `_Drain`; `_Drain.__init__` uses it when given and computes `clock() + max_runtime_hours` otherwise. In the handoff's `reexec_argv([...])` list in `chupa/drain.py`, insert `--deadline` and `render_ts(run.deadline)` after the `--parked` pairs and before the conditional `--stop-lifecycle` pair, so `--stop-lifecycle <id>` stays last. Update the two argv assertions in `tests/integration/test_drain_upgrade.py` and add the regression test. Add a new unit test file `tests/unit/test_drain_deadline.py` with three tests. `test_drain_uses_the_carried_deadline` and `test_drain_computes_its_deadline_when_none_is_carried` each build `_Drain` from a fake checkout (a `SimpleNamespace` with a fixed `clock` and `config.drain.max_runtime_hours`, no disk or process access): the first passes a deadline that differs from `clock() + hours` and asserts `run.deadline` equals the passed value; the second passes none and asserts `run.deadline == clock() + hours`. `test_drain_parser_reads_a_carried_deadline` calls `chupa.__main__._parser().parse_args(["drain", "--deadline", "2026-01-01T02:00:00+00:00"])` and asserts `args.deadline == datetime(2026, 1, 1, 2, tzinfo=UTC)`, and asserts `args.deadline is None` when the option is omitted. Add one sentence to `docs/how-chupa-works.md` section 7.1 saying the ceiling is carried across a self-upgrade handoff.
- Other callers are unaffected: the new `deadline` keyword on `drain()`/`_Drain` defaults to None and keeps today's computed deadline, and `--deadline` is optional with default None, so existing direct `_Drain(...)` and `main(["drain"])` callers and every argv assertion outside `tests/integration/test_drain_upgrade.py` are unaffected (`test_drain_upgrade.py` asserts the full handoff argv; `tests/integration/test_drain.py`'s stop-upgrade test checks only `argv[-2:] == ["--stop-lifecycle", <id>]`, which stays true because `--deadline` goes before that pair; `tests/integration/test_closed_sets.py` checks only `reexec_argv`'s last element). No other test file needs a change.
- Out: `serve` (its handoff does not use `max_runtime_hours`); the `drain_halted` signal body; `reexec_argv`'s signature; `CHUPA_PLAN.md` (frozen).
- In: a carried reproducer `tests/regress_drain_deadline.py`, shaped like `tests/regress_dev_test_args.py`. It runs `pytest.main(["tests/integration/test_drain_upgrade.py", "-k", "deadline", "-q", "-p", "no:cacheprovider"])` in-process with stdout redirected to stderr, then prints exactly one JSON object: `{"regression_result": "pass"}` with exit 0 when pytest returns 0, `{"regression_result": "defect"}` with exit 1 when pytest returns 1 (the test failed), and `{"regression_result": "error"}` with exit 2 otherwise (including no test collected) or on any exception. It uses only code present at the base commit; on the base overlaid with the carried files the named test fails, so it prints `defect`.

## Scope fence
- chupa/drain.py
- chupa/__main__.py
- tests/integration/test_drain_upgrade.py
- tests/unit/test_drain_deadline.py
- tests/regress_drain_deadline.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_drain_upgrade.py -k deadline` exits 0: with `drain: {max_runtime_hours: 2}`, a parent whose upgrading dispatch advances the fake clock 3 hours hands off, and the child halts without dispatching `after`. A child with a fresh deadline would dispatch `after`, so the test asserts `("child1", "after")` is absent from `script.calls` and the exit code is 1.
2. `./dev.py test tests/integration/test_drain_upgrade.py` exits 0 with the two handoff argv assertions updated to expect `--deadline` followed by a timestamp after `--parked red`.
3. `./dev.py test tests/unit/test_drain_deadline.py` exits 0: `test_drain_uses_the_carried_deadline` passes a deadline different from `clock() + hours` and asserts `run.deadline` equals it, ruling out a `_Drain` that ignores the passed value and recomputes; `test_drain_computes_its_deadline_when_none_is_carried` asserts the computed value when none is passed; `test_drain_parser_reads_a_carried_deadline` asserts `args.deadline == datetime(2026, 1, 1, 2, tzinfo=UTC)` for the given option and `args.deadline is None` when omitted, ruling out a parser that drops the option.
4. `chupa/drain.py` contains `"--deadline"` in the handoff argv.
5. `./dev.py test` exits 0.
6. `uv run python tests/regress_drain_deadline.py` prints only `{"regression_result": "pass"}` and exits 0 on the fixed code, and prints only `{"regression_result": "defect"}` with a nonzero exit on the unfixed code, which rules out a reproducer whose stdout carries pytest output or whose verdict ignores the test result.

## Regression
```
uv run python tests/regress_drain_deadline.py
```
- carries: tests/integration/test_drain_upgrade.py
- carries: tests/regress_drain_deadline.py

## Verification
```
./dev.py test tests/integration/test_drain_upgrade.py -k deadline
./dev.py test tests/integration/test_drain_upgrade.py
./dev.py test tests/unit/test_drain_deadline.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the child still computes its own `clock() + max_runtime_hours` when `--deadline` is passed;
- a second copy of the ceiling or a new config knob is added;
- the regression test also passes on the unfixed code (a child that dispatches `after` must fail it);
- any file outside the scope fence changes.

## Time budget
- expected: 25m
- stuck: 60m
