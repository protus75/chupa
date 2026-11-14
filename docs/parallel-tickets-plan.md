# Parallel ticket runs: plan

Let `serve` run more than one ticket at a time, behind an experimental config switch. Tickets run together only when their scope fences do not overlap. The merge queue admits them one at a time and resolves conflicts in three steps: a mechanical merge strategy, then a model for small conflicts, then discarding the later ticket's branch and running it again. Authoring rules move new tests and fixtures out of the few large shared files that would otherwise force nearly every pair of tickets to run one after the other.

## Status

Draft plan. Nothing in it is in effect and no ticket is authored. Written 2026-11-13 at commit `0895b5d4`; revised 2026-11-13 at commit `80b76d5d` for `docs/roadmap.md`.

## Roadmap

Release 0.4.0 (`docs/roadmap.md` rows 42-48), except ticket 1 (`contention-authoring-rules`), which lands in 0.2.0 because every later plan depends on its rules. Needs from the roadmap's 0.2.0 dedup tickets: `active-slot-single-owner` (six "is something running" trackers become one; ticket 6 then edits one owner) and `merge-admission-single-owner` (inline merge and queue admission become one path; ticket 7 adds its step once). What needs this plan: `doc-lens-automatable` (`docs/document-agent-plan.md`) uses `fences_overlap`; the training plan's `conflict` record kind waits on `merge-model-resolve`. Shared files: `chupa/specs/implement.md` is bumped by both ticket 8 and `graphics-render-check`, which runs first (roadmap decision 8); the host-command lock in section 4 also serializes the graphics render command and the merge queue's host checks (decision 10). The 0.3.0 journal window edits the same engine files as tickets 6 and 8, so this plan lands after it, or before it if the window slides (decision 7).

## Current state

- **Dispatch runs one ticket at a time.** `chupa/scheduler.py` describes itself as a "single-flight dispatch projection": one `asyncio.Lock`, one `active` ticket. `DaemonAdmission` in `chupa/daemon.py` has the same single slot. `AdmissionBoundary.__call__` in `chupa/merge.py` relies on this: "Single-flight dispatch retains this run's snapshot", and it assigns `self.queue.ctx = ctx` for each offer. The idle and restart checks in `chupa/serve.py` (lines ~201, ~328) test `scheduler.active is None` and `admission.active is None`.
- **The merge queue is live in `serve`, not in `drain`.** `serve` sends every admission through `MergeQueue` (`chupa/mergequeue.py`) in `mode="daemon"`. `run` and `drain` merge inline (`merge.merge`), and inline merge refuses any rebase conflict with no resolution step (how-chupa-works §4.5). `drain` is the extension's default play action, so in day-to-day use the queue and its conflict handling never run. The module docstring still says "Dormant serial admission", which is out of date; `docs-truth-sweep` (roadmap row 4) fixes it along with `chupa/heartbeat.py`'s.
- **Conflict handling today** (how-chupa-works §7.2.1, plan §9.5): first, mechanical resolution through `merge.strategies` (`union`, `regenerate`). Anything else aborts the rebase and returns a `ConflictHandoff`. `daemon.consume_handoff` passes it to full Rework (`apply_rework`), which rewrites the *ticket* and ends the attempt `gate_failed`. No step has a model resolve the conflict itself. This repo's `config.yaml` sets `merge: {}`, so no strategies are declared.
- **Admission limits.** `scheduler.max_unmerged` (default 2) stops dispatch while that many finished tickets wait to merge. Provider slots (`limits.concurrency` in `chupa/thresh.py`) are set to 1 for both providers in `config.yaml`.
- **Contention in the existing tickets.** Of 539 tickets, the paths fenced most often are: `docs/how-chupa-works.md` 172, `chupa/__main__.py` 90, `chupa/stages.py` 65, `chupa/drain.py` 56, `chupa/runner.py` 55, `tickets` 51, `chupa/daemon.py` and `chupa/observe.py` 40 each, `tests/unit/test_specs.py` 36, `tests/test_stages.py` 33 (the path those tickets fenced; the file is now `tests/integration/test_stages.py`). The largest test files are `tests/integration/test_daemon_composition.py` (2,168 lines), `test_drain.py` (1,741), `test_mergequeue.py` (1,228), and the shared rig `tests/integration/serve_rig.py`.
- **Design record.** The plan defers a concurrent worker pool until there is "measured queue starvation" (D2, §18.2). D7 and §9.6 reject comparing two fences against each other ("estimate-vs-estimate") and say to act only on observed facts. This plan departs from both on purpose; see the next section.

## Departures from the design record

| Record says | This plan | Why it is safe |
|---|---|---|
| D2: one in-flight run; a worker pool needs measured starvation first | Several runs at once, behind `scheduler.parallel.enabled` (off by default, marked experimental) | Off by default, so single-flight stays the shipped behavior. The owner chose to bring it back. |
| §9.6: never decide by comparing one fence with another | Dispatch compares fences | A fence is an upper bound, not an estimate: the `scope_fence` gate refuses any diff outside it. Two tickets with disjoint fences cannot make conflicting text edits. The cost is running some tickets one after the other that could have run together, which is the trade the owner asked for. |
| §9.5: anything mechanical resolution leaves goes to full Rework | Step 2: a model resolves small conflicts. Step 3: discard the later branch and run the ticket again. Conflict handoff to Rework is removed. | A conflict means the code needs merging, not that the ticket is wrong. Rewriting the ticket was the wrong response. |
| §18.2: "conflict-only micro-rework" waits for "the first chronically re-resolved conflict shown by the journaled conflict facts"; `chupa/specs/rework.md:47` says "never conflict-only repair" | Step 2 is a conflict-only repair by a model | 13 `merge_conflict_facts` events exist in this repo's journal and nobody has read them. Ticket 7 starts by reading them (A0) and records whether any path is chronic; the owner's 2026-11-13 decision to run tickets in parallel is the incident, because parallel runs manufacture the conflicts §18.2 was waiting to observe. Ticket 8 removes the `rework.md:47` sentence with the conflict input it belongs to. |

`CHUPA_PLAN.md` stays frozen. The tickets update `docs/how-chupa-works.md` §7.2, §7.2.1, and the config table.

## Target design

### 1. Config (experimental)

```yaml
scheduler:
  max_unmerged: 2
  parallel:              # experimental; serve only
    enabled: false
    max_runs: 2          # tickets in Implement..Review at once
    shared_paths: []     # paths allowed to overlap; their conflicts go to the model step
```

- A new `Parallel` model nested under `Scheduler` in `chupa/config.py`, using the existing `_Strict` and `Count` types.
- Only `serve` reads it. `drain` and `run` stay single-flight with inline merge. Running several tickets requires the queue and its conflict steps, and only `serve` has them.
- When `enabled` is false, nothing changes: the ordering, the dispatch, and the tests are the same as today.
- `chupa doctor` warns when `max_runs` is greater than the `limits.concurrency` of the provider that serves the implement route. Without more provider slots, the runs wait on each other's model calls, so they gain nothing.

### 2. Overlap check at dispatch

New pure function, `chupa/tickets.py::fences_overlap(a, b, shared) -> bool`, beside `_in_fence`, which moves there from `chupa/stages.py:978` because the fence grammar is `tickets.py`'s (the roadmap's audit found `_in_fence` re-implemented at `watchdog.py:60` and `drain.py:484` with different semantics; the move gives it one home). The dispatch skip in `chupa/drain.py`, which owns the eligibility sort, calls it.

- Fence entries are compared using the path rule in host-authoring "Path matching": an entry overlaps another when it is equal to it, or when one is a directory that contains the other.
- Each stem's own outbox (`tickets/<stem>/`) is left out of the comparison. A fence entry of `tickets` or of `tickets/<other>` overlaps the whole ticket plane.
- Paths covered by `merge.strategies` are not fenced, so they never block dispatch. The mechanical step handles them.
- Overlap only on `shared_paths` is allowed. Its conflicts go to the model step.
- The in-flight set is every ticket from dispatch until it merges or is retired. That includes finished tickets waiting in the merge queue.
- **Must run alone:** a ticket with a `gate_bypass` of `scope_fence` (its fence no longer bounds its diff), and a ticket being run again after a conflict discard (section 5). Such a ticket starts only when nothing it overlaps is in flight, and it ignores `shared_paths`.

### 3. Ordering: fill free slots by longest chain

- `chain(t)` is the number of unsettled tickets reachable from `t` through incoming `depends` and `runs_before` edges, that is, how much work waits behind `t`. It is a pure function in `chupa/drain.py`. `chupa/graph.py` stays drawing-only.
- When parallel is on, the eligible list is ordered by `(P0 first, -chain, priority, age, stem)`. `runs_before` edges are still applied as soft edges, as `order_tickets` applies them now. P0 stays first because P0 is the instance-fix lane in the CORE routing rules. Below P0, longest chain wins over priority, so long dependency chains start early and keep the slots full.
- **Filling slots:** walk the ordered list and dispatch each candidate that does not overlap anything in flight, until `max_runs` slots are full.
- **Starvation guard:** a candidate skipped for overlap `SKIP_LIMIT` times (an engine constant, 3) becomes a barrier. Nothing new dispatches until it can start. Each skip goes to the engine log, not the journal.
- `write_queue` (`state_dir/queue.json`) writes the order as dispatched, so status and the extension show the real order.

### 4. Several runs at once in `serve`

Code that assumes one run, and must handle a set of runs:

- After `active-slot-single-owner` (roadmap row 15) has made `DaemonAdmission` the one owner of the running set, that set becomes `running: dict[str, Ticket]`. `dispatch_next` returns once a slot is filled and does not wait for the run to finish. Each run is its own task. `dispatch_next` (`chupa/scheduler.py:50-76`) and `_Drain._select` (`chupa/drain.py:508-558`) compute the same eligibility today; this ticket gives them one `eligible()` in `drain.py`, and one `running` transition writer in `runner.run_ticket` instead of three (roadmap §2.1 rows 7 and 9).
- `DaemonAdmission` (`chupa/daemon.py`) changes from one `_slot` lock to a set of tasks with `max_runs` slots. `waiting_for_merge` releases that run's slot only.
- `AdmissionBoundary.__call__` (`chupa/merge.py`) stops overwriting `self.queue.ctx`. `MergeQueue.offer` already keeps a context for each stem (`self.contexts`), and `process()` uses it.
- `serve.py` idle and restart checks (`scheduler.active is None`, `admission.active is None`) become "no runs in flight". Retro, stop, and self-upgrade already wait for idle, and that now means every slot is empty.
- **Host command lock:** one engine-wide `asyncio.Semaphore(1)` around `stages.run_host_command`, shared by Check, both merge tiers, and the graphics plan's render command (roadmap decision 10; `host-check-selection-single-owner` makes `run_host_command` the one runner first). The suite already runs with `-n auto` on every core. Two suites at once would compete for cores and expose shared-state flakes. Model calls still run in parallel, and those are most of a run's wall time.
- **Journal:** several runs append from one process. `journal.lock` already serializes every append (`docs/how-chupa-works.md` §10.1), and the journal query layer's per-process offset (`docs/journal-sql-refactor-plan.md`) reads their lines like any other writer's.
- Unchanged: each run already has its own worktree (`<worktree_root>/<stem>`), journal effect keys already include the stem, and the watchdog already tracks each model call separately.
- Self-upgrade on this repo: nearly every ticket changes `chupa/`, and a `chupa/` merge stops new admissions until every run finishes, then restarts. Parallel runs still save time here, because two runs overlap. The slots are just not refilled until the restart.

### 5. Merge queue: three conflict steps

The queue still admits one ticket at a time. The "second ticket" is the one being rebased onto a `main` that now contains the first. Steps, in order:

1. **Mechanical** (unchanged): git merge plus the declared `merge.strategies`.
2. **Model resolve (new).** Used only when the conflict is small. It is the conflict-only repair that `chupa/specs/rework.md:47` forbids today; that sentence goes with the conflict input in ticket 8. Every bound below is an engine constant, not a config option:
   - at most 3 conflicted files and 60 conflict-marker lines in total;
   - text files only; no modify/delete or rename conflicts;
   - no conflicted path in `engine_plane_safety_inventory`;
   - paths in `shared_paths` are always eligible, as long as the other bounds hold.

   A new prompt spec, `chupa/specs/resolve.md`, receives both tickets' Goal and Scope in, plus the base, ours, and theirs version of each conflicted hunk. It returns either the resolved file contents or `decline` with a reason. The engine checks that no conflict markers remain, stages the files, and continues the rebase. The candidate then goes through the full safety and integration tiers. **Re-review:** a model resolution is not a clean rebase, so the pinned approval does not carry over. One review call checks the resolution delta (a range-diff of the reviewed head against the candidate, limited to the conflicted files). `approve` lets the candidate continue. `snag` or `decline` goes to step 3.
3. **Discard and run again (new; replaces the Rework handoff).** Abort the rebase and retire the branch and worktree through `git.py` (`worktree remove` + `prune`). Journal a `merge_conflict_rerun` signal. Return the ticket to the scheduler as eligible for a fresh Implement from the current `main`, marked run-alone (section 2). A rerun does not use the ticket's `retry` cap, because the conflict is not the ticket's fault. `CONFLICT_RERUN_LIMIT` (an engine constant, 2) caps reruns. After the limit, the ticket parks with the paved road "split the ticket, or run it with parallel disabled".

`ConflictHandoff`, `daemon.consume_handoff`, and the `handoff` parameter of `rework()` are deleted, along with their tests (no dual path). `CONFLICT_FACTS.resolving_rung` becomes `none | mechanical | model | rerun`. The journal fold still accepts the historical `rework` value.

### 6. What a discarded run passes on

The rerun may keep only decisions and reference content. It never keeps code applied directly:

- The discarded attempt's `run.md` (the decisions it made) and its `review.md` approval findings.
- A reference copy of the discarded diff, limited to files that did not conflict, stored as a new lift kind `prior-diff` at `attempts/<n>/prior.diff`.

Implement's prompt embeds both under "Prior attempt (discarded on merge conflict); re-derive against current main; do not copy blindly". Review checks the whole new diff. Rejected alternative: cherry-picking the files that did not conflict onto the new branch. They may depend on the conflicted part, and nothing would check that.

### 7. Contention rules: small tests, small tickets

Two runs can share a slot only if their fences are disjoint, so hot shared files cancel out parallelism. The rules below keep new work out of them.

Generic rules, for every host (ticket content rules belong only in `chupa/docs/host-authoring.md`, which Author embeds):

- Put a ticket's new tests in a **new test file** named for the behavior it covers. Fence an existing test file only when the change flips its assertions or the file covers the edited unit and nothing else. Never add tests to a file just because it is the closest match.
- Put a new fixture, helper, rig, or data set in a **new module** next to its tests. Change a shared fixture, `conftest.py`, harness, or rig only when that fixture is the ticket's subject. Do that in its own ticket, and have the tickets that use it list it in `Depends on`.
- **A ticket fences only what its acceptance criteria force.** A fence that spans more than one subsystem is usually two tickets. When the second needs the first's merged code, link them with `Depends on`. Otherwise link them with `Runs before`.
- A documentation update edits only the section the change makes false. (Measured: 172 of 539 fences include `docs/how-chupa-works.md`. That file goes in `shared_paths`, and its conflicts go to the model step.)

Rules for this repo only (`CLAUDE.md` and `AGENTS.md`, outside the managed block):

- No new tests go into these files: `tests/integration/test_daemon_composition.py`, `tests/integration/test_drain.py`, `tests/integration/test_mergequeue.py`, `tests/integration/test_stages.py`, `tests/integration/serve_rig.py`. New tests go in `tests/unit/test_<module>_<behavior>.py` or `tests/integration/test_<behavior>.py`. (Measured: those five files took 53 commits in the 13 days to 2026-11-13; 37 test modules double as fixture libraries with 257 cross-test imports and no `conftest.py` exists. The roadmap's `test-fakes-and-conftest` gives new tests a shared place to import from, so the rule costs nothing to follow.)

### 8. Measurement

- `chupa status` gains a "hot paths" table, built in Python and drawn by the extension: unsettled tickets per fenced path, top 10. It is the same count as the one in Current state, and it shows which files to split next.
- `merge_conflict_facts` already records each conflict, and the new `model` and `rerun` steps are counted in it. A retro proposes adding a `merge.strategies` entry or a split for any path that conflicts often.

## Where each rule lives

| Rule | Home |
|---|---|
| New tests in new files, new fixtures in new modules, fence only what is forced, edit only the false doc section | `chupa/docs/host-authoring.md` (the one authoring source) |
| Do-not-grow list of this repo's large test files | `CLAUDE.md` and `AGENTS.md`, section B |
| Overlap check, chain order, run-alone, conflict steps | Engine code, documented in `docs/how-chupa-works.md` §7.2 and §7.2.1 |
| CORE_TEMPLATE | No change: 352 bytes of headroom left, and these rules are authoring rules, not conduct rules |

## Ticket breakdown

Each ticket follows its own rule and puts its tests in a new file. Priorities are proposals.

| # | Stem | Kind | P | Depends on | Content |
|---|---|---|---|---|---|
| 1 | `contention-authoring-rules` | chore | P1 | | Section 7 rules in `host-authoring.md`, `CLAUDE.md`, and `AGENTS.md`. Docs only. Useful even with parallel off. |
| 2 | (roadmap prerequisites) | | | | `active-slot-single-owner` (roadmap row 15) and `merge-admission-single-owner` (row 16), both 0.2.0 chores owned by the roadmap. The docstring fix that was here is in `docs-truth-sweep` (row 4). |
| 3 | `parallel-config` | feature | P2 | | The `scheduler.parallel` model, the doctor warning, and the config table in how-chupa-works. |
| 4 | `fence-overlap` | feature | P2 | | `fences_overlap` and the run-alone rule, pure, with new `tests/unit/test_fence_overlap.py`. |
| 5 | `chain-order` | feature | P2 | | `chain()`, the parallel order, slot filling, the starvation guard, pure, with new `tests/unit/test_chain_order.py`. |
| 6 | `serve-parallel-dispatch` | feature | P2 | 3, 4, 5, `active-slot-single-owner` | Section 4: run set, slots, one `eligible()` filter, one `running` writer, `AdmissionBoundary` context, idle checks, host command lock. how-chupa-works §7.2. |
| 7 | `merge-model-resolve` | feature | P2 | `merge-admission-single-owner` | A0 first: read the 13 `merge_conflict_facts` events and attach them as evidence. Then section 5 step 2: `specs/resolve.md`, the bounds, the re-review of the resolution delta, the `model` step value. Useful even when single-flight, because main can move under a serve run. |
| 8 | `conflict-discard-rerun` | feature | P2 | 7 | Section 5 step 3 and section 6: delete the handoff to Rework, retire and re-offer, `prior-diff` lift, Implement prompt section, rerun cap. how-chupa-works §7.2.1. |
| 9 | `status-hot-paths` | feature | P3 | | Section 8 hot paths table (snapshot field, pytest, extension draws it). |

`Runs before`: 1 before every feature ticket in every plan (the rules should be in effect before parallel runs start; roadmap row 13). `graphics-render-check` before 8 (both bump `chupa/specs/implement.md`; roadmap decision 8). Tickets 4, 5, and 7 do not overlap and could run together once parallel works, which makes them a good first trial.

Fence notes for authoring: ticket 6 touches `chupa/scheduler.py`, `chupa/daemon.py`, `chupa/merge.py`, `chupa/serve.py`, `chupa/drain.py` (the shared `eligible()`), `chupa/runner.py` (the one `running` writer), `chupa/stages.py` (the lock around `run_host_command`), and the tests that assert on the running set: at `80b76d5d`, 53 hits in 14 files for `scheduler.active` / `admission.active` / `.active is None` (`tests/integration/test_daemon_composition.py` 15, `test_scheduler.py` 6, `test_serve_admission.py` 5, `test_daemon_admission.py` 5, `test_serve_kill.py` 4, `test_mergequeue.py` 4, `tests/unit/test_commit_lock.py` 3, `test_rework.py` 3, `test_restart_timers.py` 3, one each in `test_serve_upgrade.py`, `test_merge.py`, `test_daemon_tasks.py`, `test_daemon_soak_runner.py`, `tests/harness/daemon_soak.py`) and 40 `_slot` hits in 21 files. `active-slot-single-owner` shrinks that list first; re-grep before authoring. Ticket 8 touches `chupa/mergequeue.py`, `chupa/daemon.py`, `chupa/rework.py`, `chupa/specs/rework.md` (drop the conflict input and line 47; bump its version to the next minor), `chupa/specs/implement.md` (next minor above whatever `graphics-render-check` left), `chupa/stages.py` (lift kind), `chupa/retro.py` (reads `CONFLICT_FACTS`), and every test that names `ConflictHandoff`, `consume_handoff`, or `handoff=`: 29 hits in 7 files at `80b76d5d` (`test_rework.py` 9, `test_daemon_composition.py` 9, `test_mergequeue.py` 3, `test_caps.py` 3, `test_daemon_tasks.py` 2, `tests/harness/daemon_soak.py` 2, `test_retro.py` 1).

## Risks

- **Over-serialization on this repo.** With about a third of fences on `how-chupa-works.md` and a sixth on `__main__.py`, strict disjointness rarely finds a pair. `shared_paths` covers the doc. `__main__.py` needs the section 7 rules and, eventually, a split of its verb handlers (not in this plan).
- **Two changes that each pass but break together.** The integration tier on the rebased candidate catches what the tests can see. The rest is the same accepted risk as approval carry-over today (§9.5).
- **A wrong model resolution.** It is bounded by size, re-reviewed, and run through both tiers. Any `model` step later found to be the cause of a red merge or a bug ticket goes into retro, the same as for strategy-resolved paths.
- **Shared state in host checks.** The host command lock removes it for checks. Implement agents in different worktrees can still collide on things outside the repo (ports, `~/.cache`). Those cases get filed when they are observed.

## Open decisions

Defaults if the owner says nothing are recorded in `docs/roadmap.md` section 6.

1. **Serve only, or drain too?** Recommend serve only. `drain` would need the queue and the conflict steps, which means a second admission path or moving `drain` onto the queue. `remove-merge-hold` already made `serve` usable for day-to-day work.
2. **Chain order below P0, or below P1 too?** Recommend below P0 only. The CORE routing sends orchestration-cause fixes as P0 and product-cause fixes as P1. Only P0 has to jump the queue.
3. **Rerun cap usage.** Recommend that conflict reruns do not use `retry`, and are capped by `CONFLICT_RERUN_LIMIT` instead.
4. **Splitting the existing large test files.** Section 7 stops them growing but does not shrink them. Splitting `test_daemon_composition.py` and the other files is a set of chore tickets to run while parallel is off. Not authored by this plan.
