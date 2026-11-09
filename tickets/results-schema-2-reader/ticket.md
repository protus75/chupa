---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- chupa/testreport.py::read_results
- chupa/stages.py::_check_host_results
- tests/integration/test_testreport.py
- docs/how-chupa-works.md#12. Host projects
- docs/host-contract.md

## Goal / Why
Check reads a candidate's `results` file with the running engine's `read_results`, which is main's code, not the candidate's. `check-test-timing` changes the writer to schema 2 and refuses schema 1 in one change, so main's schema-1-only reader rejects its results and it can never pass Check (2026-11-08, attempts 1 and 2). After this change `read_results` also accepts schema 2, so the writer change can land next. The writer stays on schema 1. Accepting both versions is deliberate and lasts one merge: `check-test-timing` drops schema 1.

## Scope in / Scope out
- In: `chupa/testreport.py` `read_results` accepts `schema_version` 1 with exactly the keys `{schema_version, tests}`, or `schema_version` 2 with exactly `{schema_version, tests, seconds}`. For schema 2, `seconds` must be an object whose keys equal the `tests` keys, each value a finite float `>= 0` (not a bool). It still returns the `tests` dict for both. Any other version is refused.
- In: `tests/integration/test_testreport.py`:
  - A valid schema-2 document returns its `tests` dict.
  - `{"schema_version": 2, "tests": {}}` moves from the invalid cases to a schema-2-without-`seconds` refusal.
  - Schema 2 refusals: `seconds` keys differ from `tests` keys, a negative value, `NaN`, a bool, and `schema_version: 3`.
- In: `tests/unit/test_testreport_reader.py` unit-tests every `read_results` branch: valid schema 1, valid schema 2, schema 2 without `seconds`, `seconds` keys that differ from `tests` keys, negative, `NaN` and bool values, and `schema_version` 3. The writer stays on schema 1.
- In: `docs/how-chupa-works.md` section 12 `chupa.testreport` bullet and `docs/host-contract.md` `results` paragraph say the reader accepts schema 1 and 2, and that the plugin writes schema 1.
- Out: the writer (`pytest_sessionfinish`), the `read_results` return type, every caller in `chupa/stages.py`, timing and coverage recording (all `check-test-timing`).

## Scope fence
- chupa/testreport.py
- tests/integration/test_testreport.py
- tests/unit/test_testreport_reader.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_testreport.py` exits 0; it fails if a valid schema-2 document is refused or if a mismatched, negative, `NaN` or bool `seconds` value is accepted.
2. The plugin still writes `schema_version: 1`; `test_reports_all_phases_and_nodeids` is unchanged and passes.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_testreport.py
./dev.py test tests/unit/test_testreport_reader.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the writer emits schema 2;
- `read_results` returns anything other than the `tests` dict;
- a schema-2 document with mismatched or invalid `seconds` is accepted.

## Time budget
- expected: 20m
- stuck: 60m
