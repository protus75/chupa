---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase6-continue-06
- go-grade-machinery

## Context
- eval/harness.py
- chupa/artifacts.py
- chupa/stages.py

## Plan contract
- 19.I
- 19.P6.go-grade-run
- 19.P6.go-grade-machinery

## Goal / Why
Produce fresh measured GO-grade baseline evidence through the merged report lane.

## Scope in / Scope out
Invoke the merged harness after the machinery sibling merges. This row owns no code, schema, registration or test. Generate the named review-baseline-report.json in this stem's OUTBOX using the harness canonical writer; do not pass --record-go. An ordinary measured complete or cap-limited partial NO_GO report is valid output. An already_satisfied claim cannot replace fresh Check production.

Leave the report uncommitted: never patch, copy or Git-add evidence. Check removes inherited/Implement outputs before Verification, validates fresh named output, and lifts it only via ticket-plane/go-grade-run/<attempt>/checks. Empty code admission then records one null-commit merged terminal and retires once. Use existing report custody and failure machinery; no host cutover or live soak.

## Scope fence
- tickets/go-grade-run/review-baseline-report.json

## Acceptance criteria
1. `uv run pytest tests/test_eval_harness.py tests/test_go_grade.py tests/test_stages.py tests/test_merge.py` preserves test_go_grade_scoring_and_partial_report, test_record_go_requires_complete_floors_identity_and_operator_judgment, test_review_baseline_report_closed_schema and test_review_baseline_report_registered_checks_lift.
2. `uv run pytest tests/test_eval_harness.py tests/test_go_grade.py tests/test_stages.py tests/test_merge.py` preserves test_outbox_only_check_requires_current_report, test_outbox_only_merge_regate_requires_lift_custody and test_outbox_only_admission_records_null_commit_and_retires.
3. `uv run python -m eval.harness run --out tickets/go-grade-run/review-baseline-report.json` exits 0 with fresh validated report bytes, measured results and actual embedded verdict-signal identity. Both complete and partial NO_GO settle; incomplete evidence never records GO.
4. `tickets/go-grade-run/review-baseline-report.json` stays uncommitted for Check; missing/invalid output or failed Verification/lift cannot settle, and the successful lane has an empty code diff, one merged terminal with commit: null and one retirement.

## Verification
```
uv run pytest tests/test_eval_harness.py tests/test_go_grade.py tests/test_stages.py tests/test_merge.py
uv run python -m eval.harness run --out tickets/go-grade-run/review-baseline-report.json
```

## Definition of rejected
Missing or contradictory governing entry facts return premise_failed, kind: spec_gap naming the owning unit. A criteria-forced path beyond earned closure requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
