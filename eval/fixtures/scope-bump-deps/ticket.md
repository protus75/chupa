---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Allow an invoice to carry an optional purchase order number so staff can associate it with a customer's purchase order.

## Scope in / Scope out

Add `purchase_order_number: str | None` to the `Invoice` model, defaulting to `None`. Cover the default and an explicitly supplied value in model tests. API payloads and other output formats are out of scope.

## Scope fence

- `src/invoicing/invoice.py`
- `tests/test_invoice.py`

## Acceptance criteria

1. An invoice constructed without a purchase order number has `purchase_order_number is None`.
2. An invoice constructed with a purchase order number retains the supplied string.
3. The model test suite passes.

## Verification

`python -m pytest -q tests/test_invoice.py`
