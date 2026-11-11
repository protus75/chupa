---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- none

## Context
- chupa/__main__.py::_serve_signals
- chupa/__main__.py::main
- chupa/drain.py::drain
- chupa/drain.py::_Drain._stopping
- chupa/drain.py::_Drain._await_controlled
- chupa/control.py::ControlRequest
- chupa/control.py::publish_request
- chupa/control.py::ControlInbox
- tests/integration/test_serve_kill.py
- docs/how-chupa-works.md#7.1

## Goal / Why
A drain that receives SIGHUP or SIGTERM dies at once, without any trace. Only `serve` installs signal handlers (`_serve_signals`, which covers SIGINT and SIGTERM); `drain` installs none, and no verb handles SIGHUP. Closing the terminal that runs a foreground drain sends it SIGHUP, so the process ends mid-ticket. It writes no `engine_stop`, journals no kill, and leaves the ticket `running` until the next start reconciles it. Agent and check children run in their own session (`SubprocessExec` uses `start_new_session=True`), so the signal never reaches them. They can keep running in the worktree after the drain is gone. `evidence/unhandled-signals.txt` shows that only serve has handlers, and shows a real drain (pid 3899774) that ended after a merge with no `engine_stop`.

When this ticket is done, SIGHUP, SIGTERM, and SIGINT stop a drain exactly as `chupa kill` does. The drain aborts the running ticket's process group, journals the kill, logs `engine_stop` with outcome `killed`, prints the not-quiescent report, and releases the lock. Serve also handles SIGHUP the same way it already handles SIGINT and SIGTERM.

## Scope in / Scope out
- In: `chupa/__main__.py`: rename `_serve_signals` to `_engine_signals` and update every call site. It registers SIGINT, SIGTERM, and SIGHUP, and its restore function removes all three. `main` passes it to `drain.drain` as `signals=_engine_signals` and keeps passing it to serve.
- In: `chupa/drain.py` `drain()`: add a keyword `signals: Callable[[Callable[[], None]], Callable[[], None]] | None = None`. Right after `run = _Drain(...)` is built, it calls `signals(run._signal_kill)` when `signals` is given, and calls the returned restore in the `finally` that releases the lock. Add the method `_Drain._signal_kill(self)`, which publishes a kill to the drain's own control inbox using the same request `chupa kill` publishes: `control.publish_request(self.c.config.state_dir, ControlRequest(uuid4().hex, self.c.control.inbox.lifecycle_id, "kill", None), self.c.fs)`. The existing kill path (`_stopping`, `_await_controlled`, `consumer.apply_kill`) then aborts and reports. Add no second abort path, flag, or exit route. Callers that pass no `signals`, such as tests that call `drain.drain` directly, behave as before.
- In: new `tests/integration/test_drain_signals.py`:
  - `test_signal_kills_a_running_drain_like_kill`: drives `main(["drain"], ...)` with a scripted pipeline whose running ticket blocks. It monkeypatches `cli._engine_signals` with a fake that records the callback and returns a restore spy, and invokes the callback while the ticket runs. Model the root, pipeline, and blocking step on the drain kill tests in `tests/integration/test_kill_cli_activation.py`. The test asserts: the exit code is `runner.EXIT_TICKET`; stdout contains `drain stopped by kill -- NOT quiescent`; `engine.log` has an `engine_stop` event for verb `drain` with outcome `killed`; the journal records the kill decision for the drain's lifecycle; and the restore spy was called once. A drain that ignores the callback, or exits without going through the kill path, fails one of these.
- In: new `tests/unit/test_engine_signals.py`. It is needed because `test-gate.toml` sets unit coverage floors on `chupa/__main__.py` (13) and `chupa/drain.py` (10), and the hard `unit` check measures coverage over `tests/unit` only.
  - `test_engine_signals_covers_hangup`: inside a running loop, monkeypatches `loop.add_signal_handler` and `loop.remove_signal_handler` as `tests/integration/test_serve_kill.py` does. It calls `cli._engine_signals(cb)` and asserts that the registered set is `{SIGINT, SIGTERM, SIGHUP}`, that each registered handler is `cb`, and that calling restore removes all three.
  - `test_signal_kill_publishes_a_kill_request`: builds `_Drain` from a `SimpleNamespace` checkout, as `tests/unit/test_drain_deadline.py` does. The checkout carries a fixed `clock`, `config` with `state_dir=Path("/state")` and `drain.max_runtime_hours`, `control.inbox.lifecycle_id="life-1"`, and a fake `fs` whose `publish(path, data)` records its arguments. It calls `run._signal_kill()` and asserts one publish under `Path("/state/control/inbox")` whose decoded JSON has verb `kill`, lifecycle `life-1`, and hold `null`. A callback that bypasses the control inbox, or uses another lifecycle, fails it.
- In: `tests/integration/test_drain.py` (the self-upgrade child near line 1259), `tests/integration/test_drain_upgrade.py` (the handoff child near line 77), and `tests/integration/test_daemon_composition.py` (near line 1880): these run `main(["drain", ...])` through `asyncio.to_thread`. Off the main thread, `loop.add_signal_handler` raises, so in each of those tests monkeypatch `cli._engine_signals` (the module attribute `main` reads) with a no-op `lambda cb: lambda: None`. Add no thread check to production code; that would be a defensive dual path.
- In: `tests/integration/test_serve_kill.py`: use `cli._engine_signals`, add `"SIGHUP"` to the `mode` parametrize of `test_serve_signal_stop_and_restart_recovery`, and expect the removed set `{SIGINT, SIGTERM, SIGHUP}`.
- In: `tests/integration/test_serve_lifecycle.py`: the monkeypatch target becomes `_engine_signals`.
- In: new `tests/regress_drain_signals.py`: the carried reproducer. It runs the same scenario as `test_signal_kills_a_running_drain_like_kill` through `main(["drain"], ...)` with `cli._engine_signals` faked. If `cli` has no `_engine_signals` attribute, it fakes `_serve_signals` instead; at base drain never calls it, so no callback is captured. It prints `defect` and exits 1 when no callback is captured, or when the drain does not end with an `engine_stop` outcome of `killed`. It prints `pass` and exits 0 when it does. Its blocking step must not wait forever. When the ticket is running and no callback has been captured, it releases itself and lets the drain finish, so at base the script ends and reports `defect` with exit 1 instead of hanging. It runs `main` inside `contextlib.redirect_stdout(io.StringIO())`, so the only line on stdout is the final JSON object. It prints `error` and exits 2 when its own setup fails (an import or root construction raises). Follow `tests/regress_drain_park_findings.py`.
- In: `docs/how-chupa-works.md` section 7.1: add one sentence saying SIGHUP, SIGTERM, and SIGINT stop a drain as `kill` does: the running ticket is aborted and journaled, and the report says the drain is not quiescent.
- In: `chupa/docs/host-running.md`: in the paragraph that says serve runs until `kill`, `stop`, or Ctrl-C, add two facts. Closing a drain's terminal, SIGTERM, or Ctrl-C ends the drain the way `kill` does. Serve stops on SIGHUP the same way it already stops on Ctrl-C: an unjournaled stop that the next start reconciles.
- Out: detaching the drain from its terminal (ticket `drain-detach-in-engine`); serve's stop semantics beyond adding SIGHUP to its signal set; `SubprocessExec`; the self-upgrade handoff; and the control inbox format.

## Scope fence
- chupa/__main__.py
- chupa/drain.py
- tests/integration/test_drain_signals.py
- tests/unit/test_engine_signals.py
- tests/integration/test_drain.py
- tests/integration/test_drain_upgrade.py
- tests/integration/test_daemon_composition.py
- tests/integration/test_serve_kill.py
- tests/integration/test_serve_lifecycle.py
- tests/regress_drain_signals.py
- docs/how-chupa-works.md
- chupa/docs/host-running.md

## Acceptance criteria
1. `./dev.py test tests/unit/test_engine_signals.py tests/integration/test_drain_signals.py` exits 0. It shows that a signal callback delivered during a running ticket ends `main(["drain"])` with `runner.EXIT_TICKET`, `engine_stop` outcome `killed`, a journaled kill, and the restore called. A drain that installs no handler, or one that dies without `engine_stop`, fails it.
2. `./dev.py test tests/integration/test_serve_kill.py tests/integration/test_serve_lifecycle.py` exits 0, with the SIGHUP case included.
3. `grep -n "_serve_signals" -r chupa tests` prints nothing.
4. `uv run python tests/regress_drain_signals.py` prints `{"regression_result": "pass"}` and exits 0.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/unit/test_engine_signals.py tests/integration/test_drain_signals.py tests/integration/test_serve_kill.py tests/integration/test_serve_lifecycle.py
uv run python tests/regress_drain_signals.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of these is true: the drain gains an abort or exit path for signals that bypasses the control inbox kill path; a signal leaves no `engine_stop` or no journaled kill; `_serve_signals` survives beside `_engine_signals`; SIGHUP is ignored instead of handled; or `SubprocessExec`, the handoff, or the control request format changes.

## Time budget
- expected: 45m
- stuck: 90m

## Regression
```
uv run python tests/regress_drain_signals.py
```
- carries: tests/regress_drain_signals.py
