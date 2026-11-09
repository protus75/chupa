---
id: tombstone-box-000257-19cd5537
kind: tombstone
link: declined-box-000151-d206f44b
reopen_after_days: 90
---
The note says that when a premise park is released, the re-offer draws a `retry` cap unit. Section 11.1 charges `premise_failed` to the `premise_bounce` cap instead, so a stem with no retries left would stay parked even after its ticket was edited. It asks the re-offer to draw `premise_bounce`. Registry record 000151 already covers this same request.

This is the same request as registry record declined-box-000151-d206f44b: the premise-park re-offer should draw `premise_bounce` rather than `retry` so a stem with spent retries can be released by a ticket edit. That record found current code already does this. The open ticket `reoffer-infra-no-retry-draw` also says `premise_failed` re-offers skip the retry draw because the runner draws `premise_bounce`.

- declined-box-000151-d206f44b: same premise-park re-offer retry-draw gap, found already fixed in current code
- open ticket reoffer-infra-no-retry-draw: 'premise_failed re-offers skip the retry draw because the runner draws premise_bounce'

Message: box-000257-19cd5537
