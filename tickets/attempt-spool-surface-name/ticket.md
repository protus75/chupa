---
state: confirmed
source: human
priority: P2
kind: bug
agent_tier: medium
agent_effort: medium
---

## Depends on
none

## Context
- chupa/driver.py
- chupa/requisition.py
- tests/test_driver.py
- tests/test_echo_stage.py
- tests/test_triage.py

## Plan contract
- section 6

## Goal / Why
Each model call's attempt-spool capture lives at `<state_dir>/spools/<stem>/<attempt>/<surface>/call-<nn>/`, so the Implement, Review, and diagnose calls of one attempt keep their own `prompt.md`, `output.txt`, and `error.txt`.

Today `Driver.run` (chupa/driver.py, `name = f"call-{call_seq:02d}"`) and the requisition review (chupa/requisition.py, same naming) key the call dir on the call sequence alone. Every stage restarts `call_seq` at 1 under the same `<stem>/<attempt>/`, so a later stage's `call-01` overwrites the earlier stage's. On a failed attempt the diagnose call runs last and destroys the Implement and Review captures, which are the evidence section 6 requires a call to leave on disk.

## Scope in / Scope out
- In: `Driver.run` and the requisition review write each call's files under `f"{surface}/call-{call_seq:02d}"`, where `surface` is the stage's surface (`stage.surface` in the driver, `"requisition_review"` in requisition.py).
- In: every existing test asserting the old `call-NN/` path is updated to the surface-qualified path (tests/test_driver.py, tests/test_echo_stage.py, tests/test_triage.py).
- In: a new test `test_surfaces_sharing_an_attempt_keep_separate_spools` in tests/test_driver.py runs the existing `run()` helper twice for the same stem and attempt, once with an `implement` stage and once with a `review` stage, each echoing different text, and asserts both `implement/call-01/` and `review/call-01/` hold their own prompt and output.
- Out: the provider capture under `spools/providers/` (chupa/providers.py), the check and merge verify spools (`<stage>/verify-NN.txt`, chupa/stages.py), harvest's tail cutting (chupa/runner.py, which globs recursively and is unaffected), and journal effect keys.

## Scope fence
- chupa/driver.py
- chupa/requisition.py
- tests/test_driver.py
- tests/test_echo_stage.py
- tests/test_triage.py

## Acceptance criteria
1. `test_surfaces_sharing_an_attempt_keep_separate_spools` passes: after an `implement` run and a `review` run for stem `t-echo`, attempt 1, `spools/t-echo/1/implement/call-01/output.txt` and `spools/t-echo/1/review/call-01/output.txt` both exist and hold different text.
2. No production code writes a spool path whose call dir is not prefixed by a surface (checked by the `python -c` command in `## Verification`).
3. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_driver.py -k surfaces_sharing_an_attempt
uv run pytest -q tests/test_driver.py tests/test_echo_stage.py tests/test_triage.py
uv run python -c "import pathlib, re; bad = [str(p) for p in pathlib.Path('chupa').rglob('*.py') if re.search(r'f.call-\{call_seq', p.read_text())]; assert not bad, bad"
uv run pytest -q
```

## Regression
```
uv run pytest -q tests/test_driver.py -k surfaces_sharing_an_attempt
```
- carries: tests/test_driver.py

## Definition of rejected
The diff touches a file outside the fence, changes the provider-capture or verify-spool layout, alters journal effect keys, or keeps both the old and new spool layouts.

## Time budget
- expected: 20m
- stuck: 60m
