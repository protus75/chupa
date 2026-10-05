---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Add a CSV export command for a SQLite orders table so analysts can use order data in spreadsheets. The project uses Python 3.11. The table has `id INTEGER`, `placed_at TEXT`, `status TEXT`, and `total_cents INTEGER` columns.

## Scope in / Scope out

Add `python -m orders_export DATABASE OUTPUT [--status VALUE]` and focused tests. Schema changes and other export formats are out of scope.

## Scope fence

- `orders_export.py`
- `tests/test_orders_export.py`

## Acceptance criteria

1. The command writes UTF-8 CSV with the header `id,placed_at,status,total_cents` and data rows ordered by ascending `id`.
2. Without `--status`, it exports every order. With `--status VALUE`, it exports only rows whose status equals VALUE exactly, including when VALUE contains `%` or `_`.
3. CSV fields containing commas or newlines round-trip through a standard CSV reader.
4. An existing output file is replaced with the new export.

## Verification

`python -m pytest -q tests/test_orders_export.py`
