---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why

Add a date-range conflict check so the room-booking service can reject stays that share any calendar date with an existing booking for the same room. Booking dates are inclusive.

## Scope in / Scope out

In: Add a booking record and a function that checks a candidate stay against existing bookings. Reject a candidate whose start is after its end.

Out: Persistence, time-of-day handling, and booking creation.

## Scope fence

- `room_booking/availability.py`
- `tests/test_availability.py`

## Acceptance criteria

1. A candidate conflicts when it shares any date with a booking for the same room, including either endpoint and a single-day stay.
2. Bookings for other rooms do not cause a conflict.
3. Separated date ranges and an empty booking collection return `False`.
4. A candidate whose start is after its end raises `ValueError`.

## Verification

`python -m pytest -q tests/test_availability.py`
