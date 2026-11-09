# chupa tickets

A VS Code extension for the [chupa](https://pypi.org/project/chupa/) ticket system. View chupa tickets in the Activity Bar. The Tickets view shows the dependency graph and ticket states; Details shows the selected ticket or Suggestion Box message. Recent Steps shows engine activity, Suggestion Box lists messages, and Stats shows health figures.

Built for [chupa 0.1.2](https://pypi.org/project/chupa/0.1.2/).

## Prerequisites

Open a repository containing `tickets/` and install chupa with `uv tool install chupa`.

The `chupa.command` setting is the command and arguments used to run the engine. For an installed engine, use `["chupa"]` (the default).

On WSL or Remote-SSH, the extension runs on the remote side, where the repository and chupa command are available.
