---
id: tombstone-box-000348-f4cb4669
kind: tombstone
link: vscode-task-identity
reopen_after_days: 30
---
The note says the VS Code extension's Stop and Kill actions do nothing because `devCommand` gives every task the same definition `{type:'chupa'}`. VS Code then treats each new task as the drain task that is already running and never starts it. Merged ticket vscode-task-identity already fixed this: the definition now includes the task's argv.

Current `vscode-chupa/extension.js:36` builds each task with `new vscode.Task({ type: 'chupa', args }, ...)`, so each task's identity includes its argv. Stop, kill, the engine picker and drain are therefore separate tasks. Merged ticket vscode-task-identity covers this gap, and the behavior the note describes is not in current code.

- vscode-chupa/extension.js:36 creates the task definition as `{ type: 'chupa', args }`, not `{ type: 'chupa' }`
- vscode-task-identity is in the merged set (ticket commit 36e56df4) and its Context is vscode-chupa/extension.js
- The picker (line 354) and stop (line 358) also go through `devCommand`, so they get the per-argv identity too

Message: box-000348-f4cb4669
