# Review: snag

The commit lock and its wiring into git.py and the composition roots are correct, but the shared test helper leaves a new directory under /tmp every time a lock is acquired, and the unit test cannot tell one hold from several, so it does not check that staging and the commit share one hold.

## Findings

- [logic] tests/integration/test_git.py:24 The shared `commit_lock()` helper builds each `CommitLock` at a fresh `/tmp/chupa-test-<uuid>`. That path is hard-coded and sits outside pytest's tmp_path. Every `Git.add`, `commit`, `restore` or `merge_squash` in the integration tests and harnesses calls `acquire`, which runs `mkdir` and creates `commit.lock` there, and nothing removes either. Each `./dev.py test` run therefore leaves hundreds of directories in /tmp, and running the harnesses leaves more. (do instead: Have the helper take the directory the lock lives in, such as the test's tmp_path or the repo's `.chupa/state`, and pass it from each caller. If a caller has no tmp_path, root the lock under a directory pytest or the harness already cleans up. Do not hard-code /tmp.)
- [logic] tests/unit/test_commit_lock.py:135 Acceptance 1 requires every git call `Git.commit(..., only=paths)` makes to run inside one hold, and both steps of `merge_squash` to run inside one hold. The fake `Lock` only records whether a lock was held when each call ran. It does not count enters or exits, so a regression that takes and releases the lock separately around `update-index` and `commit` would still record `True` for every call and pass. That gap between staging and committing is the race this ticket exists to close. (do instead: Have the fake lock count `__aenter__` calls, or record a hold id for each call. Then assert that `commit(only=...)` makes exactly one enter covering `update-index`, `diff`, `commit` and `rev-parse`, and that `merge_squash` makes exactly one enter covering `merge` and its commit.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "3d3d48e46c73e5d5d8685737bdd73928db99f8fd",
  "stem": "commit-lock",
  "reviewed_sha": "3d3d48e46c73e5d5d8685737bdd73928db99f8fd",
  "summary": "The commit lock and its wiring into git.py and the composition roots are correct, but the shared test helper leaves a new directory under /tmp every time a lock is acquired, and the unit test cannot tell one hold from several, so it does not check that staging and the commit share one hold.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/integration/test_git.py",
      "line": 24,
      "message": "The shared `commit_lock()` helper builds each `CommitLock` at a fresh `/tmp/chupa-test-<uuid>`. That path is hard-coded and sits outside pytest's tmp_path. Every `Git.add`, `commit`, `restore` or `merge_squash` in the integration tests and harnesses calls `acquire`, which runs `mkdir` and creates `commit.lock` there, and nothing removes either. Each `./dev.py test` run therefore leaves hundreds of directories in /tmp, and running the harnesses leaves more.",
      "paved_road": "Have the helper take the directory the lock lives in, such as the test's tmp_path or the repo's `.chupa/state`, and pass it from each caller. If a caller has no tmp_path, root the lock under a directory pytest or the harness already cleans up. Do not hard-code /tmp.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "tests/unit/test_commit_lock.py",
      "line": 135,
      "message": "Acceptance 1 requires every git call `Git.commit(..., only=paths)` makes to run inside one hold, and both steps of `merge_squash` to run inside one hold. The fake `Lock` only records whether a lock was held when each call ran. It does not count enters or exits, so a regression that takes and releases the lock separately around `update-index` and `commit` would still record `True` for every call and pass. That gap between staging and committing is the race this ticket exists to close.",
      "paved_road": "Have the fake lock count `__aenter__` calls, or record a hold id for each call. Then assert that `commit(only=...)` makes exactly one enter covering `update-index`, `diff`, `commit` and `rev-parse`, and that `merge_squash` makes exactly one enter covering `merge` and its commit.",
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
