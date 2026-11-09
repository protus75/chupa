---
id: declined-box-000123-687dd93a
kind: declined
link: box-000123-687dd93a
reopen_after_days: 60
---
A bootstrap note says `run <stem>` exits 1 when a ticket ends `already_satisfied`, because the section 18 exit contract keeps 0 for `merged`, even though `already_satisfied` is a settled no-op and not a failure. It asks for section 18 to state the exit code for this case before `drain` starts deciding parking from it.

The note's harm depended on drain choosing whether to park a ticket from the `run` exit code. Drain does not do that. Since the merged ticket `already-satisfied-settles`, `drive` journals `to: already_satisfied` as a settled terminal with no diagnosis and no reject routing. Drain, status and intake read settlement from the journal (`SETTLED` contains `merged` and `already_satisfied`), not from the exit code. A settled no-op exiting 1 is a gap in the contract's wording only. Nothing shows a caller handling it wrongly at runtime.

- chupa/runner.py:215-216 journals already_satisfied as a settled state_transition
- chupa/status.py:16 SETTLED = frozenset({"merged", "already_satisfied"})
- chupa/tickets.py:676 and chupa/stats.py:11 treat already_satisfied as settled from journal state
- merged ticket already-satisfied-settles moved already_satisfied off the failure path
- no grep hit for already_satisfied in chupa/drain.py or chupa/__main__.py, so neither keys behavior on its exit code

Message: box-000123-687dd93a
