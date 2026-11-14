# Training data capture: plan

Turn what chupa's model runs produce into training records. The evidence store (`docs/evidence-trail-plan.md`) already keeps every model call; this plan adds the attempt-level record (the full diff before a worktree is deleted), an export verb that turns the journal, git history, and the store into labelled training records, and an eval verb that scores a local model against held-out records. A host that runs chupa on its own project accumulates examples of its own work: tickets, attempts, rejections, review findings, fixes, and the code that finally merged. With those it can train or tune a local model that takes over part of its future work.

The aim is a flywheel, not a replacement model. A few hundred tickets will not train a general coding model. They are enough for retrieval over past work, and for tuning a small model on narrow, high-volume tasks (triage, ticket review, first-pass code review), where the host's own conventions matter more than general skill.

## Status

Draft plan. Nothing in it is in effect and no ticket is authored. Written 2026-11-13 at commit `0895b5d4`; revised 2026-11-13 at commit `80b76d5d` for `docs/roadmap.md`.

## Roadmap

Release 0.5.0 (`docs/roadmap.md` rows 52-56). Needs from other plans: the evidence store and envelope (`evidence-store`, `evidence-envelope`, 0.2.0), which own the call record this plan builds on; `merge-model-resolve` (0.4.0) for the `conflict` record kind, which export skips with a count until it exists. Nothing depends on this plan except the document agent's later `outcome` lens (`docs/document-agent-plan.md` §4.4). Shared budgets: none (no CORE_TEMPLATE text; one new config block `training_data`). The P0 capture bug (`provider-capture-overwrite`) is the roadmap's row 1, not this plan's; its cause fix is `evidence-envelope` (roadmap decision 4).

## Why chupa data is unusually good training data

Most agent logs have no reliable label. chupa's lifecycle labels every attempt as a side effect of running it:

- **Input:** the ticket (Goal, Scope, Acceptance criteria, Context), checked by lint and by the requisition review before any work starts.
- **Trajectory:** the rendered prompt, the agent's tool-call stream, and the diff.
- **Outcome:** Check results, the Review verdict with findings, the diagnosis, and finally either a squash commit on `main` (with `chupa-ticket` and `chupa-reviewed-sha` trailers) or a rejection.
- **Pairs:** one ticket often has a rejected attempt and then an accepted one. That gives a (prompt, worse, better) preference pair with a stated reason (the review finding) for why one was worse.
- **Delayed label:** a merged change later blamed for a red merge or a bug ticket (retro attribution) turns a positive example into a negative one.

## Current state

What exists today, under `state_dir` (this repo: `.chupa/state`) and in git:

| Source | Holds | Kept? |
|---|---|---|
| Journal (`journal/*.jsonl`, 15 MB here) | State transitions, cap draws, signals, and each model call's result text under effect keys `llm/<stem>/<run_seq>/<surface>/<attempt>/<call>` (ticketless surfaces key under their surface name, `chupa/driver.py:274`) | Yes, the source of truth |
| `tickets/<stem>/` on `main` | `ticket.md`, `run.md`, `checks.json`, `review.md`, `attempts/<n>/harvest.json`, `diagnosis.json` | Yes, in git |
| Squash commits on `main` | The merged code, with `chupa-ticket` and `chupa-reviewed-sha` trailers | Yes, in git |
| `spools/<stem>/<attempt>/` | Each call's `prompt.md` and `output.txt` (`chupa/driver.py:345,374`), and command output (`check/verify-NN.txt`) | No retention policy (1.2 GB here) |
| `spools/providers/<stem>/<provider>-<seq>/` | Raw CLI capture: `prompt.md`, `events.jsonl` (the full tool-call stream), `stderr.txt` | **Partly lost** (gap 2); replaced by the evidence store in 0.2.0 |
| `engine.log` | Stage start and end, and other diagnostics | Rotated at 4 x 16 MiB (`chupa/enginelog.py:14-15`), so it is lost over time |

Gaps that matter for training data:

1. **Rejected code is discarded.** Before each attempt, the old worktree and branch of that stem are removed (`docs/how-chupa-works.md` §4.1). `harvest.json` keeps only a diff stat and the last 4,000 characters of the logs. The code that review snagged, which is the negative half of every preference pair, is gone.
2. **Raw provider captures get overwritten.** The capture counter `_seq` starts at 0 in each process (`chupa/providers.py:294`), so a second run of a stem in a new process writes over `claude-0001` and the rest (`providers.py:325`). At `0895b5d4` this repo's journal held 3,944 model-call completions and 2,453 capture directories with an `events.jsonl`. The worst cases are `triage` (467 calls, 282 directories) and `author` (336 calls, 157 directories). Roadmap row 1 fixes the instance; `evidence-envelope` fixes the cause.
3. **Nothing links a journal record to its capture.** The journal key is `llm/<stem>/<run_seq>/<surface>/<attempt>/<call>`; the capture path is `providers/<stem>/<provider>-<seq>`. They match only by timestamp. The evidence store keys every record by the journal effect key (roadmap decision 3).
4. **Only configured secrets are redacted.** The redactor scrubs configured secret values. An agent that reads a `.env` file or a customer data file puts that content into `events.jsonl` unscrubbed. `harvest.json` is written without the redactor at all (`chupa/runner.py:443-483`; roadmap row 12 `redaction-harvest-seam`).

## Departures from the design record

| Record says | This plan | Why |
|---|---|---|
| §18.1 refuses "the AI audit trail layer (trajectories, reward vectors, preference pairs, training exports)" and says it returns "as projections over the journal" | Preference pairs and training exports, built as projections over the journal, git, and the evidence store | The owner chose on 2026-11-13 to build the flywheel. Export is a projection in the §18.1 sense: it is rebuilt from the sources and never becomes an authority. The one new durable thing, the attempt diff, is kept because it cannot be rebuilt once the worktree is gone |
| §18.1 and D9 refuse a blob store | This plan adds no store; it writes attempt manifests into the evidence store, whose departure is declared in `docs/evidence-trail-plan.md` | One declaration, in the plan that owns the store |

`CHUPA_PLAN.md` stays frozen. The tickets update `docs/how-chupa-works.md` §10.1 and the config table, and `chupa/docs/host-contract.md`.

## Target design

### 1. Config (experimental)

```yaml
training_data:          # experimental; off by default
  enabled: false
  exclude: []           # path globs whose content is never stored, e.g. [".env*", "data/customers/**"]
```

- A new `TrainingData` model in `chupa/config.py`, added to `Config` with default `TrainingData()`, so existing configs load unchanged.
- `exclude` adds to a fixed list of globs that are always excluded (`.env*`, `*.pem`, `*.key`, `id_*`). It cannot remove entries from that list (fail closed).
- Retention is not here. The evidence store's `evidence.max_gb` (`docs/evidence-trail-plan.md` §1) bounds the whole store, attempt manifests included, whether or not training is enabled.
- What the switch gates (roadmap decision 2): the attempt manifest with its full diff, `training export`, and `training eval`. Call envelopes and raw provider output are captured for every call regardless, because diagnosis and harvest read them. When `enabled` is false, `export` and `eval` refuse with the paved road "set training_data.enabled: true; only attempts after that carry a diff".

### 2. The attempt manifest

The evidence store holds one record per model call (`evidence/calls/`). This plan adds one record per attempt, written at the attempt's terminal, before `runner.drive` removes the worktree (`docs/how-chupa-works.md` §6.1 step 9):

```
<state_dir>/evidence/
  attempts/<stem>/<run_seq>/<attempt>.json     # schema chupa.evidence.attempt/1.0
```

- Fields: `stem`, `run_seq`, `attempt`, `base_sha`, `head_sha`, the blob id of the full attempt diff (`git diff <base>..<head>` through `git.py`, with excluded paths removed), blob ids for each Check command output, the call keys the attempt made, the terminal outcome and reason, the review verdict and findings, and the `engine_version` and spec versions carried by the calls.
- Blobs go into the store's content-addressed `blobs/` (`docs/evidence-trail-plan.md` §1), so a diff shared between retries is stored once. Everything passes the redactor before hashing, as every store write does.
- The manifest is written through the store's strict writer (`chupa.evidence.attempt/1.0`) and read by its tolerant reader; schema rules are the evidence plan's §5.
- A failed write is logged to the engine log and never fails or blocks the terminal, like harvest.
- Written on every terminal, including `gate_failed`, `premise_failed`, `rejected`, and the conflict discard-and-rerun from `docs/parallel-tickets-plan.md` §5 step 3, because those are the negative examples.

### 3. Export: training records

`chupa training export [--since DATE] [--kinds ...] [--holdout PCT] --out DIR` reads the journal, git, and the store, and writes JSONL. Like `status`, it is a derived view that can always be rebuilt and is never hand-edited. Record kinds:

| Kind | Input | Target | Label source |
|---|---|---|---|
| `implement` | rendered implement prompt | normalized tool-call events + final diff | merged / snagged / rejected |
| `preference` | implement prompt | (rejected diff, accepted diff) | the Review finding on the rejected one |
| `review` | ticket + diff | verdict + findings | whether the merged diff was later blamed (retro attribution) |
| `ticket` | Suggestion Box message | authored ticket | requisition verdict, lint findings, later premise failures |
| `triage` | box message | author / tombstone / declined | operator overrides (`override_report`, `chupa/box.py:18`) |
| `diagnosis` | terminal + harvest | diagnosis reply | whether the next attempt succeeded |
| `conflict` | both sides of a merge conflict | resolution | merged green or not; exists once `merge-model-resolve` has merged, else skipped with a count |

- Each record carries `stem` (null for ticketless surfaces), `group` (stem or surface), `run_seq`, `attempt`, the call keys, `engine_version`, and the spec name and `version`, so records can be filtered by which spec produced them. Records for triage and Author come from calls keyed under the surface name (roadmap decision 3).
- Output formats: chat-message JSONL for supervised tuning, and `{prompt, chosen, rejected}` JSONL for preference tuning. Both are the common shapes most local tuning tools accept, so no tool-specific format is needed.
- `--holdout PCT` splits by ticket (never by call, so one ticket never appears in both sets) and writes the held-out stems to a file, so a later evaluation uses tickets the model never saw.
- Before writing, export runs a second scrub: the redactor, the `exclude` globs applied to file paths in tool calls, and a fixed pattern set for common credential shapes (AWS keys, `-----BEGIN ... PRIVATE KEY-----`, bearer tokens). Any record that matches is dropped and counted in the export summary, never partly written.
- Labels: an attempt is negative only when review snagged it on `logic`, `acceptance`, `scope`, or `leak` (`chupa/specs/review.md:106`). `rma`, premise, and infra outcomes are exported with a neutral label.

### 4. The flywheel: how a host uses it

chupa never trains a model and never sends data anywhere. It provides three things:

1. **Retrieval first (no training).** Past tickets, decisions from `run.md`, and review findings are the cheapest win: a host can index the export and feed similar past tickets into Context. This is a host choice. chupa adds no retrieval feature in this plan.
2. **A local provider on narrow surfaces.** chupa already routes by `(tier, surface)` to providers such as a local `qwen` through Ollama. A host tunes a small model on its `triage`, `review`, or `ticket` records and routes only that surface to it. The existing GO baseline (`docs/how-chupa-works.md` §9.6) decides whether that model's output is trusted for auto-confirm.
3. **Measured, not assumed.** `chupa training eval --route <tier>/<surface> --holdout FILE` replays held-out records through the given route and scores agreement with the recorded outcome (verdict match for review, triage, and requisition; check pass rate for implement). It is the evidence a host needs before routing a surface to its own model, and it is also the triage-dedup eval that `CHUPA_PLAN.md` §18.2 deferred to the daemon era (roadmap §3.3). The report goes to stdout and the engine log, never to the journal.

## Rights and privacy

- Everything stays on the host's machine under `state_dir`. chupa never uploads it, and it is never committed (`state_dir` is gitignored).
- Prompts embed host code and anything the agent read. The host owns that data and decides what to train on.
- **Provider terms:** model outputs come from third-party providers whose terms may restrict using those outputs to train other models. The host must check each provider's terms before training on the export. `export` prints this notice once per run, and the host guide says so too. chupa does not decide this for the host.
- Redaction is best effort beyond configured secrets. The `exclude` globs and the export scrub cut the risk but do not remove it. A host that handles regulated data should keep `enabled: false`, or exclude those paths.

## Where each piece lives

| Piece | Home |
|---|---|
| Config model and validation | `chupa/config.py` (`TrainingData`) |
| Attempt manifest schema | `chupa/evidence/schema.py` (beside the call schemas; the evidence plan owns the module) |
| Attempt manifest writer | `chupa/runner.py` terminal path, next to harvest, through the evidence store's writer |
| Export, eval | new `chupa/training.py` |
| CLI verbs `training export`, `training eval` | `chupa/__main__.py`, plus `./dev.py training-export` and `training-eval` |
| Operator docs | `docs/how-chupa-works.md` (config table, §10.1), `chupa/docs/host-contract.md` (setup and the provider-terms notice), `chupa/docs/host-training.md` (new guide, listed by `chupa docs`) |
| CORE_TEMPLATE | No change: this is an operator feature, not an agent conduct rule |

## Ticket breakdown

Each ticket puts its tests in new files (`docs/parallel-tickets-plan.md` §7). Release 0.5.0.

| # | Stem | Kind | P | Depends on | Content |
|---|---|---|---|---|---|
| 1 | `training-config` | feature | P2 | | Section 1: `training_data` model, fixed exclude list, export and eval refusal when off. Config table in how-chupa-works and the host-contract inventory. |
| 2 | `training-attempt-manifest` | feature | P2 | `training-config`, `evidence-envelope` | Section 2: `chupa.evidence.attempt/1.0`, written before worktree removal on every terminal. |
| 3 | `training-export` | feature | P2 | `training-attempt-manifest` | Section 3: record kinds, both formats, `--holdout`, scrub with drop count, provider-terms notice, `./dev.py training-export`. |
| 4 | `training-eval` | feature | P3 | `training-export` | Section 4 item 3: replay held-out records through a named route and print agreement scores; `./dev.py training-eval`. |
| 5 | `training-docs` | chore | P3 | `training-export` | `chupa/docs/host-training.md` and the `docs` verb entry: enabling, exclusions, provider terms, retrieval-first advice. |

`Runs before`: none within the plan beyond the dependencies. `contention-authoring-rules` (roadmap row 13) runs before every ticket here.

## Risks

- **Disk.** The evidence store is bounded by `evidence.max_gb`; attempt diffs are small next to raw streams, and content addressing stores a diff shared by retries once.
- **Small data.** Hundreds of tickets per host. The plan says so up front and points hosts at retrieval and narrow-surface tuning, where small data is enough.
- **Label noise.** A snag can come from a bad ticket, not bad code. Section 3 labels only `logic`, `acceptance`, `scope`, and `leak` snags negative.
- **Training on the engine's own prompts.** Records include chupa's spec text, so a tuned model learns that spec version. Every record carries spec `version`, so records from older specs can be filtered out.
- **Unscrubbed harvest today.** Until `redaction-harvest-seam` (0.2.0) lands, `harvest.json` may hold unredacted finding text; export runs its own scrub, but the file on disk is the roadmap's problem, not this plan's.

## Open decisions

Defaults if the owner says nothing are recorded in `docs/roadmap.md` section 6.

1. **Store the full tool-call stream in the export, or only prompts, outputs, and diffs?** The stream is the most valuable part (it shows how the work was done) and the largest. Recommend storing it; the evidence store already holds it.
2. **Build `training eval` in chupa, or leave evaluation to hosts?** Recommend building it. Without an in-chupa measure, "the local model is good enough" is a guess, and the GO baseline already sets the precedent.
3. **Should export include tickets from Author (engine-written), or only ones a person confirmed?** Recommend both, with an `authored_by` field so hosts can filter.
4. **Move `spools/<stem>/<attempt>/` onto the evidence store?** Not scheduled by any plan. Recommend a follow-up once the store has run for a release; until then two capture paths exist (the per-attempt spool and the store), which roadmap decision 1 accepts.
