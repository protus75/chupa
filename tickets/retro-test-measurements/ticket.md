---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- retro-trigger-toggles
- check-test-timing

## Context
- chupa/config.py
- chupa/retro.py::production_evidence
- chupa/retro.py::render_report
- chupa/gates.py::GateReport
- chupa/stages.py::Invoice
- tests/integration/test_retro.py::test_retro_trigger_boundaries
- tests/integration/test_config.py::test_retro_yaml_values
- docs/how-chupa-works.md#9.5 Retro

## On-demand
- docs/host-contract.md

## Goal / Why
After `check-test-timing`, every `checks.json` holds per-entry test timing and coverage, but the retro reads only gate codes and verdicts from it. The retro model cannot see slow suites, slow tests or low-coverage files, so it cannot propose test repairs (2026-11-08). After this change the retro measurements carry a test-timing summary and a coverage summary aggregated over the window's Check invoices. Each summary can be switched off in `config.yaml`.

## Scope in / Scope out
- In: `chupa/config.py` `Retro` gains `test_timing: bool = True` and `coverage: bool = True`.
- In: `chupa/retro.py` `production_evidence`, over every completed Check invoice it already loads in the window, in journal order:
  - When `checkout.config.retro.test_timing` is true, `evidence["tests"]` maps each gate code that has `timing` to:
    - `runs`: a list of `{ticket, seconds, passed, failed, skipped}`, one per invoice;
    - `slow`: `{nodeid: {max_seconds, runs}}`, where `runs` counts the invoices that listed the test.
  - When `checkout.config.retro.coverage` is true, `evidence["coverage"]` maps each gate code that has `coverage` to:
    - `percent`: the repository percent from the last invoice in journal order;
    - `files`: `{path: {latest, min, runs}}`.
  - When a switch is false, its key is absent from the evidence, not present and empty.
  - `render_report` needs no change: both keys appear inside `measurements`.
- In: tests in `tests/integration/test_retro.py`, publishing Check invoices the way `test_retro_trigger_boundaries` does for `override`:
  - `test_test_timing_aggregates_invoices`: two invoices list `tests/a.py::t` at 2.0s and 5.0s, so `slow` reports `max_seconds: 5.0` and `runs: 2`, not the last value or a sum. `runs` has one row per invoice.
  - `test_coverage_aggregates_invoices`: a file at 80.0 and then 60.0 reports `latest: 60.0` and `min: 60.0`, and `percent` is the later invoice's.
  - `test_measurement_switches`: with `test_timing: false` and `coverage: false`, neither `tests` nor `coverage` is in the evidence.
- In: `tests/integration/test_config.py`: the `retro` defaults include both switches, and a YAML value of `false` for each loads.
- In: docs.
  - `docs/host-contract.md`: the `Retro` row and the `Config.defaults.retro` object gain both switches.
  - `docs/how-chupa-works.md` section 9.5 describes both summaries and their switches; section 11's `retro` row names them.
- Out: the retro prompt, proposal shape, Check recording, spike kinds, triggers.

## Scope fence
- chupa/config.py
- chupa/retro.py
- tests/integration/test_retro.py
- tests/integration/test_config.py
- docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_retro.py` exits 0, including `test_test_timing_aggregates_invoices`, `test_coverage_aggregates_invoices` and `test_measurement_switches`. These rule out a last-value or summed `max_seconds`, a `min` that ignores earlier invoices, and an empty key left present when a switch is off.
2. `./dev.py test tests/integration/test_config.py tests/integration/test_host_contract.py` exits 0.
3. `docs/how-chupa-works.md` section 9.5 names `test_timing` and `coverage`.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_retro.py
./dev.py test tests/integration/test_config.py tests/integration/test_host_contract.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the retro reruns tests or reads a coverage file from disk instead of the committed `checks.json`;
- a switch set to false still sends its summary to the model;
- an invoice without `timing` or `coverage` fails the retro.

## Time budget
- expected: 45m
- stuck: 120m
