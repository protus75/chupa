---
state: confirmed
source: human
priority: P3
kind: feature
---

## Depends on
- observe-verbs-host-extension

## Context
- vscode-chupa/package.json
- vscode-chupa/extension.js
- chupa/__main__.py
- docs/how-chupa-works.md

## Goal / Why
The Tickets view's `…` menu in `vscode-chupa` has Drain, "Stop after the running ticket", "Kill the drain", and Status. It cannot start `serve`. "Kill the drain" is mislabeled: `chupa kill` stops whichever engine is running, drain or serve. VS Code shows no hover text on `…` menu items, so nothing explains what each one does (2026-11-06).

After this change, one "Engine…" button in the Tickets view title opens a QuickPick with six actions. Each has a one-line description shown under its name:
- Drain
- Serve
- Stop after the running ticket
- Kill (drain or serve)
- Status
- Retro (run now)

## Scope in / Scope out
- In: `vscode-chupa/package.json`.
  - Remove the `chupa.drain`, `chupa.stop`, `chupa.kill`, and `chupa.status` commands and their `view/title` entries.
  - Add a `chupa.engine` command titled "Engine…" with icon `$(server-process)`, in the Tickets `view/title` `navigation` group beside Refresh and Settings.
- In: `vscode-chupa/extension.js`. `chupa.engine` shows `vscode.window.showQuickPick` with one item per action:
  - `label`: the action name above;
  - `detail`: its description, taken from the `chupa` verb's help in `chupa/__main__.py` and section 2.1 of `docs/how-chupa-works.md`;
    - drain: run every eligible ticket to quiescence, then exit;
    - serve: run the continuous daemon until kill, stop, or a signal;
    - stop: finish the running ticket, admit nothing new, then exit;
    - kill: hard-stop the running drain or serve;
    - status: print the journal projection;
    - retro: run a retro report now (`chupa retro`), whatever the automatic triggers say.
- In: a sixth picker item, "Retro (run now)", runs `retro`.
- In: an "Open config.yaml" icon (`$(file-code)`, command `chupa.openConfig`) beside Settings in the Tickets `view/title` `navigation` group. It opens the repo's `config.yaml` in an editor. Retry caps, model mappings, and the `retro:` triggers live there; the extension keeps no copy of them.
- In: picking an item runs `<chupa.command> <verb>` through the same interactive-action path that `observe-verbs-host-extension` uses for engine actions. Escape does nothing.
- In: one start/stop icon in the Tickets `view/title` `navigation` group that follows the engine's state.
  - On every snapshot, `extension.js` sets the context key `chupa.engineRunning` with `setContext`, from the snapshot's engine flag.
  - New setting `chupa.playAction`: enum `drain` | `serve`, default `drain`, with one `enumDescriptions` line per value.
  - Two commands with icon `$(play)`, so the hover text names the real action:
    - `chupa.playDrain`, titled "Start drain", shown when `!chupa.engineRunning && config.chupa.playAction == 'drain'`;
    - `chupa.playServe`, titled "Start serve", shown when `!chupa.engineRunning && config.chupa.playAction == 'serve'`.
  - `chupa.stopRunning`, icon `$(debug-stop)`, titled "Stop after the running ticket", shown when `chupa.engineRunning`.
  - These three run `drain`, `serve`, and `stop` through the same path as the picker.
  - All five new commands are hidden from the command palette.
- Out: `pause` and `resume`, a Kill icon (Kill stays in the picker only), the right-click ticket menu, and every engine verb.

## Scope fence
- vscode-chupa/package.json
- vscode-chupa/extension.js

## Acceptance criteria
1. `node --check vscode-chupa/extension.js` exits 0.
2. `vscode-chupa/package.json` parses as JSON. It declares `chupa.engine`, `chupa.playDrain`, `chupa.playServe`, `chupa.stopRunning`, and `chupa.openConfig` in the `view/title` menu, and the `chupa.playAction` setting. It no longer declares `chupa.drain`, `chupa.stop`, `chupa.kill`, or `chupa.status`.
3. `grep -c "serve" vscode-chupa/extension.js` prints at least 1.
4. `uv run pytest -q` exits 0.

## Verification
```
node --check vscode-chupa/extension.js
uv run python -c "import json; c=json.load(open('vscode-chupa/package.json'))['contributes']; ids={x['command'] for x in c['commands']}; new={'chupa.engine','chupa.playDrain','chupa.playServe','chupa.stopRunning','chupa.openConfig'}; assert new <= ids and not ids & {'chupa.drain','chupa.stop','chupa.kill','chupa.status'}; assert new <= {m['command'] for m in c['menus']['view/title']}; assert 'chupa.playAction' in c['configuration']['properties']"
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- an action runs a shell string or `./dev.py`;
- an action lacks its description;
- Pause or Resume is added;
- any file outside the fence changes.

## Time budget
- expected: 20m
- stuck: 60m
