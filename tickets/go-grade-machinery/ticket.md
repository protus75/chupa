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
- supervised-merge-hold
- fixture-host-scaffold

## Context
- eval/fixtures/clean-dedupe-emails/expected.json
- eval/fixtures/clean-health-endpoint/expected.json
- eval/fixtures/clean-retry-config/expected.json
- eval/fixtures/clean-word-count/expected.json
- eval/fixtures/logic-cache-expiry/expected.json
- eval/fixtures/scope-extra-flag/expected.json
- eval/fixtures/logic-date-range/expected.json
- eval/fixtures/accept-csv-export/expected.json
- eval/fixtures/scope-refactor/expected.json
- eval/fixtures/scope-other-module/expected.json
- eval/fixtures/leak-log-token/expected.json
- eval/fixtures/accept-config-precedence/expected.json
- eval/fixtures/leak-error-message/expected.json
- eval/fixtures/leak-grader-answers/expected.json
- eval/fixtures/accept-password-policy/expected.json
- eval/fixtures/logic-retry-backoff/expected.json
- eval/fixtures/accept-slugify/expected.json
- eval/fixtures/leak-user-serializer/expected.json
- eval/fixtures/logic-pagination/expected.json
- eval/fixtures/scope-bump-deps/expected.json
- eval/fixtures/logic-rate-limiter/expected.json
- eval/fixtures/leak-child-env/expected.json
- eval/fixtures/scope-bump-deps/ticket.md
- eval/fixtures/scope-refactor/ticket.md
- eval/fixtures/clean-word-count/ticket.md
- eval/fixtures/scope-extra-flag/ticket.md
- eval/fixtures/clean-retry-config/ticket.md
- eval/fixtures/leak-log-token/ticket.md
- eval/fixtures/clean-dedupe-emails/ticket.md
- eval/fixtures/logic-date-range/ticket.md
- eval/fixtures/accept-slugify/ticket.md
- eval/fixtures/leak-user-serializer/ticket.md
- eval/fixtures/accept-password-policy/ticket.md
- eval/fixtures/logic-cache-expiry/ticket.md
- eval/fixtures/logic-retry-backoff/ticket.md
- eval/fixtures/scope-other-module/ticket.md
- eval/fixtures/clean-health-endpoint/ticket.md
- eval/fixtures/leak-error-message/ticket.md
- eval/fixtures/leak-grader-answers/ticket.md
- eval/fixtures/accept-csv-export/ticket.md
- eval/fixtures/logic-pagination/ticket.md
- eval/fixtures/accept-config-precedence/ticket.md
- eval/fixtures/logic-rate-limiter/ticket.md
- eval/fixtures/clean-word-count/diff.patch
- eval/fixtures/leak-child-env/ticket.md
- eval/fixtures/accept-slugify/diff.patch
- eval/fixtures/scope-bump-deps/diff.patch
- eval/fixtures/clean-dedupe-emails/diff.patch
- eval/fixtures/scope-other-module/diff.patch
- eval/fixtures/scope-refactor/diff.patch
- eval/fixtures/leak-error-message/diff.patch
- eval/fixtures/accept-password-policy/diff.patch
- eval/fixtures/logic-date-range/diff.patch
- eval/fixtures/clean-health-endpoint/diff.patch
- eval/fixtures/leak-grader-answers/diff.patch
- eval/fixtures/logic-cache-expiry/diff.patch
- eval/fixtures/logic-pagination/diff.patch
- eval/fixtures/leak-child-env/diff.patch
- eval/fixtures/leak-user-serializer/diff.patch
- chupa/llm.py
- eval/fixtures/clean-retry-config/diff.patch
- eval/fixtures/accept-config-precedence/diff.patch
- eval/fixtures/logic-retry-backoff/diff.patch
- eval/fixtures/logic-rate-limiter/diff.patch
- eval/fixtures/scope-extra-flag/diff.patch
- eval/fixtures/accept-csv-export/diff.patch
- eval/fixtures/leak-log-token/diff.patch
- tests/test_eval_harness.py
- chupa/requisition.py
- chupa/artifacts.py
- tests/test_fixture_host.py
- tests/test_driver.py
- eval/harness.py
- chupa/driver.py
- chupa/providers.py

## On-demand
- tests/test_stages.py
- tests/test_providers.py
- chupa/stages.py

## Plan contract
- 19.I
- 19.P6.go-grade-machinery
- section 12
- section 13

## Goal / Why
Build bounded baseline evaluation and a validated report lane for the later producer.

## Scope in / Scope out
Extend the existing owners named by the entry: eval/harness.py owns fixture loading, scoring, the local Author-graph runner, canonical writer and operator mode; chupa/artifacts.py owns the closed report schema, chupa/stages.py its registration and checks custody, chupa/llm.py the request budget and chupa/providers.py adapter enforcement. No new module or production Author prompt is introduced.

Preserve the committed 22 review fixtures and their directory format byte-for-byte, including actual author identities. Keep the loader floors at 15 planted and 3 clean. Use separate 50-planted/15-clean completeness requirements; this smaller corpus is loadable measured partial NO_GO, even when its calls and graph finish. Corpus growth and any format migration belong to later operator-authored upkeep tickets, outside this admission. Scripted authored cases stay disposable and take identity from their actual call and journal/spools; never invent measured fixtures or author provenance.

Implement the cited unit's request ceiling, shared run cap, graph validation, closed report and operator GO rules. Driver.run supplies remaining ceilings on eval retries; ordinary LLMRequest callers in review_ticket and the direct driver/fixture tests retain null budgets. Preserve run_baseline's existing parameter and score surfaces for unchanged watchdog callers. Harness-local graph problems are owned by eval/fixtures/; no production Author invocation or emitted tickets. Ordinary report production records NO_GO; machinery builds and tests its writer and registration but leaves baseline evidence to go-grade-run after merge. Keep the existing injectable seams, scoring, provider accounting and journal custody.

## Scope fence
- eval/harness.py
- eval/fixtures/
- chupa/artifacts.py
- chupa/stages.py
- chupa/llm.py
- chupa/providers.py
- tests/test_eval_harness.py
- tests/test_stages.py
- tests/test_providers.py
- tests/test_go_grade.py
- chupa/driver.py
- chupa/requisition.py
- tests/test_driver.py
- tests/test_fixture_host.py

## Acceptance criteria
1. `uv run pytest -q tests/test_go_grade.py` passes with `tests/test_go_grade.py::test_go_grade_entry_units` covering required_units, unique resolve_plan_contract and all four entry_unit_gap parts.
2. `uv run pytest -q tests/test_eval_harness.py` passes with `tests/test_eval_harness.py::test_go_grade_fixture_floors_and_author_separation` covering 15 planted/3 clean loader floors, separate 50 planted/15 clean completeness boundary, every class, malformed fixtures and author separation.
3. `uv run pytest -q tests/test_eval_harness.py` passes with `tests/test_eval_harness.py::test_go_grade_existing_corpus_is_partial_no_go` covering unchanged committed 18-planted/4-clean corpus produces valid partial NO_GO even with all verdicts and the graph complete.
4. `uv run pytest -q tests/test_eval_harness.py` passes with `tests/test_eval_harness.py::test_go_grade_fixture_author_identity_comes_from_call` covering scripted author provider/model/tier, existing journal/spool provenance and reviewer refusal; generated cases stay disposable.
5. `uv run pytest -q tests/test_watchdog_activation.py` passes with `tests/test_watchdog_activation.py::test_eval_owned_budgets_preserve_synthetic_identities` covering preserve synthetic identities and eval-owned budgets unchanged.
6. `uv run pytest -q tests/test_eval_harness.py` passes with `tests/test_eval_harness.py::test_go_grade_scoring_and_partial_report` covering caught and missed defects, false snags, absent verdicts, consistent totals, complete reports and cap-limited partial NO_GO.
7. `uv run pytest -q tests/test_eval_harness.py` passes with `tests/test_eval_harness.py::test_go_grade_shared_cap_includes_retries_and_author_graph` covering remaining USD 5.00 on every review, retry and graph call, with no spawn after exhaustion.
8. `uv run pytest -q tests/test_eval_harness.py` passes with `tests/test_eval_harness.py::test_go_grade_author_graph_uses_local_prompt` covering committed problems, resolving acyclic graph, no production Author prompt and no ticket emission.
9. `uv run pytest -q tests/test_providers.py` passes with `tests/test_providers.py::test_eval_budget_ceiling_before_spawn` covering cost-reporting ceilings in argv, estimated-cost refusal before spawn and unchanged null-budget calls.
10. `uv run pytest -q tests/test_go_grade.py` passes with `tests/test_go_grade.py::test_record_go_requires_complete_floors_identity_and_operator_judgment` covering exact 0.85/0.15 boundaries, partial/inconsistent reports, identity drift, rejected graph judgment, no-write refusal and actual matching signal identity.
11. `uv run pytest -q tests/test_go_grade.py` passes with `tests/test_go_grade.py::test_review_baseline_report_closed_schema` covering extra fields, malformed records, inconsistent scores and signal, and partial GO refusal.
12. `uv run pytest -q tests/test_stages.py` passes with `tests/test_stages.py::test_review_baseline_report_registered_checks_lift` covering canonical writer, purge before Verification, required named report, validation, sole checks custody and no machinery self-lift.

## Verification
```
uv run pytest -q tests/test_go_grade.py
uv run pytest -q tests/test_eval_harness.py
uv run pytest -q tests/test_watchdog_activation.py
uv run pytest -q tests/test_providers.py
uv run pytest -q tests/test_stages.py
uv run pytest -q tests/test_driver.py tests/test_fixture_host.py
uv run pytest -q tests/test_baseline.py tests/test_merge.py tests/test_seed_path.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed, kind: spec_gap naming the owning unit. A forced edit beyond earned closure requires plan repair.

## Time budget
- expected: 60m
- stuck: 90m
