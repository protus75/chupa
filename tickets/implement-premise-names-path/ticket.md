---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Runs before
- commit-lock

## Context
- chupa/stages.py::ImplementReply
- chupa/stages.py::implement
- chupa/driver.py::Driver.run
- tests/regress_requisition_park_not_attempt.py

## On-demand
- tests/integration/test_requisition_gate.py

## Goal / Why
`chupa/specs/implement.md` allows `premise_failed` only when the ticket cannot be done as written: the bug does not reproduce, the criteria contradict existing behavior or each other, or the change forces an edit outside `## Scope fence`. The engine accepts any `premise_failed` reply whose findings are coded `premise`. With `premise_bounce: 1`, an Implement `premise_failed` routes the ticket straight to the Reject queue.

On 2026-11-11, codex (gpt-6.1-terra) twice replied `premise_failed` on `commit-lock` without a premise. Each time it made no change, and the run took 118 and 32 seconds of a 3-hour budget. Its findings said "I could not complete the implementation and verification in this attempt; no contradiction or missing scope has been established" and "no ticket premise failure was established". Neither finding named a path. Each sent a ticket that had just passed requisition review back to the Reject queue (see `evidence/implement-premise-giveups.txt`). Across every recorded Implement `premise_failed` in `tickets/*/attempts/*/harvest.json`, 602 of 608 `premise` findings name a `path`. The other 6 are these two give-ups and four that could have named the failing or missing file.

When this ticket is done, every `premise` finding in an Implement reply must name a `path`: the file outside the fence, the file whose behavior the criteria contradict, or the ticket. A reply that does not is schema-invalid. `Driver.run` then re-prompts the same call with the validation message as `retry_findings` (as it does for any invalid artifact). That message tells the agent that unfinished work is not a premise failure and to implement the ticket.

## Scope in / Scope out
- In: `chupa/stages.py::ImplementReply._findings_match_outcome`: for `premise_failed`, every finding must also have a non-empty `path`. The `ValueError` message reads: "premise_failed needs at least one finding, every code `premise` and every one naming `path` (the file outside the fence, the file the criteria contradict, or the ticket); unfinished or large work is not a premise failure: implement the ticket and reply ok".
- In: `chupa/specs/implement.md`:
  - The Output format sentence "`premise_failed` carries at least one finding, every one coded `premise`." becomes "`premise_failed` carries at least one finding, every one coded `premise` and naming its `path`."
  - The `premise_failed` bullet gains one sentence: running out of time, or a change that is only large, is never `premise_failed`.
  - `version` goes from "2.9" to "2.10".
- In: `tests/unit/test_specs.py` pins `implement` at "2.10" in both places that pin "2.9".
- In: every test fixture or harness that scripts an Implement `premise_failed` reply gives each `premise` finding a `path`, using the ticket path `tickets/<stem>/ticket.md` where no other file fits. The files are:
  - `tests/integration/test_requisition_gate.py`
  - `tests/integration/test_reject_queue.py`
  - `tests/integration/test_terminal.py`
  - `tests/integration/test_audit.py`
  - `tests/integration/serve_rig.py`
  - `tests/integration/test_second_problems.py`
  - `tests/integration/test_caps.py`
  - `tests/harness/shakeout/drain.py`
  - `tests/harness/shakeout/runner.py`
- In: the carried reproducer `tests/regress_implement_premise_path.py` (see Regression). It is self-contained and imports nothing from `tests/`. It validates an `ImplementReply` JSON with outcome `premise_failed` and one `premise` finding with no `path`. It prints `pass` (exit 0) when validation raises `ValidationError`, and `defect` (exit 1) when it is accepted.
- Out:
  - Re-prompt mechanics in `chupa/driver.py`, which already re-prompt an invalid artifact.
  - Requisition, Review and Diagnose replies.
  - `premise_bounce` and Reject queue routing.
  - Provider routing in `config.yaml`.

## Scope fence
- chupa/stages.py
- chupa/specs/implement.md
- tests/unit/test_specs.py
- tests/unit/test_implement_premise_path.py
- tests/regress_implement_premise_path.py
- tests/integration/test_stages.py
- tests/integration/test_requisition_gate.py
- tests/integration/test_reject_queue.py
- tests/integration/test_terminal.py
- tests/integration/test_audit.py
- tests/integration/serve_rig.py
- tests/integration/test_second_problems.py
- tests/integration/test_caps.py
- tests/harness/shakeout/drain.py
- tests/harness/shakeout/runner.py

## Acceptance criteria
1. New `tests/unit/test_implement_premise_path.py` validates `ImplementReply` in memory and keeps the `test-gate.toml` unit floor for `chupa/stages.py`:
   - A `premise_failed` reply whose `premise` finding has `path: null` raises `ValidationError` whose text contains `naming \`path\`` and `implement the ticket`. Accepting it fails the test.
   - A `premise_failed` reply whose findings all have a `path` validates.
   - An `ok` reply with no findings still validates.
2. `tests/integration/test_stages.py`: a `FakeLLM` that first replies `premise_failed` with a pathless `premise` finding and then replies `ok` makes Implement call the provider twice. The second rendered prompt's `retry_findings` contains `implement the ticket`, and the stage ends `ok`, not `premise_failed`.
3. `tests/unit/test_specs.py` asserts `implement` is version "2.10".
4. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch, and prints `defect` with a non-zero exit at the merge base.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- An Implement `premise_failed` reply with a pathless `premise` finding is accepted.
- `chupa/driver.py`'s re-prompt or retry count changes.
- A `premise_failed` reply whose findings all name a path is refused.

## Time budget
- expected: 30m
- stuck: 60m

## Regression
```
uv run python tests/regress_implement_premise_path.py
```
- carries: tests/regress_implement_premise_path.py
