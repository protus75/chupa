---
state: confirmed
source: human
priority: P0
kind: feature
---

## Depends on
- none

## Context
- chupa/docs/host-authoring.md
- chupa/author.py::author
- chupa/requisition.py::prior_review
- chupa/tickets.py::template
- tests/integration/test_author.py::test_author_reprompt_carries_previous_reply

## On-demand
- chupa/specs/author.md
- docs/how-chupa-works.md
- tests/unit/test_requisition_prior_review.py

## Goal / Why
Ticket authoring has one process: start from the skeleton `chupa/tickets.py::template` writes, follow `chupa/docs/host-authoring.md`, lint until clean, then run requisition review with the prior review until it approves. A chat session follows that process through `chupa new`, `chupa lint` and `chupa review`. The Author stage follows a second, drifting copy:

- Its rules are a hand-restated subset of the guide in `chupa/specs/author.md`. The copy lacks the guide's step 3 rule that every stated invariant needs a criterion whose test fails when it is dropped. It never sees the skeleton, so it guesses section grammar.
- Its review never receives the prior review. `chupa/author.py` passes the constant `prior=FIRST_REVIEW` to `review_ticket`, so each review of a redraft starts from scratch. `requisition-prior-review` wired the prior review into the drain and `chupa review` only, and `requisition-prior-required` let the Author stage satisfy the now-required argument with that constant.

So every authoring fix landed on the chat path and missed the Author stage. On 2026-11-13, box-000428-96d00473 spent its four Author calls like this. Call 1 failed lint three times: it listed a prompt spec under `## Context`, and wrote `## Time budget` as a sentence where the skeleton has two bullets. Call 3 failed lint on criteria with no backticked check. Calls 2 and 4 each drew an `invariant-without-test` snag. The stage then declined, losing a draft one finding from approval. Since 2026-11-11 the Author stage declined 10 of 22 messages it was invoked on, each on a requisition review finding.

When this ticket is done, the Author stage reads the same rules and skeletons a chat author reads, and its reviews get their prior review the same way `chupa review` does. A rule added to the guide reaches both authors with no second edit.

## Scope in / Scope out
- In: `chupa/author.py` renders two new Author spec inputs:
  - `guide`: the full text of `chupa/docs/host-authoring.md`, read from the installed package path `chupa new` prints.
  - `skeletons`: `chupa/tickets.py::template` output for `feature`, `chore` and `bug`, each labeled with its kind.
- In: `chupa/specs/author.md` declares the `guide` and `skeletons` data blocks. Role names them as chupa's own authoring rules and skeletons: the author follows them, and every other data block stays untrusted evidence.
- In: `chupa/specs/author.md` Task keeps only what is specific to the Author stage:
  - the frontmatter sentence (stamped `state` and `source`, no `gate_bypass`, `agent_tier` and `agent_effort` defaults);
  - the instruction to start from the skeleton for the chosen kind and follow the guide;
  - a statement that this stage runs the guide's `new`, `lint` and `review` steps and returns their findings in `retry_findings`;
  - the re-prompt rule (start from `previous_reply`, change only what the findings name).
  Every ticket-content rule paragraph is removed, including the version-bump paragraph and the mechanical preflight paragraph.
- In: a rule that is in `chupa/specs/author.md` but not yet in the guide moves into the guide's `Scope fence` bullet, so no rule is lost: grep the repo for each changed name or value, and the set-membership grep rule ("When Scope in adds, removes, renames, or moves a member of a set ... asserts against the changed set or hardcodes the moved path", with its not-a-hit exclusions).
- In: `chupa/specs/author.md` `version` goes to the next minor above the version on main, and the test pin follows. A changed Author spec version moves the review baseline from GO to REVOKED (`chupa/baseline.py` matches recorded spec versions), so Author tickets start `draft` until the baseline is re-recorded. That is the existing, intended behavior for any Author spec change.
- In: `chupa/requisition.py` splits the rendering in `prior_review` into a pure function. It takes the verdict, the findings and the judged text, and renders them with the diff to the current text, in the exact format `prior_review` emits today. `prior_review` calls it.
- In: in `chupa/author.py`, the first review in an Author run passes `FIRST_REVIEW`. Each later review passes that function's rendering of the previous review in the same run (its verdict, its findings and the candidate text it judged). `chupa/author.py` no longer imports `FIRST_REVIEW` for any other use.
- In: `tests/integration/test_author.py`: `test_author_spec_requires_criteria_to_name_wrong_results` and `test_author_spec_states_ticket_rules` stop asserting rule text in the spec body and assert the criteria below instead.
- In: `docs/how-chupa-works.md` section 9.3: the Author prompt embeds the authoring guide and skeletons, and each later review gets the previous review.
- In: `CLAUDE.md` and `AGENTS.md`, section A, outside the managed block, gain one rule. This is a rule about chupa's own code, so its home is those two files, not `CORE_TEMPLATE`: "**One authoring process.** Ticket content rules live only in `chupa/docs/host-authoring.md`, and ticket format only in `chupa/tickets.py`. Every authoring surface (a chat session, the Author stage, any future one) reads those, and a prompt spec embeds the guide and skeletons rather than restating them. A fix to authoring changes that one source." Its Why line cites the 2026-11-13 box-000428 decline and the 10 of 22 Author declines since 2026-11-11.
- Out: the Author call cap, `AuthorGate` checks, decline handling, and re-authoring earlier declined messages.
- Out: `chupa/specs/requisition_review.md` and the managed `CORE_TEMPLATE` block.

## Scope fence
- chupa/author.py
- chupa/specs/author.md
- chupa/docs/host-authoring.md
- chupa/requisition.py
- tests/integration/test_author.py
- tests/unit/test_author.py
- tests/unit/test_requisition_prior_review.py
- docs/how-chupa-works.md
- CLAUDE.md
- AGENTS.md

## Acceptance criteria
1. `tests/integration/test_author.py` has a test showing that the first Author prompt holds the full text of `chupa/docs/host-authoring.md`, byte for byte, inside its `guide` data block. It also holds `template("feature")`, `template("chore")` and `template("bug")` inside its `skeletons` data block. This rules out a prompt that carries a restated subset of the rules or no skeleton.
2. `tests/integration/test_author.py` asserts that the `chupa/specs/author.md` body contains none of "the next minor above the version on main", "criterion checked by a test names the wrong result" or "adds, removes, renames, or moves a member of a set", and that `chupa/docs/host-authoring.md` contains all three. This rules out a second copy of the rules in the Author spec, and rules out losing the set-membership rule in the move.
3. `tests/integration/test_author.py` has a test of an Author run in which the first candidate's review returns `snag` with a finding whose message is a unique marker, and the second candidate is approved. The first `requisition_review` prompt's `prior_review` block equals `FIRST_REVIEW`. The second one contains the marker and a `+` diff line from the changed candidate text. This rules out a constant `prior` on every Author review.
4. `tests/unit/test_requisition_prior_review.py` asserts that the new pure rendering function gives the same string `prior_review` returns for the same verdict, findings, judged text and current text. Its existing tests pass unchanged. This rules out the Author stage and `chupa review` rendering the prior review in two different formats.
5. `tests/unit/test_author.py` has a unit test that runs the new `chupa/author.py` lines with fakes, for `chupa/author.py`'s unit coverage floor. It stubs `review_ticket` to record `prior` across two candidates in one Author run, and asserts the first is `FIRST_REVIEW` and the second carries the first review's finding message. It also renders the Author inputs and asserts the `guide` and `skeletons` blocks are present. This rules out new Author lines that only integration tests reach.
6. The `version` in `chupa/specs/author.md` is the next minor above the version on main, and `tests/integration/test_author.py` pins it, which rules out a stale pin.
7. `CLAUDE.md` and `AGENTS.md` each contain the sentence "Ticket content rules live only in `chupa/docs/host-authoring.md`, and ticket format only in `chupa/tickets.py`." outside the managed block.
8. `docs/how-chupa-works.md` section 9.3 no longer says "The Author prompt states the ticket section rules", and says the Author prompt embeds the authoring guide and skeletons.
9. `./dev.py test tests/integration/test_author.py tests/unit/test_author.py tests/unit/test_requisition_prior_review.py tests/unit/test_requisition_stage_events.py tests/integration/test_baseline.py` exits 0.

## Verification
```
./dev.py test tests/integration/test_author.py tests/unit/test_author.py tests/unit/test_requisition_prior_review.py tests/unit/test_requisition_stage_events.py tests/integration/test_baseline.py
```

## Definition of rejected
- `chupa/specs/author.md` still restates any ticket-content rule that the guide states, or the guide is loaded from a copy rather than the installed `chupa/docs/host-authoring.md`.
- A rule that was in `chupa/specs/author.md` is in neither the guide nor the remaining Author-stage text.
- Any Author review after the first in a run gets `FIRST_REVIEW`, or gets a prior review in a format different from `chupa review`'s.
- The Author call cap, `AuthorGate` or decline handling changes.
- The change adds a second rendering of the prior review instead of sharing one function.

## Time budget
- expected: 40m
- stuck: 120m
