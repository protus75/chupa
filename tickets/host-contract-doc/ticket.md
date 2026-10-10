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
- migrate-config

## Context
- chupa/config.py
- chupa/seams.py
- chupa/hostfiles.py
- chupa/providers.py
- chupa/lockfile.py
- chupa/specs.py
- chupa/gates.py
- chupa/mergequeue.py
- chupa/tickets.py

## Plan contract
- 19.I
- 19.P6.host-contract-doc
- section 15
- section 12

## Goal / Why
Give a new host a copyable configuration and precise ownership and cutover instructions.

## Scope in / Scope out
docs/host-contract.md owns the document; tests/test_host_contract.py owns executable documentation checks. Implement the cited entry's documentation contract only. Read the merged configuration, migration, conduct, provider, seam, lock and ticket owners before describing them.

Describe Gate.check and MergeQueue.host_checks from their Context owners. Do not promise optional structured findings that merged host_checks does not consume. Section 15 governs additive-only frontmatter policy; chupa/tickets.py owns the currently accepted closed Frontmatter fields and defaults. Pin the documented field list against that owner without claiming an unbuilt schema migration mechanism.

The cited report and cutover contracts describe pending consumers; documentation checks must not import future Phase 6 modules. Foreign process-state adoption stays excluded. No production source, runtime activation, provider call, git mutation, config change, managed conduct edit or journal write belongs here.

## Scope fence
- docs/host-contract.md
- tests/test_host_contract.py

## Acceptance criteria
1. `uv run pytest -q tests/test_host_contract.py` exits 0 with test_host_contract_entry_unit pinning required_units, unique resolve_plan_contract resolution, all four entry_unit_gap parts and missing-part rejection.
2. `uv run pytest -q tests/test_host_contract.py` exits 0 with test_host_contract_example_loads extracting the copyable commented YAML example and validating it with the real loader in a disposable host root.
3. `uv run pytest -q tests/test_host_contract.py` exits 0 with test_host_contract_schema_coverage comparing the full documented field list, provider package, required keys, shipped defaults, closed values, path resolution and absent/null behavior with merged config definitions. The review/merge example covers mechanical argv, surfaces, trigger_map, gate_severity, safety_checks and both strategy shapes as host choices.
4. `uv run pytest -q tests/test_host_contract.py` exits 0 with test_host_contract_migration_and_managed_ownership checking version handshake, scalar-only migration, validation-before-write, adjacent original-byte backup, current no-op and refusal roads; managed core/project remainder, routed selection, byte-preserving adoption/refresh, marker refusal and chupa core repair.
5. `uv run pytest -q tests/test_host_contract.py` exits 0 with test_host_contract_seam_inventory checking clock/sleep, process-exec, filesystem and notification signatures and edge behavior, group kill on timeout/cancellation, explicit child env, stdin-file prompts and atomic writes. Pin Gate.check(artifact, workspace) -> GateReport against chupa/gates.py and host_checks against chupa/mergequeue.py: review.mechanical argv, rc 0 passes and other results fail, redacted tails and spooled output, exactly one hard safety_checks entry and always/hard integration selection. Document additive-only frontmatter policy and compare accepted fields/defaults with chupa/tickets.py::Frontmatter.
6. `uv run pytest -q tests/test_host_contract.py` exits 0 with test_host_contract_report_custody_and_cutover checking version-1 report origins/fields, summary/commit/version, implicated paths and evidence, metadata-first 1 MiB replay/64 KiB log bounds, durable box custody before message recording, triage ticket-evidence copy and untrusted text. Pin single-writer instance isolation, state-dir custody and config re-read cadence; distinguish unattended bootstrap, supervised fixture wiring, committed baseline/operator Author-graph judgment, operator-recorded GO, NO_GO or absent-host wait and live-host acceptance, without importing future consumers.
7. `uv run pytest -q tests/test_plan_lint.py` and `uv run pytest -q` exit 0 preserving merged behavior.

## Verification
```
uv run pytest -q tests/test_host_contract.py
uv run pytest -q tests/test_hostfiles.py tests/test_cli.py tests/test_config.py
uv run pytest -q tests/test_plan_lint.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed with kind: spec_gap and the owning unit. A forced production or out-of-fence change needs plan/ticket repair.

## Time budget
- expected: 60m
- stuck: 90m
