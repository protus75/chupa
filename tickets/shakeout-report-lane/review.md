# Review: snag

The engine and runner changes are mostly in place, but tests for acceptance criteria 1, 2 and 5 and part of criterion 3 are missing, and `Bench.configure` does not rebuild what the ticket requires.

## Findings

- [acceptance] tests/test_stages.py:- The diff does not touch tests/test_stages.py. Nothing proves criterion 1: a valid shakeout-report.json lifting in the checks commit, a schema-invalid report making the Check gate_failed with neither file committed, and the implement-terminal lift leaving a registered artifact unlifted. Nothing proves criterion 2 either: a stale outbox report deleted before Verification runs, and a Verification that names tickets/<stem>/shakeout-report.json but leaves none failing with code verification even when every command is otherwise excused. (do instead: Add tests to tests/test_stages.py that drive `check` and the implement-terminal `lift_outbox` through the existing stage fixtures, one test for each behavior in criteria 1 and 2.)
- [acceptance] tests/test_shakeout.py:37 Criterion 3 asks for a proof that `produce` refuses when a re-run prior member's `observed` differs from the prior entry. No test covers that branch. The only refusal tested is a missing prior entry. (do instead: Add a test that builds a prior report whose entry for the earlier member has a different `observed` value (or a member whose re-run returns a different observation), then asserts `produce` raises ShakeoutRefused naming that member.)
- [acceptance] tests/test_shakeout.py:60 Criterion 5 is unmet. No test proves `Bench.configure` keeps the journal, clock, repo and scripted model while changing a config cap. No test runs `python -m eval.shakeout.run --group nope --out x.json` and asserts exit code 2. (do instead: Add a test that configures a Bench with a parsed config that changes one cap and asserts the journal, clock, root and llm objects are the same ones afterward and the cap changed. Add a test that runs the module command through the process seam (or calls `main` with those argv) and asserts it returns 2.)
- [logic] eval/shakeout/bench.py:87 `configure` mutates the caller's parsed config in place. It does not rebuild the runner, drain, log or pipeline factory the ticket names, and `self.journal = self.journal` is a no-op. Its only effect is swapping `self.config` and rebuilding the redactor, so it fails the ticket's 'rebuilds the production runner, drain, redactor, log, and pipeline factory' contract. (do instead: Build a copy of the config with `state_dir`/`worktree_root` replaced (for example with `model_copy(update=...)`), then rebuild every production component the bench holds from that copy. Drop the self-assignment.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f38a467e6b3f832963e91056d8ad380966d9a5a8",
  "stem": "shakeout-report-lane",
  "reviewed_sha": "f38a467e6b3f832963e91056d8ad380966d9a5a8",
  "summary": "The engine and runner changes are mostly in place, but tests for acceptance criteria 1, 2 and 5 and part of criterion 3 are missing, and `Bench.configure` does not rebuild what the ticket requires.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_stages.py",
      "line": null,
      "message": "The diff does not touch tests/test_stages.py. Nothing proves criterion 1: a valid shakeout-report.json lifting in the checks commit, a schema-invalid report making the Check gate_failed with neither file committed, and the implement-terminal lift leaving a registered artifact unlifted. Nothing proves criterion 2 either: a stale outbox report deleted before Verification runs, and a Verification that names tickets/<stem>/shakeout-report.json but leaves none failing with code verification even when every command is otherwise excused.",
      "paved_road": "Add tests to tests/test_stages.py that drive `check` and the implement-terminal `lift_outbox` through the existing stage fixtures, one test for each behavior in criteria 1 and 2."
    },
    {
      "code": "acceptance",
      "path": "tests/test_shakeout.py",
      "line": 37,
      "message": "Criterion 3 asks for a proof that `produce` refuses when a re-run prior member's `observed` differs from the prior entry. No test covers that branch. The only refusal tested is a missing prior entry.",
      "paved_road": "Add a test that builds a prior report whose entry for the earlier member has a different `observed` value (or a member whose re-run returns a different observation), then asserts `produce` raises ShakeoutRefused naming that member."
    },
    {
      "code": "acceptance",
      "path": "tests/test_shakeout.py",
      "line": 60,
      "message": "Criterion 5 is unmet. No test proves `Bench.configure` keeps the journal, clock, repo and scripted model while changing a config cap. No test runs `python -m eval.shakeout.run --group nope --out x.json` and asserts exit code 2.",
      "paved_road": "Add a test that configures a Bench with a parsed config that changes one cap and asserts the journal, clock, root and llm objects are the same ones afterward and the cap changed. Add a test that runs the module command through the process seam (or calls `main` with those argv) and asserts it returns 2."
    },
    {
      "code": "logic",
      "path": "eval/shakeout/bench.py",
      "line": 87,
      "message": "`configure` mutates the caller's parsed config in place. It does not rebuild the runner, drain, log or pipeline factory the ticket names, and `self.journal = self.journal` is a no-op. Its only effect is swapping `self.config` and rebuilding the redactor, so it fails the ticket's 'rebuilds the production runner, drain, redactor, log, and pipeline factory' contract.",
      "paved_road": "Build a copy of the config with `state_dir`/`worktree_root` replaced (for example with `model_copy(update=...)`), then rebuild every production component the bench holds from that copy. Drop the self-assignment."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
