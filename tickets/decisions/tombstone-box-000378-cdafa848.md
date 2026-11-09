---
id: tombstone-box-000378-cdafa848
kind: tombstone
link: author-spec-ticket-rules
reopen_after_days: 30
---
The Author stage spent all 4 calls on claude-effort-flag (author run 6, attempt 61) and failed on ticket rules the project already states: it wrote prose in `## Context`, wrote `gate_bypass` as a boolean, and left the fixture `hosts/fixture/bin/claude` out of the fence. The note blames `chupa/specs/author.md`: it never points the author to the host-authoring rules or the skeleton, and it lists `gate_bypass` without a type. It asks the spec to bind the author to those rules and to stop the author writing `gate_bypass`.

This repeats the merged ticket author-spec-ticket-rules. That ticket cites the same incident (author run 6, attempt 61, claude-effort-flag, `gate_bypass: false`, prose in Context, the dropped `hosts/fixture/bin/claude` fence entry) and names the same cause in `chupa/specs/author.md`. It changed that spec so the author prompt states the section rules and frontmatter keys, the author never writes `gate_bypass`, and each re-prompt carries the author's previous reply. Commit 30f18c9e merged it.

- Merged stems include author-spec-ticket-rules; commit 30f18c9e touches chupa/specs/author.md
- tickets/author-spec-ticket-rules/ticket.md Goal cites author run 6, attempt 61, claude-effort-flag, gate_bypass: false, prose in Context, dropped hosts/fixture/bin/claude
- That ticket's outcome list: the author prompt states the section rules and exact frontmatter keys, and the author never writes gate_bypass

Message: box-000378-cdafa848
