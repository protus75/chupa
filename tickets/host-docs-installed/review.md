# Review: approve

The diff moves the three host guides into the package (`chupa/docs/`) with their relative links still working. It adds a `chupa docs` verb that runs before any config or lock and prints package-relative paths, makes `_new` print the authoring guide's path, forwards `./dev.py docs` through dev.py's existing generic fallback, updates every stale reference, and adds the required tests, all inside the scope fence.

## Findings

none

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "744c4836d58490c428490bfdefe9398426989b07",
  "stem": "host-docs-installed",
  "reviewed_sha": "744c4836d58490c428490bfdefe9398426989b07",
  "summary": "The diff moves the three host guides into the package (`chupa/docs/`) with their relative links still working. It adds a `chupa docs` verb that runs before any config or lock and prints package-relative paths, makes `_new` print the authoring guide's path, forwards `./dev.py docs` through dev.py's existing generic fallback, updates every stale reference, and adds the required tests, all inside the scope fence.",
  "findings": [],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "approve"
}
```
