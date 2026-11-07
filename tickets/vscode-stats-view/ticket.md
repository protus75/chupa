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
- tests-split

## Context
- vscode-chupa/package.json
- vscode-chupa/extension.js
- chupa/stats.py
- chupa/__main__.py
- tests/test_stats.py
- docs/how-chupa-works.md

## Goal / Why
`chupa stats --json` projects engine health over a window: stage run lengths, cycles per ticket kind, ladder escalations, failures, holds, and spend. The operator watches the engine from the VS Code extension and wants these figures there without a terminal (2026-11-06). The section must stay out of the way: last in the chupa sidebar and collapsed by default.

After this change the chupa sidebar ends with a collapsed **Stats** view. Expanding it shows the `chupa stats` figures for a configurable window.

## Scope in / Scope out
- In: `vscode-chupa/package.json`:
  - a native tree view `chupa.stats` named `Stats`, last in the `chupa` views array, with `"visibility": "collapsed"`;
  - a setting `chupa.statsWindow`: a string, default `7d`, pattern `^[1-9][0-9]*[hdt]$`. Its description says hours, days, or last N settled tickets, as `chupa stats --window` takes it;
  - a `view/title` entry showing `chupa.refresh` when `view == chupa.stats`.
- In: `chupa/stats.py`: a pure `stats_tree(stats)` that turns `project_stats` output into display rows `{"label", "description", "children"}`. It is generic over the keys, so a new stats key needs no extension change:
  - each top-level key is a row with children;
  - an object whose values are all scalars is one leaf: label is its key, description is `k v · k v …`;
  - any other object is a row whose children are its entries;
  - a `[label, count]` pair list gives one leaf per pair;
  - a scalar is a leaf with the value as description;
  - `None` renders as `–`;
  - the `window` row's label shows the spec and start time.
- In: `chupa/__main__.py`: `chupa stats --tree` prints `stats_tree` of the projection as JSON. `--json` and the text output are unchanged.
- In: `tests/test_stats.py`: `stats_tree` tests covering each rule above, and one test that `chupa stats --tree` prints the rows as JSON.
- In: `vscode-chupa/extension.js`: a `StatsTree` data provider, following `StepsTree`, that only draws the rows it receives.
  - It runs `runData(root, ['stats', '--tree', '--window', <chupa.statsWindow>], { timeout: 30000 }, ...)`, matching `Snapshot.refresh`. It runs only while the Stats view is visible: when the view becomes visible, on `chupa.refresh`, and when the shared `Snapshot` publishes.
  - A run already in flight is not started again, matching `Snapshot.refresh`'s `running`/`again` guard.
  - Changing `chupa.statsWindow` refreshes it.
  - A row with children is a collapsed node; a row without children is a leaf. Label and description are drawn as given.
  - A failed run shows one leaf with the last stderr line, as `Snapshot` reports errors.
- In: `docs/how-chupa-works.md` section 2.2, the `vscode-chupa/` paragraph: the collapsed Stats view and `chupa.statsWindow`.
- In: `docs/how-chupa-works.md` section 2.1: the `stats` verb row lists `--tree`. `./dev.py stats` does not gain `--tree`; only the extension uses it.
- Out: `project_stats` and `render_stats` behavior, `vscode-chupa/snapshot.py`, the other views, the extension version (`./dev.py vscode` bumps it), and new extension commands.

## Scope fence
- vscode-chupa/package.json
- vscode-chupa/extension.js
- chupa/stats.py
- chupa/__main__.py
- tests/test_stats.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `node --check vscode-chupa/extension.js` exits 0.
2. `vscode-chupa/package.json` parses as JSON. Its last `chupa` view is `chupa.stats` with `"visibility": "collapsed"`, and it declares `chupa.statsWindow` with default `7d`.
3. `docs/how-chupa-works.md` section 2.2 describes the Stats view, and the section 2.1 `stats` row lists `--tree`.
4. `./dev.py test tests/test_stats.py` exits 0, including the new `stats_tree` and `--tree` tests.
5. `./dev.py test` exits 0.

## Verification
```
node --check vscode-chupa/extension.js
uv run python -c "import json; v = json.load(open('vscode-chupa/package.json'))['contributes']; s = v['views']['chupa'][-1]; assert s['id'] == 'chupa.stats' and s['visibility'] == 'collapsed'; assert v['configuration']['properties']['chupa.statsWindow']['default'] == '7d'"
./dev.py test tests/test_stats.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the Stats view is not last, or is expanded by default;
- the extension runs `chupa stats` while the Stats view is hidden or collapsed;
- `stats_tree` hard-codes stats key names other than `window`;
- `extension.js` inspects value types, formats descriptions, or builds labels instead of drawing the rows it receives;
- `project_stats`, `render_stats`, or `snapshot.py` changes.

## Time budget
- expected: 40m
- stuck: 120m
