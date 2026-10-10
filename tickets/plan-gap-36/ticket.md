---
state: confirmed
source: seed
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
---

## Depends on
none

## Context
- tests/test_plan_lint.py

## Plan contract
- 19.L
- 19.P6
- 19.P6.fixture-host-scaffold

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase6-continue-02` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P6.fixture-host-scaffold

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P6.fixture-host-scaffold` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P6.fixture-host-scaffold says to commit bounded 'version-1 report fixtures following section 12's report fields and origins', and test_fixture_reports_are_bounded must validate them. Section 12.8 (CHUPA_PLAN.md line 1354) names the fields only loosely: origin, summary, dedup signature, app commit/version, implicated paths and evidence. It gives no version scalar, no exact key names and no evidence layout. The concrete version-1 schema appears only in the later unit 19.P6.report-inbox-triage (line 2638). That schema has `schema_version: 1`, `origin`, `summary`, `app_commit`, `app_version`, optional `implicated_paths`, `evidence.{replay,log}` and the self_diagnosed-only `game_slug`/`anomaly_code`/`location`. No engine validator for it exists yet: chupa/inbox.py is unbuilt, and config.py only has `report_inbox`. The entry unit therefore leaves out the exact record shape the fixtures and test must follow, and the implementer would have to invent field names. The later inbox deliverable could then reject the committed fixtures.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
