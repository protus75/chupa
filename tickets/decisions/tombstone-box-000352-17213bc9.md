---
id: tombstone-box-000352-17213bc9
kind: tombstone
link: confirm-note-reofferable-stem
reopen_after_days: 30
---
When an implement-stage premise_failed stem still has premise_bounce budget, the journal routes it to the Reject queue (seen in chupa-test-gates attempt 2). `confirm` and `status` then list it as held, while the snapshot shows it unheld and the drain offers it again without a keep. docs/how-chupa-works.md section 6.6 describes the stem only as parked until ticket.md changes. The note asks for the routing and the doc to be made to agree.

The only harm this mismatch can cause at runtime is that an operator sees a Reject-queue item, runs `confirm`, and journals a keep that resets the cap budget for a stem the drain would offer again anyway. Open ticket confirm-note-reofferable-stem covers that exact state: a queued stem that is not awaiting the operator, such as a premise_failed stem with premise_bounce budget left, where `drain.reofferable` is true. It fixes the harm at the confirm prompt. What is left is a wording mismatch between the doc and the code, or a policy change to the routing. Neither shows a separate harmful behavior.

- Message: chupa-test-gates attempt 2 journaled `routed: reject_queue` with premise_bounce 2 and one draw, while the snapshot shows the stem unheld.
- Open ticket confirm-note-reofferable-stem: a premise_failed stem with premise_bounce budget left is in the Reject queue, `drain.reofferable` is true, and the drain re-offers it with no keep. A confirm-made keep resets caps, so the ticket adds a preview line that warns about this.
- Decision 000101 shows the drain already treats premise parks differently from Reject-queue holds (render_over_bound is not routed to the Reject queue), so the routing is deliberate code, not a missing path.

Message: box-000352-17213bc9
