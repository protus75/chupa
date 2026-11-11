---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- chupa/journal.py
- docs/how-chupa-works.md#10. State on disk
- tickets/journal-incremental-read/ticket.md
- tickets/journal-incremental-read/evidence/drain-start-journal-rereads.txt
- pyproject.toml
- dev.py

## Goal / Why
Chupa's journal readers re-parse the whole JSONL journal and fold it with Python loops. On 2026-11-11 the journal held about 24k events in 12 segments (12 MB). One `read()` took 0.13s, and a profiled drain start spent 157s of 164s in 491 `read()` calls (see the evidence file in Context). Both the per-read cost and the number of reads grow as tickets accumulate.

The owner has decided to fix this with a deliberate refactor at a later date, not piecemeal. Journal history is loaded into an in-memory DuckDB in each process, using DuckDB's parallel JSONL read. Only appended lines are read after that, and journal queries are written in SQL, not as Python loops over events. The refactor runs in a dedicated release window after a feature checkpoint.

When this ticket is done, `docs/journal-sql-refactor-plan.md` records that plan, its release protocol, its ticket breakdown, and every decision deferred to the refactor window. The owner can then pick it up at the checkpoint without rebuilding this context. This ticket writes the plan document only. It changes no code, dependency, or other document.

## Scope in / Scope out
- In: a new `docs/journal-sql-refactor-plan.md` with these sections, in this order:
  1. `## Status`: the refactor is deferred. It starts only at the feature checkpoint described in the release protocol. Until then this document is the plan of record and nothing in it is in effect.
  2. `## Release protocol`:
     - At the feature checkpoint, bump the minor version (0.1.x to 0.2.0) and tag that commit on main.
     - Then only the refactor tickets and bugs that the refactor surfaces run.
     - The release after the refactor lands is cut once the refactor is complete and its surfaced bugs are fixed.
     - No feature tickets run until the next minor version.
     - Note that `./dev.py publish` bumps only the patch version and nothing tags. The protocol therefore needs a verb for the minor bump and tag (repo rule: guides name verbs, not command lines). That verb is the first prerequisite ticket.
  3. `## Problem`: the measured numbers above, the 99 `journal.read()` / `read_segments()` call sites across 28 `chupa/` modules, and why the cost grows with tickets.
  4. `## Target design`:
     - Each process holds an in-memory DuckDB, bulk-loaded at start from `.chupa/state/journal/*.jsonl` with DuckDB's parallel JSONL reader. After that, only complete lines appended since the last load are read and inserted.
     - The JSONL segments remain the only source of truth. Nothing derived is persisted, so no second authority can diverge (repo rule: files and journal are the source of truth).
     - Columns are `v, type, ts, ticket, key`, plus `body` kept as JSON and read with `body->>'field'`.
     - Journal queries are SQL, not Python loops over `Event` lists.
     - `append()` keeps its current write-ahead fsync contract.
  5. `## Ticket breakdown`, as an ordered list of future tickets, none authored now:
     - (a) the minor-bump-and-tag verb;
     - (b) the DuckDB query layer in `chupa/journal.py`, with the `duckdb` dependency and its tests;
     - (c) porting tickets that group the call-site modules. Include a table of every module with its call-site count, taken from a grep of the base commit and naming that grep. Each port deletes the Python fold it replaces in the same change (repo rule: no dual-path code);
     - (d) the class-prevention gate or rule from the deferred decisions;
     - (e) the release.
  6. `## Deferred decisions`: each item is a question with the options and a recommendation, marked undecided. At least these:
     - DuckDB vs Polars. Recommend DuckDB: it reads multiple JSONL files natively, and SQL is plain text an agent can read and review.
     - What happens to `journal-incremental-read` if it has not merged by the checkpoint: ship it as a stopgap, or drop it in favor of the query layer. Its open review snag (same-size rewrites of rolled segments go undetected) is resolved by stating the contract that rolled segments are immutable.
     - Whether "journal queries are SQL, not Python loops" becomes a CLAUDE.md and AGENTS.md rule, and whether a lint gate enforces it (for example, no `journal.read()` outside `chupa/journal.py`).
     - Raw `body->>` access vs per-event-type views.
     - Validation: how line-level `JournalCorruption` errors with path and line number survive. Recommendation: when DuckDB's load fails, re-run the Python line parser on that segment to report the line.
     - Whether `chupa/observe.py`'s separate raw journal reader is in scope.
     - How DuckDB's file reads fit the injectable filesystem seam (repo rule: use the injectable seams).
     - Whether any fold stays in Python, and the test that keeps it honest.
     - Equivalence testing: whether a port is checked by comparing old and new results on a recorded journal before the old fold is deleted, without shipping both paths.
     - Persisted snapshots: rejected for now. Revisit only if the start-up bulk load measurably hurts.
     - The version number of the release after the refactor.
     - How the feature freeze is enforced during the window: operator discipline, or an engine hold on `kind: feature` tickets.
- Out:
  - Any code, dependency, test, or config change.
  - Authoring any of the future tickets.
  - Editing `tickets/journal-incremental-read/`, `CLAUDE.md`, `AGENTS.md`, `docs/how-chupa-works.md`, or `CHUPA_PLAN.md`.

## Scope fence
- docs/journal-sql-refactor-plan.md

## Acceptance criteria
1. `docs/journal-sql-refactor-plan.md` exists and has exactly the six `##` sections named in Scope in, in that order.
2. In `docs/journal-sql-refactor-plan.md`, `## Deferred decisions` lists every question named in Scope in, each marked undecided. A question resolved in the text instead of listed as undecided fails this criterion.
3. In `docs/journal-sql-refactor-plan.md`, `## Ticket breakdown` has a module table whose counts sum to the call-site total the document states, and the document names the grep that produced it.
4. `git diff --name-only` against the merge base lists only `docs/journal-sql-refactor-plan.md`.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- Any file other than `docs/journal-sql-refactor-plan.md` is changed.
- The document presents a deferred decision as settled.
- The document states the refactor is in effect, or that it starts before the feature checkpoint.
- The document proposes persisting a DuckDB database file as a source of truth.

## Time budget
- expected: 25m
- stuck: 60m
