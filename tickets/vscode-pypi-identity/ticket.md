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
- docs/how-chupa-works.md

## Goal / Why
The Marketplace page for `vscode-chupa` (version 0.0.23, seen 2026-11-08) never says it is a VS Code extension for the chupa ticket system published on PyPI at https://pypi.org/project/chupa/, and never says which chupa release it was built against. A visitor cannot tell what "chupa" is or which `uv tool install chupa` version matches the extension.

After this change, the Marketplace description and README name the extension as a VS Code extension for the chupa ticket system with the PyPI link, and every VSIX built by `./dev.py vscode-package` carries a README line naming the chupa version from `pyproject.toml` at packaging time (the engine's version, not the extension's own `package.json` version).

## Scope in / Scope out
- In: `vscode-chupa/package.json` `description`: begins `VS Code extension for the chupa ticket system (https://pypi.org/project/chupa/).` followed by the existing graph sentence.
- In: `vscode-chupa/README.md`: the paragraph under the `# chupa tickets` heading begins by saying this is a VS Code extension for the [chupa](https://pypi.org/project/chupa/) ticket system. Directly below that paragraph, one line of exactly the form `Built for [chupa X.Y.Z](https://pypi.org/project/chupa/X.Y.Z/).` with the current `pyproject.toml` version.
- In: `dev.py` `vscode-package`: before running `vsce`, read `[project] version` from `ROOT / "pyproject.toml"` with `tomllib`, and replace the single README line matching `^Built for \[chupa [^\]]*\]\(https://pypi\.org/project/chupa/[^)]*\)\.$` with that line for the read version. When the README has no such line, stop with a `dev:` message naming `Built for` and do not run `vsce`. Print `dev: built for chupa <version>`. The README edit stays in the working tree; the operator commits it with the release, as with `publish` and `pyproject.toml`.
- In: `tests/integration/test_dev.py`: the `vscode_package` fixture also writes a `pyproject.toml` (`[project]` with `version = "9.8.7"`) and a README containing a stale `Built for` line, so the existing three tests keep passing. Two new tests:
  - `test_vscode_package_stamps_chupa_version`;
  - `test_vscode_package_stops_without_built_for_line`.
- In: `docs/how-chupa-works.md` section 2.2: the `vscode-package` row and the release paragraph below the table say it stamps the chupa version from `pyproject.toml` into the extension README, and the operator commits that README change.
- Out:
  - the `vscode` and `publish` commands;
  - `vscode-chupa/extension.js` and any runtime check of the installed chupa version;
  - bumping either version;
  - engine code under `chupa/`.

## Scope fence
- dev.py
- tests/integration/test_dev.py
- vscode-chupa/package.json
- vscode-chupa/README.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/integration/test_dev.py::test_vscode_package_stamps_chupa_version` passes: with the fixture's `pyproject.toml` at `9.8.7` and a README holding `Built for [chupa 0.0.1](https://pypi.org/project/chupa/0.0.1/).`, after `dev.main()` the README contains `Built for [chupa 9.8.7](https://pypi.org/project/chupa/9.8.7/).`, no longer contains `0.0.1`, keeps its other lines unchanged, stdout contains `dev: built for chupa 9.8.7`, and the README was rewritten before the `vsce` call (the fake `subprocess.run` reads the README when it sees the `npx` argv). It rules out stamping the `package.json` version `1.2.3`, stamping after packaging, and dropping other README lines.
2. `tests/integration/test_dev.py::test_vscode_package_stops_without_built_for_line` passes: with a README lacking the `Built for` line, `dev.main()` raises `SystemExit` whose message contains `Built for`, and the fake `subprocess.run` is never called. It rules out packaging a VSIX with no chupa version and silently appending a line.
3. The existing `tests/integration/test_dev.py` tests `test_vscode_package_prints_windows_path_under_wsl`, `test_vscode_package_skips_wslpath_outside_wsl`, and `test_vscode_package_stops_when_wslpath_fails` pass with their assertions unchanged; only the shared fixture gains the `pyproject.toml` and README files.
4. `vscode-chupa/package.json` `description` contains `https://pypi.org/project/chupa/`, and `vscode-chupa/README.md` contains `https://pypi.org/project/chupa/` in its first paragraph and one `Built for [chupa` line naming the current `pyproject.toml` version.
5. The `vscode-package` row and release paragraph in `docs/how-chupa-works.md` section 2.2 mention stamping the chupa version into the README.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_dev.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the stamped version comes from `vscode-chupa/package.json` instead of `pyproject.toml`;
- `vscode-package` appends a `Built for` line when none exists instead of stopping;
- `vscode-package` bumps a version, installs, or uploads;
- `vscode-chupa/extension.js` changes.

## Time budget
- expected: 25m
- stuck: 75m
