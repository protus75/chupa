---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Add a pagination helper for an in-memory REST listing endpoint so callers receive page items and consistent metadata.

## Scope in / Scope out

In: Implement `paginate(items, page, per_page)` for sequences. Pages are numbered from 1. Return a dictionary with `items`, `page`, `per_page`, `total`, and `total_pages`.

Out: Request parsing, database queries, and HTTP response formatting.

## Scope fence

- `listing/pagination.py`
- `tests/test_pagination.py`

## Acceptance criteria

1. `items` contains only the requested page, as a list, while `total` is the full sequence length.
2. `total_pages` is the ceiling of `total / per_page`, including when the division is exact; an empty sequence has zero pages.
3. A page beyond the last page returns an empty `items` list with the requested page number and unchanged totals.
4. `page` and `per_page` must be positive integers; invalid values, including booleans, raise `ValueError`.

## Verification

`python -m pytest -q tests/test_pagination.py`
