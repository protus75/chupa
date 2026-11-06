---
state: confirmed
source: human
priority: P3
kind: bug
---

## Depends on
none

## Context
- vscode-chupa/media/view.js
- vscode-chupa/media/graph.js

## Goal / Why
The Tickets view graph draws badly on the live queue (2026-11-06):
- Blocked `vscode-marketplace-publish` depends on queued `observe-verbs-host-extension`. That edge opens an orange lane in lane 0 above the queue. The queue's top row then lands in lane 1, and the main line jumps back to lane 0 at `observe-verbs-host-extension`.
- Queued `specs-module-into-package` and `spec-path-matchers` both depend on running `specs-move`. Each opens its own lane, so two parallel lanes run 10 rows to the same dot.
- Those queued branch lanes take the SCM rotation colors (yellow, pink) because queued rows set no `branchColor`.

After this change the main line stays in one lane, dependents of one ticket share a lane, and queued branches use the queued color.

## Scope in / Scope out
- In: `view.js` `render`: a blocked row's `parentIds` hold only its blocked dependencies. Its unmerged non-blocked dependencies stay in its status text and the Details view.
- In: `view.js` `render`: queued and running rows set `branchColor: COLOR[r.section]`.
- In: `graph.js` `toViewModels`: a non-first parent that already has a lane in this row's `outputSwimlanes` joins that lane instead of opening another. `renderGraph` draws the row's merge curve into that existing lane.
- In: update the comments in both files that describe the changed behavior.
- Out: `extension.js`, `snapshot.py`, `view.css`, `detail.js`, the status text, row order, and the dot colors.
- Touch no file outside `## Scope fence`.

## Scope fence
- vscode-chupa/media/view.js
- vscode-chupa/media/graph.js

## Acceptance criteria
1. For rows `a(b,d)`, `b(c,d)`, `c(d)`, `d()`, no row's `outputSwimlanes` holds more than two lanes for `d`. The second Verification command checks this; it fails on the base commit.
2. A blocked row whose dependencies are all unmerged and non-blocked has empty `parentIds`.
3. Every queued or running row's branch lanes take `COLOR[r.section]`, never a `LANE_COLORS` entry.
4. `node --check` passes for both files.

## Verification
```
node --check vscode-chupa/media/view.js
node -e "const vm=require('vm'),c={};vm.createContext(c);vm.runInContext(require('fs').readFileSync('vscode-chupa/media/graph.js','utf8')+';this.f=toViewModels',c);const v=c.f([{id:'a',parentIds:['b','d']},{id:'b',parentIds:['c','d']},{id:'c',parentIds:['d']},{id:'d',parentIds:[]}]);for(const m of v){if(m.outputSwimlanes.filter(n=>n.id==='d').length>2)throw new Error(m.item.id)}"
uv run pytest -q
```

## Regression
```
node -e "const vm=require('vm'),c={};vm.createContext(c);vm.runInContext(require('fs').readFileSync('vscode-chupa/media/graph.js','utf8')+';this.f=toViewModels',c);const v=c.f([{id:'a',parentIds:['b','d']},{id:'b',parentIds:['c','d']},{id:'c',parentIds:['d']},{id:'d',parentIds:[]}]);for(const m of v){if(m.outputSwimlanes.filter(n=>n.id==='d').length>2)throw new Error(m.item.id)}"
```
- carries: vscode-chupa/media/graph.js

## Definition of rejected
Reject the branch if any of the following holds:
- a blocked row still draws a lane to a queued or running row;
- two branch lanes to the same parent still open in one `toViewModels` pass;
- a joined lane is drawn broken or doubled at the joining row;
- a file outside `## Scope fence` changes.

## Time budget
- expected: 30m
- stuck: 90m
