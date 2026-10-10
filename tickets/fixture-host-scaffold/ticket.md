---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase6-continue-02
- host-contract-doc
- core-drift-activation

## Context
- chupa/config.py
- chupa/providers.py
- chupa/seams.py
- chupa/llm.py
- chupa/hostfiles.py
- chupa/artifacts.py
- chupa/specs.py

## Plan contract
- 19.I
- 19.P6.fixture-host-scaffold
- 19.P6.host-contract-doc
- 19.P6.core-drift-activation
- section 15
- section 12

## Goal / Why
Supply deterministic disposable host inputs that let later Phase 6 consumers prove their loop without an external host, network, login or model spend.

## Scope in / Scope out
The entry unit assigns the fixture profile, deterministic Python app/replay runner, closed scenarios, report/evidence fixtures and scripted CLI to the fixture tree, with scaffold checks in the fenced test file. Use the existing Claude adapter unchanged, including fixture-local version, package lookup and probe responses. The entry unit's Records governs the exact version-1 report schema; validate it locally before the later inbox exists. Only disposable copies accept runtime edits. Later host-loop machinery owns serve, confirms, transitions, attribution and report production; this construction does not launch that loop or forge journal, trailer, GO or exit evidence. No engine module, adapter registration or config extension is introduced.

## Scope fence
- hosts/fixture/
- tests/test_fixture_host.py

## Acceptance criteria
1. `uv run pytest -q tests/test_fixture_host.py` exits 0 with test_fixture_host_entry_units exercising own/cited required_units, unique resolve_plan_contract resolution, all four entry_unit_gap parts and missing-part rejection.
2. `uv run pytest -q tests/test_fixture_host.py` exits 0 with test_fixture_profile_loads loading the version-1 profile through the real loader in a disposable root, checking host-local state/worktree paths, routing, review/merge checks, report inbox and explicit safety inventory.
3. `uv run pytest -q tests/test_fixture_host.py` exits 0 with test_fixture_scenario_list_is_closed pinning five scenarios: three distinct machine merges, regression and escape, each with responses, host-only edits, checks and evidence; unknown scripts refuse with a recovery road.
4. `uv run pytest -q tests/test_fixture_host.py` exits 0 with test_fixture_replay_is_deterministic checking repeated initial_state/actions bytes yield the same final state and defect result through a Python argv-list runner. test_fixture_regression_exists_at_base proves the test exists on the defective base, fails there for the defect and passes after its scripted fix. test_fixture_escape_is_machine_introduced proves a scripted machine edit passes checks then fails replay.
5. `uv run pytest -q tests/test_fixture_host.py` exits 0 with test_fixture_reports_are_bounded checking the exact Records schema: schema_version 1; both origins; nonblank summary/app_commit/app_version; optional implicated_paths and evidence defaults; nullable evidence.replay/log; self_diagnosed requires game_slug/anomaly_code/location while player omits them; unknown report/evidence keys and non-1 versions refuse. No fixture signature field is invented. Check replay initial_state/actions, host-contained regular evidence files, and 1 MiB replay/64 KiB log caps with exact-boundary acceptance, without importing an unbuilt inbox validator.
6. `uv run pytest -q tests/test_fixture_host.py` exits 0 with test_fixture_cli_adapter_roundtrip driving the real existing adapter through injectable seams: version/package/probe preflight, Author/Implement/Review/triage schema-valid scripts, stdin prompts, success terminal parsing and zero cost, plus unknown/exhausted-script refusal roads. The fixture-local Python claude executable uses the cited terminal stream protocol; only Implement writes declared host edits, using explicit environment without provider keys.
7. `uv run pytest -q tests/test_fixture_host.py` exits 0 with test_fixture_scaffold_is_dormant proving committed inputs stay unchanged, engine-plane writes and secret-bearing child environment are absent, and serve, GO, journal and exit-report producers are not activated.
8. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving merged adapters and behavior.

## Verification
```
uv run pytest -q tests/test_fixture_host.py
uv run pytest -q tests/test_providers.py tests/test_config.py tests/test_hostfiles.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed with the owning spec_gap unit. A forced engine or out-of-fence change requires plan/ticket repair; do not invent a protocol or activate later consumers.

## Time budget
- expected: 60m
- stuck: 90m
