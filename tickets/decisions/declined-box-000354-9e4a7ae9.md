---
id: declined-box-000354-9e4a7ae9
kind: declined
link: box-000354-9e4a7ae9
reopen_after_days: 30
---
During test-rules-prompt, the implementer added `merge.safety_checks: [unit]` to the python-host example block in docs/host-contract.md, although the ticket did not ask for it, and review did not flag the extra key. The note asks for a decision on whether the key stays, and for review to snag config or doc keys added beyond what Scope in names.

No reachable incorrect runtime behavior is shown. `merge.safety_checks` is a real config key (`chupa/config.py:164`). In the block, `unit` resolves to exactly one hard `review.mechanical` entry, which is the rule `chupa/mergequeue.py:203-208` enforces, so a host that merges the block gets a valid config whose merge queue runs the unit suite at the safety tier. The added key is therefore a correct, working example, not a defect. The proposed review rule (snag keys beyond what Scope in names) is a process preference with no measured harm such as a failed merge, a broken host config or a parked ticket. A related harm, tickets that copy this block verbatim and then contradict it after it grows, was already declined as 000342.

- docs/host-contract.md:80-81 sets `merge: safety_checks: [unit]` in the python-host block
- docs/host-contract.md:67-70 declares `unit` as a single `trigger: always`, `severity: hard` mechanical entry
- chupa/mergequeue.py:203-208 requires each safety_checks code to resolve to exactly one hard entry, and `unit` meets that
- chupa/config.py:164 defines `safety_checks: list[str] = []`
- declined-box-000342-ff84bb14 already covers harm from the python-host block growing under tickets that copy it

Message: box-000354-9e4a7ae9
