---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- shakeout-report-lane
- verification-base-attribution

## Context
- chupa/stages.py

## Plan contract
- 19.L
- 19.P2
- section 7
- section 11

## Goal / Why
The first shakeout battery group pins the stage layer (`chupa/stages.py`) with six members, each run through the production drain on the bench with a FakeLLM and zero human input. This group's own Check run machine-produces the first `shakeout-report.json` into its OUTBOX.

Why: the battery is the orchestrator's permanent test suite (section 15), and the Phase 2 exit reads it (19.P2). Each member plants one fault and names the ONE observable a correct engine produces and a faked run cannot. The human-readable detail lives in the harvested finding, never the terminal REASON, which stays a stable code-only value (section 11.4).

Owners (19.P2 Emits: one chained deliverable per owning production module): this group fences ONLY `chupa/stages.py`, the module whose behavior it pins, plus the battery's own home `eval/shakeout/` and `tests/test_shakeout.py`. A member that exposes a defect in `chupa/stages.py` fixes it here. A defect anywhere else is filed as a second problem and the ticket replies `premise_failed`, naming it.

## Scope in / Scope out
- In: `eval/shakeout/stages.py` with `MEMBERS`, in this order. Each entry names (1) the planted fault, (2) the discriminating observable, and (3) the detail artifact:
  - `scope_escape`: (1) the scripted Implement commits a file outside `## Scope fence`. (2) The first terminal is `gate_failed` at `check`, its `checks.json` `scope_fence` report names that path, and nothing merges. (3) The harvested `scope_fence` finding in `attempts/<n>/harvest.json`.
  - `unfixable_lint_branch_only`: (1) a Verification check that passes at the merge base and fails on every branch attempt, planted in branch-only code. (2) Every attempt ends `gate_failed` at `check` with a `verification` finding, none marked `base_red`, and the stem ends routed `reject_queue` without merging. (3) The harvested `verification` finding.
  - `review_reject`: (1) Review replies `snag`. (2) `gate_failed` at `review` with `review.md` pinning `snag`. (3) `review.md`'s findings.
  - `review_reject_reentry`: (1) Review snags attempt 1 with a unique finding message, then approves. (2) Attempt 2's Implement prompt carries that message INSIDE `## Acceptance criteria`, before the next section heading, and the stem merges in the same drain. (3) The spooled attempt-2 prompt.
  - `empty_committed_diff`: (1) Implement replies `ok` and commits nothing. (2) `gate_failed` at `check` whose `verification` finding says the branch carries no committed change. (3) The harvested finding.
  - `base_diff_attribution`: (1) a Verification command red at BOTH the merge base and the branch, beside a green one. (2) The stem merges on its first attempt with zero `retry` draws, `checks.json` marks the command `base_red`, and one `failure_report` with `outcome == "base_red"` is in the box. (3) That box message.
- In: `eval/shakeout/run.py`: `GROUPS` becomes `("stages",)`.
- In: `tests/test_shakeout.py`: one test per member asserting its observable through `run_member`, plus a test that `produce("stages", None, ...)` returns six green entries.
- Out: members owned by other modules (later groups), any production change outside `chupa/stages.py`, and any edit to the runner, the bench, or the schema beyond `GROUPS`.

## Scope fence
- chupa/stages.py
- eval/shakeout/
- tests/test_shakeout.py

## Acceptance criteria
1. The `python -m eval.shakeout.run --group stages` command in `## Verification` exits 0 and writes `tickets/shakeout-stages/shakeout-report.json` holding exactly the six members above, each `green`.
2. `uv run pytest -q tests/test_shakeout.py` passes with one test per member asserting its named observable.
3. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m eval.shakeout.run --group stages --out tickets/shakeout-stages/shakeout-report.json
uv run pytest -q tests/test_shakeout.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A member asserts only a terminal state name, or reads its detail from the terminal reason.
- The report is written by anything but `write_report`, or committed on the branch.
- A member needs human input or a real model call.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
