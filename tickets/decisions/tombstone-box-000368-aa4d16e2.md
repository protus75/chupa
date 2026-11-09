---
id: tombstone-box-000368-aa4d16e2
kind: tombstone
link: review-alongside-drain
reopen_after_days: 30
---
When serve or drain holds the checkout lock, `chupa review` refuses with LockHeld. A chat session therefore cannot run the required review-until-approve loop on a ticket it has just edited. The note asks for review to run without the lock or to go through serve's control inbox.

Merged ticket review-alongside-drain, with review-lock-only-for-intake before it, already covers this lock conflict. Review now holds the checkout lock only during intake. Reviewing a committed, unchanged ticket skips the lock completely, so it runs alongside a drain or serve. A ticket with uncommitted edits still needs intake, which writes to git. For that case the ticket chose on purpose to refuse with a paved road: wait for the running engine's intake to commit the ticket, or stop the engine, then retry. That ticket also explicitly scoped out the alternative this note proposes, running review as an engine control request. The claim that 'review writes nothing to the checkout' is wrong for an edited ticket, because intake commits it. The note is a restatement of a gap that has already been decided, not a new behavior gap.

- tickets/review-alongside-drain/ticket.md Goal: reviewing a committed, unchanged ticket skips intake and never takes the checkout lock, so it runs next to a drain; a pending change refuses with a fix the operator can follow
- tickets/review-alongside-drain/ticket.md Scope out: 'running review as an engine control request'
- tickets/review-lock-only-for-intake/ticket.md: review holds the checkout lock only for intake; journal appends use their own journal.lock
- Both stems are in the merged set

Message: box-000368-aa4d16e2
