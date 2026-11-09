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
- chupa/artifacts.py::BaselineSignal
- chupa/artifacts.py::ReviewBaselineReport
- chupa/artifacts.py::HostLoopEntry
- chupa/artifacts.py::HostLoopReport
- chupa/artifacts.py::ExitReceipt

## Goal / Why
`chupa/artifacts.py` repeats three validator bodies across its pydantic models, so a fix to one copy can miss the others:
- the `producing_run` check (`rpartition("/")`, `[0-9]+` sequence, `stem_findings(stem)`, error `producing_run must be <ticket stem>/<nonnegative run sequence>`) in `DaemonSoakEntry._consistent`, `ReliabilityBatteryEntry._consistent` and `HostLoopEntry._consistent`;
- the `type(value) is not int` check in the four `_integer_version` field validators of `BaselineSignal`, `ReviewBaselineReport`, `HostLoopReport` and `ExitReceipt`;
- the ordered-members check in `DaemonSoakReport._ordered_members` and `ReliabilityBatteryReport._ordered_members`.

After this change each check's body exists once, as a module-level private function in `chupa/artifacts.py`, and every validator above calls it. Every model accepts and rejects exactly the same inputs as today, with byte-identical error messages.

## Scope in / Scope out
- In: add three module-level private functions to `chupa/artifacts.py`:
  - a `producing_run` checker taking the string; it holds the `from chupa.tickets import stem_findings` import (kept function-local, as today) and raises the existing message;
  - an integer checker taking the value and the full error message, returning the value. It takes the whole message, not a field name, because the current messages differ beyond the field name: `signal v must be the integer 1` and `schema_version must be the integer 1` versus `schema_version must be integer 1` (in `HostLoopReport` and `ExitReceipt`), and they stay byte-identical;
  - an ordered-members checker taking the entries and the expected members tuple, raising `entries must contain exactly {expected}, in order`.
- In: each of the nine validators named in Goal / Why calls its checker in place of the inline body. Each model keeps its own `@model_validator` / `@field_validator` method; the rest of every `_consistent` body (expected/disposition, green) is unchanged.
- Existing tests that already reject each check, and keep passing unchanged: `tests/integration/test_daemon_soak.py` (bad `producing_run` values, reordered/missing entries), `tests/integration/test_reliability_battery.py::test_reliability_battery_schema_is_closed` (bad `producing_run`, reordered/missing entries), `tests/integration/test_host_loop.py::test_host_loop_closed_schema` (`producing_run="invalid/negative"`, `schema_version: True`), `tests/integration/test_host_loop.py::test_host_loop_report_regression_and_escape` (`ExitReceipt` `schema_version: True`), `tests/integration/test_go_grade.py::test_review_baseline_report_closed_schema` (`schema_version=True`, `verdict_signal` `v=True`). No test pins the message text, so the byte-identity criterion is checked by grep, and every check already has rejection coverage, so no test is added.
- Out: `ShakeoutEntry._consistent` (a different regex and message, `<bench stem>/<run seq>`); `HostLoopReport._ordered` (a different rule); the `, in order` paved road in `chupa/stages.py`; metaclasses, mixins, base-class validators or decorator factories; any change to a model's fields, accepted inputs or messages; `test-gate.toml`.

## Scope fence
- chupa/artifacts.py

## Acceptance criteria
1. `grep -c 'producing_run must be <ticket stem>/<nonnegative run sequence>' chupa/artifacts.py` prints `1`, not `3`; `grep -c 'rpartition("/")' chupa/artifacts.py` prints `1`.
2. `grep -c 'type(value) is not int' chupa/artifacts.py` prints `1`, not `4`; `grep -c 'must be the integer 1' chupa/artifacts.py` prints `2` and `grep -c 'must be integer 1' chupa/artifacts.py` prints `2`, so no message was reworded.
3. `grep -c 'in order' chupa/artifacts.py` prints `1`, not `2`.
4. `./dev.py test` exits 0, including the existing rejection tests named in Scope in / Scope out, which fail if a model accepts a bad `producing_run`, a `True` version, or reordered entries.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any validator error message changes by even one byte;
- a model accepts or rejects an input it did not before;
- a validator is removed from a model or replaced by a mixin, metaclass, shared base-class validator, or decorator factory;
- `ShakeoutEntry`, `HostLoopReport._ordered`, or a file other than `chupa/artifacts.py` changes.

## Time budget
- expected: 15m
- stuck: 45m
