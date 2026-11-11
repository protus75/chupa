---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- none

## Context
- chupa/reconcile.py
- chupa/runner.py::run_ticket
- chupa/runner.py::harvest_orphan
- chupa/runner.py::verdict
- chupa/runner.py::verdict_locked
- chupa/status.py::reject_queue
- chupa/status.py::Status
- chupa/status.py::project
- chupa/status.py::render
- docs/how-chupa-works.md#6.7 Other holds
- test-gate.toml
- tests/integration/test_reconcile.py::orphan_worktree
- tests/integration/test_cli.py::ENV
- tests/integration/test_cli.py::journal
- tests/integration/test_cli.py::test_status_projects_the_journal
- tests/integration/test_watch.py::test_snapshot_menu_availability
- tests/integration/test_drain.py::make_root
- tests/integration/test_drain.py::confirmed
- tests/integration/test_drain.py::commit_ticket
- tests/regress_drain_park_findings.py

## On-demand
- chupa/__main__.py
- chupa/observe.py

## Goal / Why
After `chupa kill` (or any engine death) stops a ticket mid-run, the journal keeps that stem
at `running` with no terminal. Every verb reads state through `status.last_states`, which
takes the journal's last transition as fact and never asks whether an engine is alive. Only
`run`, `drain` and `serve` reap such orphans (`reconcile`), and all three then start ticket
work. So with no engine running:

- `reject` refuses (`verdict_locked`: "is running -- wait for its terminal"), although
  `verdict` holds the writer lock and so knows no engine is running;
- `order` refuses ("is running; editing a ticket during its run stops it");
- `status` lists the stem under "in flight";
- the extension offers no Reject for it (`observe` turns `chupaReject` on only for drafts and
  held items);
- the only way to reject it is to start `run` on some other stem, and starting `drain` or
  `serve` reruns the very ticket the operator wants dropped.

`evidence/stale-running.txt` shows this on a fungo ticket killed 3 minutes into Implement.

When this ticket is done, every verb decides "running" from the journal AND engine liveness:
a stem the journal holds at `running` while no live process holds the writer lock is an
interrupted run, and each verb treats it as one. An interrupted run can be rejected, or rerun
by starting the engine; `confirm` has nothing to confirm (a reaped stem is `abandoned` and
eligible, not held), so it keeps its current refusal.

## Scope in / Scope out
- In: `chupa/runner.py`: a new `async def reap(checkout: Checkout) -> list[str]` that runs
  `reconcile(...)` with `harvest_orphan` exactly as `run_ticket` does today; `run_ticket`
  calls it in place of its inline call; `verdict` calls it right after `lock.acquire()` and
  before `verdict_locked`.
- In: `chupa/__main__.py`: the verbs that take the writer lock to read or settle ticket state
  call `await runner.reap(...)` right after `lock.acquire()`: `_review` and the `dismiss` and
  `triage` closures in `main`, and `_retro`. `_control` (pause, resume, kill, stop) is
  unchanged. `_order` takes no lock (it works beside a running serve); it refuses a `running`
  stem only when `observe.lock_holder(checkout.config.state_dir)` is not None, and otherwise
  proceeds as for any open stem.
- In: `chupa/status.py`: `Status` gains `interrupted: tuple[str, ...] = ()`; `project` gains a
  keyword `alive: bool = True`; with `alive` false, stems last at `running` go to
  `interrupted` instead of `in_flight`. `render` prints an `interrupted:` block of those stems
  followed by the line "the engine stopped mid-run; reject it, or start the engine to rerun
  it", and does not list them under `in flight:`. The `status` verb in `__main__.py` passes
  `alive=observe.lock_holder(state_dir) is not None`. `reject_queue` is unchanged.
- In: `chupa/observe.py`: with no live engine, a row whose stem is last at `running` has
  `chupaReject` "on" (the extension reads this flag; no TypeScript change). `chupaConfirm` is
  unchanged.
- In: `tests/integration/test_cli.py::test_status_projects_the_journal`: its stem `b` (journaled
  `running`, no lock held) is now expected under `interrupted:` instead of `in flight:`; no
  other assertion in the file changes.
- In: `docs/how-chupa-works.md`, the *Reconcile* bullet in section 6.7: replace "at the start of
  `run`, `drain`, and `serve`" with "whenever a verb other than pause, resume, kill or stop
  takes the writer lock", and replace "A `running` stem cannot be confirmed or rejected until it
  is reaped." with "With no engine running, `status` shows such a stem as interrupted, `reject`
  reaps and rejects it, and `order` treats it as open."
- In: the carried reproducer `tests/regress_stale_running.py`, modeled on
  `tests/regress_drain_park_findings.py`: build a root with `make_root` and `commit_ticket`,
  append a `running` transition for the stem with no terminal, run
  `main(["reject", "--yes", stem])` with stdout redirected, and print `defect` with exit 1 when
  it refuses, `pass` with exit 0 when the stem's last state is `rejected`, `error` with exit 2
  when its own setup raises.
- In: the `test-gate.toml` unit coverage floors for `chupa/__main__.py`, `chupa/runner.py` and
  `chupa/status.py` still pass. `runner.reap`, `status.project` and `status.render` get unit
  tests (criteria 6-8); the two new lines in `__main__._order` and the reap calls in `__main__`
  read disk and are covered by the integration criteria 3 and 5, and `chupa/__main__.py` stays
  at or above its 13% floor.
- Out: `drain` and `serve` (they already reconcile on start); `_control`, so `kill` and `stop`
  still leave the run for reconcile; `confirm`'s refusal; `reject_queue`; `vscode-chupa/`
  TypeScript; the logic of `reconcile.orphans` and `reconcile.reconcile`; `test-gate.toml`.

## Scope fence
- chupa/runner.py
- chupa/__main__.py
- chupa/status.py
- chupa/observe.py
- docs/how-chupa-works.md
- tests/integration/test_stale_running.py
- tests/integration/test_cli.py
- tests/unit/test_stale_running.py
- tests/regress_stale_running.py

## Acceptance criteria
1. `tests/integration/test_stale_running.py::test_reject_reaps_a_killed_run` builds a root
   with a committed confirmed ticket and a journal whose last transition for it is `running`
   (no process holding the lock), runs `main(["reject", "--yes", stem])`, and asserts exit 0,
   the stem's last two transitions are `abandoned` then `rejected`, and the ticket's
   frontmatter is `state: rejected`, not a refusal naming "is running".
2. `tests/integration/test_stale_running.py::test_reject_refuses_a_live_run` asserts that while
   a test-held `Lockfile` holds the lock, `reject` refuses with the lock-held message and the
   stem's last transition is still `running` (no reap beside a live engine).
3. `tests/integration/test_stale_running.py::test_order_beside_dead_run` asserts
   `main(["order", stem, "--priority", "P0"])` exits 0 and rewrites the priority when no
   process holds the lock, and still refuses with "is running" when `observe.lock_holder` is
   monkeypatched to report a live holder, so a live run stays protected.
4. `tests/integration/test_stale_running.py::test_status_shows_interrupted` asserts
   `main(["status"])` prints the stem under `interrupted:` and not under `in flight:` when no
   process holds the lock, and under `in flight:` when `observe.lock_holder` is monkeypatched
   to report a live holder; and `tests/integration/test_cli.py::test_status_projects_the_journal`
   passes with `b` under `interrupted:`.
5. `tests/integration/test_stale_running.py::test_every_locked_verb_reaps` asserts, with
   `runner.reap` monkeypatched to a recorder, that `review`, `dismiss`, `triage`, `retro` and
   `reject` each call it exactly once after taking the lock, and that an idle `kill`, `stop`,
   `pause` and `resume` call it zero times; a verb that skips the reap, or a control verb
   that reaps, fails the test.
6. `tests/integration/test_stale_running.py::test_menu_offers_reject_for_dead_run`, built as
   `tests/integration/test_watch.py::test_snapshot_menu_availability` is (monkeypatching
   `journal`, `load_tickets`, `lock_holder`, `running_stems`, `uncommitted_tickets`,
   `committed_ticket_shas` and `commits` in `observe`), asserts the row menu for a stem last at
   `running` has `chupaReject` "on" with no live engine and "off" with one, and `chupaConfirm`
   "off" both times.
7. `tests/unit/test_stale_running.py::test_reap_reconciles_with_harvest` (a fake journal and
   Git) asserts `runner.reap` returns the reaped stems and calls harvest only for a stem whose
   worktree path exists.
8. `tests/unit/test_stale_running.py::test_project_interrupted` asserts
   `status.project(events, alive=False)` puts a `running` stem in `interrupted` and not in
   `in_flight`, and `alive=True` the reverse; and
   `tests/unit/test_stale_running.py::test_render_interrupted_block` asserts `status.render` of
   a `Status` with `interrupted=("x",)` prints an `interrupted:` block with `- x` and the hint
   line, and `x` not under `in flight:`.
9. `python tests/regress_stale_running.py` prints `{"regression_result": "pass"}` and exits
   0 on the branch; at base it prints `{"regression_result": "defect"}` and exits 1.

## Verification
```
./dev.py test tests/integration/test_stale_running.py tests/unit/test_stale_running.py tests/integration/test_cli.py tests/integration/test_watch.py tests/integration/test_reconcile.py
```

## Definition of rejected
- any verb other than `run`, `drain` or `serve` starts a ticket stage
- a reap while another live process holds the writer lock, or `order` changing a stem whose
  run is live
- a second orphan-detection rule beside `reconcile.orphans`
- a change to `_control`, `reject_queue`, `reconcile.orphans`, `reconcile.reconcile`, `kill`,
  `drain` or `serve` behavior
- any edit under `vscode-chupa/` or to `test-gate.toml`

## Time budget
- expected: 75m
- stuck: 150m

## Regression
```
python tests/regress_stale_running.py
```
- carries: tests/regress_stale_running.py
