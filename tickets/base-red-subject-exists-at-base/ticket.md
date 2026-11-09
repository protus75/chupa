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
- chupa/stages.py::gather_evidence
- tests/integration/test_stages.py::test_base_red_command_is_recorded_and_filed_without_failing_check
- docs/how-chupa-works.md#4.3 Check

## Goal / Why
`gather_evidence` (`chupa/stages.py`) marks a red Verification command `base_red` whenever its rerun at the merge base exits non-zero. It never checks that the command's subject exists at the base. Verification commands usually name files the ticket adds (`./dev.py test tests/test_new.py`). Those files cannot exist at the base, so the rerun fails there and the red branch command is excused. `VerificationGate.check` skips every `base_red` result, so a failing acceptance command passes the gate. The engine also files a false "fix main" report to the Suggestion Box. After this change a red command that names a path present in the branch worktree but absent at the merge base is never `base_red`: it stays a `verification` finding and files no box message.

## Scope in / Scope out
- In: one small pure private function in `chupa/stages.py`, `_names_branch_only_path(argv, in_branch, in_base)`, where `in_branch` and `in_base` are path predicates taking a string. It returns True when some argv token names a path for which `in_branch` is true and `in_base` is false. A token starting with `-` is skipped. Every other token is cut at its first `::` (so pytest node ids resolve to their file) and the left part is tested.
- In: in the base-rerun loop of `gather_evidence`, when the rerun exits non-zero, set `base_red` and file the box message only if `_names_branch_only_path` is False. The predicates are `lambda p: (worktree / p).exists()` and the matching lambda over `base_worktree`.
- In: a command whose rerun exits 0 at the base is unchanged (it is not red there, so `base_red` was never set).
- In: new unit tests in `tests/unit/test_stages_base_red.py` using in-memory predicates: `test_dash_prefixed_token_is_skipped`, `test_node_id_is_cut_to_its_file`, `test_token_present_in_both_worktrees_is_not_branch_only`, `test_token_present_only_in_branch_is_branch_only`.
- In: one new test in `tests/integration/test_stages.py`, `test_red_command_naming_a_branch_added_file_is_not_base_red`. It calls `_report_ticket(monkeypatch, "grep -q ok chupa/added.py")` with `agent({"chupa/thing.py": "ok\n", "chupa/added.py": "no\n"})`. It asserts the Check ends `gate_failed`; a `verification` finding naming `grep -q ok chupa/added.py` is present (a scope finding for `chupa/added.py` will also appear, so do not assert it is the only finding); `invoice.verification[1].base_red is False` with rc 1; `invoice.verification[0].rc == 0`; and the Suggestion Box is empty.
- In: `docs/how-chupa-works.md` section 4.3 step 3 states that a command naming a path absent at the merge base is never base-red.
- Minimum chosen: a path-existence check on argv tokens. A mechanical rerun of the command against a base with the branch's new files overlaid would be heavier and needs the bug gate's overlay machinery. The existing base-red tests all name files present at the base, so they stay green unchanged.
- Out: `check_hosts` base attribution; `chupa/git.py`; `CHUPA_PLAN.md` (frozen); the bug gate's `carries:` overlay; the worktree-setup duplication (ticket `stages-base-worktree-helper`).

## Scope fence
- chupa/stages.py
- tests/unit/test_stages_base_red.py
- tests/integration/test_stages.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_stages.py -k test_red_command_naming_a_branch_added_file_is_not_base_red` exits 0. The test rules out the wrong result where a red command naming a file the branch adds is marked `base_red` (the check passes and a false `base_red` box message is filed).
2. `./dev.py test tests/unit/test_stages_base_red.py` exits 0. The four named tests (`test_dash_prefixed_token_is_skipped`, `test_node_id_is_cut_to_its_file`, `test_token_present_in_both_worktrees_is_not_branch_only`, `test_token_present_only_in_branch_is_branch_only`) rule out the wrong results where an option token is treated as a path, a node id is tested uncut, a path present at the base is counted as branch-only, or a branch-only path goes undetected.
3. `./dev.py test tests/integration/test_stages.py -k test_base_red_command_is_recorded_and_filed_without_failing_check` exits 0, so a command whose files exist at the base is still attributed `base_red`.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_stages.py -k test_red_command_naming_a_branch_added_file_is_not_base_red
./dev.py test tests/unit/test_stages_base_red.py
./dev.py test tests/integration/test_stages.py -k test_base_red_command_is_recorded_and_filed_without_failing_check
./dev.py test
```

## Regression
```
./dev.py test tests/integration/test_stages.py -k test_red_command_naming_a_branch_added_file_is_not_base_red
```
- carries: tests/integration/test_stages.py

## Definition of rejected
Reject the branch if any of the following holds:
- a red command whose named file is absent at the merge base is still marked `base_red` or still files a `base_red` box message;
- an existing test's assertion is changed or deleted;
- the change adds a config knob, a new gate, or a new Evidence field;
- `check_hosts` or `chupa/git.py` is edited.

## Time budget
- expected: 30m
- stuck: 60m
