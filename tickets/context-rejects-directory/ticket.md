---
priority: P1
kind: bug
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: draft
---

## Depends on
- none

## Context
- chupa/tickets.py
- tests/integration/test_tickets.py::test_context_section_findings
- tests/regress_lint_worktree_journal.py

## Goal / Why
`validate_ticket` in `chupa/tickets.py` checks each `## Context` path with `(repo / source).exists()`, while `## On-demand` uses `.is_file()`. A Context entry that names a directory (box-declined-verdict listed `tickets/decisions`) therefore passes lint and intake. Implement's input render (`implement_inputs`) later reads that path as a file and raises `IsADirectoryError`, which crashes the drain. After this change a Context path that is not a file is refused at lint with a finding, the same rule On-demand already applies.

## Scope in / Scope out
- In: in `chupa/tickets.py`, change the Context existence check from `.exists()` to `.is_file()`. Keep the existing "does not exist" finding and its paved road, and make its text say the path must be an existing file. Add a regression test and a carried reproducer.
- Out: the On-demand check; Context selector (`::`, `#`) handling; any change to `implement_inputs` in `chupa/stages.py`; symlink handling.

## Scope fence
- chupa/tickets.py
- tests/integration/test_tickets.py
- tests/regress_context_directory.py

## Acceptance criteria
1. `tests/integration/test_tickets.py::test_context_directory_is_refused` exits 0: a ticket whose `## Context` names an existing directory is refused with a finding mentioning `Context`. The wrong result it rules out is validation passing, because the test asserts `TicketInvalid` is raised.
2. `tests/regress_context_directory.py` exists, prints `{"regression_result": "pass"}` on the fixed code, and prints `defect` on the old `.exists()` code.
3. `./dev.py test` exits 0, so a Context entry naming an existing file is still accepted.

## Verification
```
./dev.py test tests/integration/test_tickets.py::test_context_directory_is_refused
./dev.py test
```

## Regression
```
uv run python tests/regress_context_directory.py
```
- carries: tests/regress_context_directory.py

## Definition of rejected
Reject the branch if any of the following holds:
- a Context directory path still passes `validate_ticket`;
- the On-demand check or any file outside `## Scope fence` changes;
- the reproducer prints `pass` against the unfixed `.exists()` check.

## Time budget
- expected: 15m
- stuck: 40m
