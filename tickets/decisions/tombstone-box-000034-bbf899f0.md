---
id: tombstone-box-000034-bbf899f0
kind: tombstone
link: host-checks
reopen_after_days: 90
---
A bootstrap note said a crashing check should fail closed as a hard failure with a generic paved road, and that this belongs in the host check runner, not in `run_gates`, which lets a gate's exception propagate. The merged `host-checks` ticket built that runner, and it already turns a crashed, timed-out or missing-executable host command into a failing finding with a paved road.

The work the note asks for already exists. In `chupa/stages.py` `run_host_command` (line 696), a non-zero exit, a `TimeoutError` or an `ExecutableNotFound` each becomes a failing `GateReport` with a matching paved road. `check_hosts` (line 1138) adds those findings to the hard failures when the entry's severity is hard, and it checks the merge base first so a failure that main already has is not blamed on the ticket. The note says `run_gates` should keep raising, and it still does. No open behavior gap is left to build.

- chupa/stages.py:696-710 run_host_command: a non-zero rc, TimeoutError or ExecutableNotFound becomes Finding + verdict 'fail' with a paved road
- chupa/stages.py:1138-1179 check_hosts: a failing hard-severity host check adds to the hard findings after the merge-base check
- chupa/gates.py:96 run_gates: still has no exception handler, as the note intends
- merged stem host-checks

Message: box-000034-bbf899f0
