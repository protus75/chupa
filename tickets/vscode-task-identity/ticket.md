---
state: confirmed
source: human
priority: P1
kind: bug
---

## Depends on
- none

## Context
- vscode-chupa/extension.js
- vscode-chupa/package.json
- tests/regress_graph_lanes.py

## Goal / Why
While a drain started from the vscode-chupa Tickets view runs, choosing Stop or Kill from the same view does nothing (2026-11-07, see `evidence/`). `devCommand` in `vscode-chupa/extension.js` gives every action the same task definition `{ type: 'chupa' }`. VS Code derives an extension task's identity from its definition only, not its argv, so Stop and Kill look like the drain task that is already running. VS Code then shows a "restart running task" picker instead of starting them, and no control request reaches the engine. The operator believed the drain was stopped when it was not.

After this change each action's task definition carries its argv, so actions with different argv are different tasks and start while another chupa task runs.

## Scope in / Scope out
- In: `vscode-chupa/extension.js`: `devCommand` builds the task with definition `{ type: 'chupa', args }`, where `args` is the chupa argv after the `chupa.command` prefix (the `args` it already receives). Nothing else in the task changes.
- In: new carried reproducer `tests/regress_vscode_task_identity.py`, in the style of `tests/regress_graph_lanes.py`, with its node harness `tests/vscode_task_identity.js`:
  - The harness loads `vscode-chupa/extension.js` under node with a stub `vscode` module. The stub records each `vscode.Task` definition, captures each `vscode.commands.registerCommand` handler, gives one workspace folder at the repo root, and returns `["true"]` for the `chupa.command` setting so nothing real runs. It calls `activate`, invokes `chupa.ticket.review` and `chupa.ticket.lint` with `{ chupaStem: "x" }`, then `chupa.ticket.review` again with the same context, and prints the three recorded definitions as JSON.
  - The Python reproducer runs the harness with `node` and prints exactly one `{"regression_result": ...}` line: `pass` (exit 0) when the review and lint definitions differ and the two review definitions are equal; `defect` (exit 1) when the review and lint definitions are equal; `error` (exit 2) when `node` is missing, the harness fails, or fewer than three definitions are recorded.
- Out:
  - `package.json` `taskDefinitions` and the task's `runOptions` / instance policy;
  - the commands, menus, and labels (`extension-engine-picker` changes those);
  - every engine verb and `chupa/`.

## Scope fence
- vscode-chupa/extension.js
- tests/regress_vscode_task_identity.py
- tests/vscode_task_identity.js

## Acceptance criteria
1. `node --check vscode-chupa/extension.js` exits 0.
2. `uv run python tests/regress_vscode_task_identity.py` prints `{"regression_result": "pass"}`: the `review x` and `lint x` task definitions differ, not both `{"type": "chupa"}`, and two `review x` runs give equal definitions.
3. `./dev.py test` exits 0.

## Verification
```
node --check vscode-chupa/extension.js
uv run python tests/regress_vscode_task_identity.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- the task definition carries anything other than `type` and the chupa argv, such as a timestamp or counter that makes identical actions distinct;
- any change outside `devCommand` in `vscode-chupa/extension.js`;
- the reproducer starts a real `chupa` or `uv` process.

## Time budget
- expected: 30m
- stuck: 90m

## Regression
```
uv run python tests/regress_vscode_task_identity.py
```
- carries: tests/regress_vscode_task_identity.py
- carries: tests/vscode_task_identity.js
