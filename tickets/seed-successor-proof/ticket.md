---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-core

## Context
- chupa/__main__.py
- chupa/runner.py
- chupa/stages.py
- chupa/merge.py
- chupa/drain.py
- chupa/tickets.py
- chupa/git.py
- chupa/llm.py
- chupa/seams.py

## Plan contract
- 19.I
- 19.P3.seed-successor-proof

## Goal / Why
Prove that a merged parent registers and runs its newly authored successor in the same production drain invocation.

The new test owns this proof only. Stage seed review/lift, ticket validation/intake, code admission, and committed-ticket re-scan/selection retain their existing production owners and writers. Read the merged seeding and CLI/drain fixtures as idioms, running their suites unchanged as preservation checks. This is an integration proof of merged behavior, with no scheduler or daemon activation.

## Scope in / Scope out
- In: a disposable real git repo initially containing only the parent of the proof pair. Use scripted FakeLLM through the CLI pipeline seam bound to runner.bind, retaining real runner.drive, Implement/Check/Review, lint/requisition review, lift_seeds, Effects/journal, merge, and drain scan/selection. Use injected clock/sleep and existing filesystem/process seams.
- In: Implement callbacks alone create the successor uncommitted in the parent's worktree and commit small code changes on both branches. The successor is a complete grammar-valid confirmed seed (P2, chore, medium/medium), with a dependency on its parent and valid Plan contract, Context, fence, and Verification. Parent construction fences tickets plus its small code path. Avoid chupa/specs changes in the disposable workload so it needs no self-upgrade or run-lane admission.
- In: at parent Review read the Check invoice, approved seed blob, lift Effect, and intake record already on main, with no parent merged terminal and no successor execution. Call the real drain scan and selector on that snapshot: the committed successor must be visible but ineligible. After real parent admission the next scan runs the successor without a drain restart, second intake, or hook.
- Out: production edits, replacing scan/selection/lift/admission, manufacturing merged terminals in scripted dispatch, setup writing the successor on main, real-model calls, wall-clock sleep evidence, and changes to preservation suites.

## Scope fence
- tests/test_seed_successor.py

## Acceptance criteria
1. `uv run pytest tests/test_seed_successor.py tests/test_seed_path.py tests/test_drain.py tests/test_merge.py` passes `test_merged_parent_registers_and_runs_successor_in_same_drain`, using one invocation of the real CLI drain composition and proving the successor is absent at invocation start, appears before parent merge, and is selected only after its parent settles.
2. `uv run pytest tests/test_seed_successor.py tests/test_seed_path.py tests/test_drain.py tests/test_merge.py` reads the Check artifact through Invoice: SeedReview has the successor stem, verdict approve, empty findings, and ticket_sha equal to the committed successor blob. Assert the exact requisition_verdict and ticket_intake signal envelopes/bodies specified by the entry unit, including reviewed text, seeded_by, confirmed state, seed source, new true, null keys, and the actual commit/blob identities.
3. `uv run pytest tests/test_seed_successor.py tests/test_seed_path.py tests/test_drain.py tests/test_merge.py` proves exactly one seed-only commit with subject `chupa(<parent>): seeds`, one seed intake, and the matching lift Effect intent/completion under `ticket-plane/<parent>/<attempt>/seeds`. Completion result names the real seed commit. Both real squash commits carry code only; both merged terminals carry their real commit and reviewed SHA, once per stem, with parent terminal before successor dispatch.
4. `uv run pytest tests/test_seed_successor.py tests/test_seed_path.py tests/test_drain.py tests/test_merge.py` proves final quiescence in that same invocation. The fixture's request sequence and intermediate scan/selector assertions fail if lift, intake emission, re-scan, or dependency gating is bypassed. Existing seed, drain, and merge suites run unchanged.
5. `uv run pytest -q` exits 0 with no test removed or skipped and no production behavior changed.

## Verification
```
uv run pytest tests/test_seed_successor.py tests/test_seed_path.py tests/test_drain.py tests/test_merge.py
uv run pytest -q
```

## Definition of rejected
Reject if the proof replaces a production lane with a scripted success, hand-writes the successor on main, commits tickets on a code branch, requires a production change, invents an entry-unit record, or leaves the fence. A needed fact missing from the entry unit returns premise_failed naming 19.P3.seed-successor-proof for section 11.4 hardening.

## Time budget
- expected: 45m
- stuck: 120m
