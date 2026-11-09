---
id: tombstone-box-000316-2a4366b2
kind: tombstone
link: declined-box-000315-dd03ac71
reopen_after_days: 30
---
The proposal is for `chupa/specs/implement.md` to tell the implementer to search `docs/` and `README.md` for statements its change makes false before committing. It would fix those inside the fence and report those outside it in `second_problems`. This would match the docs check Review already does. The motivating evidence is the attempts-cap run: attempts 7 and 8 each left a different stale section of `docs/how-chupa-works.md` (6.1, then 6.7), and the ticket passed only on attempt 9.

This asks for the same rule as registry record declined-box-000315-dd03ac71: the same implement.md step, the same `docs/` and `README.md` sweep, and the same split between fixing in-fence docs and filing out-of-fence docs in `second_problems`. Only the incident is new: attempts-cap instead of ticket-changed-midrun. A duplicate of an existing registry record is tombstoned and linked to that record, even when the evidence has changed. A grep of `chupa/specs/implement.md` finds no docs or stale-statement rule, so the gap described in record 000315 still exists.

- declined-box-000315-dd03ac71 proposes the same implement.md rule: before committing, search docs/ and README.md for statements the diff makes false, fix those inside the fence, and report those outside it in second_problems
- Grep of chupa/specs/implement.md for 'docs/|README|falsif|stale' returns no matches, so the rule has not been added since record 000315
- The message's incident is attempts-cap attempts 7 and 8, which left stale docs/how-chupa-works.md sections 6.1 and 6.7; record 000315's incident was ticket-changed-midrun attempt 3, which left a stale section 6.1

Message: box-000316-2a4366b2
