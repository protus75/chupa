---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/__main__.py
- chupa/specs.py
- chupa/config.py
- chupa/runner.py
- vscode-chupa/extension.js
- tests/test_config.py
- docs/how-chupa-works.md
- docs/host-contract.md
- tests/test_cli.py

## Goal / Why
The `vscode-chupa` extension's "Ask Claude: diagnose" and "Ask Claude: review" menu items open a Claude Code chat with a prompt. Today that prompt is hard-coded as JavaScript template strings in `askClaude` in `vscode-chupa/extension.js`. This has three problems:
- prompts are engine content, and that copy is unversioned and outside `specs/`;
- the text hard-codes `.chupa/state/` and "CLAUDE.md section B", which hold only in this repo;
- a host repo cannot add guidance of its own.

Docs section 8.4 sets the rule: prompts come from the engine's `specs/`, and host material enters only as data.

After this change:
- the three prompts live in `specs/ask/`;
- `chupa prompt <diagnose|running|review> <stem>` renders one with the host's real values and prints it;
- an optional `ask_notes` config value is appended inside a `host_notes` data block;
- the extension prints what that verb returns and holds no prompt text.

## Scope in / Scope out
- In: `specs/ask/diagnose.md`, `specs/ask/running.md`, `specs/ask/review.md`.
  - Each is a plain Markdown template, not a driver spec: no frontmatter, never passed to `load_spec`.
  - Each uses `string.Template` placeholders `${stem}`, `${ticket}` (`tickets/<stem>/ticket.md`), and `${state_dir}` (the config's `state_dir`, relative to the repo root).
  - Their text is the extension's current three prompts with three changes:
    - `.chupa/state` becomes `${state_dir}`;
    - the phrase "following CLAUDE.md section B" is dropped, because Claude Code loads the workspace's conduct file itself;
    - each ends with the current plain-English and "Recommendation" instruction.
- In: `chupa/ask.py`:
  - `KINDS = ("diagnose", "running", "review")`;
  - `render(kind, stem, config, repo) -> str` substitutes the placeholders with `string.Template.substitute`, so a missing value raises;
  - when `config.ask_notes` is set, it appends a block built with `specs.data_open("host_notes")`, `specs.quote_payload(notes)`, and `specs.data_close("host_notes")`.
- In: `chupa/config.py`: `Config.ask_notes: str | None = None`.
- In: the `prompt` verb in `chupa/__main__.py`, beside `core`, after `load_config`:
  - `prompt` takes `kind` (argparse `choices=KINDS`) and `stem`;
  - it refuses a bad stem (`stem_findings`) or a missing `tickets/<stem>/ticket.md` with a `runner.Refusal` and paved road;
  - it prints the rendered prompt and exits 0;
  - it takes no lock and writes no journal event or file.
- In: `vscode-chupa/extension.js`.
  - `askClaude` runs `uv run python -m chupa prompt <kind> <stem>` with `execFile`: an argv list, the repo root as cwd.
  - The kind is `running` when the row's `chupaSection` is `running` and the item is diagnose; otherwise it is the item's kind.
  - It passes stdout to the existing Claude Code `/open?prompt=` URI.
  - On a non-zero exit it shows stderr in an error message.
  - It holds no prompt text.
- In: tests in a new `tests/test_ask.py`:
  - `test_each_kind_renders_stem_ticket_and_state_dir`: a config whose `state_dir` is not `.chupa/state` shows up in the output;
  - `test_host_notes_appended_as_data_block_only_when_set`;
  - `test_prompt_verb_refuses_missing_ticket`;
  - `test_prompt_verb_takes_no_lock`: no lockfile appears under `state_dir`.
- In: `tests/test_config.py`: `ask_notes` defaults to `None` and parses from YAML.
- In: docs.
  - `docs/how-chupa-works.md` section 2.1: a `prompt` row.
  - Section 8.4: one sentence saying that `specs/ask/` holds operator prompt templates rendered by `prompt`, not driver specs.
  - Section 11: `ask_notes`.
  - `docs/host-contract.md`: `ask_notes` as the host's way to add guidance to these prompts.
- Out: the driver, `load_spec`, the eight driver specs, the extension's menu, and `dev.py`.

## Scope fence
- specs/ask/
- chupa/ask.py
- chupa/config.py
- chupa/__main__.py
- vscode-chupa/extension.js
- tests/test_ask.py
- tests/test_config.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. `uv run pytest -q tests/test_ask.py tests/test_config.py` exits 0, including the tests above.
2. `node --check vscode-chupa/extension.js` exits 0, and `grep -c "Diagnose chupa ticket" vscode-chupa/extension.js` prints 0.
3. `docs/how-chupa-works.md` sections 2.1, 8.4 and 11, and `docs/host-contract.md`, describe `prompt` and `ask_notes`.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_ask.py tests/test_config.py
node --check vscode-chupa/extension.js
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- prompt text remains in `vscode-chupa/extension.js`;
- a template is loaded from the host repo;
- `ask_notes` is inserted outside a `host_notes` data block;
- `prompt` takes the lock or writes state;
- any driver spec changes.

## Time budget
- expected: 45m
- stuck: 120m
