# Journal SQL refactor plan

Change journal readers so history is bulk-loaded into an in-memory DuckDB once per process, only appended lines are read after that, and journal queries are SQL instead of Python loops over events.

## Status

Deferred. The refactor starts only at the feature checkpoint described below, and only if re-measurement shows it is still needed. Until then this document is the plan of record, and nothing in it is in effect. Written 2026-11-11 at commit `bf121ef9`; revised 2026-11-13 at commit `80b76d5d` for `docs/roadmap.md`.

## Roadmap

Release 0.3.0, conditional (`docs/roadmap.md` §1 and rows 35-41). The release verb this plan's step (a) asked for is the roadmap's row 3 (`release-verb`, 0.2.0), because tagging 0.2.0 needs it first. The window's port tickets touch the same files as the parallel plan's `serve-parallel-dispatch` and `conflict-discard-rerun` (`runner`, `stages`, `merge`, `mergequeue`, `drain`, `serve`, `daemon`, `scheduler`), so those land after the window, or before it if the window slides behind 0.5.0 (roadmap decision 7). Shared budgets: one new dependency (`duckdb`), which is the `CHUPA_PLAN.md` D3 and §18.2 "DuckDB analytics engine" return, earned by the measurement below.

## Release protocol

1. **Checkpoint.** At the 0.2.0 tag, re-measure (section Problem). If the cost is still there, the owner declares the feature set complete and the window opens.
2. **Refactor window.** Only refactor tickets and the bugs the refactor surfaces run. No feature tickets run until 0.3.0 ships. The freeze is operator discipline plus the roadmap: no feature row is scheduled in 0.3.0.
3. **Release.** When the refactor is complete and its surfaced bugs are fixed, tag 0.3.0 with `./dev.py release --minor`.

## Problem

Measured on 2026-11-11 at `bf121ef9` (evidence: `tickets/journal-incremental-read/evidence/drain-start-journal-rereads.txt`):

- The journal held about 24k events in 12 segments, 12 MB.
- `Journal.read()` re-read and re-parsed every segment on every call: 0.13s per call.
- A profiled drain start made 491 `read()` calls, which took 157s of the run's 164s.
- `Journal.append()` re-parsed the whole active segment on every write, just to check its first timestamp for the roll-age rule.
- Callers fold the returned `Event` lists with Python loops. There were 98 `read()` / `read_segments()` call sites across 28 modules (101 at `80b76d5d`; see the table under Ticket breakdown).

**What changed since.** `journal-incremental-read` merged at `f790cf71`. `docs/how-chupa-works.md` §10.2 now says a Journal instance parses each byte once and re-reads only appended lines during normal append-only operation. The 157-second figure predates that fix. The §18.2 trigger ("the first projection measured too slow as a fold") fired once; whether it still holds is the re-measurement at the 0.2.0 tag: profile a drain start and `./dev.py status` on this repo's journal (now 14 segments, about 27k lines) and record the share of wall time in journal reads. If it is under a quarter, the window slides and this plan waits for the next measurement.

What the incremental reader did not change: 101 call sites still fold whole event lists in Python; `chupa/observe.py:254-256` has its own raw segment reader that returns dicts and wraps them in `SimpleNamespace` four times to call Event-typed helpers; `chupa/scheduler.py:80` reaches into `journal.dir.parent`, `journal._fs`, and `journal._clock`; and the roadmap's audit found the same "latest state for stem" scan written inline 13 times (`docs/roadmap.md` §2.1 row 5). Those are the costs a query layer removes whether or not the read time still dominates; the 0.2.0 ticket `journal-last-transition-helper` removes the worst of them without the dependency.

## Target design

- **Bulk load.** Each process holds an in-memory DuckDB connection. At start it loads `.chupa/state/journal/*.jsonl` with DuckDB's parallel JSONL reader.
- **Incremental.** After the bulk load, the reader keeps the byte offset of the active segment. A query first inserts only the complete lines appended since then. An unterminated last line is left for a later read, as today. A segment that rolls between loads is read to its end and treated as immutable.
- **Single source of truth.** The JSONL segments stay the only authority, and nothing derived is saved to disk. A new process always rebuilds from the files, so no saved copy can disagree with the journal (repo rule: files and journal are the source of truth).
- **Schema.** One `events` table with columns `seq` (write order), `v`, `type`, `ts`, `ticket`, `key`, and `body` as JSON. Queries read body fields with `body->>'field'`. Signal writers use two body keys for the signal name (`signal` and `kind`; roadmap §4.1 row for line 708); the view that names signals reads both until `docs-truth-sweep` settles one.
- **Queries.** Journal questions are SQL, for example the last state per ticket, merges per day, first-pass yield, and filtering by ticket or type. Python receives query results, not whole event lists.
- **Writes unchanged.** `append()` keeps its write-ahead fsync contract. Its roll-age check reads only the active segment's first line. Several runs appending from one process (`docs/parallel-tickets-plan.md` §4) is covered by `journal.lock` (`docs/how-chupa-works.md` §10.1); the per-process offset sees their lines like any other writer's.
- **Immutability contract.** Rolled segments are immutable and the active segment only grows. Tail truncation of a torn last line (`_truncate_torn_tail`, `chupa/journal.py:196`) is the one exception, and it touches only bytes after the last newline. The reader relies on this contract and does not try to detect rewrites made by hand.
- **Other readers go.** `observe.py`'s raw reader and `scheduler.py`'s access to journal privates are ported in the CLI and authoring group; after the window `chupa/journal.py` is the only module that opens a segment file.

## Where each piece lives

| Piece | Home |
|---|---|
| Connection, bulk load, incremental insert, query helpers | `chupa/journal.py` |
| Dependency | `pyproject.toml` (`duckdb`) |
| Ports | the module groups below, each deleting the Python fold it replaces |
| Rule and gate | `CLAUDE.md`, `AGENTS.md` (repo rules, outside the managed block); the lint in `chupa/gates.py` or a `./dev.py` check |
| Docs | `docs/how-chupa-works.md` §10.2 |

## Ticket breakdown

Future tickets, in order. None are authored yet; author them at the checkpoint. The stem `journal-sql-refactor-plan` is taken (rejected in the journal; its directory is gone) and is not reused.

| # | Stem | Kind | P | Depends on | Content |
|---|---|---|---|---|---|
| 0 | (re-measure) | evidence | | | Profile a drain start and `status` at the 0.2.0 tag; attach the output as evidence to ticket 1. Not a ticket. |
| 1 | `journal-query-layer` | feature | P2 | `release-verb` (roadmap row 3) | The DuckDB connection, bulk load, and incremental insert in `chupa/journal.py`; the `duckdb` dependency; unit tests for the offset logic and integration tests for rolls, torn tails, and other writers. |
| 2 | `journal-ports-run-path` | chore | P2 | `journal-query-layer` | `runner`, `stages`, `merge`, `mergequeue`, `rework`, `effects`, `driver`. |
| 3 | `journal-ports-loop` | chore | P2 | `journal-query-layer` | `drain`, `serve`, `daemon`, `scheduler`, `timers`, `watcher`, `control`, `checkpoint`, `reconcile`. |
| 4 | `journal-ports-feedback` | chore | P2 | `journal-query-layer` | `retro`, `triage`, `box`, `storm`, `flake`, `thresh`, `audit`, `notify`, `providers`. |
| 5 | `journal-ports-cli-authoring` | chore | P2 | `journal-query-layer` | `__main__`, `author`, `tickets`, `observe` (its raw reader goes), `scheduler.write_queue`'s journal access. |
| 6 | `journal-query-rule-gate` | chore | P2 | 2, 3, 4, 5 | The rule "journal queries are SQL, not Python loops" in `CLAUDE.md` and `AGENTS.md`, and the lint that refuses `journal.read()` outside `chupa/journal.py`. Lands last so it never fails on unported code. |

Each port deletes the Python fold it replaces in the same change (repo rule: no dual-path code). Tickets 2-5 touch disjoint module sets and could run in parallel under `docs/parallel-tickets-plan.md` if that has shipped by then; it has not under the default order (0.4.0), so they run in sequence.

Call sites: lines in `chupa/` that call `.read()` on a journal or call `.read_segments()`, excluding `chupa/journal.py` itself. Counts at `bf121ef9`; re-run at the checkpoint:

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

## Risks

- **The dependency.** `duckdb` is a compiled wheel; the repo rule is pure Python with external binaries only through argv wrappers. DuckDB is a library, not a binary, and D3 named it as the one allowed return for this trigger. The plan records that here so the next reader does not re-litigate it.
- **The filesystem seam.** DuckDB opens the segment files itself, outside the injectable `FileSystem`. Open decision 5.
- **Equivalence.** A port that changes a fold's result silently is the main risk. Open decision 7.

## Open decisions

Each item is undecided. Decide at the checkpoint, before authoring ticket 1. Defaults if the owner says nothing are recorded in `docs/roadmap.md` section 6.

1. **DuckDB or Polars.** Options: DuckDB SQL, or Polars `scan_ndjson` with dataframe code. Recommendation: DuckDB. It reads multiple JSONL files natively in parallel, and a SQL query is plain text that an agent can read and review. Pick one, not both.
2. **Rule and gate.** Should "journal queries are SQL, not Python loops" become a `CLAUDE.md` and `AGENTS.md` rule? Should a lint gate enforce it? Recommendation: both, with the gate landing in ticket 6.
3. **Body access.** Options: raw `body->>'field'` everywhere, or one view per event type with typed columns. Recommendation: start raw, and add a view when the same extraction appears in three or more queries.
4. **Validation and error messages.** Today a bad line raises `JournalCorruption` (`chupa/journal.py:124`) naming the file and line number, and DuckDB's error messages are less precise. Recommendation: run the Python line parser on a segment only when DuckDB's load of it fails.
5. **Filesystem seam.** Options: pass bytes read through the seam into DuckDB, or accept direct reads for this one reader and record why. Recommendation: direct reads, recorded in `chupa/journal.py`'s docstring, because DuckDB's parallel reader is the point.
6. **Python-only folds.** Some folds may be state machines that read badly as SQL (candidates: `reconcile`, `checkpoint`, `audit`). Should they stay Python over query results, and what test keeps that exception from spreading? Recommendation: allowed, each named in the gate's allowlist.
7. **Equivalence testing.** Should each port be checked by comparing old and new results on a recorded journal fixture before the old fold is deleted? The comparison lives in the test only, and no second code path ships. Recommendation: yes, on this repo's journal as the fixture.
8. **Saved snapshots.** Rejected for now. Revisit only if the start-up bulk load measurably hurts.
9. **Release version.** 0.3.0 is a minor version by the roadmap's rule (one minor per release theme); the question whether a refactor release should be a patch is closed by that rule.

Settled since the first draft: `journal-incremental-read` merged (its review snag about same-size rewrites of rolled segments is answered by the immutability contract above); `observe.py` ports in ticket 5; the freeze is enforced by the roadmap's schedule, not an engine hold.
