---
id: tombstone-box-000197-9987a9c5
kind: tombstone
link: declined-box-000010-e476a678
reopen_after_days: 90
---
`Effects.run` checks for completed keys but does not guard a key that is still in progress. If two calls with the same key run at the same time in one event loop, both can execute the action. The note asks for a per-key asyncio lock or an in-flight set, plus a test, once some caller runs effects concurrently.

Registry record declined-box-000010-e476a678 already decided this exact gap: no per-key in-flight guard in `Effects.run`, and a per-key asyncio lock or in-flight set plus a test proposed for when a concurrent caller appears. This message is the same bootstrap note ingested again, with no new evidence of a concurrent same-key call actually happening.

- declined-box-000010-e476a678 describes the same missing in-flight guard in `Effects.run` and the same per-key asyncio lock or in-flight set remedy
- The message origin is bootstrap-ingest, and it reports no observed double execution
- Other bootstrap notes ingested again (000194, 000195, 000196) were tombstoned against their earlier records in the same way

Message: box-000197-9987a9c5
