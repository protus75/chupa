---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Give learners a report of their grader results while keeping hidden test cases hidden.

## Scope in / Scope out

Add a case result model and a function that builds the learner report. Counts and score include every case. The `cases` list includes only visible cases, in input order. Each listed case has a name, pass status, and feedback. The summary contains aggregate counts only. Changes to test execution are out of scope.

## Scope fence

- `grader/report.py`
- `tests/test_report.py`

## Acceptance criteria

1. `passed` and `total` count all cases; `score` is their ratio rounded to three decimal places.
2. `cases` contains exactly the visible cases in input order, with their name, pass status, and feedback.
3. No hidden case name or feedback appears anywhere in the returned report, whether that case passes or fails.
4. `summary` has the form `<passed>/<total> checks passed`. With no cases, score is `0.0`.

## Verification

```sh
python -m pytest -q tests/test_report.py
```
