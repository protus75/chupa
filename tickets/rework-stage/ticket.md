---
priority: P1
kind: feature
agent_tier: high
agent_effort: high
source: seed
state: confirmed
---

## Depends on
- phase3-continue-02

## Context
- chupa/mergequeue.py
- chupa/artifacts.py
- chupa/driver.py
- chupa/requisition.py

## Plan contract
- 19.I
- 19.P3.rework-stage
- section 4
- section 9
- section 11

## Goal / Why
Build the dormant Rework stage: direct calls through the existing Driver return reviewed update/split/escalate orders without mutating tickets, and a separate post-publication supersedes writer exposes reusable dependency folds.

The registry's deep: true row crosses the Driver, ticket grammar/review, journal folds, and serial admission handoff; this is the starting-capability evidence for high/high. Construction remains sub-production until rework-activation.

## Scope in / Scope out
In: implement exactly the complete own-entry-unit contract below, using existing seams and owners. Read the grammar, renderer, journal, and failure-spine owners before using their operations. The fenced existing queue is embedded; the remaining floor paths are new outputs. No closure addition is needed: no public signature or production caller changes, no earlier assertion flips, and no activation occurs.

- **Owner:** `chupa/rework.py` owns the dormant Rework LLM stage, its composite rework-order schema, ticket-proposal validation, and supersedes-map writer and folds. `specs/rework.md` owns the governed `rework` prompt. `chupa/mergequeue.py` retains ownership of `ConflictHandoff` and admission unwind; it never calls Rework inline. The existing Driver owns model calls, effects, spools, schema re-prompts, and cost; `chupa/tickets.py` owns ticket grammar and `chupa/requisition.py` owns feasibility review. The existing failure spine retains terminal writes, cap draws, and capability selection. Construction exercises Rework directly; production consumption and ticket-plane application belong to `rework-activation`.
- **Records:** Consume the original parsed `Ticket` and its committed text, a snag list of existing `Finding` records (`code`, nullable `path` and `line`, `message`, `paved_road`, nullable `kind`), and an optional queue-owned `ConflictHandoff`. The handoff has exactly `{stem: str, reviewed_sha: str, conflicted_paths: list[str], findings: list[Finding], approval_invalidated: true}`; its stem must match the ticket, paths are sorted and unique, and its approval is never reusable. The caller supplies the run sequence/attempt and effective tier/effort; Rework does not allocate a run, reset a budget, or select its own capability.

  The model reply is a strict, extra-forbidden `{action: update | split | escalate, tickets: list[{stem: nonblank str, ticket: nonblank str}]}`. `update` carries exactly one proposal for the original stem; `split` carries at least two distinct fresh successor stems, never the original; `escalate` carries no tickets. Unknown actions or malformed combinations follow the Driver's bounded schema re-prompt loop. `chupa/rework.py` stamps the reply into one `ReworkOrder` derived from the existing `Artifact`, adding `stem`, integer `attempt`, `action`, and `tickets`; inherited `artifact_schema_version`, `produced_by_spec_version`, and `produced_at_sha` retain their existing meanings, with the SHA read from the supplied workspace's HEAD. This is one composite artifact, not a new Outcome or verdict-keyed artifact family. Success returns existing `StageResult(outcome: ok, artifact: ReworkOrder)`; failures retain the existing outcome vocabulary and paved findings. No new OUTBOX filename or KNOWN-artifact registration is introduced by construction.

  Ticket proposals use the existing closed frontmatter and body grammar. An update preserves the original `source` (`human`, `seed`, or `box:<class>`), `state: confirmed`, and starting `agent_tier` and `agent_effort` (each `low | medium | high | max`); a split inherits those values. Other content may change only to realize the rework order's narrowed or divided original goal. No escalation metadata enters frontmatter. Successor stems pass `stem_findings` and must be absent from both the repository's ticket directories and journal identities; proposals have no self-dependency or cycle, and a split successor must not depend on the superseded original. Validate every proposal with `validate_ticket` and review each separately through existing `review_ticket` before accepting the order. For sibling dependencies, use a disposable proposal tree containing all proposed successors and the original repository material required by validation/rendering; fresh-stem collision checks still read the original repository and journal. This tree is validation material only and never publishes a ticket or changes main. A snag feeds findings back; an RMA returns a paved failure for the existing failure spine, never an unreviewed ticket or automatic retry around the refusal. Construction returns reviewed proposals without editing ticket files, committing ticket-plane output, or retiring the original.

  `chupa/rework.py` owns `REWORK_ORDER = "rework_order"` and `SUPERSEDES = "supersedes"`. Emit one `EventType.SIGNAL` per accepted order with envelope `ticket: <original stem>`, `key: null`, body `{signal: rework_order, attempt: int, action: update | split | escalate}`; failed validation/review emits no accepted-order signal. The supersedes writer is a separate post-publication operation: after the lock-owning caller has committed every reviewed successor, append under the original stem, with `key: null`, `{signal: supersedes, successors: list[str]}`. Successors are nonempty, sorted, unique, and exclude the original. No map is emitted for update, escalation, or failed successor publication. Repeating the same map is a no-op; a conflicting replacement, self-edge, or transitive cycle refuses with a paved finding. The journal is the authority, never a side file or new frontmatter key. Map readers use envelope `ticket` as the old stem, resolve nested maps transitively, satisfy an original dependency only when every leaf successor is settled (`merged` or `already_satisfied`, matching existing `drain.SETTLED`), and propagate a killed (`rejected`) or `abandoned` leaf back to its superseded ancestors. Ordinary retryable failures remain unsettled, not dead; read latest `state_transition` body `to` by envelope `ticket` through existing `last_states`. These state records retain their existing writers. These are dormant reusable folds; construction does not change dispatch or the existing dead-dependency producer.
- **Observable:** `specs/rework.md` has `llm_surface: rework`, `consumes: snag-list`, `emits: rework-order`, `gates: [ticket_schema, requisition_review]`, starting `tier: high`, `effort: high`, and `version: "1.0"`, plus the existing five required prose sections. Render ticket, findings, conflict context, and re-prompt findings only through the existing spec renderer's data blocks and bound; all are untrusted evidence. Invoke the stage through `Driver.run` with surface `rework`, the caller's effective capability and time budget, and existing injected seams. Update produces a revised ticket proposal; split produces independently buildable reviewed successors and exposes post-publication supersession; escalation recommends the existing deterministic ladder without choosing or writing a rung. The failure-spine owner alone later consumes that recommendation through `next_rung` and the existing retry `cap_consumed` record (`cap`, `ticket_sha`, optional `rung: {tier, effort}`); Rework itself writes neither caps nor terminals.

  A conflict handoff is consumed only after admission has returned, aborted any unfinished rebase, and released its serial admission boundary. Rework sees the conflicted paths and original findings and preserves the invalidated-approval requirement: later implementation must pass Check and fresh Review before re-admission. It performs no conflict-only micro-rework, branch repair, squash, or reuse of the former approval. Both the transitive CLI import closure and the admission path remain free of Rework calls. Until `rework-activation`, production diagnosis `split` still routes to the Reject queue and the bootstrap drain's inline admission is unchanged.
- **Tests:** `tests/test_rework.py::test_update_order_is_reviewed_without_ticket_mutation` proves the single-original-stem proposal, preserved starting frontmatter, real grammar/feasibility paths, and no ticket writes. `test_split_order_requires_fresh_buildable_successors` proves distinct fresh stems, inherited frontmatter, sibling dependency validation in the disposable tree, dependency closure, and per-successor review; `test_rework_refuses_invalid_or_unreviewed_orders` covers unknown actions, cardinality, extra fields, identity collisions, invalid tickets, snag re-prompts, RMA, and no accepted-order/map signal on refusal. `test_escalate_order_does_not_edit_capability_or_draw_caps` proves an empty proposal list and unchanged frontmatter, rung history, and cap counts. `test_rework_spec_render_and_driver` pins the spec lint, deterministic fixture render, quoted payload delimiters, render-bound refusal before a model call, Driver schema re-prompts, artifact provenance, existing outcomes/cost, and exact accepted-order signal. `test_conflict_handoff_consumed_after_admission_unwinds` drives the real dormant queue's unresolved-conflict return and then Rework with a fake LLM, asserting abort and slot release precede the call, context matches the handoff, approval stays invalidated, and main/branch are untouched. `test_supersedes_record_after_publication_is_idempotent` proves exact journal shape, publication-before-map, no map after failed publication or non-split orders, replay without duplication, and conflicting/self/cyclic-map refusal. `test_supersedes_dependency_folds` covers nested all-successors settlement, an unsettled or retryable-failure successor, and a rejected/abandoned leaf propagating to original dependents. `test_rework_is_dormant` uses the `19.I` transitive CLI import-closure scan recognizing both import idioms and proves the queue never calls Rework inline; activation must migrate this assertion. Verification runs `uv run pytest tests/test_rework.py tests/test_mergequeue.py` with the latter unchanged as a preservation suite; existing failure-spine tests continue to pin split-to-Reject routing until activation.

Out: production consumption or ticket-plane application (rework-activation owns both); changing the bootstrap inline admission, split-to-Reject routing, capability ladder, terminal/cap writers, or dead-dependency producer; inline queue-to-Rework calls; conflict-only repair, squash, prior-approval reuse; new Outcome, frontmatter, OUTBOX registration, config, or side-file authority. Existing mergequeue and failure-spine suites are unchanged preservation suites, neither fenced nor embedded.

## Scope fence
- chupa/rework.py
- specs/rework.md
- chupa/mergequeue.py
- tests/test_rework.py

## Acceptance criteria
1. `uv run pytest tests/test_rework.py tests/test_mergequeue.py` exits 0: test_update_order_is_reviewed_without_ticket_mutation and test_split_order_requires_fresh_buildable_successors prove exact cardinality/identity, preserved starting frontmatter, real grammar and separate feasibility reviews, sibling dependency validation in a disposable proposal tree, and no publication or ticket mutation.
2. `uv run pytest tests/test_rework.py tests/test_mergequeue.py` exits 0: test_rework_refuses_invalid_or_unreviewed_orders covers malformed/extra-field replies, collisions, invalid proposals, snag re-prompts and RMA; test_escalate_order_does_not_edit_capability_or_draw_caps proves the recommendation writes no rung, cap, or terminal.
3. `uv run pytest tests/test_rework.py tests/test_mergequeue.py` exits 0: test_rework_spec_render_and_driver proves the governed spec, golden fixture render, quoted untrusted payloads, pre-call bound refusal, bounded Driver schema re-prompts, artifact provenance, cost/outcomes, and the exact accepted-order signal with no signal on refusal.
4. `uv run pytest tests/test_rework.py tests/test_mergequeue.py` exits 0: test_conflict_handoff_consumed_after_admission_unwinds drives the real dormant queue then Rework, proving abort and serial-slot release before the call, matching handoff context, invalidated approval, and untouched main/branch; test_rework_is_dormant proves the transitive CLI import closure with both import idioms and absence of inline admission calls.
5. `uv run pytest tests/test_rework.py tests/test_mergequeue.py` exits 0: test_supersedes_record_after_publication_is_idempotent proves the exact journal record only after successful successor publication, no map for other actions or failed publication, replay idempotence and conflicting/self/cyclic refusal; test_supersedes_dependency_folds proves nested all-leaf settlement and rejected/abandoned propagation while retryable failures remain unsettled.
6. `uv run pytest tests/test_ladder.py tests/test_drain.py tests/test_merge.py tests/test_driver.py tests/test_requisition.py tests/test_tickets.py tests/test_specs.py` and `uv run pytest -q` exit 0, retaining bootstrap inline admission and split-to-Reject routing. All preservation suites remain unchanged.

## Verification
```
uv run pytest tests/test_rework.py tests/test_mergequeue.py
uv run pytest tests/test_ladder.py tests/test_drain.py tests/test_merge.py tests/test_driver.py tests/test_requisition.py tests/test_tickets.py tests/test_specs.py
uv run pytest -q
```

## Definition of rejected
Reject if Rework mutates tickets, publishes proposals, selects capability or writes caps/terminals, consumes a handoff before admission unwinds, reuses invalidated approval, calls inline from admission, activates production, or edits outside the fence. A missing contract fact returns premise_failed naming 19.P3.rework-stage for section 11.4 hardening; never invent it.

## Time budget
- expected: 60m
- stuck: 90m
