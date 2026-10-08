---
priority: P0
kind: bug
source: human
state: confirmed
---

## Depends on
none

## Context
- chupa/providers.py
- tests/test_providers.py

## Plan contract
- section 6.8
- section 6.11

## Goal / Why
The provider preflight's version children, `<binary> --version` and `pnpm view <package> version`, run with `child_env(env, config)`, which removes every configured provider key. Neither process needs a key.

Why: section 6.8 sets inherit-minus-secrets for every child, and the conduct rules forbid passing a provider key to a process that does not need it. `ProviderLLM.preflight` in `chupa/providers.py` passes the full parent `self._env` to both commands. The probe calls go through the adapters, which already restore only the serving provider's key, and they stay unchanged.

## Scope in / Scope out
- In: the two `self._exec.run` calls in `ProviderLLM.preflight` pass `child_env(self._env, self._config)`.
- Out: probe invocation, adapter environments, and the preflight's notice and refusal behavior.

## Scope fence
- chupa/providers.py
- tests/test_providers.py

## Acceptance criteria
1. `uv run pytest -q tests/test_providers.py` exits 0. It includes a new `test_preflight_version_children_carry_no_provider_key`. In that test, `PreflightExec` records the `env` of each `--version` and `pnpm view` call. With `ENV` holding `CLAUDE_KEY` and `CODEX_KEY`, the test asserts that neither key appears in any recorded version-child env and that `PATH` and `HOME` do.
2. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_providers.py
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_providers.py -k test_preflight_version_children_carry_no_provider_key
```
- carries: tests/test_providers.py

## Definition of rejected
Reject the branch if any preflight child other than a serving probe receives a provider key, if probe behavior changes, or if the regression test passes on the merge base.

## Time budget
- expected: 15m
- stuck: 45m
