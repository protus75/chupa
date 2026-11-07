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
Hosts get `vscode-chupa` only by building it from a chupa checkout with `./dev.py vscode`. It is to be published to the VS Code Marketplace under its existing proprietary license (`vscode-chupa/LICENSE`), so VS Code hosts install it from the Extensions view and receive updates (2026-11-06). Open VSX is out of scope. The extension stays a thin client over the installed `chupa` command (`observe-verbs-host-extension`); it never bundles the engine.

Three things are missing today:
- the manifest has no `repository` and no `extensionKind`;
- there is no listing README;
- there is no command that builds a release `.vsix`.

Without `extensionKind`, VS Code may run the extension on the UI side under WSL or Remote-SSH, away from the repo and the `chupa` command.

Publishing is a manual browser upload on the Marketplace management page, which signs in with the user's Microsoft account. Azure DevOps global PATs, which `vsce publish` uses from a local machine, retire on 2026-12-01 (VS Code publishing docs), so nothing here uses a token.

After this change, `./dev.py vscode-package` builds the current version's `.vsix` and prints where to upload it.

## Scope in / Scope out
- In: `vscode-chupa/package.json`:
  - `"extensionKind": ["workspace"]`;
  - `"repository": {"type": "git", "url": "https://github.com/protus75/chupa.git"}`;
  - `publisher` becomes `chunkydragon`, the registered Marketplace publisher ID (`chupa` was taken), so the extension ID becomes `chunkydragon.vscode-chupa`;
  - keep the `license` field and `vscode-chupa/LICENSE` unchanged;
  - the `chupa.command` default becomes `["chupa"]`, the command `uv tool install chupa` puts on PATH. If `extension.js` repeats the default, it changes there too.
  - `extension.js`'s `chupa.openSettings` filter `@ext:chupa.vscode-chupa` becomes `@ext:chunkydragon.vscode-chupa`.
- In: `vscode-chupa/README.md`, the Marketplace listing page:
  - what the views show;
  - prerequisites: a repo with `tickets/`, and chupa installed (`uv tool install chupa`);
  - the `chupa.command` setting, with `["chupa"]` as the example for an installed engine;
  - that on WSL or Remote-SSH the extension runs on the remote side.
- In: a new `.vscode/settings.json` sets `"chupa.command": ["uv", "run", "chupa"]` for this repo, which runs the `chupa` console script that `uv sync` installs into `.venv`. This repo needs no wrapper script.
- In: `dev.py` gets a `vscode-package` subcommand.
  - It runs `npx --yes @vscode/vsce package --no-dependencies -o dist/vscode-chupa-<version>.vsix` (cwd `vscode-chupa/`, output path absolute under the repo root's `dist/`).
  - Then it prints that path and `https://marketplace.visualstudio.com/manage/publishers/chunkydragon`.
  - It packages the manifest's current version and never bumps it; the Marketplace refuses a version it already holds.
  - It installs nothing and publishes nothing.
  - The module docstring's usage lines and `--help` list it.
- In: `.gitignore` gains `dist/`.
- In: docs.
  - `docs/how-chupa-works.md` section 2.2: a `vscode-package` row, and how to release a version:
    - bump `version` in `vscode-chupa/package.json`;
    - run `./dev.py vscode-package`;
    - upload the printed `.vsix` on the `chunkydragon` management page: New extension the first time, the extension's Update action after that.
  - `docs/host-contract.md`: a host installs the extension from the Marketplace (Cursor and VSCodium: Install from VSIX), and installs chupa with `uv tool install chupa`. The VS Code extension paragraph's `chupa.command` default reads `["chupa"]`.
- Out:
  - the `./dev.py vscode` local install path;
  - the extension's views and commands;
  - `vsce publish`, tokens, and CI publishing;
  - git tags and pushes;
  - bundling Python or the engine into the VSIX;
  - Open VSX;
  - any change to `vscode-chupa/LICENSE`, the repo-root `LICENSE`, or the manifest `license` field.

## Scope fence
- vscode-chupa/package.json
- vscode-chupa/README.md
- vscode-chupa/extension.js
- .vscode/settings.json
- dev.py
- .gitignore
- docs/how-chupa-works.md
- docs/host-contract.md

## Acceptance criteria
1. `vscode-chupa/package.json` parses as JSON with `extensionKind == ["workspace"]`, a `repository.url` naming `github.com/protus75/chupa`, `publisher == "chunkydragon"`, `license == "SEE LICENSE IN LICENSE"`, and `chupa.command` defaulting to `["chupa"]`. `.vscode/settings.json` sets `chupa.command` to `["uv", "run", "chupa"]`. `vscode-chupa/README.md` and `vscode-chupa/LICENSE` exist. The first Verification command checks all of this.
2. `./dev.py --help` lists `vscode-package`, `dev.py` contains no `VSCE_PAT`, and `.gitignore` lists `dist/`. The second Verification command checks this.
3. `node --check vscode-chupa/extension.js` exits 0.
4. `docs/how-chupa-works.md` section 2.2 describes `vscode-package` and the upload steps, and `docs/host-contract.md` describes installing the extension.
5. `./dev.py test` exits 0.

## Verification
```
uv run python -c "import json, pathlib; p = json.load(open('vscode-chupa/package.json')); assert p['extensionKind'] == ['workspace'] and 'github.com/protus75/chupa' in p['repository']['url'] and p['publisher'] == 'chunkydragon' and p['license'] == 'SEE LICENSE IN LICENSE' and p['contributes']['configuration']['properties']['chupa.command']['default'] == ['chupa']; assert json.load(open('.vscode/settings.json'))['chupa.command'] == ['uv', 'run', 'chupa']; assert pathlib.Path('vscode-chupa/README.md').is_file() and pathlib.Path('vscode-chupa/LICENSE').is_file()"
uv run python -c "import subprocess, pathlib; h = subprocess.run(['./dev.py', '--help'], capture_output=True, text=True, check=True).stdout; assert 'vscode-package' in h, h; s = pathlib.Path('dev.py').read_text(); assert 'VSCE_PAT' not in s; assert 'dist/' in pathlib.Path('.gitignore').read_text().split()"
node --check vscode-chupa/extension.js
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- anything uses a token or runs `vsce publish`;
- `vscode-package` bumps the version, installs, tags, or pushes;
- the VSIX bundles Python or engine code;
- a license file or the manifest `license` field changes or is removed, or anything publishes to Open VSX;
- `vscode-chupa/extension.js` changes beyond the `chupa.command` default and the `@ext:` settings filter.

## Time budget
- expected: 30m
- stuck: 90m
