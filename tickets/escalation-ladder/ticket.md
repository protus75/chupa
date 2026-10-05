---
state: confirmed
source: seed
priority: P1
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- reject-queue-verbs

## Context
- chupa/llm.py
- tests/test_terminal.py
- chupa/runner.py
- chupa/drain.py

## On-demand
- chupa/stages.py

## Plan contract
- 19.L
- 19.P2
- section 11

## Goal / Why
Every diagnosed non-ok terminal is dispatched deterministically on its verdict (section 11.4):
- `retry` re-runs at the same capability.
- `escalate` climbs the capability ladder one rung, model-first.
- `split`, `reject`, `abandon-human`, and an exhausted ladder route to the Reject queue.
- An identical wall climbs instead of retrying.

In the bootstrap drain, a Reject arrival whose budget remains auto-resolves to keep, so the headless drain never waits on a human verdict.

Why: `spine-diagnosis` journals a closed verdict, but nothing acts on it. Every verdict re-offers at the authored capability until a cap runs out, so a hard ticket burns its whole budget at a tier that cannot land it. `reject-queue-verbs` built the queue, its fold, and its release verbs. This seed is the router that feeds it. The pre-ladder tier rule (19.L) ends when this merges.

Owners (section 9 ownership law, 19.P2 LADDER): `chupa/runner.py` owns the terminal handler and so the dispatch decision on the terminal body. `chupa/caps.py` owns the rung, which rides the `retry` `cap_consumed` body through the existing `consume` writer and is folded by the one lineage fold. It never has a copy in `chupa/drain.py`. `chupa/drain.py` owns the re-offer draw and the auto-keep. `chupa/stages.py` is the stage layer whose outcomes feed the terminal. `chupa/providers.py` `resolve` is read only, to tell models apart.

## Scope in / Scope out
- In: `chupa/caps.py`:
  - `LEVELS = ("low", "medium", "high", "max")`, the one ordered scale shared by tier and effort.
  - `consume(..., rung=None)`: a rung (`{"tier": ..., "effort": ...}`) is accepted only for the `retry` cap (otherwise `ValueError`) and adds `"rung"` to the body.
  - `capability(ticket, events) -> tuple[str, str]`: the effective (tier, effort). It is the authored frontmatter, replaced by the rung of the stem's latest rung-carrying `retry` draw that falls inside the fold (after the latest operator keep, which resets rungs as it resets caps). `ticket.md` is never edited.
  - `next_rung(config, tier, effort) -> dict | None`, MODEL-FIRST. A tier above `tier` counts only when `resolve(config, t, "implement")` gives a (provider, model) different from the current tier's; a tier with no routing row counts as no model. Take the lowest such tier, keeping the effort. Failing that, raise the effort one level. At `max` effort with no higher model, return None: the ladder is exhausted.
- In: `chupa/runner.py` `drive`:
  - Before `run_stages`, it replaces the ticket's tier and effort with `capability(...)`, so Implement, Review, and diagnosis all run at the effective rung.
  - Every non-ok terminal body gains `"reason"`, the code-only comparison key. It is the sorted unique finding codes of the terminal result joined by `,`, or the terminal state name when there are none.
  - A terminal with a diagnosis record also gains `"dispatch"`, one of `retry | escalate | reject_queue`, decided in this order:
    1. A spent cap routes to the queue exactly as `reject-queue-verbs` does.
    2. `split`, `reject`, and `abandon-human` (mechanical records included) route to the queue (pre-Rework fail-closed split, section 11.4).
    3. `retry` becomes a climb when the previous terminal of the lineage was dispatched `retry` with the same `reason`, or when this and the previous `IDENTICAL_K - 1` terminals share one `reason` (`IDENTICAL_K = 3`).
    4. `escalate` and a climb take `next_rung(...)` from the current capability: a rung gives `dispatch: escalate` with `"rung"` on the body, and None routes to the queue.
    5. Otherwise `dispatch: retry`.
  - Routing sets `"routed": "reject_queue"`.
  - A terminal with no diagnosis record (`budget_exceeded`, an over-bound render) gains neither `dispatch` nor a rung.
- In: `chupa/drain.py`:
  - A re-offer whose latest terminal body carries `rung` passes it to the `retry` draw: `consume(..., "retry", sha, rung=body["rung"])`.
  - AUTO-KEEP (section 11.4's pre-daemon default): at re-offer selection, a stem awaiting a verdict whose `spent(...)` is None gets ONE `{"signal": "reject_verdict", "verdict": "keep", "actor": "machine"}` and is re-offered like any parked stem, drawing one `retry` unit. A stem with a spent cap stays in the queue and is reported, never auto-kept. The machine keep never bounds the fold.
- In: the tests this behavior contradicts are adapted, with no assertion weakened:
  - `tests/test_terminal.py`'s exact terminal bodies gain `reason` and, when diagnosed, `dispatch`.
  - `tests/test_diagnose.py` and `tests/test_reject_queue.py` adapt only where a dispatch field, a rung, or an auto-keep now appears.
- Out: Rework and a real `split` (Phase 3: until then `split` goes to the queue), the drought exemption and the fleet-wide drought escalation (no drought classification exists yet), and oscillation detection over alternating snag lists beyond the identical-reason rule.
- Out: any change to the diagnosis call, the verdict vocabulary, `confirm`/`reject`, or `config.yaml`.

## Scope fence
- chupa/caps.py
- tests/test_caps.py
- chupa/runner.py
- chupa/stages.py
- chupa/drain.py
- tests/test_ladder.py
- tests/test_terminal.py
- tests/test_diagnose.py
- tests/test_reject_queue.py

## Acceptance criteria
1. `tests/test_ladder.py` proves `next_rung` over a config whose `implement` models are A at low and medium, B at high, and B at max. From (low, medium) it climbs to (high, medium), skipping medium's same model. From (high, medium) it gives (high, high), because max shares B. From (high, max) it returns None. A tier with no routing row is skipped.
2. `tests/test_ladder.py` drives `drain` with a FakeLLM. The first attempt fails review, and diagnosis says `escalate`. The terminal body carries `dispatch: escalate` and a rung. The re-offer's `retry` `cap_consumed` carries that rung, and the second Implement request is made at the rung's tier and effort. `ticket.md` is byte-unchanged.
3. `tests/test_ladder.py` proves routing. `reject`, `abandon-human`, and `split` verdicts each terminal with `routed: reject_queue`. An `escalate` at the exhausted top rung routes too. In each case, with budget remaining, the same drain journals one machine `reject_verdict` keep and re-offers the stem once with one `retry` draw, and `remaining` still counts every pre-keep draw.
4. `tests/test_ladder.py` proves the identical wall. Two consecutive `retry`-dispatched terminals with the same `reason` make the second one climb (`dispatch: escalate`), and three identical reasons climb whatever the verdict says. When the climb has no rung, the stem routes to the queue.
5. `tests/test_ladder.py` proves an operator `confirm` resets the rung: the next attempt runs at the authored capability.
6. `tests/test_caps.py` proves `consume` refuses a rung on a non-`retry` cap, and that `capability` ignores rungs before the latest operator keep.
7. `uv run pytest -q tests/test_terminal.py tests/test_diagnose.py tests/test_reject_queue.py tests/test_drain.py tests/test_drain_reentry.py` passes. Every assertion is unchanged apart from the adaptations named in Scope in.
8. `uv run pytest -q` exits 0 with no test removed or skipped.

## Verification
```
uv run pytest -q tests/test_ladder.py tests/test_caps.py
uv run pytest -q tests/test_terminal.py tests/test_diagnose.py tests/test_reject_queue.py tests/test_drain.py tests/test_drain_reentry.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- The model's reply picks a tier, effort, or model, or a rung is written into `ticket.md`.
- A rung lives anywhere but the `retry` `cap_consumed` body, or a second fold reads it.
- A spent cap is auto-kept, or a machine keep bounds the fold.
- `split` re-runs anywhere except through the Reject queue.
- A verdict outside the closed vocabulary dispatches `retry`.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
