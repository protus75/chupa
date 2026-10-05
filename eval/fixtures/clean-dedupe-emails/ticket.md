---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Add `dedupe_emails(list)` so callers can obtain a consistent list of email addresses when input differs in case or surrounding whitespace.

## Scope in / Scope out

In scope: strip surrounding whitespace, casefold addresses, remove duplicates, and preserve first-seen order. Out of scope: email validation, changing internal whitespace, and modifying the input list.

## Scope fence

- `email_tools.py`
- `tests/test_email_tools.py`

## Acceptance criteria

1. Each returned address is stripped of surrounding whitespace and casefolded.
2. Each normalized address appears once, in first-seen order.
3. Entries that normalize to an empty string are omitted.
4. The input list remains unchanged, and the result is a new list.
5. Internal whitespace is preserved; addresses are not validated.

## Verification

```bash
python -m pytest -q tests/test_email_tools.py
python -m pytest -q
```
