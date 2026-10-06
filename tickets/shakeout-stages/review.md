# Review: snag

The six stage members run green and the gates pass, but `scope_escape` drops the drain report and never checks that nothing merges, which is part of its named observable.

## Findings

- [acceptance] eval/shakeout/stages.py:93 The ticket's observable for `scope_escape` is: the first terminal is `gate_failed` at `check`, `checks.json` names the escaped path, AND nothing merges. The member calls `await bench.drain()` and throws away the `Report`, so it never checks the merge outcome. If a regression let the retried out-of-fence branch merge, this member would still report green. (do instead: Bind `report = await bench.drain()` and add `assert stem not in report.merged`, the same way `_review_reject_reentry` and `_base_diff_attribution` check `report.merged`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "a7132c4ecbde9a372d591dce0a889a7f639aafa0",
  "stem": "shakeout-stages",
  "reviewed_sha": "a7132c4ecbde9a372d591dce0a889a7f639aafa0",
  "summary": "The six stage members run green and the gates pass, but `scope_escape` drops the drain report and never checks that nothing merges, which is part of its named observable.",
  "findings": [
    {
      "code": "acceptance",
      "path": "eval/shakeout/stages.py",
      "line": 93,
      "message": "The ticket's observable for `scope_escape` is: the first terminal is `gate_failed` at `check`, `checks.json` names the escaped path, AND nothing merges. The member calls `await bench.drain()` and throws away the `Report`, so it never checks the merge outcome. If a regression let the retried out-of-fence branch merge, this member would still report green.",
      "paved_road": "Bind `report = await bench.drain()` and add `assert stem not in report.merged`, the same way `_review_reject_reentry` and `_base_diff_attribution` check `report.merged`."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
