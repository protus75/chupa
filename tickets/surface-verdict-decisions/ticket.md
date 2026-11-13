---
priority: P1
kind: feature
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on

- none

## Context

- chupa/status.py::project
- chupa/status.py::render
- chupa/control.py::decisions
- chupa/observe.py::snapshot
- chupa/__main__.py::_status
- vscode-chupa/media/view.js
- tests/integration/test_status.py
- tests/unit/test_control_known.py

## Goal / Why

`chupa/__main__.py` prints `<verb> submitted: <id> -- ./dev.py status shows the outcome` after confirm/reject, but `chupa/status.py` and `chupa/observe.py` never read a `control_decision` signal. A verdict decided `stale` or `rejected` under a running drain is invisible; on 2026-11-12 four stale extension verdicts went unnoticed until checked by hand and the drafts stayed in `state: draft`. `drain-settles-admissions` fixed the cause of those stale verdicts but left the visibility gap open on purpose (its Scope out excluded the extension, `observe.py` and the CLI message).

This ticket adds one projection of non-accepted `control_decision` signals to `Status`, renders it in `chupa status`, puts it in the `chupa snapshot` JSON, and has the extension draw it. All derivation stays in Python; the extension only draws the given field.

## Scope in / Scope out

Scope in:

- `Status` gains `verdict_decisions`: a tuple of `(request_id, verb, stem, decision, reason)` for every `control_decision` signal whose `decision` is `stale` or `rejected`, in journal order. `stem` is `""` when the body has none (non-admission verbs).
- `render` adds a `Verdict decisions` block, shown only when the tuple is non-empty, next to `Verdict refusals`.
- `snapshot` adds `verdictDecisions`: a list of objects with those five keys, built from the same projection (no filtering or sorting in JavaScript).
- `vscode-chupa/media/view.js` draws the `verdictDecisions` list as given.
- A new unit test file `tests/unit/test_status_verdict_decisions.py` exercises the new `chupa/status.py` lines directly (projection and render) so the unit coverage floor of `chupa/status.py` is met by a unit test.

Scope out:

- The existing `verdict_refusals` projection and its tests stay unchanged.
- No change to `control.py` decision logic, the CLI `submitted` message, drain, or serve.
- No acknowledgement or clearing verb for shown decisions.

## Scope fence

- chupa/status.py
- chupa/observe.py
- vscode-chupa/media/view.js
- tests/integration/test_status.py
- tests/unit/test_status_verdict_decisions.py

## Acceptance criteria

- A journal holding a `control_decision` signal with `decision: stale` makes `./dev.py test tests/integration/test_status.py` show that request in the `Verdict decisions` block of `render` output; the test rules out the wrong result of a block that is absent or lists only `verdict_refusals`.
- A `control_decision` with `decision: accepted` does not appear in `verdict_decisions` and no `Verdict decisions` block is rendered; `./dev.py test tests/unit/test_status_verdict_decisions.py` rules out accepted decisions being listed.
- The `snapshot` dict has a `verdictDecisions` entry equal to the five-key objects for the stale decision; `./dev.py test tests/integration/test_status.py` rules out an empty list or a missing key.
- `tests/unit/test_status_verdict_decisions.py` builds the projection from a stale and a rejected `control_decision` and asserts both appear in journal order with the five fields; the test rules out a projection that drops `rejected` or reorders rows.
- `vscode-chupa/media/view.js` contains `verdictDecisions`.

## Verification

```
./dev.py test tests/integration/test_status.py tests/unit/test_status_verdict_decisions.py
```

## Definition of rejected

- The extension filters, sorts, or derives the decision rows itself.
- Accepted decisions are listed, or `verdict_refusals` output changes.
- Tests pass when the stale decision is absent from `render` or `snapshot`.

## Time budget

- expected: 30m
- stuck: 90m
