---
id: declined-box-000003-8007f56c
kind: declined
link: box-000003-8007f56c
reopen_after_days: 60
---
The journal write seam still checks only the event envelope and signal names. It does not check event bodies, such as whether `state_transition.to` uses the closed run-state vocabulary or whether `dispatch` uses an allowed value. The `Outcome` vocabulary this work was waiting on now exists, but nothing shows a bad body has ever been written.

This is hardening against a possible future write, not a fix for current harmful behavior. `Journal.append` rejects bad event types, non-object bodies and unknown signal names, and readers already reject unknown values: `dispatch_of` raises on an unknown dispatch, and `run_terminals` uses the closed `TERMINAL_STATES` set. No incident, failing run or bad journal entry shows that an out-of-vocabulary `to` or `dispatch` value was written or misread. The prerequisite is met, since `chupa/artifacts.py` now exports `OUTCOMES` and `journal.py` imports it, but having the prerequisite in place does not show harm. The admission bar needs current, reachable, harmful behavior, so this is recorded as a decision. It reopens if a journal event with an out-of-vocabulary `state_transition.to` or `dispatch` value is found, or if a fold or dispatch fails or quietly misreads a badly shaped body.

- chupa/journal.py:156-171: append checks event type, body is a dict, ticket and key types, and SIGNAL_NAMES membership; it has no check for state_transition body shape
- chupa/journal.py:16,100: OUTCOMES is imported from chupa.artifacts and TERMINAL_STATES is built from it, so the Outcome prerequisite exists
- chupa/journal.py:79-86: dispatch_of raises on an unknown dispatch value when reading
- The message gives no incident, run record or bad journal line; origin is bootstrap-ingest

Message: box-000003-8007f56c
