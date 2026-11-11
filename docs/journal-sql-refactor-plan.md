# Journal SQL refactor plan

Change journal readers so history is bulk-loaded into an in-memory DuckDB once per process, only appended lines are read after that, and journal queries are SQL instead of Python loops over events.

## Status

Deferred. The refactor starts only at the feature checkpoint described in the release protocol. Until then this document is the plan of record, and nothing in it is in effect. Written 2026-11-11 at commit `bf121ef9`.

## Release protocol

1. **Checkpoint.** When the owner declares the current feature set complete, bump to the next minor version and tag that commit on main.
2. **Refactor window.** Only refactor tickets and the bugs the refactor surfaces run. No feature tickets run until the next minor version.
3. **Release.** When the refactor is complete and its surfaced bugs are fixed, cut a release.

Prerequisite: `./dev.py publish` bumps only the patch version, and nothing creates a tag. The repo rule "guides name verbs, not command lines" means the minor bump and tag need a verb before the checkpoint. That verb is ticket (a) below.

## Problem

Measured on 2026-11-11 (evidence: `tickets/journal-incremental-read/evidence/drain-start-journal-rereads.txt`):

- The journal held about 24k events in 12 segments, 12 MB.
- `Journal.read()` re-reads and re-parses every segment on every call: 0.13s per call.
- A profiled drain start made 491 `read()` calls, which took 157s of the run's 164s.
- `Journal.append()` re-parses the whole active segment on every write, just to check its first timestamp for the roll-age rule.
- Callers fold the returned `Event` lists with Python loops. There are 98 `read()` / `read_segments()` call sites across 28 modules (see the table under Ticket breakdown).

The cost grows faster than linearly as tickets accumulate. Each read costs more as events pile up, and more tickets means more reads.

## Target design

- **Bulk load.** Each process holds an in-memory DuckDB connection. At start it loads `.chupa/state/journal/*.jsonl` with DuckDB's parallel JSONL reader.
- **Incremental.** After the bulk load, the reader keeps the byte offset of the active segment. A query first inserts only the complete lines appended since then. An unterminated last line is left for a later read, as today. A segment that rolls between loads is read to its end and treated as immutable.
- **Single source of truth.** The JSONL segments stay the only authority, and nothing derived is saved to disk. A new process always rebuilds from the files, so no saved copy can disagree with the journal (repo rule: files and journal are the source of truth).
- **Schema.** One `events` table with columns `seq` (write order), `v`, `type`, `ts`, `ticket`, `key`, and `body` as JSON. Queries read body fields with `body->>'field'`.
- **Queries.** Journal questions are SQL, for example the last state per ticket, merges per day, first-pass yield, and filtering by ticket or type. Python receives query results, not whole event lists.
- **Writes unchanged.** `append()` keeps its write-ahead fsync contract. Its roll-age check reads only the active segment's first line.
- **Immutability contract.** Rolled segments are immutable and the active segment only grows. Tail truncation of a torn last line (`_truncate_torn_tail`) is the one exception, and it touches only bytes after the last newline. The reader relies on this contract and does not try to detect rewrites made by hand.

## Ticket breakdown

Future tickets, in order. None are authored yet; author them at the checkpoint.

- **(a) Release verb.** A `./dev.py` verb that bumps the minor version and tags the commit. It runs before the checkpoint.
- **(b) Query layer.** The DuckDB connection, bulk load, and incremental insert in `chupa/journal.py`. Adds the `duckdb` dependency to `pyproject.toml`, with unit tests for the offset logic and integration tests for rolls, torn tails, and other writers.
- **(c) Ports.** Module groups move from `read()` plus Python loops to SQL queries. Each port deletes the Python fold it replaces in the same change (repo rule: no dual-path code). Suggested grouping by subsystem:
  - Run path: `runner`, `stages`, `merge`, `mergequeue`, `rework`, `effects`, `driver`.
  - Loop: `drain`, `serve`, `daemon`, `scheduler`, `timers`, `watcher`, `control`, `checkpoint`, `reconcile`.
  - Feedback: `retro`, `triage`, `box`, `storm`, `flake`, `thresh`, `audit`, `notify`, `providers`.
  - CLI and authoring: `__main__`, `author`, `tickets`.
- **(d) Class prevention.** The rule and gate settled in the deferred decisions.
- **(e) Release.** The release that closes the refactor window.

Call sites: lines in `chupa/` that call `.read()` on a journal or call `.read_segments()`, excluding `chupa/journal.py` itself. The count comes from this grep, run at `bf121ef9`:

```
grep -rnE '\.read\(\)|\.read_segments\(\)' chupa/ | grep -E 'journal|\.read_segments' | grep -v '^chupa/journal.py'
```

| Module | Call sites |
|---|---|
| `runner.py` | 14 |
| `__main__.py` | 10 |
| `serve.py` | 8 |
| `drain.py` | 8 |
| `stages.py` | 6 |
| `author.py` | 5 |
| `retro.py` | 4 |
| `mergequeue.py` | 4 |
| `merge.py` | 4 |
| `triage.py` | 3 |
| `providers.py` | 3 |
| `daemon.py` | 3 |
| `checkpoint.py` | 3 |
| `storm.py` | 2 |
| `rework.py` | 2 |
| `reconcile.py` | 2 |
| `flake.py` | 2 |
| `effects.py` | 2 |
| `driver.py` | 2 |
| `control.py` | 2 |
| `box.py` | 2 |
| `watcher.py` | 1 |
| `timers.py` | 1 |
| `tickets.py` | 1 |
| `thresh.py` | 1 |
| `scheduler.py` | 1 |
| `notify.py` | 1 |
| `audit.py` | 1 |
| **Total (28 modules)** | **98** |

Re-run the grep at the checkpoint; the numbers will have moved.

## Deferred decisions

Each item is undecided. Decide at the checkpoint, before authoring ticket (b).

1. **DuckDB or Polars.** Options: DuckDB SQL, or Polars `scan_ndjson` with dataframe code. Recommendation: DuckDB. It reads multiple JSONL files natively in parallel, and a SQL query is plain text that an agent can read and review. Pick one, not both.
2. **What happens to `journal-incremental-read`.** That ticket adds an in-memory cache in pure Python. If it has not merged by the checkpoint, options are to ship it as a stopgap or drop it in favor of (b). Its open review snag (same-size rewrites of rolled segments go undetected) is resolved by stating the immutability contract above. Recommendation: ship it as a stopgap if the drain start is still slow before the checkpoint.
3. **Rule and gate.** Should "journal queries are SQL, not Python loops" become a CLAUDE.md and AGENTS.md rule? Should a lint gate enforce it, for example no `journal.read()` outside `chupa/journal.py`? Recommendation: both, with the gate landing in the last port so it never fails on unported code.
4. **Body access.** Options: raw `body->>'field'` everywhere, or one view per event type with typed columns. Recommendation: start raw, and add a view when the same extraction appears in three or more queries.
5. **Validation and error messages.** Today a bad line raises `JournalCorruption` naming the file and line number, and DuckDB's error messages are less precise. Options: run the Python line parser on a segment only when DuckDB's load of it fails, or always validate in Python. Recommendation: run the parser on failure only.
6. **`chupa/observe.py`.** It has its own raw journal reader. Should it move to the query layer in this window or stay as it is?
7. **Filesystem seam.** DuckDB opens the segment files itself, outside chupa's injectable filesystem seam (repo rule: use the injectable seams). Options: pass bytes read through the seam into DuckDB, or accept direct reads for this one reader and record why.
8. **Python-only folds.** Some folds may be state machines that read badly as SQL (candidates: `reconcile`, `checkpoint`, `audit`). Should they be allowed to stay Python over query results, and what test keeps that exception from spreading?
9. **Equivalence testing.** Should each port be checked by comparing old and new results on a recorded journal fixture before the old fold is deleted? The comparison lives in the test only, and no second code path ships.
10. **Saved snapshots.** Rejected for now. Revisit only if the start-up bulk load measurably hurts.
11. **Release version.** Is the release after the refactor a patch release on the checkpoint's minor version, or the next minor version, which reopens feature work?
12. **Enforcing the freeze.** Options: operator discipline, or an engine hold that keeps `kind: feature` tickets from running during the window. A hold needs a release path (repo rule: a hold ships with its release).
