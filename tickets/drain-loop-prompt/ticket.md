---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/ask.py
- chupa/__main__.py::main
- chupa/specs/ask/running.md
- vscode-chupa/extension.js
- vscode-chupa/package.json
- tests/integration/test_ask.py
- tests/unit/test_drain_detach_cli.py
- chupa/hostfiles.py::CORE_TEMPLATE
- chupa/docs/host-running.md
- docs/how-chupa-works.md#2.1 Verbs
- docs/how-chupa-works.md#2.2

## Goal / Why
Today an operator who wants a Claude Code chat to babysit the drain has to paste a hand-written supervising prompt. That prompt tells the chat to:
- start and stop the drain;
- make the small ticket fixes a supervising session is allowed;
- stop when the queue is empty or blocked on a human.

A pasted copy is unversioned, it drifts from the engine's rules, and it hard-codes the state directory.

After this change:
- `chupa prompt drain-loop` prints that supervising prompt from an engine-owned template, `chupa/specs/ask/drain-loop.md`, with the host's real `state_dir`.
- The Tickets view's More Actions menu has "Ask Claude: drain loop". It opens a Claude Code chat with that prompt, the same way "Ask Claude: diagnose" does.

The prompt is a `prompt` kind, not a separate verb. `prompt` is the one verb that renders operator prompts (ticket `ask-prompt-verb`), and `drain-loop` is one more such prompt.

## Scope in / Scope out
- In: new template `chupa/specs/ask/drain-loop.md`.
  - It is a plain `string.Template`, like its siblings. Its only placeholder is `${state_dir}`, and it contains no other `$`.
  - Its text is exactly the block below. Nothing else in the ticket is template text.

```
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
```

- In: `chupa/ask.py`.
  - Add `"drain-loop"` to `KINDS`.
  - `render` substitutes only `state_dir` for `drain-loop`. It uses the same repo-relative-or-absolute rule as the other kinds and the same `ask_notes` `host_notes` block.
- In: the `prompt` verb in `chupa/__main__.py`. `stems` is already `nargs="*"`; the existing `drafts`, `box`, and ticket-kind refusals stay unchanged.
  - `prompt drain-loop` with no stems prints the rendered prompt and exits 0. It takes no lock and writes no state.
  - `prompt drain-loop` with any stem refuses with a `runner.Refusal`, paved road "drain-loop takes no stem".
  - Help text for `prompt` becomes "render an operator prompt".
- In: `vscode-chupa/extension.js`.
  - Extract the duplicated "run `prompt` argv, then open the Claude Code `/open?prompt=` URI, or show stderr on error" code into one function, `openClaude(root, args)`.
  - `askClaude`, the `chupa.box.discuss` handler, the `chupa.ticket.askDrafts` handler, and the new command all call it. With four callers, the undocumented URI then lives in one place.
  - Register `chupa.askDrainLoop`, which calls `openClaude(root, ['prompt', 'drain-loop'])`. The extension holds no prompt text.
- In: `vscode-chupa/package.json`.
  - Add command `chupa.askDrainLoop`, titled `Ask Claude: drain loop`.
  - Add a `view/title` entry with `"when": "view == chupa.tickets"` and `"group": "chupa@7"`. This puts it in the Tickets view's More Actions menu.
  - Add a `commandPalette` entry with `"when": "false"`, like `chupa.bulkTriage`.
- In: tests.
  - A new `tests/unit/test_ask_drain_loop.py`. Following `tests/unit/test_ask_drafts.py`, it monkeypatches `chupa.__main__.load_config` and `child_env`, stubs `Path.read_text` where a test renders, and reads no file. Tests:
    - `test_render_drain_loop_unit`: with `Path.read_text` returning "/loop ${state_dir}/drain.out" and a `SimpleNamespace` config with `state_dir` `/repo/custom` and `ask_notes` None, rendering `drain-loop` through `ask.render` with repo `/repo` returns "/loop custom/drain.out". This rules out a hard-coded or absolute state directory.
    - `test_prompt_verb_drain_loop_prints_unit`: with the same stub, `main(["prompt", "drain-loop"])` returns 0 and prints the rendered text. This rules out a refusal or an empty print on the success path.
    - `test_prompt_verb_drain_loop_refuses_stem`: `main(["prompt", "drain-loop", "x"])` returns 2 with "drain-loop takes no stem" on stderr. This rules out a drain-loop kind that silently ignores a stem.
    - `test_prompt_verb_ticket_kind_still_requires_stem`: `main(["prompt", "review"])` returns 2 with "exactly one stem" on stderr. The box no-ids refusal is already pinned by `tests/unit/test_ask_drafts.py`.
  - A new `tests/integration/test_ask_drain_loop.py`, which renders the real template from disk. Tests:
    - `test_drain_loop_renders_state_dir_and_loop_prefix`: with `state_dir` `custom/state`, the output starts with `/loop ` and contains `custom/state/drain.out`. It never contains `.chupa/state`. This rules out a hard-coded state directory or a dropped `/loop` prefix.
    - `test_drain_loop_keeps_owner_verdict_limits`: the output contains ``Never run `confirm` or `reject` `` and `ticket_changed`. This rules out a template that lets the session issue verdicts.
    - `test_prompt_verb_drain_loop_prints_without_state`: in a `tmp_path` repo, `main(["prompt", "drain-loop"])` returns 0 and prints output starting with `/loop `. `state_dir` does not exist afterwards.
  - In `tests/integration/test_ask.py`, the only change: the `test_each_kind_renders_stem_ticket_and_state_dir` parametrize also skips `"drain-loop"`, because that kind renders no stem.
- In: docs.
  - `docs/how-chupa-works.md` section 2.1: the `prompt box <id> ...` table row gets a sibling row `prompt drain-loop`, "Print the supervising drain-loop prompt without writing state."
  - In the same file, the section 2.2 extension paragraph sentence about the More Actions menu also names Ask Claude: drain loop, which opens a Claude Code chat with `prompt drain-loop`.
  - `chupa/docs/host-running.md`: the `prompt` row reads "Render an operator prompt for a ticket, named box IDs, all committed drafts, or the drain loop without writing state."
- Out:
  - the existing three ticket templates, `box.md`, and `drafts.md`;
  - driver specs;
  - `dev.py`;
  - snapshot, `graph.py`;
  - `CORE_TEMPLATE`;
  - any change to drain or serve behavior.

## Scope fence
- chupa/specs/ask/drain-loop.md
- chupa/ask.py
- chupa/__main__.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- tests/unit/test_ask_drain_loop.py
- tests/integration/test_ask_drain_loop.py
- tests/integration/test_ask.py
- docs/how-chupa-works.md
- chupa/docs/host-running.md

## Acceptance criteria
1. `./dev.py test tests/unit/test_ask_drain_loop.py tests/integration/test_ask_drain_loop.py tests/integration/test_ask.py` exits 0. That run includes all seven new tests, and each rules out the wrong result named in Scope in.
2. `node --check vscode-chupa/extension.js` exits 0. In `vscode-chupa/extension.js`, `grep -c "anthropic.claude-code/open" vscode-chupa/extension.js` prints 1, not 2 or 3, so the URI lives only in `openClaude`.
3. `vscode-chupa/package.json` declares `chupa.askDrainLoop`, titled `Ask Claude: drain loop`, under `view/title` with group `chupa@7` and `when` `view == chupa.tickets`. `python3 -c` with `json.load` over the file, as listed in `## Verification`, exits 0.
4. Each doc says what Scope in sets for it:
   - the `docs/how-chupa-works.md` section 2.1 table has a `prompt drain-loop` row;
   - the section 2.2 More Actions sentence names Ask Claude: drain loop and `prompt drain-loop`;
   - the `chupa/docs/host-running.md` `prompt` row reads exactly the Scope in text, which mentions the drain loop.
5. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/unit/test_ask_drain_loop.py tests/integration/test_ask_drain_loop.py tests/integration/test_ask.py
node --check vscode-chupa/extension.js
python3 -c "import json; p = json.load(open('vscode-chupa/package.json')); m = [e for e in p['contributes']['menus']['view/title'] if e['command'] == 'chupa.askDrainLoop']; assert m == [{'command': 'chupa.askDrainLoop', 'when': 'view == chupa.tickets', 'group': 'chupa@7'}], m"
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- prompt text appears in `vscode-chupa/extension.js` or `vscode-chupa/package.json`;
- a new top-level verb is added instead of a `prompt` kind;
- `prompt drain-loop` takes the lock or writes state;
- the template's text differs from the block in Scope in, beyond the `${state_dir}` substitution;
- any existing template or driver spec changes.

## Time budget
- expected: 40m
- stuck: 120m
