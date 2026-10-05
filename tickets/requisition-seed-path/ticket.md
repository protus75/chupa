---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: high
agent_effort: high
---

## Depends on
- requisition-author-path

## Context
- chupa/merge.py
- tests/test_merge.py
- tests/test_stages.py

## On-demand
- chupa/stages.py

## Plan contract
- 19.L
- 19.P2
- section 7
- section 9
- section 10

## Goal / Why
A phase-SEEDING ticket's `confirmed` seeds reach main only after each one passes intake lint AND an `approve` from `requisition_review` at the seeding ticket's own Check stage, and only through the ticket-plane lane. The merge pre-admission MERGE-SAFETY tier re-checks the same recorded verdicts, so it is the last point that can refuse a seeding branch whose seeds were not approved as committed.

Why: from the Phase 2 exit on, every phase boundary seeds the next phase by direct ticket-plane authoring (19.L seeding chain). Today a seeding ticket's Implement can write `tickets/<new-stem>/ticket.md` files into its worktree, but nothing reviews them, nothing lifts them, and the worktree wipe discards them. The drain's after-every-merge re-scan reads only committed tickets (section 18), so a seed that never commits never runs.

Known-deep (19.L KNOWN-DEEP: this contract crosses the stage-layer and merge-admission seams), so it starts `high`/`high`.

Owners (section 9 ownership law): `chupa/stages.py` owns stage-evidence gathering and the ONE stage-terminal lift path, so seed collection, the per-seed review at Check, and the seed lift live there. `chupa/merge.py` owns admission, so the MERGE-SAFETY re-check lives there. `chupa/requisition.py` is called, never changed.

## Scope in / Scope out
- In: `chupa/stages.py`:
  - `SeedReview`, closed: `stem`, `ticket_sha`, `verdict` (`approve | snag | rma`), `findings`, `mechanical` (nullable). `Invoice` gains `seeds: list[SeedReview] = []`, so every existing `checks.json` still parses.
  - A ticket is SEEDING exactly when its `## Scope fence` lists `tickets` (the whole-plane structural exception, section 9). For any other ticket nothing below runs.
  - Seed candidates are the worktree's `tickets/<s>/ticket.md` files with `s != <stem>` that are untracked or differ from main, in sorted stem order. A candidate whose stem already exists on main is an already-emitted seed when the journal carries a `ticket_intake` signal with `seeded_by == <stem>` for it and its bytes equal main's; it is skipped (19.L RE-RUN). Any other existing stem fails with finding code `requisition_review` (paved road: a seeding run only creates new stems).
  - After every mechanical Check gate passes, each new candidate is judged: `validate_ticket` against the worktree, frontmatter `source: seed` and `state: confirmed`, then `review_ticket` with `stem_slot=<stem>`, `run_seq=<the run sequence>`, `attempt=<the run sequence>`, `call_seq=<1-based candidate index>`, at the SEED's `agent_tier`. One render per seed, never a union over the batch (section 9). Each result is a `SeedReview` in `Invoice.seeds`, and a lint failure is recorded as `snag` with its findings and no call.
  - Any non-`approve` makes the Check `gate_failed` with a `requisition_review` gate report carrying every seed's findings, and NO seed is lifted.
  - All `approve`: after `checks.json` is lifted, `lift_seeds` makes ONE ticket-plane commit `chupa(<stem>): seeds` of the seed `ticket.md` paths only, through `driver.effects.run` keyed `ticket-plane/<stem>/<attempt>/seeds`. It moves each file out of the worktree and journals one authoring-commit event per seed: `{"signal": "ticket_intake", "source": "seed", "state": "confirmed", "new": true, "commit": <sha>, "seeded_by": <stem>}`.
- In: `chupa/merge.py`: `Candidate` gains `seeds`, gathered before the rebase: for every stem the journal shows this stem seeded, main's committed blob SHA and text, and main's `checks.json` `seeds` entries. A MERGE-SAFETY gate (code `requisition_review`) runs with the existing pre-rebase checks and fails unless each seeded stem has an `approve` entry whose `ticket_sha` equals main's committed blob SHA and main's text still passes `validate_ticket`. A refusal leaves main untouched, like every merge refusal.
- In: `tests/test_seed_path.py` drives the production `drive` over a seeding ticket whose scripted Implement writes two seeds into the worktree, with a FakeLLM serving implement, review, and requisition replies.
- Out: any `chupa/requisition.py`, `chupa/drain.py`, or `chupa/runner.py` change, a re-review at merge (the recorded verdict is re-checked, never re-called), the Phase 3 serial merge queue, and run-lane (no-code) admission.

## Scope fence
- chupa/stages.py
- tests/test_stages.py
- chupa/merge.py
- tests/test_merge.py
- tests/test_seed_path.py

## Acceptance criteria
1. `tests/test_seed_path.py` proves two approved seeds land as ONE `chupa(<stem>): seeds` commit on main, each journaling a `ticket_intake` signal with `seeded_by`, with `checks.json` `seeds` holding two `approve` entries and exactly two requisition requests keyed `llm/<stem>/0/requisition_review/0/1` and `.../2`.
2. `tests/test_seed_path.py` proves one `snag` seed fails the Check `gate_failed`, commits NO seed, and leaves the other seed's `approve` recorded; a seed authored `state: draft` or `source: human` fails without a requisition request.
3. `tests/test_seed_path.py` proves a re-run whose worktree re-writes an already-lifted own seed byte-identically skips it, and a candidate rewriting a foreign existing ticket fails the Check.
4. `tests/test_merge.py` proves the MERGE-SAFETY gate refuses a seeding branch whose seed's committed text no longer matches its recorded `ticket_sha`, with main untouched, and admits one whose seeds all match.
5. `tests/test_stages.py` proves a non-seeding ticket that leaves a foreign `ticket.md` in its worktree gets no seed review and no seed lift, and an old `checks.json` without `seeds` still parses.
6. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_seed_path.py tests/test_stages.py tests/test_merge.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- A seed reaches main without an `approve` for its exact committed text, or through the code lane.
- A seeding run rewrites an existing ticket, or a seed is reviewed as part of a batch blob.
- The merge re-calls the model, or a second lift path exists.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
