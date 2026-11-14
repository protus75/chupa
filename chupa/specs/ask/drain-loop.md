/loop You are the supervising session for the chupa drain in this repo. Goal: run the queue until it is empty or every remaining ticket is blocked on a human, making only the fixes the supervising-session rule in the conduct file's chupa:core block allows. Use only ./dev.py verbs.

Each tick:

1. Observe. Run `./dev.py status` and tail ${state_dir}/drain.out. Work out whether a drain is running. A held writer lock, or a running stem in status, means yes.

2. If a drain is running and making progress, do nothing. Wake again in about 20 minutes. If it looks stalled (no new journal or drain.out output for 30+ minutes while a stem is running), first name the root cause in one sentence from status, tickets/<stem>/ (run.md, checks.json, diagnosis.json, review.md, attempts/), and ${state_dir}/engine.log. Then run `./dev.py stop`, or `./dev.py kill` if stop does not land.

3. If no drain is running, triage every non-merged stem:
   - Eligible work remains (intake, confirmed with cap budget left, abandoned, or reofferable): go to step 4.
   - Fixable by a supervisor: lint or format errors (`./dev.py lint <stem>`), a file missing from `## Scope fence` or `## Context`, a stale path, or a simple wording fix. Before editing, name the root cause in one sentence from that stem's artifacts. Edit only tickets/<stem>/ticket.md. Run `./dev.py lint <stem>` until it exits 0. Commit that one file by explicit path. A requisition-stage premise park is released by that committed edit, with no confirm.
   - Needs a human. Leave these alone and list them: anything in the Reject queue awaiting the operator (spent cap, reject or abandon-human verdict, ticket_changed, premise_bounce cap spent), rejected stems, dependents of rejected stems, drafts awaiting confirm, any fix that would change the goal or scope, and any ticket the engine authored (Author or Rework).

4. If any stem is eligible, start a drain with `./dev.py drain`. Never start one while the lock is held.

5. Done check: no drain is running, no stem is eligible, and you made no fix this tick. Then stop the loop and print the final report.

Hard limits. These are owner verdicts; never do them:
- Never run `confirm` or `reject`, and never pass `--yes` or `--extension`.
- Never re-offer a stem whose caps are spent. Editing a ticket never resets its caps; only an operator confirm does.
- Never edit ticket.md while that stem is running. A mid-run edit causes a ticket_changed hold that only confirm releases. Stop the drain first, or wait for that stem to finish.
- Never edit code, docs, conduct files, specs, or config. Never edit or rewrite a ticket's goal, acceptance criteria, or scope. Never author new tickets.
- Never push, run a tree-wide destructive git verb, delete chupa.lock, or rerun a flaky failure until it passes.
- Do not fix an engine, gate, environment, or fixture cause. Record it and `./dev.py suggest "<summary>"` it.
- For each fix, name the class-prevention change (lint, gate, template default) and `./dev.py suggest` it. Do not build it.

Final report, terse:
- Merged this session.
- Fixes made: stem, root cause, edit, commit hash.
- Needs human, one line each: stem, state or reason, cap usage, and the exact verb or edit that would release it.
- Suggestions filed.
- Still open: list.
