# Review: snag

The Author stage, triage wiring, spec and eval-harness change are correct, but the new ls_files test does not prove acceptance criterion 6: it never shows that an untracked file is left out.

## Findings

- [acceptance] tests/test_git.py:137 Acceptance criterion 6 requires `tests/test_git.py` to prove that `ls_files` lists a committed file and leaves out an untracked one. `test_ls_files_parses_tracked_paths_only` feeds canned stdout to a FakeExec and only checks that `splitlines` parses it. No repository exists, so nothing is committed and nothing is untracked. The test would still pass if `ls_files` ran `ls-files --others` or any command that lists untracked files, so it cannot fail on the behavior the criterion names. (do instead: Add a test that uses a real repo, following the existing `test_git_common_dir_resolves_main_and_linked_worktree(tmp_path)`: init a repo in tmp_path, commit one file, write a second file without adding it, then assert that `ls_files` returns the committed path and not the untracked one. The argv parametrize row can stay.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "2c5999369c6db56b07a3edf15a12b7a25f74f3fa",
  "stem": "author-stage",
  "reviewed_sha": "2c5999369c6db56b07a3edf15a12b7a25f74f3fa",
  "summary": "The Author stage, triage wiring, spec and eval-harness change are correct, but the new ls_files test does not prove acceptance criterion 6: it never shows that an untracked file is left out.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_git.py",
      "line": 137,
      "message": "Acceptance criterion 6 requires `tests/test_git.py` to prove that `ls_files` lists a committed file and leaves out an untracked one. `test_ls_files_parses_tracked_paths_only` feeds canned stdout to a FakeExec and only checks that `splitlines` parses it. No repository exists, so nothing is committed and nothing is untracked. The test would still pass if `ls_files` ran `ls-files --others` or any command that lists untracked files, so it cannot fail on the behavior the criterion names.",
      "paved_road": "Add a test that uses a real repo, following the existing `test_git_common_dir_resolves_main_and_linked_worktree(tmp_path)`: init a repo in tmp_path, commit one file, write a second file without adding it, then assert that `ls_files` returns the committed path and not the untracked one. The argv parametrize row can stay."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
