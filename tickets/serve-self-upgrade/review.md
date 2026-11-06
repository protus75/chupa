# Review: snag

The handoff mechanics look right, but no test covers acceptance criterion 2, and the self-hosted test fakes the upgrade check by hand, so the admission and merge-pass wiring is never exercised.

## Findings

- [acceptance] tests/test_serve.py:1868 Criterion 2 is not tested. It requires a host serve whose engine checkout differs from the host repo to hand off at its next admission check after the engine's `chupa` tree changes outside serve. Both new handoff tests set `rig.owner.engine = root`, which makes the engine the host repo, and no test uses a separate engine checkout. (do instead: Add a test that sets `rig.owner.engine` to a separate git checkout under tmp_path with its own `chupa/` tree. Commit a `chupa/` change there while serve is idle and do not call `check_upgrade` by hand. Assert that serve journals `serve_handoff` and spawns once from its own admission-boundary check.)
- [acceptance] tests/test_serve.py:1898 Criterion 1 says a merge touching `chupa/` triggers the handoff, and the ticket requires the tree check at admission and merge-queue boundaries. Both tests commit straight to the repo and then call `rig.owner.check_upgrade()` directly. The calls in `respond`/`merge` (serve.py) are never exercised, so the tests would still pass if those boundary calls were removed. The docs-only case also never goes through a merge. (do instead: Drive the change through a real serve merge, as other serve tests do: a ticket whose implement step changes `chupa/` (or only `docs/`). Let serve's own post-merge and pre-admission `check_upgrade` calls detect it, without calling `check_upgrade` from the test.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "734615e92bcf6502830d33879a0d2e9c84ade8a2",
  "stem": "serve-self-upgrade",
  "reviewed_sha": "734615e92bcf6502830d33879a0d2e9c84ade8a2",
  "summary": "The handoff mechanics look right, but no test covers acceptance criterion 2, and the self-hosted test fakes the upgrade check by hand, so the admission and merge-pass wiring is never exercised.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_serve.py",
      "line": 1868,
      "message": "Criterion 2 is not tested. It requires a host serve whose engine checkout differs from the host repo to hand off at its next admission check after the engine's `chupa` tree changes outside serve. Both new handoff tests set `rig.owner.engine = root`, which makes the engine the host repo, and no test uses a separate engine checkout.",
      "paved_road": "Add a test that sets `rig.owner.engine` to a separate git checkout under tmp_path with its own `chupa/` tree. Commit a `chupa/` change there while serve is idle and do not call `check_upgrade` by hand. Assert that serve journals `serve_handoff` and spawns once from its own admission-boundary check.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/test_serve.py",
      "line": 1898,
      "message": "Criterion 1 says a merge touching `chupa/` triggers the handoff, and the ticket requires the tree check at admission and merge-queue boundaries. Both tests commit straight to the repo and then call `rig.owner.check_upgrade()` directly. The calls in `respond`/`merge` (serve.py) are never exercised, so the tests would still pass if those boundary calls were removed. The docs-only case also never goes through a merge.",
      "paved_road": "Drive the change through a real serve merge, as other serve tests do: a ticket whose implement step changes `chupa/` (or only `docs/`). Let serve's own post-merge and pre-admission `check_upgrade` calls detect it, without calling `check_upgrade` from the test.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
