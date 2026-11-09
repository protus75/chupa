---
id: declined-box-000089-ab4947b8
kind: declined
link: box-000089-ab4947b8
reopen_after_days: 90
---
Intake does not compare a hand edit to an established ticket against its committed version, so a person can change `state` to `merged` or `rejected` and the edit is committed as written. The note asks for a rule on which state changes a human edit may make, enforced against the committed predecessor once `git.py` has a `show` operation.

No reachable harmful behavior is shown. Frontmatter `state` only controls dispatch eligibility: the scheduler, drain, runner and observe dispatch only `state: confirmed`. A hand edit to `merged` or `rejected` just stops the ticket from being dispatched, which is an operator's choice they could also make by deleting the ticket. It does not fake settlement. Dependency resolution and the settled/merged checks read journal `state_transition` events (`last_states`), so dependents are not unblocked and no merge is recorded. The request is speculative hardening of trusted human input. Registry decision declined-box-000085-cbfb936f already declined the same kind of committed-predecessor check for `source`.

- chupa/tickets.py:55 frontmatter state Literal draft|confirmed|rejected|merged
- chupa/tickets.py:664-676 intake reads run-state from journal STATE_TRANSITION events, not frontmatter
- chupa/drain.py:449 and chupa/scheduler.py:68 dispatch only `state == confirmed`; other values only withhold dispatch
- chupa/observe.py:553 runnable requires depends subset of journal-settled stems, so a hand-written `merged` does not unblock dependents
- chupa/runner.py:639-642 refuses to run a non-confirmed ticket
- declined-box-000085-cbfb936f declined the parallel committed-predecessor check for `source`

Message: box-000089-ab4947b8
