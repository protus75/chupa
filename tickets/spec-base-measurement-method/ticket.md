---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- implement-spec-base-red-not-premise

## Context
- tests/unit/test_specs.py

## On-demand
- chupa/specs/implement.md
- chupa/specs/diagnose.md

## Goal / Why
Implement agents made false `premise_failed` claims that a verification failure already existed on the base commit, because they measured the base with broken methods. review-unmerged-provisional ran the lint with `PYTHONPATH` pointing at the main checkout, which loaded other code; the plain command exited 0. core-chat-ticket-first checked the base in a fresh `git init` repo with no history, so every ticket looked new and failed lint. core-drift-preflight attempt 0 claimed 37 of 393 tickets fail lint on base, and its diagnosis accepted that without checking how it was measured. Each false claim spent a `premise_bounce` cap, and core-drift-preflight reached the Reject queue. `chupa/specs/implement.md` Task verifies on the base commit but gives no method. After this change Implement names the valid method, and Diagnose checks how a pre-existing-failure claim was measured before accepting it. The rule guards against overcorrection: a failure reproduced the valid way still counts as a base failure, and the base check is run once.

This ticket depends on implement-spec-base-red-not-premise because both edit the Task of `chupa/specs/implement.md` and bump its version. That ticket moves the spec from "2.3" to "2.4"; this one bumps from "2.4" to "2.5" on top of it, so the two never share a version.

## Scope in / Scope out
- In: `chupa/specs/implement.md`: extend the base-verification wording in Task. The valid method: run the ticket's `## Verification` command exactly as written, once, in a `git worktree` of the base commit that has full history, with no environment overrides (such as `PYTHONPATH`) and no synthetic repository (such as a fresh `git init`). A claim measured any other way is not evidence. Bump `version` from "2.4" to "2.5".
- In: `chupa/specs/diagnose.md`: add one rule to Task. When the terminal or run record claims a failure already exists on the base commit, check how it was measured. If the method was not the plain Verification command in a base worktree with history (env override, synthetic repo, other checkout), the claim is unproven: choose `retry` and give a lesson to re-measure the valid way. A claim measured the valid way stays a base failure and keeps its other verdicts. Bump `version` from "1.2" to "1.3".
- In: `tests/unit/test_specs.py`: update the implement and diagnose version pins and the implement version assertion, and assert the new rule text appears in each rendered spec.
- In: `tests/integration/test_stages.py`: update the `spec: implement` pin to 2.5.
- Out: Check attribution code, `chupa/stages.py`, the base-red rules of the open tickets implement-spec-base-red-not-premise and diagnose-spec-base-red-not-unsatisfiable, every other spec.

## Scope fence
- chupa/specs/implement.md
- chupa/specs/diagnose.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py

## Acceptance criteria
1. `chupa/specs/implement.md` is at version "2.5" and its rendered Task names the valid base method: the Verification command as written, run once, in a base-commit worktree with history, no env overrides, no synthetic repo. `./dev.py test tests/unit/test_specs.py` asserts the rule text including "once", which rules out a spec that gives no method or allows repeated base runs.
2. `chupa/specs/diagnose.md` is at version "1.3" and its Task tells Diagnose to check how a base-failure claim was measured and to choose `retry` for an invalid measurement. `./dev.py test tests/unit/test_specs.py` asserts this text, which rules out the 1.2 spec that accepts any claim.
3. The diagnose rule keeps a validly measured base failure as a base failure. `./dev.py test tests/unit/test_specs.py` asserts that clause, which rules out a rule that retries every base-failure claim.
4. The run-record assertion pins `spec: implement 2.5`. `./dev.py test tests/integration/test_stages.py` rules out the stale 2.4 pin.

## Verification
```
./dev.py test tests/unit/test_specs.py
./dev.py test tests/integration/test_stages.py
```

## Definition of rejected
The implement or diagnose spec fails lint or exceeds its size limit; a validly measured base failure is no longer treated as one; the base check is required more than once; any code under `chupa/` other than the two spec files changes.

## Time budget
- expected: 20m
- stuck: 45m
