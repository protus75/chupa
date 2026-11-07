---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- stats-command

## Runs before
- status-optional-locks
- soak-report-head-race

## Context
- vscode-chupa/package.json
- vscode-chupa/extension.js
- docs/how-chupa-works.md

## Goal / Why
`chupa stats --json` projects engine health over a window: stage run lengths, cycles per ticket kind, ladder escalations, failures, holds, and spend. The operator watches the engine from the VS Code extension and wants these figures there without a terminal (2026-11-06). The section must stay out of the way: last in the chupa sidebar and collapsed by default.

After this change the chupa sidebar ends with a collapsed **Stats** view. Expanding it shows the `chupa stats` figures for a configurable window.

## Scope in / Scope out
- In: `vscode-chupa/package.json`:
  - a native tree view `chupa.stats` named `Stats`, last in the `chupa` views array, with `"visibility": "collapsed"`;
  - a setting `chupa.statsWindow`: a string, default `7d`, pattern `^[1-9][0-9]*[hdt]$`. Its description says hours, days, or last N settled tickets, as `chupa stats --window` takes it;
  - a `view/title` entry showing `chupa.refresh` when `view == chupa.stats`.
- In: `vscode-chupa/extension.js`: a `StatsTree` data provider, following `StepsTree`.
  - It runs `<root>/.venv/bin/python -m chupa stats --json --window <chupa.statsWindow>` with `execFile`, `cwd` at the root, and a 30-second timeout. It runs only while the Stats view is visible: when the view becomes visible, on `chupa.refresh`, and when the shared `Snapshot` publishes.
  - A run already in flight is not started again, matching `Snapshot.refresh`'s `running`/`again` guard.
  - Changing `chupa.statsWindow` refreshes it.
  - Rendering is generic over the JSON, so new stats keys need no extension change:
    - each top-level key is a collapsed node;
    - an object whose values are all scalars is one leaf: label is its key, description is `k v · k v …`;
    - any other object is a collapsible node of its entries;
    - a `[label, count]` pair list renders one leaf per pair;
    - a scalar is a leaf with the value as description;
    - None renders as `–`.
  - The `window` node's label shows the spec and start time.
  - A failed run shows one leaf with the last stderr line, as `Snapshot` reports errors.
- In: `docs/how-chupa-works.md` section 2.2, the `vscode-chupa/` paragraph: the collapsed Stats view and `chupa.statsWindow`.
- Out: `chupa/stats.py`, `vscode-chupa/snapshot.py`, the other views, the extension version (`./dev.py vscode` bumps it), and new extension commands.

## Scope fence
- vscode-chupa/package.json
- vscode-chupa/extension.js
- docs/how-chupa-works.md

## Acceptance criteria
1. `node --check vscode-chupa/extension.js` exits 0.
2. `vscode-chupa/package.json` parses as JSON. Its last `chupa` view is `chupa.stats` with `"visibility": "collapsed"`, and it declares `chupa.statsWindow` with default `7d`.
3. `docs/how-chupa-works.md` section 2.2 describes the Stats view.
4. `uv run pytest -q` exits 0.

## Verification
```
node --check vscode-chupa/extension.js
uv run python -c "import json; v = json.load(open('vscode-chupa/package.json'))['contributes']; s = v['views']['chupa'][-1]; assert s['id'] == 'chupa.stats' and s['visibility'] == 'collapsed'; assert v['configuration']['properties']['chupa.statsWindow']['default'] == '7d'"
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- the Stats view is not last, or is expanded by default;
- the extension runs `chupa stats` while the Stats view is hidden or collapsed;
- the rendering hard-codes stats key names other than `window`;
- `chupa/` or `snapshot.py` changes.

## Time budget
- expected: 40m
- stuck: 120m
