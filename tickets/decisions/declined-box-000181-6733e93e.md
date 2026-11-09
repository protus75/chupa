---
id: declined-box-000181-6733e93e
kind: declined
link: box-000181-6733e93e
reopen_after_days: 90
---
A bootstrap handoff review note warned that the `escalation-ladder` ticket changed drain behavior but did not fence `tests/test_drain.py` or `tests/test_drain_reentry.py`. If those tests pinned request tiers or draw counts across repeated identical failures, the ticket could not have landed inside its fence. The note asked for a re-check once batches 1-2 merged.

The concern was that `escalation-ladder` might not be able to land inside its own fence. That ticket is now in the merged list, so it did land. The worry was about one ticket's authoring and has been overtaken by events. There is no current runtime behavior gap and nothing left to build.

- `escalation-ladder` appears in the merged stems list.
- Registry records declined-box-000174-123d065d and declined-box-000178-208a05fe describe the merged `escalation-ladder` code (auto-keep only when `spent(...)` is None; terminal `reason`/`dispatch` comparison key), so it shipped.
- The message names no failing test or wrong runtime behavior on current main.

Message: box-000181-6733e93e
