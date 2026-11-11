---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/author.py::AuthorGate
- chupa/author.py::author
- chupa/requisition.py::review_ticket
- tests/unit/test_author.py
- tests/regress_author_open_tickets_deleted.py

## On-demand
- tests/integration/test_author.py

## Goal / Why
The Author stage throws away box messages because its own gate refuses the stem it is revising (`evidence/evidence.txt`). Three messages were declined this way: box-000297 (2026-11-09), box-000391 and box-000397 (2026-11-11). Each decision record's only evidence is `stem '<stem>' is already named in the journal`.

The sequence: an author reply passes `AuthorGate.check`, then `review_candidate` runs requisition review on it. `review_ticket` journals its LLM calls with `ticket=<stem>` (`chupa/requisition.py`, the `llm_call(..., ticket=stem, ...)` call). The review snags, and `chupa/specs/author.md` tells the model to start from `previous_reply` and change only what the findings name, so it keeps the stem. The next `AuthorGate.check` finds that stem on the review events this same invocation just wrote and fails with "already named in the journal". The paved road says to choose a new stem; a rename then gets reviewed, snags again, and collides again. Every snag costs one call this way, and the call allowance runs out. For all three refused stems, the only journal events naming them are the same invocation's `llm/author/<pass>/requisition_review/<seq>/<n>` events, and no `tickets/<stem>/` exists on disk.

The existing tests miss this because every snag test in `tests/integration/test_author.py` renames the stem on revision (`first` then `second`).

After this change, an `AuthorGate` admits a stem that it already passed during the same invocation, even when the journal now names that stem. A stem that the journal names from anything else is still refused, including a stem drafted by an earlier invocation.

## Scope in / Scope out
- In: `chupa/author.py` `AuthorGate` keeps a set of the stems it passed. `check` adds the stem to the set when it returns `pass`. The "already named in the journal" finding is skipped for a stem in that set. The disk check, `stem_findings`, the report-custody handling, and the finding text and paved road all stay unchanged.
- In: `tests/unit/test_author.py` adds `test_gate_admits_own_passed_stem_only`. It builds `AuthorGate(SimpleNamespace(repo=Path("/repo"), journal=SimpleNamespace(read=lambda: events)))` with a list `events`, and monkeypatches `chupa.author.validate_ticket` to return `None`, so no disk is read (the gate reads `parsed` only when the message carries a report, and `message` stays `None`). It checks `AuthorReply(stem="draft-stem", ticket="t")` and gets `pass`. It then appends `SimpleNamespace(ticket="draft-stem", key="llm/author/1/requisition_review/7/1")` to `events` and checks again on the same gate, expecting `pass`. A fresh `AuthorGate` over the same `events` checking the same reply gets `fail`, with a finding message containing `already named in the journal`.
- In: `tests/integration/test_author.py` adds `test_author_snag_revision_keeps_stem`. It follows `test_author_snag_reprompts_then_approve` but replies `author_reply("first")` both times: `FakeLLM([reply("author"), author_reply("first"), requisition_reply("snag", [SNAG]), author_reply("first"), requisition_reply("approve")])`. `_run` returns 0, `tickets/first/ticket.md` exists, there are exactly 2 `author` requests, neither rendered prompt contains `already named in the journal`, and the box message resolves to `Resolution(kind="ticket", link="first")`.
- In: new `tests/regress_author_gate_own_draft_stem.py`, the carried reproducer. It follows `tests/regress_author_open_tickets_deleted.py`: it puts the repo root on `sys.path`, imports `chupa.author`, and sets `author.validate_ticket = lambda stem, text, repo: None`. It runs the same three checks as the unit test, using a temporary directory as `repo`.
  - The gate-local second check passes and the fresh-gate check fails with the journal finding: prints `{"regression_result": "pass"}` and exits 0.
  - The gate-local second check fails with a finding containing `already named in the journal`: prints `{"regression_result": "defect"}` and exits 1.
  - Anything else (an import failure, the first check failing, the fresh-gate check passing, another exception): writes the detail to stderr, prints `{"regression_result": "error"}` and exits 2.
- Coverage: `chupa/author.py` has a floor of 13 under `[coverage.files]` in `test-gate.toml`. The new unit test runs the added set lines, the add on pass, and both outcomes of the skip.
- Unaffected coverage dependents of `chupa/author.py`: `tests/integration/test_box.py`, `test_cli.py`, `test_inbox.py`, `test_retro.py`, `test_retro_box.py` and `test_triage.py`. Each one authors at most one stem per invocation and never revises a stem the gate already passed, so the exemption never fires in them. `tests/integration/test_author.py` is fenced, and its existing tests keep their outcomes for the same reason; `test_author_reprompts_for_reused_stem_and_invalid_ticket` refuses `existing` through the disk check, which is unchanged.
- Out: changing `review_ticket` or how requisition review journals its calls; making declined draft stems reusable across invocations; changing the Author spec or its paved road; recovering the three declined messages (an operator re-suggests them after this merges).

## Scope fence
- chupa/author.py
- tests/unit/test_author.py
- tests/integration/test_author.py
- tests/regress_author_gate_own_draft_stem.py

## Acceptance criteria
1. `uv run python tests/regress_author_gate_own_draft_stem.py` prints `{"regression_result": "pass"}` and exits 0 on the branch head. It prints `defect`, not `pass`, when the same gate refuses its own passed stem, and `error`, not `pass`, when a fresh gate admits a journal-named stem.
2. `./dev.py test tests/unit/test_author.py` passes `test_gate_admits_own_passed_stem_only`. A second check on the same gate returns `pass`, not `fail`, and a fresh gate returns `fail`, not `pass`, so neither keeping the bug nor deleting the journal check passes it.
3. `./dev.py test tests/integration/test_author.py` passes `test_author_snag_revision_keeps_stem`. The message resolves to ticket `first` after exactly 2 author calls, not a `declined` record after the call allowance runs out.
4. `./dev.py test` exits 0.

## Verification
```
uv run python tests/regress_author_gate_own_draft_stem.py
./dev.py test tests/unit/test_author.py
./dev.py test tests/integration/test_author.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the journal check is removed or weakened for stems the gate did not pass in this invocation;
- the exemption matches journal event keys or bodies (such as an `llm/author/` prefix) instead of the gate's own passed stems;
- `chupa/requisition.py` or the Author spec changes;
- the reproducer prints `pass` on the merge base.

## Time budget
- expected: 20m
- stuck: 60m

## Regression
```
uv run python tests/regress_author_gate_own_draft_stem.py
```
- carries: tests/regress_author_gate_own_draft_stem.py
