---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- verb-lock-need-single-source

## Context
- chupa/observe.py::lock_holder
- chupa/observe.py::processes
- chupa/observe.py::snapshot
- chupa/__main__.py::_control
- docs/how-chupa-works.md#2.2

## On-demand
- tests/integration/test_watch.py

## Goal / Why
The Tickets view shows its Stop button whenever the snapshot's `engine` flag is true (`chupa.engineRunning` in `vscode-chupa/package.json`). `snapshot` in `chupa/observe.py` sets `engine` to `alive`, which is true while any live process holds `.chupa/state/chupa.lock`. But many verbs hold that lock besides an engine: `triage`, `dismiss`, `retro`, `review` of an uncommitted ticket, and a locked verdict. On 2026-11-11 the operator saw the Stop button while `chupa triage` was authoring a ticket and no drain or serve was running. Stop runs `chupa stop`, and only `drain` and `serve` publish the control identity that a stop request reaches (`consumer.publish()` in `chupa/drain.py` and `chupa/serve.py`). So the button offered an action with no engine to receive it. Evidence: `evidence/stop-icon-evidence.txt`.

When this ticket is done, `engine` is true only while the live lock holder is a `drain` or `serve` process. The snapshot already parses the holder's verb from its process arguments to build the `lock` string; `engine` uses that same parsed verb. Any other holder (or a verb that cannot be parsed) gives `engine: false`, while `lock` still names the holder for the lock icon's tooltip.

## Scope in / Scope out
- In: the `engine` field of `chupa/observe.py::snapshot`, computed from the verb the snapshot already parses for `lock`. Allowlist `drain` and `serve`.
- In: `tests/integration/test_watch.py` coverage of `engine` for a drain holder, a serve holder, a triage holder, and no holder.
- In: `docs/how-chupa-works.md` section 2.2, the sentence "Its start/stop icon follows the snapshot engine flag": say the flag is true only while a drain or serve holds the lock.
- In: new carried reproducer `tests/regress_engine_flag_only_drain_serve.py`.
- Out:
  - Every other use of `alive` in `snapshot` (badge, menu availability, verdict availability, interrupted rows). Ticket `verb-lock-need-single-source` owns how those read verb properties.
  - Recording the holder's verb in the lockfile instead of parsing process arguments; ticket `verb-lock-need-single-source` owns that.
  - The extension (`vscode-chupa/`): it already maps `engine` to `chupa.engineRunning`.
  - The Play button now showing while a non-engine verb holds the lock. Starting a drain then refuses with `LockHeld`, which names the holder.

## Scope fence
- chupa/observe.py
- docs/how-chupa-works.md
- tests/integration/test_watch.py
- tests/regress_engine_flag_only_drain_serve.py

## Acceptance criteria
1. `tests/integration/test_watch.py`: with a live lock holder whose process arguments are `python -m chupa triage`, `snapshot(ctx)["engine"]` is `False`, not `True`, and `snapshot(ctx)["lock"]` still starts with `triage since`.
2. The same test with holder arguments `python -m chupa drain --detach` and `python -m chupa --config c.yaml serve` gives `engine` `True` for each.
3. With no live lock holder, `engine` is `False`.
4. `tests/regress_engine_flag_only_drain_serve.py` imports nothing from `tests/`, fakes a live triage lock holder, and prints `pass` only when `snapshot` returns `engine: false`. At base, where `engine` is `alive`, it prints `defect`.
5. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch. At the merge base it prints `defect` and exits non-zero.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- `engine` is true for any holder other than drain or serve.
- `engine` is false while a drain or serve holds the lock.
- The verb check lives in `vscode-chupa/` JavaScript instead of the snapshot.
- A second parse of the holder's process arguments is added beside the existing one.

## Time budget
- expected: 25m
- stuck: 60m

## Regression
```
uv run python tests/regress_engine_flag_only_drain_serve.py
```
- carries: tests/regress_engine_flag_only_drain_serve.py
