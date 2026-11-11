---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/__main__.py::_parser
- chupa/__main__.py::main
- chupa/seams.py::SubprocessExec
- chupa/observe.py::snapshot
- dev.py
- vscode-chupa/extension.js
- tests/integration/test_dev.py
- tests/regress_drain_park_findings.py
- docs/how-chupa-works.md#2.2
- tickets/drain-survives-editor-reload/ticket.md

## Goal / Why
A drain started from the VS Code extension dies when the editor exits or the window reloads. The play button (`chupa.playDrain`) and the Engine… picker run `chupa drain` in the foreground as a VS Code task, so the drain is a child of the task terminal and dies with it. Closing that terminal sends SIGHUP, and the drain has no handler for it, so it ends without `engine_stop` and leaves the ticket `running` for the next start to reconcile. See `evidence/foreground-launch.txt`.

This is the second time the problem has appeared. `drain-survives-editor-reload` fixed it on 2026-11-06 by detaching inside `dev.py`, the wrapper used only in this repo. The detach never reached the engine verb, so every other launcher still starts a foreground drain: the extension, and host operators who run `chupa drain`. The root cause is that process-lifetime policy lives in a launcher instead of in the verb.

When this ticket is done, `chupa drain --detach` starts the drain in its own session, appends its output to `<state_dir>/drain.out`, prints the child pid and output path, and exits 0 without waiting. `dev.py drain`, the extension's play button, and the Engine… picker all launch the drain through that flag. None of them contains its own detach logic.

## Scope in / Scope out
- In: `chupa/seams.py`: add a module-level `spawn_detached(argv, *, cwd, env, output) -> int`. It creates `output.parent` (`parents=True, exist_ok=True`), opens `output` in append mode, and starts `argv` with `subprocess.Popen` using `start_new_session=True`, stdin `subprocess.DEVNULL`, and stdout and stderr both set to the output file. It returns the child pid without waiting. This is the only raw process launch the ticket adds.
- In: `chupa/__main__.py`: the `drain` subparser gains `--detach` (`store_true`, with help text saying the drain runs in its own session and appends to `<state_dir>/drain.out`). `main` gains a keyword-only `spawn` parameter that defaults to `seams.spawn_detached`; tests inject a fake through it, the same way they inject `reexec`. When `args.detach` is set, `main` loads the config and then, before it takes the lock or builds a pipeline, calls `spawn([sys.executable, "-m", "chupa", *(["--config", str(args.config)] if args.config else []), "drain"], cwd=repo, env=env, output=config.state_dir / "drain.out")`. It then prints `drain: pid <pid>, output <path>` and returns 0. The child's argv never contains `--detach`, so the child runs the normal foreground drain. Use `sys.executable`, not `drain.reexec_argv`: `reexec_argv` targets this repo's `uv` project, which is wrong for a pip-installed host engine.
- In: `dev.py`: the `drain` branch becomes `chupa("drain", "--detach")`. Delete its `config.yaml` parsing, `mkdir`, `drain.out` open, and `subprocess.Popen`. Keep any import that other branches still use.
- In: `chupa/observe.py` `snapshot`: each `engineVerbs` entry replaces its `"verb"` string with an `"argv"` list. The Drain entry's argv is `["drain", "--detach"]`; every other entry's argv is `[<its verb>]`. Add a top-level `"drainCommand": ["drain", "--detach"]`.
- In: `vscode-chupa/extension.js`: the Engine… picker runs `devCommand(...choice.argv)`, and `chupa.playDrain` runs `devCommand(...snapshot.snap.drainCommand)`. The JavaScript adds no flag of its own.
- In: `tests/integration/test_dev.py`: replace `test_drain_detaches_and_appends_to_configured_state` with a test that fakes `dev.subprocess.run`, runs `dev.main()` with argv `["dev.py", "drain"]`, and asserts that the only command run is `["uv", "run", "python", "-m", "chupa", "drain", "--detach"]` and that `dev.subprocess.Popen` is never called.
- In: new `tests/integration/test_drain_detach.py`:
  - `test_detach_spawns_a_foreground_drain_and_returns`: builds a root with `tests.integration.test_drain.make_root` and calls `main(["drain", "--detach"], cwd=root, env=ENV, spawn=fake)` with a fake that records its call and returns 4242. It asserts: exit 0; the fake was called once with argv `[sys.executable, "-m", "chupa", "drain"]` (no `--detach`, so the child does not detach again), `cwd=root`, and `output=<root's configured state_dir>/drain.out`; stdout is `drain: pid 4242, output <that path>`; and `engine.log` contains no `engine_start` event (the launcher must not run the drain itself).
  - `test_detach_forwards_config`: the same call with `["--config", <path>, "drain", "--detach"]` passes `["--config", <path>]` before `"drain"` in the spawned argv.
  - `test_spawn_detached_runs_in_its_own_session_and_appends`: writes `before\n` to a tmp output file, then calls the real `seams.spawn_detached([sys.executable, "-c", "import os; print(os.getsid(0) == os.getpid())"], cwd=tmp, env=os.environ, output=that file)`. It reaps the child with `os.waitpid(pid, 0)` and asserts the file reads `before\nTrue\n`. A child that shares the caller's session prints `False`, and truncating the file loses `before`.
- In: `tests/integration/test_watch.py`: update the `engineVerbs[0]` assertion to the `argv` shape (`["drain", "--detach"]`) and assert `snap["drainCommand"] == ["drain", "--detach"]`.
- In: new `tests/regress_drain_detach.py`: the carried reproducer (see `## Regression`). It prints `defect` and exits 1 when `_parser().parse_args(["drain", "--detach"])` raises `SystemExit`, or when `main(["drain", "--detach"], ..., spawn=fake)` returns non-zero or does not call the fake. It prints `pass` and exits 0 when the fake is called once and the exit code is 0. It prints `error` and exits 2 when its own setup fails (an import or `make_root` raises), following `tests/regress_drain_park_findings.py`.
- In: `docs/how-chupa-works.md`: in the section 2.1 verb table, the `drain` row names `--detach` and `drain.out`. In section 2.2, the `drain` row becomes "`chupa drain --detach`". In the paragraph on the Tickets view, say that the play button and the Engine… picker start drain detached.
- In: `chupa/docs/host-running.md`: in the verb table, the `drain` row says `--detach` runs the drain in its own session, so it survives the terminal or editor closing, and appends output to `<state_dir>/drain.out`.
- In: `CLAUDE.md` and `AGENTS.md`: in section A, directly after the "Guides name verbs, not command lines." bullet, add the same new bullet to both files: "**Launchers carry no process policy.** `dev.py` and the extension pick a chupa verb and its flags; how the engine process lives (session, detach, output file, signals) belongs to the verb. Why: `drain-survives-editor-reload` put the detach in `dev.py` alone, so the extension's play button still died on a window reload (2026-11-10)." This is the rule that stops the problem from coming back.
- Out: `serve` and its play button (`chupa.playServe`), signal handling inside the drain (a separate ticket, `drain-sighup-graceful-stop`), the self-upgrade handoff and `reexec_argv`, `vscode-chupa/package.json`, `README.md`, and every test that calls `main(["drain"])` without `--detach`. A foreground drain without the flag behaves exactly as before.

## Scope fence
- chupa/seams.py
- chupa/__main__.py
- chupa/observe.py
- dev.py
- vscode-chupa/extension.js
- tests/integration/test_dev.py
- tests/integration/test_drain_detach.py
- tests/integration/test_watch.py
- tests/regress_drain_detach.py
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- CLAUDE.md
- AGENTS.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_drain_detach.py` exits 0. It shows that `chupa drain --detach` spawns `[sys.executable, "-m", "chupa", "drain"]` without `--detach`, writes to `<state_dir>/drain.out`, returns 0, and logs no `engine_start`; a launcher that runs the drain in-process or re-passes `--detach` fails it. It also shows that `spawn_detached` starts the child in a new session and appends rather than truncates.
2. `./dev.py test tests/integration/test_dev.py` exits 0, and its drain test fails if `dev.py` calls `subprocess.Popen` itself.
3. `./dev.py test tests/integration/test_watch.py` exits 0, with the snapshot's Drain `argv` and `drainCommand` both equal to `["drain", "--detach"]`.
4. `vscode-chupa/extension.js` contains no `devCommand('drain')` literal and no `choice.verb`; both drain launches spread an argv taken from the snapshot.
5. `CLAUDE.md` and `AGENTS.md` both contain the "Launchers carry no process policy." bullet with identical text.
6. `uv run python tests/regress_drain_detach.py` prints `{"regression_result": "pass"}` and exits 0.
7. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_drain_detach.py tests/integration/test_dev.py tests/integration/test_watch.py
uv run python tests/regress_drain_detach.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of these is true: `chupa drain` without `--detach` stops running in the foreground; the detached child's argv contains `--detach`; `dev.py` or `extension.js` still starts a process with its own session or output-file logic; the JavaScript adds `--detach` itself instead of reading it from the snapshot; `spawn_detached` waits on the child; or `serve`, the handoff, or `reexec_argv` changes.

## Time budget
- expected: 45m
- stuck: 90m

## Regression
```
uv run python tests/regress_drain_detach.py
```
- carries: tests/regress_drain_detach.py
