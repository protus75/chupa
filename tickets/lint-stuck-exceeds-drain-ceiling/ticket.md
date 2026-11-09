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
- chupa/__main__.py::_lint
- chupa/drain.py
- tests/integration/test_lint_verb.py

## Goal / Why
A confirmed ticket whose `## Time budget` `- stuck:` exceeds `drain.max_ticket_minutes` passes `chupa lint` and intake. The drain then parks it at dispatch as "never dispatched" (`chupa/drain.py`, `self.over_budget`), and that park writes no journal event. Status and the snapshot are built from the journal, so they never show it. The only record is a drain report the operator may not read (retro-request-serve: stuck 210m against a 180m ceiling). After this change `chupa lint` refuses such a ticket with the same ceiling and paved road the drain uses, so the mistake is caught at authoring time.

The change only adds a finding inside the `lint` verb path of `chupa/__main__.py`, which no other verb reaches. The coverage-dependent test files that run `chupa/__main__.py` (tests/integration/test_ask.py through test_watchdog_activation.py, plus tests/unit/test_host_running.py, for example test_drain.py, test_storm_hold.py, test_cli.py and test_tickets.py) never call lint with an over-ceiling ticket. The only fixtures above 90m (test_drain.py `stuck: 200m`, test_storm_hold.py `stuck: 100m`) never call lint, so no listed dependent's behavior changes.

## Scope in / Scope out
- In: `chupa/__main__.py` gains a small pure function `stuck_ceiling_finding(stuck_minutes, ceiling)` that returns a finding string naming both values and the paved road (lower `- stuck:` to at most the ceiling, or split the ticket) when `stuck_minutes` is greater than `ceiling`, and `None` otherwise. `_lint` calls it with `checkout.config.drain.max_ticket_minutes`. `tests/unit/test_lint_ceiling.py` adds `test_stuck_over_ceiling_finding`, which runs the helper directly with no fakes needed. `tests/integration/test_lint_verb.py` adds `test_lint_flags_stuck_over_drain_ceiling`. `docs/how-chupa-works.md` notes the new check in the `lint` verb row.
- Out: the drain's own park and its report, the grammar in `chupa/tickets.py`, `validate_ticket` and `parse_ticket` (they have no config), a journal event for the park, and the stuck versus expected rule.
- In: a carried reproducer `tests/regress_lint_stuck_ceiling.py`, shaped like `tests/regress_dev_test_args.py`. It runs `pytest.main(["tests/integration/test_lint_verb.py", "-k", "test_lint_flags_stuck_over_drain_ceiling", "-q", "-p", "no:cacheprovider"])` in-process with stdout redirected to stderr, then prints exactly one JSON object: `{"regression_result": "pass"}` with exit 0 when pytest returns 0, `{"regression_result": "defect"}` with exit 1 when pytest returns 1 (the test failed), and `{"regression_result": "error"}` with exit 2 otherwise (including no test collected) or on any exception. It uses only code present at the base commit; on the base overlaid with the carried files the named test fails, so it prints `defect`.

## Scope fence
- chupa/__main__.py
- tests/unit/test_lint_ceiling.py
- tests/integration/test_lint_verb.py
- tests/regress_lint_stuck_ceiling.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/unit/test_lint_ceiling.py` exits 0, including `test_stuck_over_ceiling_finding`. That test asserts that `stuck_ceiling_finding(91, 90)` returns a string containing both `91` and `90`, and that `stuck_ceiling_finding(90, 90)` returns `None`. A test that only checked for a non-empty result would pass on a finding that names the wrong values, so it asserts the text and the boundary.
2. `./dev.py test tests/integration/test_lint_verb.py` exits 0, including `test_lint_flags_stuck_over_drain_ceiling`. That test asserts that lint exits 1 and prints the ceiling for a ticket with `- stuck: 91m` under the default 90m ceiling. It also asserts that a ticket with `- stuck: 90m` exits 0. A test that only checked exit 1 would pass on any other lint failure, so it asserts the finding text too.
3. `./dev.py test` exits 0, so every existing lint test and committed-ticket check is unchanged.
4. `docs/how-chupa-works.md` mentions `drain.max_ticket_minutes` in the `lint` row of the verb table.
5. `uv run python tests/regress_lint_stuck_ceiling.py` prints only `{"regression_result": "pass"}` and exits 0 on the fixed code, and prints only `{"regression_result": "defect"}` with a nonzero exit on the unfixed code, which rules out a reproducer whose stdout carries pytest output or whose verdict ignores the test result.

## Verification
```
./dev.py test tests/unit/test_lint_ceiling.py
./dev.py test tests/integration/test_lint_verb.py
./dev.py test
```

## Regression
```
uv run python tests/regress_lint_stuck_ceiling.py
```
- carries: tests/integration/test_lint_verb.py
- carries: tests/regress_lint_stuck_ceiling.py

## Definition of rejected
Reject the branch if a ticket with `stuck` above `drain.max_ticket_minutes` still lints clean, if a ticket at or under the ceiling is refused, if the check is added to `chupa/tickets.py` or to the drain, or if the regression test passes on the merge base.

## Time budget
- expected: 25m
- stuck: 60m
