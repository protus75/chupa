---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/drain.py
- chupa/serve.py
- chupa/enginelog.py
- chupa/redact.py
- watch.py
- vscode-chupa/snapshot.py
- vscode-chupa/extension.js
- tests/test_drain.py
- tests/test_serve.py
- tests/test_watch.py
- docs/how-chupa-works.md

## Goal / Why
Nothing records when a drain or serve starts or stops. The engine log holds only stage and model-call events, and the journal records only a self-upgrade handoff. `./dev.py watch`'s "Recent steps" and the `vscode-chupa` Recent Steps view therefore cannot show when the engine ran. A drain killed by a VS Code window reload (2026-11-06) left no trace of its end at all.

After this change, `drain` and `serve` write an `engine_start` event to the engine log once they hold the lock, and an `engine_stop` event with an outcome before they release it. Both recent-steps views show these events among the stage events.

## Scope in / Scope out
- In: `chupa/drain.py` and `chupa/serve.py`, through an `EngineLog` built as `serve.py` builds it (state_dir `engine.log`, `Redactor.from_config`, the checkout clock). Never the journal.
  - Right after `lock.acquire()`: `engine_start` with `verb` (`drain` or `serve`) and `pid`.
  - In the `finally` that releases the lock, before release: `engine_stop` with `verb`, `pid`, and `outcome`.
    - For drain, `outcome` is one of `quiescent`, `stopped`, `killed`, `halted`, `handoff`, or `error: <ExceptionType>`.
    - For serve, it is `stopped`, `killed`, or `error: <ExceptionType>`.
- In: `watch.py`, under "Recent steps", and `vscode-chupa/snapshot.py`'s `steps`.
  - Both include `engine_start` and `engine_stop` events in time order with the stage events, rendered as `<time>  drain started (pid N)` and `<time>  drain stopped (<outcome>)`.
  - When the newest `engine_start` has no later `engine_stop` and `watch.lock_holder` reports no live holder, they add one line: `drain ended without a stop record (killed?)`.
- In: `vscode-chupa/extension.js`: Recent Steps items for these events have no ticket name, a `debug-start` or `debug-stop` icon, and no open-ticket command.
- In: tests.
  - `tests/test_drain.py`: a drain to quiescence writes exactly one `engine_start` and one `engine_stop` with outcome `quiescent`, in that order, and both precede lock release.
  - `tests/test_serve.py`: a serve stopped through control writes both, with outcome `stopped`.
  - `tests/test_watch.py`: Recent steps renders start, stop, and the "ended without a stop record" line.
- In: `docs/how-chupa-works.md`: the `engine.log` row in section 10.1 names `engine_start` and `engine_stop`.
- Out: the journal, `run`, `review`, and other lock holders; log rotation; control semantics.

## Scope fence
- chupa/drain.py
- chupa/serve.py
- watch.py
- vscode-chupa/snapshot.py
- vscode-chupa/extension.js
- tests/test_drain.py
- tests/test_serve.py
- tests/test_watch.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_drain.py tests/test_serve.py tests/test_watch.py` exits 0, including the tests above.
2. `node --check vscode-chupa/extension.js` exits 0.
3. `docs/how-chupa-works.md` section 10.1 names both events.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_drain.py tests/test_serve.py tests/test_watch.py
node --check vscode-chupa/extension.js
uv run pytest -q
```

## Definition of rejected
Reject the branch if either event goes to the journal, if `engine_stop` is written after the lock is released, if a normal drain exit writes no `engine_stop`, or if the recent-steps views drop stage events.

## Time budget
- expected: 45m
- stuck: 120m
