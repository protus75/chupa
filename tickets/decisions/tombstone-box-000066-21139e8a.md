---
id: tombstone-box-000066-21139e8a
kind: tombstone
link: provider-cooldown-failover
reopen_after_days: 90
---
A bootstrap note said `ProviderCallError` carried only a return code and stderr tail with no failure class, and that the driver turned it into `infra_error` with no finding. It expected the closed failure vocabulary (rate_limited, quota_exhausted, outage, auth_error, model_error, unclassified) to arrive in Phase 4.

Phase 4 work, including the merged `provider-cooldown-failover` ticket, has already done this. `chupa/providers.py` defines the closed `FailureClass` literal. `classify_failure` builds `ProviderCallError` with a `failure_class` and a paved road. The driver, thresh and runner act on the class, for example on `quota_exhausted`. No gap remains to author.

- chupa/providers.py:34 FailureClass = Literal["rate_limited", "quota_exhausted", "outage", "auth_error", "model_error", "unclassified"]
- chupa/providers.py:390-404 classify_failure returns ProviderCallError(..., failure_class=failure, paved_road=road)
- chupa/driver.py:397 branches on exc.failure_class == "quota_exhausted"
- chupa/thresh.py:247 reads exc.failure_class, falling back to unclassified
- merged stems include provider-cooldown-failover and phase4-exit

Message: box-000066-21139e8a
