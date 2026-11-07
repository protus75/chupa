# Review: snag

The verbs, extension and docs match the ticket, but `chupa.observe` keeps its configuration in module globals that leak between tests under xdist, and `./dev.py watch` lost its clean Ctrl-C exit.

## Findings

- [logic] chupa/observe.py:33 `configure()` sets module globals (ROOT, STATE, CONFIG, EXEC, GIT, ENV), and nothing resets them. The new tests in tests/test_watch.py call `main([... 'snapshot'])`, which leaves STATE pointing at that test's `custom-state` dir. The suite runs with `-n auto`, so any later test on the same worker that only monkeypatches ROOT reads the wrong directory. That includes `test_queue_projection_and_fallback` (`state_dir()/queue.json`) and `test_recent_steps_merges_engine_and_stage_events` (`text_snapshot()`). The tests now depend on order. (do instead: Pass the configured context (root, state dir, config path, exec, git, env) into `snapshot()` and `text_snapshot()` as an explicit object, or have the tests restore every global with monkeypatch. No call should leave process-wide state behind.)
- [logic] chupa/observe.py:28 `state_dir()` falls back to `ROOT / "state"` when the module is not configured. This is an invented default that matches neither the old config-reading behavior nor the engine's `.chupa/state`. The existing tests now pass only because their tmp dirs happen to use `state`, and the `config.yaml` they write is dead. (do instead: Require a configured state dir (no fallback), and make the existing tests supply it explicitly instead of relying on the default.)
- [logic] dev.py:101 `./dev.py watch` now goes through `chupa()` -> `run()` -> `subprocess.run` without the `KeyboardInterrupt` handler the old code had. Ctrl-C reaches dev.py's process group too, so stopping the live view now prints a traceback instead of exiting normally. The child exiting 0 does not prevent dev.py's own KeyboardInterrupt. (do instead: Keep the `try/except KeyboardInterrupt: pass` around the `chupa("watch", ...)` call in dev.py.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "c38d3d4b330f84f4831ff1342da8f3d53680f6bd",
  "stem": "observe-verbs-host-extension",
  "reviewed_sha": "c38d3d4b330f84f4831ff1342da8f3d53680f6bd",
  "summary": "The verbs, extension and docs match the ticket, but `chupa.observe` keeps its configuration in module globals that leak between tests under xdist, and `./dev.py watch` lost its clean Ctrl-C exit.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/observe.py",
      "line": 33,
      "message": "`configure()` sets module globals (ROOT, STATE, CONFIG, EXEC, GIT, ENV), and nothing resets them. The new tests in tests/test_watch.py call `main([... 'snapshot'])`, which leaves STATE pointing at that test's `custom-state` dir. The suite runs with `-n auto`, so any later test on the same worker that only monkeypatches ROOT reads the wrong directory. That includes `test_queue_projection_and_fallback` (`state_dir()/queue.json`) and `test_recent_steps_merges_engine_and_stage_events` (`text_snapshot()`). The tests now depend on order.",
      "paved_road": "Pass the configured context (root, state dir, config path, exec, git, env) into `snapshot()` and `text_snapshot()` as an explicit object, or have the tests restore every global with monkeypatch. No call should leave process-wide state behind.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/observe.py",
      "line": 28,
      "message": "`state_dir()` falls back to `ROOT / \"state\"` when the module is not configured. This is an invented default that matches neither the old config-reading behavior nor the engine's `.chupa/state`. The existing tests now pass only because their tmp dirs happen to use `state`, and the `config.yaml` they write is dead.",
      "paved_road": "Require a configured state dir (no fallback), and make the existing tests supply it explicitly instead of relying on the default.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "dev.py",
      "line": 101,
      "message": "`./dev.py watch` now goes through `chupa()` -> `run()` -> `subprocess.run` without the `KeyboardInterrupt` handler the old code had. Ctrl-C reaches dev.py's process group too, so stopping the live view now prints a traceback instead of exiting normally. The child exiting 0 does not prevent dev.py's own KeyboardInterrupt.",
      "paved_road": "Keep the `try/except KeyboardInterrupt: pass` around the `chupa(\"watch\", ...)` call in dev.py.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
