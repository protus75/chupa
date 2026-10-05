# Review: snag

The runtime dispatch, the closed vocabulary and the lessons render look correct, but one cap test drops its ordering check entirely instead of making the named adjacency change, and the marker test does not cover every later render.

## Findings

- [acceptance] tests/test_caps.py:101 test_other_terminals_draw_only_when_infra used to assert that the infra draw lands right before the terminal (`events[-2]`). The diff replaces that with a search that finds the first infra `cap_consumed` anywhere in the journal, so the ordering check is gone. The ticket allows exactly one change to adjacency assertions: the infra draw 'precedes it, with only this terminal's diagnosis events between'. Anything weaker breaks criterion 7 and the 'assertion weakened' reject rule. In the timeout case the stage seam creates no worktree, so the events between the draw and the terminal should be exactly the one mechanical `diagnosis` signal ('workspace gone'), and the new assertion no longer checks that. (do instead: Find the infra draw's index and the terminal's index (`events[-1]`). Assert the infra draw comes before the terminal, and that every event between them is this terminal's diagnosis signal (here exactly `[SIGNAL diagnosis]`). That keeps the original ordering guarantee with only the adaptation the ticket names.)
- [acceptance] tests/test_diagnose.py:176 Criterion 6 requires the unique marker from attempt one's spooled output to appear in no later render. The test checks the marker only in renders[2], and only inside the prior-attempts block between the criteria and the next section. renders[1] is the immediately-prior render, where the raw harvest `reason`/tails used to appear, and it is never checked for the marker. The full prompts are never checked either. (do instead: Assert `marker not in r.rendered` for every implement request after the first (renders[1] and renders[2], whole rendered prompt), alongside the existing checks that the lessons appear.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "6a4a63c7f02129e24a1b6f3ed46c43d0d598a382",
  "stem": "spine-diagnosis",
  "reviewed_sha": "6a4a63c7f02129e24a1b6f3ed46c43d0d598a382",
  "summary": "The runtime dispatch, the closed vocabulary and the lessons render look correct, but one cap test drops its ordering check entirely instead of making the named adjacency change, and the marker test does not cover every later render.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_caps.py",
      "line": 101,
      "message": "test_other_terminals_draw_only_when_infra used to assert that the infra draw lands right before the terminal (`events[-2]`). The diff replaces that with a search that finds the first infra `cap_consumed` anywhere in the journal, so the ordering check is gone. The ticket allows exactly one change to adjacency assertions: the infra draw 'precedes it, with only this terminal's diagnosis events between'. Anything weaker breaks criterion 7 and the 'assertion weakened' reject rule. In the timeout case the stage seam creates no worktree, so the events between the draw and the terminal should be exactly the one mechanical `diagnosis` signal ('workspace gone'), and the new assertion no longer checks that.",
      "paved_road": "Find the infra draw's index and the terminal's index (`events[-1]`). Assert the infra draw comes before the terminal, and that every event between them is this terminal's diagnosis signal (here exactly `[SIGNAL diagnosis]`). That keeps the original ordering guarantee with only the adaptation the ticket names."
    },
    {
      "code": "acceptance",
      "path": "tests/test_diagnose.py",
      "line": 176,
      "message": "Criterion 6 requires the unique marker from attempt one's spooled output to appear in no later render. The test checks the marker only in renders[2], and only inside the prior-attempts block between the criteria and the next section. renders[1] is the immediately-prior render, where the raw harvest `reason`/tails used to appear, and it is never checked for the marker. The full prompts are never checked either.",
      "paved_road": "Assert `marker not in r.rendered` for every implement request after the first (renders[1] and renders[2], whole rendered prompt), alongside the existing checks that the lessons appear."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
