---
id: tombstone-box-000226-4afeebda
kind: tombstone
link: declined-box-000071-0db3090f
reopen_after_days: 90
---
Claude's read-only surfaces (review and author) start in the main checkout, not in the ticket's worktree, so Review can see the change only as the diff in its prompt. The note asks plan section 6 to say which tree a read-only reviewer may browse, and suggests the ticket worktree.

Registry record declined-box-000071-0db3090f already decided this same note: same surfaces, same main-checkout working directory, same diff-only view, and the same request to pin the browsable tree in section 6. The note reports no new evidence that a reviewer has produced a wrong verdict because of where it runs.

- declined-box-000071-0db3090f describes the same gap: read-only surfaces run with cwd set to the main checkout, review sees only the rendered diff, and the note asks section 6 to name the browsable tree
- The message comes from bootstrap-ingest with no stage, outcome, or report attached, so it adds no new failure evidence

Message: box-000226-4afeebda
