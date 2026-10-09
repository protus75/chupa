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
- core-renderer

## Context
- chupa/config.py
- chupa/__main__.py
- tests/test_config.py
- tests/test_cli.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P6.migrate-config
- section 15

## Goal / Why
The strict loader's schema-zero repair road runs an explicit lossless, validated migration.

## Scope in / Scope out
Implement only the cited migration entry. chupa/config.py owns migration and validates the candidate through its real loader; chupa/__main__.py registers and runs migrate-config before the ordinary config load. Use the existing filesystem seam for the adjacent backup and atomic replacement. Keep current loader signatures and strict version-zero refusal intact; existing CLI seam bindings permit injection without widening main's signature.

Preserve all original bytes except the explicit integer version scalar. Publish nothing before validating the entire candidate, and preserve existing backups on refusals or current-version no-ops. The CLI selects --config or invocation-cwd config.yaml. Carry every named entry test below; version, YAML and full-schema errors must identify their cause and a repair action. No absent-version default, alternate loader, new config key, provider call, process spawn, journal append or git mutation belongs here. The activation sibling owns the routed conduct adoption and shared resolver.

## Scope fence
- chupa/config.py
- chupa/__main__.py
- tests/test_config.py
- tests/test_cli.py

## Acceptance criteria
1. `uv run pytest -q tests/test_config.py tests/test_cli.py` exits 0 with test_migrate_config_entry_unit proving unique resolve_plan_contract resolution, required_units and four-part entry_unit_gap depth with missing-part rejection.
2. `uv run pytest -q tests/test_config.py tests/test_cli.py` exits 0 with test_migrate_config_zero_to_one proving exact scalar-only replacement, comment/format retention, adjacent original-byte backup, one atomic config publication through the seam, and real-loader acceptance. test_migrate_config_validates_before_write rejects invalid candidate fields without any config or backup write.
3. `uv run pytest -q tests/test_config.py tests/test_cli.py` exits 0 with test_migrate_config_current_is_noop proving byte identity, no new backup and an unchanged existing backup on repeated current-version invocation.
4. `uv run pytest -q tests/test_config.py tests/test_cli.py` exits 0 with test_migrate_config_refuses_unsupported_inputs covering missing file/key, null, bool, string, float, negative/newer version, malformed YAML and invalid config shapes, each with a cause, paved road and unchanged original/backup bytes. Preserve test_older_schema_version_is_refused_naming_migrate_config, newer-version refusal, missing/unknown-key, null and type strictness.
5. `uv run pytest -q tests/test_config.py tests/test_cli.py` exits 0 with test_migrate_config_before_load driving the real CLI on version zero with explicit --config and cwd-default selection, success/no-op exit 0, refusal exit 2 and injected filesystem operations; no git, process, model or journal work occurs.
6. `uv run pytest -q tests/test_hostfiles.py tests/test_providers.py`, `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving merged renderer and loader behavior.

## Verification
```
uv run pytest -q tests/test_config.py tests/test_cli.py
uv run pytest -q tests/test_hostfiles.py tests/test_providers.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing or contradictory entry facts return premise_failed, kind: spec_gap naming the owning unit. A forced edit beyond earned closure needs plan repair.

## Time budget
- expected: 60m
- stuck: 90m
