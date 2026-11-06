---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/requisition.py
- chupa/author.py
- tests/test_triage.py

## On-demand
- chupa/__main__.py
- dev.py
- docs/how-chupa-works.md
- docs/host-authoring.md
- README.md

## Goal / Why
`requisition_review` checks that a ticket is buildable against merged code: every file the change forces (callers, importers, aliases, tests pinning a changed name, value, or version) is inside the fence. Today it runs only inside the Author stage, so a ticket an AI writes in a chat session reaches Implement unreviewed. On 2026-11-05 four such tickets failed `premise_failed` on fence gaps the review would have caught, and five more queued tickets carried the same defect. After this change `chupa review <stem>` runs that review on demand: the author runs it, fixes every finding, and hands the ticket over only on `approve`. The approve is journaled against the exact committed ticket content, in the same `requisition_verdict` record the Author stage writes, so a later gate can tell reviewed content from unreviewed content.

## Scope in / Scope out
- In: `chupa/__main__.py`: a new verb `review <stem>` that takes the writer lock. Under the lock it runs intake (as `confirm` does, so a working-tree edit is committed first), then refuses with exit 2 a stem with no `tickets/<stem>/ticket.md`, a ticket that failed intake, a stem settled or rejected in the journal, or a ticket with an unmerged `## Depends on` stem (the review judges against merged code, so it would report changes the dependency makes; road: `review <stem> after <deps> merge`); a refusal spends no model call. It builds the provider LLM with preflight the way the `triage` verb does (constructed through the module-level `ProviderLLM` name so tests can monkeypatch it), builds a `Driver` the way `runner.bind` does, and calls `requisition.review_ticket` on the COMMITTED `tickets/<stem>/ticket.md` text (`main:` blob, after intake stamping), so the journaled `ticket_sha` equals `git rev-parse main:tickets/<stem>/ticket.md`.
- In: the verb journals one SIGNAL `requisition_verdict` per review, for every verdict, with exactly the body keys the Author stage writes in `chupa/author.py` (`verdict`, `ticket_sha`, `provider`, `model`, `spec_version`). It prints `review <stem>: <verdict> -- <summary>`, then one line per finding: `- [<code>] <path>:<line> <message> (<paved_road>)`, omitting `<path>:<line>` when the finding has no path. It exits 0 on `approve` and 1 on `snag` or `rma`.
- In: `dev.py`: subcommand `review STEM...` runs `chupa review` once per stem, stopping at the first non-zero exit like `confirm`; add its line to the module docstring.
- In: create `tests/test_review_command.py` (monkeypatching `chupa.__main__.ProviderLLM` with a `FakeLLM`, as `tests/test_triage.py` does) with:
  - `test_review_approve_journals_verdict_for_committed_blob`: a working-tree ticket and an approve reply; exit 0, the ticket is committed, and the journal holds `requisition_verdict` `approve` whose `ticket_sha` equals `git rev-parse main:tickets/<stem>/ticket.md` (fails if the sha is taken from the unstamped working-tree text).
  - `test_review_snag_prints_findings_and_exits_1`: a snag reply with one finding; exit 1, stdout contains the finding's code, message and paved road, and the journal holds `requisition_verdict` `snag` (fails if a snag exits 0 or is not journaled).
  - `test_review_refuses_without_a_model_call`: a missing stem, a merged stem, and a ticket depending on an unmerged stem each exit 2 with an empty `FakeLLM` script (fails if any spends a call).
- In: `docs/how-chupa-works.md` section 2.1 verb table gains a `review <stem>` row (lock: yes) describing the above; section 2.2 `./dev.py` table gains `review STEM...`. `docs/host-authoring.md` Workflow gains a step between lint and drain: run `chupa review <stem>` (in this repo `./dev.py review STEM`), repair every finding, and repeat until it prints `approve`; a ticket with unmerged dependencies is reviewed after they merge. `README.md` Commands gains `./dev.py review STEM...`.
- Out: `chupa/requisition.py` and `specs/requisition_review.md` (the review itself is unchanged), the Author and Rework stages, `drive` and every dispatch path (no gate here), intake grammar, `CORE_TEMPLATE`.

## Scope fence
- chupa/__main__.py
- dev.py
- docs/how-chupa-works.md
- docs/host-authoring.md
- README.md
- tests/test_review_command.py

## Acceptance criteria
1. An approve journals `requisition_verdict` against the committed blob, not the unstamped text, checked by `uv run pytest tests/test_review_command.py -k approve_journals_verdict_for_committed_blob`.
2. A snag prints every finding with its paved road, exits 1, and is journaled, checked by `uv run pytest tests/test_review_command.py -k snag_prints_findings_and_exits_1`.
3. A missing stem, a merged stem, and a ticket with an unmerged dependency each exit 2 without a model call, checked by `uv run pytest tests/test_review_command.py -k refuses_without_a_model_call`.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_review_command.py -k approve_journals_verdict_for_committed_blob
uv run pytest tests/test_review_command.py -k snag_prints_findings_and_exits_1
uv run pytest tests/test_review_command.py -k refuses_without_a_model_call
uv run pytest -q
```

## Definition of rejected
The review prompt or `review_ticket` changes; the verb writes a journal signal other than `requisition_verdict`; an approve is journaled against any sha other than the committed blob; any dispatch path starts requiring a review.

## Time budget
- expected: 45m
- stuck: 90m
