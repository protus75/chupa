---
state: confirmed
source: human
priority: P2
kind: chore
---

## Depends on
- none

## Context
- vscode-chupa/README.md
- vscode-chupa/images/ChupaExt.png
- vscode-chupa/package.json

## Goal / Why
The Marketplace listing renders `vscode-chupa/README.md`, and today it has no picture of the extension, so a visitor cannot see what the views look like before installing. After this change, the README shows the screenshot `vscode-chupa/images/ChupaExt.png` (Details, Recent Steps, and Tickets views with the ticket context menu open).

## Scope in / Scope out
- In: add one markdown image line to `vscode-chupa/README.md`, directly after the first paragraph under `# chupa tickets` and before the `Built for` line, separated by blank lines:
  `![chupa tickets views in VS Code](https://github.com/protus75/chupa/raw/HEAD/vscode-chupa/images/ChupaExt.png)`
  The target is an absolute `https://` URL because the extension lives in a repo subfolder and vsce may rewrite a relative image path against the repo root.
- Out: the image file itself, `vscode-chupa/package.json` (`files` already excludes `images/`, so the PNG stays out of the VSIX), a Marketplace `icon`, `galleryBanner`, and `dev.py`.

## Scope fence
- vscode-chupa/README.md

## Acceptance criteria
1. `vscode-chupa/README.md` contains exactly one image, the line given in Scope in, placed after the first paragraph and before the `Built for` line.
2. The `Built for [chupa X](https://pypi.org/project/chupa/X/).` line is unchanged and still occurs exactly once, so `./dev.py vscode-package` can still stamp it.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any file other than `vscode-chupa/README.md` changes;
- the image target is a relative path;
- the `Built for` line changes or is duplicated.

## Time budget
- expected: 5m
- stuck: 20m
