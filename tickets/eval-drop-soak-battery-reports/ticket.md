---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- chupa/artifacts.py::DaemonSoakEntry
- chupa/artifacts.py::DaemonSoakReport
- chupa/artifacts.py::ReliabilityBatteryEntry
- chupa/artifacts.py::ReliabilityBatteryReport
- chupa/artifacts.py::_check_ordered_members
- chupa/stages.py::KNOWN_ARTIFACTS
- eval/daemon_soak.py
- eval/reliability_battery.py
- tests/integration/test_daemon_soak.py
- tests/unit/test_artifacts.py

## Goal / Why
The daemon soak report (`daemon-soak-report.json`) and reliability battery report (`reliability-battery-report.json`) were bootstrap phase-completion proofs. No engine path reads them at runtime. They are registered in `KNOWN_ARTIFACTS` only so a report-only ticket could lift and merge them, and the committed copies under `tickets/soak-run/` and `tickets/reliability-run/` are read by nothing. The engine still defines their schemas, and `eval/daemon_soak.py` and `eval/reliability_battery.py` still carry `--out` producers (`write_report`, `_main`, `main`) that only their own tests call.

After this change the engine no longer registers or defines either report, and the report-writing code is gone. The end-to-end harnesses stay: each still runs its members against a production drain or serve and returns its entries, and their tests keep running as end-to-end regression checks.

Simplest approach: move the observation types and constants each harness still builds into that harness module unchanged, and delete the writers and command entry points. Rejected alternative: rewriting the harnesses to return plain dicts, which would churn the end-to-end tests.

## Scope in / Scope out
- In: `chupa/artifacts.py`: remove `DAEMON_SOAK_REPORT`, `DAEMON_SOAK_SPEC_VERSION`, `DAEMON_SOAK_MEMBERS`, `_DAEMON_SOAK_EXPECTED`, `DaemonSoakEntry`, `DaemonSoakReport`, `RELIABILITY_BATTERY_REPORT`, `RELIABILITY_BATTERY_SPEC_VERSION`, `RELIABILITY_BATTERY_MEMBERS`, `_RELIABILITY_BATTERY_EXPECTED`, `ReliabilityBatteryEntry` and `ReliabilityBatteryReport`. Keep `_check_producing_run` and `_check_ordered_members` there, imported by the harnesses.
- In: `chupa/stages.py`: drop those imports and the two `KNOWN_ARTIFACTS` entries.
- In: `eval/daemon_soak.py`:
  - define the moved soak constants and types with the same fields and validators. They may import `Artifact`, `_Strict`, `NonBlank`, `_check_producing_run` and `_check_ordered_members` from `chupa.artifacts`.
  - delete `write_report`, `_main`, `main` and the `__main__` block.
  - change the `SoakRefused` road from `rerun uv run python -m eval.daemon_soak --out <path>` to `rerun the soak tests`, keeping the `<member>: <detail>` prefix.
  - keep `produce`, `_run_member`, `_observe` and the members.
- In: `eval/reliability_battery.py`:
  - the same move for the battery constants and types.
  - delete `write_report`, `_main`, `main` and the `__main__` block.
  - if `BatteryRefused`'s message names `python -m eval.reliability_battery`, change it to `rerun the battery tests` the same way.
  - keep `produce` and the members.
- In: tests.
  - `tests/integration/test_daemon_soak.py`: import the moved names from `eval.daemon_soak`. Keep `test_daemon_soak_schema_is_closed` and `test_daemon_soak_green_matches_observation_and_auditor`, minus their `DAEMON_SOAK_REPORT` constant assertion. Delete `test_daemon_soak_writer_validates_before_write`, `test_daemon_soak_uses_registered_checks_lift` and `test_daemon_soak_command_writes_report_only_on_green`.
  - `tests/integration/test_reliability_battery.py`: import the moved names from `eval.reliability_battery`. Keep the schema, green and member tests, minus the `RELIABILITY_BATTERY_REPORT` constant assertion. Delete `test_reliability_battery_writer_validates_before_write`, `test_reliability_battery_uses_registered_checks_lift` and `test_reliability_battery_command_writes_only_on_green`. Remove the `rglob(RELIABILITY_BATTERY_REPORT)` assertion in `test_classified_quota_exhaustion`.
  - `tests/integration/test_daemon_soak_runner.py`: import `DAEMON_SOAK_MEMBERS` from `eval.daemon_soak`.
  - `tests/integration/test_closed_sets.py`: remove the `DAEMON_SOAK_*` and `RELIABILITY_BATTERY_*` assertions from `test_artifacts_closed_sets_and_constants`. Remove the `daemon-soak-report.json` and `reliability-battery-report.json` rows from the `KNOWN_ARTIFACTS` assertion.
  - `tests/unit/test_artifacts.py`: `test_ordered_members_check` calls `chupa.artifacts._check_ordered_members` directly with `types.SimpleNamespace(member=...)` entries. Members in the expected order pass. The reversed order raises `ValueError` with the same `entries must contain exactly ..., in order` message. This keeps the test free of any report type.
- In: `docs/how-chupa-works.md` section 13: remove "soak" and "reliability battery" from the eval report artifacts list.
- Unaffected: the other coverage-dependent test files of `chupa/artifacts.py` and `chupa/stages.py` reference none of the removed names. A grep for `DaemonSoak`, `ReliabilityBattery`, `DAEMON_SOAK_` and `RELIABILITY_BATTERY_` outside the fenced files finds no code use, so their behavior does not change.
- Out:
  - the committed report files under `tickets/` (history);
  - moving these harnesses under `tests/` (ticket `eval-move-soak-battery-host-loop`);
  - the shakeout report;
  - `eval/harness.py` and the review-baseline report;
  - the cause of the soak flake (ticket `soak-serve-stops-early-under-load`).

## Scope fence
- chupa/artifacts.py
- chupa/stages.py
- eval/daemon_soak.py
- eval/reliability_battery.py
- tests/integration/test_daemon_soak.py
- tests/integration/test_reliability_battery.py
- tests/integration/test_daemon_soak_runner.py
- tests/integration/test_closed_sets.py
- tests/unit/test_artifacts.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run python -c "import chupa.artifacts as a, chupa.stages as s; assert not any(hasattr(a, n) for n in ('DaemonSoakReport','DaemonSoakEntry','ReliabilityBatteryReport','ReliabilityBatteryEntry','DAEMON_SOAK_REPORT','RELIABILITY_BATTERY_REPORT')); assert not {'daemon-soak-report.json','reliability-battery-report.json'} & set(s.KNOWN_ARTIFACTS)"` exits 0, ruling out a type left in the engine or still registered.
2. `uv run python -c "import eval.daemon_soak as d, eval.reliability_battery as r; assert not any(hasattr(m, n) for m in (d, r) for n in ('write_report','main','_main')); d.DaemonSoakReport; r.ReliabilityBatteryReport; d.produce; r.produce"` exits 0, ruling out a leftover producer or a deleted harness.
3. `./dev.py test tests/integration/test_daemon_soak.py tests/integration/test_reliability_battery.py tests/integration/test_daemon_soak_runner.py` exits 0 and still runs `test_daemon_soak_conflict_rungs` and `test_classified_quota_exhaustion`, so the end-to-end harnesses keep working.
4. `./dev.py test tests/unit/test_artifacts.py tests/integration/test_closed_sets.py` exits 0.
5. `./dev.py test` exits 0.

## Verification
```
uv run python -c "import chupa.artifacts as a, chupa.stages as s; assert not any(hasattr(a, n) for n in ('DaemonSoakReport','DaemonSoakEntry','ReliabilityBatteryReport','ReliabilityBatteryEntry','DAEMON_SOAK_REPORT','RELIABILITY_BATTERY_REPORT')); assert not {'daemon-soak-report.json','reliability-battery-report.json'} & set(s.KNOWN_ARTIFACTS)"
uv run python -c "import eval.daemon_soak as d, eval.reliability_battery as r; assert not any(hasattr(m, n) for m in (d, r) for n in ('write_report','main','_main')); d.DaemonSoakReport; r.ReliabilityBatteryReport; d.produce; r.produce"
./dev.py test tests/integration/test_daemon_soak.py tests/integration/test_reliability_battery.py tests/integration/test_daemon_soak_runner.py
./dev.py test tests/unit/test_artifacts.py tests/integration/test_closed_sets.py
./dev.py test
```

## Definition of rejected
Either report type is still defined in or registered by `chupa/`; an end-to-end member test is deleted rather than kept; a timeout, retry or skip is added; a committed file under `tickets/` changes; or any file outside the fence changes.

## Time budget
- expected: 40m
- stuck: 80m
