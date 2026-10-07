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
- 19.P3
- 19.P3.pause-resume-activation
- section 20

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.pause-resume-activation` states every fact the `pause-resume-activation` seed needs, so `phase3-continue-08` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.pause-resume-activation` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.pause-resume-activation

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.pause-resume-activation` states, consistent with merged code: The no-engine route says pause/resume 'acquire the same writer lock and apply directly under section 20's contract' and must 'never leave a request to act on an unrelated later lifecycle'. Section 20 only says 'the pre-daemon path is unchanged', but no pre-daemon pause/resume verb exists: the current parser has none, as the ticket itself notes. The pause projection is also lifecycle-bound (ControlInbox._fold accepts only decisions whose lifecycle_id matches its own), and with no engine running there is no lifecycle. The spec never says what a direct pause or resume writes or changes. It could journal a CONTROL_DECISION, and if so under which lifecycle_id and request_id. It could create a lifecycle. It could refuse, as direct kill does. It also never says whether a direct pause holds the next drain. test_pause_resume_apply_directly_under_lock ('direct behavior and no deferred request') therefore has no observable to assert, and the implementer would have to invent the record.
3. `CHUPA_PLAN.md` unit `19.P3.pause-resume-activation` states, consistent with merged code: The entry requires the active.json discovery record to be written through chupa/control.py's filesystem-seam writer, refreshed after each decision, and 'retired before releasing the lock' on exit, failure, cancellation and handoff. The FileSystem seam in chupa/seams.py offers only publish (no-overwrite), write and replace; it has no remove or unlink. The closed record shape {lifecycle_id, hold_id} has no retired form. So retirement either needs a new seam operation in chupa/seams.py, plus the test fakes such as ScriptFS, which is outside the scope fence, or needs a retirement representation the plan does not state. Calling Path.unlink directly would break the injectable-seam rule.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.pause-resume-activation`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
