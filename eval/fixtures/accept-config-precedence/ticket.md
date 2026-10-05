---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add a small loader that combines string settings from defaults, an optional JSON file, and environment variables.

## Scope in / Scope out
Implement `load_config(defaults, file_path, environ)` for lowercase ASCII setting names. The JSON file contains an object; values for known settings are strings. Environment keys use the `APP_` prefix and uppercase setting name. Keep value parsing, type coercion, and nested configuration out of scope.

## Scope fence
- `config.py`
- `tests/test_config.py`

## Acceptance criteria
1. Return a new dictionary without mutating `defaults`; a missing file contributes no values.
2. File values override defaults for known settings, and unknown file keys are ignored.
3. Environment values override file values and defaults for known settings. Copy those values verbatim, including leading and trailing spaces.
4. Raise `ValueError` when the file contains a JSON value other than an object or a non-string value for a known setting.

## Verification
`python -m pytest -q tests/test_config.py`
`python -m pytest -q`
