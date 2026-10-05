---
state: confirmed
source: seed
priority: P1
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- spine-caps
- spine-harvest
- spine-harvest-orphans

## Context
- chupa/runner.py
- chupa/artifacts.py
- tests/test_terminal.py
- tests/test_drain_reentry.py

## On-demand
- chupa/stages.py
- chupa/providers.py

## Plan contract
- 19.L
- 19.P2
- section 11
- section 5

## Goal / Why
Every non-ok run terminal makes the sandwich's ONE model judgment (section 11.3): after harvest and the infra draw, and before the terminal `state_transition`, the handler asks the `diagnose` surface "what should happen next?" over the harvested material. The answer is one verdict from the closed vocabulary `retry | escalate | split | reject | abandon-human` plus typed `lessons`. It is journaled, written to `tickets/<stem>/diagnosis.json`, and every later attempt's Implement render carries those lessons in place of that attempt's raw harvest payload.

Why: harvest (`spine-harvest`) preserves what a dying attempt saw, but each re-offer renders it raw, so history grows on exactly the lineages that fail most and nothing distills it into steering. The escalation ladder and Reject queue (the next seed batch) dispatch on this verdict, so the verdict must exist, journaled, first. The caps fire before the call, never model-decided: a spent cap, a gone workspace, `budget_exceeded`, and an over-bound render are MECHANICAL short-circuits that never call the model.

Owners (section 9 ownership law): `chupa/runner.py` owns the terminal handler (`drive`) and therefore the dispatch step: the short-circuits, the cap check, and the `diagnosis` draw through `consume` in `chupa/caps.py` (landed by `spine-caps`). `chupa/stages.py` owns the diagnosis LlmStage builder, the `diagnosis.json` outbox write and its lift through `lift_outbox`, and the `prior_attempts` render. `chupa/artifacts.py` owns the closed `DiagnosisReply` and `Diagnosis` models. `chupa/providers.py` owns routing resolution. `specs/diagnose.md` is the governed, versioned spec for the `diagnose` surface (section 5: a failure-spine substep, never a Stage).

## Scope in / Scope out
- In: `chupa/artifacts.py` gains:
  - `DiagnosisVerdictName = Literal["retry", "escalate", "split", "reject", "abandon-human"]` and `DIAGNOSIS_VERDICTS = get_args(DiagnosisVerdictName)`. This is the one copy of the vocabulary; every consumer imports it.
  - `DIAGNOSIS_MAX_LESSONS = 5` and `DIAGNOSIS_LESSON_CHARS = 300`, engine constants bounding what one attempt adds to every later render.
  - `DiagnosisReply`, the closed model-facing reply: `verdict` (a `DiagnosisVerdictName`) and `lessons` (1 to `DIAGNOSIS_MAX_LESSONS` non-blank strings, each at most `DIAGNOSIS_LESSON_CHARS` characters). Unknown keys are refused. A verdict outside the vocabulary is a validation failure, so the driver's bounded re-prompt loop feeds the error back (section 5 invariant 2).
  - `Diagnosis(Artifact)`, the persisted record: `stem`, `attempt` (the run sequence), `terminal`, `stage` (nullable), `verdict`, `lessons` (possibly empty), `mechanical` (nullable: the short-circuit reason when no schema-valid model verdict exists), `spec_version`, `provider` and `model` (nullable).
- In: `specs/diagnose.md`, frontmatter `llm_surface: diagnose`, `consumes: harvest`, `emits: diagnosis`, `tier: high`, `effort: medium`, `gates: []`, `version: "1.0"`, with exactly the sections Role, Task, Inputs, Output format, On-failure, lint-clean under `lint_spec`. Data blocks, each a lone placeholder line, in this order: `ticket`, `terminal`, `harvest`, `run_record`, `retry_findings`. The Task defines each verdict:
  - `retry`: a fixable oversight the findings now steer, at the same capability.
  - `escalate`: the approach was sound but needs more capability. It RECOMMENDS escalation and never names a tier, effort, or model.
  - `split`: the ticket is too large for one attempt (diff budget, render size, too many boundaries).
  - `reject`: the ticket cannot succeed as written (false premise, contradictory or unsatisfiable criteria).
  - `abandon-human`: only a human can unblock it (credentials, environment outside the engine, cause unreadable from the material).
  The spec marks every data block untrusted, and asks for lessons that are concrete next-attempt steering (what to do or avoid), never a restatement of the failure.
- In: `chupa/providers.py` `resolve`: a surface with no routing row of its own at the asked tier inherits that tier's `review` row (section 5). A surface that has its own row keeps it. When neither row exists, the existing "no routing row" refusal names the asked surface.
- In: `chupa/stages.py`:
  - `DiagnosisMaterial`, a frozen dataclass of `ticket` (ticket.md text), `terminal`, `stage` (nullable), `harvest` (a `Harvest` or None when harvest was skipped or failed), and `run_record` (run.md text or None).
  - `diagnose_stage(spec, material) -> LlmStage`, the ONE diagnosis render: surface `diagnose`, emits `DiagnosisReply`, no gates. `terminal` renders as one line (`<terminal> at <stage>`), `harvest` as the Harvest's JSON (`none` when absent), and `run_record` as its text (`none` when absent). It is pure (no StageContext), so the diagnosis eval reuses it and never copies it.
  - `async def diagnose(ctx, ticket, material, *, attempt) -> Diagnosis`: runs `diagnose_stage` through `ctx.driver.run` at the TICKET's `agent_tier` (a surface invoked for a ticket, section 6) and the spec's effort, with the engine constant `DIAGNOSIS_STUCK_S = 600.0` as its stuck budget. An `ok` reply becomes `Diagnosis` with `mechanical: null`. Any other driver outcome (re-prompts exhausted, `timeout`, `infra_error`) fails closed to `verdict: "abandon-human"`, empty lessons, `mechanical: "no schema-valid verdict (<outcome>)"`, never `retry`. It writes `tickets/<stem>/diagnosis.json` into the worktree outbox and commits it through `lift_outbox(ctx, stem, "diagnosis", attempt=attempt)`.
- In: `chupa/runner.py` `drive`, for a non-ok terminal, the dispatch step between the infra draw and the terminal `state_transition`, in order:
  1. `budget_exceeded` terminal: no diagnosis, no draw, no record.
  2. Over-bound render (a `premise_failed` result carrying a `render_over_bound` finding): no diagnosis, no draw, no record.
  3. Workspace gone (the stem's worktree dir does not exist): record `abandon-human`, `mechanical: "workspace gone"`, no call, no draw.
  4. Any cap spent (`spent(...)` from `chupa/caps.py`, read AFTER this terminal's own infra draw): record `abandon-human` with `mechanical` set to `spent_reason(cap)` verbatim, no call, no draw.
  5. Otherwise draw one `diagnosis` unit through `consume` (with the committed ticket blob SHA, read the way the infra draw reads it), BEFORE the call, so a crash mid-call still spends it, then call `diagnose`. Re-prompts inside the one call draw no further `diagnosis` unit.
- In: every record (model or mechanical) is journaled as ONE `signal` on the stem, body `{"signal": "diagnosis", "attempt": n, "verdict": ..., "lessons": [...], "mechanical": ...}`, before the terminal `state_transition`. Mechanical records with a worktree also write and lift `diagnosis.json`. The terminal `state_transition` body is unchanged.
- In: `prior_attempts` renders each prior attempt whose journaled diagnosis carries lessons as its terminal (`to` plus stage) followed by its lessons, each flattened to one line like `_one_line` does and prefixed `> `, and NEVER that attempt's raw harvest payload. This holds for the immediately prior attempt (in place of the raw `reason`/`diff_stat`/tails `spine-harvest` renders) and for every older one (in place of its one-line pointer). An attempt with no lessons renders exactly as `spine-harvest` left it. The prior terminal's findings items are unchanged.
- In: the tests this behavior contradicts are adapted, with no assertion weakened. FakeLLM scripts in `tests/test_terminal.py`, `tests/test_drain_reentry.py`, `tests/test_caps.py`, `tests/test_harvest.py`, and `tests/test_harvest_orphans.py` gain one diagnosis reply after each non-ok terminal. Their request-count and request-surface assertions filter out the `diagnose` surface. The `tests/test_caps.py` assertion that the `infra` draw lands immediately before the terminal becomes "precedes it, with only this terminal's diagnosis events between".
- Out: dispatching on the verdict (the escalation ladder, Reject-queue routing and its `routed: reject_queue` marker, `split` to Reject, auto-keep, the identical-terminal short-circuit). That is the ladder seed's. Until it lands, every verdict leaves the stem on the existing park and re-offer path, bounded by the journal-derived caps.
- Out: the `budget_exceeded` park and re-entry (its producer ships with the `api` client), the drought exemption, diagnosis of a reconcile-reaped `abandoned` orphan, Suggestion Box filing, and journaling in-stage re-prompts as retry draws.
- Out: the diagnosis real-model eval (the next two seeds) and any `config.yaml` routing row for `diagnose`.

## Scope fence
- chupa/runner.py
- chupa/stages.py
- chupa/artifacts.py
- chupa/providers.py
- specs/diagnose.md
- tests/test_diagnose.py
- tests/test_terminal.py
- tests/test_drain_reentry.py
- tests/test_caps.py
- tests/test_harvest.py
- tests/test_harvest_orphans.py

## Acceptance criteria
1. The first `python -c` command in `## Verification` exits 0: `specs/diagnose.md` loads through `load_spec` with `llm_surface == "diagnose"` and data blocks `ticket`, `terminal`, `harvest`, `run_record`, `retry_findings`. The second exits 0: `DIAGNOSIS_VERDICTS` is exactly the five-verb closed vocabulary in order.
2. `tests/test_diagnose.py` proves routing inheritance through `resolve`. With rows only for `implement` and `review`, `diagnose` at a tier resolves to that tier's `review` (provider, model). A surface with its own row keeps it. With no `review` row at that tier, the refusal names `diagnose`.
3. `tests/test_diagnose.py` drives `chupa.__main__.main(["run", ...])` with a FakeLLM to a review snag, then a diagnosis reply `{"verdict": "retry", "lessons": [...]}`. The journal shows, in order: the harvest commit completion, one `diagnosis` `cap_consumed` carrying the ticket's blob SHA, the `diagnose` LLM effect completion, the `diagnosis` signal (attempt 0, verdict `retry`, those lessons, `mechanical` null), then the unchanged terminal `state_transition`. Exactly one request has surface `diagnose`, at the ticket's `agent_tier`, and its rendered prompt carries the ticket text and the snag finding's message. Main carries `tickets/<stem>/diagnosis.json` in a `chupa(<stem>): diagnosis` commit, and it validates as `Diagnosis`.
4. `tests/test_diagnose.py` proves the closed vocabulary fails closed. A reply with verdict `maybe` is re-prompted with the validation finding. Replies invalid through every re-prompt record `abandon-human` with `mechanical` starting `no schema-valid verdict`. That case draws exactly one `diagnosis` unit, and its record is never `retry`.
5. `tests/test_diagnose.py` proves each mechanical short-circuit makes zero `diagnose` requests and draws zero `diagnosis` units. A pre-spent `diagnosis` cap records `diagnosis cap spent`. An infra cap spent by this terminal's own draw records `infra cap spent`. A gone worktree records `workspace gone`. A `budget_exceeded` terminal and an over-bound-render `premise_failed` record nothing. The test may drive `runner.drive` with a stage seam returning the terminal it needs.
6. `tests/test_diagnose.py` drives `drain` through two diagnosed failures and a green third attempt. The third Implement render's prior-attempts block, between `## Acceptance criteria` and the next ticket section, carries both attempts' lessons prefixed `> `. A unique marker placed only in attempt one's spooled stage output appears in no later render. A prior attempt whose record has no lessons still renders its raw harvest `reason`.
7. `uv run pytest -q tests/test_terminal.py tests/test_drain_reentry.py tests/test_caps.py tests/test_harvest.py tests/test_harvest_orphans.py tests/test_providers.py` passes. Every assertion is unchanged apart from the script, surface-filter, and adjacency adaptations named in Scope in.
8. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "from pathlib import Path; from chupa.specs import load_spec; s = load_spec(Path('specs/diagnose.md').read_text()); assert s.meta.llm_surface == 'diagnose' and s.inputs == ('ticket', 'terminal', 'harvest', 'run_record', 'retry_findings')"
uv run python -c "from chupa.artifacts import DIAGNOSIS_VERDICTS as v; assert v == ('retry', 'escalate', 'split', 'reject', 'abandon-human')"
uv run pytest -q tests/test_diagnose.py
uv run pytest -q tests/test_terminal.py tests/test_drain_reentry.py tests/test_caps.py tests/test_harvest.py tests/test_harvest_orphans.py tests/test_providers.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A verdict outside the vocabulary, or a failed diagnosis call, resolves to `retry`.
- A short-circuit calls the model or draws a `diagnosis` unit.
- The model picks a tier, effort, or model, or the verdict changes routing in this diff.
- A second diagnosis render, cap fold, or `cap_consumed` writer exists outside `chupa/stages.py` and `chupa/caps.py`.
- A diagnosed attempt's raw harvest payload still renders.
- `ticket.md` is written.
- An existing assertion is weakened beyond the named adaptations.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
