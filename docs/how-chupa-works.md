# How chupa works

This document describes chupa as the code behaves today. It is maintained: a ticket that changes
behavior described here updates the matching section in the same change, and tickets cite its
section headings. `CHUPA_PLAN.md` is the frozen bootstrap design record; it is history, never a
reference for current behavior. Where this document and the code disagree, the code wins and
this document is fixed.

Related documents: `chupa/docs/host-contract.md` (full config schema and host-facing contract) and
`chupa/docs/host-authoring.md` (what to write in a ticket).

## 1. What chupa is

chupa (CLI Harness for Unattended Pipeline Agents) runs tickets against a git repository (the host): Implement writes the change on a branch,
Check runs mechanical gates, Review has a model judge the diff, and Merge squashes the branch onto
`main`. Failures are harvested, diagnosed, retried within caps, or held for a human.

Two planes meet in chupa:

- **Engine plane** (chupa-owned): how work runs. Ticket grammar, prompt specs (`chupa/specs/`), gates,
  caps, git rules, the journal.
- **Host plane** (repo-owned): what to build. The host's code, docs, config, and the ticket
  content. Host material enters prompts as data, never as instructions.

chupa develops itself: this repo is both the engine and its own first host.

## 2. Commands

[Install chupa](../chupa/docs/host-contract.md#install) and run `uv run chupa <verb>`; from a checkout, run
`uv run python -m chupa <verb>` (global flag `--config PATH`, default `config.yaml`
at the checkout root). In this repo, use `./dev.py` (section 2.2).

### 2.1 Verbs

Journal appends take a short-held exclusive `journal.lock` for tail repair, segment roll, and the write.

Exit codes are one contract for every verb: **0** success or quiescence, **1** a non-ok ticket
outcome or a halted/killed run, **2** an engine refusal (bad config, lock held, invalid intake,
journal corruption, provider setup, missing executable, corrupt conduct markers). A refusal
prints `chupa <verb>: <message> -- <what to do instead>`.

| Verb | Lock | What it does |
|---|---|---|
| `watch [--once]` | no | Prints a live text view of the configured host state, refreshing every three seconds unless `--once` is supplied. |
| `snapshot` | no | Prints the extension snapshot as JSON, including the absolute state directory and `configPath` for the resolved configuration file. |
| `status` | no | Prints the journal projection (section 10.3). Read-only. |
| `stats [--window W] [--json] [--tree]` | no | Prints a read-only health and efficiency projection over a time or ticket window (default `7d`); it is not an authority. |
| `lint [stem ...]` | no | Validates ticket grammar, intake claims, committable bug evidence, and the `drain.max_ticket_minutes` stuck ceiling without running tickets or writing files, journal events, or git state. With no stems, checks every ticket except those settled or rejected in the journal; with no journal, checks all tickets. Prints each finding and its fix, then `lint: <valid>/<total> tickets valid`. Exits 0 when valid, 1 for findings, or 2 for a missing named ticket or unreadable tickets directory. |
| `covmap` | no | Runs `review.coverage_map.argv` and writes `<state_dir>/coverage-map.json`; exits 0 on success or 2 on refusal. |
| `covgate [--gate PATH] [--report PATH] -- <argv>` | no | Runs the unit-test command, then checks its fresh coverage report against `test-gate.toml` (default report `coverage.json`; paths relative to the invocation directory). Returns the command’s nonzero exit code, or 0 on coverage pass, 1 on threshold failures, or 2 for a refusal. |
| `doctor` | no | Checks venv, config load, git, lock probe, journal readability, and core check. Git is not probed if config fails to load. Exit 2 on any failure. |
| `prompt <diagnose\|running\|review> <stem>` | no | Prints an operator prompt for an existing ticket without writing state; `diagnose` selects the running prompt for a live running ticket. |
| `core` | no | Rewrites the managed `chupa:core` block in each routed agent's conduct file (section 12). |
| `probe [PROVIDER...]` | no | Probe declared providers and models. |
| `docs` | no | Prints the installed host guide paths and their purposes. |
| `migrate-config` | no | Migrates a `schema_version: 0` config to the current schema. |
| `new <stem> --kind feature\|bug\|chore` | no | Writes `tickets/<stem>/ticket.md` with section placeholders for the selected kind (default `feature`) and `state: draft`, and lints it; intake confirms it. Bugs include `## Regression`, require `--evidence <file>...`, and copy those files into `tickets/<stem>/evidence/`. Refuses a bad, reserved, or existing stem, or unknown kind (exit 2); successful authorship exits 0. |
| `order <stem> [--priority P0\|P1\|P2\|P3] [--runs-before [stem ...]]` | no | Validates and edits priority and/or runs-before ordering in the working tree; a bare `--runs-before` removes the section. Refuses a running ticket while an engine is live, and settled, rejected, missing or invalid tickets. An interrupted run with no live engine is editable. Intake commits the edit. |
| `review <stem>` | commit only | Only the named ticket's pending changes are committed through intake first; other pending tickets are left untouched. Reviews the committed ticket against merged code and journals its verdict and ticket blob SHA. A ticket with an unmerged dependency gets a provisional review that is printed but not journaled, so the drain reviews it again before its first run. Refuses missing, intake-failed, settled, or rejected tickets without a model call. Prints findings and exits 0 on approve, 1 on snag or rma. |
| `run <stem>` | yes | Reconciles orphans, intakes only the named ticket’s pending changes, then drives that ticket through every stage. Refuses a stem that failed intake, is missing, invalid, merged, not `confirmed`, or has unmerged dependencies. |
| `drain [--detach]` | yes | Runs every eligible ticket to quiescence (section 7.1); `--detach` starts its own session and appends to `<state_dir>/drain.out`. |
| `serve` | yes | Runs the continuous daemon until `kill`, `stop`, or a signal (section 7.2). |
| `retro` | try | Runs a retro report now or queues one on the running engine (section 9.5); refuses while a non-engine holder has the lock. |
| `suggest <summary>` | no | Files an idea straight into the Suggestion Box. |
| `triage [id ...]` | yes | One sequential pass over named pending messages, or all pending messages (section 9.2). |
| `dismiss <id> ...` | yes | Dismiss named messages without a model call. |
| `prompt box <id> ...` | no | Print a prompt for discussing named box messages. |
| `pause` / `resume` / `kill` / `stop` | try | With a running engine, publish a control request to it (section 7.3). With a non-engine holder, refuses and asks the operator to wait. With none: `kill` and `stop` refuse (exit 2); `pause`/`resume` print "nothing running". |
| `confirm <stem> [--yes|--extension]` | try | A person at a terminal answers `y` to keep (or uses `--yes` to skip the prompt): promotes a draft to confirmed, keeps a Reject-queue item (section 6.6). Same-content repeat keeps are refused for command-line confirms; the extension uses `--extension` to allow them. Intakes only the named ticket’s pending changes; with drain or serve running, does so before publishing the verdict to the engine; refuses while a non-engine holder has the lock. |
| `reject <stem> [--yes]` | try | A person at a terminal answers `y` to kill (or uses `--yes` to skip the prompt): stamps the ticket `rejected` (section 6.6). Refuses settled stems. Intakes only the named ticket’s pending changes; with drain or serve running, does so before publishing the verdict to the engine; refuses while a non-engine holder has the lock. |

### 2.2 `./dev.py`

The repo's one dev command; standard library only, every task through `uv`.
`./dev.py test` runs the suite in parallel on the available cores by default.
Each test has a 120-second hard limit.
Tests live in `tests/unit/` (no disk, network or process; run under `chupa.testguard`) and
`tests/integration/`. Run one suite with `./dev.py test tests/unit` or
`./dev.py test tests/integration`.
A unit test file may share its name with an integration test file.

| Subcommand | Runs |
|---|---|
| (none) | `uv run pytest -q` |
| `test [args]` | pytest with those args |
| `triage [ID ...]`, `dismiss ID ...` | One matching chupa call with all supplied IDs |
| `docs` | `chupa docs` |
| `probe [PROVIDER...]` | `chupa probe` with the supplied providers |
| `suggest SUMMARY` | `chupa suggest <summary>` |
| `core` | `chupa core` |
| `covmap` | `chupa covmap` |
| `stats [--window W] [--json]` | `chupa stats` with the supplied options; a read-only projection |
| `new STEM [--kind K] [--evidence FILE...]` | `chupa new <stem> --kind feature\|bug\|chore` (default `feature`); bugs require `--evidence` and copy the files into `tickets/<stem>/evidence/` |
| `order STEM [--priority P] [--runs-before [STEM ...]]` | `chupa order` with the supplied ordering options |
| `lint [STEM...]` | `chupa lint [stem ...]` (read-only; no writer lock) |
| `review STEM...` | `chupa review` once per stem, stopping on the first non-zero exit |
| `run STEM` | `chupa run <stem>`: one ticket through every stage, under the lock |
| `status`, `serve`, `kill`, `stop` | the matching chupa verb |
| `drain` | `chupa drain --detach` |
| `confirm STEM... [--yes]`, `reject STEM... [--yes]` | `chupa confirm` or `chupa reject` once per stem; a person at a terminal answers `y` for each stem unless `--yes` is passed |
| `watch [--once]` | `chupa watch` through `uv`: a read-only live view of the engine and queue |
| `publish` | with `UV_PUBLISH_TOKEN` set, bumps the patch version, then builds and uploads; the operator commits `pyproject.toml` and `uv.lock` |
| `vscode-package` | writes the `pyproject.toml` chupa version into the `Built for` line of `vscode-chupa/README.md`, then packages the current manifest version into `dist/vscode-chupa-<version>.vsix` and prints the Marketplace upload page; under WSL also prints the Windows path to paste into the upload dialog |
| `vscode` | bumps the patch version in `vscode-chupa/package.json` (VS Code keeps an extension's old icon until its version changes), packages it with `npx @vscode/vsce`, and installs it with `code --install-extension --force`; reload the window to load it |

To release the extension, bump `version` in `vscode-chupa/package.json`, run
`./dev.py vscode-package` to write the `pyproject.toml` chupa version into the `Built for` line of `vscode-chupa/README.md`, commit that README change, and upload the printed VSIX on the [chunkydragon management page](https://marketplace.visualstudio.com/manage/publishers/chunkydragon).
Under WSL, paste the printed Windows path into the upload dialog.
Choose New extension for the first release and the extension's Update action for subsequent releases.
The Marketplace refuses a version it already holds.

`vscode-chupa/` is an operator-only VS Code extension: an Activity Bar view of every ticket as an
SCM-style graph (blocked, queued, running, merged) with a detail pane. A line between ticket rows means a dependency; merged rows show their history line. Running and queued rows show their priority. Its Activity Bar badge shows the queued and running ticket count while the engine is alive, or the blocked and queued count while it is stopped, and is hidden when the count is zero. The Tickets view's More Actions
menu holds Ticket lifecycle, which opens `vscode-chupa/media/ticket-lifecycle.svg`, a hand-drawn diagram of ticket states.
The Confirm and Reject items are on exactly when the extension verdict would be accepted, as decided by the shared verdict predicate.
The Tickets view’s play button and Engine… picker start drain detached. The picker also runs serve, stop, kill, status, or retro. Its start/stop icon follows the snapshot engine flag, which is true only while a drain or serve holds the lock; `chupa.playAction` selects drain or serve for starting. Open config.yaml, also in More Actions, opens the snapshot’s `configPath`. Recent Steps row kinds are the closed vocabulary `STEP_KINDS` in `chupa/observe.py`, and a test fails until each step in it has its own icon. Recent Steps opens a step’s file when it exists; an Author row opens its Suggestion Box message, authored ticket, or decision record. The collapsed Stats view shows health figures for the window configured by `chupa.statsWindow` (default `7d`). The Suggestion Box view lists messages, supports multi-selection and manual triage or dismissal, and shows message details alongside tickets. `chupa snapshot` builds its data read-only from the configured host state and `order_tickets`, holding tickets awaiting an operator and those held by the drain's `parked_blob` rule; `chupa/graph.py` computes the graph layout for the extension to draw. The engine never runs the extension.

## 3. Tickets

### 3.1 Files and fields

A ticket is `tickets/<stem>/ticket.md`. The stem matches `^[a-z0-9][a-z0-9-]{1,63}$`;
`decisions` and `retro` are reserved. `chupa/tickets.py` owns the format; `chupa/docs/host-authoring.md`
says what goes in each section.

Frontmatter fields that drive behavior:

- `state`: `draft` (awaits `confirm`), `confirmed` (dispatchable), `rejected`, `merged`.
- `source`: `human` (hand-written), `box:<class>` (written by the Author stage), `seed`
  (historical bootstrap tickets; nothing writes it now).
- `kind`: `feature`, `chore`, or `bug` (a bug must carry `## Regression` and evidence,
  section 5.2).
- `priority` (P0-P3), `## Depends on`, and the optional `## Runs before` section order the queue. `agent_tier` / `agent_effort` pick the
  starting model capability (section 6.4). `gate_bypass` softens named engine gates for this
  ticket (section 5.3).

### 3.2 Intake

`drain` and `serve` intake every pending ticket; `review`, `run`, `confirm`, and `reject` intake only the named stem, including before verdict handoff to a running engine:

- It reads status, checks for stray staged paths, and commits under one `commit.lock` hold.
- It finds new or modified `tickets/<stem>/ticket.md` files in the working tree (`git status`).
- A new hand-written stem must be `draft` or `confirmed` and must not claim a machine `source`;
  intake stamps it `source: human`, `state: confirmed`.
- Every ticket read (intake, lint, confirm, drain, serve, run, and Author) refuses a bug without
  regular, non-symlink evidence under `tickets/<stem>/evidence/`. Intake and lint also require
  committable, non-gitignored evidence. Settled and rejected tickets are exempt, including at intake
  when the journal records settlement.
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

Intake, `lint`, `new`, and requisition review also check that the Regression command names
a carried path, every carried prefix is fenced, and a fenced file with a positive
`test-gate.toml` file floor has a fenced path under `tests/unit/`. These authoring checks
do not change scan or merge admission. Requisition returns a snag without a model call
when ticket lint fails. A malformed coverage gate is a lint finding.

### 3.3 What the engine writes back

Stages write into an outbox in the ticket's worktree (`tickets/<stem>/` inside it). The lift
copies each selected new or changed artifact to the main checkout's `tickets/<stem>/` and commits it on `main`
as `chupa(<stem>): <kind>`, once per attempt (an Effect, section 10.2). `ticket.md` is never
lifted from a worktree: the agent cannot edit its own ticket. Each lift takes only its named artifact,
refuses symlinks, and refuses a file over 256 KB.

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

`runner.drive` reviews committed ticket content before Implement unless the journal already records an approval for that blob. It then takes the ticket through Implement, Check, Review, then Merge.

### 4.1 Worktree

Each attempt gets a fresh worktree at `<worktree_root>/<stem>` (default
`<state_dir>/worktrees/<stem>`) on branch `<stem>`, cut from `main`. Any old worktree and branch
of that stem are removed first. Scratch worktrees under `.base/` and `.regression-base/` are
created at the merge base for base-red reruns and the bug gate, and removed after.

### 4.2 Implement

The `implement` prompt (`chupa/specs/implement.md`) gets the ticket text, its `## Context` files plus
`config.context_files`, and a "Prior attempts" block (last terminal, findings, diagnosis lessons,
log tails) when this is a retry. Context entries may select a Python top-level definition or
assignment (`path.py::Name`), a class method (`path.py::Class.method`), or a Markdown heading
(`path.md#Heading`), including its subheadings. Heading text may start with the selector followed
by a space. Selectors must resolve uniquely, and a file cannot be listed both whole and by section.
Ticket Context files are UTF-8 text; lint renders each entry exactly as Implement does.
`config.context_files` remains whole-file. The model works in the worktree with write access and replies:

- `ok`: it committed the change.
- `already_satisfied`: every acceptance criterion already holds on `main`; Check must prove it
  with green Verification on an empty diff.
- `premise_failed`: the ticket cannot be done as written; findings say why and name every forced
  file outside the scope fence separately.

Implement runs each Verification command whole and in sequence and reports that final result.
Implement runs the host hard always-trigger checks once after its last edit.
Implement also runs each host hard coverage gate once after its last edit when the diff touches a file that gate measures.
Failures reproduced on the base commit are reported as second problems rather than `premise_failed`.
Implement updates documentation statements the diff makes false inside the scope fence in the same commit.

The Implement prompt separates unit and integration suites. Unit tests use fakes for clock,
filesystem, processes and network, avoid disk, network and processes, and run in milliseconds.
Integration tests exercise seams using bounded, parallel-safe fixtures or simulators. Flaky tests
must have nondeterminism removed, without retries. Coverage thresholds and test time budgets must
not be lowered unless an acceptance criterion requires it; an unmet gate requires `premise_failed`.

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
3. A failing command is rerun at the merge base. If it also fails there and names no path present in the branch but absent at the merge base, it is **base-red**: a
   pre-existing failure, excluded from the verdict and filed once to the Suggestion Box. A command naming a branch-only path is never base-red.
4. Runs the engine Check gates (section 5.1).
5. Runs triggered host checks in config order, attributing failures also red at base to main.
6. Writes and lifts `checks.json`.

A hard gate failure ends the attempt `gate_failed`. Soft failures are recorded and the run
continues. `already_satisfied` stops here: there is no diff to review.

### 4.4 Review

The `review` prompt (`chupa/specs/review.md`) gets the ticket, the branch diff, and the previous review's
findings when it snagged, in a read-only session. It reports every defect in one pass, listing each
instance of a repeated flaw separately and marking findings that remain open. Verdicts: `approve`, `snag` (findings: `logic`, `acceptance`, `scope`, `leak`), or `rma`
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
- Before squash, `dirty_checkout` refuses tracked main-checkout edits overlapping the branch and staged changes outside the branch; commit or revert overlapping edits, or commit or unstage staged changes, and retry.

## 5. Checks

### 5.1 Engine gates

Every engine gate is hard by default.

**Check gates** (on the branch head):

| Code | Fails when |
|---|---|
| `scope_fence` | A changed file is outside `## Scope fence` (the stem's own outbox is exempt, except `ticket.md`). |
| `verification` | A Verification command fails and was green at the base; or `already_satisfied` came with a diff; or a required report is missing or invalid. |
| `run_record` | `run.md` is missing, or lacks its six fixed sections in order, or has an unknown outcome. |
| `diff_budget` | More than 1,500 inserted lines: split the ticket. |
| `core_drift` | A routed conduct file's managed `chupa:core` block does not match the current template (section 12). |
| `bug_evidence` | For `kind: bug` only: see section 5.2. |

**Merge gates** (on the rebased candidate, at admission):

| Code | Fails when |
|---|---|
| `ticket_schema` | The ticket on `main` no longer lints. |
| `post_rebase_regate` | The branch commits anything under `tickets/`, or the rebase was refused. |
| `correctness_review` | `review.md` on `main` is not an `approve` of the branch head that was reviewed. |

### 5.2 Bug tickets

A `kind: bug` ticket must prove the defect: at least one file under `tickets/<stem>/evidence/`;
a `## Regression` command that prints `{"regression_result": "pass"}` with exit 0 on the branch
head, and `{"regression_result": "defect"}` with a non-zero exit on the merge base with the
carried test or fixture files copied over it. Only files under `tests/`, `test/`, `fixtures/`, or
`fixture/` can be carried. `chupa/docs/host-authoring.md` explains the protocol for authors. Every ticket read (intake, lint, confirm, drain, serve, run, and Author) refuses a bug without
regular, non-symlink evidence. Intake and lint also require evidence that is not gitignored; intake
commits it with the ticket. Settled and rejected tickets are exempt, including at intake when the
journal records settlement. The Check gate still verifies the regression proof.

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
Missing or invalid results after a successful run or rerun fail the entry. Check records command wall time, outcome counts and slow tests from the first run, bounded by `slow_test_seconds` (default 1.0) and `slow_test_limit` (default 100). Readable coverage records the repository percentage and percentages for changed files. With a declared coverage.py JSON report, a flake also counts as edited when its test context covers a changed line or a line adjacent to a pure deletion. The host must run with `--cov-context=test`, `[tool.coverage.json] show_contexts = true` and `[tool.coverage.run] core = "ctrace"`; missing or invalid contexts fail classification.

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
   with reason `attempts cap spent`, skipping the cap draw, Diagnosis, and Rework.
5. `infra_error` / `timeout` draw the `infra` cap; `premise_failed` draws `premise_bounce`, except a requisition-stage snag ends before dispatch and draws no cap (section 6.7).
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

The `diagnose` prompt (`chupa/specs/diagnose.md`) reads the ticket, terminal, harvest, and run record
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
| `retry` | 3 (never above `diagnosis`) | each drain or serve re-offer, except after a `premise_failed` without escalation, a provider drought, or an `infra_error` or `timeout` that carries no escalation rung |
| `infra` | 3 | each `infra_error` or `timeout` (not droughts) |
| `premise_bounce` | 1 | each `premise_failed` (not over-bound renders or `requisition` snags) |
| `quarantine` | 5 | flake quarantine size |
| `poison` | 2 | read by nothing |

Failed attempts are `gate_failed`, `premise_failed`, `infra_error`, and `timeout` terminals.
A requisition-stage `premise_failed`, an `infra_error` with reason `provider_drought`, `budget_exceeded`, an `abandoned` reap,
settled terminals, and `rejected` do not count. The failure reaching `caps.attempts` is itself
routed with reason `attempts cap spent`, without another diagnosis or rework call, including
merge-conflict handoffs. Terminal routing also counts a pending failure after a published Rework
update or escalation and leaves the published ticket text intact. A published split still retires
its parent. The drain report shows the failed-attempt total, for example `attempts cap spent (5/5)`.

A spent cap, or a `reject` / `abandon-human` verdict, routes the stem to the Reject queue.
`escalate`, an Implement `premise_failed` whose Diagnose verdict is `retry`, or the same failure reason three times running, moves the stem up one **rung**: the
next higher tier whose Implement model differs, else one effort level higher. At the top rung
the stem goes to the Reject queue.

### 6.5 Rework

The `rework` prompt (`chupa/specs/rework.md`) proposes `update` (rewrite this ticket), `split` (two or
more new stems), or `escalate`. Each proposal is validated in a scratch worktree and reviewed by
`requisition_review`. Accepted proposals are committed as `chupa(<stem>): rework`. A split
journals `supersedes` and retires the original: its dependents wait on the successors.

### 6.6 The Reject queue, keep and kill

Keep and kill work while serve runs.

The Reject queue holds stems whose latest terminal was routed there, plus stems the drain finds
with a spent cap at quiescence. `status` lists them.
Settled stems (`merged` and `already_satisfied`) never await a verdict, even when a historical
terminal carries a Reject routing marker. `reject` refuses settled stems.

- **`confirm <stem>` (keep)** journals `reject_verdict keep actor: operator`. That resets the
  lineage, so every cap starts over. A second command-line keep at the same ticket content is refused: edit the
  ticket first. The extension uses `--extension` to keep unchanged content.
- **`reject <stem>` (kill)** stamps `state: rejected`, commits it, and files one Suggestion Box
  `failure_report` per confirmed ticket that depended on it ("re-wire, re-scope, or reject it").
  Those dependents stay blocked.
- **Machine keep:** drain and serve use `awaiting_operator` and `reofferable` to hold queued stems with a spent cap or `ticket_changed` and re-offer others with budget. `record_reoffer` journals `keep actor: machine` for a queued stem, then draws `retry` unless the terminal is `premise_failed` without escalation, carries `provider_drought`, or is `infra_error` or `timeout` without an escalation rung. A machine keep never resets caps. The snapshot holds Reject-queue stems only when they await the operator (content parks remain separate).
- `confirm` on a `draft` ticket promotes it to `confirmed` instead.

Keep and kill normally require a person at an interactive terminal to answer `y` at the prompt before the verdict proceeds. `--yes` and `--extension` skip the terminal check and prompt.

### 6.7 Other holds

- **`ticket_changed`:** a committed or uncommitted change to `ticket.md` during a run ends the
  attempt `gate_failed` and holds it in the Reject queue, with no diagnosis, Rework, or cap draw.
  Review the change to `tickets/<stem>/ticket.md`, then keep (`./dev.py confirm <stem>`) to run
  the changed ticket as a fresh attempt, or kill (`./dev.py reject <stem>`). Machine keeps do
  not release this hold. Stage boundaries, admission, and queued or confirmed merge admissions
  all check the dispatch identity. Rework updates between attempts are fresh ticket inputs.

- **Premise park:** a requisition-stage `premise_failed` draws no cap, makes no Diagnose call, and is not routed to the Reject queue. Edit the committed ticket to release it; no `confirm` is needed. The next review receives the last recorded review’s findings and the diff since, rules on those findings, and raises new findings only against changed text. Other premise failures: with the default `premise_bounce: 1`, the first `premise_failed` spends
  the cap and routes to the Reject queue via `premise_bounce cap spent`; only an operator
  `confirm` releases it. When a host sets `premise_bounce` above 1 and caps still have budget,
  an Implement premise overruled by Diagnose with `retry` escalates and is re-offered without an edit, drawing `retry` with the new rung and carrying the lessons. At the top rung it enters the Reject queue. Other premise failures park until their committed `ticket.md` changes; that re-offer draws no retry.
- **`budget_exceeded`:** not diagnosed, draws nothing. Ticket stages pass no spend budget, so in
  practice only eval runs reach it.
- **Reconcile:** whenever a verb other than pause, resume, kill or stop takes the writer lock, any stem still marked `running`
  (or with an unfinished effect) is reaped: harvested, journaled `abandoned`, worktree removed.
  `abandoned` stems stay eligible. With no engine running, `status` shows such a stem as interrupted, `reject`
  reaps and rejects it, and `order` treats it as open.
- **Flaky tests:** Check quarantines unedited fail-then-pass tests and releases them after a merged fix and a passing observation. Edited flakes and cap-blocked flakes fail Check.

## 7. Drain and serve

### 7.1 `drain`

A dispatch exception is journaled as an `infra_error` terminal, re-offered, and held in the Reject queue at the attempts cap.

1. Takes the lock, reconciles, fires due timers, runs the provider preflight, runs intake once.
2. Loops: reload config, honor pause/kill/stop, run intake between tickets, maybe run a retro, scan committed tickets (skipping stems settled or rejected in the journal), pick the
   next ticket, review its committed content if it lacks an approval, run it, merge it inline. Serve applies the same review before Implement and holds a premise-parked ticket until its committed content changes.
3. **Pick order:** confirmed, unsettled, not rejected, every dependency settled (through split
   successors); among eligible fresh tickets and re-offers, `## Runs before` orders named stems
   after the ticket naming them, with priority P0-P3, authored age, then stem breaking ties.
   Edges to ineligible stems never block a pick. Skipped: storm-held, drought-parked, Reject-queue stems without budget, and tickets
   whose `stuck` exceeds `drain.max_ticket_minutes` (default 90).
   Each pick records this order and its hints in `queue.json`; `watch` displays it.
4. **Quiescence:** when nothing is eligible, it re-offers parked stems with budget (drawing
   `retry`, subject to the exclusions in section 6.6), and stops when nothing changes.
5. **Report:** merged, parked (with reasons and the command to continue), blocked on depends,
   invalid tickets excluding those settled or rejected in the journal, drafts awaiting confirm. A requisition
   park lists its review findings under the parked line.

SIGHUP, SIGTERM, and SIGINT stop a drain as `kill` does: the running ticket is aborted and journaled, and the report says the drain is not quiescent.

Bounds: `drain.max_runtime_hours` (default 12) halts it (exit 1). The ceiling is carried across a self-upgrade handoff.

**Self-upgrade:** when draining the engine’s own source tree, a merge changing `chupa/` causes the drain to journal a handoff,
releases the lock, and re-executes itself so the new engine code runs the rest of the queue.
A host repo or pip-installed engine never self-upgrades through drain; upgrade those by reinstalling.
Both verbs use `uv run --project <engine checkout> python -m chupa` followed by their invocation arguments.

### 7.2 `serve`

The continuous daemon. On start it takes the lock, reconciles and rebuilds timers,
publishes `state_dir/control/active.json`, and runs four loops (every 0.1s):

- **Watcher:** runs intake and re-reads tickets, debounced, skipping stems settled or rejected in the journal; a ticket that fails to parse keeps
  its last good version.
- **Dispatch:** the scheduler runs one ticket at a time. It waits while
  `scheduler.max_unmerged` (default 2) finished tickets are waiting to merge, while paused, or
  while a stem is held (Reject queue awaiting an operator, storm, drought, or a premise or diff-budget park at unchanged ticket content). After a failed terminal, serve puts the ticket back for the re-offer rule and draws `retry` on re-offer as drain does, subject to the exclusions in section 6.6. Each fresh dispatch reviews committed content without an existing approval before Implement. Among eligible tickets,
  `## Runs before` orders named stems after the ticket naming them; priority, authored age,
  and stem break ties. Edges to ineligible stems never block dispatch.
- **Merge queue:** serial admission (section 7.2.1).
- **Box intake:** ingests host bug reports into the Suggestion Box and never triages.

Maintenance on each loop: control requests, timers, orphan sweeps, heartbeat
(`state_dir/heartbeat` mtime), notification replay, and checkpoint pushes. If any loop dies,
`serve` stops.

Requested retros and automatic retros due after a ticket settles stop new admission, wait for
the next idle point, run, and then resume admission. A pending stop takes precedence.

A git-checkout engine records its `chupa` tree at startup and checks it before
admission and after merge passes. A change stops new admissions; after running tickets and
pending or active merges finish, serve journals `serve_handoff`, cleans up, closes the journal,
releases the lock, and spawns the new serve. A pending kill wins. An accepted stop waits for the same idle condition and exits without spawning. Non-git engines do not watch.

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
5. Squash-merge as in section 4.5, and verify `main`'s tree equals the checked tree.

- Before the admission receipt, `dirty_checkout` refuses tracked main-checkout edits overlapping the branch and staged changes outside the branch; commit or revert overlapping edits, or commit or unstage staged changes, and retry.

### 7.3 Control

`confirm` and `reject` publish verdict requests to the running drain or serve, which applies them.

`pause`, `resume`, `kill`, `retro`, and `stop` write a request file to `state_dir/control/inbox/`, bound to the
running engine's lifecycle id. The engine journals a `control_decision` (accepted, stale, or
rejected) for each request. Pause stops new dispatch; resume must name the advertised hold;
kill stops the engine at the next safe point. Stop admits no new ticket, lets work in progress finish and merge, then exits and releases the lock; unlike pause, it ends the process. `run` does not read control requests.

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

Three CLI adapters ship: `claude`, `codex`, and `qwen` (Qwen Code against a local Ollama model at the provider’s `base_url`). Only `kind: cli` providers are accepted.

- Implement is the only surface with write access (`claude --permission-mode
  bypassPermissions`, `codex --dangerously-bypass-approvals-and-sandbox`, `qwen --approval-mode yolo`) and runs in the
  ticket's worktree. Every other surface is read-only.
`claude` and `qwen` read `CLAUDE.md`, and `codex` reads `AGENTS.md`. chupa points qwen at `CLAUDE.md` through its packaged `qwen-settings.json`.

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

`chupa/specs/ask/` holds operator prompt templates rendered by `prompt`, not driver specs.

Every model call goes through one driver (`chupa/driver.py`) using a prompt spec from `chupa/specs/`:

| Spec | Used for | Replies |
|---|---|---|
| `implement.md` | writing the change | packing slip: outcome, summary, second problems |
| `review.md` | judging the diff | approve / snag / rma |
| `diagnose.md` | explaining a failure | retry / escalate / split / reject / abandon-human + lessons |
| `rework.md` | rewriting or splitting a ticket | update / split / escalate |
| `requisition_review.md` | checking an authored ticket is buildable, including one-by-one accounting for coverage dependents and data-file consumers outside its fence, and the unit coverage floor check; a missing or invalid configured map snags | approve / snag / rma |
| `author.md` | writing a ticket from a Suggestion Box message | stem + ticket |
| `triage.md` | settling a Suggestion Box message | author / tombstone / declined |
| `retro.md` | proposing prompt-spec changes | proposals |

Specs always load from the engine's `chupa/specs/`, never from the host. Host material is injected only
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
`state_dir/box/`. A repeat of the same signature is folded into the existing message. Sessions file `suggestion` messages with `suggest` directly into the box.

### 9.2 Triage

`triage` settles named pending messages, or all pending messages when no IDs are supplied, one at a time:

- `author`: run the Author stage to write a ticket.
- `tombstone`: the message is already covered by a merged or committed ticket. A third
  re-report reopens it. Retro recurrences use the same re-report rule.
- `declined`: record a decision in `tickets/decisions/<id>.md`.

`dismiss <id> ...` records operator decisions without a model call; unknown IDs refuse before any message is settled.

### 9.3 Author and starting state

The Author prompt embeds the authoring guide and skeletons, and each re-prompt carries the last parsed ticket in `previous_reply`. Each later review receives the previous review and the diff from the text it judged. The Author stage writes `tickets/<stem>/ticket.md` with `source: box:<class>`, has
`requisition_review` check it, and commits it. Its state is `draft` (needs `confirm`) if the
message was reopened, the review baseline is not GO, `engine_plane_safety_inventory` is empty or
touched by the ticket's fence, or the ticket carries a `gate_bypass`. Otherwise `box_policy`
decides per message class.

### 9.4 Host bug reports

When `report_inbox` is set, serve, drain, and triage ingest host bug reports (`*.json`, closed schema, bounded
replay and log evidence) into the Suggestion Box as `bug_report` messages, keeping the evidence
in custody for the authored bug ticket. Drain ingests between tickets.

### 9.5 Retro

Spike kinds count override invoices on merges, rework orders, gate-failure transitions,
integration-red conflict facts, reject queue routed transitions or reject arrivals,
premise-failed transitions, infra-error transitions (including provider drought), flake
detection signals, and escape signals for automatically reopened tombstones.

The retro reads the journal since the last report. By default `retro.test_timing` includes each Check gate’s per-invoice counts and duration plus each slow test’s maximum duration and invoice count. `retro.coverage` includes the latest repository percentage and each file’s latest and minimum percentages and invoice count. Set either switch to false to omit its summary. During a drain it runs between tickets, never
between attempts of one ticket, when due at the `retro:` thresholds: by default 25 merges, 7 days, or 5 events of one spike kind. A requested retro runs at the drain’s next between-tickets point. Serve runs requested retros and automatic retros due after a ticket settles at its next idle point, then resumes admission. Each nested `retro.merges`, `retro.days`, and `retro.spikes` block has an `enabled` switch; their thresholds are `merges.every`, `days.every`, and `spikes.count`. The nonempty `spikes.kinds` allowlist selects which kinds can trigger; measurements still report every kind. The master `retro.enabled: false` disables automatic retros even if sub-triggers are enabled; run one on demand with `retro`. Config load refuses an enabled master with all three triggers disabled (enable a trigger or set `retro.enabled: false`) and duplicate spike kinds (list each kind once). It commits `tickets/retro/NNNNNN.md` (measurements,
scorecard, proposals) and files new proposals as `retro_finding` messages. It supplies prior findings to the model; a proposal matching an existing cause counts as a recurrence on that message. A recurrence after its ticket fix merged reopens the finding for a new fix. Proposals identify either prompt-spec paths or repository paths for a test repair. Test repairs name one issue: `unit-io`, `slow`, `drift`, `flaky`, `coverage-hard`, `over-mocking`, `weak-assertion`, `shared-state`, `duplicate`, or `skip-rot`.

### 9.6 Scorecard and baseline

- The **scorecard** counts, per gate and review surface, catches, escapes, and bypasses, and flags
  a surface with 25+ evaluations and no catch as a prune candidate.
- The **review baseline** is a GO / NO_GO verdict recorded by the eval harness
  (`eval/harness.py`). GO counts only while the recorded review and author models and spec
  versions still match the config. It gates Author starting state only.

## 10. State on disk

Everything lives under `state_dir` (this repo: `.chupa/state`).

### 10.1 Files

| Path | Holds |
|---|---|
| `journal/NNNNNN-YYYYMMDD.jsonl` | The journal (section 10.2). |
| `engine.log` | Diagnostics including `engine_start` and `engine_stop` for drain, serve and run, and `phase_start` and `phase_end` for preflight and retro checks, and stage start/end events for every stage, including Check and merge. Stages do not nest on one driver; a gate run inside a stage logs under that stage. Requisition reviews nested in author or rework have no stage events of their own; a standalone review logs them under the reviewed ticket's stem; redacted, rotated, and never authoritative. |
| `queue.json` | Derived pick order, timestamp, and `Runs before` hints for watch. |
| `spools/` | Per-attempt prompts, outputs, and command output; `spools/providers/` holds raw CLI captures. |
| `chupa.lock` | Engine lock held by `run`, `drain`, `serve` and the other verbs that still take it. Its JSON identity records the holder verb, used to decide whether it consumes control requests; the kernel frees the lock when the holder dies. |
| `commit.lock` | Serializes git index writes and commits, with a 60-second wait. |
| `journal.lock` | Short-held exclusive lock for every journal append, covering tail repair, segment roll, and the write. |
| `worktrees/` | Ticket worktrees. |
| `box/` | Suggestion Box messages and report custody. |
| `control/` | `active.json` and the control request inbox. |
| `heartbeat` | Touched by `serve` while all its loops are healthy. |

### 10.2 The journal

The journal is the record of truth: append-only JSON lines, fsynced per event. A Journal instance parses each byte once and re-reads only appended lines during normal append-only operation. Event types:
`state_transition` (run states), `cap_consumed`, `signal` (a closed list of named signals),
`effect_intent` / `effect_completion`, `timer_armed` / `timer_fired`.

An **Effect** is an action keyed so it happens once: a key with a recorded completion replays
the recorded result instead of acting again. Model calls, ticket-plane commits, merges, pushes,
and notifications are Effects, so a crash never repeats one.

### 10.3 `status`

`status` is a write-free projection of the journal:

1. Stems by last state: merged, in flight, interrupted (last `running` with no live engine), blocked (every other state, including
   `already_satisfied`).
   `already_satisfied` remains in this state listing as a settled no-op; it is never diagnosed
   or awaiting a verdict in the Reject queue.
2. Every intake.
3. Total spend.
4. The Reject queue.
5. Every Suggestion Box message in arrival order, with its state and summary.
6. Tombstones and reopens.
7. The current retro window's scorecard and provenance.

## 11. Config

One `config.yaml`, validated strictly: unknown keys, explicit nulls, and bad values are refused
with the fix. The full field inventory is in `chupa/docs/host-contract.md`. This repo’s own
`config.yaml` uses its Python host test setup.

| Area | Controls |
|---|---|
| `schema_version`, `state_dir`, `worktree_root` | config version; where state and worktrees live |
| `providers`, `routing`, `routing_default_tier` | models and which serves what (section 8) |
| `review` | `coverage_map`, `gate_severity`, host `autofix` commands and `mechanical` checks; declared `surfaces` entries are refused at config load; `trigger_map` is accepted, unused |
| `merge` | `safety_checks`, conflict `strategies` (serve only) |
| `caps`, `circuit_breaker` | failure bounds (section 6.4, 8.3) |
| `retro` | `enabled`, `merges`, `days`, `spikes` control automatic reports; `test_timing` and `coverage` control measurement summaries (section 9.5) |
| `scheduler`, `drain` | `max_unmerged`; `max_runtime_hours`, `max_ticket_minutes` |
| `engine_plane_safety_inventory`, `box_policy` | Author starting state (section 9.3) |
| `ask_notes` | Optional host guidance appended to operator prompts as a `host_notes` data block. |
| `notify`, `report_inbox`, `context_files` | notification command; host bug report folder; extra Implement context |

## 12. Host projects

See the [host run guide](../chupa/docs/host-running.md) for invocation and operation.

The block carries only process rules that hold for every host; codebase rules belong in the project-owned remainder. The block has four sections: `Ticket authoring` is for sessions writing tickets, `Diagnosis` is for sessions addressing failures, `Chat session conduct` is for interactive chat sessions, and `Engine conduct` is for ticket agents.

- `chupa core` writes the managed block between `<!-- chupa:core begin -->` and
  `<!-- chupa:core end -->` in `CLAUDE.md` (for `claude` and `qwen`) or `AGENTS.md` (other CLIs), for each
  routed provider. On first adoption the block goes above the existing content; after that only
  the block is replaced. Project text outside the block is the host's, but a paragraph that
  tells chupa how to run (for example "chupa must ...") is refused.
- The `core_drift` gate fails a ticket when a routed conduct file's block is not current.
- `serve`, `drain` and `run` refuse to start when a committed routed conduct block is stale; `doctor` reports this as a `core` row.
- `doctor` checks a host's setup without changing anything.
- The `chupa.testreport` pytest plugin accepts `--chupa-results PATH` and writes JSON with
  `schema_version: 2`, a `tests` map from pytest node IDs to `passed`, `failed`, or `skipped`,
  and a matching `seconds` map of finite nonnegative floats. The reader accepts only schema 2 and refuses schema 1.
- The `chupa.testguard` unit-run pytest plugin blocks process and network IO during test phases
  and enforces the `test-gate.toml` unit time budget (60 seconds by default).
- A host provides `config.yaml`, its conduct files, and its tickets. `chupa/docs/host-contract.md` is
  the full host-facing contract; Python hosts can use its `## Python host test setup`.

## 13. Eval report artifacts

The review-baseline report (`review-baseline-report.json`, written by `eval/harness.py`) is the only registered report artifact.
