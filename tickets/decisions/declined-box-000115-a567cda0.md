---
id: declined-box-000115-a567cda0
kind: declined
link: box-000115-a567cda0
reopen_after_days: 90
---
The note says a ticket's `gate_bypass` valve also applies to `correctness_review` at merge. Listing that code makes the pinned Review approval soft for that ticket, so the ticket could merge without a current approval. The note asks the frozen plan's section 7 to say whether the approval can be bypassed.

The mechanism is real: `merge` passes `check_severity` to `MERGE_GATES`, and that applies every `gate_bypass` code, including `correctness_review`. But nothing shows it has caused harm. A bypass needs human sign-off first: `policy.start_state` keeps any engine-authored box ticket that carries `gate_bypass` in `draft` until a human confirms it, and a human-authored ticket's bypass is an operator decision. The message's actual ask is to reword `CHUPA_PLAN.md`, which is frozen and never edited. It cites no ticket that merged without a current approval, so there is no observed incorrect runtime behavior to repair.

- chupa/merge.py:300-301 runs MERGE_GATES (which include ApprovalGate, code `correctness_review`) with `check_severity(ctx, ticket)`
- chupa/stages.py:1330-1338 `check_severity` makes every `gate_bypass` code soft, with only a `ticket_schema` carve-out for retro_finding tickets
- chupa/policy.py:68 `start_state` returns `draft` for any box-authored ticket with a non-empty `gate_bypass`, so a human must confirm the bypass
- CLAUDE.md: `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited; the requested change is plan wording

Message: box-000115-a567cda0
