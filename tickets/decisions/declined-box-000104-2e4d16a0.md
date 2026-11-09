---
id: declined-box-000104-2e4d16a0
kind: declined
link: box-000104-2e4d16a0
reopen_after_days: 60
---
The scope-fence gate refuses any edit outside the fence, including test-file edits, and the only way past it is a ticket's `gate_bypass`. The anti-weakening AST check that would let it admit such test edits automatically has not been built. Fence prefixes match whole path components, so `chupa/thing` does not cover `chupa/thing_x.py`. The note proposes building auto-admission once a real incident shows it is needed.

This describes a deliberate fail-closed design, and the `gate_bypass` valve already gives a way past it. Neither the message nor its evidence shows a ticket that failed or got stuck because an out-of-fence test edit was refused. The note itself puts off the work until a first incident happens. That makes it speculative hardening, not a current harmful gap in behavior.

- The message says the gate 'fails closed to the `gate_bypass` valve' and 'Build the auto-admission when its first incident lands', so it reports no incident.
- `gate_bypass` and `scope_fence` handling exist in `chupa/gates.py`, `chupa/tickets.py` and `chupa/stages.py`, so the release path is built.
- No open ticket or registry record names a run blocked by an out-of-fence test edit.

Message: box-000104-2e4d16a0
