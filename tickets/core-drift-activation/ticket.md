---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase6-continue
- core-drift-classifier

## Context
- chupa/mergequeue.py
- chupa/seams.py
- chupa/stages.py
- tests/test_drain.py
- tests/test_mergequeue.py
- tests/test_merge.py
- tests/test_gates.py

## On-demand
- chupa/hostfiles.py
- chupa/gates.py
- chupa/config.py
- chupa/merge.py
- chupa/providers.py
- chupa/__main__.py
- tests/test_hostfiles.py
- tests/test_providers.py
- tests/test_cli.py
- CLAUDE.md
- AGENTS.md
- tests/test_stages.py
- tests/test_seed_path.py
- tests/test_terminal.py
- tests/test_seed_successor.py
- tests/test_daemon_soak.py
- eval/daemon_soak.py
- eval/reliability_battery.py
- eval/shakeout/bench.py

## Plan contract
- 19.I
- 19.P6.core-drift-activation
- 19.P6.core-renderer
- 19.P6.core-drift-classifier
- section 7
- section 8

## Goal / Why
Check and both merge paths reject noncurrent routed conduct before main moves, with chupa's own conduct adopted in the activation candidate.

## Scope in / Scope out
Implement the cited activation contract. chupa/hostfiles.py owns the gate and chupa/providers.py owns the shared resolver; replace core's inline selection using the existing candidate resolution. Activate the existing core_drift code in stages.CHECK_GATES and the merge rerun composition with the shipped hard default and ordinary severity/bypass semantics. No new module, config key, signal or record belongs here. Keep callable signatures intact unless a criteria-forced change has its complete caller closure within this fence.

Replace test_core_classifier_unreachable_from_production_gates with the named reachable test through the real production graph. Retain renderer marker refusal, first adoption, exact project-byte retention, branch-template authority and idempotence. Read every On-demand path before edits. Mechanically render both self-host conduct files using this candidate's engine template and their complete original remainder, then commit them with the activation wiring; gate evaluation itself never writes. Do not hand-edit managed blocks or defer adoption to the migration or documentation siblings.

The hard flip also invalidates independently constructed test and eval hosts. Update the fenced repo constructors to commit conduct mechanically rendered with hostfiles.render from their own fixture bytes for their actual routes, before Check/merge. Builders in test_stages, test_seed_path, test_drain, test_merge, test_cli, test_mergequeue, test_terminal, test_seed_successor and the eval harnesses own that repair; test_daemon_soak also changes routes after its imported builder. Follow the import/composition closure without changing downstream preservation assertions. Do not soften core_drift in fake CONFIG, bypass it, or rewrite historical seeding snapshots. No migration implementation, new provider adapter or host-loop machinery belongs here.

## Scope fence
- chupa/hostfiles.py
- chupa/gates.py
- chupa/config.py
- chupa/merge.py
- chupa/providers.py
- chupa/__main__.py
- tests/test_hostfiles.py
- tests/test_gates.py
- tests/test_merge.py
- tests/test_providers.py
- tests/test_cli.py
- CLAUDE.md
- AGENTS.md
- chupa/stages.py
- tests/test_stages.py
- tests/test_seed_path.py
- tests/test_drain.py
- tests/test_mergequeue.py
- tests/test_terminal.py
- tests/test_seed_successor.py
- tests/test_daemon_soak.py
- eval/daemon_soak.py
- eval/reliability_battery.py
- eval/shakeout/bench.py

## Acceptance criteria
1. `uv run pytest -q tests/test_hostfiles.py tests/test_gates.py tests/test_merge.py tests/test_providers.py tests/test_cli.py` exits 0 with test_core_activation_entry_unit proving required_units, unique resolve_plan_contract and all entry_unit_gap parts with missing-part rejection. test_core_drift_reachable_from_production_gates replaces the dormancy assertion through production Check and both merge paths.
2. `uv run pytest -q tests/test_hostfiles.py tests/test_gates.py tests/test_merge.py tests/test_providers.py tests/test_cli.py` exits 0 with test_core_drift_gate_reports proving every classification, exact report shape, named paths, useful roads, corruption/process refusal and effect-free evaluation; test_core_drift_default_hard pins existing vocabulary and severity/bypass behavior. Missing or stale blocks name chupa core; marker and process refusals give their specific repair actions.
3. `uv run pytest -q tests/test_hostfiles.py tests/test_gates.py tests/test_merge.py tests/test_providers.py tests/test_cli.py` exits 0 with test_core_drift_merge_rerun refusing stale committed bytes before main mutation, including after rebase, and admitting current bytes; test_core_drift_candidate_template uses the candidate template rather than the serving instance.
4. `uv run pytest -q tests/test_hostfiles.py tests/test_gates.py tests/test_merge.py tests/test_providers.py tests/test_cli.py` exits 0 with test_routed_conduct_paths covering claude, other CLI, mixed, duplicate and unrouted candidates. test_core_and_gate_share_routed_paths proves the CLI and gate use one resolver while preserving refusal, project bytes and repeated-render identity.
5. `uv run pytest -q tests/test_hostfiles.py tests/test_gates.py tests/test_merge.py tests/test_providers.py tests/test_cli.py` exits 0 with test_core_activation_first_adoption proving original marker-free claude/codex bytes are missing, rendered bytes are current, every project byte survives and a repeat render is identical. test_core_activation_committed_conduct reads both committed routed files and validated config and passes the real Check gate against the candidate template.
6. `uv run pytest -q tests/test_hostfiles.py tests/test_gates.py tests/test_merge.py tests/test_providers.py tests/test_cli.py` exits 0 with test_core_activation_first_adoption_merge proving inline and queued admission of the adopted activation candidate and a subsequent ordinary candidate without conduct edits, while omission of either routed conduct fails before main moves. Both CLAUDE.md and AGENTS.md in the committed activation candidate classify current without operator repair.
7. `uv run pytest -q tests/test_stages.py tests/test_seed_path.py tests/test_drain.py tests/test_mergequeue.py tests/test_terminal.py tests/test_seed_successor.py tests/test_daemon_soak.py` and `uv run pytest -q` exit 0 after fixture adoption with the hard gate enabled; `uv run pytest -q tests/test_plan_lint.py` exits 0. Preserve merged renderer/classifier behavior and immutable historical snapshots. The diff stays within 30 files and 1,500 inserted lines.

## Verification
```
uv run pytest -q tests/test_hostfiles.py tests/test_gates.py tests/test_merge.py tests/test_providers.py tests/test_cli.py
uv run pytest -q tests/test_stages.py tests/test_seed_path.py tests/test_drain.py tests/test_mergequeue.py tests/test_terminal.py tests/test_seed_successor.py tests/test_daemon_soak.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory governing facts return premise_failed, kind: spec_gap and their owning cited entry. Any criteria-forced path beyond earned closure needs contract repair.

## Time budget
- expected: 60m
- stuck: 90m
