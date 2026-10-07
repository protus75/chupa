---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: seed
state: confirmed
---

## Depends on
- phase3-continue-06

## Context
- chupa/merge.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_daemon_composition.py
- chupa/runner.py

## Plan contract
- 19.I
- 19.P3.merge-queue-activation

## Goal / Why
The existing production pipeline binding composes its real MergeQueue while bootstrap run/drain retain inline admission.

## Scope in / Scope out
- **Owner:** `chupa/merge.py` owns the production pipeline admission factory `compose_pipeline(ctx, *, escalate) -> MergeQueue`, returning the existing `MergeQueue` constructed with the pipeline's `StageContext` and the required keyword consumer unchanged. `chupa/mergequeue.py` retains sole ownership of serial admission, conflict resolution, integration checks, and queue state; no admission algorithm is copied into the factory. `chupa/runner.py` owns the existing production provider/stage binding (`pipeline` and `bind`) and inline call from `drive` to `merge`; `bind(checkout, llm)` builds a synchronous no-op escalation consumer and calls `compose_pipeline(ctx, escalate=consumer)` once after constructing its context, then returns the existing dispatch lambda. `pipeline(checkout)` and `bind(checkout, llm)` keep their signatures and returned `Dispatch` contract; `Checkout` gains no escalation field. The factory returns the queue directly; no callable attribute or StageContext/driver slot is added. No new engine module is introduced. Under `19.L` caller/composition closure, the activation seed adds `chupa/runner.py` to the registry fence floor and its Context/on-demand partition, and records that addition in its seeding test. The registry's `tests/test_daemon_composition.py` is the production harness landed by scheduler activation; extend that harness rather than creating a parallel graph.
- **Records:** Reuse the existing `StageContext` and its config, Git, filesystem, process exec, driver, clock, journal, Effects, and spool; the composed queue shares these exact instances with the pipeline. Preserve `MergeQueue(ctx, *, escalate)` and its injected synchronous `Callable[[Event], None]` consumer. Production's no-op returns `None` without writing, notifying, or otherwise handling the event: `MergeQueue._signal` already journals it before invoking the consumer. Until `19.P4`'s `notify-transport`, section 13's escalations remain journaled signals only. Direct factory callers must supply `escalate`; there is no default consumer. `admission-holds-activation` later adds the separate shared control inbox at every direct factory caller, as its registry row requires; the no-op escalation consumer neither constructs nor replaces that inbox. A freshly composed queue has `pending: {}`, `active: None`, `paused: false`, and `red_stems: []`; these remain memory-only. `offer(ticket, *, attempt)` stores the parsed `Ticket` and integer attempt by stem; `process()` returns `list[StageResult | ConflictHandoff]`. Ordinary results remain `ok` with `Admission` or `gate_failed` with no artifact; `Admission` retains `stem`, real `commit`, original `reviewed_sha`, and existing provenance. `ConflictHandoff` retains `stem`, `reviewed_sha`, sorted unique `conflicted_paths`, `findings`, and `approval_invalidated: true`; it is an in-memory result, never a new stage outcome or durable artifact.

  Activation introduces no event, signal, body key, frontmatter value, config key, or constant. Existing queue writers remain unchanged: `CONFLICT_FACTS = "merge_conflict_facts"` with `{kind, conflicted_paths, resolving_rung: none | mechanical | rework, strategy_paths, integration_red_paths}`; `RED_STREAK = "merge_red_streak"` with `{kind, stems, limit: 3}` and `RED_STREAK_LIMIT = 3`; `TREE_MISMATCH = "merge_tree_mismatch"` with `{kind, checked_tree, main_tree}`. Each is an `EventType.SIGNAL` with envelope ticket stem and null key, written only when the queue actually processes an admission. `merge.write_squash` remains the sole squash Effect and merged-transition writer (`merge/<stem>/<attempt>`, body `{to: merged, commit, reviewed_sha}`); composition writes none of these records.
- **Observable:** The queue becomes reachable through the production CLI's transitive import closure and is constructed by the production pipeline factory, using the actual pipeline context and supplied escalation consumer. Factory construction offers no ticket, performs no git operation or verification, emits no journal record, invokes no escalation, and starts no background task. The production harness wraps the real `compose_pipeline` at `runner.bind`'s call site, delegates with the exact context and consumer received, captures its returned queue, and returns that same queue to the caller. It exercises the real binding (directly with a scripted LLM or through the daemon's injected `prepare` seam), then explicitly offers/processes a reviewed candidate on the captured queue; it never substitutes a fake factory or constructs a second test-only queue. `build_daemon_core` and `prepare` continue handing out only the dispatch callable; capture occurs when preparation reaches `bind`, not when the daemon core is built. Direct harness exercise proves composition, not daemon routing.

  Bootstrap `run` and `drain` continue calling the existing inline `merge(ctx, ticket, *, attempt)` and retain its restore/rebase/regate, pinned approval, seed safety, base-red attribution, squash trailers, merged transition, and retirement behavior. They neither offer to nor process the composed queue and acquire no daemon holds. Daemon-mode routing belongs to `serve-merge-admission`; owned background consumption belongs to `background-consumers`; Rework handoff consumption belongs to `rework-activation`; identity-bound red-streak/tree-hash release belongs to `admission-holds-activation`. Composition does not activate these behaviors or notification transport. Migrate `tests/test_mergequeue.py::test_merge_queue_is_dormant` from its negative import-closure assertion to positive production reachability, preserving its inline-admission/no-conflict-facts proof; migrate any queue-absence assertion in the production composition harness in the same change.
- **Tests:** `tests/test_daemon_composition.py` adds named obligations `test_production_pipeline_composes_merge_queue` (real production binding, shared context/seams, fresh queue state, captured factory return, and identity of the required consumer passed by `bind`; invoking that production no-op returns `None` with no effect, while a direct factory call preserves a supplied recording consumer unchanged); `test_merge_queue_composition_has_no_side_effects` (no offer/process, git/verification, event, escalation, or background task at construction); and `test_composed_merge_queue_admits_reviewed_candidate` (queue captured from the real factory call during that binding, real disposable git repo, existing integration path, real commit/original reviewed SHA, one merged transition, retirement). In `tests/test_mergequeue.py`, replace the dormancy assertion with `test_merge_queue_is_reachable_from_production`, with a removed import edge proving the positive scan discriminates, and retain the inline/no-conflict-facts behavior as `test_inline_admission_does_not_use_merge_queue`. `tests/test_merge.py` adds `test_bootstrap_pipeline_keeps_inline_admission`, driving the production binding with a scripted LLM and proving queue offer/process are never invoked. Keep all existing queue algorithm and inline merge tests green, particularly approval carry, seed safety, base-red policy, lifted ticket-plane restore, and conflict abort. Verification runs `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py`; the last two are unchanged preservation suites. Use injected seams and disposable repos, never real-model calls or wall-clock waits.

CALLER CLOSURE adds chupa/runner.py: bind is the existing production composition caller and must construct the queue. No other bind/pipeline caller is forced to change because their signatures and Dispatch return remain unchanged. tests/test_mergequeue.py fences the predecessor test_merge_queue_is_dormant; tests/test_daemon_composition.py fences any queue-absence assertion. Migrate only these negatives, retaining inline admission and no conflict facts.

Out: other Phase 3 machinery, notify transport, daemon admission routing, background consumer startup, controls and holds. Keep bootstrap inline admission, accounting, reconciliation, lock lifetime and terminals. Preservation suites in Verification remain unchanged and are neither fenced nor embedded.

## Scope fence
- chupa/merge.py
- tests/test_merge.py
- tests/test_mergequeue.py
- tests/test_daemon_composition.py
- chupa/runner.py

## Acceptance criteria
1. `uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py` exits 0 through the real production binding and existing tests/test_daemon_composition.py harness, proving every named Tests obligation and transition described above.
2. `uv run pytest -q` exits 0 with existing invariants preserved and no test removed or skipped.
3. `tests/test_daemon_composition.py` proves shared seams, exact record custody, construction without side effects and unchanged bootstrap inline admission; deliberately removing or misordering production wiring makes the applicable named invariant fail.

## Verification
```
uv run pytest tests/test_merge.py tests/test_mergequeue.py tests/test_daemon_composition.py tests/test_cli.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
Stop with premise_failed if a criterion forces a path outside the fence or the governing entry omits a needed fact; name the missing contract for section 11.4 hardening. Refuse replacement graphs, invented records, unreviewed ticket changes, and production behavior outside this admission.

## Time budget
- expected: 60m
- stuck: 90m
