---
state: confirmed
source: human
priority: P1
kind: chore
---

## Depends on
- merge-skip-unchanged

## Context
- chupa/mergequeue.py
- chupa/serve.py
- chupa/control.py
- chupa/baseline.py
- chupa/__main__.py
- tests/test_supervised_merge_hold.py
- tests/test_mergequeue.py
- chupa/author.py

## On-demand
- chupa/merge.py
- chupa/daemon.py
- chupa/reconcile.py
- chupa/runner.py
- chupa/notify.py
- chupa/storm.py
- eval/host_loop.py
- eval/daemon_soak.py
- eval/reliability_battery.py
- tests/test_control.py
- tests/test_control_cli.py
- tests/test_serve.py
- tests/test_restart_timers.py
- tests/test_reconcile.py
- tests/test_drain.py
- tests/test_merge.py
- tests/test_host_loop.py
- tests/test_daemon_soak_runner.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Goal / Why
`serve` holds every green merge candidate for an operator `confirm <stem>` unless a recorded GO review baseline covers the review model (the "supervised merge hold"). `drain` merges the same work, judged by the same reviewer, with no hold. A host that moves from drain to serve therefore turns every merge into a manual step, so hosts stay on drain and start and stop it by hand. The hold adds no gate that drain lacks; the safety tier, integration tier and red-streak pause all still run without it.

After this change the serve merge queue never holds a candidate for supervision: a candidate that passes the safety and integration tiers merges. The GO baseline keeps its other job, deciding whether Author-written tickets start as `draft` or `confirmed` (`chupa/author.py`); that does not change.

## Scope in / Scope out
- In: `chupa/mergequeue.py`: delete the supervision step. Remove `MergeQueue.supervised`, `MergeQueue.held`, `_policy`, the held-candidate re-check loop in `process()`, and the `merge.Held` return. Every regate receipt is written `admission: "READY"`, `reason: "bootstrap"`. The receipt validator still accepts the historical `HELD` receipts and reason values already in journals, so an existing journal folds.
- In: `chupa/serve.py`: stop setting `supervised`. `reconstruct_admissions` no longer rebuilds held merges. A stem whose latest regate receipt is `HELD` with no release is re-offered to the merge queue on start and re-gated (rebase and both tiers) like any other candidate.
- In: `chupa/control.py` and `chupa/__main__.py`: remove the held-merge release path, which is the `AdmissionRequest` branch with a non-null `hold_id`, `MERGE_RELEASE`, `releases()`, `held_admissions()` and the `inbox.admissions` predicate. Draft confirmation through the inbox (`hold_id` null) keeps working unchanged. Pause/resume/kill holds and their `hold_id` are not touched.
- In: `chupa/baseline.py`: delete `review_coverage`; it has no other caller. `resolve_baseline` stays.
- In: the remaining files in On-demand that import a removed name: delete the dead branch, never shim it. Tests whose only subject is the supervised hold are deleted (`tests/test_supervised_merge_hold.py`); tests that use its helpers for other subjects keep their subject with a non-supervised setup.
- In: `docs/how-chupa-works.md`:
  - section 2.1: the `confirm` row no longer says "or releases a held merge";
  - section 7.2: remove "rebuilds held merges" and "held merge" from the dispatch wait list;
  - section 7.2.1: remove step 5 and renumber;
  - section 9.6: the baseline gates Author starting state only.
- In: `docs/host-contract.md` "Pending cutover contract": state that serve merges without an operator confirm, and that GO governs only Author starting state.
- Out: Author starting state and the GO baseline record; draft confirm; pause/resume/kill; red-streak and storm holds; the eval harness; drain.

## Scope fence
- chupa/mergequeue.py
- chupa/serve.py
- chupa/control.py
- chupa/baseline.py
- chupa/__main__.py
- chupa/merge.py
- chupa/daemon.py
- chupa/reconcile.py
- chupa/runner.py
- chupa/notify.py
- chupa/storm.py
- eval/host_loop.py
- eval/daemon_soak.py
- eval/reliability_battery.py
- tests
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. In serve's merge queue, with no `BASELINE_SIGNAL` in the journal, a candidate that passes both tiers squash-merges on the first `process()` pass. Its regate receipt is `READY`/`bootstrap`, and no confirm is involved. A test fails if the candidate is held. Checked by `uv run pytest tests/test_mergequeue.py`.
2. A journal with a historical `HELD` regate receipt and no release, plus a retained worktree, restarts under serve. The stem is re-gated and merged without a confirm. A test fails if the stem stays held or the journal fails to fold. Checked by `uv run pytest tests/test_restart_timers.py`.
3. A committed draft confirmed through the inbox while serve runs is still promoted to `confirmed` exactly once. Checked by `uv run pytest tests/test_control.py tests/test_control_cli.py`.
4. With GO absent, Author still writes `draft` for sources whose policy depends on GO. Checked by `uv run pytest tests/test_author.py`.
5. `docs/how-chupa-works.md` sections 2.1, 7.2, 7.2.1 and 9.6 and `docs/host-contract.md` no longer describe a supervised merge hold.
6. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_mergequeue.py tests/test_restart_timers.py tests/test_control.py tests/test_control_cli.py tests/test_author.py
uv run pytest -q
```

## Definition of rejected
A config field, flag or environment variable that re-enables the merge hold; a compat shim around a removed name; Author starting state or draft confirm changes; a historical journal with `HELD` receipts no longer folds.

## Time budget
- expected: 90m
- stuck: 180m
