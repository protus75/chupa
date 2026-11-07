---
id: declined-box-000030-f689a116
kind: declined
link: box-000030-f689a116
reopen_after_days: 90
---
The config schema types `providers[].auth` as any string, but it is meant to hold the name of an environment variable. The proposal is to reject values that don't look like a variable name (`^[A-Z_][A-Z0-9_]*$`) when the config loads, so a key pasted in by mistake is refused before the redaction seam has to catch it.

This is speculative hardening with no incident behind it. The code already fails closed when a literal key is pasted. `chupa/providers.py` treats `auth` only as a lookup name in the environment. A pasted key won't match any variable, so preflight raises `ProviderSetupError` and the run stops before any provider call. The key never reaches a child process or the journal through the auth path. The worst current effect is that the pasted value is echoed in that setup error message, and nothing shows this has happened. The value also already sits in the operator's own `config.yaml`, so the config check would only move the refusal earlier and give a clearer error. That improves ergonomics; it does not repair harmful behavior.

- chupa/config.py:80 `auth: str | None = None` (shape is not validated)
- chupa/providers.py:87-90 uses `serving.auth` only as a key into the environment and raises ProviderSetupError when it is unset, so a literal key fails closed
- chupa/redact.py:25 builds redaction from `env[p.auth]`, which only applies to values that are names of set env vars
- The message comes from bootstrap-ingest and cites no incident where a literal secret was accepted, used, or leaked

Message: box-000030-f689a116
