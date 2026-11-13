---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/drain.py::_Drain.run
- chupa/serve.py::Serve.box_intake
- chupa/triage.py::report_intake
- docs/how-chupa-works.md#9.4 Host bug reports
- tests/integration/test_inbox.py::arrival
- tests/unit/test_drain_containment.py

## On-demand
- tests/integration/test_drain.py

## Goal / Why
`suggest-lands-in-box` fixes one case of a wider problem: an arrival that lands outside the Suggestion Box stays invisible until a lifecycle that ingests it runs. Serve ingests through its `box_intake` task and triage through `triage_pass`, but `_Drain.run` never calls `triage.report_intake`. Drain is the lifecycle the operator actually runs: `engine.log` records 418 drain starts and no serve. So with `report_inbox` set, a host bug report written during a drain also stays out of the box until someone runs `triage`. Section 9.4 of `docs/how-chupa-works.md` says "serve and triage ingest host bug reports", which leaves drain out.

After this change, every engine lifecycle that holds the writer lock ingests `report_inbox` arrivals. `_Drain.run` calls `triage.report_intake(self.c)` each loop, directly after the ticket `intake(...)` call, so an arrival is in the box by the next loop. Ingesting is not triaging: the drain still never settles a message.

## Scope in / Scope out
Scope in:
- `chupa/drain.py`, `_Drain.run`: call `triage.report_intake(self.c)` each loop, directly after the ticket `intake(...)` call. A refused report is logged by `report_intake` as `report_intake_refused` and skipped, as it already is; the drain loop goes on.
- `tests/integration/test_drain.py`: add a test where `report_inbox` is set and one valid host report is in the inbox when a drain starts. After the drain's first loop, the box holds one pending `bug_report` message for it, and the journal has no `triage_pass` signal. Build the report with `tests/integration/test_inbox.py::arrival`.
- Create `tests/unit/test_drain_report_intake.py`, which lint requires because `chupa/drain.py` has a unit coverage floor. With `triage.report_intake` monkeypatched to record its call and the other per-loop collaborators faked in the style of `tests/unit/test_drain_containment.py`, one `_Drain.run` loop calls `report_intake` once with the drain's checkout, after ticket `intake`. A loop that skips it fails.
- `docs/how-chupa-works.md` section 9.4: change "serve and triage ingest host bug reports" to "serve, drain, and triage ingest host bug reports", adding that drain ingests between tickets.

Scope out:
- `chupa/serve.py`, `chupa/triage.py`, and `chupa/box.py`; triage passes inside the drain; the `suggest` verb, which is `suggest-lands-in-box`; `chupa/docs/host-contract.md`, whose report-inbox contract does not name lifecycles.

## Scope fence
- chupa/drain.py
- tests/integration/test_drain.py
- tests/unit/test_drain_report_intake.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_drain.py` passes a test in which a valid host report in `report_inbox` at drain start is a pending `bug_report` box message after the first loop. The current drain, which never calls `report_intake`, leaves the box empty and fails it.
2. The same test asserts the journal has no `triage_pass` signal after that loop. A drain that triages instead of only ingesting fails it.
3. `./dev.py test tests/integration/test_triage.py` still passes, including the assertion that the `drain` function never references `triage`.
4. `./dev.py test tests/unit/test_drain_report_intake.py` passes: one drain loop calls `report_intake` once, after ticket intake. A loop without the call fails it.
5. `docs/how-chupa-works.md` section 9.4 contains "serve, drain, and triage ingest host bug reports".

## Verification
```
./dev.py test tests/unit/test_drain_report_intake.py tests/integration/test_drain.py tests/integration/test_triage.py tests/integration/test_inbox.py
```

## Definition of rejected
- The drain runs `triage_pass` or settles any box message.
- A malformed report stops the drain loop.
- Any file outside the scope fence changes.

## Time budget
- expected: 25m
- stuck: 60m
