---
id: tombstone-box-000205-28177ca6
kind: tombstone
link: declined-box-000027-210a053d
reopen_after_days: 90
---
A bootstrap note says routing candidates must include `model`, so a config that names only a provider and expects the model to come from `models_by_tier[tier]` would be refused. It asks to make `model` optional while still refusing an explicit null.

This repeats the gap already decided in registry record declined-box-000027-210a053d. That record found the current config code already lets a candidate omit `model`. Tombstone record 000055 already links a duplicate of this note to the same record, and nothing new suggests the gap has come back.

- declined-box-000027-210a053d: a routing candidate without `model` was refused, but current code allows the omission
- tombstone-box-000055-925679f6: earlier duplicate of the same note, linked to declined-box-000027-210a053d
- origin is bootstrap-ingest, and the note asks for the change before Phase 1 prompt 1 runs, which describes the bootstrap state and not current code

Message: box-000205-28177ca6
