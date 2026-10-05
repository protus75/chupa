---
state: confirmed
source: seed
priority: P2
kind: feature
agent_tier: medium
agent_effort: medium
---

## Depends on
- shakeout-merge

## Context
- chupa/providers.py
- chupa/driver.py

## Plan contract
- 19.L
- 19.P2
- section 6

## Goal / Why
The seventh and LAST shakeout battery group pins the provider layer (`chupa/providers.py`) with two members: agent-CLI auth expiry and a planted secret. They run through the production drain on the bench with zero human input. Its Check run re-confirms every prior entry and machine-produces the CUMULATIVE `shakeout-report.json` into its OUTBOX, the copy the Phase 2 exit reads.

Why: a dead credential never self-heals, so an expired agent login must surface as a classified non-ok naming the re-auth road, never an unclassified `infra_error` retried blind (section 6). A secret that reaches a ticket-plane artifact is permanent in git history. 19.P2 PROVIDER FAILURES pins the auth member: `to: infra_error` plus an `infra` `cap_consumed`, with the harvested finding carrying `auth_error` and the re-auth road.

Owners (19.P2 Emits, section 6): the classification is the provider's, so `chupa/providers.py` gains the one class this member pins. The driver owns the ONE mapping from a classified exception to a `Finding`, so `chupa/driver.py` is fenced for that mapping alone. A defect anywhere else is filed as a second problem and the ticket replies `premise_failed`, naming it.

## Scope in / Scope out
- In: `chupa/providers.py`:
  - `ProviderCallError` gains `failure_class: str | None` and `paved_road: str | None`. `failure_class` is `auth_error` or None (unclassified).
  - Each `CliAdapter` subclass declares `AUTH_MARKERS` (lowercase substrings) and `LOGIN_ROAD`. Claude: markers `invalid api key`, `please run /login`, `not logged in`, `oauth token has expired`; road `run claude interactively and complete /login, then uv run python -m chupa drain`. Codex: markers `not logged in`, `401 unauthorized`, `token has expired`; road `run codex login, then uv run python -m chupa drain`.
  - A failed call whose lowercased stderr tail or failure message contains a marker raises `ProviderCallError` with `failure_class="auth_error"` and `paved_road=LOGIN_ROAD`. Every other failure stays unclassified, unchanged.
- In: `chupa/driver.py`: a `ProviderCallError` with a non-null `failure_class` ends the attempt `infra_error` with ONE finding: `code` the failure class, message the provider error, paved road the provider's road. An unclassified exception still carries no finding. The terminal reason stays code-only.
- In: `eval/shakeout/providers.py` with `MEMBERS`, in this order:
  - `auth_expiry`: (1) the bench's model seam is a production `ProviderLLM` over a scripted process seam whose `claude` child exits 1 with stderr `Invalid API key · Please run /login`. (2) The terminal is `infra_error` with one `infra` `cap_consumed` before it, and the harvested finding has code `auth_error` and the claude login road. (3) That harvested finding.
  - `planted_secret`: (1) the bench config declares a provider `auth: SHAKEOUT_SECRET`, the bench env carries a unique value for it, and the scripted Implement reply and its run record echo that value. (2) No committed file under `tickets/` and no journal line contains the value, and the run record carries `[REDACTED:SHAKEOUT_SECRET]` where it was echoed. (3) The committed `run.md`.
- In: `eval/shakeout/run.py`: `GROUPS` gains `"providers"` after `"merge"`. The group list is then complete.
- In: `tests/test_shakeout.py`: one test per member asserting its observable through `run_member`.
- Out: the rest of the failure vocabulary, failover, cooldowns, and the breaker (Phase 3 THRESH and Phase 4), the dead-credential push alert (Phase 4 notify), and any runner, bench, or schema edit beyond `GROUPS`.

## Scope fence
- chupa/providers.py
- chupa/driver.py
- eval/shakeout/
- tests/test_shakeout.py

## Acceptance criteria
1. The `python -m eval.shakeout.run --group providers` command in `## Verification` exits 0 and writes `tickets/shakeout-providers/shakeout-report.json` holding all eighteen battery members (every prior member re-confirmed plus `auth_expiry` and `planted_secret`), each `green`.
2. `uv run pytest -q tests/test_shakeout.py` passes with one test per member asserting its named observable.
3. `uv run pytest -q tests/test_providers.py tests/test_driver.py` passes with no edit.
4. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run python -m eval.shakeout.run --group providers --prior tickets/shakeout-merge/shakeout-report.json --out tickets/shakeout-providers/shakeout-report.json
uv run pytest -q tests/test_shakeout.py
uv run pytest -q tests/test_providers.py tests/test_driver.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- An unrecognized failure is classified `auth_error`, or the terminal reason carries the provider message.
- The secret value reaches any committed file or journal line.
- The report is written by anything but `write_report`, or committed on the branch.
- The diff touches a file outside the fence.

## Time budget
- expected: 75m
- stuck: 150m
