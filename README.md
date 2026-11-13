# chupa

*CLI Harness for Unattended Pipeline Agents*

chupa is an engine that runs CLI coding agents through the ticket lifecycle against a git repository. Each ticket lives in `tickets/<stem>/`; its markdown and JSON files, including `ticket.md`, `run.md`, `review.md`, `diagnosis.json`, and others, pass work between stages. Reviewed work merges to local `main`. See the [ticket lifecycle diagram](https://github.com/protus75/chupa/blob/main/vscode-chupa/media/ticket-lifecycle.svg).

[GitHub repository](https://github.com/protus75/chupa)

## Install

Add chupa to your host project and sync its environment:

```sh
uv add --dev chupa
uv sync
```

Run its verbs as `uv run chupa <verb>`. Your host also needs `config.yaml`; start with the [copyable configuration](https://github.com/protus75/chupa/blob/main/chupa/docs/host-contract.md).

## Set up a host

Run `uv run chupa doctor`, then `uv run chupa core` to write the managed conduct block into `CLAUDE.md` for Claude and Qwen Code or `AGENTS.md` for other CLIs. Commit the files. The block gives a chat agent rules for authoring and editing tickets with `chupa new`, `chupa lint`, and `chupa review`, and for supervising a drain. Re-run `core` after upgrading chupa: `drain`, `serve`, and `run` refuse to start while the block is stale.

## The working loop

1. Open Claude Code or Codex in the host checkout, often with auto permissions.
2. Work out a plan with the chat agent.
3. Ask it to turn the plan into tickets. It runs `chupa new`, fills each ticket, and repeats `chupa lint` and `chupa review` until each is clean.
4. Ask it to drain the queue with `uv run chupa drain`, or leave `uv run chupa serve` running to pick up new tickets live. chupa coordinates CLI agents through authoring, implementation, checking, review, and merge.
5. Ask the chat agent to supervise: watch `chupa status` and `chupa watch`, diagnose rejected or blocked tickets from their `tickets/<stem>/` artifacts, fix small ticket problems, and stop with `chupa stop` or `chupa kill` and restart the drain as needed.
6. Use the Suggestion Box as an escape valve. An implementing agent reports second problems in its `second_problems` reply, and the engine files them to the box so the ticket can complete its own goal. Runs that exhaust attempt caps, retros, and `chupa suggest` from a chat session also file there. Triage resolves each message as `declined`, `tombstone` (already covered), or authored into a ticket; an authored ticket can start as a `draft` awaiting a person.
7. Keep the judgment calls: ask the chat agent for a plain-English summary of each draft or held ticket, then run `chupa confirm` or `chupa reject` on each.

In chupa's own repository history, measured on 2026-11-09 from `.chupa/state/box/` and the journal, 32 of 389 Suggestion Box messages (about 8%) became tickets, all as drafts. Of the 31 drafts decided, 24 were confirmed (about 77%) and 7 rejected.

One unattended drain ran about 30 tickets in about 4 hours, many of them triage-authored bug fixes and small features. The practical limit is how fast a person can plan enough work to fill the queue, so planning sessions with the chat agent are where the person spends their time.

For example, ask your chat agent:

- “Help me plan this feature and turn the plan into chupa tickets.”
- “Drain the queue and supervise any held tickets.”
- “Summarize the drafts in plain English so I can decide which to confirm.”

## Commands

```sh
# Setup
uv run chupa doctor   # inspect host setup
uv run chupa core     # refresh managed conduct files
# Authoring
uv run chupa new      # create and lint a ticket skeleton
uv run chupa lint     # validate tickets without writing
uv run chupa review   # review a committed ticket
uv run chupa order    # edit ticket priority or ordering
uv run chupa suggest  # file an idea into the Suggestion Box
# Running
uv run chupa drain    # run eligible tickets to quiescence
uv run chupa serve    # run the continuous daemon
uv run chupa run      # run one ticket through the pipeline
uv run chupa stop     # finish active work and exit
uv run chupa kill     # stop the engine at a safe point
uv run chupa pause    # ask the engine to pause admission
uv run chupa resume   # ask the engine to release its current hold
# Observing
uv run chupa status   # show the journal projection
uv run chupa watch    # show the live text view
uv run chupa stats    # show health and efficiency figures
# Decisions
uv run chupa confirm  # confirm a draft or Reject item
uv run chupa reject   # reject a draft or Reject item
```

Stop `serve` before `drain` or `run`: each takes the writer lock. See the [host run guide](https://github.com/protus75/chupa/blob/main/chupa/docs/host-running.md) for every verb.

## VS Code extension

The [chupa tickets extension](https://marketplace.visualstudio.com/items?itemName=chunkydragon.vscode-chupa) (`chunkydragon.vscode-chupa`) shows the ticket graph, details, recent steps, Suggestion Box, and stats. Set `chupa.command` when the engine command differs from the default host `.venv/bin/chupa`.

## Docs

- [Host run guide](https://github.com/protus75/chupa/blob/main/chupa/docs/host-running.md): invocation and operation on a host.
- [Host ticket authoring](https://github.com/protus75/chupa/blob/main/chupa/docs/host-authoring.md): what to write in a ticket.
- [Host contract](https://github.com/protus75/chupa/blob/main/chupa/docs/host-contract.md): the config schema and host-facing contract.
- [How chupa works](https://github.com/protus75/chupa/blob/main/docs/how-chupa-works.md): how chupa behaves today. Tickets keep it current.

## Developing chupa

This section is for working on chupa itself. In this repo, use `./dev.py`:

    ./dev.py new STEM [--kind feature|bug|chore] [--evidence FILE...]   # write a ticket skeleton
    ./dev.py lint [STEM...]                         # check tickets
    ./dev.py review STEM...                       # review tickets against merged code
    ./dev.py drain                                  # run every eligible ticket to quiescence
    ./dev.py status                                 # what ran, what is held, total spend
    ./dev.py confirm STEM / ./dev.py reject STEM    # keep or kill a held ticket
    ./dev.py kill                                   # stop a running drain
    ./dev.py test [args]                            # run the test suite

`CHUPA_PLAN.md` is the frozen record of how chupa was first built. It is history, not a reference.

Every chupa verb is listed in [how chupa works, section 2](https://github.com/protus75/chupa/blob/main/docs/how-chupa-works.md#2-commands).
