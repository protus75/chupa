---
state: confirmed
source: seed
priority: P1
kind: chore
agent_tier: high
agent_effort: high
---

## Depends on
none

## Context
- tests/test_plan_lint.py

## Plan contract
- 19.L
- 19.P7
- 19.P7.host-mechanical-check
- section 7
- 19.P7.host-review-surfaces
- section 4
- section 9

## Goal / Why
`CHUPA_PLAN.md` states every fact `phase7-continue` needs from its gapped units.

## Scope in / Scope out
- In: the fenced entry units, with their Owner, Records, Observable, and Tests parts; insert a missing unit after its phase's last unit.
- Out: every other plan byte, code, and tickets.

## Scope fence
- CHUPA_PLAN.md#19.P7.host-mechanical-check
- CHUPA_PLAN.md#19.P7.host-review-surfaces

## Acceptance criteria
1. `uv run pytest tests/test_plan_lint.py` exits 0.
2. `CHUPA_PLAN.md` unit `19.P7.host-mechanical-check` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The entry says 'Severity per TRIGGER and SEVERITY (`19.P7`)', and the ticket says the entry governs trigger matching and effective severity. However, `_seed_cites` forbids a registry-row seed from citing its phase unit, so 19.P7's settled contracts are not rendered. The entry and section 7.3 omit the matching rule: a path-prefix list runs when any changed file in the committed diff matches by the scope-fence prefix rule (section 9), which is a path-boundary match rather than a raw string prefix. Under a raw `startswith`, prefix `chupa/x` wrongly triggers on `chupa/xy.py`, breaking the requirement that an untriggered entry leaves no command, report, spool or finding.
3. `CHUPA_PLAN.md` unit `19.P7.host-review-surfaces` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The Owner part says a surface call is rendered from specs/review.md with rules_doc content as a data block, but it does not say how that block reaches the render. render() requires inputs to match spec.inputs exactly, and tests/test_specs.py::test_review_spec_read_only pins those inputs to (ticket, diff, retry_findings) and the version to 1.1. The Role section also limits the reviewer to whether the diff is correct and does what the ticket asks, 'and only that', with no instruction to judge against host rules. specs/review.md is outside the row fence and 19.L rules 2-5 do not earn it. 19.P7 SPEC VERSIONS settles only the 1.0 -> 1.1 bump. The unit omits the block name and how it is supplied, whether the spec is edited (with its version and fence) or the block is composed by the stage, the instruction to apply the rules, and how the correctness render stays unchanged.
4. `CHUPA_PLAN.md` unit `19.P7.host-review-surfaces` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> The Records part refuses a declared surface with no routing row for any tier a ticket may run at, and the Tests part says existing fixtures stay green. Merged fixtures declare surfaces with no matching row: tests/test_config.py declares `correctness` with only a medium implement route, and the docs/host-contract.md example declares `host-review` with only medium review and implement routes. tests/test_host_contract.py::test_host_contract_example_loads loads that example. docs/host-contract.md is outside the row fence and is not a test or caller that rules 2-5 can earn. chupa/providers.py resolve() and candidates() also fall back to the review row for an unrouted surface, and that file is outside the fence too. The unit does not say which tiers are required, whether a surface may be satisfied by the review fallback, whether `correctness` collides (section 7.3 calls it engine-shipped, ENGINE_LLM_SURFACES omits it), or who updates these fixtures and the doc.
5. `CHUPA_PLAN.md` unit `19.P7.host-review-surfaces` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P7 SEVERITY covers a host 'entry' and says a soft failure is reported without a Suggestion Box message, with no carve-out for surfaces. The entry unit's Records part and section 7.3 file soft-surface findings to the Box, and test_soft_surface_findings_filed requires it. The unit also omits the exact record: box.enqueue needs message_class, stage, outcome, summary and occurrence_id, and the unit gives no class or arrival identity, so retries cannot be shown to deduplicate.
6. `CHUPA_PLAN.md` unit `19.P7.host-review-surfaces` states the needed fact, consistent with merged code. Gap fact (untrusted data):
> 19.P7 SEVERITY lets a ticket gate_bypass naming the entry's code demote it to soft, but a ReviewSurface has a `name` and no `code`. The hardened 19.P7.host-mechanical-check limits accepted bypass codes to ENGINE_GATE_CODES plus review.mechanical codes and refuses anything else, in chupa/tickets.py, which is outside this row's fence. The unit does not say whether a surface can be bypassed. If it can, it does not give the identifier, the validator change and fence, the demoted severity recorded in review.md, or the merge behavior. No named test covers the rule.

## Verification
```
uv run pytest tests/test_plan_lint.py
```

## Definition of rejected
Stating a fact needs plan text outside the fenced units, or contradicts merged code.

## Time budget
- expected: 30m
- stuck: 90m
