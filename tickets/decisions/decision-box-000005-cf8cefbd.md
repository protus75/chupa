---
id: decision-box-000005-cf8cefbd
kind: decision
link: box-000005-cf8cefbd
reopen_after_days: 90
---
The note warned that the first journal append could read the clock twice, once for the event timestamp and once for the segment file's date, so an append at midnight could get a timestamp and segment name with different dates. Current code reads the clock once, so the problem no longer exists.

`Journal.append` now calls `self._clock()` once, at chupa/journal.py:172, to render `event.ts`. It then gets `now` from that same string (`datetime.fromisoformat(event.ts)`, line 175) and passes it to `_active_segment` and `_create_segment`, which builds the `YYYYMMDD` segment name. The timestamp and the segment date therefore come from one clock read and cannot differ. The defect is not reachable now, so there is nothing to author. No open ticket, merged stem or decision clearly covers this exact fix, so a tombstone link would be a guess.

- chupa/journal.py:172 `event = Event(..., render_ts(self._clock()), ...)` is the only clock read in append
- chupa/journal.py:175 `now = datetime.fromisoformat(event.ts)` gets the segment date from the rendered timestamp
- chupa/journal.py:176 and :182 pass that `now` to `_active_segment`/`_create_segment`, and :225 builds the name as `f"{sequence:06d}-{now:%Y%m%d}.jsonl"`

Message: box-000005-cf8cefbd
