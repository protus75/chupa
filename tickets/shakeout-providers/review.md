# Review: snag

The provider classification and driver mapping are correct, but the diff edits eval/shakeout/bench.py, and the ticket's Scope out explicitly excludes any bench edit beyond GROUPS.

## Findings

- [scope] eval/shakeout/bench.py:92 Bench.configure gains new `llm`, `process` and `env` keyword overrides, and GroupExec is now imported. The ticket's Scope out excludes "any runner, bench, or schema edit beyond `GROUPS`", so this is a bench edit outside the allowed work, even though the eval/shakeout/ fence covers the path. (do instead: Revert eval/shakeout/bench.py. In eval/shakeout/providers.py, use the existing Bench API to set the bench's llm, process and env attributes before calling the unchanged `bench.configure(config)`. That method already rebuilds the checkout and the pipeline from `self.llm`. If a bench API change is truly needed, reply premise_failed and file it as a second problem.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "1f5d0cfd379a2f7002061fa734ed0b53f050ec70",
  "stem": "shakeout-providers",
  "reviewed_sha": "1f5d0cfd379a2f7002061fa734ed0b53f050ec70",
  "summary": "The provider classification and driver mapping are correct, but the diff edits eval/shakeout/bench.py, and the ticket's Scope out explicitly excludes any bench edit beyond GROUPS.",
  "findings": [
    {
      "code": "scope",
      "path": "eval/shakeout/bench.py",
      "line": 92,
      "message": "Bench.configure gains new `llm`, `process` and `env` keyword overrides, and GroupExec is now imported. The ticket's Scope out excludes \"any runner, bench, or schema edit beyond `GROUPS`\", so this is a bench edit outside the allowed work, even though the eval/shakeout/ fence covers the path.",
      "paved_road": "Revert eval/shakeout/bench.py. In eval/shakeout/providers.py, use the existing Bench API to set the bench's llm, process and env attributes before calling the unchanged `bench.configure(config)`. That method already rebuilds the checkout and the pipeline from `self.llm`. If a bench API change is truly needed, reply premise_failed and file it as a second problem."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
