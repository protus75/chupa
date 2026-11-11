---
priority: P1
kind: chore
agent_tier: medium
agent_effort: medium
source: box:retro_finding
state: draft
---

## Depends on
- none

## Context
- tests/unit/test_specs.py::test_review_spec_read_only
- tests/integration/test_stages.py::test_implement_check_review_all_ok_with_artifacts_and_provenance

## On-demand
- chupa/specs/review.md

## Goal / Why
Review replies often put text outside the single JSON object, although `chupa/specs/review.md` says "ONLY one JSON object, no prose before or after". Each such reply costs an extra paid Review call. In the retro window (retro/40), `requisition-prior-review` review/0/1 opened with a markdown verdict heading and bullets before a fenced JSON block. Calls 0/2 and 0/3 still opened with a sentence, and only 0/4, plain JSON, was accepted: three extra calls. `stale-running-after-kill` review/1/1 wrapped its JSON in a preamble and ended with a `Still open:` list. That list is a chat-session rule from the host CLAUDE.md that ticket agents skip. Review was called again. Replies that were only JSON, or one fenced JSON block, were accepted in one call.

The merged `requisition-review-bare-json-reply` ticket applied the same first-character rule to `chupa/specs/requisition_review.md` after the same failure. This ticket does the same for review.md. It does not change the re-prompt path (`review-reprompt-invalid-reply`).

Overcorrection risk: reviewers may cram reasoning into a long `summary`. The spec must keep `summary` to one sentence and put defects and non-blocking notes in `findings`.

## Scope in / Scope out
- In: `chupa/specs/review.md`. In `## Output format`, after the opening line, add a sentence containing the exact phrase "The first non-whitespace character of your reply is the opening brace of the object or of one json code fence." Add another sentence containing the exact phrase "Commentary, including host chat-conduct conventions such as Still open: lists, belongs in summary or nowhere." Add a third sentence containing the exact phrase "Keep `summary` to one sentence and put every defect in `findings`." Bump `version` from `1.4` to `1.5`. The spec stays within `SPEC_MAX_LINES`.
- In: `tests/unit/test_specs.py`: `test_review_spec_read_only` and `test_review_spec_checks_docs` pin version `1.5`, and `test_review_spec_read_only` also asserts all three exact phrases appear in the whitespace-normalized spec body.
- In: `tests/integration/test_stages.py`: the `spec_version` assertion in `test_implement_check_review_all_ok_with_artifacts_and_provenance` moves to `1.5`.
- Out: the reply parser or schema, the allowed verdicts and finding fields, the `## Task` rules, and any engine code.

## Scope fence
- chupa/specs/review.md
- tests/unit/test_specs.py
- tests/integration/test_stages.py

## Acceptance criteria
1. `chupa/specs/review.md` contains all three exact phrases (the first-character rule, the commentary rule, and "Keep `summary` to one sentence and put every defect in `findings`.") and `version: "1.5"`.
2. `tests/unit/test_specs.py` asserts all three phrases, and `./dev.py test tests/unit/test_specs.py` passes. The phrase assertions fail on the unchanged spec, which lacks them, so a spec left unedited, or one missing the summary-length sentence, cannot pass.
3. `tests/unit/test_specs.py` and `tests/integration/test_stages.py` pin `1.5`, so a spec left at `1.4` fails `./dev.py test tests/integration/test_stages.py`.
4. `./dev.py test` passes.

## Verification
```
./dev.py test tests/unit/test_specs.py tests/integration/test_stages.py
./dev.py test
```

## Definition of rejected
The change edits engine code or the reply parser, loosens the reply schema to accept prose or fences beyond one json code fence, changes the allowed verdicts or finding fields, or alters the `## Task` rules.

## Time budget
- expected: 15m
- stuck: 40m
