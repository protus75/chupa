---
id: declined-box-000065-039360fa
kind: declined
link: box-000065-039360fa
reopen_after_days: 90
---
A CLI provider's adapter is chosen by its configured provider name (`claude` or `codex`), and the section 15 provider schema has no `binary` or `adapter` key that would let an operator give a provider a different name. The note says this works today because every provider name matches its binary.

The note describes a possible future need, not a current fault. By its own account, the behavior is correct while provider names match binary names, which is true of every configured provider. No operator has asked to rename a provider, and nothing shows a wrong adapter being chosen at runtime. Adding a `binary`/`adapter` key now would be a speculative config knob, which engine conduct forbids without a real incident behind it. No open or merged ticket, and no registry record, covers this.

- Message text: 'Fine while names equal binaries; pin it in section 15 or add a key when an operator needs a renamed provider.'
- The message comes from bootstrap-ingest and reports no stage, outcome, or failure.
- Engine conduct: no speculative config knobs or metadata; every addition must cite the incident that earned it.

Message: box-000065-039360fa
