---
id: tombstone-box-000158-1bee1d13
kind: tombstone
link: tombstone-box-000059-07864ba4
reopen_after_days: 30
---
The CLI provider adapter writes each call's event stream and stderr to `spools/providers/<stem>/<provider>-<seq>/`. `<seq>` is a counter kept inside each client process, so it starts again in every new process. The note asks to key that capture by attempt under the per-attempt spool directory named in section 6, so a later process cannot overwrite an earlier attempt's `events.jsonl`. `spine-harvest` currently works around this by reading the newest `events.jsonl` under the stem.

Registry record tombstone-box-000059-07864ba4 already covers this proposal. That record asks to move the adapter's event-stream and stderr capture out of the per-client sequence directory and into the per-attempt spool directory, by passing the spool path through `LLMRequest`. It also links to declined-box-000039-af7f01a0. The only thing this note adds is that the overwrite happens because the sequence restarts in each process. It shows no failure: no wrong harvest and no lost evidence that a diagnosis needed. Reopen if a harvest or diagnosis is shown to read another attempt's events, or to lose events that were overwritten.

- chupa/providers.py:286 sets `self._seq = 0` for each client instance, and :313-314 builds `call_dir = capture_dir/<ticket>/<provider>-<seq:04d>`.
- chupa/providers.py:369 writes `events.jsonl` with `self._fs.write`, which replaces any existing file at that path.
- chupa/runner.py:442-443 harvests by searching `spools/providers/<stem>` for `events.jsonl` files with rglob, which is the stopgap the note describes.
- Registry tombstone-box-000059-07864ba4 proposes the same move of the adapter capture into the per-attempt spool.

Message: box-000158-1bee1d13
