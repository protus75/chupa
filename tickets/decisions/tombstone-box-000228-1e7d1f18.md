---
id: tombstone-box-000228-1e7d1f18
kind: tombstone
link: tombstone-box-000077-a79f4db4
reopen_after_days: 90
---
The note asks that the Phase 5 baseline binding reader treat a recorded null `author.spec_major` in the `review_baseline` signal as a mismatch, so the binding stays on the supervised side. The null comes from the time when `specs/author.md` was only a seed.

Registry record tombstone-box-000077-a79f4db4 already covers this same request and links it to merged ticket `baseline-binding-reader`. According to that record, `_matches` in `chupa/baseline.py` returns False when the recorded major is not an int, so a null major already counts as non-matching.

- Registry record tombstone-box-000077-a79f4db4: the baseline binding reader treats a null `author.spec_major` as a mismatch; delivered by merged ticket `baseline-binding-reader`.
- `baseline-binding-reader` is in the merged stems list.

Message: box-000228-1e7d1f18
