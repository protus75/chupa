---
id: declined-box-000148-dbca0fe9
kind: declined
link: box-000148-dbca0fe9
reopen_after_days: 90
---
This note asks for a unit test that pins `_one_line` in `chupa/stages.py`, the function that flattens re-entry finding text. The test would feed it a message containing a newline or a `## ` prefix and check that the message cannot forge a ticket section heading in the rendered re-entry block. It reports no failure.

This only adds a test, and no wrong runtime behavior can be reached today. `_one_line` returns `" ".join(text.split())`, which turns every run of whitespace into one space. That includes `\n`, `\r` and other Unicode line breaks, so the output is always a single line. Every place that puts finding text into the re-entry block runs it through `_one_line` and adds a `- ` or `> ` prefix in front, so a `## ` in the text can never start a line. Earlier re-entry review notes asking only for tests were declined the same way (declined-box-000146-bd19e063, declined-box-000147-ce29be8b).

- chupa/stages.py:525-527 `_one_line` returns `" ".join(text.split())`, which removes every line break, and carries a comment explaining that it guards against heading forgery
- chupa/stages.py:570 finding message and paved_road are passed through `_one_line` after a `- [code]` prefix
- chupa/stages.py:574 and :586 lesson items are passed through `_one_line` after a `> ` prefix
- chupa/stages.py:625 second-problem summaries are passed through `_one_line` after a `- id:` prefix

Message: box-000148-dbca0fe9
