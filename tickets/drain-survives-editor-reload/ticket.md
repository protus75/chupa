---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- dev.py
- watch.py
- docs/how-chupa-works.md

## Goal / Why
`./dev.py drain` runs the engine as a child of the shell that typed it. When that shell belongs to a VS Code terminal or an agent session inside VS Code, reloading the window kills the drain mid-ticket. On 2026-11-06 a window reload at 14:53Z killed the drain (lock pid 53650) during Implement on `remove-plan-grammar`. The engine log stops at 14:50:26Z, and the ticket stayed `running` in the journal until the next start reconciled it.

After this change `./dev.py drain` starts the engine in its own session, detached from the calling terminal, and returns at once. Closing or reloading the editor no longer stops it. `./dev.py watch` shows its progress, and `./dev.py stop` and `./dev.py kill` end it as before.

## Scope in / Scope out
- In: `dev.py` `drain` launches `uv run python -m chupa drain` from the repo root with `subprocess.Popen`, `start_new_session=True`, stdin from `subprocess.DEVNULL`, and stdout and stderr appended to `<state_dir>/drain.out`. `state_dir` is read from `config.yaml` the same way `watch.state_dir()` reads it.
- In: it prints the child pid and the output path, then exits 0 without waiting.
- In: a new `tests/test_dev.py` imports `dev` and replaces `subprocess.Popen` with a fake. It asserts that `drain` passes `start_new_session=True`, stdin `DEVNULL`, an append-mode file under the state dir, and the argv `["uv", "run", "python", "-m", "chupa", "drain"]`. It also asserts that `main()` returns without waiting on the child.
- In: `docs/how-chupa-works.md` section 2.2: the `drain` row says it runs detached and writes `<state_dir>/drain.out`.
- Out: `serve`, `run`, `stop`, `kill`, and every engine module; how the engine recovers a killed drain.

## Scope fence
- dev.py
- tests/test_dev.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `uv run pytest -q tests/test_dev.py` exits 0.
2. `docs/how-chupa-works.md` section 2.2 states that `./dev.py drain` runs detached and names `drain.out`.
3. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_dev.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if `./dev.py drain` still waits on the engine, if the engine shares the caller's session or terminal, if drain output is discarded rather than written to `drain.out`, or if any engine module changes.

## Time budget
- expected: 20m
- stuck: 60m
