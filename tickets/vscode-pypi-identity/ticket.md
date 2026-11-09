---
state: draft
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- dev.py
- tests/integration/test_dev.py
- vscode-chupa/package.json
- vscode-chupa/README.md
- docs/how-chupa-works.md#2.2

## Goal / Why
The Marketplace page for `vscode-chupa` (0.0.23, seen 2026-11-08) shows the manifest `description` and `vscode-chupa/README.md`. Neither says the extension is a VS Code extension for the chupa ticket system published at https://pypi.org/project/chupa/, and neither names the chupa release the extension was built against. A visitor cannot tell what chupa is or which `uv tool install chupa` version matches.

After this change, the description and README name the extension as a VS Code extension for the chupa ticket system with the PyPI link. Every VSIX that `./dev.py vscode-package` builds carries a README line naming the `[project] version` from `pyproject.toml` at packaging time: the engine's version, not the extension's own `package.json` version.

## Scope in / Scope out
- In: `vscode-chupa/package.json` `description` becomes `VS Code extension for the chupa ticket system (https://pypi.org/project/chupa/): tickets as an SCM-style dependency graph: blocked, queued, running, merged.`
- In: `vscode-chupa/README.md`: the first paragraph under `# chupa tickets` begins `A VS Code extension for the [chupa](https://pypi.org/project/chupa/) ticket system.` followed by the existing sentences. Directly below that paragraph, a paragraph that is exactly the line `Built for [chupa X.Y.Z](https://pypi.org/project/chupa/X.Y.Z/).`, where `X.Y.Z` is the `[project] version` in `pyproject.toml` when the ticket is implemented.
- In: `dev.py` `vscode-package` branch: before the `vsce` call, read `[project] version` from `ROOT / "pyproject.toml"` with `tomllib`. Replace the one README line matching `^Built for \[chupa [^\]]*\]\(https://pypi\.org/project/chupa/[^/)]*/\)\.$` (multiline) with the line for that version, and print `dev: built for chupa <version>`. When no line matches, exit with a message that starts with `dev:` and contains `Built for`, without calling `subprocess.run`. The rewritten README stays uncommitted for the operator to commit with the release, as `publish` leaves `pyproject.toml`.
- In: `tests/integration/test_dev.py`: the `vscode_package` fixture also writes `pyproject.toml` (`[project]` with `version = "9.8.7"`) and `vscode-chupa/README.md` holding `# chupa tickets`, a blank line, `Built for [chupa 0.0.1](https://pypi.org/project/chupa/0.0.1/).`, a blank line, and `tail`. The three existing `vscode-package` tests keep their assertions. Two new tests: `test_vscode_package_stamps_chupa_version` and `test_vscode_package_stops_without_built_for_line`.
- In: `docs/how-chupa-works.md` section 2.2: the `vscode-package` table row and the release paragraph below the table say that it writes the `pyproject.toml` chupa version into the `Built for` line of `vscode-chupa/README.md` before packaging, and that the operator commits that README change.
- Out:
  - the `vscode` and `publish` branches of `dev.py`;
  - `vscode-chupa/extension.js`, `vscode-chupa/media/`, and any runtime check of the installed chupa version;
  - bumping the extension or chupa version;
  - engine code under `chupa/`.

## Scope fence
- dev.py
- tests/integration/test_dev.py
- vscode-chupa/package.json
- vscode-chupa/README.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_dev.py` runs `test_vscode_package_stamps_chupa_version`, which passes. Its fake `subprocess.run` records the README text when it receives the `npx` argv. After `dev.main()`, that recorded text and the final README both equal the fixture README with the `Built for` line replaced by `Built for [chupa 9.8.7](https://pypi.org/project/chupa/9.8.7/).`, and stdout contains `dev: built for chupa 9.8.7`. It rules out stamping the `package.json` version `1.2.3`, stamping after packaging, a README left at `0.0.1`, and lost `# chupa tickets` or `tail` lines.
2. `./dev.py test tests/integration/test_dev.py` runs `test_vscode_package_stops_without_built_for_line`, which passes. Its README has no `Built for` line, `dev.main()` raises `SystemExit` whose message contains `Built for`, the fake `subprocess.run` has no calls, and the README is unchanged. It rules out packaging a VSIX with no chupa version and appending a line silently.
3. `./dev.py test tests/integration/test_dev.py` passes `test_vscode_package_prints_windows_path_under_wsl`, `test_vscode_package_skips_wslpath_outside_wsl`, and `test_vscode_package_stops_when_wslpath_fails` with their assertions unchanged.
4. `vscode-chupa/package.json` `description` contains `https://pypi.org/project/chupa/`. `vscode-chupa/README.md` has `https://pypi.org/project/chupa/` in its first paragraph and exactly one `Built for [chupa` line, naming the `pyproject.toml` version.
5. The `vscode-package` row and the release paragraph in section 2.2 of `docs/how-chupa-works.md` mention writing the chupa version into the `Built for` line of `vscode-chupa/README.md`.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_dev.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the written version comes from `vscode-chupa/package.json` instead of `pyproject.toml`;
- `vscode-package` appends a `Built for` line when none exists instead of stopping;
- `vscode-package` bumps a version, installs, uploads, or commits;
- `vscode-chupa/extension.js` or `vscode-chupa/media/` changes.

## Time budget
- expected: 25m
- stuck: 75m
