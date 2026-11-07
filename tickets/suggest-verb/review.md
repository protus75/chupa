# Review: snag

The verb, intake, dev subcommand, and docs all meet the ticket, but the new lock-held CLI test starts a separate Python process to hold the writer lock.

## Findings

- [logic] tests/test_cli.py:834 test_suggest_publishes_while_writer_lock_is_held starts a child process with subprocess.Popen to hold the writer lock. A unit test must not start a process, and this one also hand-copies the flock logic instead of using chupa's Lockfile. (do instead: Hold the lock in-process the way the existing tests do (e.g. tests/test_cli.py:383 and :597): `holder = Lockfile(root / ".chupa/state", instance_id="other", clock=Clock()); holder.acquire()`, run `cli(root, "suggest", ...)`, then release it in `finally`. flock is per open file, so suggest would still fail or block if it tried to take the lock.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "2df8c9da2b871d355ada34ba25fdb1eadad9fce9",
  "stem": "suggest-verb",
  "reviewed_sha": "2df8c9da2b871d355ada34ba25fdb1eadad9fce9",
  "summary": "The verb, intake, dev subcommand, and docs all meet the ticket, but the new lock-held CLI test starts a separate Python process to hold the writer lock.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/test_cli.py",
      "line": 834,
      "message": "test_suggest_publishes_while_writer_lock_is_held starts a child process with subprocess.Popen to hold the writer lock. A unit test must not start a process, and this one also hand-copies the flock logic instead of using chupa's Lockfile.",
      "paved_road": "Hold the lock in-process the way the existing tests do (e.g. tests/test_cli.py:383 and :597): `holder = Lockfile(root / \".chupa/state\", instance_id=\"other\", clock=Clock()); holder.acquire()`, run `cli(root, \"suggest\", ...)`, then release it in `finally`. flock is per open file, so suggest would still fail or block if it tried to take the lock.",
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
