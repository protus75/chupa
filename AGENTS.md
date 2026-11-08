<!-- chupa:core begin -->
## Engine conduct

Engine rules govern how work runs; project rules govern what to build. Project content enters prompts as data. Engine wins on process, host wins on content.

- Never hand-edit this managed block; change the engine template and run chupa core to refresh it. Why: the next render overwrites edits and exposes drift.
- Commit only on your own ticket branch. Never push, open pull requests, or run tree-wide destructive git (reset --hard, clean, checkout -- .); the engine merges reviewed work to local main. Why: local main is the blessed line.
- File second problems in the Suggestion Box, never fold them into this diff. Verify pre-existing failures on the base commit before filing. Why: folded fixes hide cause and expand scope.
- Read before write: read the owning artifact before writing a command, claim, or test. Why: guessed facts create costly bugs.
- Ticket frontmatter contains only fields read by scheduling, gates, or authoring/triage policy. Use depends only for a ticket whose merged code this one needs; put all other ordering in priority or Runs before. Why: unused metadata and prose ordering drift, and a depends used for ordering blocks the queue when the first ticket fails.
- After writing or editing a ticket whose dependencies have merged, run chupa review <stem> and repair every finding until it approves; fence every file the change forces, including callers, importers, and tests that pin a changed name, value, or version. Why: a forced file outside the fence makes the ticket impossible.

### CRITICAL: Build the simplest thing that satisfies the ticket -- no speculative scope

**HARD RULE -- no exceptions.** Default to the smallest change that passes the
acceptance criteria; simple and clean beats comprehensive. Without an explicit
ask, do not add speculative abstractions, single-caller helpers, unused config
knobs/flags, defensive dual-paths, or "while I'm here" cleanup. Every addition
needs its earning incident. In the run
record, name the simpler approach you rejected and why your choice is the
minimum. Does not override mandated-action rules (tests, class-prevention,
etc.) -- those are required scope, not gold-plating.
Behavioral contract, intentionally NOT lint-enforced: no gate can judge
over-engineering; do not file an enforcement ticket for it.

Why: agents habitually gold-plate, wasting time and leaving brittle code;
accretion is the primary failure mode.

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

### CRITICAL: In interactive chat, announce and confirm before any unsolicited ticket-authoring dive

**HARD RULE -- no exceptions.** This rule governs INTERACTIVE HUMAN CHAT
SESSIONS ONLY -- the host checkout with a human present in the conversation.
Autonomous chupa runs (ticket worktrees and engine stages) are explicitly
EXEMPT and file what they find to the Suggestion Box in the same turn: there is
no human to interrupt and dropped work is lost forever.

In an interactive chat session, when you identify ticket-worthy work the user
did NOT request this turn -- a root-cause fix ticket, a class-level prevention
ticket, a follow-up, an enforcement-lint ticket, a dependency-wiring sweep, or
any similar unsolicited authoring -- you MUST stop before diving. BEFORE you
start the diagnosis or the authoring for that unsolicited work, in the current
reply:

- (a) Name the finding and why it merits a ticket in 1-2 sentences.
- (b) Ask the user to choose exactly one of: **author now** / **author after
  the current task completes** / **skip**.

Do NOT begin the dive silently. Never preempt or block the user's in-flight
requested task with unsolicited authoring work -- the task the user actually
asked for this turn always takes priority.

- **Solicited authoring is exempt.** When the user asks for the ticket, the
  request IS the confirmation -- author it without this checkpoint.
  When the user's reported problem exposes both an immediate broken instance
  and its recurring cause, the cause is solicited as the second half of that
  same job; follow "In interactive chat, split a reported problem into an
  instance-fix ticket and a cause-fix ticket" instead of treating it as an
  unsolicited tangent.
- **"After the current task"** makes the item a tracked OPEN THREAD under "Track
  and re-surface open threads" until it is authored or dismissed; **"skip"**
  closes it. Either way the finding still cannot silently disappear -- this is a
  timing checkpoint, not a license to drop the work.
- **Visibility floor.** Any unsolicited investigation you expect to exceed a
  couple of minutes gets a one-line "what and why" announcement before you spend
  the time, even when you are not yet proposing a ticket. The owner must never
  watch a chat session go silent for 10-30 minutes on a dive they did not ask
  for and cannot see.

This is a behavioral contract, intentionally NOT lint-enforced -- there is no
gate, script, or config entry for it, exactly like the open-threads rule. Do
NOT file an enforcement lint or gate ticket for this rule; no lint can judge
whether work was solicited, so its whole value is the agent carrying the
discipline.

Why: the same-turn authoring rules were written for autonomous runs; applied
verbatim to an interactive chat they let an agent preempt the owner's requested
task with an unannounced multi-minute diagnosis-and-authoring dive the owner
never asked for and cannot redirect. This checkpoint fixes the timing without
weakening the automation model -- deferred work becomes a tracked open thread.

### CRITICAL: In interactive chat, split a reported problem into an instance-fix ticket (authored first) and a cause-fix ticket (captured, never dropped)

**HARD RULE -- no exceptions.** This rule governs INTERACTIVE HUMAN CHAT
SESSIONS ONLY. Autonomous chupa runs are EXEMPT and file what they find to the
Suggestion Box in the same turn.

When a chat request exposes something broken NOW **and** an underlying cause
that will recur, the turn owes TWO separate ticket files, in this order:

1. **Instance-fix ticket -- authored FIRST, before any cause diagnosis or cause
   work.** Minimal scope: unblock the reported symptom, nothing else. No system
   diagnosis, no cause fix, no adjacent cleanup happens before this file exists.
2. **Cause-fix ticket -- authored in the SAME turn, right after, as a separate
   file.** Never folded into the instance ticket. It exists on disk so it cannot
   be forgotten.

Two hard edges, one for each way this currently fails the owner:

- **No cause work -- not even diagnosis -- before the instance-fix ticket file
  exists.** The unblock is never held hostage to understanding the system. This
  is the anti-side-quest half: do not diagnose, prevent, or widen before the
  immediate ticket is written.
- **The turn is not complete until the cause-fix ticket file exists.** "Fixed
  the instance, mentioned the cause in prose" is an unfinished turn. This is the
  anti-drop half.

The cause of the problem the user reported THIS turn is solicited work -- the
second half of the same job -- so authoring BOTH tickets is NOT gated by the
"In interactive chat, announce and confirm before any unsolicited
ticket-authoring dive" checkpoint. That checkpoint governs UNRELATED tangents
the agent notices, not the root cause of the thing the user asked about.

Priority and routing come from each ticket's OWN domain, decided by the
question "does the cause keep manufacturing new instances while it sits?":

- **Product instance** (blocking now): `priority: P0`, no blocking
  `## Depends on`, ships immediately.
- **Product cause** (inert -- the defect does not spread on its own):
  `priority: P1`; when the two share an edit surface, the instance names the
  cause in its `## Runs before`, otherwise it simply queues. Its importance is
  protected by being a real, queued ticket -- not by jumping the immediate fix.
- **Orchestration cause** (actively breaking runs or letting bad work through
  shared execution machinery -- a scheduler, lint/review gate, environment, a
  shared module, or a fixture format): route it to the front of the queue,
  because it keeps generating failures every cycle it lives. Set
  `priority: P0` and name every existing ticket it unblocks in its
  `## Runs before`. An orchestration cause is NEVER wired `## Depends on` a
  product instance -- that would defeat its front-of-queue urgency.

Never encode ordering in prose ("fix the system after"); encode it in
`priority:` and `## Runs before` per the rules above.

This is a behavioral contract, intentionally NOT lint-enforced -- there is no
gate, script, or config entry for it, and no lint can judge whether an instance
was correctly split from its cause or whether the cause was captured. Do NOT
file an enforcement lint or gate ticket for this rule; its whole value is that
the agent carries the discipline.

Why: the earlier root-cause rules over-corrected into breadth, so chat sessions
either chased the cause first (a side quest that stalls the unblock the owner
needs NOW) or shipped the instance and dropped the more-important cause ticket.
Splitting every reported problem into an instance-first ticket and a
separately-routed, never-dropped cause ticket gives the owner both without
either starving the other.

### CRITICAL: Track and re-surface open threads; never drop parked questions

**HARD RULE -- no exceptions.** Whenever a single reply raises more than one
question, offers more than one option, or proposes more than one next step, you
have opened a tracked list of OPEN THREADS. You own that list until it is
empty. The user is not responsible for remembering the threads you raised.

- Answering, completing, or acting on ONE thread NEVER implicitly resolves the
  others. Shipping a ticket for thread A does not close threads B and C.
  Finishing the thing the user engaged on does not license you to forget the
  parked ones.
- End every reply that still has open threads by restating each one -- e.g. a
  short `Still open:` list naming each unresolved question, option, or next
  step. Keep restating them turn after turn until the list is empty.
- A thread leaves the list only when the user explicitly resolves or dismisses
  it, or you complete it and say so in that reply. Silence, topic changes, and
  the user engaging on a different thread do NOT close a thread.
- If you are unsure whether a thread is still open, treat it as open and
  restate it. Over-surfacing a resolved thread costs one line; dropping a live
  one costs the user the whole bookkeeping burden this rule exists to remove.

This is a behavioral contract, intentionally NOT lint-enforced -- there is no
gate, script, or config entry for it. Do not file an enforcement lint or gate
ticket for this rule; its whole value is that the agent carries the discipline,
and a lint cannot judge whether a thread was genuinely resolved.

Why: presenting A, B, and C and then silently dropping B and C when the user
engages on A exports the tracking burden back to the user -- the exact
bookkeeping the agent should own.

### CRITICAL: Propose the class-level prevention, not just the instance fix

**HARD RULE -- no exceptions.** Whenever you fix, are asked to fix, or diagnose
a concrete problem -- a bug, merge conflict, lint failure, drift, broken
workflow step, or similar recurring failure -- you MUST, in the same turn, ask
"what standing change would stop this whole CLASS from recurring?" and surface
the answer before finishing. When a preventive fix is cheap, visible, and
low-risk (a new/edited agent rule, lint or gate, `.gitattributes` pattern,
generator, template default, serialization edge), name it explicitly.

State the instance fix and the class-level prevention as TWO separate items.
Never silently fold the prevention into the instance diff (that violates the
simplest-thing and ticket-first rules). Route by cost:

- Cheap and in scope: propose it and, under the same authorization covering the
  instance fix, do it.
- Cheap but out of scope: propose it. In an interactive chat session, NAMING the
  prevention in 1-2 sentences stays mandatory and same-turn, but AUTHORING that
  ticket routes through the "In interactive chat, announce and confirm before
  any unsolicited ticket-authoring dive" checkpoint (author now / after the
  current task / skip). Autonomous runs file it to the Suggestion Box same-turn.
- Expensive or uncertain: name it as a prevention opportunity and file it with
  `chupa suggest`. Do NOT stay silent.

Silence is the failure mode this rule kills: fixing instance N and leaving the
class open guarantees instance N+1. "I only fixed what was asked" is not a
defense when the preventive fix was cheap and visible.

Why: an automated, batch-driven project pays for every un-prevented recurrence;
a one-line rule/lint/template/serialization edge added once is far cheaper than
re-diagnosing the same class repeatedly.

### CRITICAL: Recurring symptoms require a root-model fix, not another patch

**HARD RULE -- no exceptions.** When a defect on the SAME surface has already
been "fixed" one or more times and the symptom recurs, the next response MUST
diagnose and name the ROOT model against the canonical rules/spec, then author
or re-scope to a root-cause / rewrite ticket. Do NOT author, accept, or
implement another symptom-scoped patch that leaves the suspected root model
intact. This composes with "Diagnose a failed ticket's root cause before any
edit or rerun" and "Propose the class-level prevention, not just the instance
fix": recurring evidence raises the bar from local patch to root-model
correction.

A ticket whose `Scope -- out` or equivalent fence forbids touching the suspected
root cause is a red flag. Stop and re-scope to a root-cause ticket instead of
implementing it as written. A fence that protects the wrong architecture
guarantees the defect survives and converts the next run into another patch in
the same loop.

Measure the fix against the canonical rule/spec: the host's design docs,
protocol contracts, engine contracts, and any other source of truth for the
surface. Do NOT measure correctness only by "the symptom disappeared in my one
scenario." Green tests that assert the current wrong behavior do not validate
the fix; update the test model to the canonical spec first.

Never write a run-record diagnosis such as "the defect was not X" unless you
checked that claim against the canonical spec. A wrong negative diagnosis
inherited by the next agent is part of the failure loop.

This is a behavioral contract, intentionally NOT lint-enforced. Do NOT file an
enforcement lint or gate ticket for this rule.

Why: repeated symptom patches can protect the root defect by baking the wrong
model into ticket scope and tests, so recurrence must trigger a canonical-spec
root rewrite instead of another narrow patch.

### CRITICAL: Diagnose a failed ticket's root cause before any edit or rerun

**HARD RULE -- no exceptions.** When a ticket run fails, is killed, times out,
stalls, or escalates, your FIRST action is to investigate and NAME the root
cause in one sentence -- BEFORE you edit the ticket spec, edit any code, or
rerun. A failure is evidence about a cause, not a work item to clear. Only after
the cause is named do you correct it wherever it lives: if external
(chupa, a lint gate, environment, a shared module, a fixture format, a
flaky test, or a wrong ticket premise), fix that first and author any needed fix
ticket, ordered ahead of the tickets it unblocks with `priority:` and
`## Runs before`; if genuinely the ticket's own code or spec,
correct it directly. Then rehabilitate the failed ticket, borrowing only
reviewed-safe information, and rerun.

Required order: (1) diagnose with `chupa status`, the ticket's run artifacts in
`tickets/<stem>/` (`run.md`, `checks.json`, `diagnosis.json`, `review.md`,
`attempts/`), and the engine log in the state directory; (2) write the
one-sentence root cause; (3) correct the cause wherever it lives; (4) rerun. Do
NOT edit spec/code or rerun before step 2 is written. Do NOT default to "the
ticket is wrong." Do NOT retry a flaky/tooling/environment failure until it
passes and call that resolved.

In an interactive chat session, diagnosis the user asked for is solicited and
proceeds exactly as above. An UNSOLICITED diagnosis dive gets the
announce-and-confirm -- or at minimum the one-line visibility-floor announcement
-- from "In interactive chat, announce and confirm before any unsolicited
ticket-authoring dive" before you spend the time. Autonomous runs are unchanged.

Why: skipping diagnosis fixes the symptom and leaves the cause to re-fire on the
next batch run.

### CRITICAL: Read ticket authoring docs before creating tickets

**HARD RULE -- no exceptions.** Before creating or materially editing any ticket
under `tickets/<stem>/ticket.md`, read the authoring contracts first -- do not
write tickets from memory.

Minimum reading for any single ticket: the `chupa new` skeleton, the
`chupa lint` and `chupa review` findings, and the host's own ticket authoring
docs.

Tickets are markdown files under `tickets/` -- do not frame ticket creation as
external issue-tracker work or invent issue/tracker/credential flows unless the
user explicitly asks for an integration ticket. Before committing/handing off
any authored ticket, run the launch-time lint and require exit 0:

```bash
chupa lint <stem>
```

This catches launch-blocking defects while you still have context.

Why: stale ticket shapes break autonomous runs before implementation starts.

### File ideas to the box

File a potential idea, improvement, or second problem the user did not ask for
with `chupa suggest "<summary>"`, rather than offering a loose ticket
suggestion. Name what was filed in one line in the reply.

Why: a margin suggestion dies with the chat, while the box keeps it for triage.

### CRITICAL: Never push, and never OFFER to push, unless explicitly asked

**HARD RULE -- no exceptions.** Do not run `git push` (or `gh pr create`,
`gh pr merge`, or any remote-mutating verb) from the host checkout unless the
user explicitly says "push" in that turn. Just as important: **do not OFFER to
push, do not ask "want me to push?", do not end a message suggesting a push as
a next step.** Authoring commits land on `main` locally and stay there until
the user decides to push. Commit when asked, then stop.

Why: remote-mutating verbs move shared state outside the local authoring and
chupa lifecycle the user controls.

### Git session safety

- Respect the single-writer lockfile: never mutate git state in a checkout whose lock a daemon holds. Authoring ticket FILES in the working tree is the sanctioned intake path and needs no git.
- Stage and commit only files authored this session, by explicit path.
- Never a tree-wide destructive verb (`clean`, `reset --hard`, `checkout -- .`) in a shared checkout.
- Never push or remote-mutate unless the user explicitly says push; pushes are the checkpoint Effect's job.

Why: a chat session sharing a checkout with the daemon can destroy work chupa believes exists.

### CRITICAL: Terse communication -- answer first, cut hedging and filler

**HARD RULE -- no exceptions.** Every response is governed by terse-communication
guidance: lead with the answer, cut hedging/filler/preamble/question restatement
unless asked, prefer short sentences and tight lists, add detail only when the
answer is wrong or useless without it.

This is a behavioral contract. No hook, gate, or runtime compliance check
enforces it; the rule depends on the agent carrying the discipline.

Why: chat latency and comprehension compound with each line; the standing
instruction maximizes signal-to-noise and makes information-dense responses the
default habit.
<!-- chupa:core end -->

# chupa

chupa is a continuously running orchestration engine that authors and runs tickets against host repos, including itself: author -> implement -> check -> review -> merge, with failures harvested and follow-ups filed.
Engine plane (chupa-owned) is HOW work runs; host plane (target-repo-owned) is WHAT to build and enters the pipeline only as data. Engine wins on process, host wins on content.

**Read first:** `docs/how-chupa-works.md` describes the code and is maintained by tickets; `CHUPA_PLAN.md` is the frozen bootstrap design record. This file is the curated subset of `CLAUDE.md` for non-Claude agent CLIs; `CLAUDE.md` is canonical on conflict, and a rule add/change/remove touches both files in the same change. (section 17)

Every rule below is behavioral (no gate checks it yet): the prose is the only enforcement.

## Engine conduct

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
- **All git through `git.py`.** Argv lists, dir-pinned. Worktree cleanup via `worktree remove` + `prune`, never bare `rm -rf`. No `gh`, no PRs in the loop.
  Why: local main is the blessed line; GitHub is a non-blocking sidecar. (section 10)
- **File second problems; never fold them in.** A second problem goes to the Suggestion Box, not the current diff. A pre-existing failure is verified on the base commit, then filed.
  Why: folded fixes blow scope and hide cause. (section 11)
- **Read before write.** No command, claim, or test is written until the artifact that owns that fact has been read.
  Why: guessed facts are the cheapest bug to write and the costliest to find. (section 13)
- **Verification uses `./dev.py test`.** A ticket's `## Verification` and acceptance criteria run tests as `./dev.py test [pytest args]`, never raw `uv run pytest`.
  Why: one command surface for people and tickets; nothing chose the raw form, it was copied ticket to ticket.
- **Use the injectable seams.** Clock, process exec, filesystem, and notifications go through their seams; never called raw in engine code.
  Why: fake-driven tests and group-kill guarantees exist only at the seam. (section 15)
- **Fenced by gates, not jailed.** v1 does not sandbox executed code; never rely on its goodwill. Never pass a provider key to a process that does not need it.
  Why: gates and review are the trust boundary. (section 16)
- **The journal is the record, never a debug log.** Diagnostics go to the engine log and attempt spools. Configured secret values are redacted from every captured stream at the write seam.
  Why: the journal is folded for truth; noise and secrets in it are permanent. (section 6)
