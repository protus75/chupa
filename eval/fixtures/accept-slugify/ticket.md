---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add a `slugify(title)` helper so blog posts can use stable, readable URL paths.

## Scope in / Scope out
Add the helper and focused tests. URL routing and persistence are out of scope.

## Scope fence
- `slug.py`
- `tests/test_slug.py`

## Acceptance criteria
1. `slugify` returns lowercase ASCII letters and digits separated by single hyphens, with no leading or trailing hyphen. For example, `"  Hello, Python 3!  "` becomes `"hello-python-3"`.
2. Unicode text is casefolded, then normalized with NFKD and converted to ASCII. `"Crème brûlée"` becomes `"creme-brulee"`, and `"Straße"` becomes `"strasse"`.
3. Each run of nonalphanumeric characters, including underscores and slashes, becomes one hyphen. `"A/B__C"` becomes `"a-b-c"`.
4. A title that produces no ASCII letters or digits raises `ValueError` with the message `title has no slug characters`.

## Verification
- `python -m pytest tests/test_slug.py`
- `python -m pytest`
