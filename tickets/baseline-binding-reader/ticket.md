---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase5-continue-03
- retro-box-activation

## Context
- chupa/journal.py
- chupa/config.py
- chupa/policy.py
- tests/test_policy.py
- chupa/author.py
- tests/test_author.py
- tests/test_retro_box.py
- chupa/providers.py

## Plan contract
- 19.I
- 19.P5.baseline-binding-reader
- section 12

## Goal / Why
Author uses one fail-closed baseline resolution to authorize the existing starting-state policy.

## Scope in / Scope out
Implement the cited BINDING READER entry. New chupa/baseline.py is owned by 19.P5.baseline-binding-reader; create its entry tests in tests/test_baseline.py. Replace policy.go_binds in place with resolve_baseline(config, events, *, specs_dir) and immutable BaselineResolution; remove the interim reader and migrate its Author and test imports, without an alias or compatibility implementation. Keep policy.baseline_identity, BASELINE_SIGNAL and TIERS for eval/harness.py's identity producer. That producer is unchanged; eval/harness.py is a preservation caller, not a binding reader.

Implement all four closed states, latest complete baseline precedence, binds true only for GO, both surface identities and every recorded tier, existing registry fallback, spec major drift and minor preservation. All invalid identity, routing, spec and event inputs resolve unbound without escaping exceptions. Exercise a real torn journal tail through the existing journal seam. There is no new baseline writer. Author alone passes the resolution's binds to policy.start_state's go operand. Preserve the policy table and all safety-inventory, bypass and reopen overrides in every era; no bootstrap gate or Phase 6 merge hold.

Named obligations: test_baseline_entry_unit, test_baseline_states_and_latest_signal, test_baseline_routing_and_spec_drift, test_baseline_invalid_inputs_fail_closed, test_author_uses_baseline_resolution, test_bootstrap_without_a_go_or_with_phase_one_no_go_drafts_every_row, test_standing_go_uses_the_table_and_each_override_drafts, test_reopened_retro_ticket_starts_draft. test_baseline_entry_unit proves required_units for this seed and phase5-continue-03, exactly one resolve_plan_contract heading and each entry_unit_gap part. test_author_uses_baseline_resolution exercises the production Author path and its handoff under unbound and binding evidence, including each table row. Migrate tests/test_policy.py's go_binds assertions to the sole reader and keep their policy observations. Keep test_reopened_retro_ticket_starts_draft and all retro-box evidence intact.

Author and tests/test_policy.py are the only go_binds readers/imports found across chupa/, eval/ and tests/. The registry floor covers both and all necessary ownership; no addition is earned. Keep public baseline_identity and start_state signatures intact, preserving the eval identity producer. Do not create tests in a future Context or migrate historical seeding fixtures. Leave status, retro/doctor verbs and supervised merge to other rows.

## Scope fence
- chupa/baseline.py
- tests/test_baseline.py
- chupa/journal.py
- chupa/config.py
- chupa/policy.py
- tests/test_policy.py
- chupa/author.py
- tests/test_author.py
- tests/test_retro_box.py

## Acceptance criteria
1. `uv run pytest -q tests/test_baseline.py tests/test_policy.py tests/test_author.py tests/test_retro_box.py` exits 0 proving every named baseline and Author obligation, fail-closed invalid evidence and unchanged policy overrides.
2. `uv run pytest -q tests/test_eval_harness.py` exits 0 retaining the identity producer.
3. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0.

## Verification
```
uv run pytest -q tests/test_baseline.py tests/test_policy.py tests/test_author.py tests/test_retro_box.py
uv run pytest -q tests/test_eval_harness.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed with kind: spec_gap and the owning cited unit; a criteria-forced path outside earned closure needs contract repair.

## Time budget
- expected: 60m
- stuck: 180m
