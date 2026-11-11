---
id: declined-box-000403-d925564b
kind: declined
link: box-000403-d925564b
reopen_after_days: 60
---
One sentence in docs/how-chupa-works.md (line 459, the serve paragraph) is out of date. It says serve holds a premise-parked ticket until the ticket's committed content changes. Since the merged ticket confirm-releases-premise-park, an operator keep also releases that hold. The implementing run could not fix the sentence because the file was outside its scope fence.

This is a gap in documentation only, and nothing in it causes wrong runtime behavior. The code change already merged: drain.parked_blob now releases a premise park after an operator keep. The same doc's section on premise parks (around line 441) already tells the operator that an operator confirm releases a premise park routed to the Reject queue. That leaves one stale sentence in one place. It is also not wrong advice: editing the ticket still releases the park, so an operator who follows it still gets unstuck. It only leaves out the other release. That is a wording fix, not a harmful behavior gap that needs a ticket. Reopen if an operator or a model-driven stage shows it was misled by line 459, for example by editing a ticket instead of confirming it and losing work or cap budget. Also reopen if a later ticket that edits that section of how-chupa-works.md needs this correction in its fence.

- docs/how-chupa-works.md:459 says serve 'holds a premise-parked ticket until its committed content changes'
- docs/how-chupa-works.md:441-443 already says only an operator `confirm` releases a Reject-queue premise park
- tickets/confirm-releases-premise-park/ticket.md:24-27 changed drain.parked_blob so an operator keep releases the park; the stem is in the merged set
- The message reports stage implement, outcome ok, and names no runtime failure

Message: box-000403-d925564b
