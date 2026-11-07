---
id: declined-box-000054-61f0e8fe
kind: declined
link: box-000054-61f0e8fe
reopen_after_days: 90
---
A bootstrap review note said the plan-unit parser `_units` noticed a code fence only when it started at column 0. A fence indented by up to three spaces would not have hidden the `## N.` headings inside it. The note asked for CommonMark-style handling of indented fences.

The parser no longer exists. No `_units` function is left anywhere in the Python tree, and the plan-grammar and plan-text code was removed by the merged tickets remove-plan-grammar and remove-plan-text-tests. The code fence scanners that remain in `chupa/tickets.py` and `chupa/stages.py` already use `line.lstrip().startswith("```")`, so they accept indented fences. Even when it was written, the note recorded no failure: it said the real plan linted green. So there is no current, reachable incorrect behavior.

- A search of all `*.py` files for `_units` finds no definition; the only hit is the unrelated `plan_units` fixture key in tests/integration/test_drain.py:1441
- Merged stems include remove-plan-grammar and remove-plan-text-tests
- chupa/tickets.py:155, chupa/tickets.py:626 and chupa/stages.py:598 detect fences with `line.lstrip().startswith("```")`, which already allows indentation
- The message itself says the real plan lints green today

Message: box-000054-61f0e8fe
