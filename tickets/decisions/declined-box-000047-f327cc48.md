---
id: declined-box-000047-f327cc48
kind: declined
link: box-000047-f327cc48
reopen_after_days: 90
---
`EngineLog.event` in `chupa/enginelog.py` runs the redactor over the line after `json.dumps` has encoded it. A secret containing a character JSON escapes (a quote, a backslash, a control character, or non-ASCII under the default ensure_ascii) would appear in the line only in escaped form, so the plain-text match would miss it and the secret would reach the engine log. The proposal is to scrub each field before encoding, or to also match the JSON-encoded form, and to add a test that pins the behavior.

The ordering exists in the code, but nothing current can trigger it. The only secrets the `Redactor` holds are provider API-key values, read from the env vars that `providers[].auth` names (`Redactor.from_config` in `chupa/redact.py`). Provider keys use URL-safe token alphabets with no characters JSON would escape, and the note itself says the gap is unreachable for them. That makes this speculative hardening with no reachable incorrect runtime behavior, which falls below the bar for authoring a ticket.

- chupa/enginelog.py:28 scrubs the result of json.dumps(record, default=str), so redaction runs on the encoded line
- chupa/redact.py:24-25 collects secrets only from provider `auth` env-var values
- The message itself says the gap is unreachable for URL-safe token alphabets
- No open or merged ticket or existing decision covers JSON escaping in engine-log redaction; decision-box-000045 covers only how EngineLog opens its file, not redaction

Message: box-000047-f327cc48
