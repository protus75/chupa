---
id: tombstone-box-000260-2ac04d53
kind: tombstone
link: tombstone-box-000158-1bee1d13
reopen_after_days: 30
---
The CLI provider adapter writes its event-stream capture under `spools/providers/<stem>/<provider>-<seq>/`. `<seq>` is a counter that restarts in each process, so a later process can overwrite an earlier attempt's `events.jsonl`. The note asks to move that capture into the per-attempt spool directory, so `spine-harvest` no longer has to work around it by reading the newest `events.jsonl` under the stem.

Registry record tombstone-box-000158-1bee1d13 already covers this gap: per-process `<seq>` capture directories, overwrites across processes, the `spine-harvest` newest-`events.jsonl` workaround, and the request to key capture by attempt. Records 000059, 000220 and 000225 trace back to the same request.

- tombstone-box-000158-1bee1d13 asks to attempt-key the adapter capture because `<seq>` restarts per process and spine-harvest reads the newest events.jsonl
- tombstone-box-000225-4486696a was already tombstoned to 000158 for the same overwrite-on-restart concern
- tombstone-box-000059-07864ba4 and tombstone-box-000220-f4fb7411 cover moving the adapter capture into the per-attempt spool directory

Message: box-000260-2ac04d53
