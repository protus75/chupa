---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/retro.py
- chupa/__main__.py
- tests/test_retro.py
- tests/test_cli.py
- tests/test_drain.py

## On-demand
- specs/retro.md

## Plan contract
- 19.P5.retro-drain-invoker
- section 8
- section 14

## Goal / Why
A forced retro over a journal window larger than the section 8 render bound commits its `tickets/retro/<seq>.md` report, and a recorded retro failure stops suppressing the window once a later merge lands (19.P5.retro-drain-invoker). Today `Retro.__call__` (`chupa/retro.py`) embeds every window event in the prompt: the first window (all history) rendered 5,132,419 characters against the 400,000 bound, failed `RenderOverBound`, and its `retro-failed/initial/merges` record then suppressed every later retro, including the forced pre-exit run, so phase5-exit has no receipt to read.

## Scope in / Scope out
- In: `Retro.__call__` always embeds the evidence measurements; it embeds the window only when the rendered prompt fits the authoring headroom (0.75 of the render bound), otherwise it writes the window's ordered `{v, type, ts, ticket, key, body}` envelopes as JSONL into the retro call's spool through the Driver's filesystem seam and renders that path for the model to read on demand; `specs/retro.md` states both input forms and bumps its version.
- In: retro failure suppression in `chupa/retro.py` and the `retro` verb in `chupa/__main__.py` holds only while no `state_transition` to `merged` follows the matching `retro_failed` record; the signal's key and body are unchanged.
- In: `tests/test_retro.py` adds `test_window_over_headroom_is_read_on_demand` (a window under headroom is embedded; one over it is spooled as ordered JSONL named by path, with the rendered prompt within the bound and the report committed) and extends `test_failed_retro_suppresses_window_until_completion` with later-merge release; `tests/test_cli.py::test_retro_no_commit` keeps its suppressed case and adds a merge-after-failure case that runs; `tests/test_drain.py::test_drain_retro_due_quiescence_and_pre_exit` selected-failure case expects the retro to run again after the later merges release the failure (one attempt and one `retro_failed` record per release), retaining its dispatch-order assertion.
- Out: trigger selection, the report format, the window boundary, the failure signal's shape, and the Driver.

## Scope fence
- chupa/retro.py
- chupa/__main__.py
- specs/retro.md
- tests/test_retro.py
- tests/test_cli.py
- tests/test_drain.py

## Acceptance criteria
1. `uv run pytest -q tests/test_retro.py tests/test_cli.py tests/test_drain.py tests/test_specs.py` exits 0, including `test_window_over_headroom_is_read_on_demand`.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_retro.py tests/test_cli.py tests/test_drain.py tests/test_specs.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_retro.py -k test_window_over_headroom_is_read_on_demand
```
- carries: tests/test_retro.py

## Definition of rejected
Reject the branch if any window is truncated or summarized instead of spooled whole, if a failure is retried before a later merge or completion, if the failure signal's key or body changes, or if the regression test passes on the merge base.

## Time budget
- expected: 45m
- stuck: 120m
