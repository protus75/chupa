---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
none

## Context
- chupa/__main__.py
- chupa/status.py
- chupa/journal.py
- chupa/tickets.py
- chupa/caps.py
- dev.py
- tests/test_status.py
- tests/test_cli.py
- docs/how-chupa-works.md

## Goal / Why
The operator has no way to see how the engine is doing over time: how long each stage takes, how many attempts a ticket needs, how often the ladder escalates, where failures land, or what a merge costs. `status` prints current state only, and the retro scorecard covers gates and review surfaces only. Asked for by the operator on 2026-11-06. A hand prototype over the live journal showed every figure below can be derived from the journal alone: implement p50 3.5m, 2.2 attempts per merged ticket, and 5 escalations in 7 days.

After this change `chupa stats [--window W] [--json]` prints a read-only health and efficiency projection of the journal over a window. `./dev.py stats` runs it. The JSON form feeds the VS Code extension in a later ticket.

## Scope in / Scope out
- In: new `chupa/stats.py`, a write-free fold of the journal, like `chupa/status.py`.
  - `project_stats(events, kinds, *, now, window) -> dict`. `kinds` maps stem to `feature` / `bug` / `chore`; a stem missing from it is `unknown`. It returns plain JSON-serializable data: dicts, lists, str, int, float, and None.
  - `render_stats(stats) -> str`: the text rendering, one titled block per top-level key.
- In: **Window.** `--window` takes `<N>h` or `<N>d` (time), or `<N>t` (tickets); default `7d`. `N` is a positive integer.
  - `h` and `d`: the window starts at `now - N` (`now` from the clock seam).
  - `t`: the window starts at the settle time of the N-th most recently settled stem. A stem settles at its latest `merged`, `already_satisfied`, or `rejected` transition. With fewer than N settled stems the window starts at the first journal event.
  - Every interval and count below counts only when its end event's `ts` is in the window: at or after the start, at or before `now`.
  - Per-ticket figures (`cycles`, `ladder.outcomes`) cover the stems that settled in the window and count those stems' whole journal history. An attempt that began before the window still counts.
- In: **Top-level keys** of the returned dict, in this order:
  - `window`:
    - `spec`: the argument as given;
    - `start` and `end`: ISO timestamps;
    - `events`: events in the window.
  - `throughput`:
    - `intake`: `ticket_intake` signals with `new: true`;
    - `settled`: counts of `merged`, `already_satisfied`, and `rejected` stems;
    - `merged_per_day`: merged divided by the window length in days, using a minimum length of 1 day.
  - `durations`: stage name to `{n, p50, p90, max}`, in minutes, rounded to 0.1. Stages with no samples are left out. Stage names:
    - `requisition_review`, `implement`, `review`, `diagnose`, `rework`, `retro`. One sample per stage instance: llm effect keys `llm/<stem>/<run_seq>/<surface>/<attempt>/<call>` grouped on everything but `<call>`. The sample runs from the first `effect_intent` to the last `effect_completion`. A group with no completion is skipped.
    - `attempt`: a stem's `running` transition to its next non-`running` transition.
    - `check`: inside one attempt, from the last `implement` completion to the next `review` intent, or to the terminal transition if none comes first.
    - `merge`: inside one attempt, from the last `review` completion to a `merged` transition, or to a terminal with `stage: merge`.
    - `lead_time`: a stem's first `ticket_intake` signal to its `merged` transition.
  - `cycles`: kind name (`feature`, `bug`, `chore`, `unknown`, and `all`) to:
    - `tickets`;
    - `attempts_mean` and `attempts_max`: `running` transitions per settled stem;
    - `review_snags_mean`: `gate_failed` terminals with `stage: review` per stem;
    - `first_pass_yield`: the share of merged stems with exactly one `running` transition, or None when nothing merged.

    Kinds with no settled stems are left out, except `all`.
  - `ladder`:
    - `escalations`: terminal transitions with `dispatch: escalate`;
    - `stems`: distinct escalated stems;
    - `rungs`: `"<tier>/<effort>"` to count, from each escalation's `rung`;
    - `outcomes`: for escalated stems that settled in the window, counts by settle state.
  - `failures`:
    - `terminals`: `"<to>@<stage>"` to count, for non-`running`, non-`merged` transitions (`stage` missing is `-`);
    - `reasons`: the 10 most common `reason` values, each cut to its first 80 characters, as `[reason, count]` pairs;
    - `dispatch`: `dispatch` value to count;
    - `diagnosis`: `diagnosis` signal `verdict` to count;
    - `rework`: `rework_order` signal `action` to count;
    - `requisition`: `requisition_verdict` signal `verdict` to count.
  - `holds`:
    - `reject_queue_arrivals`: terminals with `routed: reject_queue`;
    - `keeps`: `reject_verdict` signals by `actor`;
    - `abandoned`: `abandoned` transitions;
    - `droughts`: terminals with `reason: provider_drought`.
  - `spend`:
    - `usd`: the sum of completion `cost.usd`, as `status` sums it;
    - `usd_per_merge`: None when nothing merged;
    - `by_surface`: llm surface to usd;
    - `tokens`: `input` and `output` sums of `cost.input_tokens` and `cost.output_tokens` when present;
    - `provider_calls`: provider to `{calls, failures}`, from `provider_call_outcome` signals, where a failure has a non-null `failure_class`.
- In: `chupa/__main__.py`: a `stats` verb with `--window` (default `7d`) and `--json`. It takes no lock and runs no intake. It reads the journal through the checkout's `Journal` and `now` from the checkout clock.
  - `kinds` comes from each `tickets/<stem>/ticket.md` frontmatter `kind`, read with `chupa.tickets.split_frontmatter` and `yaml.safe_load`. A file that is missing or does not parse leaves the stem out.
  - A malformed `--window` is an engine refusal: exit 2, `chupa stats: bad window <value> -- use <N>h, <N>d, or <N>t`.
  - `--json` prints `json.dumps(stats)`; otherwise it prints `render_stats`.
- In: `dev.py`: `stats` subcommand passing `--window W` and `--json` through, with a docstring line.
- In: `docs/how-chupa-works.md` section 2.1 verbs table row for `stats`, and section 2.2 table row for `./dev.py stats`. Describe it as a projection, never an authority, like `status`.
- In: `tests/test_stats.py`. Build journals with `Journal.append` and a fake clock, as `tests/test_status.py` does. Cover:
  - stage durations, including `check` and `merge` derived from neighbouring events, with distinct per-stage times so a swapped stage fails;
  - an `h`/`d` window that excludes an older interval, and a `t` window whose start is the N-th most recent settle;
  - `cycles` by kind with two kinds that have different attempt counts, where `first_pass_yield` differs from 1 and 0;
  - `ladder` escalation counts and rungs;
  - `--json` output parsing as JSON with the top-level keys in order;
  - the bad-window refusal exit code and message;
  - `stats` writing nothing: the journal bytes are unchanged.
- Out: the VS Code extension, `status`, the retro, the scorecard, engine.log parsing, any new journal event, and any config key.

## Scope fence
- chupa/stats.py
- chupa/__main__.py
- dev.py
- docs/how-chupa-works.md
- tests/test_stats.py

## Acceptance criteria
1. `uv run pytest -q tests/test_stats.py` exits 0, including the tests above.
2. `--json` output's top-level keys are exactly `window`, `throughput`, `durations`, `cycles`, `ladder`, `failures`, `holds`, `spend`, in that order.
3. `docs/how-chupa-works.md` sections 2.1 and 2.2 list `stats`.
4. `uv run pytest -q` exits 0.

## Verification
```
uv run pytest -q tests/test_stats.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of the following holds:
- `stats` writes to the journal, takes the writer lock, or runs intake;
- a figure reads engine.log, spools, or anything but the journal and ticket frontmatter;
- a new journal event, signal, or config key is added;
- the clock is read outside the clock seam.

## Time budget
- expected: 60m
- stuck: 150m
