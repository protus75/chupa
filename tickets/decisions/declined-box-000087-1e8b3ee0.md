---
id: declined-box-000087-1e8b3ee0
kind: declined
link: box-000087-1e8b3ee0
reopen_after_days: 60
---
Ticket intake checks each `gate_bypass[].code` only against the engine's built-in gate codes, because intake does not load config. A ticket that bypasses a host-declared review-surface code registered in config would therefore be refused. The note asks to widen the check once a host ships its first such surface.

The note itself makes the change conditional on a host review surface that does not exist yet. The evidence names no host that declares config-registered gate codes and no ticket refused for bypassing one. The current check fails closed against the closed engine vocabulary, which is the intended behavior until a host vocabulary exists. With no reachable harm today, this is speculative hardening.

- The message says to widen the check 'when the first host surface ships', so no host surface exists today.
- No open or merged ticket, and no failure report, shows a ticket refused at intake for a host-declared gate_bypass code.
- Engine conduct requires closed vocabularies that fail closed, which is what the current ENGINE_GATE_CODES check does.

Message: box-000087-1e8b3ee0
