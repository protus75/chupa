---
id: declined-box-000093-e1f5e684
kind: declined
link: box-000093-e1f5e684
reopen_after_days: 60
---
When intake refuses a hand-authored ticket, the ticket stays uncommitted, and it stays staged if the author staged it. The pathspec-limited commit keeps it out of other stems' commits. Drain (`chupa/drain.py:263`, `:335`) and serve (`chupa/serve.py:284`) call `intake` but ignore `IntakeResult.refused`, so a background loop never names the refused stem. The note asks for refused stems to appear in the engine log or an intake signal.

This is an observability preference. It does not show a materially harmful behavior gap. A refused ticket is never committed, so it never runs and cannot corrupt any other commit; `chupa/tickets.py:686` limits each commit to its own pathspec on purpose. Every per-stem path a human uses already reports the refusal with its findings: `run` (`chupa/runner.py:629`), the verdict path (`runner.py:535`) and `review` (`chupa/__main__.py:522`). The authoring contract also requires `chupa lint <stem>` to exit 0 before handoff. The note is a bootstrap-ingest suggestion and cites no incident where a refused ticket sat unnoticed and cost work.

- chupa/tickets.py:646 docstring: a refused ticket stays on disk, uncommitted, untouched
- chupa/tickets.py:686 pathspec-limited commit so a staged refused ticket never rides along in another stem's commit
- chupa/drain.py:263 and :335 and chupa/serve.py:284 discard the IntakeResult, so refused stems are not logged there
- chupa/runner.py:535, chupa/runner.py:629 and chupa/__main__.py:522 raise Refusal naming the stem and its findings on the per-stem verbs
- merged ticket review-surfaces-refused already reports refusals on the review path

Message: box-000093-e1f5e684
