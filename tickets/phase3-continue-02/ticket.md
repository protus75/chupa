---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- merge-queue

## Context
- tests/test_seeded_phase3_core.py

## Plan contract
- 19.L
- 19.P3
- section 13

## Goal / Why
Continue the Phase 3 registry chain after `merge-queue`. This pass authors only the next admission, `rework-stage`, and `phase3-continue-03`, leaving both new `ticket.md` files uncommitted for Check seed-path review and ticket-plane lift. `tests/test_seeded_phase3_02.py` owns this pass's authoring-time pins and uses the merged `tests/test_seeded_phase3_core.py` as its idiom.

The next admission is the registry's `rework-stage` row alone: known-deep, `high`/`high`, with its exact `does`, cited sections 4, 9, and 11, and fence floor. It depends on `merge-queue`. The successor depends on `rework-stage`, fences `tickets` and its own new `tests/test_seeded_phase3_03.py`, and embeds a merged earlier seeding test as its idiom, never the test created in its own admission.

After that next admission, the still-unseeded registry suffix, in order, is: thresh-runtime, dispatch-admission-boundary, dispatch-config-snapshot, scheduler-activation, merge-queue-activation, rework-activation, background-consumers, control-inbox, dispatch-pause-boundary, pause-resume-activation, admission-holds-activation, kill-signal-journal, kill-executor-abort, kill-worker-stop, kill-failure-suppression, kill-cli-activation, heartbeat, restart-timers, flake-detection, flake-release, journal-roll, storm-ledger, storm-producer-wiring, storm-notification-activation, storm-dispatch-hold, checkpoint-push, serve-activation, serve-merge-admission, worker-recovery-disposition, outbox-only-admission, daemon-soak, daemon-soak-runner, soak-run, phase3-exit. The successor carries this shrinking suffix; it does not author any suffix payload in this pass.


Seed-writing checklist (each item is a requisition_review snag this lineage already drew; satisfy all before Check):
- `rework-stage` is a CONSTRUCTION row adding `chupa/rework.py`: name a criterion and test for the 19.L dormancy observable (the transitive `chupa.*` import closure from `chupa/__main__.py`, recognizing `import chupa.x` and `from chupa import x`, excludes `chupa.rework`). Any change to an already-reachable module (e.g. `chupa/drain.py`) instead names a BEHAVIORAL observable: no production caller of the new seam, proven over the CLI composition root.
- Every invariant the seed states or cites names its test AND its durable record (the journal event type and body keys, or the constant), e.g. the escalate rung recorded via `caps.consume`, the supersedes map's shape, the approval record a successor needs, and the `ticket_intake` body (never `seeded_by`, which merged code treats as seed lineage).
- `phase3-continue-03` states its next admission paragraph like this one: `thresh-runtime` alone, tier from the registry `deep` flag (`deep: true` -> `high`/`high`), its exact `does`, cited section 6, and its fence floor copied VERBATIM from `BEGIN_REGISTRY_P3`; plus its successor `phase3-continue-04` (`medium`/`medium`, depends on `thresh-runtime`, fences `tickets` and its new `tests/test_seeded_phase3_04.py`, idiom a merged earlier seeding test). Its criterion 1 names those tiers, the fence floor, and the cited section.
- After editing any seed, rerun `tests/test_seeded_phase3_02.py` and update its authoring-time render pins.

## Scope in / Scope out
- In: parse `BEGIN_REGISTRY_P3` straight from `CHUPA_PLAN.md`; author the next row and one successor under 19.L's dependency, fence, Context, authoring-headroom, and seeding-test rules.
- In: `tests/test_seeded_phase3_02.py` pins only `rework-stage` and `phase3-continue-03` by identity, edges, frontmatter, registry floor, Context closure, and authoring-time render arithmetic.
- Out: Phase 3 machinery and every row after `rework-stage`.

## Scope fence
- tickets
- tests/test_seeded_phase3_02.py

## Acceptance criteria
1. `uv run pytest -q tests/test_seeded_phase3_02.py` passes for exactly `rework-stage` and `phase3-continue-03`, including `rework-stage` at `high`/`high` and the registry row's fence floor and cited sections.
2. `tickets/rework-stage/ticket.md` and `tickets/phase3-continue-03/ticket.md` are new, uncommitted, lint-valid `confirmed` seeds with their required dependency edges and shrinking suffix; each fits section 8 headroom by the authoring-time sizes recorded in `tests/test_seeded_phase3_02.py`.
3. `uv run pytest -q` exits 0 without removing or skipping a test; Check records two `requisition_review` approvals and lifts them in one `chupa(phase3-continue-02): seeds` commit.

## Verification
```
uv run pytest -q tests/test_seeded_phase3_02.py
uv run pytest -q
```

## Definition of rejected
Reject if this pass authors a suffix payload, copies the registry into a repo file, commits a seed on its code branch, or changes outside the fence.

## Time budget
- expected: 60m
- stuck: 90m
