---
id: tombstone-box-000356-fe31ef5d
kind: tombstone
link: vscode-task-identity
reopen_after_days: 30
---
On 2026-11-07, Stop and Kill from the vscode-chupa right-click menu put no control request in the engine inbox while a drain held the lock. The operator thought the drain had stopped when it was still running. The note also complains that the action gave no visible confirmation or failure.

This is the same incident that merged ticket vscode-task-identity diagnosed and fixed, and its evidence file is named kill-reached-no-inbox-2026-11-07. Every devCommand task had the same definition, `{type:'chupa'}`, so VS Code treated Stop and Kill as the drain task already running and never started them. No control request reached the engine. `devCommand` in `vscode-chupa/extension.js:36` now puts `args` in the task definition, so each action runs as its own task in a terminal, and that terminal shows its output or failure. That covers the missing feedback. Registry record tombstone-box-000348-f4cb4669 already linked this same symptom to vscode-task-identity.

- Merged squash commit d771fc1f (2026-11-07 03:38): vscode-task-identity describes Stop and Kill doing nothing during a drain, no control request reaching the engine, and the operator believing the drain had stopped.
- tickets/vscode-task-identity has evidence/kill-reached-no-inbox-2026-11-07.txt, the same date and symptom as this message.
- vscode-chupa/extension.js:36 now builds `new vscode.Task({ type: 'chupa', args }, ...)`, so each action has its own task identity.
- Registry record tombstone-box-000348-f4cb4669 already tombstoned the same Stop and Kill report to vscode-task-identity.

Message: box-000356-fe31ef5d
