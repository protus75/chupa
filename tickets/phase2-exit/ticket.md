---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: high
agent_effort: high
---

## Depends on
- shakeout-providers
- diagnosis-eval-run

## Context
- chupa/artifacts.py
- tests/test_seeded_phase2.py

## Plan contract
- 19.L
- 19.P2
- 19.P3
- section 13

## Goal / Why
The Phase 2 exit is READ, never claimed (19.L): a merged test proves each `19.P2` exit read from committed artifacts, and this ticket's Implement authors Phase 3's `core` admission plus one `phase3-continue` seeding ticket as `confirmed` `ticket.md` files, directly on the ticket plane. Its own Check stage lint-validates and feasibility-reviews each seed (`requisition-seed-path`) before lifting it. The drain's after-every-merge re-scan (section 18) then makes them eligible in the SAME running drain.

Why: one continuous `chupa drain` carries Phases 2-6 only if each phase's final ticket seeds the next (19.L bootstrap contract). Seeds are NEVER filed to the Suggestion Box, which carries filed problems, never a known build-plan ticket (section 12).

Known-hard: 19.L names the phase-exit seed plan-named KNOWN-HARD, starting `high`/`high`; that `19.L` sentence, cited under `## Plan contract`, is this ticket's citing evidence.

Owners: `tests/test_phase2_exit.py` owns the exit reads. `tests/test_seeded_phase3_core.py` owns this batch's seeding pins. The registry block `BEGIN_REGISTRY_P3` in the `19.P3` unit is the ONE source the seeding reads, parsed straight from CHUPA_PLAN.md, never copied into a repo file and never edited. `chupa/artifacts.py` (`ShakeoutReport`) and `chupa/stages.py` (`Invoice`) are read, never changed.

## Scope in / Scope out
- In: the exit reads, each from its emitter's committed artifact, never the live journal (the exit runs on a clean checkout without the state dir):
  - Every Phase 2 stem merged. Emitter: the merge lane, through this ticket's transitive `## Depends on`, which covers every Phase 2 seed. Its dispatch IS the merged-presence proof (squash trailers, section 10), so no further entry-read is authored.
  - Battery green, every named member. Emitter: the committed cumulative `tickets/shakeout-providers/shakeout-report.json` (machinery `shakeout-report-lane`, producers the seven battery groups). `tests/test_phase2_exit.py` loads it through `ShakeoutReport` and asserts its member ids are exactly `scope_escape`, `unfixable_lint_branch_only`, `review_reject`, `review_reject_reentry`, `empty_committed_diff`, `base_diff_attribution`, `invalid_output_exhausted`, `stuck_budget_kill`, `premise_false`, `timeout_dead_ends`, `identical_terminals`, `bad_schema`, `premise_park_release`, `red_then_green`, `engine_death_mid_call`, `conflicted_rebase`, `auth_expiry`, `planted_secret`, each `green` with an empty `auditor`.
  - Auditor green across the battery. Emitter: the Check-lane `tickets/shakeout-providers/checks.json`, written by the engine's Check, never by any ticket's fence. The test loads it through `Invoice` and asserts `passed` and a `pass` `verification` report: that Check ran the cumulative runner, which re-ran every member under `invariant-auditor`'s `audit`, and 19.P2 REPORT REQUIRED means it passes only when that runner wrote the report, so no excused runner command reads green.
  - An unmet read means Implement replies `premise_failed` naming it.
- In: Phase 3 seeding, core-first (19.L seeding chain), written into the worktree and left UNCOMMITTED for the seed-path lift:
  - `tickets/daemon-scheduler/ticket.md` and `tickets/seed-successor-proof/ticket.md`: the registry's first admission. Each realizes exactly its row: its `does`, `## Plan contract` `19.L`, `19.P3`, and the row's `cite` sections, its `fence` as the `## Scope fence` floor, `## Depends on` `phase2-exit`, `state: confirmed`, `source: seed`, `medium`/`medium` (neither row is `deep`), and a stuck budget at or under `drain.max_ticket_minutes`. The fence widens only by paths 19.L mechanical rules 2-5 find, each recorded in the batch test.
  - `tickets/phase3-continue/ticket.md`: the first continuation. It depends on both payloads, fences `tickets` plus its own new `tests/test_seeded_phase3_01.py`, embeds `tests/test_seeded_phase3_core.py` as its idiom, and authors the registry's next admission (`merge-queue`, `deep`, riding alone at `high`/`high`) plus `phase3-continue-02` carrying the shrinking unseeded suffix. It never authors past that admission.
  - Each seed's `## Context` holds only EXISTING paths and never a path a sibling seed creates; a fenced existing path whose embedding breaches the section 8 authoring headroom goes under `## On-demand`.
- In: `tests/test_seeded_phase3_core.py` NAMES the three stems and asserts only over them (pin grain, 19.L SEEDING TESTS): intake lint passes, `source: seed` and `state: confirmed` as authored (a later `rejected` stamp is accepted as history), stuck at or under the configured `drain.max_ticket_minutes`, the `depends` edges above, each fence a superset of its registry row's floor, and Context closure plus render feasibility computed from sizes and plan-unit lengths RECORDED IN THE TEST, never re-read live.
- Out: any Phase 3 machinery, any seed beyond the first admission and `phase3-continue`, any Suggestion Box message, any edit to an existing ticket, and any edit to the plan or its registry.

## Scope fence
- tickets
- tests/test_phase2_exit.py
- tests/test_seeded_phase3_core.py

## Acceptance criteria
1. `uv run pytest -q tests/test_phase2_exit.py` passes, reading the battery report and the `checks.json` exactly as stated, and this ticket's transitive `## Depends on` covers every Phase 2 seed (pinned by `tests/test_seeded_phase2.py`).
2. `uv run pytest -q tests/test_seeded_phase3_core.py` passes over exactly `daemon-scheduler`, `seed-successor-proof`, and `phase3-continue`.
3. At this ticket's Check, all three seeds receive a `requisition_review` `approve` and lift in one `chupa(phase2-exit): seeds` commit, recorded in `tickets/phase2-exit/checks.json`.
4. The branch's committed diff carries no `tickets/` path, so the `post_rebase_regate` MERGE-SAFETY check passes and every seed reaches main only through the ticket-plane lift.
5. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_phase2_exit.py
uv run pytest -q tests/test_seeded_phase3_core.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- An exit read is satisfied by a report or journal this ticket writes, or by a symbol-presence grep.
- A seed is filed through the Suggestion Box, committed on the branch, or authored past the first admission and `phase3-continue`.
- The registry is copied into a repo file, or a row is renamed, reordered, split, or widened beyond 19.L rules 2-5.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
