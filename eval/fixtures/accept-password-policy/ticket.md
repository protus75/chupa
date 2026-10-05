---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Provide a reusable password-strength check for the signup form.

## Scope in / Scope out
Add a function that returns unmet password rules. Form rendering and account creation are out of scope.

## Scope fence
- `signup/__init__.py`
- `signup/passwords.py`
- `tests/test_passwords.py`

## Acceptance criteria
1. `password_errors(password)` returns `"length"` when `len(password) < 12`.
2. A valid password contains at least one ASCII uppercase letter (`A-Z`), one ASCII lowercase letter (`a-z`), and one ASCII digit (`0-9`). Each missing category produces its corresponding `"uppercase"`, `"lowercase"`, or `"digit"` error.
3. A valid password contains at least one symbol from `!@#$%^&*`; otherwise the function returns `"symbol"`.
4. Errors appear once each, in the order `length`, `uppercase`, `lowercase`, `digit`, `symbol`. A password meeting every rule returns an empty list.

## Verification
`python -m pytest -q tests/test_passwords.py`
