---
state: confirmed
source: human
priority: P3
kind: feature
---

## Depends on
- observe-verbs-host-extension
- pypi-package

## Context
- vscode-chupa/package.json
- vscode-chupa/extension.js
- dev.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Goal / Why
Hosts get `vscode-chupa` only by building it from a chupa checkout with `./dev.py vscode`. It is to be published to the VS Code Marketplace, unlicensed, so VS Code hosts install it from the Extensions view and receive updates (2026-11-06). Open VSX is out: it refuses an extension without a license (`ovsx` `check-license.js`), and the user wants no license. The extension stays a thin client over the installed `chupa` command (`observe-verbs-host-extension`); it never bundles the engine.

Three things are missing today:
- the manifest has no `repository` and no `extensionKind`;
- there is no listing README;
- there is no publish command.

Without `extensionKind`, VS Code may run the extension on the UI side under WSL or Remote-SSH, away from the repo and the `chupa` command.

After this change, `./dev.py vscode-publish` publishes the current version to the Marketplace.

## Scope in / Scope out
- In: `vscode-chupa/package.json`:
  - `"extensionKind": ["workspace"]`;
  - `"repository": {"type": "git", "url": "https://github.com/protus75/chupa.git"}`;
  - `publisher` stays `chupa`;
  - remove the `license` field: the extension carries no license;
  - the `chupa.command` default becomes `["chupa"]`, the command `uv tool install chupa` puts on PATH. If `extension.js` repeats the default, it changes there too.
- In: `vscode-chupa/README.md`, the Marketplace listing page:
  - what the views show;
  - prerequisites: a repo with `tickets/`, and chupa installed (`uv tool install chupa`);
  - the `chupa.command` setting, with `["chupa"]` as the example for an installed engine;
  - that on WSL or Remote-SSH the extension runs on the remote side.
- In: a new `.vscode/settings.json` sets `"chupa.command": ["uv", "run", "chupa"]` for this repo, which runs the `chupa` console script that `uv sync` installs into `.venv`. This repo needs no wrapper script.
- In: `dev.py` gets a `vscode-publish` subcommand.
  - It refuses with one message that names `VSCE_PAT` when it is unset, before packaging anything.
  - Otherwise it packages once into a temporary directory with `npx --yes @vscode/vsce package --no-dependencies --skip-license -o <vsix>`, then runs `npx --yes @vscode/vsce publish --skip-license --packagePath <vsix>`. vsce reads `VSCE_PAT` from the environment, so the token never appears in argv.
  - It publishes the manifest's current version and never bumps it; the Marketplace refuses a version it already holds.
  - The module docstring's usage lines and `--help` list it.
- In: docs.
  - `docs/how-chupa-works.md` section 2.2: a `vscode-publish` row, plus the one-time setup the user does before the first publish:
    a Marketplace publisher `chupa` and an Azure DevOps PAT with Marketplace Manage scope as `VSCE_PAT`.
  - `docs/host-contract.md`: a host installs the extension from the Marketplace (Cursor and VSCodium: Install from VSIX), and installs chupa with `uv tool install chupa`.
- Out:
  - the `./dev.py vscode` local install path;
  - the extension's views and commands;
  - CI publishing;
  - git tags and pushes;
  - bundling Python or the engine into the VSIX;
  - Open VSX and any license.

## Scope fence
- vscode-chupa/package.json
- vscode-chupa/README.md
- vscode-chupa/extension.js
- .vscode/settings.json
- dev.py
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. `vscode-chupa/package.json` parses as JSON with `extensionKind == ["workspace"]`, a `repository.url` naming `github.com/protus75/chupa`, `publisher == "chupa"`, no `license` key, and `chupa.command` defaulting to `["chupa"]`. `.vscode/settings.json` sets `chupa.command` to `["uv", "run", "chupa"]`. `vscode-chupa/README.md` exists and `vscode-chupa/LICENSE` does not. The first Verification command checks all of this.
2. With `VSCE_PAT` unset, `./dev.py vscode-publish` exits non-zero, its output names `VSCE_PAT`, and it runs no `npx`. The second Verification command checks this.
3. `node --check vscode-chupa/extension.js` exits 0.
4. `docs/how-chupa-works.md` section 2.2 describes `vscode-publish` and its one-time setup, and `docs/host-contract.md` describes installing the extension.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run python -c "import json, pathlib; p = json.load(open('vscode-chupa/package.json')); assert p['extensionKind'] == ['workspace'] and 'github.com/protus75/chupa' in p['repository']['url'] and p['publisher'] == 'chupa' and 'license' not in p and p['contributes']['configuration']['properties']['chupa.command']['default'] == ['chupa']; assert json.load(open('.vscode/settings.json'))['chupa.command'] == ['uv', 'run', 'chupa']; assert pathlib.Path('vscode-chupa/README.md').is_file() and not pathlib.Path('vscode-chupa/LICENSE').exists()"
uv run python -c "import os, subprocess; env = {k: v for k, v in os.environ.items() if k != 'VSCE_PAT'}; r = subprocess.run(['./dev.py', 'vscode-publish'], env=env, capture_output=True, text=True); out = r.stdout + r.stderr; assert r.returncode != 0 and 'VSCE_PAT' in out and 'npx' not in r.stdout, r"
node --check vscode-chupa/extension.js
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- a token is passed in argv;
- `vscode-publish` bumps the version, tags, or pushes;
- the VSIX bundles Python or engine code;
- any license file or `license` field is added, or anything publishes to Open VSX;
- `vscode-chupa/extension.js` changes beyond the `chupa.command` default.

## Time budget
- expected: 30m
- stuck: 90m
