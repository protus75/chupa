---
id: declined-box-000335-4a6be0d2
kind: declined
link: box-000335-4a6be0d2
reopen_after_days: 30
---
Author could not produce a ticket.

Evidence: - coverage_floor: Scope in adds a branch to chupa/tickets.py, which has a floor of 11 under [coverage.files] in test-gate.toml. The ticket says the integration test `test_context_directory_is_refused` 'covers the coverage floor', but covgate measures the unit-test command ('name the unit-test command after --'). No tests/unit file in the fence has a named test that runs the new lines. (do instead: Add tests/unit/test_tickets_context.py (it already exists and imports from chupa.tickets) to `## Scope fence` and Scope in. Name a test there that runs the new `is_dir()` Context branch, or state how the unit suite reaches that line. Delete the sentence that says the integration test covers the floor.)
- coverage_dependents: 71 test files outside the fence run chupa/tickets.py, including tests/integration/test_author.py, test_lint_verb.py, test_stages.py, test_review_command.py and test_requisition.py. The ticket neither fences them nor clears them. (do instead: In Scope in / Scope out, add one sentence that clears them all. For example: the new branch fires only for a `## Context` entry that is a directory, and no fixture outside tests/integration/test_tickets.py lists one (checked by grep), so their outcomes are unchanged.)
