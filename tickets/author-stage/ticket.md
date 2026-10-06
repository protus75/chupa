---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- box-triage
- box-start-policy

## Context
- chupa/git.py
- tests/test_git.py
- tests/test_eval_harness.py

## Plan contract
- 19.L
- 19.P2
- section 8
- section 12
- section 13

## Goal / Why
The Author stage (Requisition, section 4) turns a triaged `author` verdict into ONE committed `tickets/<stem>/ticket.md` in the same `chupa triage` pass. The ticket is stamped `source: box:<class>`, its starting state comes from `chupa/policy.py`, and its commit journals the per-stem authoring-commit event the eligibility sort's age term reads (section 9).

Why: `box-triage` records an `author` verdict and leaves the message pending with a paved road naming this deliverable. Nothing turns a filed problem into work, so the machine route from a parked stem's filed fix to the ticket change that releases it is dead (section 12). Phase 1 deferred the stage because nothing executed it (19.P1).

Owners (19.P2 NAMES and BOX): `chupa/author.py` / `tests/test_author.py` own the stage: its closed reply model, its gate, its render, the ticket-plane commit, and the failure decision record. `specs/author.md` is the ONE author spec. `chupa/triage.py` (from `box-triage`) owns the pass and gains the invocation. `chupa/git.py` owns the new tracked-file listing op. `chupa/policy.py` (from `box-start-policy`) and `chupa/box.py` (from `suggestion-box`) are called, never changed. `chupa/tickets.py` is read for `validate_ticket` and `stamp`, never changed.

## Scope in / Scope out
- In: `specs/author.md`, lint-clean under `lint_spec`:
  - Frontmatter `llm_surface: author`, `consumes: triage-verdict`, `emits: ticket`, `tier: medium`, `effort: medium`, `gates: [ticket_schema]`, `version: "1.0"`, with exactly the sections Role, Task, Inputs, Output format, On-failure.
  - Data blocks, each a lone placeholder line, in this order: `request`, `files`, `open_tickets`, `retry_findings`. Every block is marked untrusted.
  - The Task states the section 13 ticket contract (sections, grammar, the anti-bloat frontmatter list, `medium`/`medium` defaults) and section 12's mechanical PREFLIGHT the model runs before replying: every list item starts `- `; `Depends on` is `- none` or stem bullets; each acceptance criterion names, in backticks, an exact substring of a `## Verification` command or an observable repository path; a bug's `## Regression` is exactly one fenced command plus one or more `- carries: <path-prefix>` bullets; on a re-prompt, repair every supplied finding and keep already-valid sections byte-identical.
  - The Output format is one JSON object `{"stem": "<new stem>", "ticket": "<the full ticket.md text>"}`. The model never writes `state` or `source`: the stage stamps both.
- In: `chupa/author.py`:
  - `AuthorReply`, closed and strict: `stem` (non-blank) and `ticket` (non-blank).
  - Engine constant `AUTHOR_STUCK_S = 900.0`.
  - `AuthorGate` (code `ticket_schema`) over a stamped candidate. It fails, with a paved road per finding, when the stem fails `stem_findings`, when `tickets/<stem>/` exists or any journal event names the stem (a stem is never reused), or when `validate_ticket` refuses the stamped text. It passes `lint_gate`.
  - `async def author(...) -> AuthorOutcome` for one pending message carrying a recorded `author` verdict:
    1. Validate the policy inputs BEFORE any paid call: `policy_row(message_class, bug_origin, has_repro)`. A `ValueError` writes the failure decision record (step 5) with no call.
    2. Journal `{"signal": "author_invoked", "message": <id>}` on no ticket, then call `driver.run` with `ticket=None`, `run_seq=<pass>`, `attempt=<message seq>`, tier `config.routing_default_tier`, the spec's effort, and stuck budget `AUTHOR_STUCK_S`. The call is keyed `llm/author/<pass>/author/<seq>/<call_seq>` (section 6). The render stamps `source: box:<class>` and a provisional `state: draft` into the reply's frontmatter with `stamp`, then `AuthorGate` judges it; a hard failure re-prompts within the driver's local allowance sized from `caps.retry` (section 11.1: pre-lineage, never the journal cap fold).
    3. On `ok`, resolve the starting state: `start_state(config, row=..., fence=<parsed Scope fence>, gate_bypass=<parsed gate_bypass>, go=go_binds(events, baseline_identity(config, specs_dir)))`, and stamp it.
    4. Write `tickets/<stem>/ticket.md` through the filesystem seam and make ONE ticket-plane commit `chupa(<stem>): ticket` of that path only, through `driver.effects.run` keyed `ticket-plane/<stem>/author`. Then journal the authoring-commit event `{"signal": "ticket_intake", "source": "box:<class>", "state": <state>, "new": true, "commit": <sha>}` on the stem (the same `INTAKE_SIGNAL` shape intake writes), then `resolve` the message `{kind: ticket, link: <stem>}`.
    5. Any other ending (a non-ok driver outcome, a commit failure) writes ONE `decision` record `decision-<message id>` carrying the failure evidence, committed exactly as `box-triage` commits records, and resolves the message as `decision`. No later pass invokes Author for it again. This step requires no deletion of an already-written `tickets/<stem>/ticket.md`: no `FileSystem` delete is needed, and `chupa/seams.py` is not edited.
  - The `request` block carries the message class, the recorded triage rationale, and the message summary quoted as untrusted data. `files` is the tracked-file listing. `open_tickets` lists each committed non-merged stem with its `## Goal / Why` first line.
- In: `chupa/triage.py`: an `author` verdict, and a recorded `author` verdict at the current spec version, invoke `author` in the same pass instead of resting pending, and the outcome line names the authored stem or the decision record. A pending message whose journal already carries an `author_invoked` signal for it (a pass that died mid-author) gets the failure decision record with no call. The stale-version rule is unchanged.
- In: `chupa/git.py` gains `ls_files(dir) -> list[str]`, running `ls-files` (the named tracked-file listing op, 19.P2 BOX).
- In: `tests/test_eval_harness.py`: the pre-Author expectation `author["spec_major"] is None` becomes `== 1` (19.P2 SUPERSEDED BEHAVIOR). No other assertion changes.
- Out: `requisition_review` and both its wirings (the next three seeds). Until they land, an authored ticket commits on grammar alone.
- Out: any `chupa/policy.py`, `chupa/box.py`, or `chupa/tickets.py` change, tombstone auto-reopen (Phase 5), host bug evidence copying (Phase 6), and phase seeding (seeds are never box-authored, section 12).

## Scope fence
- chupa/author.py
- specs/author.md
- tests/test_author.py
- chupa/triage.py
- tests/test_triage.py
- chupa/git.py
- tests/test_git.py
- tests/test_eval_harness.py

## Acceptance criteria
1. The `python -c` command in `## Verification` exits 0: `specs/author.md` loads through `load_spec` with `llm_surface == "author"` and data blocks `request`, `files`, `open_tickets`, `retry_findings`.
2. `tests/test_author.py` drives `chupa.__main__.main(["triage"])` with a FakeLLM: a `failure_report` message gets a triage `author` reply, then an author reply. Main gains one `chupa(<stem>): ticket` commit whose `ticket.md` passes `validate_ticket`, carries `source: box:failure_report` and `state: draft` (no GO is recorded), and the journal carries one `ticket_intake` signal on the stem. The message resolves `{kind: ticket, link: <stem>}`. The author request is keyed `llm/author/0/author/<seq>/1` at `routing_default_tier`.
3. `tests/test_author.py` proves an author reply naming an existing stem, and one failing `validate_ticket`, re-prompt with the findings, and that exhausting the allowance commits no ticket and resolves the message with one `decision-<id>` record.
4. `tests/test_author.py` proves a message whose journal carries `author_invoked` gets the failure decision record with ZERO author requests.
5. `tests/test_triage.py` passes with its `author`-verdict expectations moved from "rests pending" to "authors in the same pass", and every other assertion unchanged.
6. `tests/test_git.py` proves `ls_files` lists a committed file and omits an untracked one.
7. `uv run pytest -q tests/test_eval_harness.py` passes with only the `spec_major` expectation changed.
8. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "from pathlib import Path; from chupa.specs import load_spec; s = load_spec(Path('specs/author.md').read_text()); assert s.meta.llm_surface == 'author' and s.inputs == ('request', 'files', 'open_tickets', 'retry_findings')"
uv run pytest -q tests/test_author.py tests/test_triage.py tests/test_git.py tests/test_eval_harness.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A ticket commits without passing `validate_ticket`, or an authored ticket starts anything but the `start_state` result.
- A second ticket-writing path, a second Driver or LLM-effect path, or a second author spec exists.
- A message gets a second Author invocation, or resolves before its commit lands.
- The drain, or anything it calls, invokes Author or scans the box.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
