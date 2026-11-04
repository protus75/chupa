# Review: snag

The attempts cap and new defaults are implemented, but the new premise_bounce default breaks the real shakeout member while a test patch hides it, and the new `_admit` check gives settled stems a dead-end refusal.

## Findings

- [acceptance] tests/test_shakeout.py:220 The test monkeypatches `Bench.initialize` to set `premise_bounce: 2`, so `premise_park_release` passes only in this test. The real member in `eval/shakeout/drain.py` still runs on the shipped default of 1 through `eval.shakeout.run`. There, the first `premise_failed` spends the cap and routes the stem to Reject. `_next` then never re-offers it after the ticket edit, so `assert stem in released.merged` fails and the battery goes red. (do instead: Remove the monkeypatch and set `premise_bounce: 2` inside `_premise_park_release` with `bench.configure`, as other members already override caps. `eval/` is outside this ticket's Scope fence, so a human must widen the fence to include `eval/shakeout/drain.py` before this can land.)
- [logic] chupa/runner.py:722 The attempts-spent refusal in `_admit` runs before the already-merged and non-confirmed state checks. A merged or otherwise settled stem with five or more failed terminals in its lineage is told to run drain and then `confirm`. `_settle` skips settled stems, so it is never routed, and `confirm` then refuses because the stem is not in the Reject queue. The operator should have received the existing 'already merged' refusal and its road to author a new stem. (do instead: Move the attempts check below the merged and `state != confirmed` refusals in `_admit`, and add a test that runs a merged stem with five prior failures and expects the 'already merged' refusal.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "c7c53f9d9835eef2a4aeffc05d650631faf6a8b2",
  "stem": "attempts-cap",
  "reviewed_sha": "c7c53f9d9835eef2a4aeffc05d650631faf6a8b2",
  "summary": "The attempts cap and new defaults are implemented, but the new premise_bounce default breaks the real shakeout member while a test patch hides it, and the new `_admit` check gives settled stems a dead-end refusal.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_shakeout.py",
      "line": 220,
      "message": "The test monkeypatches `Bench.initialize` to set `premise_bounce: 2`, so `premise_park_release` passes only in this test. The real member in `eval/shakeout/drain.py` still runs on the shipped default of 1 through `eval.shakeout.run`. There, the first `premise_failed` spends the cap and routes the stem to Reject. `_next` then never re-offers it after the ticket edit, so `assert stem in released.merged` fails and the battery goes red.",
      "paved_road": "Remove the monkeypatch and set `premise_bounce: 2` inside `_premise_park_release` with `bench.configure`, as other members already override caps. `eval/` is outside this ticket's Scope fence, so a human must widen the fence to include `eval/shakeout/drain.py` before this can land.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/runner.py",
      "line": 722,
      "message": "The attempts-spent refusal in `_admit` runs before the already-merged and non-confirmed state checks. A merged or otherwise settled stem with five or more failed terminals in its lineage is told to run drain and then `confirm`. `_settle` skips settled stems, so it is never routed, and `confirm` then refuses because the stem is not in the Reject queue. The operator should have received the existing 'already merged' refusal and its road to author a new stem.",
      "paved_road": "Move the attempts check below the merged and `state != confirmed` refusals in `_admit`, and add a test that runs a merged stem with five prior failures and expects the 'already merged' refusal.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.1",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
