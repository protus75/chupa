---
id: declined-box-000061-72ece377
kind: declined
link: box-000061-72ece377
reopen_after_days: 30
---
Author could not produce a ticket.

Evidence: - scope_fence: hosts/fixture/bin/claude (lines 20-25) requires the adapter argv to be exactly `-p --output-format stream-json --verbose --model fixture` followed by one of the two grants. It raises `unknown argv` for anything else. tests/integration/test_fixture_host.py puts this binary on PATH and runs it through the real ClaudeAdapter. Once `--effort <effort>` follows the `--model` pair, every fixture-host claude call returns an error result and test_fixture_host fails, so `./dev.py test` cannot exit 0. (do instead: Add hosts/fixture/bin/claude to `## Scope fence` and to Scope in. In that file, require `--effort` and an AgentEffort value right after `--model fixture`, then take the grant from the remaining argv. Example: `prefix = [..., "--model", "fixture"]`, then check `argv[len(prefix)] == "--effort"` and `argv[len(prefix)+1] in ("low", "medium", "high", "max")`, then `grant = argv[len(prefix)+2:]`. Also add it to `## Context`.)
