# Operator setup note (Phase 1 prerequisites, CHUPA_PLAN.md section 0)

Operator-owned truth for Phase 1 prompt 1's config.yaml. Use these values
verbatim; do not substitute placeholders for anything stated here.

Both providers are `kind: cli` on ambient CLI login: no `auth` block, no
env-var export, no API key anywhere. Each id below was smoke-tested headless
on this machine on 2026-10-05.

## Provider `claude` (kind: cli, binary `claude`)
- models_by_tier:
  - low: claude-sonnet-5-5
  - medium: claude-sonnet-5-5
  - high: claude-opus-5-5
  - max: claude-opus-5-5
- Its stream reports `total_cost_usd`, so no `est_cost_per_call_usd` is needed;
  if the schema requires one, use 1.00.

## Provider `codex` (kind: cli, binary `codex`, ChatGPT-account login)
- models_by_tier:
  - low: gpt-6-luna
  - medium: gpt-5.6-terra
  - high: gpt-6-sol
  - max: gpt-6-sol
- limits.est_cost_per_call_usd: 1.00 (no cost in its stream; flat subscription)
- Note: gpt-6.1-sol is NOT usable with a ChatGPT-account login (HTTP 400).

## Routing
- REVIEW: claude, pinned to claude-opus-5-5 at every tier (strongest model).
- AUTHOR: claude, inherits models_by_tier[tier].
- IMPLEMENT: codex, inherits models_by_tier[tier].
