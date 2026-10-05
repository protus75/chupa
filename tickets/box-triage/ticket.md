---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- box-start-policy
- suggestion-box

## Context
- chupa/driver.py
- chupa/__main__.py
- tests/test_drain.py

## Plan contract
- 19.L
- 19.P2
- section 12
- section 8

## Goal / Why
`chupa triage` is the Suggestion Box's sequential consumer in the BOOTSTRAP era (section 12). It makes ONE pass over every pending box message, in seq order, and resolves each one: a tombstone onto the existing ticket or decision it duplicates, a decision record, or an `author` verdict. Then it stops.

An `author` verdict invokes Author in the same pass once Author exists. Until the Author stage (`chupa/author.py`, 19.P2) merges, the message rests `pending` with its verdict recorded and a paved road naming that deliverable. The bootstrap drain NEVER scans the box, neither before a dispatch nor after a merge. Only the operator's verb consumes it.

Why: harvest, the run record, and the `reject` verb now file into the box, but nothing reads it. A filed problem, including the ticket change that would release a parked stem, never becomes work. Section 12's admission bar keeps the box from turning into an accretion engine: cleanup, speculative hardening, and plan-wording nits become decision records, not tickets. The bootstrap era is operator-triggered because a human is present at every scan. The daemon-era continuous consumer (sections 9, 12) is a separate era, built with the daemon, never folded in here.

Owners (19.P2 NAMES): `chupa/triage.py` / `tests/test_triage.py` own the consumer, its closed reply model, decision-record writing, and the record's ticket-plane commit. `specs/triage.md` is the ONE triage spec: per-class guidance lives inside it, never a spec file per class (section 12). `chupa/driver.py` owns the effect-key shape a ticketless call needs. `chupa/__main__.py` is the CLI entry. `chupa/box.py` (from `suggestion-box`) owns the queue and registry format and is called, never changed.

## Scope in / Scope out
- In: `specs/triage.md`, lint-clean under `lint_spec`:
  - Frontmatter `llm_surface: triage`, `consumes: box-message`, `emits: triage-verdict`, `tier: medium`, `effort: medium`, `gates: []`, `version: "1.0"`, with exactly the sections Role, Task, Inputs, Output format, On-failure.
  - Data blocks, each a lone placeholder line, in this order: `message`, `open_tickets`, `merged`, `decisions`, `retry_findings`. Every block is marked untrusted.
  - The Task states section 12's admission bar. `author` only when the message or its evidence shows a current, materially harmful behavior gap, bounded to one buildable ticket, with a measurable post-change observation. A plan-wording mismatch, speculative hardening, cleanup, refactor, style preference, or test-only improvement is a `decision` unless it is tied to reachable incorrect runtime behavior.
  - `tombstone` when the message duplicates an open or merged ticket or an existing decision (semantic match, not string match), with `link` naming it.
  - One short paragraph per message class gives class-specific guidance. The model applies the paragraph matching the message's class.
- In: `chupa/triage.py`:
  - `TriageReply`, closed and strict, with fields `verdict` (`author | tombstone | decision`), `link` (a string, required non-null exactly for `tombstone`), `summary` (non-blank: triage's OWN summary, never the raw message text), `rationale` (non-blank), `evidence` (list of strings), and `reopen_after_days` (int >= 1, required for `tombstone` and `decision`, null for `author`).
  - Engine constant `TRIAGE_STUCK_S = 600.0`.
  - `async def triage_pass(...) -> list[tuple[str, str]]` returns one (message id, outcome line) per pending message. It first journals `{"signal": "triage_pass", "pass": n}`, where `n` counts prior `triage_pass` signals. Then, for each pending message in seq order:
    1. If `read_registry` already holds a record with id `<kind>-<message id>` (the pass crashed after its commit), resolve the message from it with no call.
    2. A recorded `author` verdict whose `produced_by_spec_version` differs from the current `specs/triage.md` version becomes a `decision` record with both versions as evidence. There is no model call.
    3. A recorded `author` verdict at the current version stays pending with no call. Its line reads `author verdict recorded; waits for the Author stage (chupa/author.py, 19.P2) -- run chupa triage again after it merges`.
    4. Otherwise the pass renders the spec and calls the `driver.run` method with `ticket=None`, `run_seq=<message seq>`, `attempt=<pass>`, the workspace the repo, tier `config.routing_default_tier`, the spec's effort, and stuck budget `TRIAGE_STUCK_S`.
       - The `message` block carries the message's class, summary, origin, stage, and outcome.
       - `open_tickets` lists each committed non-merged stem with its `## Goal / Why` first line.
       - `merged` lists the merged stems from the journal.
       - `decisions` lists each registry record's id, kind, link, and first body line.
       - A non-ok driver outcome leaves the message pending with no verdict and reports the outcome.
  - An `ok` reply is resolved by its verdict:
    - `tombstone`: the link must resolve to a committed `tickets/<stem>/ticket.md`, a merged stem, or a registry id. Write a `tombstone` record linking it, then resolve the message as `tombstone`. An unresolvable link writes a `decision` record instead, naming the bad link as evidence.
    - `decision`: write a `decision` record linking the message id, then resolve the message as `decision`.
    - `author`: `record_verdict` with the current spec version, and the message stays pending, as in step 3.
  - A record has id `<kind>-<message id>`. Its body is the reply's summary, rationale, and evidence bullets, plus `Message: <message id>`. The raw message summary never enters it.
  - Each record is written at `record_path(id)` and committed as ONE ticket-plane commit `chupa(decisions): <id>` of that path only, through `driver.effects.run` keyed `ticket-plane/decisions/<id>`. The message is resolved only after the commit.
- In: the `driver.run` method gains keyword `run_seq: int | None = None`. Given it (only valid with `ticket=None`, else `ValueError`), it replaces the journal-folded run sequence in the LLM effect key and spools under `<surface>/<run_seq>/<attempt>/`. A triage call is therefore keyed `llm/triage/<seq>/triage/<pass>/<call_seq>` (section 6), and two messages in one pass never share a key or a spool dir. Every existing call is unchanged.
- In: a `triage` CLI verb in `chupa/__main__.py`. It acquires the single-writer lock (contention exits 2 like `run`), runs one `triage_pass` with the production provider seam, prints one line per message (`no pending suggestions` when empty), and exits 0.
- In: `tests/test_drain.py` adds one test. With a pending box message present, a drain that dispatches and merges a ticket makes no `triage` request, journals no `triage_pass`, and leaves the message pending.
- Out: the Author stage and invoking it, any ticket authoring, `requisition_review`, and the draft starting state (`chupa/policy.py` resolves it for Author). Also out: dedup-onto-tombstone re-report counting and auto-reopen (Phase 5), the storm breaker (Phase 3), the daemon's continuous consumer, host bug evidence copying (Phase 6), and the triage-dedup eval (deferred, section 18).

## Scope fence
- chupa/triage.py
- specs/triage.md
- tests/test_triage.py
- chupa/driver.py
- chupa/__main__.py
- tests/test_drain.py

## Acceptance criteria
1. The `python -c` command in `## Verification` exits 0: `specs/triage.md` loads through `load_spec` with `llm_surface == "triage"` and data blocks `message`, `open_tickets`, `merged`, `decisions`, `retry_findings`.
2. `tests/test_triage.py` drives `chupa.__main__.main(["triage"])` with a FakeLLM over three pending messages replying `tombstone` (linking an existing ticket), `decision`, and `author`. Main gains two `chupa(decisions): <id>` commits whose records parse through `parse_record` with the right kind, link, and `reopen_after_days`. The first two messages are `resolved`. The third is pending with a recorded `author` verdict, and stdout names `chupa/author.py`. Exactly three `triage` requests are made, at `routing_default_tier`, with distinct effect keys `llm/triage/<seq>/triage/0/1`.
3. `tests/test_triage.py` proves a second `triage` pass makes ZERO requests: the resolved messages are skipped, and the recorded `author` verdict at the current version stays pending. Re-recording that verdict at a stale version resolves it as a `decision` with no request.
4. `tests/test_triage.py` proves fail-closed handling. A tombstone whose link resolves nowhere writes a `decision` record. A record already committed for a pending message resolves it with no request. A reply invalid through every re-prompt leaves the message pending and commits nothing.
5. `tests/test_triage.py` proves the raw message summary (a unique marker) appears in no committed record, and that the `triage` verb exits 2 while another holder has the lock.
6. The new `tests/test_drain.py` test passes, and every existing `tests/test_drain.py` assertion is unchanged.
7. `uv run pytest -q tests/test_driver.py` passes with no edit.
8. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -c "from pathlib import Path; from chupa.specs import load_spec; s = load_spec(Path('specs/triage.md').read_text()); assert s.meta.llm_surface == 'triage' and s.inputs == ('message', 'open_tickets', 'merged', 'decisions', 'retry_findings')"
uv run pytest -q tests/test_triage.py tests/test_drain.py
uv run pytest -q tests/test_driver.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- The drain, or anything it calls, reads or consumes the box.
- A ticket is authored, or a message is resolved before its record commits.
- A box message file is deleted, or raw message text enters a committed record.
- A second spec file per class, or a second Driver or LLM-effect path for the triage call, exists.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
