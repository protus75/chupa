---
id: declined-box-000351-db4f90d1
kind: declined
link: box-000351-db4f90d1
reopen_after_days: 30
---
After the extension's publisher changed from `chupa` to `chunkydragon` (vscode-marketplace-publish), `./dev.py vscode` installs the new `chunkydragon.vscode-chupa` and leaves the old `chupa.vscode-chupa` installed. Both copies load and their Tickets view '…' menu items merge, so entries such as Bulk Triage appear twice. The suggestion asks the install task to uninstall the old extension id.

The gap is real: `dev.py` lines 146-161 run only `code --install-extension <vsix> --force` and never remove the old publisher's id. But it is leftover state from a one-time rename on an operator's machine, not an ongoing engine defect. One manual `code --uninstall-extension chupa.vscode-chupa` (or Uninstall in the Extensions view) fixes it for good, and no later install can bring the old id back. Adding a permanent uninstall of a retired id to `dev.py` would be migration code that outlives its one use, which the no-compat-shim rule forbids. The harm is a duplicated menu entry in an operator-only tool. No engine run, gate, journal or ticket outcome goes wrong.

- dev.py:146-161: the `vscode` task bumps the patch, packages, and runs `code --install-extension <vsix> --force` with no uninstall step
- vscode-chupa/package.json:6: `"publisher": "chunkydragon"`, so the extension id changed and VS Code treats the old `chupa.vscode-chupa` as a separate extension
- vscode-marketplace-publish is merged; the rename happened once, and the stale copy exists only on machines that installed before it
- Remedy without code: `code --uninstall-extension chupa.vscode-chupa`, run once per affected machine

Message: box-000351-db4f90d1
