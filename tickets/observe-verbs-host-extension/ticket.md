---
state: confirmed
source: human
priority: P3
kind: feature
---

## Depends on
- ask-prompt-verb
- order-verb
- verdict-yes-flag
- engine-lifecycle-log

## Context
- watch.py
- vscode-chupa/snapshot.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- vscode-chupa/media/view.js
- chupa/__main__.py
- chupa/seams.py
- chupa/git.py
- dev.py
- tests/test_watch.py
- docs/how-chupa-works.md
- docs/host-contract.md
- docs/host-running.md
- tests/test_host_running.py

## Goal / Why
The `vscode-chupa` extension and `watch` work only in the chupa checkout:
- `watch.py` and `vscode-chupa/snapshot.py` sit in this repo and read `config.yaml` from it;
- the extension activates only in a workspace that contains them;
- its menu runs `./dev.py ...`.

A host repo (for example fungo, which runs chupa as `scripts/chupa`, i.e. `python -m chupa --config <host>/config.yaml`) gets neither. It already carries a hand-adapted copy of `watch.py` (2026-11-06).

After this change:
- `chupa watch [--once]` and `chupa snapshot` are engine verbs that read the `--config` host's state;
- the extension runs every action through a configurable chupa command;
- it works in any repo with a `tickets/` directory.

## Scope in / Scope out
- In: new `chupa/observe.py`. It holds the read-only logic now split across `watch.py` and `vscode-chupa/snapshot.py`, as they stand once the dependencies merge:
  - journal and engine-log reading;
  - lock-holder liveness and `running_stems`;
  - held stems;
  - the current step;
  - the queue;
  - the ordered ticket rows with run-order simulation, `settled_dependencies`, draft, committed, runnable, and held flags;
  - recent steps;
  - the text renderer.

  The state dir comes from the loaded config. Process listing and git go through chupa's seams (`SubprocessExec`, `Git`), with no raw `subprocess` in `chupa/observe.py`.
- In: `chupa/__main__.py`. These verbs take no lock and write nothing:
  - `chupa watch [--once]` prints the text view (refreshing every 3 seconds without `--once`);
  - `chupa snapshot` prints the extension's JSON, plus a `stateDir` field (absolute path).
- In: delete `watch.py` and `vscode-chupa/snapshot.py`.
- In: `dev.py`: `watch` runs `chupa watch` through `uv`.
- In: `tests/test_watch.py` imports from `chupa.observe`. Every existing test keeps its assertion, plus `test_snapshot_verb_reads_config_state_dir`, which uses a `--config` whose `state_dir` is not `.chupa/state`, and `test_observe_verbs_take_no_lock_and_write_nothing`:
  - the test process holds a `Lockfile` on the config's `state_dir`;
  - `main(['--config', <path>, 'snapshot'])` and `main(['--config', <path>, 'watch', '--once'])` both exit 0;
  - the state dir's file listing and every file's bytes are unchanged afterwards.
- In: `vscode-chupa`.
  - New setting `chupa.command`: an array of strings, `resource` scope, default `["uv", "run", "python", "-m", "chupa"]`. A host sets, for example, `["scripts/chupa"]`.
  - Activation is `workspaceContains:tickets/*/ticket.md`. The root is the first workspace folder with a `tickets/` dir.
  - Snapshot, prompt, `order`, and every engine action (review, lint, run, confirm/reject with `--yes`, drain, stop, kill, status) run as `<chupa.command> <verb> <args>`:
    - interactive ones through a VS Code `Task` with a `ProcessExecution` argv;
    - data ones through `execFile`;
    - never `./dev.py`, never a shell string.
  - File watchers use the snapshot's `stateDir` instead of `.chupa/state`.
- In: docs.
  - `docs/how-chupa-works.md` section 2.1: `watch` and `snapshot` rows.
  - Section 2.2: the `watch` row.
  - `docs/host-contract.md`: the extension and `chupa.command`.
  - `docs/host-running.md` verb table: `watch` and `snapshot` rows (both work while serve runs: Yes), which `tests/test_host_running.py::test_verb_table_matches_parser` requires.
- Out: engine behavior, the extension's views, colors and menu conditions, and host repos' own files (fungo's `scripts/watch` is the host's to drop).

## Scope fence
- chupa/observe.py
- chupa/__main__.py
- watch.py
- vscode-chupa/snapshot.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- vscode-chupa/media/view.js
- dev.py
- tests/test_watch.py
- docs/how-chupa-works.md
- docs/host-contract.md
- docs/host-running.md

## Acceptance criteria
1. `./dev.py test tests/test_watch.py` exits 0, including `test_snapshot_verb_reads_config_state_dir`.
2. `test_observe_verbs_take_no_lock_and_write_nothing` passes: with the lock held elsewhere, both verbs exit 0 instead of refusing on the held lock, and the state dir is byte-identical, not changed by a written `queue.json` or journal segment.
3. `watch.py` and `vscode-chupa/snapshot.py` no longer exist. `grep -rn "dev.py\|\.chupa/state" vscode-chupa/` prints nothing.
4. `node --check vscode-chupa/extension.js` exits 0.
5. `docs/how-chupa-works.md` sections 2.1 and 2.2, and `docs/host-contract.md`, describe `watch`, `snapshot`, and `chupa.command`; `docs/host-running.md`'s verb table has `watch` and `snapshot` rows.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/test_watch.py
node --check vscode-chupa/extension.js
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `watch` or `snapshot` takes the lock or writes state;
- `chupa/observe.py` calls `subprocess` directly;
- the extension runs `./dev.py` or a shell string;
- a host with a non-default `state_dir` gets a wrong snapshot;
- any engine behavior changes.

## Time budget
- expected: 90m
- stuck: 180m
