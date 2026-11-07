---
id: decision-box-000022-a109febf
kind: decision
link: box-000022-a109febf
reopen_after_days: 90
---
The note asks for a written spec of which top-level config keys are required and which are optional with defaults. Today `chupa/config.py` decides this by itself: it requires the keys that have no stated default and uses the example YAML values as defaults for the rest. Nothing in the spec states the split, so the loader cannot be rebuilt from the spec alone.

This only asks for documentation to say what the code already does. The message shows no wrong runtime behavior: no config was wrongly rejected or accepted, and no default was wrong. It also targets section 15 of `CHUPA_PLAN.md`, which is frozen and never edited. Any home for this would have to be `docs/host-contract.md`, and with no harm shown, that is a wording preference, not a behavior gap.

- The message class is `suggestion` from `bootstrap-ingest`, with no stage, outcome, or failure report.
- The message itself says `config.py` already enforces a consistent split: keys with no stated default are required, and the rest default to the YAML example values.
- `CHUPA_PLAN.md` is a frozen design record (CLAUDE.md, 'The plan is the seed'), so the section 15 edit it proposes is not allowed.
- No open ticket, merged stem, or registry decision covers documenting the required/optional config key split, so this is not a duplicate.

Message: box-000022-a109febf
