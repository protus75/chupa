# Training data capture: plan

Record what chupa's model runs produce, including the parts that are thrown away today, in a local store next to the journal. Add an export verb that turns the journal, git history, and that store into training records. A host that runs chupa on its own project builds up examples of its own work: tickets, attempts, rejections, review findings, fixes, and the code that finally merged. With those it can train or tune a local model that takes over part of its future work.

The aim is a flywheel, not a replacement model. A few hundred tickets will not train a general coding model. They are enough for retrieval over past work, and for tuning a small model on narrow, high-volume tasks (triage, ticket review, first-pass code review), where the host's own conventions matter more than general skill.

## Status

Draft plan. Nothing in it is in effect and no ticket is authored. Written 2026-11-13 at commit `0895b5d4`.

## Why chupa data is unusually good training data

Most agent logs have no reliable label. chupa's lifecycle labels every attempt as a side effect of running it:

- **Input:** the ticket (Goal, Scope, Acceptance criteria, Context), checked by lint and by the requisition review before any work starts.
- **Trajectory:** the rendered prompt, the agent's tool-call stream, and the diff.
- **Outcome:** Check results, the Review verdict with findings, the diagnosis, and finally either a squash commit on `main` (with `chupa-ticket` and `chupa-reviewed-sha` trailers) or a rejection.
- **Pairs:** one ticket often has a rejected attempt and then an accepted one. That gives a (prompt, worse, better) preference pair with a stated reason (the review finding) for why one was worse.
- **Delayed label:** a merged change later blamed for a red merge or a bug ticket (retro attribution, §14 of the design record) turns a positive example into a negative one.

## Current state

What already exists, under `state_dir` (this repo: `.chupa/state`) and in git:

| Source | Holds | Kept? |
|---|---|---|
| Journal (`journal/*.jsonl`, 15 MB here) | State transitions, cap draws, signals, and each model call's result text under effect keys `llm/<stem>/<run_seq>/<surface>/<attempt>/<call>` | Yes, the source of truth |
| `tickets/<stem>/` on `main` | `ticket.md`, `run.md`, `checks.json`, `review.md`, `attempts/<n>/harvest.json`, `diagnosis.json` | Yes, in git |
| Squash commits on `main` | The merged code, with `chupa-ticket` and `chupa-reviewed-sha` trailers | Yes, in git |
| `spools/<stem>/<attempt>/` | Each call's `prompt.md` and `output.txt`, and command output (`check/verify-NN.txt`) | No retention policy (1.2 GB here) |
| `spools/providers/<stem>/<provider>-<seq>/` | Raw CLI capture: `prompt.md`, `events.jsonl` (the full tool-call stream), `stderr.txt` | **Partly lost** (see below) |
| `engine.log` | Stage start and end, and other diagnostics | Rotated at 4 x 16 MB, so it is lost over time |

Gaps that matter for training data:

1. **Rejected code is discarded.** Before each attempt, the old worktree and branch of that stem are removed (how-chupa-works §4.1). `harvest.json` keeps only a diff stat and the last 4,000 characters of the logs. The code that review snagged, which is the negative half of every preference pair, is gone.
2. **Raw provider captures get overwritten.** The capture counter `_seq` starts at 0 in each process (`chupa/providers.py:294`), so a second run of a stem in a new process writes over `claude-0001` and the rest. This repo's journal has 3,944 model-call completions but only 2,301 capture directories. The worst cases are `triage` (467 calls, 282 directories) and `author` (336 calls, 157 directories).
3. **Nothing links a journal record to its capture.** The journal key is `llm/<stem>/<run_seq>/<surface>/<attempt>/<call>`; the capture path is `providers/<stem>/<provider>-<seq>`. You can only match them up by timestamp.
4. **Only configured secrets are redacted.** The redactor scrubs configured secret values. An agent that reads a `.env` file or a customer data file puts that content into `events.jsonl` unscrubbed.

## Target design

### 1. Config (experimental)

```yaml
training_data:          # experimental; off by default
  enabled: false
  dir: null             # default <state_dir>/training
  max_gb: 20            # oldest unreferenced blobs are pruned beyond this
  exclude: []           # path globs whose content is never stored, e.g. [".env*", "data/customers/**"]
```

- A new `TrainingData` model in `chupa/config.py`, added to `Config` with default `TrainingData()`.
- When `enabled` is false, nothing is captured beyond what is captured today, and `export` refuses with the paved road "set training_data.enabled: true; only runs after that are captured".
- `exclude` adds to a fixed list of globs that are always excluded (`.env*`, `*.pem`, `*.key`, `id_*`). It cannot remove entries from that list (fail closed).

### 2. The training data store (sidecar)

`<dir>/` is a content-addressed store plus one manifest per model call or attempt. It is separate from the journal, which stays the record of what happened and never becomes a debug log.

```
training/
  blobs/ab/abcdef...        # sha256-named, zstd-compressed, redacted before hashing
  calls/<journal-effect-key>.json
  attempts/<stem>/<run_seq>/<attempt>.json
```

- **Call manifest**: the evidence record defined in `docs/evidence-trail-plan.md` (envelope, raw blobs, normalized events), keyed by the journal effect key. That plan owns the call-level schema; this one adds attempt manifests, retention, and export.
- **Attempt manifest**, written at the attempt's terminal before the worktree is removed: base sha, branch head sha, blob id of the full attempt diff (`git diff base..head`, minus excluded paths), blob ids for each Check command output, the call keys used, the terminal outcome, and the review verdict.
- **Links:** the store refers to the journal by effect key, and the journal does not change. `engine.log` stage events gain a `call_key` field, so a log line leads straight to its manifest. Because the store is content-addressed, the 88 KB prompt that is re-sent on every retry is stored once.
- **Writes go through the existing seams** (`FileSystem`, the redactor) in one new module, `chupa/training.py`. A failed write is logged to the engine log and never fails or blocks a run (like harvest).
- **Retention:** when the store goes over `max_gb`, blobs referenced only by the oldest attempt manifests are pruned first. Manifests are kept, so the record of what was lost stays.

### 3. Export: training records

`chupa training export [--since DATE] [--kinds ...] --out DIR` reads the journal, git, and the store, and writes JSONL. Like `status`, it is a derived view that can always be rebuilt and is never hand-edited. Record kinds:

| Kind | Input | Target | Label source |
|---|---|---|---|
| `implement` | rendered implement prompt | tool-call stream + final diff | merged / snagged / rejected |
| `preference` | implement prompt | (rejected diff, accepted diff) | Review finding on the rejected one |
| `review` | ticket + diff | verdict + findings | Did the merged diff later get blamed? |
| `ticket` | Suggestion Box message | authored ticket | requisition verdict, lint findings, later premise failures |
| `triage` | box message | author / tombstone / declined | operator overrides (`override_report`) |
| `diagnosis` | terminal + harvest | diagnosis reply | did the next attempt succeed? |
| `conflict` | both sides of a merge conflict | resolution | merged green or not (once the parallel plan's model step exists) |

- Each record carries `stem`, `run_seq`, `attempt`, call keys, `engine_version` (the `chupa` tree sha), and the spec name and `version`, so records can be filtered by which spec or prompt produced them.
- Output formats: chat-message JSONL for supervised tuning, and `{prompt, chosen, rejected}` JSONL for preference tuning. Both are the common shapes most local tuning tools accept, so no tool-specific format is needed.
- `--holdout PCT` splits by ticket (never by call, so one ticket never appears in both sets) and writes the held-out stems to a file, so a later evaluation uses tickets the model never saw.
- Before writing, export runs a second scrub: the redactor, the `exclude` globs applied to file paths in tool calls, and a fixed pattern set for common credential shapes (AWS keys, `-----BEGIN ... PRIVATE KEY-----`, bearer tokens). Any record that matches is dropped and counted in the export summary, never partly written.

### 4. The flywheel: how a host uses it

chupa never trains a model and never sends data anywhere. It provides three things:

1. **Retrieval first (no training).** Past tickets, decisions from `run.md`, and review findings are the cheapest win: a host can index the export and feed similar past tickets into Context. This is a host choice. chupa adds no retrieval feature in this plan.
2. **A local provider on narrow surfaces.** chupa can already route by tier to providers such as a local `qwen` through ollama. A host tunes a small model on its `triage`, `review`, or `ticket` records and routes only that surface to it. The existing GO baseline gate decides whether that model's output is trusted for auto-confirm.
3. **Measured, not assumed.** `chupa training eval --model <route> --holdout FILE` replays held-out records through the given route and scores agreement with the recorded outcome (verdict match for review, triage, and requisition; check pass rate for implement). It is the evidence a host needs before routing a surface to its own model. The report goes to stdout and the engine log, never to the journal.

## Rights and privacy

- Everything stays on the host's machine under `state_dir`. chupa never uploads it, and it is never committed (`state_dir` is already gitignored).
- Prompts embed host code and anything the agent read. The host owns that data and decides what to train on.
- **Provider terms:** model outputs come from third-party providers whose terms may restrict using those outputs to train other models. The host must check each provider's terms before training on the export. `export` prints this notice once per run, and the setup guide says so too. chupa does not decide this for the host.
- Redaction is best effort beyond configured secrets. The `exclude` globs and the export scrub cut the risk but do not remove it. A host that handles regulated data should keep `enabled: false`, or exclude those paths.

## Where each piece lives

| Piece | Home |
|---|---|
| Config model and validation | `chupa/config.py` |
| Store, manifests, prune, export, eval | new `chupa/training.py` |
| Call capture hook | `chupa/driver.py` (already spools the prompt and output) and `chupa/providers.py` (capture directory named by call key) |
| Attempt manifest before worktree removal | `chupa/runner.py` terminal path, next to harvest |
| CLI verbs `training export`, `training eval` | `chupa/__main__.py`, plus `./dev.py` subcommands that run them |
| Operator docs | `docs/how-chupa-works.md` (config table, §10.1 state files, new section), `docs/host-contract.md` (setup and the provider-terms notice) |
| CORE_TEMPLATE | No change: this is an operator feature, not an agent conduct rule |

## Ticket breakdown

Each ticket puts its tests in a new file (see the contention rules in `docs/parallel-tickets-plan.md` §7).

| # | Stem | Kind | P | Depends on | Content |
|---|---|---|---|---|---|
| 1 | `provider-capture-overwrite` | bug | P0 | | Name capture directories by the journal call key so a new process cannot overwrite an earlier capture. Evidence: 3,944 journaled calls against 2,301 capture directories. Needed whether or not this feature ships, because diagnosis reads these captures. |
| 2 | `training-config` | feature | P2 | | Section 1: `training_data` model, fixed exclude list, export refusal when off. Config table in how-chupa-works. |
| 3 | `training-store` | feature | P2 | 2, `evidence-envelope` | Section 2: retention and prune over the evidence store, `call_key` in engine.log stage events. The store and call records come from `docs/evidence-trail-plan.md` tickets 2-3. |
| 4 | `training-attempt-manifest` | feature | P2 | 3 | Attempt manifest and full diff, written before worktree removal on every terminal, including snag, reject, and conflict discard. |
| 5 | `training-export` | feature | P2 | 4 | Section 3: record kinds, both formats, `--holdout`, scrub with drop count, provider-terms notice, `./dev.py training-export`. |
| 6 | `training-eval` | feature | P3 | 5 | Section 4 item 3: replay held-out records through a named route and print agreement scores. |
| 7 | `training-docs` | chore | P3 | 5 | Host setup guide in `docs/host-contract.md`: enabling, exclusions, provider terms, retrieval-first advice. |

Ticket 1 is a real defect found while writing this plan. Under the CORE routing rules it is a product instance (P0). Its cause fix is the class rule "every capture path is keyed by the journal identity of what it captures", which tickets 3 and 4 put into code for all new captures.

## Risks

- **Disk.** Spools are 1.2 GB on this repo already with no retention. Content addressing and zstd should shrink the new store well below that, and `max_gb` caps it. The existing `spools/` stays as it is. Moving spools onto the store is deferred.
- **Small data.** Hundreds of tickets per host. The plan says so up front and points hosts at retrieval and narrow-surface tuning, where small data is enough.
- **Label noise.** A snag can come from a bad ticket, not bad code (`rma`, premise failures). Export labels an attempt negative only when review snagged it on `logic`, `acceptance`, `scope`, or `leak`. `rma`, premise, and infra outcomes are exported with a neutral label.
- **Training on the engine's own prompts.** Records include chupa's spec text. A model tuned on them learns that spec version. Every record carries spec `version`, so records from older specs can be filtered out.

## Open decisions

1. **Store the full tool-call stream, or only prompts, outputs, and diffs?** The stream is the most valuable part (it shows how the work was done) and the largest. Recommend storing it, under `max_gb`.
2. **Keep `spools/` separate, or make it a view on the store?** Recommend separate for now: one source of truth per job, and spools work with the feature off.
3. **Build `training eval` in chupa, or leave evaluation to hosts?** Recommend building it. Without an in-chupa measure, "the local model is good enough" is a guess, and the GO baseline already sets the precedent.
4. **Should export include tickets from Author (engine-written), or only ones a person confirmed?** Recommend both, with an `authored_by` field so hosts can filter.
