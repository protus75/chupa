# Review: snag

The test meets most of the ticket, but the size-limit message says "Compress" with a capital C, so it does not contain `compress` as acceptance criterion 2 requires; the test hides this by matching `[Cc]ompress`.

## Findings

- [acceptance] tests/integration/test_hostfiles.py:32 Acceptance criterion 2 requires the AssertionError message for an 8193-byte template to contain `compress`. The message is "Compress existing rules or move host-specific ones to the project's own rules outside the managed block". A case-sensitive substring check for `compress` does not match it. (do instead: Use the lowercase word in the message, for example "Template too large: compress existing rules or move host-specific ones to the project's own rules outside the managed block".)
- [acceptance] tests/integration/test_hostfiles.py:40 The boundary test uses `match="[Cc]ompress"`, which accepts the capital-C message. So the test passes even though the message does not contain `compress` as acceptance criterion 2 requires. (do instead: Change the match to `match="compress"` so the test checks the exact substring the criterion names.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "2f5d29094b38927081850cb3c9b3aca07f43ae7a",
  "stem": "core-template-budget",
  "reviewed_sha": "2f5d29094b38927081850cb3c9b3aca07f43ae7a",
  "summary": "The test meets most of the ticket, but the size-limit message says \"Compress\" with a capital C, so it does not contain `compress` as acceptance criterion 2 requires; the test hides this by matching `[Cc]ompress`.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/integration/test_hostfiles.py",
      "line": 32,
      "message": "Acceptance criterion 2 requires the AssertionError message for an 8193-byte template to contain `compress`. The message is \"Compress existing rules or move host-specific ones to the project's own rules outside the managed block\". A case-sensitive substring check for `compress` does not match it.",
      "paved_road": "Use the lowercase word in the message, for example \"Template too large: compress existing rules or move host-specific ones to the project's own rules outside the managed block\".",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/integration/test_hostfiles.py",
      "line": 40,
      "message": "The boundary test uses `match=\"[Cc]ompress\"`, which accepts the capital-C message. So the test passes even though the message does not contain `compress` as acceptance criterion 2 requires.",
      "paved_road": "Change the match to `match=\"compress\"` so the test checks the exact substring the criterion names.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
