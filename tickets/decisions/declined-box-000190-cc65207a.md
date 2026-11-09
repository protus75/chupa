---
id: declined-box-000190-cc65207a
kind: declined
link: box-000190-cc65207a
reopen_after_days: 90
---
A bootstrap review note asked that a seeding ticket whose Implement commits a seed `tickets/<other>/ticket.md` on its branch fail Check, with a paved road telling the agent to leave seeds uncommitted. The note says `lift_seeds` would otherwise leave a tracked deletion behind. Merged ticket `remove-seeding` has since removed the seeding lane, including the seed lift and the path for seeds authored during Implement.

The gap is in a mechanism that no longer exists. Registry record declined-box-000138-65491dbc confirms that `remove-seeding` removed the seeding lane, and that only `chupa/tickets.py` intake and `chupa/author.py` write tickets now. A branch-committed seed path therefore cannot reach a `lift_seeds` move, so current runtime behavior has no reachable fault.

- Merged stems include remove-seeding, remove-phase-exits and remove-bootstrap-ingest.
- Registry declined-box-000138-65491dbc: the seeding lane no longer exists; in current code only tickets.py intake and author.py write tickets.
- The note reports no failure. It asks the requisition-seed-path and phase2-exit specs, both merged bootstrap tickets, to pin an extra edge case.

Message: box-000190-cc65207a
