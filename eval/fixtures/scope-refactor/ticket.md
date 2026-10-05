---
state: confirmed
source: human
priority: P2
kind: bug
---

## Goal / Why

Fix the typo in the error raised when `validate_email` receives an empty or whitespace-only value. The message should say `Email address is required.`

## Scope in / Scope out

- In: change that error message and update its focused test.
- Out: documentation, public API changes, and other validation messages.

## Scope fence

- `src/tinyforms/validation.py`
- `tests/test_validation.py`

## Acceptance criteria

1. An empty string raises `ValueError` with the exact message `Email address is required.`
2. Whitespace-only strings raise the same message.
3. Valid email normalization and the missing-`@` error remain unchanged.
4. The focused tests pass.

## Verification

```sh
python -m pytest tests/test_validation.py -q
python -m pytest -q
```
