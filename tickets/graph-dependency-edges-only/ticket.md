---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- none

## Context
- chupa/graph.py
- tests/unit/test_graph.py
- tests/regress_graph_lanes.py
- vscode-chupa/media/graph.js
- docs/how-chupa-works.md#2. Commands

## Goal / Why
In the Tickets view, a line between two rows should mean "depends on". Today it does not. `layout` makes the row below the first parent of every queued or running row, so the graph draws a git-log-style spine through the whole queue (`evidence/parents.txt`, the live queue on 2026-11-08):
- `check-test-timing`, `results-schema-2-reader` and `review-unmerged-provisional` have no dependencies, but each gets the row below it as a parent. The line implies dependencies that do not exist.
- `vscode-verdict-menu` depends on `review-unmerged-provisional`, which is the row directly below it. `layout` drops that dependency from the branches (`d != below`) and draws it as a plain spine edge. The owner could not see it.

After this change, every edge on a non-merged row is a declared, unmerged dependency of that row. Row order alone shows queue order. Merged rows keep their history line.

## Scope in / Scope out
- In: `chupa/graph.py` `layout`, where parents are chosen:
  - A queued or running row's `parents` are its `reduced` dependencies in `lane_key` order, with no implicit row-below parent. A dependency that is the row below comes first by position and continues the node's own column.
  - A merged row's `parents` are `[below]` when the row below is also merged, else `[]`. Merged history stays one line, and no edge joins a merged row to a non-merged row.
  - Blocked rows are unchanged.
  - Lane allocation, `parentLanes`, `lanesIn`/`lanesOut` and the trailing-gap trim are unchanged. Only the input `parents` changes.
- In: `tests/unit/test_graph.py`. Update the assertions that encode the implicit row-below parent to the dependency-only model, and change nothing else in those tests. Add tests for:
  - a queued row with no dependencies above a queued row: `parents == []`, not `[below]`;
  - a queued row depending on the row directly below: `parents == [below]` and `parentLanes == [circle column]`;
  - a running row above a merged row: `parents == []`;
  - two adjacent merged rows: the upper one has `parents == [lower]`.
- In: new `tests/regress_graph_dependency_edges.py`, which speaks the regression protocol. On the evidence queue shape, it reports `defect` when any non-merged row has a parent outside its `depends`, else `pass`. It reports `error` when `chupa.graph` cannot be imported.
- In: `docs/how-chupa-works.md` section 2 (Commands), the `vscode-chupa/` paragraph: add one sentence saying a line between ticket rows means a dependency, and that merged rows show their history line.
- Out: `vscode-chupa/media/graph.js`, `view.js` and every other extension file. A row with no parents and no incoming lane already draws as a lone dot, as blocked rows do today. Also out: `observe.py` and the snapshot builder, row order, colours, and `tests/regress_graph_lanes.py`, which must still pass unchanged.

## Scope fence
- chupa/graph.py
- tests/unit/test_graph.py
- tests/regress_graph_dependency_edges.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/unit/test_graph.py` passes. It includes a test where a dependency-free queued row's `parents` is `[]`, not the row below, and a test where a dependency on the row directly below is `parents == [below]`, not dropped.
2. `uv run python tests/regress_graph_dependency_edges.py` prints `{"regression_result": "pass"}` and exits 0.
3. `uv run python tests/regress_graph_lanes.py` still prints `{"regression_result": "pass"}`.
4. `docs/how-chupa-works.md` states that a line between ticket rows means a dependency, checked by reading the file.

## Verification
```
./dev.py test tests/unit/test_graph.py
uv run python tests/regress_graph_dependency_edges.py
uv run python tests/regress_graph_lanes.py
```

## Definition of rejected
Reject the branch if any of the following holds:
- a non-merged row has a parent that is not in its `depends`;
- a declared unmerged dependency on a lower row is missing from `parents` (blocked rows' existing blocked-only filter excepted);
- any extension JavaScript file changes;
- `layout` does I/O or emits colours or pixels.

## Time budget
- expected: 30m
- stuck: 75m

## Regression
```
uv run python tests/regress_graph_dependency_edges.py
```
- carries: tests/regress_graph_dependency_edges.py
