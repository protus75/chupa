---
state: confirmed
source: seed
priority: P1
kind: feature
agent_tier: high
agent_effort: medium
---

## Depends on
- spine-caps

## Context
- chupa/runner.py
- chupa/git.py
- chupa/artifacts.py
- tests/test_git.py
- tests/test_terminal.py
- tests/test_drain_reentry.py

## On-demand
- chupa/stages.py

## Plan contract
- 19.L
- 19.P2
- section 11
- section 10

## Goal / Why
Every non-ok run terminal runs section 11.2's fixed handler: harvest -> dispatch -> journal -> wipe. Harvest is a fail-closed ALLOWLIST extraction, ticket-plane committed to `tickets/<stem>/attempts/<n>/harvest.json`. The next attempt's Implement render shows that harvest inside the existing prior-attempts block.

Why: today a non-ok terminal leaves the worktree in place and the next attempt sees only the prior terminal's durable findings artifact (Phase 1). A timeout or provider crash writes no findings artifact, so attempt two repeats attempt one's dead ends blind. The worktree holds the only copy of that material and dies at teardown-and-create. Harvest EXTENDS the section 11.2 rendering seam `prior_attempts` in `chupa/stages.py`. It is never a second render path. The diagnosis call (next seed batch) reads this harvest, so the harvest must exist first.

Owners (section 9 ownership law): `chupa/runner.py` owns the terminal handler (`drive`) and the harvest extraction it invokes. `chupa/stages.py` owns the ONE stage-terminal outbox lift (`lift_outbox`), which harvest reuses for its commit, and the prior-attempts render. `chupa/git.py` owns the new `diff --stat` op. `chupa/artifacts.py` owns the closed `Harvest` schema.

## Scope in / Scope out
- In: `chupa/artifacts.py` gains a closed pydantic `Harvest` model. Unknown keys are refused. Its fields, exactly:
  - `attempt` (the run sequence `<n>`)
  - `stage` (nullable: an orphan reap has no terminal stage)
  - `terminal` (the run's terminal state, a member of `TERMINAL_STATES` in `chupa/journal.py`)
  - `findings` (structured `Finding`s from the terminal StageResult)
  - `reason` (nullable: set only when `findings` is empty)
  - `diff_stat`
  - `stage_log_tail`
  - `events_tail`
  - `wall_seconds` (nullable: unknown for an orphan reap)
  - `usd` (nullable: unknown for an orphan reap)
  - `run_record` (nullable repo-relative path)
- In: `chupa/git.py` gains `diff_stat(dir, base, stem)`, which runs `diff --stat <base>...<stem>` (names and counts only, never content). It refuses option-shaped refs like the existing diff ops.
- In: in `chupa/runner.py` `drive`, a non-ok terminal runs, in order:
  1. Harvest: build the `Harvest`, write it to the worktree outbox `tickets/<stem>/attempts/<n>/harvest.json`, and commit it through `lift_outbox(ctx, stem, "harvest", attempt=n)`. That gives one ticket-plane commit with subject `chupa(<stem>): harvest`.
  2. The merged infra draw (`chupa/caps.py`).
  3. The terminal `state_transition`.
  4. `git worktree remove` + `prune` of `<worktree_root>/<stem>`. The branch is kept.
- In: how each harvest field is sourced:
  - `reason` is set only when `findings` is empty. It is the newest `error.txt` text under the attempt spool `<state_dir>/spools/<stem>/<n>/`, else the terminal state's name.
  - `stage_log_tail` is the last `HARVEST_TAIL_CHARS` characters of the attempt spool's files concatenated in sorted path order.
  - `events_tail` is the last `HARVEST_TAIL_CHARS` characters of the most recently modified `events.jsonl` under `<state_dir>/spools/providers/<stem>/`, or `""` when there is none.
  - `wall_seconds` and `usd` are summed over the run's stage results.
  - `run_record` is `tickets/<stem>/run.md` when that file exists after the lift.
  - `HARVEST_TAIL_CHARS = 4_000` is an engine constant in `chupa/runner.py`.
  - The unreviewed code diff never enters the harvest.
  - The extraction and commit are ONE function in `chupa/runner.py`, so the orphan-harvest seed reuses it rather than copying it.
- In: harvest is SOFT. Any harvest exception journals one `signal` `{"signal": "harvest_failed", "error": "<type>: <message>"}` on the stem, and dispatch, journal, and wipe proceed. SETUP-DEATH short-circuit: when the stem's worktree does not exist, harvest is skipped. A `merged` or `already_satisfied` run harvests nothing.
- In: `prior_attempts` in `chupa/stages.py` appends the PRIOR terminal's harvest (the one whose `attempt` equals that terminal's run sequence) to the existing block, after the findings items. The appended material is: its `reason`, `diff_stat`, `stage_log_tail`, and `events_tail`, marked untrusted data, with every line of each multi-line payload prefixed `> `. A payload line therefore can never open a ticket section heading, the same hazard `_one_line` guards. Each OLDER attempt with a harvest renders as one line naming its terminal, stage, and `tickets/<stem>/attempts/<n>/`, never its raw payload, so cumulative history stays bounded. The no-findings fallback line names `tickets/<stem>/attempts/<n>/` instead of the engine log when that harvest exists.
- Out: orphan harvest during reconcile-on-entry (the `spine-harvest-orphans` seed).
- Out: the diagnosis call, `lessons`, and their render form (the next seed batch).
- Out: Suggestion Box enqueue of second problems (the box seed).
- Out: attempt-keying the provider adapter's capture dir.
- Out: any change to the prior-attempts block's existing heading, head text, or findings item format.

## Scope fence
- chupa/runner.py
- chupa/stages.py
- chupa/git.py
- chupa/artifacts.py
- tests/test_git.py
- tests/test_harvest.py

## Acceptance criteria
1. `tests/test_harvest.py` drives `chupa.__main__.main(["run", ...])` with a FakeLLM to a review snag. Main then carries `tickets/<stem>/attempts/0/harvest.json` in a commit whose subject is `chupa(<stem>): harvest`. The file validates as `Harvest`, its findings equal the snag findings, and its `diff_stat` names the edited file. After the run the stem's worktree dir is gone and its branch still resolves.
2. `tests/test_harvest.py` proves the handler order from the journal: the harvest ticket-plane effect completion precedes the `infra` `cap_consumed` (on an `infra_error` run), which precedes the terminal `state_transition`. That run's `reason` carries the raising call's spooled error text, and its `findings` is empty.
3. `tests/test_harvest.py` proves the allowlist. The harvest's keys are exactly the `Harvest` field set. A unique marker string written only into the agent's code edit appears in no file under `tickets/<stem>/attempts/`. Each tail is at most `HARVEST_TAIL_CHARS` characters even when the spooled output is larger.
4. `tests/test_harvest.py` proves softness and the short-circuits. A harvest that raises journals `harvest_failed`, still journals the terminal, and `run` still exits 1. A missing worktree skips harvest. A merged run writes no `attempts/` dir.
5. `tests/test_harvest.py` drives the `drain` verb to re-offer a stem after an `infra_error` attempt. The re-offer's Implement render carries that attempt's harvest `reason` inside the prior-attempts block, between `## Acceptance criteria` and the next ticket section, with each payload line prefixed `> `. After two failed attempts, the older attempt appears as one line naming `tickets/<stem>/attempts/0/` and its raw tail does not.
6. `tests/test_git.py` covers `diff_stat`'s argv and its refusal of an option-shaped ref.
7. `uv run pytest -q` exits 0 with no test removed or skipped. `tests/test_terminal.py` and `tests/test_drain_reentry.py` pass unchanged.

## Verification
```
uv run pytest -q tests/test_harvest.py tests/test_git.py
uv run pytest -q tests/test_terminal.py tests/test_drain_reentry.py tests/test_caps.py
uv run pytest -q
```

## Definition of rejected
Reject the branch if any of these hold:
- Harvest copies the code diff or any non-allowlisted material.
- A second render path or a second ticket-plane commit path exists beside `prior_attempts` and `lift_outbox`.
- The worktree is wiped before the terminal is journaled, or the terminal is journaled before harvest.
- A harvest error stops the terminal.
- `ticket.md` is written.
- The diff touches a file outside the fence.

## Time budget
- expected: 90m
- stuck: 180m
