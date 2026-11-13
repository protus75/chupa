# Review: snag

The diff routes every menu key through one closed table and shared admission functions as the ticket asks, but the snapshot's input builder now does per-stem git subprocesses and full-repo validation for all ~527 tickets on every snapshot.

## Findings

- [logic] chupa/observe.py:538 `ticket_menu_inputs` runs `await ticket_pending(ctx.git, ctx.root, stem)` once for every stem in `set(tickets) | set(invalid) | set(last)`. That set includes every merged or settled stem in the journal, and `ticket_pending` (chupa/runner.py:544) starts a separate `git status --untracked-files=all -- tickets/<stem>/` subprocess. Before this diff, `snapshot` made one porcelain call through `uncommitted_tickets`. This repo has 527 ticket files, so each extension refresh now starts hundreds of git processes, and for unsettled admitted stems it also runs a `git show main:` per stem. (do instead: Read porcelain once with `--untracked-files=all` (or reuse the entries `plan_intake` already reads), then derive each stem's `pending` flag from that single listing using the same `tickets/<stem>/` prefix test. Keep the flag's meaning the same as `runner.ticket_pending`.)
- [logic] chupa/observe.py:537 `run_ticket = validated(...)` runs `validate_ticket` on the disk text of every stem with a file, including every merged or settled ticket that `load_tickets` deliberately skipped ('Full engine parse of unsettled tickets only'). `order_ticket` and `review_ticket` can add up to two more calls per stem. `validate_ticket` calls `_graph(repo)` (chupa/tickets.py:544), which reads every `tickets/*/ticket.md`. Each snapshot therefore does O(N²) ticket file reads, about 280k or more for this repo's 527 tickets, where it used to do O(N). (do instead: Build the ticket graph once per snapshot and pass it into validation, for example with an edges parameter on `validate_ticket` that the verbs also use, or a per-call cache inside `tickets.py`. Either way the admission inputs stay the same values the verbs compute, without rescanning the whole tickets tree for every stem.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "17621bdd7b1f3ac31a8484a588ecd0106fdaa26b",
  "stem": "menu-table-run-review-admission",
  "reviewed_sha": "17621bdd7b1f3ac31a8484a588ecd0106fdaa26b",
  "summary": "The diff routes every menu key through one closed table and shared admission functions as the ticket asks, but the snapshot's input builder now does per-stem git subprocesses and full-repo validation for all ~527 tickets on every snapshot.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/observe.py",
      "line": 538,
      "message": "`ticket_menu_inputs` runs `await ticket_pending(ctx.git, ctx.root, stem)` once for every stem in `set(tickets) | set(invalid) | set(last)`. That set includes every merged or settled stem in the journal, and `ticket_pending` (chupa/runner.py:544) starts a separate `git status --untracked-files=all -- tickets/<stem>/` subprocess. Before this diff, `snapshot` made one porcelain call through `uncommitted_tickets`. This repo has 527 ticket files, so each extension refresh now starts hundreds of git processes, and for unsettled admitted stems it also runs a `git show main:` per stem.",
      "paved_road": "Read porcelain once with `--untracked-files=all` (or reuse the entries `plan_intake` already reads), then derive each stem's `pending` flag from that single listing using the same `tickets/<stem>/` prefix test. Keep the flag's meaning the same as `runner.ticket_pending`.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/observe.py",
      "line": 537,
      "message": "`run_ticket = validated(...)` runs `validate_ticket` on the disk text of every stem with a file, including every merged or settled ticket that `load_tickets` deliberately skipped ('Full engine parse of unsettled tickets only'). `order_ticket` and `review_ticket` can add up to two more calls per stem. `validate_ticket` calls `_graph(repo)` (chupa/tickets.py:544), which reads every `tickets/*/ticket.md`. Each snapshot therefore does O(N²) ticket file reads, about 280k or more for this repo's 527 tickets, where it used to do O(N).",
      "paved_road": "Build the ticket graph once per snapshot and pass it into validation, for example with an edges parameter on `validate_ticket` that the verbs also use, or a per-call cache inside `tickets.py`. Either way the admission inputs stay the same values the verbs compute, without rescanning the whole tickets tree for every stem.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
