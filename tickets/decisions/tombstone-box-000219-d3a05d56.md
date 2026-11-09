---
id: tombstone-box-000219-d3a05d56
kind: tombstone
link: declined-box-000027-210a053d
reopen_after_days: 90
---
A bootstrap note says routing candidates must set `model` in the config schema, even though the provider contract lets a candidate leave it out and take the model from its provider's `models_by_tier[tier]`. It proposes making the field optional and resolving it in the provider layer.

Registry record declined-box-000027-210a053d already covers this gap: a routing candidate that leaves out `model` was refused even though the contract allows the omission. That record found that current code already allows it. Records tombstone-box-000055 and tombstone-box-000205 link to it for the same request. The wording here differs, but the request is the same.

- declined-box-000027-210a053d: current code already allows a routing candidate to omit `model`
- tombstone-box-000055-925679f6 and tombstone-box-000205-28177ca6 are earlier duplicates of the same note, both linked to 000027

Message: box-000219-d3a05d56
