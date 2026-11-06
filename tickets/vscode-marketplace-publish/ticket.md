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
- dev.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Goal / Why
Hosts get `vscode-chupa` only by building it from a chupa checkout with `./dev.py vscode`. It is to be published to both the VS Code Marketplace and Open VSX, so hosts on VS Code, Cursor or VSCodium install it from their editor's extension view and receive updates (2026-11-06). The extension stays a thin client over the installed `chupa` command (`observe-verbs-host-extension`); it never bundles the engine.

Three things are missing today:
- the manifest has no `repository` and no `extensionKind`;
- there is no listing README or LICENSE file;
- there is no publish command.

Without `extensionKind`, VS Code may run the extension on the UI side under WSL or Remote-SSH, away from the repo and the `chupa` command.

After this change, `./dev.py vscode-publish` publishes the current version to both registries.

## Scope in / Scope out
- In: `vscode-chupa/package.json`:
  - `"extensionKind": ["workspace"]`;
  - `"repository": {"type": "git", "url": "https://github.com/protus75/chupa.git"}`;
  - `publisher` stays `chupa` and `license` stays `MIT`.
- In: `vscode-chupa/README.md`, the Marketplace and Open VSX listing page:
  - what the views show;
  - prerequisites: a repo with `tickets/`, and chupa installed (`uv tool install chupa`);
  - the `chupa.command` setting, with `["chupa"]` as the example for an installed engine;
  - that on WSL or Remote-SSH the extension runs on the remote side.
- In: `vscode-chupa/LICENSE`: MIT, matching the manifest's `license`, with copyright `2026 richard protus`.
- In: `dev.py` gets a `vscode-publish` subcommand.
  - It refuses with one message that names every unset variable among `VSCE_PAT` and `OVSX_PAT`, before packaging anything.
  - Otherwise it packages once into a temporary directory with `npx --yes @vscode/vsce package --no-dependencies -o <vsix>`, then runs `npx --yes @vscode/vsce publish --packagePath <vsix>` and `npx --yes ovsx publish <vsix>`. Both tools read their token from the environment, so tokens never appear in argv.
  - It publishes the manifest's current version and never bumps it; both registries refuse a version they already hold.
  - The module docstring's usage lines and `--help` list it.
- In: docs.
  - `docs/how-chupa-works.md` section 2.2: a `vscode-publish` row, plus the one-time setup the user does before the first publish:
    - a Marketplace publisher `chupa` and an Azure DevOps PAT with Marketplace Manage scope as `VSCE_PAT`;
    - an Open VSX account with the signed publisher agreement, `npx ovsx create-namespace chupa`, and its token as `OVSX_PAT`.
  - `docs/host-contract.md`: a host installs the extension from the Marketplace or Open VSX, and installs chupa with `uv tool install chupa`.
- Out:
  - the `chupa.command` default (an open decision for the user);
  - the `./dev.py vscode` local install path;
  - the extension's views and commands;
  - CI publishing;
  - git tags and pushes;
  - bundling Python or the engine into the VSIX.

## Scope fence
- vscode-chupa/package.json
- vscode-chupa/README.md
- vscode-chupa/LICENSE
- dev.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. `vscode-chupa/package.json` parses as JSON with `extensionKind == ["workspace"]`, a `repository.url` naming `github.com/protus75/chupa`, `publisher == "chupa"` and `license == "MIT"`. `vscode-chupa/README.md` and `vscode-chupa/LICENSE` exist. The first Verification command checks all of this.
2. With `VSCE_PAT` and `OVSX_PAT` unset, `./dev.py vscode-publish` exits non-zero, its output names both variables, and it runs no `npx`. The second Verification command checks this.
3. `node --check vscode-chupa/extension.js` exits 0.
4. `docs/how-chupa-works.md` section 2.2 describes `vscode-publish` and its one-time setup, and `docs/host-contract.md` describes installing the extension.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run python -c "import json, pathlib; p = json.load(open('vscode-chupa/package.json')); assert p['extensionKind'] == ['workspace'] and 'github.com/protus75/chupa' in p['repository']['url'] and p['publisher'] == 'chupa' and p['license'] == 'MIT'; assert pathlib.Path('vscode-chupa/README.md').is_file() and pathlib.Path('vscode-chupa/LICENSE').is_file()"
uv run python -c "import os, subprocess; env = {k: v for k, v in os.environ.items() if k not in ('VSCE_PAT', 'OVSX_PAT')}; r = subprocess.run(['./dev.py', 'vscode-publish'], env=env, capture_output=True, text=True); out = r.stdout + r.stderr; assert r.returncode != 0 and 'VSCE_PAT' in out and 'OVSX_PAT' in out and 'npx' not in r.stdout, r"
node --check vscode-chupa/extension.js
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- a token is passed in argv;
- `vscode-publish` bumps the version, tags, or pushes;
- the VSIX bundles Python or engine code;
- `vscode-chupa/extension.js` changes.

## Time budget
- expected: 30m
- stuck: 90m
