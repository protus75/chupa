---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- CLAUDE.md#A. Engine conduct
- AGENTS.md

## Goal / Why
The existing **Command surface** rule (`CLAUDE.md` section B) governs only what an interactive chat session runs. Nothing governs what a guide or ticket tells an operator to type.

On 2026-11-10 the first draft of the qwen provider setup guide told operators to hand-type qwen's full provider command line as a smoke test: `qwen --auth-type openai --openai-base-url <base_url> --openai-api-key ollama -m <model> -o stream-json --approval-mode plan --chat-recording false`. That is a copy of the argv chupa builds. It drifts from what chupa actually runs, and it makes the operator type it. The fix was a `chupa probe` verb.

When this ticket is done, section A of `CLAUDE.md`, and the matching `## Engine conduct` list in `AGENTS.md`, carry a rule. A guide, setup step, or ticket that has an operator exercise something chupa drives names the `chupa` verb, or `./dev.py` subcommand in this repo, that runs it. A missing verb is added by the same change.

## Scope in / Scope out
- In: insert one bullet in `CLAUDE.md` section `## A. Engine conduct`, directly after the **Verification uses `./dev.py test`.** bullet and its `Why:` line. Insert the same bullet in `AGENTS.md`, directly after that file's **Verification uses `./dev.py test`.** bullet and its `Why:` line. The bullet text, exactly:
  ```
  - **Guides name verbs, not command lines.** A host guide, setup step, or ticket that has an operator exercise something chupa drives (a provider CLI, a check, a gate) names the `chupa` verb, or `./dev.py` subcommand in this repo, that runs it; never a hand-built copy of chupa's argv. A step no verb covers gets a new verb in the same change. Third-party install and server commands (`pnpm add`, `ollama pull`) stay as written.
    Why: a copied argv drifts from what chupa runs and makes the operator type it; the first qwen setup guide draft had operators hand-type qwen's full provider command line (2026-11-10).
  ```
- Out:
  - every other line of `CLAUDE.md` and `AGENTS.md`, including the managed `## Engine conduct` block between the chupa core markers in `CLAUDE.md`;
  - the section B **Command surface** bullet;
  - existing guides and tickets;
  - code, tests, and any lint or gate enforcing the rule.

## Scope fence
- CLAUDE.md
- AGENTS.md

## Acceptance criteria
1. `grep -c "Guides name verbs, not command lines" CLAUDE.md AGENTS.md` prints `CLAUDE.md:1` and `AGENTS.md:1`, not `0` or `2` for either file.
2. In each file, the line directly after the **Verification uses `./dev.py test`.** bullet's `Why:` line is the new bullet. Check with `grep -n -A2 "nothing chose the raw form" CLAUDE.md AGENTS.md`.
3. `git diff main -- CLAUDE.md AGENTS.md` adds exactly two lines to each file and removes none.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a file other than `CLAUDE.md` or `AGENTS.md` changes;
- the managed `## Engine conduct` block in `CLAUDE.md` changes;
- either file loses or rewords an existing line;
- the bullet text differs from the text in `Scope in`.

## Time budget
- expected: 5m
- stuck: 30m
