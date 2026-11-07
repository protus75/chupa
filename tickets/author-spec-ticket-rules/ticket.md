---
state: confirmed
source: human
priority: P1
kind: feature
---

## Depends on
- none

## Context
- chupa/author.py
- chupa/tickets.py
- tests/integration/test_author.py
- tests/integration/test_triage.py
- docs/host-authoring.md

## On-demand
- chupa/specs/author.md
- docs/how-chupa-works.md

## Goal / Why
The Author stage keeps failing on ticket rules that hand authors follow without trouble. Author run 6 (attempt 61, 2026-11-07) spent all 4 calls on `claude-effort-flag`, and no ticket was written:
- call 1 wrote prose sentences in `## Context`, and wrote `gate_bypass: false`, a boolean where a list is required;
- call 2 put prose before the JSON;
- call 3 wrote `gate_bypass: false` again;
- call 4 removed `gate_bypass`, but also dropped `hosts/fixture/bin/claude`, which call 3 had correctly added. Requisition review then snagged on `scope_fence`, because that fixture pins the exact claude argv.

`chupa/specs/author.md` causes this:
- It names "the section 13 sections" but never states what each one may hold. The rules live in `docs/host-authoring.md`, which this prompt never sees.
- It lists `gate_bypass` as a normal frontmatter field and gives no type.
- On a re-prompt, the author sees only the findings, never its own previous reply. It rewrites the whole ticket from memory, which undoes fixes made on earlier calls.

After this change:
- the author prompt states the section rules and the exact frontmatter keys;
- the author never writes `gate_bypass`;
- every re-prompt carries the author's previous reply, so it repairs that reply instead of rewriting it.

## Scope in / Scope out
- In: `chupa/specs/author.md`, `version` `1.1` -> `1.2` (minor, so the recorded GO baseline, which binds the major version only, still holds).
  - Frontmatter: the Task says to write exactly `priority` (P0-P3), `kind` (`feature`, `chore`, or `bug`), `agent_tier`, and `agent_effort`, each as a plain scalar. It says never to write `state`, `source`, or `gate_bypass`, because the stage stamps the first two and a bypass is an operator decision.
  - Section rules, stated in the spec body:
    - every `## Context` and `## On-demand` item is an existing repo-relative file path from the tracked files, never prose;
    - a file the ticket creates appears only in `## Scope fence` and `## Verification`;
    - `## Scope fence` lists every file the change forces, including tests, fixtures, and fake binaries that pin a changed name, value, argv, or version. Before replying, the author greps the repo for each changed name or value to find these;
    - a ticket that changes documented behavior fences that document.
  - A new data block, `previous_reply`, comes after `retry_findings`. The re-prompt rule says to start from `previous_reply`, change only what the findings name, and keep every other section byte-identical.
- In: `chupa/author.py` keeps the text of the most recent candidate that parsed as an `AuthorReply`, captured in `review_candidate`, which sees every parsed candidate. `render_author` passes it as `previous_reply`: the candidate's `ticket` text, or `none` before the first parsed candidate.
- In: `tests/integration/test_author.py`:
  - update the version assertion in `test_author_spec_requires_criteria_to_name_wrong_results` to `1.2`;
  - add `test_author_spec_states_ticket_rules`;
  - add `test_author_reprompt_carries_previous_reply`.
- In: `docs/how-chupa-works.md` section 9.3 says the author prompt states the ticket section rules and that each re-prompt carries the previous reply.
- Out:
  - the call budget;
  - `requisition_review` and its `coverage_dependents`;
  - the `ticket_schema` gate and its fix-hint text;
  - `chupa/driver.py`;
  - `docs/host-authoring.md`;
  - `CHUPA_PLAN.md`.

## Scope fence
- chupa/specs/author.md
- chupa/author.py
- tests/integration/test_author.py
- docs/how-chupa-works.md

## Acceptance criteria
1. `./dev.py test tests/integration/test_author.py` exits 0. In it:
   - `test_author_spec_requires_criteria_to_name_wrong_results` asserts version `1.2`.
   - `test_author_spec_states_ticket_rules` asserts that the `chupa/specs/author.md` body:
     - contains `gate_bypass` only inside the never-write rule;
     - names `priority`, `kind`, `agent_tier`, and `agent_effort` as the keys to write;
     - states that `## Context` items are existing file paths;
     - states that the fence includes tests and fixtures pinning a changed value.

     It fails on the old spec, which lists `gate_bypass` among the fields to write.
   - `test_author_reprompt_carries_previous_reply` drives the author with a `FakeLLM`. The first reply is a parsed `AuthorReply` that fails `ticket_schema` (`gate_bypass: false`); the second reply is valid. The test asserts that the second rendered prompt's `previous_reply` block contains the first reply's ticket text, and that the first prompt's block is `none`. It rules out a re-prompt that carries only findings.
2. `./dev.py test` exits 0.
3. `docs/how-chupa-works.md` section 9.3 mentions `previous_reply`.

## Verification
```
./dev.py test tests/integration/test_author.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of these is true:
- the author spec still offers `gate_bypass` as a field to write;
- `previous_reply` is missing from any re-prompt after a parsed candidate;
- the call budget, requisition review, the `ticket_schema` gate, or `chupa/driver.py` changes;
- the spec's major version changes;
- `CHUPA_PLAN.md` is edited.

## Time budget
- expected: 30m
- stuck: 90m
