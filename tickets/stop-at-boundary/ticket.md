---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- serve-self-upgrade

## Context
- chupa/control.py
- chupa/drain.py
- chupa/serve.py
- chupa/__main__.py
- dev.py
- tests/test_control.py
- tests/test_closed_sets.py

## On-demand
- tests/test_control_cli.py
- tests/test_drain.py
- tests/test_serve.py
- tests/test_kill_cli_activation.py
- docs/how-chupa-works.md

## Goal / Why
An operator who needs the lock (to keep or kill a Reject-queue ticket, or to let a drain pick up new tickets) has two choices today:
- `kill` aborts the running ticket and loses its attempt;
- `pause` stops new dispatch but keeps the process alive, still holding the lock.

On 2026-11-05 a supervising session had to poll `watch` for the current ticket to end, then send `kill`, several times. After this change `stop` asks a running drain or serve to finish the work in progress, admit nothing new, and exit 0, freeing the lock.

## Scope in / Scope out
- In: `chupa/control.py`:
  - add `stop` to `Verb` and to `validate_request`'s verbs, with no hold id;
  - add `stop_requested: bool = False` to `ControlProjection`, folded from accepted `stop` decisions as `kill` is.
- In: `chupa/drain.py`: once `stop_requested` is set, `_select` picks nothing.
  - A ticket already dispatched runs to its terminal, including its inline merge.
  - The drain then returns a report that says it stopped on request, with exit code 0.
  - A stop requested before any dispatch exits at the next checkpoint.
  - A pending self-upgrade handoff still happens first; the child sees the same accepted request and stops.
- In: `chupa/serve.py`: once `stop_requested` is set, serve admits nothing new, waits for the same idle condition its self-upgrade handoff uses (no running ticket, no continuation, empty merge queue), and then exits 0 through its normal cleanup with no spawn. Reuse that idle check; never add a second one.
- In: `chupa/__main__.py`: a `stop` verb published like `kill`. With nothing running it refuses (exit 2) with the road "nothing running to stop". Help: "finish the running ticket, admit nothing new, then exit".
- In: `dev.py`: a `stop` subcommand that runs `chupa stop`, plus a docstring line.
- In: docs.
  - `docs/how-chupa-works.md` section 2.1: the verb table row for `stop`.
  - Section 2.2: list `stop`.
  - Section 7.3: `stop` versus `pause` and `kill`.
- Out: `kill` and `pause` semantics; `run`; any timeout on how long `stop` waits.

## Scope fence
- chupa/control.py
- chupa/drain.py
- chupa/serve.py
- chupa/__main__.py
- dev.py
- tests/test_control.py
- tests/test_closed_sets.py
- tests/test_control_cli.py
- tests/test_drain.py
- tests/test_serve.py
- tests/test_kill_cli_activation.py
- tests/test_kill_signal_journal.py
- docs/how-chupa-works.md

## Acceptance criteria
1. A `stop` request published while a drain runs ticket `a` lets `a` reach its terminal and merge. No further ticket dispatches, and the drain exits 0 with the lock released. A test fails if `a` is aborted or another ticket starts. Checked by `uv run pytest tests/test_drain.py`.
2. A `stop` published while serve has a running ticket lets that ticket finish and merge, admits nothing new, and serve exits 0 without spawning a child. Checked by `uv run pytest tests/test_serve.py`.
3. `stop` with nothing running exits 2 with "nothing running to stop". Checked by `uv run pytest tests/test_control_cli.py`.
4. `control.Verb` is exactly `{kill, pause, resume, stop}`. Checked by `uv run pytest tests/test_closed_sets.py`.
5. `./dev.py --help` lists `stop`.
6. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_control.py tests/test_closed_sets.py tests/test_control_cli.py tests/test_drain.py tests/test_serve.py
./dev.py --help
uv run pytest -q
```

## Definition of rejected
`stop` aborts a running ticket; a second serve idle check beside the self-upgrade one; `stop` keeps holding the lock after the work in progress ends; `kill` or `pause` behaviour changes.

## Time budget
- expected: 60m
- stuck: 150m
