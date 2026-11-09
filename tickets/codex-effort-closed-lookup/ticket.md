---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:suggestion
state: draft
---

## Depends on
- none

## Context
- chupa/providers.py::CodexAdapter.argv
- chupa/caps.py
- tests/integration/test_providers.py

## Goal / Why
`config.yaml` routes Implement to codex at every tier, and `caps.next_rung` escalates effort up to `max`. `CodexAdapter.argv` formats the effort into `-c model_reasoning_effort=<effort>` unchanged. Codex accepts `minimal|low|medium|high` (and `xhigh` on some models), not `max`, so the last escalation rung would end in a provider error instead of a stronger attempt. After this change `CodexAdapter.argv(model, "max", writes)` emits `model_reasoning_effort=high`, which every codex model accepts. Other effort values pass through unchanged.

Dependents cleared: only `max` changes, and it now maps to `high`. The only tests that assert a codex effort string are `tests/integration/test_providers.py` (`high` and `low`, both unchanged). `chupa/observe.py` only reads the effort back out of argv for display. `tests/integration/test_ladder.py`, `test_caps.py` and the other tests that run `chupa/providers.py` assert no codex `max` effort string, so none of them needs a change.

## Scope in / Scope out
- In: `chupa/providers.py` gains a closed module-level mapping `CODEX_EFFORT = {"low": "low", "medium": "medium", "high": "high", "max": "high"}` covering every `AgentEffort` value. `CodexAdapter.argv` formats `CODEX_EFFORT[effort]` into the `-c model_reasoning_effort=` argument. An effort outside the mapping raises `KeyError`, which fails closed.
- In: new `tests/unit/test_codex_effort.py` with one test, `test_codex_max_effort`. It calls `CodexAdapter.argv(CodexAdapter.__new__(CodexAdapter), "model", "max", False)` directly, with no exec and no disk. It asserts the argv contains `model_reasoning_effort=high` and does not contain `model_reasoning_effort=max`. It also asserts that an effort outside the mapping raises `KeyError`.
- Out: the claude adapter (it has no effort flag); `chupa/caps.py` and the escalation ladder; `config.yaml`; `xhigh` support; `CHUPA_PLAN.md` (frozen).

## Scope fence
- chupa/providers.py
- tests/unit/test_codex_effort.py

## Acceptance criteria
1. `./dev.py test tests/unit/test_codex_effort.py` exits 0. The test asserts the argv contains `model_reasoning_effort=high` for effort `max`, which rules out the unmapped `model_reasoning_effort=max`, and asserts a `KeyError` for an unmapped effort, which rules out an open fallback.
2. `./dev.py test tests/integration/test_providers.py` exits 0 with the existing codex argv tests (`model_reasoning_effort=high`, `model_reasoning_effort=low`) unchanged.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/unit/test_codex_effort.py
./dev.py test tests/integration/test_providers.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `CodexAdapter.argv` can still emit `model_reasoning_effort=max`;
- the mapping is an open fallback (`.get(effort, effort)` or a denylist) instead of a closed lookup;
- the claude adapter, `chupa/caps.py` or `config.yaml` is changed;
- the new test passes on the unmapped code.

## Time budget
- expected: 15m
- stuck: 45m
