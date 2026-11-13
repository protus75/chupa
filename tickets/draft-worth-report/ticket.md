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
- chupa/specs/ask/box.md
- chupa/specs/ask/review.md
- chupa/__main__.py::_parser
- chupa/__main__.py::main
- chupa/observe.py::snapshot
- chupa/observe.py::MENU
- tests/integration/test_menu_verb_parity.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- dev.py
- tests/integration/test_ask.py
- tests/integration/test_dev.py

## Goal / Why
Triage turns Suggestion Box messages into draft tickets that wait for the operator's confirm or reject. Today the operator reads each draft alone and decides by feel. Tickets that are easy or sound sensible get confirmed even when they guard a rare corner case or add polish nobody needed, and that accretion is chupa's main failure mode (CLAUDE.md section A, "Simplest thing that satisfies the ticket").

When this ticket is done:
- `chupa prompt drafts` prints one operator prompt that names every committed draft ticket (the rows the Tickets view marks `draft`). The prompt asks Claude for a plain-English confirm-or-reject report with a high bar for confirm.
- `./dev.py prompt KIND [STEM ...]` forwards to `chupa prompt` in this repo.
- Right-clicking any draft row in the extension's Tickets view shows "Ask Claude: assess drafts". It opens a new Claude Code chat with that prompt, the same way "Ask Claude: review" does.

The report helps the operator reject just-in-case, corner-case, and gold-plating drafts before they cost implementation runs.

## Scope in / Scope out
In:
- `chupa/specs/ask/drafts.md`: a new `string.Template` operator prompt with two placeholders, `${tickets}` and `${state_dir}`, and no other `$`. Its text, verbatim:

  ```
  Assess these draft chupa tickets, each waiting for me to confirm or reject it:
  ${tickets}

  For each draft, read its ticket, the merged code and files it names, and, when its frontmatter `source` starts with `box:`, the Suggestion Box message under ${state_dir}/box/ whose resolution links to it. Then recommend confirm or reject.

  The bar for confirm is high. Confirm only a ticket that fixes a defect or failure that has happened, or will happen in normal use, or that delivers a benefit the project needs now; name the incident, failure, or file that proves it. Being easy, cheap, or sensible-sounding is never a reason to confirm. Reject a ticket that is just-in-case hardening, guards a corner case unlikely to occur in normal use, duplicates or overlaps another ticket or merged code, rests on a premise the merged code contradicts, or is gold plating: polish, abstraction, configurability, or extra checks that no incident earned. When the evidence is thin, recommend reject and say what evidence would change your mind.

  Write the report to me in plain English, as to someone who has not read the engine code. For each draft give its stem, one or two sentences on what it would change, your verdict (confirm or reject), and the concrete reason. Explain any chupa term you must use, and name files, stems, and commands only where I need them. End with a "Recommendation" section that walks me through what to do as numbered steps: one step that confirms every draft you would keep and one that rejects every draft you would drop. For each step, say in one sentence what it does and why, give the exact `./dev.py confirm --yes STEM ...` or `./dev.py reject --yes STEM ...` command in its own copy/paste block, and say what I should see when it worked. Where a verdict is a judgment call, lay out the options and say which you would pick. Do not run the steps yourself; wait for me to say go.
  ```
- `chupa/ask.py`: add `"drafts"` to `KINDS`. `render("drafts", stems, config, repo)` takes a list of stems. It substitutes `${tickets}` with one line per stem, in the order given: `- <stem>: tickets/<stem>/ticket.md`. It substitutes `${state_dir}` the same way the other kinds do, and appends `ask_notes` the same way.
- `chupa/__main__.py`, `prompt` verb:
  - `stems` becomes `nargs="*"`.
  - `prompt drafts` refuses any stems (exit 2, paved road: run `chupa prompt drafts` with no stems). With no stems, it selects the stems of `observe.snapshot` rows whose `draft` field is true, in snapshot row order. It builds the `observe.Context` the way the `snapshot` verb does. It does not re-derive the draft predicate. With no drafts, it refuses (exit 2): "no draft tickets await confirm or reject", paved road "run triage, or author a ticket with chupa new".
  - `prompt box` with no ids refuses (exit 2, paved road: name at least one box id).
  - The ticket kinds keep their exactly-one-stem refusal.
  - `prompt` still writes no state.
- `chupa/observe.py`: add a `"chupaAskDrafts"` entry to `MENU`, following `chupaAskReview`: kind `"ticket"`, `extension_only=True`, inputs `("draft",)`, admission `admit` when `draft` is true and `noop` otherwise. Each ticket row's `menu` then carries `chupaAskDrafts` as `"on"` for a draft row and `"off"` otherwise. Nothing else in the snapshot changes.
- `vscode-chupa/extension.js`: register `chupa.ticket.askDrafts`. It runs `prompt drafts` through `runData`, shows any error with `showErrorMessage`, and opens the Claude Code `/open` URI with stdout, exactly as `chupa.box.discuss` does. It passes no stems and selects nothing itself.
- `vscode-chupa/package.json`:
  - a `chupa.ticket.askDrafts` command titled "Ask Claude: assess drafts", category `chupa`, enablement `chupaAskDrafts == 'on'`;
  - a `webview/context` entry in group `4_claude@3` whose `when` follows the `chupaAskReview` pattern with `chupaAskDrafts`;
  - a `commandPalette` entry with `when: "false"`.
- `dev.py`: a `prompt` subcommand taking `kind` and `stems` (`nargs="*"`) that runs `chupa prompt <kind> <stems...>` once. Add it to the module docstring.
- Tests:
  - `tests/integration/test_ask.py`: exclude `"drafts"` from the per-stem parametrize skip list, alongside `"box"`, and add the real-git drafts selection test.
  - `tests/integration/test_ask_drafts.py`: the render tests. They read the real template from disk, so they are integration tests.
  - `tests/unit/test_ask_drafts.py`: the `main` selection and refusal tests, touching no disk: `chupa.observe.snapshot`, `chupa.__main__.load_config`, and `chupa.ask.render` are monkeypatched, and the `render` stub records the stems it receives.
  - `tests/integration/test_watch.py`: the menu test.
  - `tests/integration/test_menu_verb_parity.py`: widen the extension-only set assertion to `{"chupaAskDiagnose", "chupaAskReview", "chupaAskDrafts"}`.
  - `tests/integration/test_dev.py`: the forwarding test.
- Docs:
  - `docs/how-chupa-works.md` section 2.1: add a `prompt drafts` row to the verb table, next to the `prompt box` row.
  - `docs/how-chupa-works.md` section 2.2: add a `prompt KIND [STEM ...]` row.
  - `chupa/docs/host-running.md`: widen the `prompt` row's description to cover all committed drafts.

Out:
- The engine running the model itself, or writing a report file. The operator chose the Claude-chat route.
- Any change to confirm, reject, triage, or the Author prompt.
- A drafts section, group, or title-bar button in the Tickets view.
- Explicit stem selection for `prompt drafts`.

## Scope fence
- chupa/specs/ask/drafts.md
- chupa/ask.py
- chupa/__main__.py
- chupa/observe.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- dev.py
- docs/how-chupa-works.md
- chupa/docs/host-running.md
- tests/integration/test_ask.py
- tests/integration/test_watch.py
- tests/integration/test_dev.py
- tests/integration/test_ask_drafts.py
- tests/integration/test_menu_verb_parity.py
- tests/unit/test_ask_drafts.py

## Acceptance criteria
1. In `tests/integration/test_ask_drafts.py`, `ask.render("drafts", ["a-one", "b-two"], config, repo)`:
   - contains `- a-one: tickets/a-one/ticket.md` before `- b-two: tickets/b-two/ticket.md`. This rules out dropping a stem, reordering, or using a fixed path.
   - contains the configured state directory followed by `/box/`, not the default `.chupa`.
   - contains `"Recommendation"`, `./dev.py confirm --yes`, `./dev.py reject --yes`, and `gold plating`. A prompt without the reject bar or the command steps fails.
   - when `config.ask_notes` is set, ends with the `host_notes` data block.
   Checked by `./dev.py test tests/integration/test_ask_drafts.py`.
2. In `tests/integration/test_ask.py`, a test sets up a real git repo in `tmp_path` with three tickets: a committed `state: draft`, a committed `state: confirmed`, and an untracked `state: draft`. `main(["prompt", "drafts"], cwd=tmp_path)` returns 0. The output names only the committed draft, not the confirmed or untracked ticket, and the state directory is not created. Checked by `./dev.py test tests/integration/test_ask.py`.
3. In `tests/unit/test_ask_drafts.py`, tests call `main([...])` with `chupa.observe.snapshot` monkeypatched to return rows, `chupa.__main__.load_config` monkeypatched to return a config, and `chupa.ask.render` monkeypatched to a stub that records its kind and stems. They read and write no disk and use no git subprocess.
   - With rows `draft-one` (draft), `not-draft` (not draft), `draft-two` (draft), in that order, `main(["prompt", "drafts"])` returns 0 and the stub received kind `"drafts"` and exactly `["draft-one", "draft-two"]`. A predicate other than the `draft` field, or a reordering, fails.
   - Each of these returns 2 with the paved road on stderr, never calls the stub, and prints no prompt: `main(["prompt", "drafts", "some-stem"])`; `main(["prompt", "drafts"])` when no row is a draft; and `main(["prompt", "box"])` with no ids.
   Checked by `./dev.py test tests/unit/test_ask_drafts.py`.
4. In `tests/integration/test_watch.py`, a snapshot with one draft row and one confirmed row gives `menu["chupaAskDrafts"] == "on"` for the draft and `"off"` for the confirmed row. A flag that is on for every row fails. `tests/integration/test_menu_verb_parity.py` asserts the extension-only `MENU` keys are exactly `{"chupaAskDiagnose", "chupaAskReview", "chupaAskDrafts"}`, so a hand-added row key outside `MENU` fails. Checked by `./dev.py test tests/integration/test_watch.py tests/integration/test_menu_verb_parity.py`.
5. In `tests/integration/test_dev.py`, `./dev.py prompt drafts` runs exactly `["uv", "run", "python", "-m", "chupa", "prompt", "drafts"]` once. Checked by `./dev.py test tests/integration/test_dev.py`.
6. `vscode-chupa/package.json` declares `chupa.ticket.askDrafts` with enablement `chupaAskDrafts == 'on'`, a `webview/context` entry in `4_claude@3`, and a `commandPalette` `when: "false"` entry. `vscode-chupa/extension.js` registers it and calls `runData` with argv `['prompt', 'drafts']` and no stem filtering. Checked by reading `vscode-chupa/package.json` and `vscode-chupa/extension.js`.
7. The `docs/how-chupa-works.md` 2.1 and 2.2 tables and the `chupa/docs/host-running.md` `prompt` row describe `prompt drafts`. Checked by reading `docs/how-chupa-works.md` and `chupa/docs/host-running.md`.
8. The full suite passes: `./dev.py test`.

## Verification
```
./dev.py test
```

## Definition of rejected
- `prompt drafts` selects drafts with its own predicate rather than the snapshot rows' `draft` field.
- The extension filters, lists, or passes draft stems itself.
- Any `chupa/specs/ask/drafts.md` text that softens the reject bar, for example by allowing confirm because a ticket is cheap.
- The change calls a model from chupa or writes a report file.
- `prompt` writes state.

## Time budget
- expected: 45m
- stuck: 120m
