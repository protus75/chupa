---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase5-exit

## Context
- chupa/__main__.py
- tests/test_cli.py
- chupa/config.py
- chupa/providers.py
- chupa/seams.py
- chupa/specs.py

## Plan contract
- 19.I
- 19.P6.core-renderer
- section 8
- section 15

## Goal / Why
The core verb installs and refreshes routed conduct blocks while retaining exact project bytes.

## Scope in / Scope out
Implement the first Phase 6 renderer row only. The cited entry assigns the new chupa/hostfiles.py module ownership of the template, parser, byte renderer and refresh writer; chupa/__main__.py composes the verb. Use the existing config, candidate resolution and filesystem seams. Keep main's public signature and existing callers compatible in place; tests can inject the existing seam bindings. No provider-module edits, shared conduct-path resolver, gate activation, daemon refresh, model invocation, journal record or git work belongs here.

Author the entry's named obligations in tests/test_hostfiles.py and tests/test_cli.py, exercising the component through real CLI routing as well as direct byte operations. Preserve all existing CLI assertions. An unrouted agent gets no conduct file. Atomic filesystem publication is the sole mutation. Inspect every selected file before any publication so one broken marker structure leaves the whole selection untouched. A repeat invocation must do no further writes. Keep first adoption lossless even for populated files, mixed line endings and a missing final newline. Repair roads retain project content. Generate the golden through the branch's renderer and template; do not manually maintain expected managed bytes.

## Scope fence
- chupa/hostfiles.py
- tests/test_hostfiles.py
- chupa/__main__.py
- tests/test_cli.py

## Acceptance criteria
1. `uv run pytest -q tests/test_hostfiles.py tests/test_cli.py` exits 0 with test_renderer_entry_unit checking required_units, unique resolve_plan_contract resolution, complete entry_unit_gap depth, and refusal when each depth part is removed.
2. `uv run pytest -q tests/test_hostfiles.py tests/test_cli.py` exits 0 with test_core_first_adoption_preserves_project_bytes covering absent, empty and marker-free populated conduct files, including the initial chupa form, exact bytes, mixed line endings and missing final newline; test_core_refresh_preserves_remainder proves both project prefix and suffix survive replacement unchanged.
3. `uv run pytest -q tests/test_hostfiles.py tests/test_cli.py` exits 0 with test_core_marker_corruption_refuses_without_writes covering malformed, partial, duplicate, reordered, unterminated and stray marker text plus a corrupt member of a multi-file selection. Every refusal precedes all writes and provides marker repair without data loss.
4. `uv run pytest -q tests/test_hostfiles.py tests/test_cli.py` exits 0 with test_core_render_is_byte_idempotent proving repeated byte renders and refreshes make no further writes; test_core_golden_uses_branch_template compares a mechanically generated branch golden with a fresh render and detects a stale golden after a template change.
5. `uv run pytest -q tests/test_hostfiles.py tests/test_cli.py` exits 0 with test_core_routed_conduct_files driving the real CLI for claude-only, other-CLI-only, mixed and repeated-path routing. test_core_refusal_and_no_git proves exit 0 on success, exit 2 with a road on corruption, atomic writes, and no git, journal, provider call or gate work.
6. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving merged behavior. Shared provider resolver and core_drift activation remain the later activation's obligation.

## Verification
```
uv run pytest -q tests/test_hostfiles.py tests/test_cli.py
uv run pytest -q tests/test_config.py tests/test_providers.py tests/test_gates.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing entry facts return premise_failed with kind: spec_gap and the owning cited unit. A required edit outside this fence needs contract repair; do not activate drift checks or change unrelated process rules.

## Time budget
- expected: 60m
- stuck: 90m
