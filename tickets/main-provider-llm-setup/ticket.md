---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- chupa/__main__.py::main
- chupa/__main__.py::_review
- chupa/providers.py::ProviderLLM.__init__
- chupa/providers.py::ProviderLLM.preflight
- chupa/runner.py::prepare_pipeline
- tests/integration/test_review_command.py
- tests/integration/test_triage.py::run

## Goal / Why
`chupa/__main__.py` builds and preflights a provider LLM with the same six lines twice: in the `triage` verb's `one_pass` inside `main`, and in `_review`. Each builds `ProviderLLM(...)`, calls `session.timers.reconstruct()` and `session.timers.fire_due()`, runs `await llm.preflight() if session.active else []`, and raises `ProviderSetupError("; ".join(problems))` when problems come back. Triage passes the locals `config`, `exec_`, `env`, `repo` of `main`; review passes `checkout.config`, `checkout.exec_`, `checkout.env`, `checkout.repo`. These are the same objects: `main` builds `checkout = runner.Checkout(repo=repo, config=config, env=env, exec_=exec_, ...)` and does not rebind any of the four before the triage branch. The copies will drift the next time one is edited.

After this change one async helper in `chupa/__main__.py` holds the sequence. It takes the checkout and the provider session, builds the `ProviderLLM` from the checkout's fields, runs the timer and preflight steps, and returns the preflighted LLM. Triage and review both call it, and their behaviour does not change.

## Scope in / Scope out
- In: add one module-level async function to `chupa/__main__.py`, for example `_preflighted_llm(checkout: runner.Checkout, session: ProviderSession) -> ProviderLLM`. Its body is the current sequence with every argument taken from `checkout`: `ProviderLLM(checkout.config, exec_=checkout.exec_, fs=checkout.fs, env=checkout.env, cwd=checkout.repo, timeout=runner.call_timeout(checkout.config), session=session)`, then `session.timers.reconstruct()`, `session.timers.fire_due()`, the `session.active` preflight, and the `ProviderSetupError` raise.
- In: replace the inline sequence in triage's `one_pass` with `llm = await _preflighted_llm(checkout, session)`. Keep the call inside the existing `try` so `session.close()` and `lock.release()` still run when preflight fails.
- In: replace the inline sequence in `_review` the same way, inside its existing `try`.
- In: add one test per path, because neither path's preflight failure is tested today. The existing tests in `tests/integration/test_review_command.py` and `tests/integration/test_triage.py` monkeypatch `chupa.__main__.ProviderLLM` with a lambda that returns a `FakeLLM`. That leaves `session.active` False, so preflight is skipped. Each new test keeps the real `ProviderLLM` and monkeypatches `chupa.providers.ProviderLLM.preflight` with an async function returning `["probe refused"]`.
  - `tests/integration/test_review_command.py`: `test_review_preflight_failure_refuses` writes `candidate` with `write(root, "candidate", ticket())` and runs `main(["review", "candidate"], cwd=root, env=ENV, clock=Clock())`. It asserts the result is `2`, not `0` or `1`; stderr contains `chupa review: probe refused`; and `verdicts(root) == []`.
  - `tests/integration/test_triage.py`: `test_triage_preflight_failure_refuses` runs `main(["triage"], cwd=root, env=ENV, clock=Clock())` on its usual fixture root. It asserts the result is `2`, not `0`, and stderr contains `chupa triage: probe refused`.
  - Both tests then take a `Lockfile` on `root / ".chupa/state"` with `acquire()` without raising `LockHeld`, which shows the failure path released the lock. If a test needs to, it puts a `claude` provider candidate in its config the way `test_retro_success` in `tests/integration/test_cli.py` does.
- Unaffected tests: `tests/integration/test_review_command.py`, `tests/integration/test_triage.py`, and the triage and review cases in `tests/integration/test_cli.py` replace `ProviderLLM` wholesale. The helper still looks up `ProviderLLM` from `chupa.__main__` module globals, so those monkeypatches still apply and the tests pass unchanged.
- Out: `chupa/runner.py` `prepare_pipeline` (`ProviderLLM` + `preflight()` for run/drain). It is a different sequence. It calls no timers, because `run_ticket` reconstructs and fires them separately before `dispatch.prepare()`. It preflights without the `session.active` guard, prints `preflight_notices`, and raises `runner.Refusal` with a paved road instead of `ProviderSetupError`. Merging it would change run/drain behaviour.
- Out: the other `timers.reconstruct()` callers in `chupa/restart.py`, `chupa/checkpoint.py`, `chupa/drain.py`, and `chupa/runner.py` `run_ticket`; printing preflight notices from triage or review; the triage and review error messages.

## Scope fence
- chupa/__main__.py
- tests/integration/test_review_command.py
- tests/integration/test_triage.py

## Acceptance criteria
1. `ProviderLLM(` appears in `chupa/__main__.py` only inside the new helper. `grep -c "ProviderLLM(" chupa/__main__.py` prints `1`, not `2` or `3`.
2. `session.timers.reconstruct()` and `await llm.preflight()` each appear in `chupa/__main__.py` only inside the helper. `grep -c "timers.reconstruct()" chupa/__main__.py` prints `1`.
3. `./dev.py test tests/integration/test_review_command.py tests/integration/test_triage.py` exits 0. It includes `test_review_preflight_failure_refuses`, which asserts exit `2` (not `0`), `chupa review: probe refused` on stderr, and no journaled verdict. It also includes `test_triage_preflight_failure_refuses`, which asserts exit `2` (not `0`) and `chupa triage: probe refused` on stderr. Both assert that the lock was released.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_review_command.py tests/integration/test_triage.py tests/integration/test_cli.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any copy of the sequence stays inline in `chupa/__main__.py`, or the helper takes `config`, `exec_`, `env`, or `repo` as separate parameters instead of reading them from the checkout;
- `chupa/runner.py` is changed;
- triage or review drops the `session.active` guard, the `timers.reconstruct()`/`fire_due()` calls, or the `ProviderSetupError` raise;
- a new test passes when the preflight raise is deleted.

## Time budget
- expected: 20m
- stuck: 60m
