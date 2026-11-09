---
id: declined-box-000339-b4e8fec1
kind: declined
link: box-000339-b4e8fec1
reopen_after_days: 14
---
The forced retro for window retro/30 failed with infra_error on 2026-11-07. It could not load the decision record `tickets/decisions/decision-box-000027-210a053d.md`, whose `kind: decision` is not one of the allowed values (`declined` or `tombstone`). Commit 20073cda has since renamed those records to the allowed kinds, and later retro runs finish ok.

No failure needs repair now. The cause was a single malformed decision record, and commit 20073cda ("rename decision records to declined") fixed it. `tickets/decisions/` now holds only `declined-*` and `tombstone-*` files. Retro stages after that commit end ok (engine.log run_seq 33 and 34 on 2026-11-09). A new ticket would repair nothing.

- engine.log:6119 retro_failed window_boundary=retro/30 trigger=forced: invalid decision record decision-box-000027-210a053d.md, kind input_value='decision' not 'declined' or 'tombstone'
- git log: b02c4e62 created decision-box-000027-210a053d; 20073cda 'chupa(decisions): rename decision records to declined'
- tickets/decisions/ now holds only declined-* and tombstone-* files
- engine.log:6622 and 6717: retro stage_end outcome ok at run_seq 33 and 34 on 2026-11-09

Message: box-000339-b4e8fec1
