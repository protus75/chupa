---
id: tombstone-box-000422-6260dc47
kind: tombstone
link: declined-box-000418-0758c804
reopen_after_days: 30
---
An implement-stage note from commit-lock-commands says README.md line 73 states that Review needs the writer lock, and that the line would go out of date once the ticket's change lands.

Record 000418 already handled this report. On current main, README.md:73 says only that `serve` must be stopped before `drain` or `run` because each of those takes the writer lock. It says nothing about `review` and the lock. Records 000419-000421 were closed as duplicates of 000418 for the same reason. Reopen only if a README line on main is shown to claim that `review` takes the writer lock.

- README.md:73: "Stop `serve` before `drain` or `run`: each takes the writer lock."
- No other README.md line pairs `review` with the writer lock (grep for 'lock' matches lines 22, 30, 73 only).
- declined-box-000418-0758c804 decided the same README.md:73 claim; tombstones 000419-000421 link to it.

Message: box-000422-6260dc47
