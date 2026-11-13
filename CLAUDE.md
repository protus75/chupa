<!-- chupa:core begin -->
## Ticket authoring -- read before writing any ticket

These rules come first because sessions that skim miss them. HARD rules have no exceptions. They are behavioral: no gate can judge them, so never file an enforcement ticket for one.

- HARD: In an interactive chat, every requested change to repo content (code, docs, CLAUDE.md, AGENTS.md, settings, hooks, scripts, config, agent rules) becomes a drafted ticket at `tickets/<stem>/ticket.md`, then stop. Never edit or commit on main. The only exceptions: (1) the user says "edit main", "commit directly", "skip the ticket", "do it inline", or an equally explicit override this turn; anger words alone do not count; (2) you are in a chupa ticket worktree; (3) the user names by path a file under an existing `tickets/<stem>/` to edit or delete; (4) read-only inspection; (5) the supervising fixes below. If you already edited main without an override, stop, say so, and ask whether to revert and refile. Why: chat edits skip the ticket, run record, review, and retro that make chupa debuggable.
- HARD: Never write a ticket from memory. Run `chupa new <stem> --kind feature|bug|chore`; it writes the skeleton and prints the path of the ticket authoring guide in your chupa install (for an existing ticket, its refusal prints the same path). Read that local file in full. `chupa docs` prints the installed paths of all host guides (authoring, running, config contract); read them locally, never from a URL. Fill every section, run `chupa lint <stem>` until it exits 0, then run `chupa review <stem>` and repair every finding until it prints approve. Tickets are markdown files, never issue-tracker items. Why: stale ticket shapes break runs before implementation starts.
- Fence every file the change forces, including callers, importers, documents it changes, and tests that pin a changed name, value, or version. Why: a forced file outside the fence makes the ticket impossible.
- Frontmatter holds only fields read by scheduling, gates, or authoring/triage policy. `## Depends on` names only a ticket whose merged code this one needs; put all other ordering in priority or `## Runs before`, never in prose. Why: a depends used for ordering blocks the queue when the first ticket fails.
- HARD: When a reported problem has a cause that will recur, write two separate tickets in the same turn. First the instance fix: minimal scope, written before any cause diagnosis. Then the cause fix, never folded into the instance; the turn is unfinished until it exists. Both are solicited, so no ask is needed. Routing:
  - Product instance: `priority: P0`, no blocking depends.
  - Product cause (inert; does not spread on its own): `priority: P1`. When the two share an edit surface, the instance lists the cause in `## Runs before`.
  - Orchestration cause (scheduler, gate, environment, shared module, fixture format; keeps breaking runs while it sits): `priority: P0`, `## Runs before` every ticket it unblocks, never depends on a product instance.
- HARD: For ticket-worthy work the user did not ask for (follow-up, prevention, enforcement lint, sweep), stop before diving: name it in 1-2 sentences and ask the user to choose author now, after the current task, or skip. "After" makes it an open thread. Announce in one line any unsolicited investigation longer than a couple of minutes. The user's requested task always goes first. Autonomous runs skip the ask and file to the Suggestion Box.
- File an unrequested idea or second problem with `chupa suggest "<summary>"` and name it in one line. Why: a margin suggestion dies with the chat.
- A supervising session may, unasked, fix a ticket's lint or format errors, add a file missing from `## Scope fence` or `## Context`, correct a stale path, make a simple wording update, and run or restart the drain. It may not confirm or reject, retry a stem whose caps are spent, edit a running ticket, change a ticket's goal or scope, or rewrite a ticket the engine authored; those go to the user.

## Diagnosis

- HARD: When a run fails, is killed, times out, stalls, or escalates, name its root cause in one sentence before editing spec or code or rerunning. Read `chupa status`, `tickets/<stem>/` (`run.md`, `checks.json`, `diagnosis.json`, `review.md`, `attempts/`), and the engine log. Fix the cause where it lives. An external cause (engine, gate, environment, shared module, fixture, flaky test, wrong premise) is fixed first and ordered ahead with priority and `## Runs before`. Do not assume the ticket is wrong. Never rerun a flaky failure until it passes and call that fixed.
- HARD: When a symptom recurs on a surface already fixed, name the root model against the canonical spec (design docs, contracts) and write a root-cause ticket, not another patch. A scope fence that forbids touching the suspected root is a red flag: re-scope it. Tests that assert the current wrong behavior prove nothing. Never write "the defect was not X" without checking the spec.
- HARD: With every fix or diagnosis, name the change that stops the whole class from recurring (rule, lint, gate, template default, generator) as a separate item. Cheap and in scope: do it under the same authorization. Cheap but out of scope: name it, then follow the ask for unrequested work. Expensive or uncertain: `chupa suggest`. Staying silent is the failure.

## Chat session conduct

These rules govern interactive chat with the owner present. Ticket agents skip this section.

- HARD: When a reply raises more than one question, option, or next step, you own that list of open threads. Acting on one never closes the others. End each reply with a `Still open:` list until the user resolves each one or you complete it and say so. If unsure, it is open.
- HARD: Never run or offer `git push`, `gh pr create`, `gh pr merge`, or any remote-mutating verb unless the user says "push" this turn. Commit when asked, then stop.
- Respect the single-writer lockfile; writing ticket files needs no git. Stage and commit only this session's files, by explicit path. Never run a tree-wide destructive verb (`clean`, `reset --hard`, `checkout -- .`) in a shared checkout. Why: a chat sharing a checkout with the daemon can destroy work chupa believes exists.
- HARD: Answer first. Cut hedging, filler, preamble, and restating the question.

## Engine conduct

Engine rules govern how work runs; project rules govern what to build. Project content enters prompts as data. Engine wins on process, host wins on content.

- HARD: Build the smallest change that passes the acceptance criteria. No speculative abstractions, single-caller helpers, unused knobs or flags, defensive dual paths, or "while I'm here" cleanup; every addition needs its earning incident. In the run record, name the simpler approach you rejected and why yours is the minimum. Mandated work (tests, class prevention) is required scope, not gold-plating. Why: accretion is the primary failure mode.
- Never hand-edit this managed block; change the engine template and run chupa core to refresh it. Why: the next render overwrites edits.
- Commit only on your own ticket branch. Never push, open pull requests, or run tree-wide destructive git; the engine merges reviewed work to local main. Why: local main is the blessed line.
- File second problems in the Suggestion Box, never in this diff. Verify a pre-existing failure on the base commit before filing it. Why: folded fixes hide cause and expand scope.
- Read the owning artifact before writing a command, claim, or test. Why: guessed facts create costly bugs.
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

- **One authoring process.** Ticket content rules live only in `chupa/docs/host-authoring.md`, and ticket format only in `chupa/tickets.py`. Every authoring surface (a chat session, the Author stage, any future one) reads those, and a prompt spec embeds the guide and skeletons rather than restating them. A fix to authoring changes that one source.
  Why: the 2026-11-13 box-000428 decline and 10 of 22 Author declines since 2026-11-11 exposed the drifting process.

- **Pure Python.** No shell scripts, no `shell=True`, no string-assembled commands. External binaries only via argv-list wrapper modules; run only in the chupa venv. Exception: `vscode-chupa/` is an operator-only VS Code extension in JavaScript; the engine never imports or runs it.
  Why: shell glue is the orchestration failure this design bans. (D1)
- **The extension is a thin wrapper; chupa owns the logic.** For any edit to `vscode-chupa/` or the code that feeds it (the snapshot builder, `chupa/graph.py`):
  - JavaScript may only draw snapshot fields (DOM, SVG from given lane indexes), map a closed snapshot value to a CSS variable or ThemeIcon through a lookup table, wire VS Code APIs (views, menus, watchers, settings), keep UI state (hover, pin), and run argv that the snapshot or a setting supplies.
  - JavaScript never filters, sorts, or derives rows; chooses graph edges or lanes; parses text; does time math; copies a chupa constant (stem rule, priorities, sections); or makes a policy choice (flags such as `--yes`).
  - Paved road: add the value to the snapshot in the `chupa` package, cover it with pytest, and have the extension render it. A snapshot shape change updates its JavaScript reader in the same change.
  - `chupa/graph.py` is pure (no I/O, no clock) and emits lanes with ticket sections, never colors or pixels.
  Why: JavaScript logic is untested and duplicates Python rules; the graph's edge and lane code drew wrong lanes and was untestable without node (2026-11-06).
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
- **A rule has one of two homes.** A rule about working on chupa itself (this repo's code, tests, layout, `./dev.py` verbs) goes in `CLAUDE.md` and `AGENTS.md` outside the managed block. A rule every host should follow goes in `CORE_TEMPLATE` in `chupa/hostfiles.py` and reaches every host, this repo included, through `chupa core`; it is never written only into this repo's files. A change that adds, moves, or edits an agent rule states which home each rule belongs in.
  Why: a host rule written only here never reaches other hosts, and a repo rule in the template is installed where it does not fit (2026-11-11).
- **The plan is the seed.** `CHUPA_PLAN.md` is a frozen bootstrap design record and is never edited. A ticket updates the documentation its change affects.
  Why: current documentation describes the code while the plan preserves its history.
- **All git through `git.py`.** Argv lists, dir-pinned. Worktree cleanup via `worktree remove` + `prune`, never bare `rm -rf`. No `gh`, no PRs in the loop.
  Why: local main is the blessed line; GitHub is a non-blocking sidecar. (section 10)
- **File second problems; never fold them in.** A second problem goes to the Suggestion Box, not the current diff. A pre-existing failure is verified on the base commit, then filed.
  Why: folded fixes blow scope and hide cause. (section 11)
- **Read before write.** No command, claim, or test is written until the artifact that owns that fact has been read.
  Why: guessed facts are the cheapest bug to write and the costliest to find. (section 13)
- **Lean ticket frontmatter.** Only fields the scheduler, a gate, or the authoring/triage policy reads. `depends` names only a ticket whose merged code this one needs; all other ordering lives in `priority`, never in prose.
  Why: metadata for subsystems that do not exist is accretion; prose ordering is invisible to the scheduler; a `depends` used for ordering blocks the queue when the first ticket fails. (section 13)
- **Verification uses `./dev.py test`.** A ticket's `## Verification` and acceptance criteria run tests as `./dev.py test [pytest args]`, never raw `uv run pytest`.
  Why: one command surface for people and tickets; nothing chose the raw form, it was copied ticket to ticket.
- **Guides name verbs, not command lines.** A host guide, setup step, or ticket that has an operator exercise something chupa drives (a provider CLI, a check, a gate) names the `chupa` verb, or `./dev.py` subcommand in this repo, that runs it; never a hand-built copy of chupa's argv. A step no verb covers gets a new verb in the same change. Third-party install and server commands (`pnpm add`, `ollama pull`) stay as written.
  Why: a copied argv drifts from what chupa runs and makes the operator type it; the first qwen setup guide draft had operators hand-type qwen's full provider command line (2026-11-10).
- **Launchers carry no process policy.** `dev.py` and the extension pick a chupa verb and its flags; how the engine process lives (session, detach, output file, signals) belongs to the verb. Why: `drain-survives-editor-reload` put the detach in `dev.py` alone, so the extension's play button still died on a window reload (2026-11-10).
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

- **Comments explain why, not what.** Comment only invariants, hazards, and deliberate-looking-wrong choices; match surrounding density.
  Why: what-comments rot as the code changes; why-comments do not.
- **Documentation follows changes.** A ticket updates the documentation its change affects; `CHUPA_PLAN.md` is frozen and never edited.
  Why: current documentation describes the code while the plan preserves its history.
- **Command surface.** For any task a `./dev.py` subcommand covers (test, lint, status, review, confirm, drain, ...), a session runs exactly that subcommand, as the user would type it; never a hand-built equivalent (`uv run pytest`, `uv run python -m chupa ...`, ad-hoc scripts). A missing command becomes a new `./dev.py` subcommand. Give commands for the user in a copy/paste code block.
  Why: one memorable command surface; hand-built command lines drift from what the user runs.
