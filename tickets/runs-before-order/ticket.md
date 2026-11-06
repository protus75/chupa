---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/tickets.py
- chupa/drain.py
- chupa/scheduler.py
- tests/test_tickets.py
- tests/test_closed_sets.py
- tests/test_scheduler.py

## On-demand
- tests/test_drain.py
- docs/host-authoring.md
- docs/how-chupa-works.md

## Goal / Why
Tickets with no code dependency can be ordered only by `priority` (four levels) and then authored age. To put a new ticket ahead of specific queued tickets, an operator either edits those tickets or adds a `## Depends on` edge. A `depends` edge is a hard block: when the first ticket fails, every ticket behind it stops (2026-11-05).

After this change a ticket can carry an optional `## Runs before` section listing stems it should run ahead of. The hint is soft:
- among eligible tickets, a ticket runs before every stem it names;
- if it fails or is held, the named tickets run anyway;
- a new ticket can be injected into the order by writing only the new ticket.

## Scope in / Scope out
- In: `chupa/tickets.py`:
  - add `Runs before` to `OPTIONAL_SECTIONS` and a `runs_before: tuple[str, ...] = ()` field to `Ticket`;
  - parse it as bullets of stems, like `Depends on`: the item `none` is not allowed. A self-edge is refused, and a stem that does not resolve to an existing `tickets/<stem>/` dir is refused, each with a paved road;
  - at intake, refuse a cycle among `Runs before` edges over all on-disk tickets, using `depends_cycle`, with the road "drop the edge that inverts the intended order".
- In: one ordering function beside `sort_key` in `chupa/drain.py`, used by both the drain's `_select` and the serve scheduler's pick in `chupa/scheduler.py`:
  - it takes the eligible tickets and returns them ordered;
  - repeatedly take, in `sort_key` order, the first ticket that no remaining eligible ticket names in its `Runs before`;
  - edges to stems outside the eligible set are ignored, so a merged, failed, held, rejected or blocked ticket never delays another.

  Eligibility rules are unchanged.
- In: tests.
  - `tests/test_tickets.py`: parsing, self-edge, unknown stem, cycle refusal.
  - `tests/test_closed_sets.py`: the `OPTIONAL_SECTIONS` and `SECTIONS` pins.
  - `tests/test_scheduler.py` and `tests/test_drain.py`: a newer P2 ticket naming an older P1 ticket in `Runs before` is picked first. When it fails with no retry budget, the named ticket is picked next. An edge to a non-eligible stem changes nothing.
- In: docs.
  - `docs/host-authoring.md`: one bullet for `Runs before`, a soft order that never blocks, beside `Depends on`.
  - `docs/how-chupa-works.md`: section 3.1 lists the section; section 7.1 step 3 and the serve dispatch bullet in section 7.2 state the order.
- Out: `Depends on` semantics; eligibility; the merge queue's order; `chupa new` skeleton; Author and its spec.

## Scope fence
- chupa/tickets.py
- chupa/drain.py
- chupa/scheduler.py
- tests/test_tickets.py
- tests/test_closed_sets.py
- tests/test_scheduler.py
- tests/test_drain.py
- tests/test_lint_verb.py
- docs/host-authoring.md
- docs/how-chupa-works.md

## Acceptance criteria
1. A ticket with `## Runs before` and `- <existing stem>` parses with that stem in `runs_before`. A self-edge, an unknown stem, and a two-ticket `Runs before` cycle are each refused with a finding naming the section. Checked by `uv run pytest tests/test_tickets.py`.
2. Serve's scheduler and the drain both pick a P2 ticket that names an older eligible P1 ticket in `Runs before` before that P1 ticket. A test fails if the P1 goes first. Checked by `uv run pytest tests/test_scheduler.py tests/test_drain.py`.
3. When the hinting ticket fails with no retry budget, the drain's next pick is the named ticket, not a stall. Checked by `uv run pytest tests/test_drain.py`.
4. A `Runs before` edge to a merged or held stem leaves the pick order equal to plain `sort_key` order. Checked by `uv run pytest tests/test_scheduler.py`.
5. `docs/host-authoring.md` and `docs/how-chupa-works.md` sections 3.1, 7.1 and 7.2 describe `Runs before`.
6. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest tests/test_tickets.py tests/test_closed_sets.py tests/test_scheduler.py tests/test_drain.py
uv run pytest -q
```

## Definition of rejected
A `Runs before` edge that blocks a pick; two ordering implementations for drain and serve; a frontmatter field instead of a section; any change to `Depends on` or eligibility.

## Time budget
- expected: 60m
- stuck: 150m
