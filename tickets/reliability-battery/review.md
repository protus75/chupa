# Review: snag

The machinery, registration, writer and command look correct, but the test for the ticket's 'a supplied success/auditor verdict must refuse green' obligation can never fail.

## Findings

- [logic] tests/test_reliability_battery.py:194 The supplied-verdict check sets `m.success = m.auditor = True` and asserts `not battery._observe(m).green`. At that point `battery.audit_journal` is still monkeypatched to return two violations, so `_observe` comes back red whatever it does with a supplied success or auditor verdict. The assertion passes even if `_observe` trusted the injected verdict, so the obligation is never actually tested. (do instead: Restore the real `audit_journal` before this case. Then supply a success/auditor verdict together with evidence that is otherwise refused (for example, the member's journal with one required fault event removed) and assert that `_observe` still raises `BatteryRefused` or returns red. Alternatively, pass the supplied verdict through whatever input `_observe` actually reads, so that a regression which trusts it would make the test fail.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "5fdcd1c4329b86c9487b1ee0f0b5512641feae5e",
  "stem": "reliability-battery",
  "reviewed_sha": "5fdcd1c4329b86c9487b1ee0f0b5512641feae5e",
  "summary": "The machinery, registration, writer and command look correct, but the test for the ticket's 'a supplied success/auditor verdict must refuse green' obligation can never fail.",
  "findings": [
    {
      "code": "logic",
      "path": "tests/test_reliability_battery.py",
      "line": 194,
      "message": "The supplied-verdict check sets `m.success = m.auditor = True` and asserts `not battery._observe(m).green`. At that point `battery.audit_journal` is still monkeypatched to return two violations, so `_observe` comes back red whatever it does with a supplied success or auditor verdict. The assertion passes even if `_observe` trusted the injected verdict, so the obligation is never actually tested.",
      "paved_road": "Restore the real `audit_journal` before this case. Then supply a success/auditor verdict together with evidence that is otherwise refused (for example, the member's journal with one required fault event removed) and assert that `_observe` still raises `BatteryRefused` or returns red. Alternatively, pass the supplied verdict through whatever input `_observe` actually reads, so that a regression which trusts it would make the test fail.",
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
