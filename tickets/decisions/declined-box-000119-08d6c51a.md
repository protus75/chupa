---
id: declined-box-000119-08d6c51a
kind: declined
link: box-000119-08d6c51a
reopen_after_days: 60
---
When merge builds the `Candidate` that its gates check (`chupa/merge.py:208-209`), it reads `tickets/<stem>/ticket.md` and `review.md` from the main checkout's working tree, not from main's committed blobs. An uncommitted edit to either file in the shared main checkout is therefore checked as if it were on main. The note proposes reading them with `git show main:<path>`.

The code matches the note: `ticket_text=(ctx.repo / ticket_path(stem)).read_text()` and `review_text=review_md.read_text()` read files from disk. To cause harm, though, someone has to leave an uncommitted edit to that stem's ticket.md or review.md in the main checkout at the moment its merge runs. The likely result of that is a refusal that should not have happened, for example a ticket that is half-edited and fails validation, or an approval pin that does not match. That fails closed, and the operator can recover by committing or reverting the edit. Letting unapproved code through would need someone to hand-forge review.md in the working tree on purpose. This bootstrap-ingest note cites no incident in which a merge was wrongly admitted or wrongly refused because of working-tree content. It is speculative hardening, with no demonstrated runtime failure behind it.

- chupa/merge.py:208 reads ticket_text from the working-tree file `ctx.repo / ticket_path(stem)`
- chupa/merge.py:209 reads review_text with `review_md.read_text()` when the file exists
- chupa/merge.py:121-130 judges the approval from `artifact.review_text`
- origin is bootstrap-ingest, and no journal or run artifact shows a merge decided by uncommitted ticket-plane content
- the open ticket merge-guard-staged-outside-branch covers staged paths in the main checkout but not unstaged edits to the ticket plane, so this note is not a duplicate

Message: box-000119-08d6c51a
