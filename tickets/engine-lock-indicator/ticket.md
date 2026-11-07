---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/observe.py
- vscode-chupa/media/view.js
- tests/test_watch.py

## Goal / Why
Confirm and Reject in the tickets view are greyed out whenever any chupa process holds the engine lock, including a short `review`. The header only says `engine running`, so on 2026-11-06 the operator could not tell why Confirm was disabled: a `./dev.py review` held the lock, not a drain.

After this change the tickets view header starts with a padlock icon: closed when a live process holds the lock, open when none does. Hovering the padlock shows the holder's verb, start time and pid (for example `review since 2:19 AM (pid 60216)`), or `unlocked`. The header text stays short; the holder appears only on hover.

## Scope in / Scope out
- In: `chupa/observe.py`: `snapshot()` adds a string field `lock`. It is empty when `lock_holder(state)` is None. Otherwise it is `<verb> since <time> (pid <pid>)`:
  - pid and start time come from `.chupa/state/chupa.lock`, the same file `lock_holder` reads; the time is `clock(started_at)`, the existing observe.py display helper (for example `2:19 AM`);
  - verb is the first non-option token after `-m chupa` in the holder's command line, skipping `--config` and its value; it reads the command line through the existing `processes(ctx)` rows. When the pid has no row or no such token exists, the verb is `chupa`. No verb list is consulted.
  - The existing `engine` field is unchanged; the context-menu enablement keeps reading it.
- In: `vscode-chupa/media/view.js`: the header's `engine running` / `engine stopped` prefix becomes a single padlock glyph, `🔒` when `snap.lock` is non-empty, else `🔓`. The glyph's hover tooltip (`title`) is `snap.lock`, or `unlocked` when it is empty. The counts after it are unchanged. JavaScript does no parsing or time math on `lock`.
- In: `tests/test_watch.py`: tests for the `lock` field: empty with no lockfile; empty when the lockfile pid is dead; `review since <time> (pid N)` for a live holder whose command line is `python -m chupa --config x.yaml review stem`, with the expected time built from the fixture's `started_at` via `clock()` so the test passes in any timezone; verb `chupa` when the command line has no token after `-m chupa`. Fake the process rows and the liveness check; do not spawn processes.
- Out: the `engine` field and every menu `when` / `enablement` clause; the `watch` text view; the status bar; writing the verb into the lockfile; `chupa/daemon.py` and the lock acquire code.

## Scope fence
- chupa/observe.py
- vscode-chupa/media/view.js
- tests/test_watch.py

## Acceptance criteria
1. `./dev.py test tests/test_watch.py` exits 0, including the four `lock` field cases in Scope in.
2. `grep -n "engine running\|engine stopped" vscode-chupa/media/view.js` prints nothing.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_watch.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- JavaScript parses, formats, or derives the lock text instead of drawing `snap.lock`;
- the `engine` field or any menu enablement changes;
- the snapshot spawns a process other than the existing `ps` calls.

## Time budget
- expected: 30m
- stuck: 90m
