---
id: declined-box-000381-d5f2e361
kind: declined
link: box-000381-d5f2e361
reopen_after_days: 30
---
Proposes a conduct rule that no command holds the checkout writer lock while a model call runs. The lock would be taken only around git and main writes, so one-shot verbs could never block confirm/reject. Review lock holding prompted it, and merged review-lock-only-for-intake already fixed that.

The incident that motivated the rule, `chupa review` holding the lock through its requisition call, is fixed on main. `_review` in `chupa/__main__.py` now takes the lock only around intake and makes the provider call unlocked. Merged `review-alongside-drain` covers the same ground. Two one-shot verbs still hold the lock across provider calls: `triage` (`one_pass`, `__main__.py:442-459`) and `retro` (`_retro`). Both also write the box, decision records or the journal under the same lock. The message names no incident where either one blocked confirm/reject or caused wrong behavior. During that window confirm/reject would fail with a LockHeld refusal, not do the wrong thing. Drain and serve hold the lock across provider calls by design, so the rule as written does not apply to them as stated. The request is a policy preference with no current harmful behavior shown, and it is not bounded to one buildable change.

- chupa/__main__.py:514-525: `_review` takes the Lockfile only around `intake` and releases it before the ProviderLLM/requisition call at 539-565
- chupa/__main__.py:442-459: `triage` `one_pass` holds the Lockfile across `triage.triage_pass` (provider calls), with no reported incident blocking confirm/reject
- chupa/__main__.py:592-604: `_retro` acquires the lock and, on LockHeld, submits to the running engine instead
- merged stems review-lock-only-for-intake and review-alongside-drain already cover the review instance
- chupa/drain.py:212-215 and chupa/serve.py:539-541 hold the lock for the whole session by design

Message: box-000381-d5f2e361
