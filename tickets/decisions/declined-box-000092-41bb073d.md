---
id: declined-box-000092-41bb073d
kind: declined
link: box-000092-41bb073d
reopen_after_days: 90
---
`_porcelain` in `chupa/tickets.py` parses `git status --porcelain` output without `-z`. It strips the surrounding quotes from a C-quoted path but does not undo git's escapes, so a path containing non-ASCII or other special characters would come back with escape sequences instead of the real characters. The note proposes switching to `status --porcelain -z`.

This is speculative hardening with no reachable failure shown. Intake reads ticket paths under `tickets/<stem>/`, and the `STEM` regex in `chupa/tickets.py:26` (`^[a-z0-9][a-z0-9-]{1,63}$`) allows only ASCII stems, so those paths are never C-quoted. The note itself calls the risk low. Nothing shows a ticket file or dirty path with special characters causing a wrong intake, drain or verdict decision. The callers that need exact paths (`stages.py:367`, `merge.py:252`) already use `-z`.

- chupa/tickets.py:26 STEM regex allows only ASCII lowercase letters, digits and hyphens
- chupa/tickets.py:568 `_porcelain` parses non-`-z` porcelain output; its callers are tickets.py:648, drain.py:413 and __main__.py:650
- chupa/stages.py:367 and chupa/merge.py:252 already call status_porcelain with -z
- The message gives no incident and itself rates the risk as low

Message: box-000092-41bb073d
