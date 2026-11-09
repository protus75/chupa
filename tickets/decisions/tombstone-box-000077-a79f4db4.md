---
id: tombstone-box-000077-a79f4db4
kind: tombstone
link: baseline-binding-reader
reopen_after_days: 90
---
A bootstrap note asked that the baseline binding reader treat a recorded `author.spec_major` of null as a mismatch, because `chupa/policy.py` writes null when a surface's spec file is missing. The merged ticket `baseline-binding-reader` already does this: `_matches` in `chupa/baseline.py` returns False when the recorded major is not an int, so the binding stays on the supervised side.

Merged ticket baseline-binding-reader already covers this. In `chupa/baseline.py:42`, `_matches` rejects any `spec_major` that is not an int, including null. It also requires the major to equal the current spec's major (line 45), so a null major can never bind GO. No behavior gap remains.

- chupa/policy.py:28 records spec_major as None when specs/<surface>.md does not exist
- chupa/baseline.py:42 `if type(major) is not int or major < 0 ...: return False` makes a null major a mismatch
- chupa/baseline.py:45 requires the recorded major to equal the current spec version's major
- merged stem baseline-binding-reader delivered the fail-closed baseline binding reader

Message: box-000077-a79f4db4
