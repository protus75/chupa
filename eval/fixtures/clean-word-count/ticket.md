---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add `word_count(text)` so the editor status bar can display a word total.

## Scope in / Scope out
In: a Python helper that counts whitespace-separated words and focused tests. Out: status bar UI changes and text normalization.

## Scope fence
- `editor/__init__.py`
- `editor/status.py`
- `tests/test_status.py`

## Acceptance criteria
1. `word_count` is importable from `editor.status` and returns an integer.
2. Empty and whitespace-only strings return 0.
3. Each nonempty run of characters separated by Python Unicode whitespace counts as one word, including when separators are consecutive.
4. Punctuation within a run, or forming a run by itself, does not change that run's count.

## Verification
`python -m pytest -q tests/test_status.py`
