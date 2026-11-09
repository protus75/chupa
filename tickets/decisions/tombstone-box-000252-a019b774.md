---
id: tombstone-box-000252-a019b774
kind: tombstone
link: reject-queue-verbs
reopen_after_days: 30
---
Section 11.2 says the re-offer fold should record a cap-spent park as a releasable arrival in the Reject queue (`routed: reject_queue`). This bootstrap note says the drain only reports such a park, and that until the Phase 2 Reject queue and auto-keep exist, the only way forward is to fix the plan or ticket and author a successor.

This note raises the same gap as registry record tombstone-box-000136-eafeff77: a cap-spent park was reported but never journaled as a Reject-queue arrival. That record was closed against the merged ticket `reject-queue-verbs`. The Reject queue has since shipped, the terminal handler marks cap-spent runs as Reject-queue arrivals, and those arrivals can be released. The note describes no remaining defect.

- Registry record tombstone-box-000136-eafeff77 covers the same cap-spent park / `routed: reject_queue` gap and links it to `reject-queue-verbs`.
- `reject-queue-verbs` is in the merged stems list.
- `escalation-ladder` (the Phase 2 auto-keep the note was waiting for) is also merged.

Message: box-000252-a019b774
