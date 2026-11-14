# Cross-provider evidence trail: plan

Every model call chupa makes leaves one evidence record with the same shape, whichever provider served it. The record keeps the provider's raw output byte for byte, wraps it in an envelope of facts only chupa knows (what was asked, by which route, against which tree, at what time), and adds a normalized event view that a versioned normalizer derives from the raw bytes. The schema is versioned and open for extension. Because the raw bytes are always kept, any field a later schema version needs can be recovered from records written before anyone knew to ask for it.

This is the lower layer of `docs/training-data-plan.md`. That plan's "call manifest" becomes the evidence record defined here.

## Status

Draft plan. Nothing in it is in effect and no ticket is authored. Written 2026-11-13 at commit `0895b5d4`.

## Principles

1. **Raw first, everything else derived.** The provider's stdout and stderr are stored verbatim (after redaction) and never rewritten. The normalized view is a projection: it can be deleted and rebuilt by a newer normalizer at any time. Nothing is lost by normalizing badly today.
2. **Over-record what can only be captured live.** Arrival times, process resource use, the tree state before and after a writing call, the CLI version, and the routing decision all disappear when the call ends. They are cheap to record and impossible to rebuild. Anything that can be derived later from raw bytes or git is *not* stored twice.
3. **Closed vocabulary, open payload.** Normalized event kinds and tool classes are closed lists (fail closed, as elsewhere in chupa). Anything a normalizer cannot map is kept as an `unknown` event with its native payload, never dropped.
4. **One identity.** A record's id is the journal effect key of the call (`llm/<stem>/<run_seq>/<surface>/<attempt>/<call>`). Provider-native ids (session id, thread id, message uuid) are recorded alongside it so provider-side logs can be joined later.
5. **The journal does not change.** It stays the record of decisions. The evidence store refers to the journal by key. The journal never refers to the evidence store.

## Current state

How each adapter in `chupa/providers.py` handles its CLI today, and what this repo's captures contain (sampled from `.chupa/state/spools/providers/`):

| | claude | codex | qwen |
|---|---|---|---|
| Output mode | `--output-format stream-json --verbose` | `exec --json` | `-o stream-json` (Claude-shaped; `QwenAdapter` subclasses `ClaudeAdapter`) |
| Captures in this repo | 1,435 | 1,018 | 0 |
| Event types seen | `system/init`, `system/thinking_tokens`, `system/permission_denied`, `assistant`, `user`, `rate_limit_event`, `result/success` | `thread.started`, `turn.started`, `item.started`, `item.completed`, `turn.completed`, `turn.failed`, `error` | not yet observed |
| Tool calls | `tool_use` / `tool_result` content blocks with ids | items of type `command_execution`, `file_change` (no separate read or search: reads are shell commands) | expected Claude-shaped; unverified |
| Reasoning | `thinking` content blocks (text) plus `thinking_tokens` events | count only (`reasoning_output_tokens`) | unknown |
| Usage keys | `input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`, `output_tokens_details`, `server_tool_use`, `service_tier`, `iterations`, `speed`, plus `modelUsage` per model on `result` | `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`, `reasoning_output_tokens` | not yet observed |
| Cost | `total_cost_usd` on `result` | none (`est_cost_per_call_usd` in config) | none |
| Served model | `system/init.model`, `result.modelUsage` keys | not in the stream | not yet observed |
| CLI version | `system/init.claude_code_version` | not in the stream | not yet observed |

What chupa keeps today:

- `Parsed` (`chupa/providers.py:250`) keeps only `text`, `input_tokens`, `output_tokens`, and `usd`. For Claude, `input_tokens` is the sum of the three input buckets. For Codex it is the raw `input_tokens`. Whether those two numbers are comparable depends on whether Codex's `input_tokens` already includes `cached_input_tokens`. Nothing in chupa pins that, so the journaled token totals may mix two scales.
- `watchdog.CallMeter` (`chupa/watchdog.py:64`) has a second, separate set of rules that recognize Claude and Codex tool events for progress tracking.
- The raw capture (`prompt.md`, `events.jsonl`, `stderr.txt`) is written once the process exits. A killed or timed-out call keeps only what `process_capture` returned. No arrival times are recorded, so the time between events is lost.
- Capture directories are overwritten across processes (`_seq` resets to 0). `docs/training-data-plan.md` ticket 1 fixes that instance.

## Target design

### 1. Record layout

```
<state_dir>/evidence/
  blobs/<aa>/<sha256>              # zstd-compressed, redacted before hashing
  calls/<escaped effect key>/
    start.json                     # written at spawn
    end.json                       # written at exit, kill, or timeout
    normalized/<normalizer-id>.json  # derived, rebuildable, may hold several versions
```

`start.json` is written before the process starts, so a call that crashes, hangs, or is killed still leaves a record. A `start.json` with no `end.json` is itself evidence (the engine died mid-call). This layout replaces `spools/providers/`. There is one capture path, not two, and every reader (harvest, diagnosis, the watchdog's tail) moves to it in the same change.

### 2. Envelope schema (`chupa.evidence.call`, version 1.0)

`start.json`:

```json
{
  "schema": "chupa.evidence.call/1.0",
  "id": "llm/<stem>/<run_seq>/<surface>/<attempt>/<call>",
  "stem": "...", "run_seq": 3, "attempt": 0, "surface": "implement", "call": 1,
  "engine": {"version": "<chupa tree sha>", "spec": "implement.md", "spec_version": "3.4"},
  "route": {"tier": "medium", "effort": "high", "candidates": ["codex"], "chosen": "codex",
            "reason": "first|spill|failover", "config_sha": "<sha256 of config snapshot>"},
  "provider": {"name": "codex", "adapter": "CodexAdapter", "kind": "cli",
               "package": "@openai/codex", "cli_version": "x.y.z", "billing": "metered|subscription|local"},
  "model": {"requested": "gpt-6.1-terra"},
  "process": {"argv": ["...redacted..."], "env_names": ["PATH", "HOME"], "cwd": "<worktree>",
              "timeout_s": 5400, "writes": true},
  "repo": {"main_sha": "...", "base_sha": "...", "tree_before": "<git tree id>"},
  "prompt": {"blob": "sha256:...", "chars": 88986, "bytes": 89012},
  "clock": {"wall_start": "2026-11-13T19:35:00.123Z", "mono_start_ns": 123456789}
}
```

`end.json`:

```json
{
  "schema": "chupa.evidence.call/1.0",
  "id": "...",
  "exit": {"status": "ok|nonzero|killed|timeout|spawn_error", "code": 0, "signal": null,
           "failure_class": null},
  "clock": {"wall_end": "...", "mono_end_ns": 0, "wall_ms": 0},
  "rusage": {"user_s": 0.0, "sys_s": 0.0, "max_rss_kb": 0},
  "raw": {"stdout": "sha256:...", "stderr": "sha256:...",
          "stdout_times": "sha256:...", "lines": 412, "non_json_lines": 0},
  "repo": {"tree_after": "<git tree id>", "changed_paths": ["..."]},
  "model": {"served": "gpt-6.1-terra|null", "served_source": "stream|none"},
  "native_ids": {"session_id": "...", "thread_id": "..."},
  "parsed": {"text_chars": 0, "input_tokens": 0, "output_tokens": 0, "usd": null}
}
```

Notes on fields:

- `stdout_times` is a blob of arrival offsets (one monotonic nanosecond value per stdout line), captured through the exec seam's existing `on_stdout_line` hook. It is the only source for time-to-first-event, gaps between tool calls, and per-step latency. No provider stream reports those consistently.
- `tree_before` and `tree_after` are git tree ids from a temporary index (`git add -A` into `GIT_INDEX_FILE`, then `write-tree`, through `git.py`). They do not touch the branch, the real index, or the reflog. Together with the blob store, they let a later reader rebuild the exact worktree each writing call saw and left. Read-only surfaces record `tree_before` only.
- `env_names` records names only, never values.
- `parsed` repeats what `Parsed` returned, so a later normalizer can be checked against what the engine actually acted on.
- `cli_version`: Claude reports it in `system/init`. For others, the adapter runs `<binary> --version` once per process and caches it. The probe goes through the exec seam and is recorded in the engine log.

### 3. Normalized events (`chupa.evidence.events`, version 1.0)

A normalizer is a pure function from raw stdout bytes (plus `stdout_times`) to a list of events. Its id is `<provider>-stream/<n>`, for example `claude-stream/1`. Its output file records that id, so views from different normalizer versions can sit side by side.

Each event:

```json
{"seq": 17, "t_ms": 41230, "kind": "tool_call",
 "role": "assistant",
 "tool": {"id": "toolu_...", "class": "edit", "native": "Edit"},
 "args": {"path": "chupa/drain.py"}, "args_blob": "sha256:...",
 "status": null, "output_blob": null, "text_blob": null,
 "tokens": null,
 "native_type": "assistant/tool_use", "native": {"...unmapped fields...": "..."}}
```

Closed `kind` list: `session_start`, `message`, `reasoning`, `tool_call`, `tool_result`, `file_change`, `usage`, `rate_limit`, `permission_denied`, `error`, `result`, `unknown`.

Closed tool `class` list: `read`, `search`, `list`, `edit`, `write`, `shell`, `web_fetch`, `web_search`, `mcp`, `subagent`, `plan`, `other`. Every tool event also keeps its `native` tool name. Codex reads files through shell commands, so its reads are `shell`. A later normalizer version may split out commands such as `cat` or `rg` into `read` or `search` by parsing the command. That can be done from old raw bytes too.

Large text (tool output, assistant text, thinking text) goes to blobs. Events carry only the blob ids, so the events file stays small enough to load whole.

`reasoning` events carry `text_blob` when the provider exposes the text (Claude `thinking`), and only `tokens` when it reports a count (Codex). A `visibility` field says which: `text`, `summary`, `count_only`, or `none`.

### 4. Tokens and cost across providers

Token counts from different providers are not on the same scale: different tokenizers, and different rules for what "input" includes. The normalized `usage` event reports buckets with a stated basis, never a single blended number:

| Bucket | claude | codex |
|---|---|---|
| `input_uncached` | `input_tokens` | `input_tokens` minus `cached_input_tokens`, *if* Codex's total includes cached tokens (to be pinned by a fixture in ticket 4) |
| `input_cache_read` | `cache_read_input_tokens` | `cached_input_tokens` |
| `input_cache_write` | `cache_creation_input_tokens` | `cache_write_input_tokens` |
| `output_total` | `output_tokens` | `output_tokens` |
| `output_reasoning` | from `output_tokens_details` when present | `reasoning_output_tokens` |
| `tokenizer` | `anthropic` | `openai-o200k` (or the reported family) |

- Each bucket is nullable. A missing number stays `null`, never `0`.
- For comparisons across providers, the envelope always has `chars` and `bytes` for the prompt, and the export can add counts from one fixed reference tokenizer. Characters are the only scale that is the same for every provider.
- Cost: `usd_reported` (stream), `usd_estimated` (config `est_cost_per_call_usd`), and `billing` from the envelope. Subscription and local providers have a real marginal cost of about 0 and a quota cost. They are never mixed into one dollar total.
- `Parsed` and the journal are unchanged in this plan. If the Codex fixture shows that the current journaled `input_tokens` mix scales, that is a separate bug ticket against `Parsed`. It is not fixed silently here.

### 5. Versioning and extension

- **Schema ids** have the form `chupa.evidence.<record>/<major>.<minor>`. A minor bump only adds optional fields. A major bump renames or removes fields, or changes their meaning.
- **Writers are strict, readers are tolerant.** The writer validates each record against the current version's strict pydantic model (`extra="forbid"`, as elsewhere in chupa). Readers (export, eval, renormalize) accept any record with a known major version and ignore unknown fields. A reader that meets an unknown major version skips the record and counts it.
- **Envelopes are never rewritten.** A major bump changes only new records. `normalized/` views are rebuilt by `chupa evidence renormalize`, which runs the current normalizers over stored raw bytes. Old views can stay for comparison.
- **Adding a provider** takes three things: an adapter (exists today), a normalizer module `chupa/evidence/<provider>.py`, and a golden fixture (one redacted real stream per CLI version under `tests/fixtures/evidence/<provider>/`). A provider with no normalizer still gets full envelopes and raw bytes. Its records simply have no normalized view until one is written.
- **CLI version drift:** each normalizer declares the CLI versions its fixtures cover. Renormalizing a stream from an uncovered version still runs, but the result is flagged `unverified`.
- **Coverage report:** `chupa evidence coverage` prints, for each provider and CLI version, the share of raw events mapped to a known kind and the most common `unknown` native types. It shows where the next normalizer version should start.
- The JSON Schema for each record version is generated from the pydantic models (`chupa evidence schema`), so tools outside chupa can validate records without importing chupa.

### 6. What is deliberately over-recorded

Recorded now even though nothing reads it yet, because it cannot be rebuilt later:

| Field | Why keep it |
|---|---|
| Full stdout and stderr (not just the tail) | Every future normalizer starts here |
| `stdout_times` | Latency, stall, and pacing analysis; no provider reports it consistently |
| `tree_before` / `tree_after` | Which files each call changed, and the exact state each call saw |
| `cli_version`, `package`, `adapter` | Explains format changes and behavior shifts between CLI releases |
| Route `reason`, `config_sha` | Separates "the model was worse" from "a different model served the call" |
| `rusage`, exit signal | Separates resource exhaustion from model failure |
| Killed or timed-out calls (`start.json` with partial raw bytes) | Negative examples and failure analysis; dropped today |
| `native_ids` | Joins to provider-side logs and billing if a host ever needs them |

Not recorded: values of environment variables, files the agent read (they are in git at `tree_before`, or in the tool output already in raw), and the provider's own session logs under the user's home directory (see Open decisions).

### 7. Redaction

Raw bytes pass through the existing redactor before hashing, as `spools/providers/` does today. `_scrub_event` already scrubs decoded strings inside JSON events. The same applies to `args` and blobs in normalized events. The training-data export scrub (`docs/training-data-plan.md` §3) still runs on top. Hashing after redaction means a configured secret never reaches the blob store, not even as a hash of the original text.

## Where each piece lives

| Piece | Home |
|---|---|
| Record models, schema ids, JSON Schema generation | new `chupa/evidence/schema.py` |
| Blob store and record writer | new `chupa/evidence/store.py` (`FileSystem` seam, redactor) |
| Envelope capture at spawn and exit | `chupa/providers.py` (`CliAdapter.invoke`, replacing `_write_capture`) |
| Arrival times, rusage | `chupa/seams.py` exec seam (`on_stdout_line` already exists; add the timing and rusage return) |
| Temporary-index tree ids | `chupa/git.py` (new argv-list operation) |
| Normalizers | `chupa/evidence/claude.py` (qwen reuses it until a fixture shows a difference), `chupa/evidence/codex.py` |
| `evidence show`, `schema`, `renormalize`, `coverage` verbs | `chupa/__main__.py`, plus `./dev.py` subcommands |
| Docs | `docs/how-chupa-works.md` §8.5 (redaction), §10.1 (`evidence/` replaces `spools/providers/`), new section on the evidence record |

## Ticket breakdown

| # | Stem | Kind | P | Depends on | Content |
|---|---|---|---|---|---|
| 1 | `provider-capture-overwrite` | bug | P0 | | Instance fix (from `docs/training-data-plan.md`): key captures by journal call key. |
| 2 | `evidence-store` | feature | P2 | 1 | Blob store, schema module, strict writer, tolerant reader, JSON Schema generation. Pure apart from the `FileSystem` seam. New tests only. |
| 3 | `evidence-envelope` | feature | P2 | 2 | `start.json` and `end.json` from `CliAdapter.invoke`, arrival times and rusage through the exec seam, tree ids through `git.py`, CLI version probe. Move every reader of `spools/providers/` to the new path and delete the old writer (no dual path). |
| 4 | `evidence-normalize-codex` | feature | P2 | 2 | Codex normalizer and golden fixture. The fixture pins whether `input_tokens` includes `cached_input_tokens`. |
| 5 | `evidence-normalize-claude` | feature | P2 | 2 | Claude normalizer and golden fixture. qwen uses it, flagged `unverified` until a qwen fixture exists. |
| 6 | `evidence-verbs` | feature | P3 | 3, 4, 5 | `show`, `schema`, `renormalize`, `coverage`. |

Tickets 4 and 5 touch separate files and could run in parallel under `docs/parallel-tickets-plan.md`. The Gemini provider in `docs/gemini-graphics-refactor-plan.md` gets its normalizer as one more ticket of the same shape.

## Risks

- **Disk.** Full streams are already kept today (681 MB of provider captures in this repo). Content addressing removes repeated prompts, and zstd compresses JSON streams well. Arrival times add 8 bytes per line. Tree ids cost one `write-tree` per writing call and store nothing new in git beyond objects that are not referenced.
- **Temporary-index cost on large repos.** `git add -A` into a temporary index rehashes changed files only after the first run, but the first one on a big host can take seconds. Measure on the first large host before making it unconditional. If it is too slow, record `tree_after` only.
- **Normalizer drift.** CLI output formats change without notice. The coverage report and per-version fixtures make drift visible. Raw bytes make it recoverable.
- **Two parsers.** `Parsed`, `CallMeter`, and the normalizers all read the same streams. Moving `CallMeter` and `Parsed` onto the normalized events would leave one parser per provider. That move is deferred until the normalizers have run for a while, and is listed below.

## Open decisions

1. **Always on, or behind `training_data.enabled`?** Recommend: envelope and raw capture always on, since they replace today's always-on `spools/providers/` and also serve diagnosis. Long-term retention and attempt diffs stay behind `training_data.enabled`.
2. **Copy the provider's own session log** (Claude and Codex both write transcripts under the user's home directory)? Recommend not for now. It is outside chupa's custody, and the stdout stream holds the same events. `native_ids` keeps the join possible later.
3. **Store thinking text?** Claude exposes it, and it is the most useful part for training reasoning. Recommend storing it as a blob, like any other text.
4. **Move `CallMeter` and `Parsed` onto normalized events** (one parser per provider) after ticket 6? Recommend filing it as a suggestion once normalizers have run on real traffic for a while.
