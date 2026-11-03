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
- chupa/config.py
- chupa/gates.py
- chupa/providers.py
- chupa/seams.py

## On-demand
- chupa/stages.py
- tests/test_merge.py
- tests/test_stages.py

## Plan contract
- 19.I
- 19.P7.host-mechanical-check
- section 7

## Goal / Why
Host mechanical declarations run at Check and at the inline merge re-run, under each entry's own code and configured severity.

## Scope in / Scope out
Realize the complete cited host-mechanical-check entry at the existing Check (`chupa/stages.py`) and inline-merge (`chupa/merge.py`) owners. This is behavioral activation in reachable modules; do not create a production module. Keep daemon mechanical execution tiers in `chupa/mergequeue.py` as they are.

Implement the entry's execution, finding, spool, trigger, severity and base-red attribution behavior. Severity is the entry's configured `severity` only: host check codes are not `gate_bypass` codes, so ticket validation (`chupa/tickets.py`) and every bypass consumer stay unchanged. Reuse the existing subprocess, stream-redaction, child environment, base-worktree and second-problem mechanisms. Test the real production Check and inline admission rather than only a selector helper. Respect path boundaries, including the sibling-name non-match; an untriggered entry leaves no execution evidence. Keep the mechanical no-Box rule and the existing attribution exception for a base-red command. Do not implement host LLM surfaces, change config schema or ticket validation, add a new artifact type, alter daemon execution tiers, change either prompt source, or author tickets.

## Scope fence
- chupa/stages.py
- chupa/merge.py
- tests/test_host_mechanical.py
- tests/test_stages.py
- tests/test_merge.py

## Acceptance criteria
1. `uv run pytest -q tests/test_host_mechanical.py tests/test_stages.py tests/test_merge.py` exits 0 with production Check proofs in tests/test_host_mechanical.py: test_triggered_entries_run_at_check, test_untriggered_entry_never_runs, test_hard_failure_fails_check, test_soft_failure_reported_and_passes and test_base_red_entry_is_preexisting. Cover the boundary and selection cases named by the entry at Check and inline merge, including a prefix chupa/x against chupa/xy.py in the untriggered test. Assert report order and code, absence of untriggered commands/reports/spools/findings, soft findings on the stage result with the stage proceeding, and base attribution without retry charge.
2. `uv run pytest -q tests/test_host_mechanical.py tests/test_stages.py tests/test_merge.py` exits 0 with test_structured_findings_and_crash_fail_closed covering structured stdout, bare nonzero output, timeout and crash; assert the entry's cwd, stuck timeout, redacted captured streams, and provider-key-free child environment. Verify the spool contract at both stages and the absence of mechanical soft-failure Box arrivals.
3. `uv run pytest -q tests/test_host_mechanical.py tests/test_stages.py tests/test_merge.py` exits 0 with test_inline_merge_reruns_triggered_hard_entries exercising inline admission on its rebased candidate. A newly failing hard check refuses admission without moving main; soft and untriggered entries are excluded from the inline hard execution set. Existing tests/test_merge.py and tests/test_stages.py behavior and engine gate order remain green.
4. `uv run pytest -q tests/test_host_mechanical.py tests/test_stages.py tests/test_merge.py` exits 0 with test_host_mechanical_entry_unit recording required_units, uniquely resolved entry text, Owner/Records/Observable/Tests coverage and missing-part refusal. `uv run pytest -q tests/test_tickets.py` exits 0 unchanged, proving ticket validation is untouched. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 with historical seeding fixtures unchanged.

## Verification
```
uv run pytest -q tests/test_host_mechanical.py tests/test_stages.py tests/test_merge.py
uv run pytest -q tests/test_tickets.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
A governing gap stops with premise_failed and its owning entry unit. A forced edit outside the earned fence requires contract repair.

## Time budget
- expected: 60m
- stuck: 90m
