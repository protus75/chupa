---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- retro-reemit-skip

## Context
- chupa/retro.py
- docs/how-chupa-works.md

## On-demand
- chupa/specs/retro.md
- chupa/box.py
- tests/integration/test_retro.py
- tests/integration/test_retro_box.py

## Goal / Why
Each retro sees only its own window. It never sees the findings earlier retros already filed, so a failure that keeps happening is filed again as a new `retro_finding` every time, in new words. Box dedupe matches only identical hashes, so reworded repeats are never matched. On 2026-11-11, the 55 `retro_finding` messages were mostly a handful of failures filed again and again:

- "requisition review approved a ticket whose fence or regression was wrong": retro/9, 15, 28 (twice), 29, 30, 33, 36, 37, 39.
- "Implement claimed `premise_failed` early or falsely": retro/15, 16, 25, 30, 32, 40.
- "reviewer wrapped its JSON verdict in prose": retro/1, 4, 5, 39, 40.
- "Implement replied `ok` after running only `## Verification`": retro/24, 33, 36, 40.

Every repeat after a merged fix means the fix did not work, and nothing says so.

When this ticket is done, the retro sees the existing findings and marks a proposal that repeats one with `recurs`. A recurrence counts on the existing message instead of filing a new one. When the existing finding's fix ticket has merged, the recurrence reopens it as pending with `reopen` set, so the operator sees that the fix did not hold.

## Scope in / Scope out
- In: `chupa/retro.py`:
  - The retro render gains a `prior_findings` input: every `retro_finding` box message as `{id, fixed_failure, status, resolution_kind, resolution_link, fix_merged}`. `fix_merged` is true when the resolution is a `ticket` whose stem's last journal state is `merged`. It is computed in Python, never by the model.
  - `RetroProposal` gains an optional `recurs`: the id of an existing `retro_finding`. A reply whose `recurs` names an id not in `prior_findings` fails validation and goes back to the model as a retry finding, like any other schema error.
  - `emit_proposals`: a proposal with `recurs` files no new message. It records one recurrence on the named message, keyed by an occurrence id from `arrival_id("retro-recurrence", report_key, proposal_id)`, so a re-emit after a crash, or on any later drain start, counts it once. If the named message is resolved as a `ticket` whose stem merged, the recurrence also reopens it: `status` `pending`, `resolution` and `verdict` cleared, and `reopen` true. Every other state (pending, tombstone, declined, or a fix not yet merged) only counts the recurrence. Tombstones keep their existing three-report reopen rule.
  - The re-emit skip from `retro-reemit-skip` also skips a `recurs` proposal whose occurrence is already recorded.
- In: `chupa/box.py`: whatever minimal method or field the recurrence record and reopen need, through the existing write-ahead re-report receipts. No second receipt mechanism.
- In: `chupa/specs/retro.md`: a `prior_findings` data block, and a Task rule to set `recurs` when a proposal fixes the same failure as an existing finding, judged by cause rather than wording. Its `version` goes from `1.3` to `1.4`, and `tests/integration/test_retro.py`'s pinned `"1.3"` follows.
- In: `docs/how-chupa-works.md`: the retro paragraph (around "files each proposal as a `retro_finding`") and the tombstone-and-reopen list item describe recurrences and the fix-did-not-hold reopen.
- Out:
  - Embeddings, vector search, DuckDB, or any new dependency. The whole `prior_findings` list goes into the prompt; at 55 findings it is about 6k characters.
  - Matching suggestions or failure reports, which are other message classes.
  - Merging or rewriting the existing duplicate messages.

## Scope fence
- chupa/retro.py
- chupa/box.py
- chupa/specs/retro.md
- docs/how-chupa-works.md
- tests/integration/test_retro.py
- tests/integration/test_retro_box.py
- tests/unit/test_retro_recurrence.py

## Acceptance criteria
1. `tests/unit/test_retro_recurrence.py`: the `prior_findings` render input lists every `retro_finding` box message with the six fields. `fix_merged` is true only for a `ticket` resolution whose stem's last journal state is `merged`, and false for a ticket still running, a tombstone and a pending message.
2. `tests/unit/test_retro_recurrence.py`: a retro reply whose `recurs` names an id not in `prior_findings` is rejected with a retry finding, not filed.
3. `tests/integration/test_retro_box.py`, with a `FakeLLM` retro reply carrying `recurs`:
   - For a pending finding: no new box message is created, and the named message's recurrence count rises by exactly 1.
   - For a finding resolved as a `ticket` whose stem is `merged`: the message becomes `pending` with `reopen` true and no resolution.
   - For a finding resolved as a `ticket` still `running`: the count rises, and the message stays resolved.
   - Running `emit_proposals` for the same report twice leaves the count and the box files as after the first run, not counted twice.
4. `tests/integration/test_retro.py` passes with the spec version pin updated to `"1.4"`.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- A recurrence creates a new box message.
- A re-emit of the same report counts a recurrence more than once.
- Duplicate matching runs anywhere but in the retro model's reply (no Python text similarity, no embeddings).
- A finding whose fix has not merged is reopened.

## Time budget
- expected: 60m
- stuck: 120m
