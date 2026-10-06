---
state: confirmed
source: seed
priority: P1
kind: chore
agent_tier: high
agent_effort: high
---

## Depends on
none

## Context
- tests/test_plan_lint.py

## Plan contract
- 19.L
- 19.P3
- 19.P3.merge-queue
- section 9
- section 10

## Goal / Why
`CHUPA_PLAN.md` entry unit `19.P3.merge-queue` states every fact the `merge-queue` seed needs, so `phase3-continue` authors that seed from the plan instead of inventing it.

## Scope in / Scope out
- In: the entry unit `### 19.P3.merge-queue` (inserted after its phase's last unit when missing), with its Owner, Records, Observable, and Tests parts.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P3.merge-queue

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P3.merge-queue` states, consistent with merged code: The entry unit requires MERGE-SAFETY to run before integration, so a refusal pays no full verification run. Two of the safety gates, `ScopeFenceGate` and `RunRecordGate`, judge an `Evidence` record. The only producer of `Evidence` is `stages.gather_evidence`, and it runs every Verification command, including the base-red worktree rerun, before it returns `changed_files` and `run_record`. Section 9.5's fence-authoring law makes stage-evidence gathering the stage layer's seam (`chupa/stages.py`), and a deliverable that hooks that seam must fence it. That leaves the implementer two options, and the ticket forbids both: build the non-verification `Evidence` fields a second time inside `mergequeue.py`, which duplicates the stage-owned gatherer and conflicts with 'reuse the stage-owned gather_evidence'; or split `gather_evidence`, which needs an edit to `chupa/stages.py` outside the fence. The entry unit does not say which owner produces safety-tier evidence without running Verification.
3. `CHUPA_PLAN.md` unit `19.P3.merge-queue` states, consistent with merged code: Nothing in the engine executes `review.mechanical` entries today: no module outside `config.py` reads `.mechanical`, `safety_checks` or `strategies`. The ticket says host checks run 'through the existing evidence writer', but `gather_evidence` runs only the ticket's own Verification commands. So the queue would be the first host-check runner, and the entry unit leaves out the facts that runner needs: (1) its child env (presumably `child_env(ctx.env, ctx.config)`, to keep provider keys out) and its timeout source; (2) where output is spooled and how it is redacted at the write seam; (3) how a nonzero, timed-out or unresolvable check becomes a `GateReport`/`Finding`, with which code and which paved road; (4) whether a soft or non-`always` entry is skipped or reported; (5) what happens when a `merge.safety_checks` code matches no `review.mechanical` entry (fail closed is implied but not stated); (6) whether host checks get base-red attribution. Without these the implementer has to invent entry-unit facts, which the Definition of rejected forbids.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside `19.P3.merge-queue`, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
