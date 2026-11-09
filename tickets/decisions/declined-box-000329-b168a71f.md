---
id: declined-box-000329-b168a71f
kind: declined
link: box-000329-b168a71f
reopen_after_days: 30
---
Requisition review was inconsistent about tickets whose Verification ran `uv run pytest -q` instead of `./dev.py test`. Three tickets got a snag for it and one was approved with only a note. The finding asks the requisition review spec to make this an explicit snag.

`./dev.py test` runs exactly `uv run pytest -q` with the same arguments (`dev.py` lines 57 and 97). So the raw command checks the same tests in the same way, and a ticket that uses it is still buildable and checked correctly. The extension-thin-wrapper approval let through nothing that ran wrong. The real cost is that the three snags spent attempts on a command that behaves identically, and the proposed rule would add more of those bounces, not fewer. This is a wording rule with no runtime effect. Under the triage bar it is declined as a style preference, not a behavior gap.

- dev.py:57 `run(["uv", "run", "pytest", "-q", *sys.argv[2:]])`: `./dev.py test [args]` is the same command as `uv run pytest -q [args]`
- No file under chupa/specs mentions `dev.py test`, `uv run pytest`, or the command surface, so the inconsistency is reviewer judgment, not a spec contradiction
- Message: extension-thin-wrapper merged with the raw command; nothing reports a wrong Check result or a failed merge because of it
- The message's own overcorrection_risk says the change could turn requisition review into a style lint and cause extra premise_failed bounces

Message: box-000329-b168a71f
