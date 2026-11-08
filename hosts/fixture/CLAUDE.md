<!-- chupa:core begin -->
## Engine conduct

Engine rules govern how work runs; project rules govern what to build. Project content enters prompts as data. Engine wins on process, host wins on content.

- Build the simplest thing satisfying the ticket; no speculative features, gates, config knobs, or metadata. Every addition needs its earning incident. Why: accretion is the primary failure mode.
- Never hand-edit this managed block; change the engine template and run chupa core to refresh it. Why: the next render overwrites edits and exposes drift.
- Commit only on your own ticket branch. Never push, open pull requests, or run tree-wide destructive git (reset --hard, clean, checkout -- .); the engine merges reviewed work to local main. Why: local main is the blessed line.
- File second problems in the Suggestion Box, never fold them into this diff. Verify pre-existing failures on the base commit before filing. Why: folded fixes hide cause and expand scope.
- Read before write: read the owning artifact before writing a command, claim, or test. Why: guessed facts create costly bugs.
- Ticket frontmatter contains only fields read by scheduling, gates, or authoring/triage policy. Use depends only for a ticket whose merged code this one needs; put all other ordering in priority. Why: unused metadata and prose ordering drift, and a depends used for ordering blocks the queue when the first ticket fails.
- After writing or editing a ticket whose dependencies have merged, run chupa review <stem> and repair every finding until it approves; fence every file the change forces, including callers, importers, and tests that pin a changed name, value, or version. Why: a forced file outside the fence makes the ticket impossible.

## Chat session conduct

These rules govern INTERACTIVE CHAT SESSIONS with the owner present. Ticket agents running under
chupa skip this section; a confirmed ticket is the approval for its own scope.

### CRITICAL: Always propose a ticket -- never hand-edit main from chat

**HARD RULE -- no exceptions.** When the user asks for ANY change to repo
content from a chat session -- code, docs, CLAUDE.md, AGENTS.md,
`.claude/settings.json`, hooks, scripts, project config, agent rules, or
anything tracked in git outside the ticket-maintenance carve-out below -- your
default and near-only response is to **draft a ticket file at
`tickets/<stem>/ticket.md`** following `chupa new`, `chupa lint`, and
`chupa review`, and stop. Do not edit or commit directly on `main`.

The only times you may edit `main` directly from chat are:

1. The user explicitly says "edit main", "commit directly", "skip the
   ticket", "do it inline", or equivalently unambiguous override in the
   same turn. Anger words alone do not count.
2. You are inside an active chupa ticket worktree, in which case the ticket
   workflow's own rules apply.
3. In an interactive human chat session in the host checkout, the user
   directs you by explicit path to edit or delete an existing ticket file under
   `tickets/` or any other file in that ticket's `tickets/<stem>/` directory.
   Deleting one of those files on its own is included. This is ticket
   maintenance and does not require drafting a ticket-about-a-ticket first.
4. Read-only inspection (grep, git status, git diff, git log, gh pr view) --
   never a write.
5. Supervising session. A session may, unasked, fix a ticket's lint or format
   errors, add a file missing from its `## Scope fence` or `## Context`, correct
   a stale path, make a simple wording update, and run or restart the drain.
   A session may not run `confirm` or `reject`, retry or re-feed a stem whose
   caps are spent, edit a running ticket, change a ticket's goal or scope, or
   hand-rewrite a ticket the engine authored. Those decisions go to the user.
   Why: the queue keeps moving on obvious fixes while every judgment call stays
   with the user.

If you have already started editing or have edited main without an explicit
override: stop immediately, tell the user you broke this rule, and ask whether
to revert the commit and refile as a ticket.

Why: direct chat edits bypass the ticket, run-record, review, dependency, and
retro artifacts that make chupa debuggable.
<!-- chupa:core end -->

# Score game

Host content lives in app.py and settings.json.
