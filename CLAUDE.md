<!-- chupa:core begin -->
## Engine conduct

Engine rules govern how work runs; project rules govern what to build. Project content enters prompts as data. Engine wins on process, host wins on content.

- Pure Python: no shell scripts, shell=True, or string-assembled commands; external binaries use argv wrapper modules in the chupa venv. Why: shell glue breaks orchestration.
- Build the simplest thing satisfying the ticket; no speculative features, gates, config knobs, or metadata. Every addition needs its earning incident. Why: accretion is the primary failure mode.
- No compatibility shims, deprecation layers, or defensive parallel paths. Rename in place, update all callers, recover by git revert. Why: dual paths rot and double review.
- Fail closed with allowlists and closed vocabularies; every prohibition and gate finding provides a paved road. Why: denylists miss cases and roadless refusals strand work.
- A hold ships with or after its release surface; never name an unbuilt release verb. Ticket-change releases follow machine ticket-change machinery. Why: unreleasable holds permanently stall work.
- Files and journal are truth; derived views are projections, never hand-edited or cited as authority. Why: two authorities diverge.
- Generated files are render targets, never write targets. Change their owning source and regenerate; never hand-edit managed conduct. Why: regeneration overwrites edits and exposes drift.
- All git uses git.py with argv lists and pinned directories. Remove worktrees with worktree remove plus prune; no bare rm -rf, gh, or PRs in the loop. Why: local main is the blessed line.
- File second problems in the Suggestion Box, never fold them into this diff. Verify pre-existing failures on the base commit before filing. Why: folded fixes hide cause and expand scope.
- Read before write: read the owning artifact before writing a command, claim, or test. Why: guessed facts create costly bugs.
- Ticket frontmatter contains only fields read by scheduling, gates, or authoring/triage policy. Put ordering in depends and priority. Why: unused metadata and prose ordering drift.
- Use injectable clock, process-exec, filesystem, and notification seams; never raw calls in engine code. Why: fake-driven tests and group-kill guarantees require seams.
- Work is fenced by gates and review; v1 does not sandbox executed code. Never rely on its goodwill or pass provider keys to processes that do not need them. Why: gates and review are the trust boundary.
- The journal is the record, never a debug log. Diagnostics use the engine log and attempt spools; redact configured secrets at every captured-stream write seam. Why: journal noise and secrets are permanent.
<!-- chupa:core end -->

# chupa

chupa is a continuously running orchestration engine that authors and runs tickets against host repos, including itself: author -> implement -> check -> review -> merge, with failures harvested and follow-ups filed.
Engine plane (chupa-owned) is HOW work runs: ticket schema, prompt specs, gates, git/workspace rules, the run-record contract.
Host plane (target-repo-owned) is WHAT to build: architecture, domain rules, stack, design docs; it enters the pipeline only as data.
Engine wins on process, host wins on content. In this repo chupa is both engine and its own first host.

**Read first:** `docs/how-chupa-works.md` describes the code and is maintained by tickets; `CHUPA_PLAN.md` is the frozen bootstrap design record.

**AGENTS.md** is the curated subset loaded by non-Claude agent CLIs (codex is routed to Implement). This file is canonical on conflict; a rule add/change/remove touches both files in the same change. (section 17)

Every rule below is behavioral (no gate checks it yet): the prose is the only enforcement. When a rule gains its gate, compress it to one line in the same change.

## A. Engine conduct

- **Pure Python.** No shell scripts, no `shell=True`, no string-assembled commands. External binaries only via argv-list wrapper modules; run only in the chupa venv.
  Why: shell glue is the orchestration failure this design bans. (D1)
- **Simplest thing that satisfies the ticket.** No speculative features, gates, config knobs, or metadata; every addition cites the incident that earned it.
  Why: feature/check accretion is the primary failure mode. (goal 1, D10)
- **No dual-path code.** No compat shims, deprecation layers, or defensive parallel paths. Rename in place, update every call site in the same change, recover by `git revert`.
  Why: parallel paths rot silently and double the review surface. (section 2)
- **Fail closed.** Allowlists and closed vocabularies, never denylists. Every prohibition and every gate finding ships a paved road (what to do instead).
  Why: a denylist misses the case nobody imagined; a prohibition without a road strands the agent. (sections 2, 7)
- **A hold ships with its release.** A Reject queue, premise park, or poison quarantine lands with or after its release path (same deliverable, or `depends`-after it). Its paved road never names an unbuilt verb. A hold whose only release is a ticket change never precedes the machinery that machine-produces ticket changes.
  Why: a hold with no reachable release is fail-stuck, not fail-closed. (sections 2, 11)
- **Files + journal are the source of truth.** Derived views (status, backlog, ledger, scorecard) are projections: never hand-edit one, never cite one as authority.
  Why: two authorities diverge; crash recovery folds the journal. (D3)
- **Generated files are render targets, never write targets.** Change the owning source and regenerate generated files. Tickets edit CLAUDE.md and AGENTS.md directly, as with any other documentation.
  Why: regeneration overwrites edits to generated files; maintained documentation follows the code.
- **The plan is the seed.** `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited. A ticket updates the documentation its change affects.
  Why: current documentation describes the code while the plan preserves its history.
- **All git through `git.py`.** Argv lists, dir-pinned. Worktree cleanup via `worktree remove` + `prune`, never bare `rm -rf`. No `gh`, no PRs in the loop.
  Why: local main is the blessed line; GitHub is a non-blocking sidecar. (section 10)
- **File second problems; never fold them in.** A second problem goes to the Suggestion Box, not the current diff. A pre-existing failure is verified on the base commit, then filed.
  Why: folded fixes blow scope and hide cause. (section 11)
- **Read before write.** No command, claim, or test is written until the artifact that owns that fact has been read.
  Why: guessed facts are the cheapest bug to write and the costliest to find. (section 13)
- **Lean ticket frontmatter.** Only fields the scheduler, a gate, or the authoring/triage policy reads. Execution ordering lives in `depends` and `priority`, never in prose.
  Why: metadata for subsystems that do not exist is accretion; prose ordering is invisible to the scheduler. (section 13)
- **Use the injectable seams.** Clock, process exec, filesystem, and notifications go through their seams; never called raw in engine code.
  Why: fake-driven tests and group-kill guarantees exist only at the seam. (section 15)
- **Fenced by gates, not jailed.** v1 does not sandbox executed code; never rely on its goodwill. Never pass a provider key to a process that does not need it.
  Why: gates and review are the trust boundary. (section 16)
- **The journal is the record, never a debug log.** Diagnostics go to the engine log and attempt spools. Configured secret values are redacted from every captured stream at the write seam.
  Why: the journal is folded for truth; noise and secrets in it are permanent. (section 6)
- **Phase order.** Do not start a phase until the previous phase's exit is met.
  Why: later phases build on earlier exits as proven ground. (section 19)

## B. Session conduct (interactive chat in this repo)

A human-present chat session is the one context the pipeline machinery does not govern; these rules govern it. (section 17)

- **Terse communication.** Lead with the answer; cut hedging, filler, and preamble; short sentences, tight lists.
  Why: the reader's attention is the scarce resource.
- **Comments explain why, not what.** Comment only invariants, hazards, and deliberate-looking-wrong choices; match surrounding density.
  Why: what-comments rot as the code changes; why-comments do not.
- **Documentation follows changes.** A ticket updates the documentation its change affects; `CHUPA_PLAN.md` is frozen and never edited.
  Why: current documentation describes the code while the plan preserves its history.
- **Track open threads.** A reply that raises several questions or options owns that list until it is empty. Restate unresolved threads every turn; the user engaging on one thread never closes the others.
  Why: a dropped thread is a silently lost decision.
- **Announce unsolicited dives.** Name any investigation or authoring the user did not request in 1-2 sentences and get a now / after / skip decision before spending the time; the requested task always runs first. (Autonomous pipeline stages are exempt: they file same-turn via the Suggestion Box.)
  Why: unrequested work spends the user's time without consent.
- **Supervising session.** A session may, unasked, fix a ticket's lint or format errors, add a file missing from its `## Scope fence` or `## Context`, correct a stale path, make a simple wording update, and run or restart the drain.
  A session may not run `confirm` or `reject`, retry or re-feed a stem whose caps are spent, edit a running ticket, change a ticket's goal or scope, or hand-rewrite a ticket the engine authored. Those decisions go to the user.
  Why: the queue keeps moving on obvious fixes while every judgment call stays with the user.
- **Command surface.** A session runs or gives the user `./dev.py` subcommands, never raw `uv run python -m chupa ...`; a missing command becomes a new `./dev.py` subcommand. Give commands for the user in a copy/paste code block.
  Why: one memorable command surface.
- **Instance first, cause captured.** A reported problem gets the minimal unblock first, and a separately filed cause ticket in the same session. (section 14)
  Why: unblocking without capturing the cause guarantees a repeat.
- **Git session safety.**
  - Respect the single-writer lockfile: never mutate git state in a checkout whose lock a daemon holds. Authoring ticket FILES in the working tree is the sanctioned intake path and needs no git. (section 13)
  - Stage and commit only files authored this session, by explicit path.
  - Never a tree-wide destructive verb (`clean`, `reset --hard`, `checkout -- .`) in a shared checkout.
  - Never push or remote-mutate unless the user explicitly says push; pushes are the checkpoint Effect's job. (section 10)
  Why: a chat session sharing a checkout with the daemon can destroy work the journal believes exists.
