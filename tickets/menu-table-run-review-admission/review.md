# Review: snag

The admission refactor keeps the run, review, intake and lint verbs' refusals and adds the menu table, but the new order validation turns `chupaRunsBefore` off for a ticket whose only defect is a Runs-before cycle, even though `_order` accepts the Runs-before edit that fixes it.

## Findings

- [logic] chupa/observe.py:530 `chupaRunsBefore` gets `order_admission` with `ticket=order_ticket`, which is `validate_ticket` on the current disk text. With the new `isinstance(ticket, list)` check in `order_admission` (chupa/status.py:132), a ticket whose `## Runs before` closes a cycle is now "off" for Runs before. `_order` (chupa/__main__.py) does not validate the current text. It validates `order(text, runs_before=...)`, the changed text, so `order <stem> --runs-before` without the cycle edge is accepted and writes the file. That edit is exactly the paved road of the cycle finding: "drop the edge that inverts the intended order". Before this diff the item was "on" for this row (open section, parse-valid). The menu now hides an action the verb accepts, which is the drift the ticket forbids. The new `runs-before-cycle` case in tests/integration/test_menu_verb_parity.py pins it (`order=False` for both `chupaPriority` and `chupaRunsBefore`). The same over-refusal hits any ticket made invalid only by its Runs before entries. (do instead: Build each order key's ticket input the way `_order` validates: validate the text after that key's edit, not the current text. For `chupaRunsBefore`, validate `tickets.order(text, priority=None, runs_before=[])` (Runs before cleared), so the key admits when some Runs-before edit can produce a valid ticket. Keep the current-text validation for `chupaPriority`. Update the `runs-before-cycle` expectation so `chupaRunsBefore` is on and `chupaPriority` is off.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "f92b4ee63ea6f4568c08391b5a5207a04b234c20",
  "stem": "menu-table-run-review-admission",
  "reviewed_sha": "f92b4ee63ea6f4568c08391b5a5207a04b234c20",
  "summary": "The admission refactor keeps the run, review, intake and lint verbs' refusals and adds the menu table, but the new order validation turns `chupaRunsBefore` off for a ticket whose only defect is a Runs-before cycle, even though `_order` accepts the Runs-before edit that fixes it.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/observe.py",
      "line": 530,
      "message": "`chupaRunsBefore` gets `order_admission` with `ticket=order_ticket`, which is `validate_ticket` on the current disk text. With the new `isinstance(ticket, list)` check in `order_admission` (chupa/status.py:132), a ticket whose `## Runs before` closes a cycle is now \"off\" for Runs before. `_order` (chupa/__main__.py) does not validate the current text. It validates `order(text, runs_before=...)`, the changed text, so `order <stem> --runs-before` without the cycle edge is accepted and writes the file. That edit is exactly the paved road of the cycle finding: \"drop the edge that inverts the intended order\". Before this diff the item was \"on\" for this row (open section, parse-valid). The menu now hides an action the verb accepts, which is the drift the ticket forbids. The new `runs-before-cycle` case in tests/integration/test_menu_verb_parity.py pins it (`order=False` for both `chupaPriority` and `chupaRunsBefore`). The same over-refusal hits any ticket made invalid only by its Runs before entries.",
      "paved_road": "Build each order key's ticket input the way `_order` validates: validate the text after that key's edit, not the current text. For `chupaRunsBefore`, validate `tickets.order(text, priority=None, runs_before=[])` (Runs before cleared), so the key admits when some Runs-before edit can produce a valid ticket. Keep the current-text validation for `chupaPriority`. Update the `runs-before-cycle` expectation so `chupaRunsBefore` is on and `chupaPriority` is off.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.5",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
