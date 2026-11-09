---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Runs before
- vscode-command-not-found

## Context
- vscode-chupa/package.json
- vscode-chupa/README.md
- .vscode/settings.json
- README.md
- docs/host-contract.md#Host contract
- docs/host-contract.md#VS Code extension
- docs/host-contract.md#Instance custody
- docs/host-running.md#Running chupa on a host
- docs/how-chupa-works.md#2. Commands

## Goal / Why
Hosts install chupa from PyPI as a dev dependency of the host project (fungo's `pyproject.toml` has `"chupa>=0.1.2"` in `[dependency-groups] dev`), so the executable is `<host>/.venv/bin/chupa`. The docs say something else in several places. `README.md`, `docs/how-chupa-works.md` section 2, `docs/host-contract.md` (`## VS Code extension`, `## Instance custody`), and `vscode-chupa/README.md` each say `uv tool install chupa`, and `docs/host-running.md` runs chupa from a separate checkout through `CHUPA_CHECKOUT`. The `chupa.command` default `["chupa"]` works only when that venv is on VS Code's PATH, which a VS Code started from a desktop launcher does not have.

After this change:
- the `chupa.command` default is `[".venv/bin/chupa"]`; `execFile` and `ProcessExecution` already run with `cwd` set to the workspace root, and node resolves a relative path containing `/` against `cwd` (checked 2026-11-08: from `cwd` `/home/djp/source/fungo`, `.venv/bin/chupa --help` printed usage);
- one section, `## Install` in `docs/host-contract.md`, states the install model, and every other doc links to it instead of restating it.

Why: every doc that restated the install drifted the same wrong way, and the default fails on a native-Linux VS Code.

## Scope in / Scope out
- In: `vscode-chupa/package.json`: `chupa.command` `default` becomes `[".venv/bin/chupa"]`; its `description` says the default is the host's `.venv/bin/chupa`, resolved from the workspace folder.
- In: `docs/host-contract.md`: new `## Install` section directly after the intro paragraph, before `## Copyable configuration`. It says: add chupa to the host project as a dev dependency (`uv add --dev chupa`, pinned as `chupa==<version>` when a specific release is wanted), run `uv sync`, and the executable is `.venv/bin/chupa`; run verbs as `uv run chupa <verb>`. It also says the native Windows venv layout (`.venv\Scripts\chupa.exe`) needs `chupa.command` set explicitly. This is the only place in the repo that states how to install chupa.
- In: `docs/host-contract.md` `## VS Code extension`: drop the `uv tool install chupa` clause and link to `## Install`; say the `chupa.command` default is `[".venv/bin/chupa"]`, resolved relative to the workspace folder.
- In: `docs/host-contract.md` `## Instance custody`: replace `installed with \`uv tool install chupa==<version>\`` with a link to `## Install` (stable is a PyPI release pinned as a host dev dependency); "reinstalling the desired version" becomes "changing the pin, running `uv sync`".
- In: `docs/host-running.md`: the code block becomes `uv run chupa doctor` and `uv run chupa serve`; the intro sentence links to `host-contract.md#install` instead of describing `CHUPA_CHECKOUT`; "Use the same prefix" stays true for `uv run chupa`.
- In: `README.md`: the install line links to `docs/host-contract.md#install` instead of saying `uv tool install chupa`.
- In: `docs/how-chupa-works.md` section 2: the first sentence links to `host-contract.md#install` instead of saying `uv tool install chupa`; the checkout sentence (`uv run python -m chupa <verb>`) and the `./dev.py` sentence stay.
- In: `vscode-chupa/README.md` `## Prerequisites`: link to the `## Install` section of the host contract (absolute GitHub URL `https://github.com/protus75/chupa/blob/main/docs/host-contract.md#install`, since the Marketplace page renders this README); say the default `chupa.command` is `[".venv/bin/chupa"]` and when to override it.
- In: delete `.vscode/settings.json`; its only key is `"chupa.command": ["uv", "run", "chupa"]`, which the new default makes unnecessary because this repo's `.venv/bin/chupa` exists after `uv sync`.
- Out:
  - `vscode-chupa/extension.js` and `vscode-chupa/media/`; the missing-command error message is `vscode-command-not-found`;
  - `dev.py`;
  - engine code under `chupa/`;
  - `CHUPA_PLAN.md`;
  - bumping the extension or chupa version.

## Scope fence
- vscode-chupa/package.json
- vscode-chupa/README.md
- docs/host-contract.md
- docs/host-running.md
- docs/how-chupa-works.md
- README.md
- .vscode/settings.json

## Acceptance criteria
1. `vscode-chupa/package.json` `contributes.configuration.properties["chupa.command"].default` is exactly `[".venv/bin/chupa"]`, not `["chupa"]`.
2. `git grep -n "uv tool install" -- README.md docs vscode-chupa` prints nothing: no doc restates the old install (`CHUPA_PLAN.md` is frozen and keeps its text).
3. `git grep -n "CHUPA_CHECKOUT" -- docs README.md` prints nothing.
4. `docs/host-contract.md` has exactly one `## Install` heading, placed before `## Copyable configuration`, and it contains `uv add --dev chupa`, `.venv/bin/chupa`, and `uv run chupa`.
5. `README.md`, `docs/how-chupa-works.md`, `docs/host-running.md`, and `vscode-chupa/README.md` each contain a link whose target ends in `host-contract.md#install`.
6. `git grep -n "uv add --dev chupa" -- README.md docs vscode-chupa` matches only `docs/host-contract.md`.
7. `.vscode/settings.json` does not exist.
8. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- `vscode-chupa/extension.js` changes;
- the default is an absolute path, or the extension resolves the path itself instead of relying on `cwd`;
- a doc other than `docs/host-contract.md` states the install steps instead of linking;
- `CHUPA_PLAN.md` changes.

## Time budget
- expected: 20m
- stuck: 60m
