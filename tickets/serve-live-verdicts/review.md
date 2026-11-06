# Review: snag

The prior findings are fixed and the single verdict path is in place. But serve's crash-recovery shortcut can drop an operator keep, and criteria 1-4 have no tests that drive the real verdict path.

## Findings

- [logic] chupa/serve.py:358 The recovering-confirm shortcut takes the last commit touching the ticket and treats a `chupa(<stem>): confirmed` draft-to-confirmed stamp as proof that this request promoted a draft. Take a ticket that was confirmed from a draft long ago, then ran and landed in the Reject queue. An operator keeps it at unchanged content, and serve crashes after the effect intent but before the `reject_verdict keep` signal. On restart the shortcut finds the old confirm commit and every check passes. It appends a spurious `draft_confirmed` signal and returns. The effect then completes with `refusal: None`, the keep is never journaled, and the stem stays held. This breaks criterion 1: keep must be journaled exactly once across a mid-effect restart. (do instead: Bind the recovery check to this request. For example, only accept a confirm commit made after the effect intent: record the HEAD sha in the intent window, or compare the commit time with the intent. Otherwise fall through to `runner.verdict_locked`. Add a test where a stem was confirmed from a draft earlier, sits in the Reject queue, and crashes mid-keep.)
- [acceptance] chupa/control.py:250 Criteria 1 and 2 have no tests. No test publishes a keep for a Reject-queue stem while the lock is held, then runs `settle_admissions` twice and across a restart in the middle of the effect, and asserts exactly one `reject_verdict keep actor: operator`. No test sends `reject` while the lock is held, for a Reject-queue stem or for a committed draft, and asserts the `state: rejected` stamp and commit, a single `rejected` transition, and the dead-dependent box messages. The only settle test that runs the real verdict path is the existing draft-confirm test in tests/test_control_cli.py. (do instead: Add tests to tests/test_control.py or tests/test_control_cli.py. They should drive `settle_admissions` with `runner.verdict_locked` for a held-lock keep (repeat pass plus restart after the intent) and for a held-lock reject on a Reject-queue stem and on a committed draft, asserting the journal and box effects named in criteria 1 and 2.)
- [acceptance] chupa/serve.py:364 Criterion 3 (a kept stem dispatches on serve's next scheduling pass without a restart) is checked by tests/test_serve.py, but the diff adds no test there. The existing test at test_serve.py:1079 uses the lock-free `runner.verdict` between serve runs, not a keep published to a running serve. (do instead: Add a tests/test_serve.py test: a stem lands in the Reject queue while serve runs, a held-lock `confirm` request is published, and the same serve instance dispatches the stem on its next pass with no restart.)
- [acceptance] tests/test_control.py:443 Criterion 4 is met only with a stub. `refuse` raises a hand-written Refusal instead of running the real verdict function against a stem that was already kept at unchanged content, so the test cannot show that the real path refuses or that no second keep is journaled. (do instead: Run a second keep at unchanged content through `runner.verdict_locked` on a real journal, after a first keep. Assert that the completion carries the 'already kept at this ticket content' refusal, that `status` renders it, and that there is exactly one `reject_verdict keep` event.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "237a91cee131f9a081466d06535dc7964b8fc357",
  "stem": "serve-live-verdicts",
  "reviewed_sha": "237a91cee131f9a081466d06535dc7964b8fc357",
  "summary": "The prior findings are fixed and the single verdict path is in place. But serve's crash-recovery shortcut can drop an operator keep, and criteria 1-4 have no tests that drive the real verdict path.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 358,
      "message": "The recovering-confirm shortcut takes the last commit touching the ticket and treats a `chupa(<stem>): confirmed` draft-to-confirmed stamp as proof that this request promoted a draft. Take a ticket that was confirmed from a draft long ago, then ran and landed in the Reject queue. An operator keeps it at unchanged content, and serve crashes after the effect intent but before the `reject_verdict keep` signal. On restart the shortcut finds the old confirm commit and every check passes. It appends a spurious `draft_confirmed` signal and returns. The effect then completes with `refusal: None`, the keep is never journaled, and the stem stays held. This breaks criterion 1: keep must be journaled exactly once across a mid-effect restart.",
      "paved_road": "Bind the recovery check to this request. For example, only accept a confirm commit made after the effect intent: record the HEAD sha in the intent window, or compare the commit time with the intent. Otherwise fall through to `runner.verdict_locked`. Add a test where a stem was confirmed from a draft earlier, sits in the Reject queue, and crashes mid-keep.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "chupa/control.py",
      "line": 250,
      "message": "Criteria 1 and 2 have no tests. No test publishes a keep for a Reject-queue stem while the lock is held, then runs `settle_admissions` twice and across a restart in the middle of the effect, and asserts exactly one `reject_verdict keep actor: operator`. No test sends `reject` while the lock is held, for a Reject-queue stem or for a committed draft, and asserts the `state: rejected` stamp and commit, a single `rejected` transition, and the dead-dependent box messages. The only settle test that runs the real verdict path is the existing draft-confirm test in tests/test_control_cli.py.",
      "paved_road": "Add tests to tests/test_control.py or tests/test_control_cli.py. They should drive `settle_admissions` with `runner.verdict_locked` for a held-lock keep (repeat pass plus restart after the intent) and for a held-lock reject on a Reject-queue stem and on a committed draft, asserting the journal and box effects named in criteria 1 and 2.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "chupa/serve.py",
      "line": 364,
      "message": "Criterion 3 (a kept stem dispatches on serve's next scheduling pass without a restart) is checked by tests/test_serve.py, but the diff adds no test there. The existing test at test_serve.py:1079 uses the lock-free `runner.verdict` between serve runs, not a keep published to a running serve.",
      "paved_road": "Add a tests/test_serve.py test: a stem lands in the Reject queue while serve runs, a held-lock `confirm` request is published, and the same serve instance dispatches the stem on its next pass with no restart.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "tests/test_control.py",
      "line": 443,
      "message": "Criterion 4 is met only with a stub. `refuse` raises a hand-written Refusal instead of running the real verdict function against a stem that was already kept at unchanged content, so the test cannot show that the real path refuses or that no second keep is journaled.",
      "paved_road": "Run a second keep at unchanged content through `runner.verdict_locked` on a real journal, after a first keep. Assert that the completion carries the 'already kept at this ticket content' refusal, that `status` renders it, and that there is exactly one `reject_verdict keep` event.",
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
