# Review: snag

The plugin matches the ticket, but the setup/teardown test cannot catch the case where only one of the two phases is guarded, which acceptance criterion 2 requires it to catch.

## Findings

- [logic] tests/test_testguard.py:76 Acceptance criterion 2 says the test must fail if either fixture's subprocess.run succeeds. It doesn't. If one phase is left unguarded, that fixture's `pytest.fail(...)` still produces an error. So `assert_outcomes(passed=2, errors=2)` still holds. One UnitIOBlocked error then prints the name several times: the `raise UnitIOBlocked(` source line, the `E   chupa.testguard.UnitIOBlocked` line, and the short-summary ERROR line. That alone satisfies `count("UnitIOBlocked") >= 2`, so the test passes with only setup, or only teardown, guarded. (do instead: Assert that `setup process succeeded` and `teardown process succeeded` are both absent from the inner output. Better, use `result.stdout.fnmatch_lines` or a per-test check so the test_before setup error and the test_after teardown error each name UnitIOBlocked.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "43e6e74c0b613651c719727d1594e6c2f58d1420",
  "stem": "testguard",
  "reviewed_sha": "43e6e74c0b613651c719727d1594e6c2f58d1420",
  "summary": "The plugin matches the ticket, but the setup/teardown test cannot catch the case where only one of the two phases is guarded, which acceptance criterion 2 requires it to catch.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/test_testguard.py",
      "line": 76,
      "message": "Acceptance criterion 2 says the test must fail if either fixture's subprocess.run succeeds. It doesn't. If one phase is left unguarded, that fixture's `pytest.fail(...)` still produces an error. So `assert_outcomes(passed=2, errors=2)` still holds. One UnitIOBlocked error then prints the name several times: the `raise UnitIOBlocked(` source line, the `E   chupa.testguard.UnitIOBlocked` line, and the short-summary ERROR line. That alone satisfies `count(\"UnitIOBlocked\") >= 2`, so the test passes with only setup, or only teardown, guarded.",
      "paved_road": "Assert that `setup process succeeded` and `teardown process succeeded` are both absent from the inner output. Better, use `result.stdout.fnmatch_lines` or a per-test check so the test_before setup error and the test_after teardown error each name UnitIOBlocked.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.3",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
