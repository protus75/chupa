---
priority: P1
kind: chore
source: human
state: confirmed
---

## Depends on
- remove-plan-grammar

## Context
- docs/how-chupa-works.md

## On-demand
- chupa/box.py
- tests/test_box.py
- tests/test_storm_notification_activation.py
- tests/test_daemon_composition.py

## Goal / Why
`chupa/box.py` still carries the bootstrap conductor's hook: `python -m chupa.box` reads `bootstrap/suggestions.md` from the main checkout and files each line to the Suggestion Box (`ingest_main_checkout`, `ingest_bootstrap`). The `bootstrap/` folder is deleted and nothing else calls these. After this change the Suggestion Box has no bootstrap entry point; problems arrive only through the stages, triage, and the report inbox.

## Scope in / Scope out
- In: `chupa/box.py`: delete `BOOTSTRAP_ORIGIN`, `BOOTSTRAP_FILE`, `ingest_bootstrap`, `ingest_main_checkout`, the `if __name__ == "__main__":` block, and imports left unused.
- In: `tests/test_box.py`: delete `test_bootstrap_ingest_uses_main_checkout` and its imports.
- In: `tests/test_storm_notification_activation.py`: drop `"bootstrap"` and `"main-ingest"` from `SITES`, delete their branch in `exercise_site`, and drop the `ingest_bootstrap`/`ingest_main_checkout` imports. Origin strings such as `"bootstrap-ingest"` used as plain test data elsewhere stay.
- In: `tests/test_daemon_composition.py` `test_production_boxes_receive_rereport_callback`: drop the `"bootstrap"` and `"main-ingest"` sites.
- In: `docs/how-chupa-works.md` section 13: delete the bootstrap-files bullet (the folder and the box ingest).
- In: `tests/test_box.py` `test_signature_recipe`: replace `BOOTSTRAP_ORIGIN` with the literal `"bootstrap-ingest"`.
- Out: existing box messages on disk (their `bootstrap-ingest` origin is free text and stays readable), the merge admission reason `"bootstrap"` (it names inline admission and is journaled), every other box behavior.

## Scope fence
- chupa/box.py
- tests/test_box.py
- tests/test_storm_notification_activation.py
- tests/test_daemon_composition.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `grep -rn -E "ingest_bootstrap|ingest_main_checkout|BOOTSTRAP_FILE|BOOTSTRAP_ORIGIN|bootstrap/suggestions" chupa tests` prints nothing.
2. `uv run python -m chupa.box` no longer ingests anything: the module has no `__main__` block, checked by `grep -n "__main__" chupa/box.py` printing nothing.
3. `docs/how-chupa-works.md` section 13 has no bootstrap-files bullet.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_box.py tests/test_storm_notification_activation.py
uv run pytest -q
```

## Definition of rejected
Any box message file or journal record changes; the `"bootstrap"` merge admission reason changes; any other Suggestion Box behavior changes.

## Time budget
- expected: 20m
- stuck: 45m
