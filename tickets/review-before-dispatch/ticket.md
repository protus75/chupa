---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- review-approval-records

## Context
- chupa/requisition.py
- chupa/author.py
- tests/test_triage.py

## On-demand
- chupa/runner.py
- eval/shakeout/bench.py
- eval/reliability_battery.py
- tests/test_terminal.py
- tests/test_stages.py
- tests/test_mergequeue.py
- tests/test_cli.py
- tests/test_drain.py
- docs/how-chupa-works.md

## Goal / Why
A ticket an AI writes in a chat session reaches Implement without the buildability review the Author stage runs, so a fence that misses a forced file is found only when the run fails `premise_failed`: four failed runs on 2026-11-05, five more tickets carried the same defect. `ticket-review-command` lets an author run the review; nothing makes it happen. After this change every dispatch path (`run`, `drain`, `serve`, all through `runner.drive`) reviews a ticket before its first stage unless the journal already holds a `requisition_verdict` `approve` for its exact committed content. A snag stops the ticket before any worktree or Implement call; an author-reviewed, Author-stage, or Rework ticket pays nothing extra.

## Scope in / Scope out
- In: `chupa/runner.py` `drive`: on a fresh run (`ctx.boundary.run is None`, not a continuation), before `run_stages`, read the committed blob of `tickets/<stem>/ticket.md` (`git rev-parse HEAD:<path>` for the sha, `ctx.git._run(ctx.repo, "show", f"HEAD:<path>")` for the text, as `chupa/rework.py` does). If no SIGNAL `requisition_verdict` with `verdict` `approve`, that `ticket_sha`, and `ticket=` this stem exists, call `requisition.review_ticket` on that text and journal its verdict with the Author stage's body keys (`verdict`, `ticket_sha`, `provider`, `model`, `spec_version`).
  - `approve`: continue to `run_stages`.
  - `snag` whose findings all have code `render_feasibility`: continue to `run_stages`, so an oversized ticket still reaches the existing `render_over_bound` -> Rework split path.
  - any other `snag`, or `rma`: end the run with terminal `premise_failed`, `stage` `requisition`, the review's findings in the terminal reason, routed to the Reject queue (`dispatch`/`routed` `reject_queue`, as `failure_terminal` routes `ticket_changed`). Consume no cap (`premise_bounce`, `retry`, `diagnosis`), make no Diagnose call, create no worktree. The release is the existing Reject-queue road: edit `ticket.md`, then `confirm`; the next dispatch reviews the new content.
  - `ProviderCallError` / `ProviderDrought` from the review: handle exactly as the same errors from the Implement stage are handled.
- In: create `tests/approval.py` with `approve(repo, stem, clock)`: journal a real `requisition_verdict` approve for the blob intake will commit for `tickets/<stem>/ticket.md` (stamp with production `_intake_claims`), into `load_config(None, cwd=repo).state_dir`, with a timestamp no earlier than the journal's last event. No production code path may skip the review for tests.
- In: call `approve` from the helpers that commit a ticket and then dispatch it: `tests/test_terminal.py` `author`, `tests/test_stages.py` `author`, `tests/test_mergequeue.py` `ready`, the `tests/test_cli.py` helpers that dispatch (not its plain `write`, which tests asserting an empty journal also use), `eval/shakeout/bench.py` `Bench.add_ticket`, and `eval/reliability_battery.py` after it writes and intakes its ticket.
- In: every remaining test the gate breaks gets one of: an `approve` call where it commits and dispatches a ticket; a re-`approve` (or a scripted review reply) after it edits a ticket mid-test; a leading `requisition_review` entry where it asserts the exact request surfaces; updated journal indexes where it asserts exact event positions. A prototype of this gate broke tests in the files listed in `## Scope fence`.
- In: create `tests/test_requisition_gate.py` with:
  - `test_unreviewed_ticket_is_reviewed_once_then_runs`: one `requisition_review` call, then Implement (fails on zero or two review calls).
  - `test_approved_content_runs_without_review`: an approve at the committed sha means no review call.
  - `test_snag_routes_to_reject_queue_before_implement`: no Implement call, no worktree, terminal `premise_failed` at stage `requisition` in the Reject queue, cap draws unchanged.
  - `test_render_feasibility_snag_proceeds_to_implement`: a snag with only `render_feasibility` findings still reaches Implement.
  - `test_edit_and_confirm_reviews_the_new_content`: after a snag, editing the ticket and confirming reviews the new sha once.
- In: `docs/how-chupa-works.md`: the stage order and the drain/serve dispatch description say a ticket without an approve for its committed content is reviewed before Implement; the Reject queue section names the `requisition` stage terminal and its release (edit, then confirm).
- Out: `chupa/requisition.py` and the review prompt, the Author and Rework stages, intake, `CORE_TEMPLATE`, `hosts/fixture/bin/claude` (it already answers the review role).

## Scope fence
- chupa/runner.py
- tests/approval.py
- tests/test_requisition_gate.py
- eval/shakeout/bench.py
- eval/reliability_battery.py
- tests/test_terminal.py
- tests/test_stages.py
- tests/test_mergequeue.py
- tests/test_cli.py
- tests/test_serve.py
- tests/test_kill_cli_activation.py
- tests/test_shakeout.py
- tests/test_drain.py
- tests/test_ladder.py
- tests/test_diagnose.py
- tests/test_provider_cooldown_failover.py
- tests/test_caps.py
- tests/test_reliability_battery.py
- tests/test_merge.py
- tests/test_harvest.py
- tests/test_drain_reentry.py
- tests/test_second_problems.py
- tests/test_storm_producer.py
- tests/test_reject_queue.py
- tests/test_hostfiles.py
- tests/test_daemon_composition.py
- tests/test_watchdog_activation.py
- tests/test_supervised_merge_hold.py
- tests/test_retro_box.py
- tests/test_kill_signal_journal.py
- tests/test_kill_executor_abort.py
- tests/test_harvest_orphans.py
- tests/test_daemon_soak.py
- tests/test_audit.py
- docs/how-chupa-works.md

## Acceptance criteria
1. An unreviewed ticket gets exactly one review call before Implement, and approved content gets none, checked by `uv run pytest tests/test_requisition_gate.py -k "reviewed_once_then_runs or approved_content_runs_without_review"`.
2. A snag ends at stage `requisition` in the Reject queue with no Implement call, no worktree, and no cap draw, while a `render_feasibility`-only snag still reaches Implement, checked by `uv run pytest tests/test_requisition_gate.py -k "snag_routes_to_reject_queue or render_feasibility_snag_proceeds"`.
3. Editing and confirming after a snag reviews the new content once, checked by `uv run pytest tests/test_requisition_gate.py -k edit_and_confirm_reviews_the_new_content`.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_requisition_gate.py
uv run pytest -q
```

## Definition of rejected
Any production path skips the review based on the LLM type or a test flag; a snag consumes a cap or calls Diagnose; a `render_feasibility`-only snag blocks Implement; the review prompt or `review_ticket` changes.

## Time budget
- expected: 75m
- stuck: 90m
