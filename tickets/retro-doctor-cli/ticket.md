---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase5-continue-04

## Context
- chupa/retro.py
- chupa/__main__.py
- tests/test_retro.py
- tests/test_cli.py
- chupa/runner.py
- chupa/seams.py
- chupa/lockfile.py
- chupa/journal.py
- chupa/config.py

## Plan contract
- 19.I
- 19.P5.retro-doctor-cli
- section 18

## Goal / Why
Operators can force the existing retro machinery and inspect setup through a read-only doctor verb.

## Scope in / Scope out
Implement the registry's VERBS row. New chupa/doctor.py ownership comes from 19.P5.retro-doctor-cli; CLI wiring belongs to chupa/__main__.py. Keep Retro's public signatures and the existing drain composition intact. Use the shared provider session and prepare the pipeline before a selected run needs Pipeline.stages.driver; never dispatch a ticket to obtain a Driver. Invoke Retro(checkout, pipeline) with forced=True under the existing writer lock. Reuse its window projection, commit effect, receipt, recovery, failure suppression and proposals.

Doctor inspects venv, git, config, lock and journal in that order through the existing seams and readers. It must remain usable with invalid config, report dependent failures with repair roads, and inspect a lock without creating it or changing its bytes. Do not use Lockfile.acquire for doctor inspection because it publishes a writer identity. Do not initialize state, repair a torn tail, call providers or prepare a pipeline for doctor. Keep all five output rows after any failed prerequisite.

Create test_retro_doctor_entry_unit in tests/test_cli.py: check required_units for this row and its authoring continuation phase5-continue-04, one resolve_plan_contract heading and every Owner, Records, Observable and Tests part using entry_unit_gap, including missing-part rejection. The terminal phase5-continue-05 cites no non-exit entry and its required_units is empty. test_plan_lint must stay green.

Create test_retro_no_merge, test_retro_success, test_retro_no_commit and test_retro_refusals in tests/test_cli.py. They respectively prove no model/report work with exact no-merge output; forced shared-Driver composition while the real lock is held, a real Git/Effects report commit and completion boundary plus exact success output; failed and suppressed selected runs with exact no-commit output; and lock/config/journal/missing-Driver refusals with repair roads. Check lock release on success, no-commit and every refusal after acquisition.

Create test_doctor_check_order, test_doctor_failures and test_doctor_is_read_only in new tests/test_doctor.py. Cover every failed check, invalid-config dependent checks, empty history, active torn tail, corrupt journal and lock contention; pin exact five-row ordering and continued checking, exit 2 and no traceback. Snapshot repository/state bytes and prove no creation with absent state; forbid providers and pipeline calls. Create test_doctor_cli in tests/test_cli.py to prove the production all-pass composition and exit 0.

Keep every existing tests/test_retro.py assertion unchanged, including recovery, suppression, provenance and proposals. Preserve scorecard, status, baseline and retro-box assertions through unchanged Verification suites. No phase exit, new record schemas, signals, supervision, config knobs or unrelated CLI changes.

## Scope fence
- chupa/doctor.py
- tests/test_doctor.py
- chupa/retro.py
- chupa/__main__.py
- tests/test_retro.py
- tests/test_cli.py

## Acceptance criteria
1. `uv run pytest -q tests/test_cli.py tests/test_doctor.py tests/test_retro.py` exits 0 with all nine named entry obligations and the production retro/doctor behavior above.
2. `uv run pytest -q tests/test_scorecard.py tests/test_status.py tests/test_baseline.py tests/test_retro_box.py tests/test_drain.py tests/test_stages.py` exits 0 preserving their assertions and existing public caller shapes.
3. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0.

## Verification
```
uv run pytest -q tests/test_cli.py tests/test_doctor.py tests/test_retro.py
uv run pytest -q tests/test_scorecard.py tests/test_status.py tests/test_baseline.py tests/test_retro_box.py tests/test_drain.py tests/test_stages.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed with kind: spec_gap and unit 19.P5.retro-doctor-cli. A forced edit outside earned closure requires contract repair.

## Time budget
- expected: 60m
- stuck: 180m
