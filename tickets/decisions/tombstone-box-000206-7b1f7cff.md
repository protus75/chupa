---
id: tombstone-box-000206-7b1f7cff
kind: tombstone
link: declined-box-000028-4e669249
reopen_after_days: 90
---
A bootstrap note says `Limits.concurrency` has no default and must be set. Because Phase 1 prompt 1 parses only `limits.est_cost_per_call_usd`, a `limits` block that sets only that key is refused. The note asks section 15 to say whether concurrency is required or has a shipped default. Registry record 000028 already covers the same gap.

This means the same thing as declined-box-000028-4e669249: the same required-concurrency field, the same Phase 1 prompt 1 cause, and the same request for section 15 to settle required-or-default. Only the wording differs.

- declined-box-000028-4e669249 records that `Limits.concurrency` is required with no default, so a `limits` block that sets only `est_cost_per_call_usd` is refused, and asks the spec to settle required-or-default.
- tombstone-box-000063-d4772598 already links a related concurrency note to the same record.

Message: box-000206-7b1f7cff
