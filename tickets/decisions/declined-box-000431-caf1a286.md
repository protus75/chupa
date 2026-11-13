---
id: declined-box-000431-caf1a286
kind: declined
link: box-000431-caf1a286
reopen_after_days: 30
---
The note proposes adding a rule to the Scope fence bullet in the host authoring guide. The rule would say to fence only the test modules and fixture directories a ticket owns, never a whole tests directory, so that an agent cannot rewrite tests it does not own. The idea was carried over from the fungo host on 2026-11-13. It cites no run where a wide fence let an agent change tests it did not own.

This is preventive hardening of authoring guidance. No current, reachable harm is shown. The note says outright that it cites no incident, and nothing in the open tickets or the decision registry records an agent rewriting tests outside its ownership because a fence named a whole tests directory. The Scope fence bullet in `chupa/docs/host-authoring.md` (lines 52-55) already requires fencing every file the acceptance criteria force, including existing tests whose assertions flip. Review also checks the diff against what the ticket asks for, and that check would catch an unrelated test rewrite. With no observed failure, a post-change measurement has nothing to show. Reopen within 30 days if a run record, review finding, or retro shows a ticket with a directory-wide tests fence whose Implement attempt changed or weakened tests outside the ticket's ownership, and that change reached Review or merge.

- The message says 'No incident cited.'
- `chupa/docs/host-authoring.md:52-55`: the Scope fence bullet already requires fencing forced files, including existing tests whose assertions flip
- No open ticket or registry record reports harm from a directory-wide tests fence

Message: box-000431-caf1a286
