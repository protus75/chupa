---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- README.md
- pyproject.toml
- docs/host-running.md
- docs/host-authoring.md
- docs/host-contract.md#Install
- docs/host-contract.md#VS Code extension
- docs/host-contract.md#Managed conduct and ticket ownership
- docs/how-chupa-works.md#1. What chupa is
- docs/how-chupa-works.md#3.3 What the engine writes back
- docs/how-chupa-works.md#7. Drain and serve
- docs/how-chupa-works.md#12. Host projects
- vscode-chupa/package.json
- vscode-chupa/README.md

## Goal / Why
`pyproject.toml` sets `readme = "README.md"`, so `README.md` is the page at https://pypi.org/project/chupa/. Today that page is written for chupa's own developers. It lists only `./dev.py` commands, which do not exist in a host project that installs chupa from PyPI. Its links are relative (`docs/host-contract.md#install`), so they break on PyPI. It never explains how a person actually uses chupa on their own repo.

After this change, `README.md` is written first for a host-project user. It explains the working loop: a person plans with a local chat agent (Claude Code or Codex) open in the host checkout. That agent authors tickets under the rules `chupa core` installs. `chupa drain` or `chupa serve` then coordinates CLI agents through the ticket lifecycle (author, implement, check, review, merge), and those agents communicate through markdown files in `tickets/<stem>/`. The same chat agent supervises the run. The owner's real use of this loop ran about 30 tickets in one day. The `./dev.py` commands stay, in a final section for people working on chupa itself.

## Scope in / Scope out
- In: rewrite `README.md` with these sections, in this order:
  1. `# chupa`, then one paragraph saying what chupa is: an engine that runs CLI coding agents through the ticket lifecycle against a git repo. Each ticket is a folder `tickets/<stem>/` whose markdown and JSON files (`ticket.md`, `run.md`, `review.md`, `diagnosis.json`, and others, per `docs/how-chupa-works.md` section 3.3) are how the stages hand work to each other. Reviewed work merges to local `main`. Include a link to the ticket lifecycle diagram at `https://github.com/protus75/chupa/blob/main/vscode-chupa/media/ticket-lifecycle.svg`.
  2. `## Install`: `uv add --dev chupa`, `uv sync`, then run verbs as `uv run chupa <verb>`. Note that a host needs `config.yaml` and link to the copyable configuration in `docs/host-contract.md`.
  3. `## Set up a host`: `uv run chupa doctor`, then `uv run chupa core` to write the managed conduct block into `CLAUDE.md` (Claude) or `AGENTS.md` (other CLIs), then commit those files. Say what the block gives a chat agent: the rules for authoring and editing tickets (`chupa new`, `chupa lint`, `chupa review`) and for supervising a drain. Re-run `core` after upgrading chupa, because `drain`, `serve`, and `run` refuse while the block is stale.
  4. `## The working loop`: numbered happy path. (a) Open Claude Code or Codex in the host checkout, often with auto permissions. (b) Work out a plan with it. (c) Ask it to turn the plan into tickets; it runs `chupa new`, fills each ticket, and repeats `chupa lint` and `chupa review` until each is clean. (d) Ask it to drain the queue (`uv run chupa drain`), or leave `uv run chupa serve` running, which picks up new tickets live. (e) Ask it to supervise: watch `chupa status` and `chupa watch`, diagnose rejected or blocked tickets from their `tickets/<stem>/` artifacts, fix small ticket problems, and stop (`chupa stop` or `chupa kill`) and restart the drain as needed. (f) The person keeps the judgment calls: `chupa confirm` / `chupa reject` for held tickets and drafts. Include 2 to 4 short example prompts a user would type to the chat agent. State that this loop ran about 30 tickets in a day.
  5. `## Commands`: a code block of the host-facing verbs grouped as setup (`doctor`, `core`), authoring (`new`, `lint`, `review`, `order`, `suggest`), running (`drain`, `serve`, `run`, `stop`, `kill`, `pause`, `resume`), observing (`status`, `watch`, `stats`), and decisions (`confirm`, `reject`), each prefixed `uv run chupa` with a one-line comment. Each comment must agree with `docs/host-running.md` and `chupa --help`. Then one sentence on the writer lock: stop `serve` before `drain`, `run`, or `review`. Link to `docs/host-running.md` for every verb.
  6. `## VS Code extension`: one paragraph naming the `chupa tickets` extension (`chunkydragon.vscode-chupa`, https://marketplace.visualstudio.com/items?itemName=chunkydragon.vscode-chupa). Say what it shows (ticket graph, details, recent steps, Suggestion Box, stats) and mention the `chupa.command` setting, per `vscode-chupa/README.md`.
  7. `## Docs`: absolute GitHub links (`https://github.com/protus75/chupa/blob/main/...`) to `docs/host-running.md`, `docs/host-authoring.md`, `docs/host-contract.md`, and `docs/how-chupa-works.md`, each with its existing one-line description.
  8. `## Developing chupa`: one sentence saying this section is for working on chupa itself, then the existing `./dev.py` block unchanged, the `CHUPA_PLAN.md` sentence, and the pointer to `docs/how-chupa-works.md` section 2.
- In: every link in `README.md` is an absolute `https://` URL so it resolves on PyPI.
- Out:
  - `pyproject.toml` (including its `readme` key and version);
  - `docs/`, `vscode-chupa/`, `CLAUDE.md`, `AGENTS.md`, and `chupa/` code and specs;
  - a second README file or a separate PyPI long description;
  - publishing to PyPI.

## Scope fence
- README.md

## Acceptance criteria
1. `README.md` contains the headings `## Install`, `## Set up a host`, `## The working loop`, `## Commands`, `## VS Code extension`, `## Docs`, and `## Developing chupa`, in that order. Check with `grep -n '^## ' README.md`.
2. `./dev.py` appears in `README.md` only after the `## Developing chupa` heading. Check with `grep -n 'dev.py' README.md` against the heading's line number from criterion 1.
3. Every markdown link target in `README.md` starts with `https://`. Check with `grep -noE '\]\([^)]*\)' README.md`; no target is relative or a bare `#anchor`.
4. Every verb in the `## Commands` block is listed by `uv run chupa --help`, and every line of that block starts with `uv run chupa ` or `#`.
5. `## Set up a host` names `chupa core`, `CLAUDE.md`, and `AGENTS.md`. `## The working loop` names `drain`, `serve`, `confirm`, `reject`, and `tickets/<stem>/`, and includes the 30-tickets-a-day figure.
6. `## VS Code extension` contains `https://marketplace.visualstudio.com/items?itemName=chunkydragon.vscode-chupa` and `chupa.command`.
7. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `./dev.py` commands appear outside `## Developing chupa`;
- any file other than `README.md` changes;
- the README documents a verb, flag, or behavior that `chupa --help` or `docs/host-running.md` contradicts;
- a relative link remains.

## Time budget
- expected: 25m
- stuck: 75m
