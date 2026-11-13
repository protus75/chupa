---
id: declined-box-000432-6db34da4
kind: declined
link: box-000432-6db34da4
reopen_after_days: 30
---
The note proposes a new 'Splitting and ordering' section for the host authoring guide (chupa/docs/host-authoring.md). The section would say when a request becomes several tickets: pieces with fences that don't overlap and that don't use each other's output get separate tickets. Each deliverable would be marked ticket, defer or reject. Foundation tickets would be written before the tickets that use them, and an enforcement check would get its own ticket that depends on the feature. The idea comes from the fungo host on 2026-11-13.

This is guidance wording that cites no chupa incident. No run is named where one ticket bundled independent pieces and cross-wired them, or where a bad piece sank good ones. With no reachable harmful runtime behavior, it fails the admission bar. The guide already covers part of the ordering question: its Runs before entry says to use that soft order, not Depends on, for ordering that is not a code dependency. Registry record declined-box-000431-caf1a286 declined a similar fungo-sourced authoring-guide rule for the same reason. This is not a tombstone, because no open or merged ticket covers splitting guidance. Reopen if a chupa run record or retro shows a bundled ticket whose independent pieces broke each other, or one piece failing and taking down a mergeable sibling.

- The message says 'No chupa incident cited yet.'
- chupa/docs/host-authoring.md has no splitting or independence guidance; its only ordering text is at lines 36-37 (Runs before as a soft, non-blocking order, not Depends on).
- declined-box-000431-caf1a286 declined another fungo-sourced host-authoring rule (narrow test fences) because it cited no incident.
- No open ticket or merged stem covers how to split tickets into pieces.

Message: box-000432-6db34da4
