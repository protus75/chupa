---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
none

## Context
- dev.py
- tests/integration/test_dev.py
- docs/how-chupa-works.md

## Goal / Why
`./dev.py vscode-package` prints the VSIX's Linux path, but the Marketplace upload runs in a Windows browser whose file picker cannot open `/home/...`. Under WSL the operator had to work out the `\\wsl.localhost\<distro>\...` path by hand to upload `vscode-chupa-0.0.23.vsix` (2026-11-07).

After this change, under WSL, `vscode-package` also prints the VSIX's Windows path, ready to paste into the upload dialog.

## Scope in / Scope out
- In: `dev.py` `vscode-package`: after packaging succeeds and the existing upload line prints, when `WSL_DISTRO_NAME` is set, it runs `wslpath -w <vsix path>` through `subprocess.run` as an argv list with captured text output, and prints `dev: Windows path <wslpath stdout, stripped>`. A non-zero `wslpath` exit stops with a `dev:` message naming `wslpath`. When `WSL_DISTRO_NAME` is unset, nothing beyond today's output prints and `wslpath` is not run. The path comes from `wslpath`, never a string assembled from the distro name, because a repo under `/mnt/c` maps to `C:\...`, not `\\wsl.localhost\...`.
- In: `tests/integration/test_dev.py`: two new tests, faking `dev.subprocess.run` and reading `capsys`:
  - `test_vscode_package_prints_windows_path_under_wsl`;
  - `test_vscode_package_skips_wslpath_outside_wsl`.
- In: `docs/how-chupa-works.md` section 2.2: the `vscode-package` row and the release paragraph below the table say that under WSL it also prints the Windows path to paste into the upload dialog.
- Out:
  - the `vscode` and `publish` commands;
  - copying the VSIX to a Windows folder;
  - version bumps, installs, uploads;
  - `vscode-chupa/`;
  - engine code under `chupa/`.

## Scope fence
- dev.py
- tests/integration/test_dev.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/integration/test_dev.py::test_vscode_package_prints_windows_path_under_wsl` passes: with `WSL_DISTRO_NAME` set and the fake returning `\\wsl.localhost\Distro\repo\dist\vscode-chupa-<version>.vsix` for `["wslpath", "-w", <vsix path>]`, stdout contains the existing upload line and `dev: Windows path ` followed by exactly that stripped value. It rules out a Windows path built from the distro name instead of the `wslpath` output, a missing Windows line, and a call that passes a path other than the packaged VSIX.
2. `tests/integration/test_dev.py::test_vscode_package_skips_wslpath_outside_wsl` passes: with `WSL_DISTRO_NAME` unset, the fake sees no `wslpath` call and stdout has no `Windows path` line, not an attempted `wslpath` that fails off WSL.
3. The `vscode-package` row and release paragraph in `docs/how-chupa-works.md` section 2.2 mention the Windows path under WSL.
4. `./dev.py test` exits 0.

## Verification
```
./dev.py test tests/integration/test_dev.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the Windows path is assembled from `WSL_DISTRO_NAME` or a hard-coded `\\wsl.localhost` prefix instead of `wslpath` output;
- `wslpath` runs when `WSL_DISTRO_NAME` is unset;
- `vscode-package` copies, installs, uploads, or bumps anything.

## Time budget
- expected: 20m
- stuck: 60m
