---
id: tombstone-box-000419-4ee493b9
kind: tombstone
link: declined-box-000418-0758c804
reopen_after_days: 30
---
An implement run in verb-lock-need-single-source reported that README.md says `review` always takes the writer lock, although committed tickets can be reviewed without it. The run left README.md alone because it was outside the scope fence.

This is the same report that registry record declined-box-000418-0758c804 already settled: README.md never says `review` takes the writer lock. On current main the only lock statement is line 73: "Stop `serve` before `drain` or `run`: each takes the writer lock." That line names only `drain` and `run`, not `review`. The claimed doc mismatch does not exist, so nothing needs to be built. Reopen if README.md gains a statement that `review` takes the writer lock.

- README.md:73 reads "Stop `serve` before `drain` or `run`: each takes the writer lock." It does not mention `review`.
- A search of README.md for 'lock' finds no line that says `review` takes the writer lock.
- Registry record declined-box-000418-0758c804 declined the same claim about README.md line 73 and `review`.

Message: box-000419-4ee493b9
