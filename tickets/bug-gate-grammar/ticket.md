---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase6-continue-03
- fixture-host-scaffold

## Context
- chupa/tickets.py
- chupa/gates.py
- chupa/stages.py
- tests/test_tickets.py
- tests/test_gates.py
- tests/test_mergequeue.py
- chupa/merge.py
- chupa/mergequeue.py
- chupa/git.py
- chupa/seams.py
- hosts/fixture/scaffold.py
- hosts/fixture/regression_test.py

## On-demand
- tests/test_serve.py

## Plan contract
- 19.I
- 19.P6.bug-gate-grammar
- section 7
- section 13

## Goal / Why
Require durable defect evidence at Check and both merge admissions for regression bug tickets.

## Scope in / Scope out
Implement the cited regression contract in the existing ticket parser and shared stage collector/gates. Keep public signatures intact. Both merge owners already call gather_evidence and CHECK_GATES; register BugEvidenceGate there so their existing wiring collects and gates fresh candidate evidence. Check alone persists its report. The metadata-only queue pass remains metadata-only. Read both merge owners before changing the shared collector.

The new tests/test_bug_gate.py owns the regression proofs. Under 19.L rule 2, update tests/test_mergequeue.py::test_strategy_resolution_still_regates and tests/test_serve.py::test_serve_conflict_handoff_runs_after_admission_unwinds: both pin the exact integration gate sequence, which gains bug_evidence even for non-bugs. Non-bugs pass the new gate without executing regression. Read tests/test_serve.py On-demand before editing; its embedding exceeds authoring headroom as recorded by the seeding test. Existing merge owners are references, not write targets.

No new module, git operation, bypass, signal, frontmatter field or outcome; no inbox, escape attribution, host-loop producer, prompt-spec edits or historical fixture changes. Use existing process, Git, environment and scrubbed spool seams.

## Scope fence
- chupa/tickets.py
- chupa/gates.py
- chupa/stages.py
- tests/test_tickets.py
- tests/test_gates.py
- tests/test_bug_gate.py
- tests/test_mergequeue.py
- tests/test_serve.py

## Acceptance criteria
1. `uv run pytest -q tests/test_bug_gate.py` exits 0 with test_bug_gate_entry_units using required_units, resolve_plan_contract and entry_unit_gap for unique resolution, four parts and missing-part rejection.
2. `uv run pytest -q tests/test_tickets.py` preserves test_bug_ticket_with_regression_validates and test_grammar_refusals and covers empty/multiple regression commands, absent carries and non-bug regression refusal using the existing closed grammar.
3. `uv run pytest -q tests/test_bug_gate.py` proves test_regression_overlay_proves_defect with a newly added test copied to base; test_passing_new_test_is_not_bug_evidence refuses green/green, and test_missing_base_input_is_not_bug_evidence refuses missing-input failures.
4. `uv run pytest -q tests/test_bug_gate.py` proves durable custody in test_bug_gate_requires_evidence, red-head refusal in test_bug_gate_rejects_red_head, changed-path matching, traversal and implementation-fix exclusion in test_bug_gate_refuses_invalid_carries, and closed spawn/timeout failure in test_bug_gate_execution_failure_is_closed.
5. `uv run pytest -q tests/test_bug_gate.py` proves production Check's hard report and non-bug no-execution behavior in test_bug_gate_check_wiring. test_bug_gate_base_cleanup proves seam use, scrubbed stage spools, child environment, unchanged source/branch and detached worktree removal/prune on success and failure.
6. `uv run pytest -q tests/test_bug_gate.py` proves test_bug_gate_merge_wiring exercises inline merge and queue integration through shared CHECK_GATES: each freshly executes regression, refuses red head or green overlaid base before main moves despite passing Check evidence, passes valid evidence, and executes no regression for non-bugs. test_bug_gate_merge_rebase_regates covers the current candidate/base after rebase or conflict resolution. test_bug_gate_merge_report_custody proves neither merge consumes or rewrites Check's checks.json, and both apply hard severity and the existing ticket bypass.
7. `uv run pytest -q tests/test_mergequeue.py tests/test_serve.py` updates test_strategy_resolution_still_regates and test_serve_conflict_handoff_runs_after_admission_unwinds to include bug_evidence in integration, keeping the metadata-only safety sequence unchanged.
8. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving unrelated behavior and immutable seeding fixtures.

## Verification
```
uv run pytest -q tests/test_bug_gate.py tests/test_tickets.py tests/test_gates.py
uv run pytest -q tests/test_mergequeue.py tests/test_serve.py
uv run pytest -q tests/test_stages.py tests/test_merge.py tests/test_git.py tests/test_fixture_host.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed with kind: spec_gap and the owning unit. A forced edit beyond earned closure needs plan repair.

## Time budget
- expected: 60m
- stuck: 90m
