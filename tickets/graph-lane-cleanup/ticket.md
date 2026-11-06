---
state: confirmed
source: human
priority: P3
kind: bug
---

## Depends on
none

## Context
- vscode-chupa/snapshot.py
- vscode-chupa/media/view.js
- vscode-chupa/media/graph.js
- docs/how-chupa-works.md
- tests/test_watch.py

## Goal / Why
The Tickets view graph draws badly on the live queue (2026-11-06; `evidence/lanes.txt`):
- Blocked `vscode-marketplace-publish` depends on queued `observe-verbs-host-extension`. That edge opens a lane in lane 0 above the queue, so the queue starts in lane 1 and jumps back to lane 0 at `observe-verbs-host-extension`.
- Queued `specs-module-into-package` and `spec-path-matchers` both depend on running `specs-move`, and each opens its own lane: two parallel lanes run 10 rows to one dot.
- Queued rows set no `branchColor`, so those lanes take the SCM rotation colors.

The root cause is where the logic lives. `view.js` chooses graph edges (unmerged filter, transitive reduction, lane order) and `graph.js` allocates lanes, all in JavaScript with no tests. The extension must be a thin drawing wrapper; all logic belongs in the `chupa` package under pytest.

After this change `chupa/graph.py` computes the whole layout, `snapshot.py` ships it in each row, and the extension only draws it.

## Scope in / Scope out
- In: new `chupa/graph.py` with `layout(rows: list[dict]) -> list[dict]`. Input: snapshot rows top first, each with `stem`, `section`, `depends`. Output: one dict per row, `{"kind": "head" | "node", "parents": [stem, ...], "lanesIn": [lane, ...], "lanesOut": [lane, ...]}`, where a lane is `{"id": stem | None, "section": section | None}` (`None` id: a held-open gap). It is pure: no I/O, no clock.
  - Edges: port `view.js` `render`'s item building (unmerged filter, transitive reduction, lane order, the row below as first parent), with these fixes: a blocked row's parents are only its blocked dependencies; every lane's `section` is the section of the row that opened it. There is no rotation palette.
  - Lanes: port `graph.js` `toViewModels`, with this fix: a non-first parent that already has a lane in this row's `lanesOut` joins that lane instead of opening another.
- In: `snapshot.py` sets `row["graph"]` from `layout(rows)` after its final `depends` filter.
- In: `view.js` and `graph.js` keep only drawing: `renderGraph` draws from `row.graph`, mapping a lane's `section` to the existing `COLOR` CSS variables. Delete `toViewModels`, `LANE_COLORS`, and the edge code in `render`.
- In: `tests/test_graph.py` covers each fix and the ported behavior. Copy `evidence/regress_graph_lanes.py` to `tests/regress_graph_lanes.py` unchanged; it reports `defect` on the base commit and `pass` at head.
- In: the `Pure Python` rule's extension exception in `CLAUDE.md` and `AGENTS.md` gains: "The extension is a thin drawing wrapper: all logic, layout included, lives in Python." `docs/how-chupa-works.md` says the layout comes from `chupa/graph.py`.
- Out: `extension.js`, `detail.js`, `view.css`, `package.json`, the status text, row order, dot colors, and any other logic still in the extension.
- Touch no file outside `## Scope fence`.

## Scope fence
- chupa/graph.py
- vscode-chupa/snapshot.py
- vscode-chupa/media/view.js
- vscode-chupa/media/graph.js
- tests/test_graph.py
- tests/regress_graph_lanes.py
- CLAUDE.md
- AGENTS.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/regress_graph_lanes.py` reports `pass`: dependents of one ticket share a lane, a blocked row with only queued dependencies has no parents, and every lane carries a ticket section.
2. `tests/test_graph.py` covers each of those three fixes plus first-parent order and transitive reduction.
3. `vscode-chupa/media/graph.js` and `vscode-chupa/media/view.js` contain no `toViewModels`, `LANE_COLORS`, or `reachable`; the fifth Verification command checks it.
4. `node --check` passes for both JavaScript files.
5. `uv run pytest -q` exits 0.

## Verification
```
uv run python tests/regress_graph_lanes.py
uv run pytest -q tests/test_graph.py
node --check vscode-chupa/media/view.js
node --check vscode-chupa/media/graph.js
uv run python -c "from pathlib import Path; m = Path('vscode-chupa/media'); t = (m / 'graph.js').read_text() + (m / 'view.js').read_text(); assert not any(s in t for s in ('toViewModels', 'LANE_COLORS', 'reachable'))"
uv run pytest -q
```

## Regression
```
uv run python tests/regress_graph_lanes.py
```
- carries: tests/regress_graph_lanes.py

## Definition of rejected
Reject the branch if any of the following holds:
- the extension still chooses edges, allocates lanes, or picks lane colors;
- a blocked row still has a lane to a queued or running row;
- two branch lanes to the same parent still open in one layout;
- `chupa/graph.py` does I/O;
- a file outside `## Scope fence` changes.

## Time budget
- expected: 60m
- stuck: 150m
