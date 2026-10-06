---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- daemon-scheduler
- seed-successor-proof

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.P3
- section 13

## Goal / Why
Continue the Phase 3 registry chain after the core admission. This pass authors only the next admission, `merge-queue`, and `phase3-continue-02`, leaving both new `ticket.md` files uncommitted for its Check seed-path review and ticket-plane lift. `tests/test_seeded_phase3_01.py` owns this pass's authoring-time pins and uses the merged core seeding test as its idiom.

The next admission is the registry's `merge-queue` row alone: known-deep, `high`/`high`, with its exact `does`, `cite` sections 9 and 10, and fence floor. Its owner is `chupa/mergequeue.py`; `chupa/merge.py` and `chupa/git.py` own the existing seams it changes. It depends on this continuation. The successor `phase3-continue-02` depends on `merge-queue`, fences `tickets` and its own new `tests/test_seeded_phase3_02.py`, and embeds `tests/test_seeded_phase3_01.py` as its idiom.

After that next admission, the still-unseeded registry suffix, in order, is: rework-stage, thresh-runtime, dispatch-admission-boundary, dispatch-config-snapshot, scheduler-activation, merge-queue-activation, rework-activation, background-consumers, control-inbox, dispatch-pause-boundary, pause-resume-activation, admission-holds-activation, kill-signal-journal, kill-executor-abort, kill-worker-stop, kill-failure-suppression, kill-cli-activation, heartbeat, restart-timers, flake-detection, flake-release, journal-roll, storm-ledger, storm-producer-wiring, storm-notification-activation, storm-dispatch-hold, checkpoint-push, serve-activation, serve-merge-admission, worker-recovery-disposition, outbox-only-admission, daemon-soak, daemon-soak-runner, soak-run, phase3-exit. The successor carries this shrinking suffix; it does not author any suffix payload in this pass.

## Scope in / Scope out
- In: parse `BEGIN_REGISTRY_P3` straight from `CHUPA_PLAN.md`. Author the next row and one successor, respecting 19.L's dependency, fence, Context, authoring-headroom, and seeding-test rules.
- In: `tests/test_seeded_phase3_01.py` pins only `merge-queue` and `phase3-continue-02` by identity, edges, frontmatter, registry floor, Context closure, and authoring-time render arithmetic.
- Out: Phase 3 machinery and every row after `merge-queue`.

## Scope fence
- tickets
- tests/test_seeded_phase3_01.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_01.py` passes for exactly `merge-queue` and `phase3-continue-02`, including `merge-queue` at `high`/`high` and the registry row's fence floor and cited sections.
2. `tickets/merge-queue/ticket.md` and `tickets/phase3-continue-02/ticket.md` are new, uncommitted, lint-valid `confirmed` seeds, with the dependency edges and the shrinking suffix stated above; each fits the section 8 headroom by the authoring-time sizes recorded in `tests/test_seeded_phase3_01.py`.
3. `uv run pytest -q` exits 0 without removing or skipping a test; Check records two `requisition_review` approvals and lifts them in one `chupa(phase3-continue): seeds` commit.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_01.py
uv run pytest -q
```

## Definition of rejected
Reject if this pass authors a suffix payload, copies the registry into a repo file, commits a seed on its code branch, or changes outside the fence.

## Time budget
- expected: 60m
- stuck: 90m
