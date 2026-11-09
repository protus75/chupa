---
id: tombstone-box-000338-98ba883a
kind: tombstone
link: chupa-ruff-config
reopen_after_days: 14
---
The chupa-test-gates Implement run stopped with premise_failed because whole-repository Ruff lint and format checks were already red on the merge base. That made a repo-wide Ruff check impossible to satisfy inside the ticket's fence.

Open ticket chupa-ruff-config already covers this. It adds the missing Ruff configuration to pyproject.toml, pins ruff as a dev dependency and fixes the remaining findings, so that `uv run ruff check .` and `uv run ruff format --check .` both exit 0. Once it merges, the base will no longer fail whole-repository Ruff checks, which is exactly the gap this message reports.

- The message is from origin chupa-test-gates at stage implement with outcome premise_failed. Its summary says the merge base fails whole-repository Ruff lint and format checks.
- The open ticket chupa-ruff-config says the repo has no Ruff configuration and 14 findings Ruff cannot fix itself. Its stated result is that `uv run ruff check .` and `uv run ruff format --check .` both exit 0.
- The merged chupa-ruff-reclean* and chupa-ruff-src/tests tickets show earlier passes that left the whole-repo checks still red. chupa-ruff-config is the remaining open fix.

Message: box-000338-98ba883a
