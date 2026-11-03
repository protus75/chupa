---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase7-core

## Context
- chupa/specs.py
- tests/test_specs.py
- tests/test_stages.py

## Plan contract
- 19.I
- 19.P7.implement-consumer-read
- section 8

## Goal / Why
Require the implementer to read downstream consumers before changing a production value's representation, so a literal criterion does not silently break an unfenced caller.

## Scope in / Scope out
Apply the cited entry's complete prompt and test contract. Read the fenced implement spec directly from the worktree before editing; prompt specs cannot be embedded as Context. Ownership stays with specs/implement.md and its chupa/specs.py loader; add no module.

Move the implement spec to version 1.5 and add the entry-governed Task instruction covering representation changes, repository consumer searches and reads, a plausible reading preserving an unfenced consumer, surprises in the run record, and premise_failed when no such reading exists. Preserve other metadata, placeholders, outcomes and artifacts. Adjust the existing spec lint version assertion and only the contradicted implement version assertion in the stage provenance test. No engine code or run-record schema changes.

## Scope fence
- specs/implement.md
- tests/test_specs.py
- tests/test_stages.py

## Acceptance criteria
1. `uv run pytest -q tests/test_specs.py` exits 0 with `test_implement_spec_consumer_read` pinning version 1.5, the consumer search/read before a production representation edit, null/empty, type, field or column naming and encoding cases, the out-of-fence interpretation rule naming surprises and premise_failed, unchanged non-version metadata, and unchanged placeholders. It checks the rendered prompt and existing section and line limits.
2. `uv run pytest -q tests/test_specs.py` exits 0 with `test_implement_consumer_read_entry_unit` checking required_units, unique resolve_plan_contract resolution, and each Owner, Records, Observable and Tests part through entry_unit_gap.
3. `uv run pytest -q tests/test_stages.py` exits 0 with `test_implement_check_review_all_ok_with_artifacts_and_provenance` recording implement 1.5; preserve every other assertion. The version assertion in `test_spec_lint_accepts_the_implement_and_requisition_specs` expects implement 1.5.
4. `uv run pytest -q` exits 0; existing lint tests remain green and historical seeding snapshots remain untouched.

## Verification
```
uv run pytest -q tests/test_specs.py
uv run pytest -q tests/test_stages.py
uv run pytest -q
```

## Definition of rejected
Missing governing facts return premise_failed with kind: spec_gap and the owning entry unit. An unavoidable unfenced consumer change needs contract repair.

## Time budget
- expected: 30m
- stuck: 60m
