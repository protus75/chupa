---
id: declined-box-000048-07b9be14
kind: declined
link: box-000048-07b9be14
reopen_after_days: 90
---
`Redactor.scrub` in `chupa/redact.py` replaces each configured secret in turn, longest first. If the text contains two different secrets that overlap, such as the end of one being the start of the other, the first replacement removes the shared part and the second secret no longer matches. The rest of the second secret then stays in clear text. The proposal is to find every secret's match spans first, merge spans that overlap, and redact the merged spans.

The code does behave this way: `scrub` runs `str.replace` once per secret in sequence. But the leak only happens when two different configured provider credentials share a run of characters and appear overlapping in one captured stream. Secrets come from provider `auth` environment variables, which hold long random API keys, so that overlap does not happen in practice. Nothing shows it has ever happened or that a leaked tail was ever seen. Even then, the part left in clear is only a piece of one key, not the whole key. This is speculative hardening, not a current, harmful gap that can actually happen.

- chupa/redact.py:20 sorts secrets longest first, which only covers a secret nested inside a longer one
- chupa/redact.py:27-30 scrub runs str.replace once per secret in sequence, so overlapping matches are never merged
- chupa/redact.py:25 secrets are only provider auth env-var values (API keys)
- No incident, spool, or engine-log sample shows a partly redacted secret

Message: box-000048-07b9be14
