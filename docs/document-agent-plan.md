# Document agent: plan

A document agent for chupa that creates, reviews, and transforms documents. Each request picks one value from six dimensions: **Type**, **Audience**, **Format**, **Review**, **Tone**, and **Theme**. Each dimension is a list of files that can be extended. One canonical Markdown document (usually a Plan) is the source, and versions for other audiences and formats are derived from it. When a derived version is edited, the edit is folded back into the canonical document and then passed on to the other derived versions, so the set does not drift apart. Reviews run as isolated agent panels with a synthesis that checks the findings against the document, following the owner's existing review prompts.

## Status

Draft plan. Nothing in it is in effect and no ticket is authored. Written 2026-11-13 at commit `0895b5d4`. Revised the same day to take in the owner's review prompts in `/home/djp/source/` (`CutReview.md`, `KillReview.md`, `BuildItReview.md`, `CompressionReview.md`, and `gizmo/review/OutcomeReview.md`).

## What it is for

1. **From conversation or loose notes to a plan.** Turn a chat or "vibe" session, or several scattered Markdown files, into one canonical Plan with a fixed shape.
2. **One source, many readers.** Derive an overview for non-technical readers, an API reference for developers, a seed for ticket authoring, or a blog post, all from the same Plan, and render them as Markdown, HTML, or PDF.
3. **Reviews you can act on.** Run a lens as several isolated reviewers, then verify and merge their findings. A finding that several reviewers reach independently is treated as real. A finding from one reviewer is a lead to check.
4. **No drift.** Every derived document records which canonical sections it was built from. When the canonical document changes, chupa says which derived documents are stale. When a derived document is edited, the edit is proposed back into the canonical document instead of being lost or contradicting it.
5. **Plans organize other work.** A Plan's ticket breakdown is the bridge to chupa tickets (through a Seed), and its sections are the anchors that derived works cite.

## Current state

- `chupa/specs/ask/` holds operator prompt templates rendered by `chupa prompt <kind>` (`chupa/ask.py`, closed `KINDS` tuple). The extension opens one in a Claude Code chat ("Ask Claude: drain loop"). That is the existing route for interactive, guided work.
- Driver specs in `chupa/specs/` run headless through one driver (`chupa/driver.py`), with routing by `(tier, surface)` and a fallback to the `review` row for an unrouted surface (`chupa/providers.py:104`). Every surface except Implement is read-only. The model returns text, and the engine writes the files.
- Read-only surfaces are **not isolated**. Claude runs with `--tools Read Grep Glob LS` in the repo (`ClaudeAdapter.argv`). Codex runs `--sandbox read-only` in the repo. A reviewer can browse the repository, which the owner's review prompts forbid ("Your only input is the document").
- Specs always load from the engine. Host material enters a prompt only inside `<<chupa-data:...>>` blocks (`ask_notes` is the precedent). Config load refuses `review.surfaces` (host review prompts).
- The owner's review prompts (`/home/djp/source/*.md`, identical copies in `gizmo/review/`) have been run by hand against seed plans across several sibling repos. Reports sit in `gizmo/review/` (for example, `REVIEW_reports/cut-agent-{A,B,C}.md` with `REVIEW_CutSynthesis.md`).
- No document tooling exists in chupa: no Markdown-to-HTML renderer, no PDF path, no theme CSS.

## Target design

### 1. Dimensions and facets

Each dimension value is a **facet**: one Markdown file with frontmatter, kept under `chupa/specs/doc/facets/<dimension>/<value>.md`. The set of files is the closed list (an allowlist). Adding a value means adding a file and its test pin.

| Dimension | Initial values | Kind | Applies at |
|---|---|---|---|
| Type | `plan`, `seed`, `overview`, `architecture`, `api`, `spec`, `whitepaper`, `blog` | prompt facet: required sections and their order, what each section is for | create, derive |
| Audience | `technical`, `non-technical`, `ai`, `user`, `developer`, `student` | prompt facet: assumed knowledge, vocabulary, what to explain, what to leave out | create, derive |
| Tone | `default`, `examples` | prompt facet. `examples` takes example files as data: "match the voice, sentence length, and structure; never copy content" | create, derive |
| Review | `scope`, `viability`, `buildability`, `automatable`, `compression` | lens facet (section 4): roles, run shape, prompts, output schema, verdict set | review |
| Format | `markdown`, `html`, `pdf` | render facet, mechanical, no model | render |
| Theme | `light`, `dark` | render facet: a CSS token file, used by `html` and `pdf` only | render |

Facet frontmatter:

```yaml
---
facet: audience/non-technical
version: "1.0"
summary: Readers who use the result but do not build it.
aliases: []                        # e.g. review/scope has [cut]
applies_to: [create, derive]       # or [review], or [render]
requires: []                       # e.g. theme facets: requires format in [html, pdf]
---
```

- **Model facets** (Type, Audience, Tone, Review) change the prompt. **Render facets** (Format, Theme) change only the mechanical output. The model always writes Markdown.
- A facet that does not apply to an operation is refused with a paved road.
- **Host extension:** `docs.facets_dir` points at host facet files with the same frontmatter. They enter the prompt as `<<chupa-data:facet>>` blocks inside the engine's surface frame. Whether host *lenses* are allowed is Open decision 2.

### 2. Doc sets: one canonical document and its derived versions

A **doc set** is a directory with a manifest:

```
docs/plans/parallel-tickets/
  docset.yaml
  plan.md                         # canonical
  overview.non-technical.md       # derived
  overview.non-technical.html     # rendered
  spec.md                         # derived by the compression lens, promoted on LOSSLESS
  reviews/2026-11-13-scope.md     # review report
```

`docset.yaml` (schema `chupa.docset/1.0`, strict writer and tolerant reader, as in `docs/evidence-trail-plan.md` §5):

```yaml
schema: chupa.docset/1.0
canonical:
  path: plan.md
  facets: {type: plan, audience: developer, tone: default}
  sections: {status: 3f9a..., current-state: 81c2..., target-design: 0d7e...}   # heading slug -> content hash
derived:
  - path: overview.non-technical.md
    facets: {type: overview, audience: non-technical, tone: default}
    renders: [{format: html, theme: light, path: overview.non-technical.html}]
    built_from: {commit: 0895b5d4, sections: {target-design: 0d7e..., risks: 77aa...}}
    hash: 5be1...            # this file's hash when chupa last wrote it
    fidelity: {verdict: LOSSY-MINOR, report: reviews/2026-11-13-fidelity-overview.md}
```

- **Section identity** comes from heading slugs. The owner's compression prompt already requires that "section numbers and heading text stay exactly as in the original", so headings are a stable key across derived versions.
- **`chupa doc status`** is mechanical and reports one state per derived document: `current`, `stale` (a canonical section it used changed), `diverged` (edited after chupa wrote it), or `stale+diverged`.
- `derive` refuses to overwrite a `diverged` file. The paved road is `chupa doc fold <path>`, or `--discard-edits` to throw the edits away on purpose.

### 3. Surfaces and isolation

| Surface | Spec | Purpose |
|---|---|---|
| `doc_draft` | `chupa/specs/doc/draft.md` | sources + Type, Audience, and Tone facets → canonical Markdown + open questions |
| `doc_derive` | `chupa/specs/doc/derive.md` | canonical + target facets → derived Markdown + the sections it used |
| `doc_review` | `chupa/specs/doc/review.md` | one generic frame. The lens facet supplies the role prompt (cut agent, synthesis, compressor, fidelity, ...) and the reply schema. |
| `doc_fold` | `chupa/specs/doc/fold.md` | canonical + diverged derived document + its diff → proposed canonical patch, with changes in meaning separated from changes in style |

**Isolation is a property of the call, not of the prompt.** Every lens prompt says the agent's only input is the document, with "no knowledge that other agents exist". Today's read-only surfaces can read the whole repository, so the doc surfaces get a new isolated mode:

- The call runs with its working directory set to a fresh scratch directory under `state_dir/doc-scratch/<call>/`. That directory holds only the files the role is allowed to see: the document for a panelist; the document and the panel reports for a synthesis; the original and the draft for a fidelity auditor.
- Claude gets `--tools Read Grep Glob LS` scoped to that directory, and Codex gets `--sandbox read-only` with that directory as its working directory. The adapter's existing `writes` flag stays false. A new `isolated` request field selects the scratch directory as the working directory.
- The prompt names no other agent, no prior run, and no review history. No earlier report from the doc set's `reviews/` directory is ever placed in a panelist's scratch directory. That prevents anchoring, as the owner's prompts require.
- The scratch directory is removed after the call, and the evidence record (`docs/evidence-trail-plan.md`) keeps what the call saw.

Reply gates (fail closed, with re-prompting as the driver does now):

- `doc_draft` / `doc_derive`: every required section of the Type facet is present and in order. Every cited canonical section exists.
- `doc_review`: the reply matches the role's declared schema. Every finding cites a heading or line that exists in the document ("no finding without a location"). The verdict, when the role has one, is in the lens's closed verdict set.
- Synthesis roles: **accounting gate.** Every panel finding id appears exactly once: in a cluster, the findability list, the low-confidence tail, or `dropped` with a reason (for example, single-reviewer opinion). A synthesis that loses a finding without saying so is refused.
- `doc_fold`: the patch applies cleanly to the canonical document at its current hash.

### 4. Review lenses

#### 4.1 Lens catalog (from the owner's prompts)

| Lens id | Source prompt | Alias | Question | Run shape | Verdicts |
|---|---|---|---|---|---|
| `scope` | `CutReview.md` | `cut` | What does the document specify that no stated goal justifies, and what effort is in the wrong order? | 3 isolated cut agents → 1 synthesis | LEAN / TRIMMABLE / GOLD-PLATED, plus NO-METRIC |
| `viability` | `KillReview.md` | `kill` | Should this be built as written? | 3 isolated kill agents → 1 synthesis | VIABLE / VIABLE-WITH-CHANGES / NOT VIABLE AS WRITTEN |
| `buildability` | `BuildItReview.md` | `build-it` | What does an implementer have to invent, because the document does not decide it? | 3 isolated dry-run implementers for `<PHASE_SCOPE>` → 1 synthesis | SELF-CONTAINED / GAPS-FIXABLE / NOT SELF-CONTAINED |
| `compression` | `CompressionReview.md` | | Rewrite in specification form with nothing lost | 1 compressor (writes a draft) → 1 isolated fidelity auditor | LOSSLESS / LOSSY-MINOR / LOSSY |
| `automatable` | new, section 4.3 | | Could an AI pipeline carry the document to merged code with no human decisions? | 3 isolated dry-run *ticket authors* → mechanical lint → 1 synthesis | AUTOMATABLE / AUTOMATABLE-WITH-GATES / NOT AUTOMATABLE AS WRITTEN |

What every lens shares, taken from the prompts:

- **Panelists use identical prompts and are fully isolated.** "Identical prompts keep the convergence statistic clean."
- **The synthesis re-reads the document and checks each cluster.** When the document does answer an issue that reviewers missed, the cluster moves to a **FINDABILITY** list: the answer exists, but sits where a reader would not look. That is a structure defect, not a content gap.
- **Ranking:** blocking findings first (NOT VIABLE grounds, BLOCKED, NO-METRIC), then 3/3, then 2/3. Single-reviewer findings labelled opinion are dropped. Other single-reviewer findings go to a low-confidence tail.
- **Disagreement is reported, not averaged.** Divergent value judgments go to the owner.
- **High reasoning effort** for every role (`agent_effort: high`).
- **The review recommends, and the owner decides.** No lens commits code or edits the canonical document. Its findings become proposed edits through the same accept flow as fold-back (section 5).
- **A short report is a valid result.** "On a lean document, few findings is a valid outcome, not a failed run."

#### 4.2 Lens facet format

A lens facet carries the source prompt text verbatim, split into roles, with the placeholders made explicit:

```yaml
---
facet: review/buildability
version: "1.0"
aliases: [build-it]
source: BuildItReview.md
params: {PLAN_PATH: document, PHASE_SCOPE: required}   # refused with a paved road when missing
stages:
  - {role: dry_run, count: 3, isolated: true, sees: [document]}
  - {role: synthesis, count: 1, isolated: true, sees: [document, stage.0]}
verdicts: [SELF-CONTAINED, GAPS-FIXABLE, NOT SELF-CONTAINED]
---
## Role: dry_run
<the "Dry-run agent prompt (verbatim)" section>
## Role: synthesis
<the "Synthesis agent prompt (verbatim)" section>
## Schema: dry_run
<ledger entry fields and closed classes: missing / ambiguous / contradictory / deliberate-freedom; BLOCKED list>
```

- The prompt text stays the owner's. chupa adds only the output schema, so "output returns as structured data" becomes a gated JSON reply.
- `<PLAN_PATH>` becomes the document's file name inside the scratch directory. `<SPEC_PATH>` (compression) becomes the draft the engine writes from the compressor's reply, since agents never write files.
- `count` is configurable per run (`--panel N`, minimum 2). The default stays 3, as the prompts specify.
- `compression` declares a different shape: `compressor` (count 1, returns the spec text + ledgers + metrics) then `fidelity` (count 1, sees the original, the draft, and the compressor's ledger and duplicate map, but not its reasoning). The fidelity auditor's mechanical checks ("check these mechanically with diff") run in the engine: protected regions (fenced code, commands, extraction-marker blocks) are compared byte for byte, and those results are given to the auditor as facts.
- `OutcomeReview.md` and `SeedPlanDiagnosis.md` are **evidence lenses**: they read run history (repos, git logs, tickets), not one document. They are out of v1. Section 4.4 says how they connect later.

#### 4.3 The AI Automatable lens, and how it compares with BuildIt

**What it tests.** BuildIt asks whether the document *determines* every decision an implementer needs. Automatable asks a different question: once decided, can the work be *carried out and verified by machine*, as a set of chupa tickets that go through Implement, Check, Review, and Merge with no human beyond `confirm`? A document can be fully self-contained and still not be automatable: "the dashboard feels responsive" is fully decided and has no oracle. It can also be automatable while leaving free choices an AI is allowed to make.

**How it is fully automated.** Its implementer role-plays chupa's *Author*, not a human engineer. It produces artifacts chupa can already check without a model:

1. **3 isolated dry-run authors.** Each sees the document plus the authoring contract the real executor obeys: `chupa/docs/host-authoring.md` and the ticket skeletons. That contract is to Automatable what "the document's implementation language" is to BuildIt. It is the target machine's rules, not project context. No repository, no history, no knowledge of the other agents. For `<PHASE_SCOPE>`, each returns:
   - a **ticket set** in chupa format (frontmatter, Goal, Scope, Scope fence, Acceptance criteria, Verification, Depends on);
   - an **oracle ledger**: for every acceptance criterion, how a machine decides it (`test`, `command`, `path-exists`, `lint`, `none`). `none` means a person has to decide;
   - a **human-gate ledger**: every step the agent could not hand to an agent, in closed classes: `credential` (accounts, keys, payment), `external` (third-party approval, hardware, a service that does not exist yet), `judgment` (taste, UX feel, legal, business priority), `data` (inputs the document assumes but nothing produces), `irreversible` (a production action with no rollback);
   - an **invented-decisions ledger**, with BuildIt's classes, so the two lenses can be compared directly.
2. **Mechanical stage, with no model.** The engine writes each ticket set into a scratch `tickets/` directory and runs the real ticket checks that `chupa lint` runs (`validate_ticket`, then `lint_findings`, both in `chupa/tickets.py`) on every ticket. The checks cover the grammar, required sections, the fence covering every carried path, `Depends on` naming tickets in the set, and acyclic ordering. When the document belongs to an existing host repo, `## Context` entries are also resolved against that repo. Results per ticket, plus counts (tickets, criteria by oracle class, estimated fence overlap from `docs/parallel-tickets-plan.md` §2), go to the synthesis as facts. `--deep` also runs `requisition_review` on each ticket. It is expensive and opt-in.
3. **1 synthesis.** It re-reads the document, then ranks:
   - human gates found by 3/3 and then 2/3 agents (verified against the text; a gate the document does settle goes to FINDABILITY);
   - criteria with oracle `none` that several agents reached for the same deliverable;
   - **decomposition divergence**: when three authors split the same deliverable in three different ways, the document does not determine the work's structure. That is a finding even when every ticket passes lint;
   - recurring lint failures on the same deliverable across agents, which point at a document gap and not at one agent's slip;
   - ordering disagreements (different `Depends on` graphs for the same deliverables).

   It also reports an **automation ratio**: the share of the document's deliverables covered, in at least 2 of the 3 sets, by lint-clean tickets whose criteria all have an oracle other than `none`.

   Verdict:
   - AUTOMATABLE: no verified human gate, ratio 1.0;
   - AUTOMATABLE-WITH-GATES: every verified gate is named and can be placed as a human ticket or a `confirm` point ahead of the tickets that need it;
   - NOT AUTOMATABLE AS WRITTEN: a core deliverable has no oracle in any set, or a verified gate sits in the middle of the work where no ordering can isolate it.

**Disposition.** As in BuildIt, the ticket sets are measurement instruments and are discarded by default. The owner may promote the synthesis's consensus set into a Seed (section 7), but it still goes through the real authoring flow. Findings become document edits: add the oracle, name the gate and its owner, fix the decomposition.

**Comparison:**

| | BuildIt (`buildability`) | AI Automatable (`automatable`) |
|---|---|---|
| Question | Does the text determine every decision? | Can a machine carry out and verify the work? |
| Role-played implementer | A human engineer writing skeletons | chupa's Author writing tickets |
| Input beyond the document | none | the authoring contract (guide + skeletons) |
| Product | module skeleton, interface stubs, invented-decisions ledger, BLOCKED list | ticket set, oracle ledger, human-gate ledger, invented-decisions ledger |
| Mechanical check | none: everything is model judgment | real ticket lint on every ticket, plus counts |
| Convergence signal | the same decision invented by k/3 agents | the same gate, missing oracle, lint failure, or split found by k/3 agents |
| Catches that the other misses | interface and data-shape gaps, contradictions between passages | unverifiable criteria, human-only steps, work that cannot be split into tickets under the diff budget, unclear ordering |
| Misses | whether the result can be checked or run unattended | design gaps the authors filled from the authoring guide's defaults |
| Cost | 4 calls | 4 calls + one lint per ticket (+ requisition reviews with `--deep`) |
| Can be checked against reality later | by OutcomeReview, by hand | by `docs/training-data-plan.md` data: predicted gates and ticket counts against the journal's actual parks, confirms, and attempts |

Run BuildIt first. Automatable assumes the decisions are settled, so its findings on an unsettled document mostly repeat BuildIt's gaps. A full draft of the lens prompt in the owner's house style is in the Appendix.

#### 4.4 Later: evidence lenses

OutcomeReview's **evidence overlay** stamps each document-review cluster CONFIRMED, UNCONTRADICTED, WEAKENED, or CONTRADICTED against what real runs did. "Convergence ranks attention; evidence decides." For a host that runs its plan through chupa, the run evidence is already in its own journal and tickets: attempts, parks, confirms, conflict facts, plus the evidence trail once it ships. A later `outcome` lens can read those instead of sibling repos. Its trigger is the first plan that has both a review report and a finished chupa run.

### 5. Fold-back, review dispositions, and fidelity

1. `chupa doc status` reports a derived document as `diverged`, or a review report proposes edits.
2. `chupa doc fold <path>` (or `chupa doc apply <report>`) writes a proposed patch to the canonical document, plus a note on what was not applied and why.
3. The owner accepts the patch, edits it, or rejects it. Accepting applies it and updates the section hashes. Refuse-class cuts from the `scope` lens go to the document's refusals list, as `CutReview.md`'s disposition requires, so the cut scope does not come back.
4. Derived documents built from changed sections become `stale`. `chupa doc derive --stale` rebuilds them.

**Fidelity as a gate on derivation.** The compression lens's fidelity role is reused to check derived documents:

- For a derive that changes only form (`spec`, or the same audience), the full class list applies (DROPPED, ALTERED, INVENTED, RESOLVED AMBIGUITY, VERBATIM VIOLATION, BROKEN REFERENCE), and a `spec` is promoted only on LOSSLESS plus a human-reviewed diff, as in `CompressionReview.md`.
- For a derive that changes audience (a non-technical overview drops detail on purpose), only INVENTED, ALTERED, and RESOLVED AMBIGUITY count. A derived document may leave things out, but never add or change facts.
- The verdict is recorded in `docset.yaml` (`fidelity`).

### 6. Guided drafting: from chat to a plan

- **Interactive.** `chupa prompt doc-plan [files...]` (template `chupa/specs/ask/doc-plan.md`) opens a Claude Code chat that walks the operator through the Plan Type's sections, one question at a time for what the sources leave open. It ends by writing the doc set through `chupa doc draft`. The extension gets an "Ask Claude: draft a plan" menu item.
- **Headless.** `chupa doc draft --type plan --audience developer --from a.md b.md notes/*.md --out docs/plans/<name>/`. Anything the sources leave open goes into `## Open decisions`, never into an invented answer.
- The `plan` Type facet requires what the lenses need in order to work at full strength: stated goals and an **optimization metric** (otherwise `scope` leads with NO-METRIC), a refusals list, implementation phases (BuildIt's `<PHASE_SCOPE>` names one), and a ticket breakdown.

### 7. Plans and Seeds lead to tickets

- The `seed` Type, derived for Audience `ai`, turns each ticket row into what an authoring session needs: fence files, acceptance criteria, and where each rule lives. An `automatable` consensus set can be its starting point.
- Tickets are still authored the one way chupa allows: `chupa new` + `chupa/docs/host-authoring.md` + `chupa lint` + `chupa review`. The document agent never writes `ticket.md` into `tickets/`.

### 8. Render

- Markdown to HTML in pure Python with a new dependency (`markdown-it-py`, with tables, footnotes, and heading anchors). The theme's CSS is embedded inline, so the output is a single file.
- Themes are `chupa/specs/doc/themes/light.css` and `dark.css` (CSS custom-property tokens). Host themes come from `docs.facets_dir/theme/`.
- PDF goes HTML to PDF through a host-declared argv (`docs.render.pdf`), run through the exec seam. When none is configured, `--format pdf` is refused with a paved road naming the key.
- Mermaid stays as code blocks in v1.

### 9. Config

```yaml
docs:
  facets_dir: null          # host facet extensions; injected as data
  review:
    panel: 3                # default panelists per lens (min 2)
    diverse: false          # rotate panelists across the route's candidates
  render:
    pdf: null               # argv list
```

A new `Docs` model in `chupa/config.py` with a default, so existing configs load unchanged.

## Where each piece lives

| Piece | Home |
|---|---|
| Facet and lens files (engine-owned; lens prompt text from the owner's review files) | `chupa/specs/doc/facets/<dimension>/<value>.md` |
| Surface specs | `chupa/specs/doc/{draft,derive,review,fold}.md` |
| Interactive prompt | `chupa/specs/ask/doc-plan.md`, added to `KINDS` in `chupa/ask.py` |
| Isolated scratch working directory for a call | `chupa/providers.py` (`isolated` request field), `chupa/llm.py` (`LLMRequest`) |
| Facet registry, docset schema, section hashing, status | new `chupa/docs_agent/` package (`facets.py`, `docset.py`) |
| Lens runner (stages, panel, accounting gate, engine-side mechanical checks), fold, apply | `chupa/docs_agent/review.py`, `fold.py` |
| Dry-run ticket lint for `automatable` | `chupa/docs_agent/review.py` calling `validate_ticket` and `lint_findings` in `chupa/tickets.py` (no copy of the rules) |
| Render and themes | `chupa/docs_agent/render.py`, `chupa/specs/doc/themes/` |
| Verbs `doc draft / derive / review / fold / apply / render / status / facets` | `chupa/__main__.py`, plus `./dev.py` subcommands |
| Extension menu items | `vscode-chupa/` (draws snapshot fields and runs the verbs) |
| Operator docs | `docs/how-chupa-works.md`, new section "Documents" |

## Ticket breakdown

Each ticket puts its tests in new files (`docs/parallel-tickets-plan.md` §7).

| # | Stem | Kind | P | Depends on | Content |
|---|---|---|---|---|---|
| 1 | `doc-facet-registry` | feature | P2 | | Facet format (with `aliases`, `params`, `stages`, `verdicts`), loader, validation, `chupa doc facets`. Type, Audience, Tone, Format, and Theme facet files. |
| 2 | `docset-manifest` | feature | P2 | | `chupa.docset/1.0`, section hashing, `chupa doc status`. |
| 3 | `isolated-readonly-call` | feature | P2 | | `isolated` request mode: scratch working directory with only the declared files, for Claude and Codex. Tests prove a panelist cannot read a repo file. |
| 4 | `doc-review-runner` | feature | P2 | 1, 3 | Generic `doc_review` surface, stage runner, schema and verdict gates, accounting gate, report. |
| 5 | `doc-lenses-from-owner-prompts` | feature | P2 | 4 | `scope`, `viability`, `buildability`, and `compression` lens facets from the owner's prompt files, with schemas. Engine-side byte-identity checks of protected regions for `compression`. |
| 6 | `doc-lens-automatable` | feature | P2 | 4 | The Appendix prompt as a lens facet, the mechanical ticket-lint stage, the automation ratio, and `--deep`. |
| 7 | `doc-derive-fidelity` | feature | P2 | 2, 5 | `doc_derive`, fidelity gate by derive class, `fidelity` recorded in `docset.yaml`. |
| 8 | `doc-fold-apply` | feature | P2 | 2, 7 | `doc_fold`, `doc apply <report>`, accept flow, refusals-list placement, `derive --stale`. |
| 9 | `doc-render` | feature | P2 | 1 | Markdown to HTML with themes, PDF through the configured argv, `Docs` config. |
| 10 | `doc-draft` | feature | P2 | 1, 2 | `doc_draft` (headless) and the `doc-plan` ask prompt (interactive). |
| 11 | `doc-extension-menu` | feature | P3 | 8, 10 | Snapshot fields for doc sets and their states, and menu items. |

Tickets 1, 2, and 3 touch separate files and suit a first parallel trial.

## Risks

- **Fold-back or review edits that change meaning without notice.** The owner approves every canonical patch. Nothing applies automatically.
- **Cost.** One lens is 4 calls (3 + synthesis). All five lenses are 18 calls plus lint. Lenses are chosen for each run, with no "all" default.
- **Model diversity and the convergence statistic.** Identical prompts on one model measure agreement across samples. Panelists on different models measure agreement across models, which is a stronger signal (SeedPlanDiagnosis: "a defect both providers hit is almost certainly a real seed defect"). The two counts are not comparable, so every report records the model that served each panelist, and `diverse` is off by default.
- **The Automatable lens judges against the authoring guide as it stands.** When the guide changes, old automatable reports become stale. Each report records the guide's hash.
- **Host lenses are host instructions.** They cut against the current refusal of `review.surfaces` (Open decision 2).

## Open decisions

1. **`diverse` panels by default?** Recommend off by default, so that convergence counts compare with the owner's earlier manual runs, and on for a deliberate cross-provider review.
2. **Host-defined lenses and facets.** Recommend allowing them as data blocks inside the engine frame. The owner's lenses ship as engine facets either way.
3. **Verbs only, or a `doc` ticket kind too?** Recommend verbs only for v1.
4. **Where doc sets live.** Recommend `docs/<anything>/` with a `docset.yaml`, found by search.
5. **Promote an `automatable` consensus ticket set into a Seed?** Recommend allowing it only as an explicit owner step, never automatically. Otherwise the instrument starts shaping the result it measures.
6. **Move today's plans into doc sets** once tickets 1 and 2 merge? Recommend yes, and run `scope` and `buildability` on them as the first real use.

## Appendix: draft `AutomatableReview` prompt

Written to match the owner's review files and intended as the body of the `review/automatable` lens facet.

```
# What this tests and why
A design document can be self-contained -- every decision determined, BuildItReview clean -- and still not be buildable by an AI pipeline, because determining a decision is not the same as being able to carry it out and verify it unattended. This exercise tests the document under automated execution. Fresh agents with no project context role-play the ticket author of an AI build pipeline for <PHASE_SCOPE> and must express the work as tickets in the pipeline's format, from the document at <PLAN_PATH> and the authoring contract at <GUIDE_PATH> alone. Every step they cannot hand to an agent, every criterion no machine can decide, and every place their decompositions diverge is a measured automation gap. Convergence is the signal: a gate or missing oracle independently found by two or more isolated agents is real, not one agent's caution. Run BuildItReview first; this review assumes the decisions are settled and measures whether they can be executed. Designed to re-run as the document evolves; an empty gate ledger is a valid outcome, not a failed run.

# Run shape
* 3 DRY-RUN AUTHOR agents, identical prompt (below), fully isolated: each gets the document at <PLAN_PATH> and the authoring contract at <GUIDE_PATH> and nothing else -- no repo browsing, no conversation history, no prior review results, no knowledge that other agents exist.
* A MECHANICAL stage, no model: every ticket from every agent is run through the pipeline's real ticket lint; per-ticket results and counts are passed to synthesis as facts.
* 1 SYNTHESIS agent (prompt below) compares the three ticket sets, their ledgers, and the lint facts after all finish.
* High reasoning effort for all four. No file writes by any agent; output returns as structured data.

# Dry-run author agent prompt (verbatim)
You are the ticket author for an AI build pipeline that will implement the system specified by the design document at <PLAN_PATH>. The pipeline's rules for tickets are the authoring contract at <GUIDE_PATH>. Those two files are your ONLY input. Read both in full. You cannot ask questions; there is no other documentation, no repository, and no team. Every ticket you write will be implemented by an AI agent, checked only by the commands and criteria the ticket names, reviewed by another AI agent, and merged with no human in the loop except where you explicitly place one.

Produce four things for <PHASE_SCOPE> as defined in the document's implementation-phases section:

1. TICKET SET: the tickets you would author, in the contract's format, each complete: Goal, Scope in / Scope out, Scope fence, Acceptance criteria, Verification commands, Depends on. Cover every deliverable the document names for <PHASE_SCOPE>. Size each ticket so its diff stays within the contract's budget; if a deliverable cannot be split to fit, say so in the gate ledger.

1. ORACLE LEDGER: for every acceptance criterion, one entry:
  * criterion: quoted from your ticket.
  * oracle: one of test (a test the ticket adds or names decides it), command (a named command's exit status or output decides it), path-exists (a file or section someone can read decides it), lint (a static check decides it), none (only a person can decide it).
  * how: one sentence on what the machine runs or reads.

1. HUMAN-GATE LEDGER: every step you could not hand to an agent, one entry each:
  * step: what has to happen, in one sentence.
  * section: the document section that requires it.
  * class: one of credential (accounts, keys, payment), external (third-party approval, hardware, a service that does not exist yet), judgment (taste, feel, legal, business priority), data (inputs the document assumes but nothing produces), irreversible (an action with no rollback).
  * placement: where in the ticket order a human must act, and which tickets wait on it.

1. INVENTED-DECISIONS LEDGER: as in BuildItReview -- every choice the document did not determine for you, with decision, section, chose, and class (missing / ambiguous / contradictory / deliberate-freedom).

Rules: author AS SPECIFIED -- do not evaluate, improve, or redesign the system. Follow the authoring contract exactly; a ticket that breaks it is a failed ticket, not a stylistic choice. Never write a judgment word into a criterion to avoid an oracle of none -- an honest none is the measurement; a disguised one corrupts it. Filling a gap from your own experience is still an invented decision -- ledger it. Do not pad the gate ledger: a step an agent can do with what the document provides is not a gate, and an empty gate ledger is a valid answer. Be exhaustive on the ledgers before polishing ticket prose; if effort runs short, cut ticket prose, never ledger entries.

# Synthesis agent prompt (verbatim)
You receive three ticket sets with oracle, human-gate, and invented-decisions ledgers, produced independently by three isolated authors from the same design document at <PLAN_PATH> and authoring contract at <GUIDE_PATH>, plus mechanical lint results for every ticket. Read the document, then:

1. Map every ticket in every set to the document deliverable it serves. A deliverable no set covers is a finding; a deliverable all three cover with structurally different splits is DECOMPOSITION DIVERGENCE -- the document does not determine the shape of the work.
1. Cluster ledger entries describing the same underlying gate, oracle gap, or decision across sets (they will word it differently).
1. Rank: (a) any core deliverable whose criteria have oracle none in every set; (b) then human gates found by 3/3, then 2/3; (c) then oracle-none criteria by convergence; (d) then decomposition divergence; (e) then lint failures recurring on the same deliverable across sets -- recurrence points at the document, a single failure at the author. Single-agent deliberate-freedom entries drop; other single-agent entries go in a low-confidence tail.
1. Verify each cluster against the document before reporting it: if the document does supply the oracle, the data, or the decision and the authors missed it, report it separately as FINDABILITY.
1. For each surviving cluster: the deliverable, the owning section, what each author did (divergence matters), and a one-sentence document edit -- add the oracle, name the gate and its owner and placement, or fix the decomposition.
1. Compute the AUTOMATION RATIO: the share of <PHASE_SCOPE> deliverables covered, in at least two of the three sets, by lint-clean tickets whose criteria all have an oracle other than none.

Output, verdict first:
* Automation: AUTOMATABLE (no verified human gate and ratio 1.0) / AUTOMATABLE-WITH-GATES (every verified gate is named and can be placed ahead of the tickets that need it) / NOT AUTOMATABLE AS WRITTEN (a core deliverable has no oracle in any set, or a verified gate sits where no ordering can isolate it) -- with the ratio and one paragraph of justification.
* The ranked cluster list with per-cluster convergence counts, the findability list, and the low-confidence tail.

# Disposition of results
Gaps, gates, and findability problems become document edits, reviewed before applying, same as every round; the exercise re-runs after material edits, rescoped to the phases now earliest-unbuilt. Ticket sets are measurement instruments and are discarded, unless the owner explicitly promotes the consensus set as a starting point for real authoring -- which still goes through the pipeline's own authoring and review. Once the phase has actually run, its real parks, confirms, and attempt counts are the check on this review's predictions. Nothing from this exercise commits code.
```
