---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase7-continue
- review-spec-readonly
- implement-consumer-read

## Context
- chupa/merge.py
- chupa/tickets.py
- tests/test_tickets.py
- chupa/mergequeue.py
- chupa/daemon.py
- chupa/watcher.py
- chupa/author.py
- chupa/rework.py
- chupa/requisition.py
- chupa/__main__.py
- chupa/serve.py
- tests/test_rework.py
- chupa/config.py
- chupa/gates.py
- chupa/seams.py

## On-demand
- eval/reliability_battery.py
- chupa/stages.py
- tests/test_merge.py
- tests/test_stages.py
- chupa/runner.py
- chupa/drain.py

## Plan contract
- 19.I
- 19.P7.host-mechanical-check
- section 7

## Goal / Why
Host mechanical declarations govern Check and inline admission with active-config bypass validation.

## Scope in / Scope out
Realize the complete cited host-mechanical-check entry at the existing Check and inline-merge owners. This is behavioral activation in reachable modules; do not create a production module. Keep daemon mechanical execution tiers as they are; changes there are only for validation's configuration input.

Thread the active configuration explicitly into ticket validation: add a keyword-only mechanical_codes collection to parse_ticket and validate_ticket and forward it through intake and requisition review_target/review_ticket. The empty default means validation with only the engine code vocabulary, a useful component-validation input; callers operating on configured host tickets must supply the codes from their active Config or ConfigSnapshot. Use the collection as Pydantic validation context for GateBypass instead of loading a config from the repository or accepting arbitrary strings. Keep code and reason nonblank. Update all fenced production validation callers, including temporary author/rework trees, retained tickets, schema and seed merge gates, confirmation, watcher and scans. Give Watcher an injectable code-reader callback so its existing production load callback supplies the currently active configuration. Configure merge schema/seed gates from the admission context; keep engine gate order. Refresh through the existing active-config loaders at rescan boundaries. Propagate the same codes to every nested validation, including per-seed feasibility review. Isolate simultaneous validators using their explicit inputs; no process-global code registry or ambient context.

The unchanged historical callers validate engine-only fixture tickets and require no new argument. Preserve those files and all historical snapshots; the optional empty collection describes that validation policy rather than a second implementation. Fence and migrate tests/test_rework.py's keyword-rejecting validation wrapper. No production validation of configured host work may rely on the empty default. The admission snapshot records this consumer-preserving interpretation of caller closure, following the plan's distinction between forced production callers and unchanged component callers.

Implement the entry's execution, finding, spool, trigger, effective severity and attribution behavior. Reuse the existing subprocess, stream-redaction, child environment, base-worktree and second-problem mechanisms. Test the real production Check and inline admission rather than only a selector helper. Respect path boundaries, including the sibling-name non-match; an untriggered entry leaves no execution evidence. Keep the mechanical no-Box rule and the existing attribution exception for a base-red command. Do not implement host LLM surfaces, change config schema, add a new artifact type, alter daemon execution tiers, change either prompt source, or author tickets.

## Scope fence
- chupa/stages.py
- chupa/merge.py
- tests/test_host_mechanical.py
- tests/test_stages.py
- tests/test_merge.py
- chupa/tickets.py
- tests/test_tickets.py
- chupa/runner.py
- chupa/mergequeue.py
- chupa/daemon.py
- chupa/watcher.py
- chupa/drain.py
- chupa/author.py
- chupa/rework.py
- chupa/requisition.py
- chupa/__main__.py
- chupa/serve.py
- eval/reliability_battery.py
- tests/test_rework.py

## Acceptance criteria
1. `uv run pytest -q tests/test_host_mechanical.py tests/test_tickets.py tests/test_stages.py tests/test_merge.py tests/test_rework.py` exits 0 with production Check proofs in tests/test_host_mechanical.py: test_triggered_entries_run_at_check, test_untriggered_entry_never_runs, test_trigger_matches_scope_path_boundaries, test_hard_failure_fails_check, test_soft_failure_reported_and_passes, test_gate_bypass_demotes_entry and test_base_red_entry_is_preexisting. Cover all boundary and selection cases named by the entry at Check and inline merge, including a prefix chupa/x against chupa/xy.py in the untriggered test. Assert report order and code, absence of untriggered commands/reports/spools/findings, soft findings and progress, bypass from a validated ticket, and base attribution without retry charge.
2. `uv run pytest -q tests/test_host_mechanical.py tests/test_tickets.py tests/test_stages.py tests/test_merge.py tests/test_rework.py` exits 0 with test_structured_findings_and_crash_fail_closed covering structured stdout, bare nonzero output, timeout and crash; assert the entry's cwd, stuck timeout, redacted captured streams, and provider-key-free child environment. Verify the existing spool contract at both stages and the absence of mechanical soft-failure Box arrivals.
3. `uv run pytest -q tests/test_host_mechanical.py tests/test_tickets.py tests/test_stages.py tests/test_merge.py tests/test_rework.py` exits 0 with test_inline_merge_reruns_triggered_hard_entries and test_inline_merge_excludes_bypassed_entry exercising inline admission on its rebased candidate. A newly failing hard check refuses admission without moving main; soft, untriggered and demoted entries are excluded from the inline hard execution set. Existing tests/test_merge.py and tests/test_stages.py behavior and engine gate order remain green.
4. `uv run pytest -q tests/test_host_mechanical.py tests/test_tickets.py tests/test_stages.py tests/test_merge.py tests/test_rework.py` exits 0 with tests/test_tickets.py::test_gate_bypass_accepts_declared_host_mechanical_code, test_gate_bypass_rejects_undeclared_code and test_gate_bypass_preserves_engine_codes_and_nonblank_reason. In tests/test_host_mechanical.py add test_active_config_codes_reach_production_validation: select a --config file outside the repo with a host code absent from repo/config.yaml, and a repo-only code absent from that active file. Drive the real CLI intake/dispatch and production validation to accept only the active file's declared code. Exercise Author, Rework, requisition, seed Check, watcher, drain/serve rescans, retained-ticket and merge-schema validation with the same policy through their production entry points, retaining closed engine codes. test_validation_code_sets_are_isolated proves two explicitly configured validators cannot accept each other's codes. Preserve nonblank code/reason validation and engine-only component callers, including historical snapshots. Update the tests/test_rework.py forwarding wrapper without weakening its custody assertions.
5. `uv run pytest -q tests/test_host_mechanical.py tests/test_tickets.py tests/test_stages.py tests/test_merge.py tests/test_rework.py` exits 0 with test_host_mechanical_entry_unit recording required_units, uniquely resolved entry text, Owner/Records/Observable/Tests coverage and missing-part refusal. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 with historical seeding fixtures unchanged.

## Verification
```
uv run pytest -q tests/test_host_mechanical.py tests/test_tickets.py tests/test_stages.py tests/test_merge.py tests/test_rework.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A governing gap stops with premise_failed and its owning entry unit. A forced edit outside the earned fence requires contract repair.

## Time budget
- expected: 60m
- stuck: 90m
