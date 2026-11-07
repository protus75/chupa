---
id: declined-box-000057-dfbd681c
kind: declined
link: box-000057-dfbd681c
reopen_after_days: 90
---
The note asks the crash-fault harness to also crash a second time during restart recovery, inside the journal writer's torn-tail truncate and fsync, and then check that once-semantics still hold. It is a proposal for more test coverage. It reports no failure.

This only adds tests and names no current runtime fault. `_truncate_torn_tail` in `chupa/journal.py` is idempotent: it cuts the segment back to its last newline. A crash during that truncate or fsync leaves the file either still torn or already cut back. On the next restart a new `Journal` has `_tail_repaired` false, so it runs the same repair again before it appends anything. `_parse_segment` already drops a torn tail on the active segment when reading. So a crash during recovery ends in the same state as a crash before recovery, and the case the existing harness already induces covers it. There is no evidence of a duplicated or lost effect after a crash during recovery.

- chupa/journal.py:230-238 `_truncate_torn_tail` truncates to `data.rfind(b"\n") + 1` and fsyncs, which is idempotent if repeated
- chupa/journal.py:177-179 the repair runs on the first append of every new Journal handle, so a restart after a crash during recovery repeats it
- chupa/journal.py:241-248 a torn tail on the active segment is dropped on read, so readers never see the partial state
- The message cites no failing run, journal corruption, or duplicate effect

Message: box-000057-dfbd681c
