---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/hostfiles.py::classify_core
- chupa/hostfiles.py::committed_core
- chupa/hostfiles.py::CoreDriftGate
- chupa/providers.py::routed_conduct_paths
- chupa/doctor.py
- chupa/runner.py::Refusal
- tests/integration/test_doctor.py
- tests/integration/test_stages.py::adopt_conduct
- tests/integration/test_drain.py::make_root
- docs/how-chupa-works.md#12. Host projects

## On-demand
- chupa/__main__.py
- tests/integration/test_hostfiles.py

## Goal / Why
When a chupa upgrade changes `CORE_TEMPLATE`, a host's committed `CLAUDE.md`/`AGENTS.md` block is stale. Nothing says so until a ticket has run Implement and failed Check on `core_drift`. The ticket's fence never holds the conduct files, so retries cannot repair it, and every ticket in the host fails the same way and spends its caps. The only "run `chupa core`" message is that gate finding's paved road (2026-11-08, found while porting chat rules into the block).

After this change, `serve`, `drain` and `run` refuse to start, before taking the lock or admitting any ticket, when a routed conduct file committed at `HEAD` is not `current`. The refusal names each file and its state and says to run `chupa core`, then commit. `doctor` reports the same check as a row.

## Scope in / Scope out
- In: `chupa/hostfiles.py`. Add `async def stale_core(repo, config, git) -> list[str]`.
  - For each path from `routed_conduct_paths(config, repo)`, it reads the bytes committed at `HEAD` through `git` (a file absent at `HEAD` reads as `None`). It classifies them with `classify_core` against the installed `CORE_TEMPLATE`.
  - It returns one message per file whose state is not `current`: `<rel>: chupa core is <state>; <paved_road>`, using `classify_core`'s paved road. Order follows `routed_conduct_paths`.
  - An empty list means every routed file is current. `classify_core` and `CoreDriftGate` are unchanged.
- In: `chupa/__main__.py`. Before `serve`, `drain` and `run` start (before the lock and before any dispatch), call `stale_core`. When it returns messages, raise `runner.Refusal` with the joined messages and the paved road `run chupa core, then commit the conduct files and retry <verb>`, so the verb exits `runner.EXIT_REFUSED` (2) through the existing refusal handler. A serve restart re-execs `main`, so it is covered too.
- In: `chupa/doctor.py` `check`. When config loads, add one row named `core`. It passes with `routed conduct files are current` when `stale_core` returns nothing, and fails with the joined messages otherwise. When config fails, the `core` row fails with `state directory unavailable; repair the selected config and rerun doctor`, like `lock` and `journal`.
- In: tests.
  - `tests/integration/test_hostfiles.py`: `stale_core` returns `[]` for an adopted repo. It returns one `drifted` message naming `CLAUDE.md` when the committed block's bytes differ from the template, and one `missing` message when the committed file has no block. A block fixed only in the working tree, uncommitted, still reports.
  - `tests/integration/test_cli.py::test_doctor_cli`: the expected rows gain `PASS core` after `journal`.
  - `tests/integration/test_doctor.py`: the `core` row passes on an adopted repo and fails, naming `chupa core`, on a committed drifted block.
  - `tests/integration/test_drain.py`: with a committed drifted `CLAUDE.md` and a ready ticket, `drain` exits 2 and prints a message containing `chupa core`. The ticket is not dispatched (the fake pipeline records no call), and no lock holder is left.
- In: `docs/how-chupa-works.md` section 12: add a bullet saying `serve`, `drain` and `run` refuse to start on a committed stale block, and that `doctor` reports a `core` row. Also update the `doctor` row in the 2.1 Verbs table to list the core check.
- Out: running `chupa core` automatically, any change to the `core_drift` gate or `classify_core`, and other verbs (`review`, `status`, `lint`, `triage`).

## Scope fence
- chupa/hostfiles.py
- chupa/__main__.py
- chupa/doctor.py
- tests/integration/test_hostfiles.py
- tests/integration/test_doctor.py
- tests/integration/test_drain.py
- tests/integration/test_cli.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_hostfiles.py` passes, including `stale_core` returning `[]` for an adopted repo and one message (not zero) for a committed `drifted` and a committed `missing` block, with the working-tree-only fix still reported.
2. `./dev.py test tests/integration/test_doctor.py` passes, including a failing `core` row whose detail contains `chupa core` on a committed drifted block, not a passing one.
3. `./dev.py test tests/integration/test_drain.py` passes, including `drain` exiting 2 on a committed drifted block, with zero tickets dispatched, not one.
4. `./dev.py test` passes: every existing test repo is adopted, so no other verb test starts refusing.
5. `docs/how-chupa-works.md` section 12 and the `doctor` row name the startup refusal and the `core` row.

## Verification
```
./dev.py test
./dev.py lint
```

## Definition of rejected
An engine verb dispatches a ticket while a committed routed conduct file is stale, `chupa core` runs automatically, or the `core_drift` gate's behavior changes.

## Time budget
- expected: 30m
- stuck: 75m
