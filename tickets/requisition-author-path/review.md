# Review: snag

The hooks are wired correctly, but the author review approves the draft-stamped candidate while the commit writes text with its resolved start state, so a ticket that resolves to a non-draft state commits text that no `approve` verdict covers and journals a ticket_sha that does not match the committed blob.

## Findings

- [logic] chupa/author.py:127 review_author reviews `stamp(..., "state", "draft")`, and review_ticket hashes that text as ticket_sha. After approval, author() restamps the text with `start_state(...)`, which returns `config.box_policy[row]` (for example `confirmed`) when go binds and the fence avoids the safety inventory, and commits that text. The committed blob then differs from the reviewed text. The journaled `requisition_verdict` ticket_sha names text that was never committed, which breaks the rejection rule 'a box-authored ticket commits without an approve verdict for its committed text'. (do instead: Inside the review hook, resolve the final text before calling review_ticket: run validate_ticket on the provisional stamp, then start_state, then the final stamp. Review exactly that text and commit the same reviewed text, for example by keeping it beside the verdict in `reviewed`, so the ticket_sha equals the committed blob. Add a test in which start_state resolves non-draft and assert that the journaled ticket_sha equals `git rev-parse HEAD:<ticket path>`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "dcdb2f6c03781db81df80dc9e006cf1302e2f3de",
  "stem": "requisition-author-path",
  "reviewed_sha": "dcdb2f6c03781db81df80dc9e006cf1302e2f3de",
  "summary": "The hooks are wired correctly, but the author review approves the draft-stamped candidate while the commit writes text with its resolved start state, so a ticket that resolves to a non-draft state commits text that no `approve` verdict covers and journals a ticket_sha that does not match the committed blob.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/author.py",
      "line": 127,
      "message": "review_author reviews `stamp(..., \"state\", \"draft\")`, and review_ticket hashes that text as ticket_sha. After approval, author() restamps the text with `start_state(...)`, which returns `config.box_policy[row]` (for example `confirmed`) when go binds and the fence avoids the safety inventory, and commits that text. The committed blob then differs from the reviewed text. The journaled `requisition_verdict` ticket_sha names text that was never committed, which breaks the rejection rule 'a box-authored ticket commits without an approve verdict for its committed text'.",
      "paved_road": "Inside the review hook, resolve the final text before calling review_ticket: run validate_ticket on the provisional stamp, then start_state, then the final stamp. Review exactly that text and commit the same reviewed text, for example by keeping it beside the verdict in `reviewed`, so the ticket_sha equals the committed blob. Add a test in which start_state resolves non-draft and assert that the journaled ticket_sha equals `git rev-parse HEAD:<ticket path>`."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
