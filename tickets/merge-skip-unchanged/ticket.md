---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- none

## Runs before
- remove-merge-hold

## Context
- chupa/merge.py
- chupa/git.py
- tests/test_host_mechanical.py
- chupa/stages.py

## On-demand
- chupa/mergequeue.py
- tests/test_merge.py
- tests/test_bug_gate.py
- tests/test_mergequeue.py
- docs/how-chupa-works.md

## Goal / Why
Inline merge (`run` and `drain`) always reruns Verification, the bug regression, the Check gates and every triggered hard host check on the rebased branch (`chupa/merge.py`, `merge`). The drain runs one ticket at a time, so between Check and merge `main` normally gains only the engine's own commits under `tickets/` (ticket intake and outbox lifts). The rerun therefore tests the code Check just passed, byte for byte. It doubles test time and gives a flaky test a second chance to fail the merge. The `serve` merge queue (`chupa/mergequeue.py`) is worse: its safety tier runs the host's `merge.safety_checks`, and then its integration tier reruns every Check gate and host check, so a ticket's tests can run three times. After this change, inline merge and the serve merge queue both skip those reruns when `main` changed no path outside `tickets/` since the branch's merge base, and still runs the Merge gates. The skip trusts one invariant: a Review approval pinned to `reviewed` implies a passing Check at that head, because `run_stages` reaches Review only after an ok Check.

## Scope in / Scope out
- In: `chupa/merge.py` `merge`: compute main's changes since the branch's merge base with the existing `await ctx.git.diff_names(ctx.repo, reviewed, MAIN)`. It is three-dot, so it lists merge-base(reviewed, main)..main. `reviewed` is the sha captured before the rebase. Drop every path under `tickets/`. A tree diff is not used: a main commit whose content the branch already has would hide from it, while the bug regression and base-red attribution depend on the new merge base.
  - If that list is empty and the branch's changed files against `main` are nonempty: take `evidence` from `gather_safety_evidence(ctx, ticket, "ok")` and skip `run_gates(CHECK_GATES, ...)` and the triggered host checks. Spool nothing under `merge/` for them.
  - Otherwise behave exactly as today. This includes an empty-diff (outbox-only) branch, which needs `gather_evidence`'s report custody checks.
  - The Merge gates (`run_gates(MERGE_GATES, candidate, ...)`), `write_squash` and retirement run in both cases.
- In: `chupa/merge.py`: the "did main's code move" decision above is one function, and `chupa/mergequeue.py` calls the same one. Serve's `_admit` takes `reviewed` from before the rebase. When nothing outside `tickets/` moved and the branch diff is nonempty:
  - The safety tier keeps its `scope_fence`/`run_record` gates and the Merge gates, but skips the host safety checks.
  - The integration tier (`gather_evidence` for `merge-integration`, `run_gates(CHECK_GATES, ...)` and the integration host checks) is skipped. The squash proceeds on the safety-tier evidence.
  - Otherwise the queue behaves exactly as today. Red-streak counting only sees tiers that ran.
- In: `chupa/merge.py`: the module docstring states the skip and the invariant it relies on (Review only after an ok Check, `run_stages`).
- In: tests.
  - `tests/test_host_mechanical.py`: `test_inline_merge_reruns_triggered_hard_entries` commits a code change to `main` before merging, so it still exercises the rerun. Add a test where `main` gains only a `tickets/` commit: no host command runs and the merge succeeds.
  - `tests/test_mergequeue.py`: add a test where `main` gains only a `tickets/` commit. No host command runs in either tier, and the candidate merges. Any existing queue test whose assertion depends on a merge-time rerun commits a code change to `main` first.
  - `tests/test_serve.py`, `tests/test_daemon_composition.py`, `tests/test_daemon_soak_runner.py` (and its `eval/daemon_soak.py` scenario): each asserts `merge-integration/` or `merge-safety/` spools. A scenario that must keep the rerun commits a main-side code change before admission; assertions are not weakened.
  - `tests/test_merge.py`, `tests/test_bug_gate.py`, `tests/test_mergequeue.py`: any inline-merge test whose assertion depends on a merge-time rerun (a Check gate, host check, Verification or bug-regression failure at merge) commits a code change to `main` before merging, so it keeps testing the rerun path. Assertions are not weakened.
- In: `docs/how-chupa-works.md` section 4.5: steps 2-3 apply only when the rebase brought a change outside `tickets/`; otherwise only the Merge gates run. Section 7.2.1: the same skip applies to the host safety checks and the integration tier.
- Out: Check; the gates themselves; flaky-test handling.

## Scope fence
- chupa/merge.py
- chupa/mergequeue.py
- tests/test_host_mechanical.py
- tests/test_merge.py
- tests/test_bug_gate.py
- tests/test_mergequeue.py
- tests/test_serve.py
- tests/test_daemon_composition.py
- tests/test_daemon_soak_runner.py
- eval/daemon_soak.py
- docs/how-chupa-works.md

## Acceptance criteria
1. Skip when unchanged. A reviewed branch with a code change, where `main` gains only a commit under `tickets/` after Check, merges with zero host-command calls and no `merge/verify-*` or `merge/host-*` spool files. A test fails if any host command or Verification command runs. Checked by `uv run pytest tests/test_host_mechanical.py`.
2. Rerun when main's code moved, including content the branch already has. `tests/test_bug_gate.py::test_bug_gate_merge_rebase_regates` (inline), where main commits the same fix as the branch, still ends `gate_failed`. Checked by `uv run pytest tests/test_bug_gate.py`. Also: The same branch, where `main` gains a commit changing a file outside `tickets/`, runs the triggered hard host checks. A failing one refuses the merge and leaves `main` untouched. A test fails if the rerun is skipped. Checked by `uv run pytest tests/test_host_mechanical.py`.
3. Merge gates still run when skipping. On an unchanged-code merge, an approval pinned to an older head is refused by `correctness_review`. A test fails if the skip also skips Merge gates. Checked by `uv run pytest tests/test_host_mechanical.py`.
4. The serve merge queue skips the same way. With `main` gaining only a `tickets/` commit, a candidate merges with zero host-command calls across both tiers, and the Merge gates still run. With `main` gaining a code commit, both tiers run and a failing host check refuses. Checked by `uv run pytest tests/test_mergequeue.py`.
5. An empty-diff (outbox-only) branch still takes the full path, and its existing tests pass. Checked by `uv run pytest tests/test_merge.py`.
6. `uv run pytest tests/test_merge.py tests/test_bug_gate.py tests/test_mergequeue.py` exits 0.
7. `docs/how-chupa-works.md` sections 4.5 and 7.2.1 state the skip.
8. The trusted invariant stays tested: `tests/test_stages.py::test_check_fails_closed_on_an_out_of_fence_edit_and_never_reaches_review` passes unchanged, checked by `uv run pytest tests/test_stages.py -k never_reaches_review`.
9. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_host_mechanical.py tests/test_merge.py tests/test_bug_gate.py tests/test_mergequeue.py
uv run pytest tests/test_stages.py -k never_reaches_review
uv run pytest -q
```

## Definition of rejected
The skip applies when `main` changed any path outside `tickets/` since the branch's merge base, or is decided by a tree diff; Merge gates are skipped; inline merge and the serve queue decide the skip with two different functions; an existing test's assertion is weakened instead of given a main-side code change.

## Time budget
- expected: 75m
- stuck: 150m
