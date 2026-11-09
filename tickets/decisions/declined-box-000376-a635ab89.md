---
id: declined-box-000376-a635ab89
kind: declined
link: box-000376-a635ab89
reopen_after_days: 30
---
The note proposes two authoring rules for `author.md` and `host-authoring.md`. First, every item in a ticket's 'Definition of rejected' should map to a failing test in an acceptance criterion. Second, an edit to a doc or value should name every occurrence found by searching the file that owns it. The trigger was retro-spike-kinds, which requisition review snagged on 2026-11-08 for an untested invariant and for a fence that named only some occurrences of a value repeated in one file.

The evidence shows the current gate working, not a harmful gap. Requisition review caught both defects before Implement ran, and retro-spike-kinds has since merged. The only cost shown is one requisition re-author round. No paid Implement attempt, cap unit or Reject-queue hold was lost. The note also bundles two unrelated authoring rules, so it is not one buildable ticket. The second rule partly overlaps the open ticket set-membership-fence-closure, which already adds a closure step for values listed in several places. Without a downstream failure, adding author-side rules is speculative hardening.

- Message: retro-spike-kinds was 'snagged at requisition for both' (2026-11-08), so requisition review already caught both defects before Implement.
- retro-spike-kinds is in the merged set, so nothing is still blocked.
- The open ticket set-membership-fence-closure already adds an author-spec and requisition-review closure for set members repeated across tests and docs.
- The proposal bundles two separate rules, one about Definition-of-rejected test mapping and one about every occurrence in the owning file, so it is not one bounded ticket.
- The note reports no Implement premise_failed, gate_failed, spent cap or Reject-queue entry caused by either gap.

Message: box-000376-a635ab89
