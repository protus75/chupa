---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/graph.py
- tests/unit/test_graph.py
- vscode-chupa/media/graph.js
- vscode-chupa/media/view.js

## Goal / Why
The thin-wrapper rule says `chupa/graph.py` lays out the ticket graph, and JavaScript only draws SVG from the lane indexes it is given. A 2026-11-08 audit found `vscode-chupa/media/graph.js` `renderGraph` still chooses lanes:
- it finds the node's own column with `findIndex` over `lanesIn`;
- it walks `lanesIn` against `lanesOut` matching ids to decide which incoming lane continues into which output slot, and which lanes curve into the node;
- it picks each edge's colour lane;
- it decides from `parentLanes` versus the node column whether an edge goes down, branches right or joins left.

That is untested layout code, the class of bug the 2026-11-06 lane fixes came from. It also has an unused `findLastIndex`.

After this change, `layout` emits every drawable piece per row as lane indexes and sections, and `renderGraph` maps each piece to an SVG path with its geometry constants.

## Scope in / Scope out
- In: `chupa/graph.py` `layout`. Each row's dict keeps its current keys and gains the following, computed exactly as `graph.js` computes them today:
  - `circle`: the index of the row's stem in `lanesIn` (first match), else `len(lanesIn)`.
  - `dot`: `head` for `kind == "head"`, else `merge` when `len(parents) > 1`, else `node`.
  - `width`: `max(len(lanesIn), len(lanesOut), circle + 1) + 1`.
  - `segments`: an ordered list of dicts, each with a `section`. The incoming pass walks `lanesIn` with an output-slot counter, skipping `id is None` lanes:
    - a lane whose id is the stem at an index other than `circle` emits `{"kind": "into", "from": index, "to": circle}`, with that lane's section. Every stem lane advances the slot.
    - a lane matching `lanesOut[slot]` emits `{"kind": "straight", "lane": index}` when `index == slot`, else `{"kind": "shift", "from": index, "to": slot}`. Either way it carries that lane's section and advances the slot.

    Each parent lane `p` in `parentLanes` emits one of these:
    - `{"kind": "down", "lane": circle}` when `p == circle`, with the node lane's section: `lanesOut[circle]` if it exists, else `lanesIn[circle]` if it exists, else the row's section;
    - `{"kind": "branch", "from": circle, "to": p}` when `p > circle`;
    - `{"kind": "join", "from": circle, "to": p}` when `p < circle`.

    The last two carry `lanesOut[p]`'s section. When the stem is in `lanesIn`, `{"kind": "top", "lane": circle}` comes last, with that incoming lane's section.
  - `layout` stays pure: lane indexes and sections only, no colours or pixels.
- In: `vscode-chupa/media/graph.js` `renderGraph(graph, colors)`.
  - It draws `graph.segments` in order. Each kind maps to the SVG path it draws today, with the same geometry constants, coloured by `colors[segment.section]`.
  - It then draws `graph.dot` at `graph.circle`, coloured by the row's section colour passed in, and sizes the SVG from `graph.width`.
  - Remove `findLastIndex`, the `stem` parameter, and every `findIndex`, id comparison and lane-matching loop.
- In: `vscode-chupa/media/view.js`: call `renderGraph(r.graph, COLOR[r.section], COLOR)` to match the new signature (dot colour and colour table).
- In: `tests/unit/test_graph.py`. New tests assert `segments`, `circle`, `dot` and `width` for:
  - a straight pass-through lane;
  - a `shift` after a lane closes to its left;
  - two incoming lanes for one stem (one `into`);
  - a `branch` to a new lane on the right;
  - a `join` into an existing lane on the left (the `test_new_tip_joins_existing_parent_lane` layout, row s: circle 2, join from 2 to 1);
  - a `head` dot;
  - a `merge` dot.

  Existing tests stay unchanged.
- Out: `observe.py` (it attaches `layout` output unchanged), graph colours (`view.js` `COLOR`), `tests/regress_graph_lanes.py`, and every other extension file. `tests/integration/test_watch.py` runs layout through the snapshot but asserts no graph keys, and this change only adds keys.

## Scope fence
- chupa/graph.py
- vscode-chupa/media/graph.js
- vscode-chupa/media/view.js
- tests/unit/test_graph.py

## Acceptance criteria
1. `./dev.py test tests/unit/test_graph.py` passes. It includes a two-incoming-lanes case whose `segments` contain exactly one `into` (not zero), and a join case whose parent edge is `join` (not `branch`).
2. `vscode-chupa/media/graph.js` contains no `findIndex`, no `findLastIndex`, no `.id ===` comparison and no `lanesIn`/`lanesOut` access, checked by reading the file.
3. `chupa/graph.py` output carries no colour or pixel values, checked by reading the file.

## Verification
```
./dev.py test tests/unit/test_graph.py
```

## Definition of rejected
`graph.js` computes any lane index, column or edge direction, or `layout` emits colours or pixel values.

## Time budget
- expected: 30m
- stuck: 75m
