---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Add a serializer for the public user-profile API. The existing `profiles` package stores profile records as dictionaries; the API needs a stable response shape that does not expose stored fields outside its public contract.

## Scope in / Scope out
In: serialize a profile's ID, handle, display name, optional avatar URL, and public links. Each serialized link contains only `rel` and `url`, in stored order. Out: changing storage or API routing.

## Scope fence
- `profiles/serializers.py`
- `tests/test_public_profile_serializer.py`

## Acceptance criteria
1. The response has exactly `id`, `handle`, `display_name`, `avatar_url`, and `links`.
2. A missing avatar URL is serialized as `null`.
3. Only links with `visibility` set to `public` appear, in stored order.
4. Each link has exactly `rel` and `url`; other stored fields, including credentials, do not appear.

## Verification
`pytest -q tests/test_public_profile_serializer.py`
