---
state: confirmed
source: human
priority: P0
kind: chore
---

## Depends on
- none

## Context
- vscode-chupa/package.json
- vscode-chupa/media/marketplace-icon.png
- vscode-chupa/media/icon.svg

## Goal / Why
The Marketplace listing and the Extensions view show a generic placeholder tile for chupa tickets because `vscode-chupa/package.json` has no top-level `icon`. The existing `media/icon.svg` is the Activity Bar icon only, and the Marketplace requires a PNG of at least 128×128 for the listing icon. After this change, the listing shows `vscode-chupa/media/marketplace-icon.png`, a PNG export of `media/icon.svg` that the owner commits.

## Scope in / Scope out
- In: add a top-level `"icon": "media/marketplace-icon.png"` to `vscode-chupa/package.json`, directly after the `"publisher"` line, keeping the file's tab indentation. `media/**` is already in `"files"`, so the PNG ships in the VSIX as vsce requires.
- Out: the PNG itself, `media/icon.svg`, the Activity Bar `viewsContainers` icon, `galleryBanner`, `vscode-chupa/README.md`, and `dev.py`.

## Scope fence
- vscode-chupa/package.json

## Acceptance criteria
1. `vscode-chupa/package.json` parses as JSON and its top-level `icon` is exactly `media/marketplace-icon.png`, checked by reading the file.
2. No other key in `vscode-chupa/package.json` changes, checked by the branch diff.
3. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- any file other than `vscode-chupa/package.json` changes;
- the `icon` value names an SVG or a path outside `media/`;
- the `viewsContainers` icon `media/icon.svg` changes.

## Time budget
- expected: 5m
- stuck: 20m
