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

- HARD: A fix that belongs in chupa (a prompt spec, gate, ticket format, host guide, or this block) is never copied or patched into host files. Report it for the owner to carry to chupa, then stop. Why: a host copy competes with chupa's rule, reaches no other host, and goes stale on upgrade.

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

# Score game

Host content lives in app.py and settings.json.
