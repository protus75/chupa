---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/hostfiles.py::CORE_TEMPLATE
- tests/integration/test_hostfiles.py::test_core_template_is_host_neutral
- dev.py
- tests/integration/test_dev.py::test_suggest_forwards_summary
- docs/how-chupa-works.md#2.2
- docs/how-chupa-works.md#12. Host projects

## Goal / Why
The managed block that `chupa core` writes into every host's `CLAUDE.md` and `AGENTS.md` carries only rules for ticket agents. It has no rule for interactive chat sessions. The owner wrote the rule "Always propose a ticket -- never hand-edit main from chat" in boardgameui. It never reached chupa or its hosts: fungo has a weaker "Plan first" rule in its own text, and chupa has neither. On 2026-11-08 a chat session in this repo was asked about a review feature and edited engine code, docs and tests while `serve` was running tickets, instead of authoring a ticket.

After this change, the managed block carries a `## Chat session conduct` section holding that rule, ported word for word from boardgameui with only repo-specific names substituted. Every host gets it through `core`. `./dev.py core` exists so the refresh runs from this repo's command surface, and this repo's `CLAUDE.md` and `AGENTS.md` carry the refreshed block.

## Scope in / Scope out
- In: `chupa/hostfiles.py` `CORE_TEMPLATE`. Append the text inside the `markdown` code fence below (not the fence lines) after the last existing bullet, separated from it by one blank line. Copy it byte for byte. Keep the line breaks, the double hyphens and the backticks. Do not reword, reflow, shorten or summarize it. The existing heading, intro paragraph and seven bullets are unchanged.

```markdown
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

If you have already started editing or have edited main without an explicit
override: stop immediately, tell the user you broke this rule, and ask whether
to revert the commit and refile as a ticket.

Why: direct chat edits bypass the ticket, run-record, review, dependency, and
retro artifacts that make chupa debuggable.
```

- In: `dev.py`. Add a `core` subcommand, help `refresh the managed conduct block`, forwarding to `chupa core` through the existing fallthrough `chupa(args.task)`.
- In: run `./dev.py core` after the template change so `CLAUDE.md` and `AGENTS.md` carry the new block. `core` does not touch `hosts/fixture/CLAUDE.md`, so re-render its managed block with `hostfiles.render`; `tests/integration/test_fixture_host.py` requires it `current`. In all three files only the managed block changes; every byte outside the `chupa:core` marker lines stays identical.
- In: tests.
  - `tests/integration/test_hostfiles.py::test_core_template_is_host_neutral`: also assert `b"## Chat session conduct"`, `b"### CRITICAL: Always propose a ticket -- never hand-edit main from chat"` and `b"Anger words alone do not count."` are in `CORE_TEMPLATE`. The `- ` bullet count stays 7, because the new text has no `- ` lines.
  - `tests/integration/test_dev.py`: add a test, like `test_suggest_forwards_summary`, that `dev.py core` calls `run` once with `["uv", "run", "python", "-m", "chupa", "core"]`.
- In: docs.
  - `docs/how-chupa-works.md` 2.2 `./dev.py` table: add a row `core` -> `chupa core`.
  - `docs/how-chupa-works.md` section 12, after "The block carries only process rules that hold for every host": add one sentence saying that the block has two parts. `Engine conduct` is for ticket agents, and `Chat session conduct` is for interactive chat sessions in a host checkout.
- Out: every other boardgameui or fungo chat rule (a later ticket ports those), section B of this repo's `CLAUDE.md` and `AGENTS.md`, the text of fungo or boardgameui, and `chupa/__main__.py`'s `core` verb.

## Scope fence
- chupa/hostfiles.py
- dev.py
- CLAUDE.md
- AGENTS.md
- hosts/fixture/CLAUDE.md
- tests/integration/test_hostfiles.py
- tests/integration/test_dev.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_hostfiles.py` passes. It asserts that `CORE_TEMPLATE` contains `### CRITICAL: Always propose a ticket -- never hand-edit main from chat` and `Anger words alone do not count.`, and still has exactly 7 `- ` bullet lines, not 8.
2. `CORE_TEMPLATE` contains the text inside this ticket's `markdown` code fence byte for byte, checked by reading `chupa/hostfiles.py` against this ticket.
3. `./dev.py test tests/integration/test_dev.py` passes, including a test that `dev.py core` runs `chupa core` once.
4. `CLAUDE.md`, `AGENTS.md` and `hosts/fixture/CLAUDE.md` each contain `## Chat session conduct` between the `chupa:core` marker lines, `classify_core` returns `current` for each (the `core_drift` gate and `./dev.py test tests/integration/test_fixture_host.py`), and `git diff main -- CLAUDE.md AGENTS.md hosts/fixture/CLAUDE.md` shows changes only between the marker lines.
5. `docs/how-chupa-works.md` has a `core` row in the 2.2 table and the two-part sentence in section 12.

## Verification
```
./dev.py test tests/integration/test_hostfiles.py tests/integration/test_dev.py tests/integration/test_merge.py tests/integration/test_fixture_host.py
./dev.py lint
```

## Definition of rejected
The rule text in `CORE_TEMPLATE` differs from the text inside this ticket's `markdown` code fence in any word, or `CLAUDE.md`, `AGENTS.md` or `hosts/fixture/CLAUDE.md` changes outside the managed block.

## Time budget
- expected: 20m
- stuck: 50m
