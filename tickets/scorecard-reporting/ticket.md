---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase5-continue-02

## Context
- chupa/retro.py
- tests/test_retro.py

## Plan contract
- 19.I
- 19.P5.scorecard-reporting
- section 14

## Goal / Why
Retro receipts expose journal-derived per-surface catches, bypasses, prune candidates and accounting totals.

## Scope in / Scope out
Implement the cited scorecard entry in full. New chupa/scorecard.py is owned by that entry; chupa/retro.py collects production evidence and renders the receipt through its existing seams. This is behavior added inside the reachable retro module, exercised through the real lock-held production composition, not a dormant construction or a new invoker.

Read the entry's Owner, Records, Observable and Tests. Create tests/test_scorecard.py with these named obligations: test_scorecard_entry_unit, test_scorecard_uses_completed_check_evidence, test_scorecard_catches_resolved_and_upheld_findings, test_scorecard_rates_and_prune_threshold, test_scorecard_totals_and_rendering. test_scorecard_entry_unit exercises required_units, resolve_plan_contract and entry_unit_gap for this seed and a continuation citing its entry. Keep test_plan_lint green unchanged.

Read completed Check evidence from the commit carried by each ticket-plane checks lift completion. Preserve journal and report ordering, fold duplicate completions once, exclude unfinished effects and evidence outside the selected window. The pure projection receives the window's collected observations without performing Git, filesystem or model operations. Exercise actual invoice production and lift commits in disposable repositories with injected seams, plus production report integration. Derive resolved and upheld catches from the existing gate and review durable records; no catch writer or new signal vocabulary. Pin bypassed failures, distinct ticket operands, immutable sorted rows, rates, threshold boundaries, unknown tokens, deterministic totals and empty/populated rendering in the named tests. Escapes remain zero in Phase 5.

Keep every tests/test_retro.py assertion unchanged, especially test_receipt_uses_engine_provenance_usage_calibration_and_tombstones and the JSON receipt readers. Append the engine-rendered scorecard while retaining the existing JSON evidence and receipt fields. Preserve public signatures and constructor arity for project_window, measurements, production_evidence, render_report and Retro; Window construction is local to fenced project_window, so extend its collected evidence there; extend evidence within the existing seam rather than changing external callers. Existing trigger selection, Stages.driver/Pipeline.stages access, exit-window materialization, proposal-to-Box emission and report commit custody remain unchanged. No status, baseline reader, CLI verbs, escape attribution, prompt-spec edits or report hand-commits.

## Scope fence
- chupa/scorecard.py
- tests/test_scorecard.py
- chupa/retro.py
- tests/test_retro.py

## Acceptance criteria
1. `uv run pytest -q tests/test_scorecard.py` exits 0 creating all named entry tests, proving entry depth, real completed-invoice evidence, resolved/upheld findings, distinct catches, bypasses, rates, 24/25 pruning, immutable sorted rows and Phase 5 zero escapes.
2. `uv run pytest -q tests/test_scorecard.py tests/test_retro.py` exits 0 proving write-free projection and deterministic production report integration while every predecessor assertion remains unchanged.
3. `uv run pytest -q tests/test_driver.py tests/test_stages.py tests/test_retro_box.py tests/test_vocabularies.py` exits 0 preserving callers, exit-window selection, Box bridge and closed signals; `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0.

## Verification
```
uv run pytest -q tests/test_scorecard.py
uv run pytest -q tests/test_scorecard.py tests/test_retro.py
uv run pytest -q tests/test_driver.py tests/test_stages.py tests/test_retro_box.py tests/test_vocabularies.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
An absent or conflicting entry fact returns premise_failed, kind: spec_gap, unit: 19.P5.scorecard-reporting. A required edit outside this fence returns premise_failed for contract repair. Never migrate historical seeding fixtures.

## Time budget
- expected: 60m
- stuck: 180m
