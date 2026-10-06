---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- box-triage

## Context
- chupa/git.py
- tests/test_git.py
- tests/test_stages.py
- tests/test_merge.py
- tests/test_drain_reentry.py

## On-demand
- chupa/stages.py
- tests/test_diagnose.py
- tests/test_terminal.py

## Plan contract
- 19.L
- 19.P2
- section 7
- section 10

## Goal / Why
The verification gate attributes each red `## Verification` command by BASE DIFF, per command (section 7): a command red on the branch is re-run at the branch's merge base, and one that is ALSO red there is a pre-existing base failure. It is filed to the Suggestion Box as a second problem and charged to neither the Check nor the retry budget. A command green at the base and red on the branch still fails the Check. The same attribution runs at merge regating.

Why: the Phase 1 gate fails a stem on ANY red. A full-suite command that a broken main already reddens fails every ticket for a defect none of them introduced, and each one burns its retry cap on it. Section 7 ships the attribution with the Phase 2 spine beside its filing consumer, the Suggestion Box, which has merged. The 19.P2 settled contracts (ATTRIBUTION, SUPERSEDED BEHAVIOR) name this deliverable.

Owners (section 9 ownership law): `chupa/stages.py` owns stage-evidence gathering and the verification gate, so the base re-run, the per-command record, and the filing live there. Merge regating calls the same `gather_evidence`, so it inherits the attribution with no `chupa/merge.py` change. `chupa/git.py` owns the two new ops. `chupa/box.py` is called through `Box.enqueue`, never changed. `tests/test_drain_reentry.py` is owned here (19.P2 SUPERSEDED BEHAVIOR).

## Scope in / Scope out
- In: `chupa/git.py` gains `merge_base(dir, a, b) -> str` (`merge-base <a> <b>`) and `worktree_add_detached(dir, path, rev)` (`worktree add --detach <path> <rev>`). Both refuse option-shaped refs like the existing ops.
- In: `chupa/stages.py`:
  - `CommandResult` gains `base_red: bool = False`.
  - In `gather_evidence`, when at least one command exits nonzero (or cannot run), the base is `merge_base(repo, MAIN, <stem>)`. A detached base worktree is created ONCE at `<worktree_root>/.base/<stem>` (removed first if a prior run left it), each red command is re-run there with the same env and timeout, and the worktree is removed with `worktree remove` + `prune` before `gather_evidence` returns. A command red at the base too gets `base_red: true`. Its base output is spooled beside the branch output as `<stage>/verify-<nn>-base.txt`.
  - Each `base_red` command files ONE `failure_report` through `Box(config.state_dir / BOX_DIR, fs).enqueue(...)` with `origin=<stem>`, `stage=<stage>`, `outcome="base_red"`, and summary `` `<command>` fails on the merge base <sha8> too; fix main, not this ticket ``. Enqueue dedup collapses repeats within the stem (section 12).
  - `VerificationGate` ignores `base_red` commands. The empty-diff and `already_satisfied` rules are unchanged, and 19.P2 REPORT REQUIRED still fails a Check whose named registered report is missing, `base_red` or not.
- In: `tests/test_drain_reentry.py` gains the base-red case beside the Phase 1 branch-only-red re-entry regression, which stays as it is: a command red at both base and branch lets the drain merge the ticket in one attempt with no `retry` draw, and one `failure_report` names the command.
- Out: per-test attribution or any runner-output parsing (section 18), the integration check (Phase 3), and any `chupa/merge.py`, `chupa/box.py`, or `chupa/runner.py` change.

## Scope fence
- chupa/stages.py
- tests/test_stages.py
- chupa/git.py
- tests/test_git.py
- tests/test_merge.py
- tests/test_drain_reentry.py
- tests/test_diagnose.py
- tests/test_terminal.py

## Acceptance criteria
1. `tests/test_stages.py` proves a ticket with two Verification commands, one red at both base and branch and one green, passes Check, its `checks.json` marks the first `base_red`, and one `failure_report` with `outcome == "base_red"` and `origin` the stem is in the box.
2. `tests/test_stages.py` proves a command green at the base and red on the branch fails Check `gate_failed` with no box message, and that no `.base/<stem>` worktree survives `gather_evidence` on either path.
3. `tests/test_merge.py` proves merge regating attributes the same way: a base-red command does not refuse an otherwise-admissible candidate.
4. `tests/test_git.py` proves `merge_base` and `worktree_add_detached` against a temp repo and refuses a ref starting with `-`.
5. `uv run pytest -q tests/test_drain_reentry.py` passes with the base-red case added and the existing branch-only-red test unchanged.
6. `tests/test_diagnose.py`'s drain fixture (`test_drain_renders_two_attempts_lessons_and_no_spooled_raw_marker`) is rewritten so its Verification command is green at the merge base and red only on the branch; it still proves a branch-introduced retry. No other test in that file changes. `tests/test_terminal.py`'s red-check fixture is converted the same way (red only on the branch).
7. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_stages.py tests/test_merge.py tests/test_git.py tests/test_drain_reentry.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A branch-introduced red passes, or a base-red command fails the Check or draws `retry`.
- A base worktree is left behind, or is cleaned with anything but `worktree remove` + `prune`.
- Attribution parses test-runner output, or merge regating gets a second attribution path.
- The diff touches a file outside the fence.

## Time budget
- expected: 75m
- stuck: 150m
