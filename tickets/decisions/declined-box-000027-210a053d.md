---
id: declined-box-000027-210a053d
kind: declined
link: box-000027-210a053d
reopen_after_days: 90
---
The bootstrap note said a routing candidate without a `model` key was rejected as a missing required key, even though the config contract lets a candidate leave `model` out and use its provider's `models_by_tier[tier]`. Current code already allows the omission, so the gap is gone.

In `chupa/config.py`, `Candidate.model` is now `str | None = None`, and a comment there says that when it is absent the provider's `models_by_tier[tier]` is used. A config.yaml whose candidate names only a provider no longer gets the missing-key error. The note's other point, that an explicit `model: null` is still refused, is hardening with no harm shown, because null and an omitted key both mean 'inherit'. No open or merged ticket stem clearly claims this change, so the verdict is decision, not tombstone.

- chupa/config.py:92-94 `class Candidate(_Strict): provider: str; model: str | None = None  # absent: the provider's models_by_tier[tier] serves`
- chupa/config.py:422-442: the cross-key checks for each candidate look only at `provider`, not `model`

Message: box-000027-210a053d
