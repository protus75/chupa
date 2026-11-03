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
- 19.P7.review-spec-readonly
- section 8

## Goal / Why
Make the correctness review prompt explicitly describe the tools available to its session and the mechanical evidence already decided at Check.

## Scope in / Scope out
Apply the cited entry's complete prompt and test contract. Read the fenced review spec from the worktree before editing; prompt specs cannot be embedded as Context. Its owner remains specs/review.md with the existing chupa/specs.py loader; add no module.

Change the review spec to version 1.1 and adjust its Role or Task instructions and acceptance snag reason as the entry requires. Preserve the remaining metadata, placeholders, verdicts, artifacts, and other review instructions. Add the named spec tests and update only the contradicted review version assertion in the existing stage provenance test. No loader, driver, gate, routing, or GO machinery changes.

## Scope fence
- specs/review.md
- tests/test_specs.py
- tests/test_stages.py

## Acceptance criteria
1. `uv run pytest -q tests/test_specs.py` exits 0 with `test_review_spec_read_only` pinning version 1.1, the Read/Grep/Glob/LS-only session, Verification and host mechanical checks already decided at Check, no command attempts or verdict qualification for not running them, removal of the Verification snag clause, and unchanged metadata other than version and unchanged placeholders. It renders the edited prompt and keeps spec section and line limits green.
2. `uv run pytest -q tests/test_specs.py` exits 0 with `test_review_spec_readonly_entry_unit` checking required_units, unique resolve_plan_contract resolution, and each Owner, Records, Observable and Tests part through entry_unit_gap.
3. `uv run pytest -q tests/test_stages.py` exits 0 with `test_implement_check_review_all_ok_with_artifacts_and_provenance` recording the served review version 1.1; preserve every other assertion.
4. `uv run pytest -q` exits 0; existing spec lint tests remain green and historical seeding snapshots remain untouched.

## Verification
```
uv run pytest -q tests/test_specs.py
uv run pytest -q tests/test_stages.py
uv run pytest -q
```

## Definition of rejected
A missing governing fact returns premise_failed with kind: spec_gap and its owning entry unit. A forced change beyond the fence needs contract repair.

## Time budget
- expected: 30m
- stuck: 60m
