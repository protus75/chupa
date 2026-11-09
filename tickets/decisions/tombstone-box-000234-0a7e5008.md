---
id: tombstone-box-000234-0a7e5008
kind: tombstone
link: declined-box-000085-cbfb936f
reopen_after_days: 90
---
Ticket intake never compares an edited established ticket with its committed predecessor, so a hand edit that lowers `source: seed` to `human` gets through unchecked. The note asks to add a git `show <rev>:<path>` operation so intake can enforce that an established seed is never demoted.

Registry record declined-box-000085-cbfb936f already settled this request: intake does not re-check `source` on edit, and the proposed fix is a git `show` op to compare against the committed version. The wording differs but the gap and the fix are the same. Since that decision, seeding has been removed (merged `remove-seeding`, see declined-box-000190 and declined-box-000138), so `source: seed` now has even less to protect.

- declined-box-000085-cbfb936f: same gap (no `source` check on edit) and same fix (git `show <rev>:<path>`)
- Merged ticket remove-seeding removed the seeding lane, so a seed-provenance demotion has no reachable harmful consequence
- declined-box-000089-ab4947b8 declined the related request to enforce state edits against the committed predecessor through `show`

Message: box-000234-0a7e5008
