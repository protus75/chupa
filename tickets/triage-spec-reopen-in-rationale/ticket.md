---
priority: P2
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- none

## Context
- tests/integration/test_triage.py

## On-demand
- chupa/specs/triage.md

## Goal / Why
Triage needed a second paid call six times in the retro/31 window (`llm/triage/6`, `7`, `33`, `36`, `38`, `44` each have a `.../2` call) because the first reply put prose outside the single JSON object. Five added a trailing "Reopen if ..." paragraph after the object; two (7, 38) added leading commentary. The `## On-failure` section of `chupa/specs/triage.md` says to "explain what evidence would reopen it" but never says where that text goes, so the model writes it as free prose beside the JSON.

After this change `## On-failure` says the reopen condition goes inside the `rationale` field, and `## Output format` says nothing, including prose and code fences, may appear before or after the object. The success measure is a lower share of `llm/triage/N` keys with a `/2` call in the next retro window. The change fixes where the reopen text goes; it does not drop reopen guidance or require longer rationales.

## Scope in / Scope out
- In: `chupa/specs/triage.md`. In `## Output format`, add a sentence containing the exact phrase "Nothing may appear before or after the object, including prose and code fences". In `## On-failure`, replace "explain what evidence would reopen it" so the sentence contains the exact phrase "put the reopen condition inside `rationale`". Keep `version: "1.0"` (verdict records and tests pin it).
- In: `tests/integration/test_triage.py`: add one test that reads `chupa/specs/triage.md` and asserts both exact phrases are present.
- Out: engine code, the reply schema, the `## Task` rules, rationale length requirements, and the spec version.

## Scope fence
- chupa/specs/triage.md
- tests/integration/test_triage.py

## Acceptance criteria
1. `chupa/specs/triage.md` contains both exact phrases; the new test in `tests/integration/test_triage.py` fails on the unchanged spec, which lacks them.
2. `./dev.py test tests/integration/test_triage.py` passes, so the spec still loads and `version: "1.0"` is unchanged.
3. `./dev.py test tests/unit/test_specs.py` passes.

## Verification
```
./dev.py test tests/integration/test_triage.py
./dev.py test tests/unit/test_specs.py
```

## Definition of rejected
The change edits engine code or the reply schema, changes the spec version, removes the reopen guidance, or requires longer rationales.

## Time budget
- expected: 10m
- stuck: 30m
