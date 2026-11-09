---
id: tombstone-box-000196-8eb8892d
kind: tombstone
link: declined-box-000009-d7745566
reopen_after_days: 90
---
A bootstrap note says `chupa/seams.py` began with Clock, ProcessExec and FileSystem Protocols that only declared signatures, and that git.py was supposed to add the real process-exec contract to that file later. It also says `journal.py` types its clock parameter as a raw `Callable` and not as `seams.Clock`.

Registry record declined-box-000009-d7745566 already covers the same note: seams.py starting with signature-only Protocols, git.py adding the process-exec contract later, and journal.py's raw Callable clock annotation. That record found that the process-exec contract now exists and that the clock annotation is only a type-name difference with no runtime effect.

- declined-box-000009-d7745566 describes the same seams.py signature-only origin, the git.py process-exec deferral and the journal.py raw Callable clock annotation
- tombstone-box-000013-7d15aaed and merged kill-executor-abort show the process-exec pieces (kill_group, pgid hook, abort binding) now exist

Message: box-000196-8eb8892d
