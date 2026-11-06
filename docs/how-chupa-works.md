# How chupa works

This document describes chupa as the code behaves today. It is maintained: a ticket that changes
behavior described here updates the matching section in the same change, and tickets cite its
section headings. `CHUPA_PLAN.md` is the frozen bootstrap design record; it is history, never a
reference for current behavior. Where this document and the code disagree, the code wins and
this document is fixed.

Related documents: `docs/host-contract.md` (full config schema and host-facing contract) and
`docs/host-authoring.md` (what to write in a ticket).

## 1. What chupa is

chupa runs tickets against a git repository (the host): Implement writes the change on a branch,
Check runs mechanical gates, Review has a model judge the diff, and Merge squashes the branch onto
`main`. Failures are harvested, diagnosed, retried within caps, or held for a human.

Two planes meet in chupa:

- **Engine plane** (chupa-owned): how work runs. Ticket grammar, prompt specs (`specs/`), gates,
  caps, git rules, the journal.
- **Host plane** (repo-owned): what to build. The host's code, docs, config, and the ticket
  content. Host material enters prompts as data, never as instructions.

chupa develops itself: this repo is both the engine and its own first host.

## 2. Commands

Run chupa as `uv run python -m chupa <verb>` (global flag `--config PATH`, default `config.yaml`
at the checkout root). In this repo, use `./dev.py` (section 2.2).

### 2.1 Verbs

Exit codes are one contract for every verb: **0** success or quiescence, **1** a non-ok ticket
outcome or a halted/killed run, **2** an engine refusal (bad config, lock held, invalid intake,
journal corruption, provider setup, missing executable, corrupt conduct markers). A refusal
prints `chupa <verb>: <message> -- <what to do instead>`.

| Verb | Lock | What it does |
|---|---|---|
| `status` | no | Prints the journal projection (section 10.3). Read-only. |
| `lint [stem ...]` | no | Validates ticket grammar, intake claims, and committable bug evidence without running tickets or writing files, journal events, or git state. With no stems, checks every ticket except those settled or rejected in the journal; with no journal, checks all tickets. Prints each finding and its fix, then `lint: <valid>/<total> tickets valid`. Exits 0 when valid, 1 for findings, or 2 for a missing named ticket or unreadable tickets directory. |
| `doctor` | no | Checks venv, git, config load, lock probe, journal readability. Exit 2 on any failure. |
| `core` | no | Rewrites the managed `chupa:core` block in each routed agent's conduct file (section 12). |
| `migrate-config` | no | Migrates a `schema_version: 0` config to the current schema. |
| `new <stem> --kind feature\|bug\|chore` | no | Writes `tickets/<stem>/ticket.md` with section placeholders for the selected kind (default `feature`) and lints it. Bugs include `## Regression` and a missing-evidence finding; no evidence files are created. Refuses a bad, reserved, or existing stem, or unknown kind (exit 2); successful authorship exits 0. |
| `review <stem>` | yes | Runs intake, then reviews the committed ticket against merged code and journals its verdict and ticket blob SHA. Refuses missing, intake-failed, settled, rejected, or dependency-blocked tickets without a model call. Prints findings and exits 0 on approve, 1 on snag or rma. |
| `run <stem>` | yes | Reconciles orphans, runs intake, then drives the one named ticket through every stage. Refuses a stem that failed intake, is missing, invalid, merged, not `confirmed`, or has unmerged dependencies. |
| `drain` | yes | Runs every eligible ticket to quiescence (section 7.1). |
| `serve` | yes | Runs the continuous daemon until `kill` or a signal (section 7.2). |
| `retro` | yes | Forces a retro report (section 9.5). |
| `triage` | yes | One sequential pass over pending Suggestion Box messages (section 9.2). |
| `pause` / `resume` / `kill` | try | With a running engine, publish a control request to it (section 7.3). With none: `kill` refuses (exit 2); `pause`/`resume` print "nothing running". |
| `confirm <stem>` | yes | A person at a terminal answers `y` to keep: promotes a draft to confirmed, keeps a Reject-queue item, or releases a held merge (section 6.6). |
| `reject <stem>` | yes | A person at a terminal answers `y` to kill: stamps the ticket `rejected` (section 6.6). Refuses settled stems. |

### 2.2 `./dev.py`

The repo's one dev command; standard library only, every task through `uv`.
`./dev.py test` runs the suite in parallel on the available cores by default.
Each test has a 120-second hard limit.

| Subcommand | Runs |
|---|---|
| (none) | `uv run pytest -q` |
| `test [args]` | pytest with those args |
| `new STEM [--kind K]` | `chupa new <stem> --kind feature\|bug\|chore` (default `feature`) |
| `lint [STEM...]` | `chupa lint [stem ...]` (read-only; no writer lock) |
| `review STEM...` | `chupa review` once per stem, stopping on the first non-zero exit |
| `run STEM` | `chupa run <stem>`: one ticket through every stage, under the lock |
| `status`, `drain`, `kill` | the matching chupa verb |
| `confirm STEM...`, `reject STEM...` | `chupa confirm` or `chupa reject` once per stem; a person at a terminal answers `y` for each stem |

## 3. Tickets

### 3.1 Files and fields

A ticket is `tickets/<stem>/ticket.md`. The stem matches `^[a-z0-9][a-z0-9-]{1,63}$`;
`decisions` and `retro` are reserved. `chupa/tickets.py` owns the format; `docs/host-authoring.md`
says what goes in each section.

Frontmatter fields that drive behavior:

- `state`: `draft` (awaits `confirm`), `confirmed` (dispatchable), `rejected`, `merged`.
- `source`: `human` (hand-written), `box:<class>` (written by the Author stage), `seed`
  (bootstrap-era, section 13).
- `kind`: `feature`, `chore`, or `bug` (a bug must carry `## Regression` and evidence,
  section 5.2).
- `priority` (P0-P3), `## Depends on`, and the optional `## Runs before` section order the queue. `agent_tier` / `agent_effort` pick the
  starting model capability (section 6.4). `gate_bypass` softens named engine gates for this
  ticket (section 5.3).

### 3.2 Intake

`run`, `drain`, `serve`, `confirm`, and `reject` start with intake, under the writer lock:

- It finds new or modified `tickets/<stem>/ticket.md` files in the working tree (`git status`).
- A new hand-written stem must be `draft` or `confirmed` and must not claim a machine `source`;
  intake stamps it `source: human`, `state: confirmed`.
- Intake refuses a bug ticket without a regular, non-symlink evidence file that is not gitignored
  under `tickets/<stem>/evidence/`. Settled and rejected tickets are exempt from this check.
- Each ticket that lints clean is committed with its new or changed regular, non-symlink evidence
  files as `chupa(<stem>): ticket` and journaled as
  `ticket_intake`. A ticket that fails lint stays on disk uncommitted, and the refusal names the
  fix.
- If anything other than pending ticket files and their committable evidence files is staged,
  intake refuses entirely; staged evidence deletions and symlinks must be unstaged first.
- An existing stem is never restamped.

So writing a ticket file is enough: the next `drain` commits it. After intake,
dispatch pins the committed `ticket.md` blob on `main`. Before each stage and
merge admission, both main's committed blob and its checkout bytes must still match. A committed
or uncommitted edit during the run stops it with `ticket_changed` and holds it for an operator.
Engine artifacts such as `run.md` and `checks.json` do not affect this identity.

### 3.3 What the engine writes back

Stages write into an outbox in the ticket's worktree (`tickets/<stem>/` inside it). The lift
copies each new or changed file to the main checkout's `tickets/<stem>/` and commits it on `main`
as `chupa(<stem>): <kind>`, once per attempt (an Effect, section 10.2). `ticket.md` is never
lifted from a worktree: the agent cannot edit its own ticket.

| Lift kind | File |
|---|---|
| `run-record` | `run.md` (the Implement run record) |
| `checks` | `checks.json` (Check's report), plus registered report artifacts |
| `review` | `review.md` |
| `harvest` | `attempts/<n>/harvest.json` |
| `diagnosis` | `diagnosis.json` |

Other engine commits on `main`: `ticket` (intake), `confirmed`, `rejected`, `rework`, and the
squash merge itself.

## 4. A ticket's run

`runner.drive` takes one ticket through Implement, Check, Review, then Merge.

### 4.1 Worktree

Each attempt gets a fresh worktree at `<worktree_root>/<stem>` (default
`<state_dir>/worktrees/<stem>`) on branch `<stem>`, cut from `main`. Any old worktree and branch
of that stem are removed first. Scratch worktrees under `.base/` and `.regression-base/` are
created at the merge base for base-red reruns and the bug gate, and removed after.

### 4.2 Implement

The `implement` prompt (`specs/implement.md`) gets the ticket text, its `## Context` files plus
`config.context_files`, and a "Prior attempts" block (last terminal, findings, diagnosis lessons,
log tails) when this is a retry. The model works in the worktree with write access and replies:

- `ok`: it committed the change.
- `already_satisfied`: every acceptance criterion already holds on `main`; Check must prove it
  with green Verification on an empty diff.
- `premise_failed`: the ticket cannot be done as written; findings say why.

The Implement prompt asks for each assertion to name the likely wrong implementation it rules out
and use a fixture that gives a different value under that version. It forbids asserting values a
default, zero, or shared fixture would produce anyway, and asks retries to check every assertion
this way, not only the one named by a finding.

The engine writes `run.md` from the reply and lifts it. Each `second_problems` entry is filed to
the Suggestion Box as a `suggestion`.

### 4.3 Check

1. Runs configured autofix commands on existing changed files outside `tickets/` matching each entry's `files` patterns and commits changes.
2. Runs each `## Verification` command in the worktree (provider keys removed from the
   environment, timeout = the ticket's stuck budget, output spooled to `check/verify-NN.txt`).
3. A failing command is rerun at the merge base. If it also fails there it is **base-red**: a
   pre-existing failure, excluded from the verdict and filed once to the Suggestion Box.
4. Runs the engine Check gates (section 5.1).
5. Runs triggered host checks in config order, attributing failures also red at base to main.
6. Writes and lifts `checks.json`.

A hard gate failure ends the attempt `gate_failed`. Soft failures are recorded and the run
continues. `already_satisfied` stops here: there is no diff to review.

### 4.4 Review

The `review` prompt (`specs/review.md`) gets the ticket and the branch diff, in a read-only
session. Verdicts: `approve`, `snag` (findings: `logic`, `acceptance`, `scope`, `leak`), or `rma`
(the ticket itself is wrong). `review.md` records the verdict and the reviewed branch head
(`reviewed_sha`). Review also snags a stale or missing doc update. Only `approve` continues;
`snag` and `rma` end the attempt `gate_failed`.

### 4.5 Merge

`run` and `drain` merge inline (`merge.merge`); `serve` uses the merge queue (section 7.2).
For a nonempty branch, if main changed only paths under `tickets/` since the reviewed
merge base, the Check reruns and host checks are skipped; Merge gates still run.
Inline merge:

1. Rebases the branch onto current `main`. A refused rebase is `gate_failed`.
2. Re-runs Verification (and the bug regression) on the rebased candidate.
3. Runs the Check gates, Merge gates and triggered hard host checks (section 5.1). Any hard failure refuses the merge;
   `main` is untouched and the branch is kept.
4. Squash-commits onto `main`: subject `chupa(<stem>): <first Goal line>`, trailers
   `chupa-ticket: <stem>` and `chupa-reviewed-sha: <sha>`. Journals `to: merged`.
5. Removes the worktree and deletes the branch.

Inline merge does not run merge strategies or the conflict ladder; a rebase
conflict is simply refused.

## 5. Checks

### 5.1 Engine gates

Every engine gate is hard by default.

**Check gates** (on the branch head):

| Code | Fails when |
|---|---|
| `scope_fence` | A changed file is outside `## Scope fence` (the stem's own outbox is exempt, except `ticket.md`). |
| `verification` | A Verification command fails and was green at the base; or `already_satisfied` came with a diff; or a required report is missing or invalid. |
| `run_record` | `run.md` is missing, or lacks its six fixed sections in order, or has an unknown outcome. |
| `diff_budget` | More than 30 changed files, or more than 1,500 inserted lines: split the ticket. |
| `core_drift` | A routed conduct file's managed `chupa:core` block does not match the current template (section 12). |
| `bug_evidence` | For `kind: bug` only: see section 5.2. |

**Merge gates** (on the rebased candidate, at admission):

| Code | Fails when |
|---|---|
| `ticket_schema` | The ticket on `main` no longer lints. |
| `post_rebase_regate` | The branch commits anything under `tickets/`, or the rebase was refused. |
| `correctness_review` | `review.md` on `main` is not an `approve` of the branch head that was reviewed. |
| `requisition_review` | A seeded ticket lacks its approval (bootstrap-era, section 13). |

### 5.2 Bug tickets

A `kind: bug` ticket must prove the defect: at least one file under `tickets/<stem>/evidence/`;
a `## Regression` command that prints `{"regression_result": "pass"}` with exit 0 on the branch
head, and `{"regression_result": "defect"}` with a non-zero exit on the merge base with the
carried test or fixture files copied over it. Only files under `tests/`, `test/`, `fixtures/`, or
`fixture/` can be carried. `docs/host-authoring.md` explains the protocol for authors. Intake
refuses a bug ticket without a regular, non-symlink evidence file that is not gitignored and
commits its evidence in the same commit as the ticket. Settled and rejected tickets are exempt
from the intake evidence check. The Check gate still verifies the regression proof.

### 5.3 Severity and bypass

- `review.gate_severity` in config can make an engine gate soft for every ticket.
- A ticket's `gate_bypass: [{code, reason}]` makes the named engine gates soft for that ticket
  only; bypassed codes are recorded in `checks.json`.
- A soft failure is recorded with its findings and does not stop the run.

### 5.4 Host checks

A host declares its own checks in `review.mechanical` (`code`, `argv`, `trigger: always` or a
list of path prefixes, `severity: hard | soft`). Check runs every triggered entry in order;
prefixes match an equal path or a descendant. A base-red failure is filed and excluded from
Check and retry findings. Soft failures are recorded without blocking. When main changed a path
outside `tickets/` since the reviewed merge base, or the branch diff is empty, inline merge reruns
triggered hard entries on the rebased candidate. The `serve` merge queue runs the hard entries
named in `merge.safety_checks` at safety and every always/hard entry at integration under the
same conditions. Otherwise only the Merge gates run, alongside the queue safety gates; see
sections 4.5 and 7.2.1. All use one shared command runner.

An entry may declare a worktree-relative `results` file written by `chupa.testreport`. Check
clears it before each run and reruns a failing command with failed tests once. Edited flakes
block; unedited flakes are quarantined unless the cap is full. Quarantined unedited failures
do not block, and a passing quarantined test is released when its resolved fix has merged.
Missing or invalid results after a successful run or rerun fail the entry. With a declared coverage.py JSON report, a flake also counts as edited when its test context covers a changed line or a line adjacent to a pure deletion. The host must run with `--cov-context=test`, `[tool.coverage.json] show_contexts = true` and `[tool.coverage.run] core = "ctrace"`; missing or invalid contexts fail classification.

Config load refuses a declared `review.surfaces` entry (host review prompts); remove
the entries because host review surfaces are not supported yet.
`review.trigger_map` is accepted by config and read by nothing.

## 6. When a run fails

### 6.1 Order of handling

`already_satisfied` is settled after Check proves it: `runner.drive` journals its stage and
`already_satisfied` reason, then removes the worktree. It makes no diagnosis call, draws no cap,
and records no dispatch or Reject routing marker.

After any other non-ok terminal, `runner.drive` does, in order:

1. **Harvest** the attempt (section 6.2).
2. **`ticket_changed`** journals a `gate_failed` terminal routed to the Reject queue, removes
   the worktree, and stops (section 6.7), skipping the cap, Diagnosis, and Rework steps.
3. A provider **drought** or quota result parks the stem with no diagnosis (section 8.3).
4. A failure reaching `caps.attempts` goes straight to the terminal, routed to the Reject queue
   with reason `attempts cap spent`, skipping the cap draw, spec-gap hold, Diagnosis, and Rework.
5. `infra_error` / `timeout` draw the `infra` cap; `premise_failed` draws `premise_bounce`.
6. **Diagnosis** (section 6.3), unless the outcome is `budget_exceeded` or an over-bound render.
7. **Rework** if diagnosis said `split`, or the render was over bound (section 6.5).
8. Decide the dispatch (retry, escalate, or the Reject queue) and journal the terminal.
9. Remove the worktree.

### 6.2 Harvest

`attempts/<n>/harvest.json` records the stage, terminal, findings, diff stat, the last 4,000
characters of the stage logs and of the provider event stream, time, and cost. It is lifted as
`chupa(<stem>): harvest` and feeds the next attempt's "Prior attempts" block. A harvest failure is
journaled and never blocks the terminal.

### 6.3 Diagnosis

The `diagnose` prompt (`specs/diagnose.md`) reads the ticket, terminal, harvest, and run record
and replies with a verdict and 1-5 lessons:

- `retry`: run again with these lessons.
- `escalate`: run again with more capability (section 6.4).
- `split`: Rework the ticket into smaller ones.
- `reject`, `abandon-human`: send it to the Reject queue.

If a cap is already spent or the worktree is gone, the verdict is a mechanical `abandon-human`
with no model call. `diagnosis.json` is lifted and a `diagnosis` signal is journaled.

### 6.4 Caps and escalation

Caps bound how much one ticket can fail over the stem's **lineage**: every event since the
last operator keep. Editing `ticket.md` never resets a cap; only an operator `confirm` does.
Machine keeps never reset counts. Draws are journaled `cap_consumed` events, except `attempts`,
which counts failed terminal `state_transition` events directly and journals no cap draw.

| Cap | Default | Drawn by |
|---|---|---|
| `attempts` | 5 | total failed attempts per lineage |
| `diagnosis` | 3 | each diagnosis call |
| `retry` | 3 (never above `diagnosis`) | each drain re-offer |
| `infra` | 3 | each `infra_error` or `timeout` (not droughts) |
| `premise_bounce` | 1 | each `premise_failed` (not over-bound renders) |
| `hardening` | 1 | each spec-gap hold (bootstrap-era, section 13) |
| `quarantine` | 5 | flake quarantine size |
| `poison` | 2 | read by nothing |

Failed attempts are `gate_failed`, `premise_failed`, `infra_error`, and `timeout` terminals.
An `infra_error` with reason `provider_drought`, `budget_exceeded`, an `abandoned` reap,
settled terminals, and `rejected` do not count. The failure reaching `caps.attempts` is itself
routed with reason `attempts cap spent`, without another diagnosis or rework call, including
merge-conflict handoffs. Terminal routing also counts a pending failure after a published Rework
update or escalation and leaves the published ticket text intact. A published split still retires
its parent. The drain report shows the failed-attempt total, for example `attempts cap spent (5/5)`.

A spent cap, or a `reject` / `abandon-human` verdict, routes the stem to the Reject queue.
`escalate`, or the same failure reason three times running, moves the stem up one **rung**: the
next higher tier whose Implement model differs, else one effort level higher. At the top rung
the stem goes to the Reject queue.

### 6.5 Rework

The `rework` prompt (`specs/rework.md`) proposes `update` (rewrite this ticket), `split` (two or
more new stems), or `escalate`. Each proposal is validated in a scratch worktree and reviewed by
`requisition_review`. Accepted proposals are committed as `chupa(<stem>): rework`. A split
journals `supersedes` and retires the original: its dependents wait on the successors.

### 6.6 The Reject queue, keep and kill

The Reject queue holds stems whose latest terminal was routed there, plus stems the drain finds
with a spent cap at quiescence. `status` lists them.
Settled stems (`merged` and `already_satisfied`) never await a verdict, even when a historical
terminal carries a Reject routing marker. `reject` refuses settled stems.

- **`confirm <stem>` (keep)** journals `reject_verdict keep actor: operator`. That resets the
  lineage, so every cap starts over. A second keep at the same ticket content is refused: edit the
  ticket first.
- **`reject <stem>` (kill)** stamps `state: rejected`, commits it, and files one Suggestion Box
  `failure_report` per confirmed ticket that depended on it ("re-wire, re-scope, or reject it").
  Those dependents stay blocked.
- **Machine keep:** at quiescence the drain re-offers a queued stem whose caps still have budget,
  journaling `keep actor: machine` and drawing `retry`. A machine keep never resets caps.
- `confirm` on a `draft` ticket promotes it to `confirmed` instead.

Keep and kill require a person at an interactive terminal to type the exact stem before the verdict proceeds.

### 6.7 Other holds

- **`ticket_changed`:** a committed or uncommitted change to `ticket.md` during a run ends the
  attempt `gate_failed` and holds it in the Reject queue, with no diagnosis, Rework, or cap draw.
  Review the change to `tickets/<stem>/ticket.md`, then keep (`./dev.py confirm <stem>`) to run
  the changed ticket as a fresh attempt, or kill (`./dev.py reject <stem>`). Machine keeps do
  not release this hold. Stage boundaries, admission, and queued or confirmed merge admissions
  all check the dispatch identity. Rework updates between attempts are fresh ticket inputs.

- **Premise park:** with the default `premise_bounce: 1`, the first `premise_failed` spends
  the cap and routes to the Reject queue via `premise_bounce cap spent`; only an operator
  `confirm` releases it. When a host sets `premise_bounce` above 1 and caps still have budget,
  the stem parks until its committed `ticket.md` changes. That re-offer draws no retry.
- **`budget_exceeded`:** not diagnosed, draws nothing. Ticket stages pass no spend budget, so in
  practice only eval runs reach it.
- **Reconcile:** at the start of `run`, `drain`, and `serve`, any stem still marked `running`
  (or with an unfinished effect) is reaped: harvested, journaled `abandoned`, worktree removed.
  `abandoned` stems stay eligible. A `running` stem cannot be confirmed or rejected until it is
  reaped.
- **Flaky tests:** Check quarantines unedited fail-then-pass tests and releases them after a merged fix and a passing observation. Edited flakes and cap-blocked flakes fail Check.

## 7. Drain and serve

### 7.1 `drain`

1. Takes the lock, reconciles, fires due timers, runs the provider preflight, runs intake once.
2. Loops: reload config, honor pause/kill, maybe run a retro, scan committed tickets, pick the
   next ticket, run it, merge it inline.
3. **Pick order:** confirmed, unsettled, not rejected, every dependency settled (through split
   successors); among eligible fresh tickets and re-offers, `## Runs before` orders named stems
   after the ticket naming them, with priority P0-P3, authored age, then stem breaking ties.
   Edges to ineligible stems never block a pick. Skipped: storm-held, drought-parked, Reject-queue stems without budget, and tickets
   whose `stuck` exceeds `drain.max_ticket_minutes` (default 90).
4. **Quiescence:** when nothing is eligible, it re-offers parked stems with budget (drawing
   `retry`), forces a retro, and stops when nothing changes.
5. **Report:** merged, parked (with reasons and the command to continue), blocked on depends,
   invalid tickets excluding those settled or rejected in the journal, drafts awaiting confirm.

Bounds: `drain.max_runtime_hours` (default 12) halts it (exit 1).

**Self-upgrade:** when a merge changes `chupa/` or `specs/`, the drain journals a handoff,
releases the lock, and re-executes itself so the new engine code runs the rest of the queue.

### 7.2 `serve`

The continuous daemon. On start it takes the lock, reconciles, rebuilds held merges and timers,
publishes `state_dir/control/active.json`, and runs four loops (every 0.1s):

- **Watcher:** runs intake and re-reads tickets, debounced; a ticket that fails to parse keeps
  its last good version.
- **Dispatch:** the scheduler runs one ticket at a time. It waits while
  `scheduler.max_unmerged` (default 2) finished tickets are waiting to merge, while paused, or
  while a stem is held (Reject queue, storm, drought, held merge). Among eligible tickets,
  `## Runs before` orders named stems after the ticket naming them; priority, authored age,
  and stem break ties. Edges to ineligible stems never block dispatch.
- **Merge queue:** serial admission (section 7.2.1).
- **Triage:** works the Suggestion Box.

Maintenance on each loop: control requests, timers, orphan sweeps, heartbeat
(`state_dir/heartbeat` mtime), notification replay, and checkpoint pushes. If any loop dies,
`serve` stops.

#### 7.2.1 Merge queue (serve only)

For a nonempty branch with only `tickets/` changes on main since the reviewed merge
base, the safety host checks and integration tier are skipped; safety and Merge
gates still run. Empty branches take the full path for report custody.

For each candidate, in pick order:

1. Rebase onto `main`. A conflicted path that matches exactly one `merge.strategies` entry is
   resolved mechanically (`union` for append-only files, `regenerate` re-runs a generator).
   Anything else aborts the rebase and hands the ticket to Rework.
2. **Safety tier:** scope fence, run record, Merge gates, and host safety checks.
3. **Integration tier:** all Check and Merge gates, plus host `always` + `hard` checks through the shared runner also used by Check and inline merge.
4. **Red streak:** three different stems failing integration in a row pause the queue; `resume`
   with the advertised hold releases it.
5. **Supervision:** unless the configured review model is covered by a recorded GO baseline
   (section 9.6), a green candidate is HELD for the operator's `confirm <stem>` instead of
   merging.
6. Squash-merge as in section 4.5, and verify `main`'s tree equals the checked tree.

### 7.3 Control

`pause`, `resume`, and `kill` write a request file to `state_dir/control/inbox/`, bound to the
running engine's lifecycle id. The engine journals a `control_decision` (accepted, stale, or
rejected) for each request. Pause stops new dispatch; resume must name the advertised hold;
kill stops the engine at the next safe point. `run` does not read control requests.

### 7.4 Storms, watchdog, notifications, pushes

- **Storm breaker:** every Suggestion Box arrival is counted per signature. More than 5 in an
  hour trips a hold on the emitting ticket's stage. Only `resume` naming that trip releases it.
- **Watchdog:** watches each model call's active time (soft past 1.5x expected, killed at the
  stuck budget) and spending without progress in the scope fence (warned past 3x a call's
  cost). It notifies on both.
- **Notifications:** sent by running `config.notify` (an argv) with the message. `serve` replays
  undelivered escalations (storm trips, red streaks, tree mismatches) from the journal. Unset
  `notify` only logs.
- **Checkpoint push:** in `serve`, idle, after 5 merges or 24 hours: `git push origin main`. A
  failed push is journaled and filed to the Suggestion Box.

## 8. AI providers and prompts

### 8.1 Providers

Two CLI adapters ship: `claude` and `codex`. Only `kind: cli` providers are accepted.

- Implement is the only surface with write access (`claude --permission-mode
  bypassPermissions`, `codex --dangerously-bypass-approvals-and-sandbox`) and runs in the
  ticket's worktree. Every other surface is read-only.
- Each provider maps tiers `low | medium | high | max` to models (`models_by_tier`).
- A provider's `auth` env var is removed from every child process except that provider's own
  calls; git, checks, and notifications get no provider key.
- **Preflight** (start of `run`/`drain`/`serve`/`triage`): checks each CLI's version against its
  latest release (a mismatch is only a notice) and sends one probe call to every routed model.

### 8.2 Routing

`routing` rows map `(tier, surface)` to an ordered list of candidates. A surface with no row
falls back to the `(tier, review)` row. The model is the candidate's `model` or the provider's
`models_by_tier[tier]`.

### 8.3 Admission, breakers, droughts

- Each provider has `limits.concurrency` call slots. A call waiting over 60s spills to the next
  candidate.
- `circuit_breaker.k` (default 3) consecutive outages open a provider for `cooldown_minutes`
  (default 10).
- A quota error cools the provider for `limits.quota_window_minutes`. An auth error drops it for
  the session and notifies.
- When no candidate is available the stem is **drought-parked**: journaled
  `infra_error / provider_drought`, no cap drawn, re-offered when a route frees up.

### 8.4 Prompt specs and the driver

Every model call goes through one driver (`chupa/driver.py`) using a prompt spec from `specs/`:

| Spec | Used for | Replies |
|---|---|---|
| `implement.md` | writing the change | packing slip: outcome, summary, second problems |
| `review.md` | judging the diff | approve / snag / rma |
| `diagnose.md` | explaining a failure | retry / escalate / split / reject / abandon-human + lessons |
| `rework.md` | rewriting or splitting a ticket | update / split / escalate |
| `requisition_review.md` | checking an authored ticket is buildable | approve / snag / rma |
| `author.md` | writing a ticket from a Suggestion Box message | stem + ticket |
| `triage.md` | settling a Suggestion Box message | author / tombstone / decision |
| `retro.md` | proposing prompt-spec changes | proposals |

Specs always load from the engine's `specs/`, never from the host. Host material is injected only
inside `<<chupa-data:...>>` blocks; a rendered prompt over 400,000 characters is refused. The
driver re-prompts with findings when a reply is invalid or fails a gate, up to `caps.retry`
times; each call is spooled under `state_dir/spools/`.

### 8.5 Spend and redaction

- Spend is the sum of each call's journaled cost (the stream's reported USD, else the provider's
  `est_cost_per_call_usd`). `status` prints the total.
- Configured secret values are replaced with `[REDACTED:NAME]` in spools, the engine log,
  provider captures, notifications, and retro reports. The journal itself is not scrubbed; model
  results are scrubbed before they are journaled.

## 9. Suggestion Box

### 9.1 Messages

Problems found while working are filed, not fixed in the current diff. Classes: `suggestion`,
`failure_report`, `override_report`, `retro_finding`, `bug_report`. Each message is a file in
`state_dir/box/`. A repeat of the same signature is folded into the existing message.

### 9.2 Triage

`triage` (or `serve`'s triage loop) settles pending messages one at a time:

- `author`: run the Author stage to write a ticket.
- `tombstone`: the message is already covered by a merged or committed ticket. A third
  re-report reopens it.
- `decision`: record a decision in `tickets/decisions/<id>.md`.

### 9.3 Author and starting state

The Author stage writes `tickets/<stem>/ticket.md` with `source: box:<class>`, has
`requisition_review` check it, and commits it. Its state is `draft` (needs `confirm`) if the
message was reopened, the review baseline is not GO, `engine_plane_safety_inventory` is empty or
touched by the ticket's fence, or the ticket carries a `gate_bypass`. Otherwise `box_policy`
decides per message class.

### 9.4 Host bug reports

When `report_inbox` is set, triage ingests host bug reports (`*.json`, closed schema, bounded
replay and log evidence) into the Suggestion Box as `bug_report` messages, keeping the evidence
in custody for the authored bug ticket.

### 9.5 Retro

The retro reads the journal since the last report. It runs after 25 merges, 7 days, or a spike
of failures, and at drain quiescence. It commits `tickets/retro/NNNNNN.md` (measurements,
scorecard, proposals) and files each proposal as a `retro_finding`.

### 9.6 Scorecard and baseline

- The **scorecard** counts, per gate and review surface, catches, escapes, and bypasses, and flags
  a surface with 25+ evaluations and no catch as a prune candidate.
- The **review baseline** is a GO / NO_GO verdict recorded by the eval harness
  (`eval/harness.py`). GO counts only while the recorded review and author models and spec
  versions still match the config. It gates Author starting state and `serve` merge supervision.

## 10. State on disk

Everything lives under `state_dir` (this repo: `.chupa/state`).

### 10.1 Files

| Path | Holds |
|---|---|
| `journal/NNNNNN-YYYYMMDD.jsonl` | The journal (section 10.2). |
| `engine.log` | Diagnostics, redacted, rotated; never authoritative. |
| `spools/` | Per-attempt prompts, outputs, and command output; `spools/providers/` holds raw CLI captures. |
| `chupa.lock` | The single-writer lock. Its JSON identity is informational; the kernel frees the lock when the holder dies. |
| `worktrees/` | Ticket worktrees. |
| `box/` | Suggestion Box messages and report custody. |
| `control/` | `active.json` and the control request inbox. |
| `heartbeat` | Touched by `serve` while all its loops are healthy. |

### 10.2 The journal

The journal is the record of truth: append-only JSON lines, fsynced per event. Event types:
`state_transition` (run states), `cap_consumed`, `signal` (a closed list of named signals),
`effect_intent` / `effect_completion`, `timer_armed` / `timer_fired`.

An **Effect** is an action keyed so it happens once: a key with a recorded completion replays
the recorded result instead of acting again. Model calls, ticket-plane commits, merges, pushes,
and notifications are Effects, so a crash never repeats one.

### 10.3 `status`

`status` is a write-free projection of the journal:

1. Stems by last state: merged, in flight, blocked (every other state, including
   `already_satisfied`).
   `already_satisfied` remains in this state listing as a settled no-op; it is never diagnosed
   or awaiting a verdict in the Reject queue.
2. Every intake.
3. Total spend.
4. The Reject queue.
5. Tombstones and reopens.
6. The current retro window's scorecard and provenance.

## 11. Config

One `config.yaml`, validated strictly: unknown keys, explicit nulls, and bad values are refused
with the fix. The full field inventory is in `docs/host-contract.md`.

| Area | Controls |
|---|---|
| `schema_version`, `state_dir`, `worktree_root` | config version; where state and worktrees live |
| `providers`, `routing`, `routing_default_tier` | models and which serves what (section 8) |
| `review` | `gate_severity`, host `autofix` commands and `mechanical` checks; declared `surfaces` entries are refused at config load; `trigger_map` is accepted, unused |
| `merge` | `safety_checks`, conflict `strategies` (serve only) |
| `caps`, `circuit_breaker` | failure bounds (section 6.4, 8.3) |
| `scheduler`, `drain` | `max_unmerged`; `max_runtime_hours`, `max_ticket_minutes` |
| `engine_plane_safety_inventory`, `box_policy` | Author starting state (section 9.3) |
| `notify`, `report_inbox`, `context_files` | notification command; host bug report folder; extra Implement context |

## 12. Host projects

The block carries only process rules that hold for every host; codebase rules belong in the project-owned remainder.

- `chupa core` writes the managed block between `<!-- chupa:core begin -->` and
  `<!-- chupa:core end -->` in `CLAUDE.md` (for `claude`) or `AGENTS.md` (other CLIs), for each
  routed provider. On first adoption the block goes above the existing content; after that only
  the block is replaced. Project text outside the block is the host's, but a paragraph that
  tells chupa how to run (for example "chupa must ...") is refused.
- The `core_drift` gate fails a ticket when a routed conduct file's block is not current.
- `doctor` checks a host's setup without changing anything.
- The `chupa.testreport` pytest plugin accepts `--chupa-results PATH` and writes JSON with
  `schema_version: 1` and a `tests` map from pytest node IDs to `passed`, `failed`, or `skipped`.
- A host provides `config.yaml`, its conduct files, and its tickets. `docs/host-contract.md` is
  the full host-facing contract.

## 13. Bootstrap-era machinery still in the code

chupa built itself from `CHUPA_PLAN.md` through self-seeding phases, now finished. This code
remains and does not apply to ordinary tickets:

- **Seeding:** a ticket whose fence includes `tickets` writes `source: seed` tickets, reviewed by
  `requisition_review` at its own Check and lifted as `chupa(<stem>): seeds`; the
  `requisition_review` merge gate; `seeding.max_seeds_per_admission` (read by nothing).
- **Plan pointers:** `## Plan contract` and `## Exit-read window` ticket sections and
  `CHUPA_PLAN.md#...` fence anchors, resolved against `CHUPA_PLAN.md`. The plan structure lint.
- **Spec-gap hardening:** a `spec_gap` finding holds the stem and files a `plan-gap-<n>` ticket
  that edits `CHUPA_PLAN.md` (`chupa/hardening.py`, `runner.hold_on_hardening`); the `hardening`
  cap; `plan_units` on terminals. Spec-gap hardening is reached only through the seed review's
  mechanical entry-unit check.
- **Plan reads:** runtime reads of `CHUPA_PLAN.md` go through one function; an absent plan is
  tolerated for hosts that do not have the file. Prompts carry no plan text.
- **Phase exits:** a forced retro before any `phase<N>-exit` stem; eval report artifacts
  (shakeout, soak, reliability battery, host loop, exit receipt).
- **Bootstrap files:** `bootstrap/` (conductor, state, operator setup) and the box's bootstrap
  ingest.
