---
id: tombstone-box-000211-4198a97b
kind: tombstone
link: declined-box-000037-20f6edc5
reopen_after_days: 90
---
The frozen plan gives gates that run at authoring time their own severity, soft by default, but `chupa/gates.py` has only the merge-context severity map. The note asks for an author-context severity constant plus its first author-time gate consumer, such as requisition review or the ticket schema check.

Registry record declined-box-000037-20f6edc5 already covers this request: an author-context severity constant in gates.py, wired to a first author-time consumer (requisition review or the ticket schema check). The incoming message is a near-verbatim duplicate from the same bootstrap ingest, and it adds no new evidence of a harmful runtime gap.

- declined-box-000037-20f6edc5 covers the same request: an author-context soft severity constant in chupa/gates.py, with requisition_review or ticket_schema as the first consumer.
- The message gives no failure, outcome, or incident showing incorrect runtime behavior. Its origin is bootstrap-ingest.

Message: box-000211-4198a97b
