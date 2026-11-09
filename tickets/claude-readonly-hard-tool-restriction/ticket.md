---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: confirmed
---

## Depends on
- none

## Context
- chupa/providers.py::ClaudeAdapter.argv
- tests/integration/test_providers.py
- hosts/fixture/bin/claude
- tests/integration/test_fixture_host.py

## Goal / Why
Claude's non-writing surfaces (review, author, triage, requisition review, diagnose) are launched with `--allowedTools Read Grep Glob LS`. That flag only pre-approves those tools. It does not remove the others, and the CLI merges it with the operator's ambient `~/.claude` settings. Settings that pre-approve `git commit`, `gh pr`, or `bypassPermissions` therefore still run unprompted under `-p`, inside surfaces the engine treats as read-only. After this change the read-only argv carries a hard tool restriction and an explicit permission mode, so ambient settings cannot grant write or state-changing tools.

## Scope in / Scope out
In: in `ClaudeAdapter.argv`, replace the read-only grant `--allowedTools Read Grep Glob LS` with `--tools Read Grep Glob LS --permission-mode dontAsk`. `--tools` restricts which built-in tools exist; `dontAsk` denies anything not pre-approved instead of consulting ambient defaults. The writes grant is unchanged. Update the tests and the fixture `claude` binary that pin the old grant.

Coverage dependents of `chupa/providers.py` outside the fence are unaffected: grep shows none of them pins the `--allowedTools` grant, and those that drive the fixture claude binary go through `hosts/fixture/bin/claude`, which is fenced and updated here.

Out: the codex adapter, the writes path, prompt specs, docs, and `CHUPA_PLAN.md` (frozen).

## Scope fence
- chupa/providers.py
- tests/integration/test_providers.py
- hosts/fixture/bin/claude
- tests/integration/test_fixture_host.py

## Acceptance criteria
1. `tests/integration/test_providers.py` asserts the read-only argv ends with `--tools Read Grep Glob LS --permission-mode dontAsk`. It also asserts that `--allowedTools` and `bypassPermissions` are absent. A test that only checked for the allow-list would also pass on the old argv, so it must rule out `--allowedTools`.
2. The fixture `hosts/fixture/bin/claude` accepts the new read-only grant and the writes grant, and still rejects any other grant. `./dev.py test tests/integration/test_fixture_host.py` exits 0 with its read-only assertion updated from `--allowedTools` to `--tools`.
3. The writes argv is unchanged: the existing implement test in `tests/integration/test_providers.py` still passes with `--permission-mode bypassPermissions`.

## Verification
```
./dev.py test tests/integration/test_providers.py
./dev.py test tests/integration/test_fixture_host.py
```

## Definition of rejected
A missing governing fact returns premise_failed. A forced change beyond the fence needs contract repair.

## Time budget
- expected: 30m
- stuck: 60m
