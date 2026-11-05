---
state: confirmed
source: human
priority: P0
kind: feature
---

## Depends on
- none

## Context
- chupa/serve.py
- chupa/drain.py
- chupa/__main__.py
- chupa/journal.py
- chupa/seams.py
- tests/test_drain_upgrade.py
- tests/test_serve.py
- chupa/scheduler.py
- chupa/mergequeue.py

## On-demand
- tests/test_closed_sets.py
- tests/test_vocabularies.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Goal / Why
`serve` keeps running the engine code it started with. When chupa's own code changes, `drain` re-execs itself onto the new code (section 7.1 "Self-upgrade"), but `serve` has no equivalent. So chupa cannot self-host under `serve`: every merge of `chupa/` or `specs/` would leave the daemon on stale code. A host's `serve` likewise needs a manual restart after each chupa update. This keeps operators on `drain`, which they must start and stop by hand.

After this change `serve` notices when the engine's own source changes and hands off to a re-exec'd `serve` on the new code, with no operator step. Changes it notices include one serve itself merged (self-hosting) and an update to the chupa checkout a host runs from.

## Scope in / Scope out
- In: the engine checkout is the directory the running `chupa` package was imported from (the parent of the `chupa/` package directory).
  - At startup, `serve` records the git tree ids of `chupa` and `specs` at that checkout's `HEAD` through the git seam.
  - When the engine directory is not a git checkout, serve logs one `engine_log` event saying self-upgrade is off and does not watch.
- In: `serve` re-reads those two tree ids before each scheduler admission and after each merge-queue pass. When either differs from the startup value:
  - it stops admitting new dispatch;
  - once no ticket is running and the merge queue has no pending or active candidate, it hands off.
- In: the handoff follows drain's fixed order (`chupa/drain.py`):
  1. journal a `serve_handoff` signal carrying the new tree ids;
  2. run serve's normal cleanup;
  3. close the journal and release the lock;
  4. spawn the child through an injected `ProcessExec` (never the instance active work uses), with `timeout=None`;
  5. exit with the child's code.

  A kill accepted before the spawn wins: no child is spawned, as in drain.
- In: one function in `chupa/drain.py` builds the re-exec argv for both verbs: `[uv, run, --project, <engine checkout>, python, -m, chupa, *args]`.
  - `args` is the verb's own CLI argv, including `--config`.
  - Drain passes its `--parked` arguments through `args`, replacing `REEXEC`.
  - The child inherits the parent's environment and cwd.
- In: `chupa/__main__.py` passes the `serve` invocation's argv and a `SubprocessExec` re-exec seam into `serve.serve`.
- In: `chupa/journal.py` `SIGNAL_NAMES` and `tests/test_closed_sets.py`: add `serve_handoff`.
- In: docs.
  - `docs/how-chupa-works.md` section 7.2: a self-upgrade paragraph covering the trigger, the wait for idle and the handoff order.
  - Section 7.1: the shared re-exec argv.
  - `docs/host-contract.md` "Instance custody": a git-checkout engine's `serve` restarts itself when the engine's `chupa/` or `specs/` changes, while a tagged install still upgrades by install and restart.
- Out: drain's trigger and handoff order; installed (non-git) engines; any config knob to turn this off.

## Scope fence
- chupa/serve.py
- chupa/drain.py
- chupa/__main__.py
- chupa/journal.py
- tests/test_serve.py
- tests/test_drain_upgrade.py
- tests/test_drain.py
- tests/test_closed_sets.py
- tests/test_vocabularies.py
- tests/test_daemon_composition.py
- tests/test_restart_timers.py
- tests/test_provider_cooldown_failover.py
- tests/test_daemon_soak.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. Self-hosted serve with a fake re-exec seam: a merge touching `chupa/` journals `serve_handoff`, releases the lock before the spawn, and spawns once with argv `[uv, run, --project, <engine checkout>, python, -m, chupa, ..., serve]` (including `--config` when given). A merge touching only `docs/` spawns nothing. Checked by `uv run pytest tests/test_serve.py`.
2. When the engine checkout's `chupa` tree changes outside serve, a host serve whose engine checkout differs from the host repo hands off at its next admission check. Checked by `uv run pytest tests/test_serve.py`.
3. With a ticket running when the change is seen, serve admits nothing new and hands off only after that ticket's terminal and an empty merge queue. Checked by `uv run pytest tests/test_serve.py`.
4. A kill accepted while a handoff is pending spawns no child. Checked by `uv run pytest tests/test_serve.py`.
5. An engine directory that is not a git checkout logs that self-upgrade is off and never spawns. Checked by `uv run pytest tests/test_serve.py`.
6. Drain's handoff argv comes from the shared builder and keeps its `--parked` arguments. Checked by `uv run pytest tests/test_drain_upgrade.py`.
7. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_serve.py tests/test_drain_upgrade.py tests/test_closed_sets.py tests/test_vocabularies.py
uv run pytest -q
```

## Definition of rejected
A handoff that spawns while holding the lock or mid-ticket; a second re-exec argv builder; a config knob or flag; polling the engine tree from a background loop instead of at admission and merge boundaries; any change to drain's trigger.

## Time budget
- expected: 90m
- stuck: 180m
