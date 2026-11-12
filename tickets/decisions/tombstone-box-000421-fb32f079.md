---
id: tombstone-box-000421-fb32f079
kind: tombstone
link: declined-box-000418-0758c804
reopen_after_days: 30
---
A note from the verb-lock-need-single-source Implement run says README.md tells operators to stop serve before running review. The run did not fix it because README.md was outside its scope fence.

This is the same report that record 000418 already declined, and records 000419 and 000420 already tombstoned against it. Current README.md still does not make the claim. Line 73 says to stop `serve` only before `drain` or `run`. Line 53 describes `chupa review` as reviewing a committed ticket, with no lock or stop-serve requirement. Reopen if a README line is found that ties `review` to stopping serve or to the writer lock.

- README.md:73 reads: 'Stop `serve` before `drain` or `run`: each takes the writer lock.' It does not mention review.
- README.md:53 reads: 'uv run chupa review   # review a committed ticket'. It states no lock or serve requirement.
- Record declined-box-000418-0758c804 already declined this README claim from the same origin, and records tombstone-box-000419 and -000420 point to it.

Message: box-000421-fb32f079
