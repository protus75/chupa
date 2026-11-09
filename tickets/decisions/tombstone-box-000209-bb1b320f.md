---
id: tombstone-box-000209-bb1b320f
kind: tombstone
link: declined-box-000033-431305e6
reopen_after_days: 90
---
Gate-lint does not check plan invariant 5, which says autofix commands must be idempotent (running one twice must leave the same result). The note asks `lint_gate` to run each autofix twice and require that the second run changes nothing, starting with the first gate that sets `autofix_applied`.

Registry record declined-box-000033-431305e6 already covers this request: add a run-twice fixpoint check to gate-lint to enforce invariant 5. That record also found that autofix now runs as its own Check step (`check_autofix`) and that `autofix_applied` is never set. This message asks for the same thing in different words, so it is a duplicate.

- declined-box-000033-431305e6 asks gate-lint to run each autofix command twice, require a fixpoint, and enforce invariant 5
- The same record notes that `autofix_applied` in `chupa/gates.py` is never set, the trigger this message names
- No open ticket implements an autofix idempotency check

Message: box-000209-bb1b320f
