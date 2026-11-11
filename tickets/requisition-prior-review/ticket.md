---
state: confirmed
source: human
priority: P0
kind: bug
---

## Depends on
- none

## Context
- chupa/requisition.py::review_ticket
- chupa/runner.py::drive
- chupa/__main__.py::_review
- docs/how-chupa-works.md#6.7
- tests/unit/test_requisition_stage_events.py
- tests/regress_requisition_stage_events.py

## On-demand
- tests/integration/test_requisition_gate.py
- tests/integration/test_review_command.py

## Goal / Why
`chupa/specs/requisition_review.md` (Task section) tells the reviewer: "When a prior review is given, first rule each of its findings `cleared` or `standing` in your summary. Raise a NEW finding only against text the diff shows changed since that review." Its `prior_review` input is "Your prior review of this ticket and the diff from the text it judged (`none` on a first review)". That is what makes repeated reviews of an edited ticket converge. No production caller fills that input. `runner.drive` (the drain's review before dispatch) and `__main__._review` (the `review` verb) call `review_ticket` without `prior`, so `prior_review` always renders as `none`. The last caller that passed it was the seed path, deleted by `remove-seeding` (fcefd4f5).

On 2026-11-10 and 11, `commit-lock` was reviewed five times by the drain and four times by the `review` verb. Every prompt's `prior_review` block read `none`, and every round found a different set of problems. The fifth drain review opened with "First review, so there are no prior findings to rule on" (see `evidence/prior-review-none.txt`). Five requisition snags used up the ticket's attempts before any code was written.

When this ticket is done, both callers pass the stem's last recorded review, with its findings and a diff from the text it judged, so the reviewer rules on its own earlier findings instead of starting cold.

## Scope in / Scope out
- In: `chupa/requisition.py` adds `async def prior_review(git, repo, events, stem, text) -> str`.
  - It takes the latest `requisition_verdict` signal for `stem` in `events` whose body has a `findings` key. When there is none, it returns `none`.
  - It reads the judged text with `git._run(repo, "show", body["ticket_sha"])`. `ticket_sha` is the committed `ticket.md` blob both callers already record.
  - It returns this text. Each finding is one line with its message on one line. `- none` stands in for an empty list, and `(unchanged)` for an empty diff:
    ```
    Verdict: <verdict>
    Findings:
    - [<code>] <message>

    Diff from the judged text:
    <difflib unified diff, judged -> current>
    ```
- In: `chupa/runner.py::drive` and `chupa/__main__.py::_review`:
  - Each passes `prior=await prior_review(...)` to its existing `review_ticket` call, with its own git, repo, journal history, stem and reviewed text.
  - Each adds `"findings": [{"code": f.code, "message": f.message} for f in <verdict>.findings]` to its existing `requisition_verdict` journal body.
  - Both changes sit inside existing statements: the `review_ticket` call and the `journal.append` dict. No new statement or branch lands in those files.
- In: `docs/how-chupa-works.md`, the "Premise park" bullet in section 6.7: after "Edit the committed ticket to release it", add one sentence. It says the next review receives the last recorded review's findings and the diff since, rules on them, and raises new findings only against changed text.
- In: the carried reproducer `tests/regress_requisition_prior_review.py` (see Regression). It is self-contained and imports nothing from `tests/`.
  - It builds a temp git repository with a config and one committed ticket.
  - It runs `chupa.__main__.main(["review", stem])` twice, with `chupa.__main__.ProviderLLM` patched to a `FakeLLM` that snags with a finding and then approves. It edits and commits the ticket in between.
  - It passes when the second rendered prompt's block between `<<chupa-data:begin prior_review>>` and `<<chupa-data:end prior_review>>` contains the first finding's message.
- Out:
  - `chupa/specs/requisition_review.md`, which already says what to do with a prior review.
  - `chupa/author.py` and `chupa/rework.py`. Author journals only approvals, and rework passes its own `prior`.
  - How many attempts a requisition snag costs.

## Scope fence
- chupa/requisition.py
- chupa/runner.py
- chupa/__main__.py
- docs/how-chupa-works.md
- tests/unit/test_requisition_prior_review.py
- tests/integration/test_requisition_gate.py
- tests/integration/test_review_command.py
- tests/regress_requisition_prior_review.py

## Acceptance criteria
1. New `tests/unit/test_requisition_prior_review.py` calls `prior_review` with in-memory `Event` lists and a fake git whose async `_run` returns judged text from a dict. It never touches disk, and it keeps the `test-gate.toml` floor of 22 for `chupa/requisition.py`. Cases:
   - No `requisition_verdict` for the stem returns `none`.
   - A verdict for another stem only returns `none`.
   - A verdict whose body has no `findings` key returns `none`, not a block with `- none`.
   - A snag with finding `[fence_gap] missing x`, judged text `a\n`, and current text `a\nb\n` returns text containing `Verdict: snag`, `- [fence_gap] missing x` and `+b`. The fake git received `("show", <that ticket_sha>)`.
   - With two verdicts for the stem, only the later one's findings appear.
   - An approve with `findings: []` on unchanged text returns text containing `- none` and `(unchanged)`.
2. `tests/integration/test_requisition_gate.py::test_edit_releases_and_reviews_the_new_content` also asserts:
   - The first `requisition_review` request's `prior_review` block is `none`.
   - The second request's block contains `missing required file` and `+Edited content.`, not `none`.
   - The journaled snag verdict's `findings` equals `[{"code": "missing_file", "message": "missing required file"}]`.
3. A new test in `tests/integration/test_review_command.py` runs `review` (snag with a finding), edits and commits the ticket, then runs `review` again (approve). The first request's `prior_review` block is `none`. The second's contains the first finding's message.
4. The Regression command prints `{"regression_result": "pass"}` and exits 0 on the branch, and prints `defect` with a non-zero exit at the merge base.
5. `docs/how-chupa-works.md` section 6.7's "Premise park" bullet says the next review receives the last review's findings and the diff since.
6. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
- A requisition review from `runner.drive` or the `review` verb renders `prior_review` as `none` when the stem has a recorded verdict with findings.
- `chupa/specs/requisition_review.md` changes.
- Review findings are stored anywhere other than the `requisition_verdict` signal body.

## Time budget
- expected: 45m
- stuck: 90m

## Regression
```
uv run python tests/regress_requisition_prior_review.py
```
- carries: tests/regress_requisition_prior_review.py
