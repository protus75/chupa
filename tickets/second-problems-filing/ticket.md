---
state: confirmed
source: seed
priority: P1
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- suggestion-box

## Context
- chupa/artifacts.py
- chupa/stages.py

## On-demand
- specs/implement.md

## Plan contract
- 19.L
- 19.P2
- section 12

## Goal / Why
Every second problem an Implement agent reports becomes a `suggestion` message in the Suggestion Box. The run record's `## Second problems filed` section lists each one's box id. This is the machine route section 11.7 prescribes: the agent leaves an out-of-scope problem alone, records it in the run record, and files it as schedulable work.

Why: `specs/implement.md` tells the agent to mention a second problem in `surprises`, and `run_record` writes `## Second problems filed` as a fixed `none`. A noticed problem is therefore prose nobody triages. A parked stem's real fix (a wrong plan line, a pre-existing red test) is lost unless a human reads the run record. Section 12's producer rule ("harvest enqueues each run record's second problems") needs the problems as data first. Filing them where the run record is written covers EVERY reply that writes one (`ok`, `already_satisfied`, and `premise_failed`). Harvest's `run_record` path then points at a record whose ids name the filed messages.

Owners (section 9 ownership law): `chupa/stages.py` owns the `ImplementReply` model, the run-record writer, and the `implement` stage that writes and lifts `run.md`, so it owns the enqueue. `chupa/box.py` (from `suggestion-box`) owns the queue and the signature recipe, and is called, never copied. `specs/implement.md` is the governed spec for the reply shape.

## Scope in / Scope out
- In: `chupa/stages.py` gains `SecondProblem`, a closed strict model with one field, `summary` (non-blank). `ImplementReply` gains `second_problems: list[SecondProblem] = []`, so an absent key means none. Every existing reply without the key still validates.
- In: in `implement`, after a schema-valid reply and BEFORE `run.md` is written, each second problem is enqueued with `Box(ctx.config.state_dir / BOX_DIR, ctx.fs).enqueue(message_class="suggestion", origin=<stem>, stage="implement", outcome=<reply.outcome>, summary=<summary>)`. `run_record` takes the resulting ids and renders `## Second problems filed` as one bullet per problem, in reply order, `- <id>: <summary flattened to one line>`, or `none` when there are none. A deduped enqueue lists the existing id.
- In: `specs/implement.md`:
  - The Task's "A second problem you notice is reported in `surprises`, never fixed in this diff" becomes: report it in `second_problems`, never fix it in this diff, and verify that a failure you did not cause also fails on the base commit before reporting it (section 11.7).
  - The Output format documents `"second_problems": [{"summary": "<one problem, one sentence>"}]`, empty when there are none.
  - `version` becomes `"1.1"`. It must stay lint-clean under `lint_spec`.
- Out: any other producer (the `reject` verb's dead-dependency reports, base-red attribution, ingesting outbox box-message files at lift), and any second-problem filing from Review or Check.
- Out: the triage consumer, any change to `chupa/box.py`, the `Harvest` schema, `prior_attempts`, or the run-record section set.

## Scope fence
- chupa/stages.py
- specs/implement.md
- tests/test_second_problems.py

## Acceptance criteria
1. The `python -c` command in `## Verification` exits 0: `specs/implement.md` loads through `load_spec` at version `1.1`, and its text names `second_problems`.
2. `tests/test_second_problems.py` drives `chupa.__main__.main(["run", ...])` with a FakeLLM whose implement reply carries two `second_problems`. Two `suggestion` messages exist in `<state_dir>/box/`, each with `origin` equal to the stem, `stage` `implement`, and `outcome` `ok`. The lifted `tickets/<stem>/run.md` on main lists both ids under `## Second problems filed`, in reply order.
3. `tests/test_second_problems.py` proves dedup and the empty case. A second run whose reply repeats a summary differing only in a line number lists the SAME id and adds no message file. A reply with no `second_problems` key writes `none` and creates no box dir entry.
4. `tests/test_second_problems.py` proves a `premise_failed` reply carrying a second problem still files it, with `outcome` `premise_failed`, and its run record lists the id.
5. `uv run pytest -q tests/test_stages.py tests/test_terminal.py tests/test_drain_reentry.py` passes with no edit to those files.
6. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "from pathlib import Path; from chupa.specs import load_spec; t = Path('specs/implement.md').read_text(); assert load_spec(t).meta.version == '1.1' and 'second_problems' in t"
uv run pytest -q tests/test_second_problems.py
uv run pytest -q tests/test_stages.py tests/test_terminal.py tests/test_drain_reentry.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A second problem is fixed in code or written into `ticket.md`.
- A second enqueue or signature path exists outside `chupa/box.py`.
- An existing reply shape without `second_problems` stops validating.
- `## Second problems filed` lists a summary with no box id.
- The diff touches a file outside the fence.

## Time budget
- expected: 45m
- stuck: 90m
