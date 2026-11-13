---
id: declined-box-000402-ae816ecc
kind: declined
link: box-000402-ae816ecc
reopen_after_days: 30
---
Author could not produce a ticket.

Evidence: - missed-version-pin: `tests/unit/test_specs.py:246` (`test_review_spec_checks_docs`) asserts `spec.meta.version == "1.5"` for chupa/specs/review.md. Scope in says to update the pin only in `test_review_spec_read_only`. After the bump, `./dev.py test tests/unit/test_specs.py -k review_spec` also selects `test_review_spec_checks_docs`, so that test fails unless the implementer edits it, and Scope in does not cover that edit. (do instead: In Scope in, extend the test_specs.py bullet so it also updates the `spec.meta.version` pin in `test_review_spec_checks_docs` (tests/unit/test_specs.py:246) to the bumped version. Optionally add an acceptance criterion that both review-spec tests pin the new version.)
