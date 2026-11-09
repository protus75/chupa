---
id: declined-box-000139-65491dbc
kind: declined
link: box-000139-65491dbc
reopen_after_days: 90
---
`chupa/drain.py` and `chupa/__main__.py` both import `_porcelain`, a private parser of `git status --porcelain` output defined in `chupa/tickets.py`. The note proposes making it a public helper or adding a public query for committed ticket paths.

This is only a naming and visibility cleanup. The cross-module import works, and the message points to no wrong runtime result caused by the private name. Promoting it would not change what any caller observes. Under the admission bar, a refactor or style preference that is not tied to reachable incorrect behavior is declined.

- chupa/tickets.py:568 defines `_porcelain(out: str) -> list[tuple[str, str]]`
- chupa/drain.py:39 imports `_porcelain` and uses it at line 413 to build the set of dirty paths
- chupa/__main__.py:44 also imports `_porcelain` and uses it at line 650
- The message describes no failure, wrong output or incident caused by the import

Message: box-000139-65491dbc
