# Review: snag

The exit reads are implemented, but test_phase6_exit_missing_evidence_refuses can never fail: it makes `Path.read_bytes` raise and then catches that same error before any real read runs, so it does not prove missing evidence fails closed.

## Findings

- [logic] tests/test_phase6_exit.py:185 test_phase6_exit_missing_evidence_refuses replaces Path.read_bytes so it raises for the chosen path. It then calls LOOP_PATH.read_bytes(), BASELINE_PATH.read_bytes() and RECEIPT_PATH.read_bytes() inline as the arguments to _validate_receipt. The FileNotFoundError comes from the test's own replacement while those arguments are evaluated, before _validate_receipt, _reports() or the baseline_bytes fixture (host_loop.committed_bytes) runs. The test passes whatever the code under test does, so criterion 6 ('Missing ... evidence fails closed') is not actually tested. (do instead: Exercise the real read paths against a genuinely absent file. For example, point LOOP_PATH and RECEIPT_PATH (via monkeypatch on the module globals) at nonexistent paths under tmp_path and assert that _reports() raises FileNotFoundError. For the baseline, call host_loop.committed_bytes on a nonexistent path and assert that it refuses. Do not make the test's own argument expressions raise.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "53cf9cf23251a78ead45694e918dcc2f4915de66",
  "stem": "phase6-exit",
  "reviewed_sha": "53cf9cf23251a78ead45694e918dcc2f4915de66",
  "summary": "The exit reads are implemented, but test_phase6_exit_missing_evidence_refuses can never fail: it makes `Path.read_bytes` raise and then catches that same error before any real read runs, so it does not prove missing evidence fails closed.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/test_phase6_exit.py",
      "line": 185,
      "message": "test_phase6_exit_missing_evidence_refuses replaces Path.read_bytes so it raises for the chosen path. It then calls LOOP_PATH.read_bytes(), BASELINE_PATH.read_bytes() and RECEIPT_PATH.read_bytes() inline as the arguments to _validate_receipt. The FileNotFoundError comes from the test's own replacement while those arguments are evaluated, before _validate_receipt, _reports() or the baseline_bytes fixture (host_loop.committed_bytes) runs. The test passes whatever the code under test does, so criterion 6 ('Missing ... evidence fails closed') is not actually tested.",
      "paved_road": "Exercise the real read paths against a genuinely absent file. For example, point LOOP_PATH and RECEIPT_PATH (via monkeypatch on the module globals) at nonexistent paths under tmp_path and assert that _reports() raises FileNotFoundError. For the baseline, call host_loop.committed_bytes on a nonexistent path and assert that it refuses. Do not make the test's own argument expressions raise.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
