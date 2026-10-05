---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- author-stage

## Context
- chupa/gates.py
- chupa/driver.py
- chupa/llmeffect.py

## On-demand
- chupa/stages.py

## Plan contract
- 19.L
- 19.P2
- section 7
- section 8
- section 9
- section 13

## Goal / Why
`requisition_review` exists as a pure engine review call over ONE authored ticket (section 7): grammar-invalid work never spends a call, an over-headroom base Implement render is a mechanical `snag`, and otherwise one model call returns a closed `approve | snag | rma` verdict with findings. A `requisition_review` gate is registered over that verdict. Nothing calls it yet.

Why: the Requisition gate is grammar only (section 13). A machine-authored ticket whose fence misses a criteria-forced file, whose criteria contradict merged behavior, or whose render cannot fit is discovered only when it runs, as a premise park (19.L seed buildability). The call lands first, with no consumers, so the Author path and the seed path (the next two seeds) wire the same call rather than each growing its own.

Owners (19.P2 NAMES): `chupa/requisition.py` / `tests/test_requisition.py` own the review target resolver, the render-feasibility measurement, the call, the verdict model, and the gate. `specs/requisition_review.md` is the one spec. `chupa/stages.py` owns the Implement render inputs, so the base render is measured through a pure helper extracted there, never a second copy. `chupa/driver.py` owns the stuck-budget race.

## Scope in / Scope out
- In: `chupa/stages.py`: the Implement inputs assembly (`ticket`, `plan_contract`, `context`) moves into a pure `implement_inputs(repo, plan, ticket_text, ticket, context_files) -> dict[str, str]` that `implement_stage` calls. Implement renders stay byte-identical.
- In: `chupa/driver.py`: `_race` is renamed in place to the public `race`, every call site updated.
- In: `specs/requisition_review.md`, lint-clean under `lint_spec`: frontmatter `llm_surface: requisition_review`, `consumes: ticket`, `emits: {approve: requisition-approval, snag: requisition-snag, rma: requisition-rma}`, `tier: high`, `effort: high`, `gates: [requisition_review]`, `version: "1.0"`, exactly the sections Role, Task, Inputs, Output format, On-failure, and data blocks `ticket`, `plan_contract`, `context`, `render`, `retry_findings` in that order, each untrusted. The Task directs the read-only reviewer to judge the ticket BUILDABLE against the shipped engine and the plan it renders (section 7) and to `snag` on:
  - a fence missing a forced file: it traces the reference closure of every symbol the scope-in changes (callers and importers, aliases included) and the recorded-value closure of every constant or version it bumps (section 9), and fails a fence that hooks an outside-owner seam;
  - a criterion contradicting merged behavior, or mutually unsatisfiable criteria;
  - a stated or cited invariant with no named test obligation;
  - for a phase-exit or seeding ticket, an exit criterion reading a signal or artifact no deliverable of its phase emits.
  `rma` is reserved for a plan defect the author cannot fix.
- In: `chupa/requisition.py`:
  - `RequisitionReply`, closed: `verdict` (`approve | snag | rma`), `summary` (non-blank), `findings` (list of `Finding`; empty exactly for `approve`).
  - `RequisitionVerdict(Artifact)`: `stem`, `ticket_sha` (the git blob SHA of the reviewed text, computed with `hashlib` over `blob <len>\0<bytes>`), `verdict`, `summary`, `findings`, `render_chars`, `mechanical` (nullable), `spec_version`, `provider`, `model` (both nullable).
  - `review_target(repo, stem, text) -> Ticket`: the complete ticket-schema admission predicate, `validate_ticket` with reserved stems included; a `TicketInvalid` propagates and no call is made.
  - `base_render_chars(repo, plan, ticket, text, specs_dir) -> int`: the length of the implement spec rendered at `max` effort through `implement_inputs`, with `retry_findings` `none` and no prior attempts (section 8 AUTHORING HEADROOM).
  - `REQUISITION_STUCK_S = 600.0`.
  - `async def review_ticket(driver, *, repo, plan, stem, text, specs_dir, tier, stem_slot, run_seq, attempt, call_seq) -> RequisitionVerdict`. It resolves the target, then measures the render: over `REQ_RENDER_HEADROOM * RENDER_BOUND_CHARS["max"]` returns `snag` with one finding code `render_feasibility` (paved road: shrink or split at authoring), `mechanical: "render over headroom"`, and no call. Otherwise it spools the rendered prompt, makes ONE call through `llm_call` keyed `llm/<stem_slot>/<run_seq>/requisition_review/<attempt>/<call_seq>` raced by `driver.race` against `REQUISITION_STUCK_S`, and validates the fence-unwrapped reply. An invalid reply, a timeout, or a provider error returns `snag` with one finding code `requisition_review` naming the failure and `mechanical` set; it never returns `approve`. Callers choose the key identities, so each consumer keys its own calls.
  - `RequisitionGate` (code `requisition_review`) over a `RequisitionVerdict`: pass exactly for `approve`, else fail with the verdict's findings. It passes `lint_gate`.
- Out: any caller (the Author path and the seed path are the next two seeds), a terminal-findings driver hook, config routing rows (an unrouted surface inherits `review`, section 5), a mechanical closure analyzer (section 18), and every merge-time use.

## Scope fence
- chupa/requisition.py
- specs/requisition_review.md
- tests/test_requisition.py
- chupa/stages.py
- chupa/driver.py

## Acceptance criteria
1. The `python -c` command in `## Verification` exits 0: `specs/requisition_review.md` loads with `llm_surface == "requisition_review"` and the five data blocks in order.
2. `tests/test_requisition.py` proves `review_ticket` with a FakeLLM: an `approve` reply yields `verdict == "approve"` and a call keyed `llm/s/0/requisition_review/1/1`; a `snag` reply carries its findings; a reply outside the vocabulary yields `snag` with `mechanical` set and never `approve`.
3. `tests/test_requisition.py` proves zero requests for a grammar-invalid ticket (`TicketInvalid`) and for a reserved stem, and proves a ticket whose Context pushes `base_render_chars` over the headroom returns `snag` with a `render_feasibility` finding and zero requests.
4. `tests/test_requisition.py` proves `base_render_chars` equals the length of the production Implement render of the same ticket at `max` effort, and `RequisitionGate` passes `lint_gate` and fails a `snag` verdict with its findings.
5. `uv run pytest -q tests/test_stages.py tests/test_driver.py` passes with no edit to those files.
6. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "from pathlib import Path; from chupa.specs import load_spec; s = load_spec(Path('specs/requisition_review.md').read_text()); assert s.meta.llm_surface == 'requisition_review' and s.inputs == ('ticket', 'plan_contract', 'context', 'render', 'retry_findings')"
uv run pytest -q tests/test_requisition.py
uv run pytest -q tests/test_stages.py tests/test_driver.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- Any path returns `approve` without a schema-valid model `approve`.
- A grammar-invalid or over-headroom ticket spends a model call.
- A second Implement render-input assembly exists, or an Implement render changes.
- Anything outside `tests/` calls `review_ticket`.
- The diff touches a file outside the fence.

## Time budget
- expected: 75m
- stuck: 150m
