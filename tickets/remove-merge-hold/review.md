# Review: snag

The code change removes the supervised merge hold correctly, but docs/host-contract.md's Pending cutover contract still describes supervised host merge confirms.

## Findings

- [acceptance] docs/host-contract.md:- Acceptance criterion 5 requires that docs/host-contract.md no longer describe a supervised merge hold. The diff rewrites only item 4 of the "Pending cutover contract". Item 1 still reads "Unattended bootstrap self-build continues through Phase 6 under drain's safety envelope; it never waits for supervised host merge confirms." That sentence says host merges under serve wait for an operator confirm, which is no longer true. (do instead: Reword item 1 so it no longer contrasts drain with supervised host merge confirms. For example: serve and drain both merge green candidates without an operator confirm. Keep the rest of the section consistent with the rewritten item 4.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "e7679fbed4beb0aa9ac9a45894c1b41183e8679b",
  "stem": "remove-merge-hold",
  "reviewed_sha": "e7679fbed4beb0aa9ac9a45894c1b41183e8679b",
  "summary": "The code change removes the supervised merge hold correctly, but docs/host-contract.md's Pending cutover contract still describes supervised host merge confirms.",
  "findings": [
    {
      "code": "acceptance",
      "path": "docs/host-contract.md",
      "line": null,
      "message": "Acceptance criterion 5 requires that docs/host-contract.md no longer describe a supervised merge hold. The diff rewrites only item 4 of the \"Pending cutover contract\". Item 1 still reads \"Unattended bootstrap self-build continues through Phase 6 under drain's safety envelope; it never waits for supervised host merge confirms.\" That sentence says host merges under serve wait for an operator confirm, which is no longer true.",
      "paved_road": "Reword item 1 so it no longer contrasts drain with supervised host merge confirms. For example: serve and drain both merge green candidates without an operator confirm. Keep the rest of the section consistent with the rewritten item 4.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.3",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
