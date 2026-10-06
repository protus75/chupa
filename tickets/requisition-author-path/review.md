# Review: rma

The ticket cannot be implemented as written: it requires a review call on every Author pass, but it also forbids changing the test_triage assertions that pin the exact request list and journal key set, and its driver spec contradicts acceptance criterion 1.

## Findings

- [ticket] tests/test_triage.py:122 Scope-in says test_triage.py gets 'No assertion changes' and acceptance criterion 4 requires it to pass 'with only FakeLLM script additions'. But test_three_verdicts_and_second_pass_and_stale_author asserts len(llm.requests) == 4, the exact (surface, tier, ticket) request list, and the exact set of llm/ effect keys. The mandatory requisition review adds a fifth request ('requisition_review') and a new key llm/author/0/requisition_review/<seq>/1. Those assertions cannot hold unchanged, so the diff had to edit them, which breaks the criterion. (do instead: Amend the ticket (and the plan's 19.P2 wiring text) to allow test_triage.py assertion updates that only reflect the added review request and its effect key. Then re-run Implement against the amended ticket.)
- [ticket] chupa/driver.py:218 Scope-in says the driver awaits review only 'After the synchronous gates pass'. But the terminal_findings bullet and acceptance criterion 1 require one call to return gate_failed carrying BOTH a hard sync-gate finding and a review finding. That can only happen if the review also runs when sync gates fail. The two specs contradict each other. The diff runs the review unconditionally, which also makes Author spend a review call on candidates that AuthorGate already rejected. (do instead: Amend the ticket to say which is intended: either review runs on every call regardless of sync gates (and criterion 1 stands), or review runs only after sync gates pass (and criterion 1 drops the combined sync+review findings requirement).)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "db82cae8eeae4021315d808b568521ae26748bd6",
  "stem": "requisition-author-path",
  "reviewed_sha": "db82cae8eeae4021315d808b568521ae26748bd6",
  "summary": "The ticket cannot be implemented as written: it requires a review call on every Author pass, but it also forbids changing the test_triage assertions that pin the exact request list and journal key set, and its driver spec contradicts acceptance criterion 1.",
  "findings": [
    {
      "code": "ticket",
      "path": "tests/test_triage.py",
      "line": 122,
      "message": "Scope-in says test_triage.py gets 'No assertion changes' and acceptance criterion 4 requires it to pass 'with only FakeLLM script additions'. But test_three_verdicts_and_second_pass_and_stale_author asserts len(llm.requests) == 4, the exact (surface, tier, ticket) request list, and the exact set of llm/ effect keys. The mandatory requisition review adds a fifth request ('requisition_review') and a new key llm/author/0/requisition_review/<seq>/1. Those assertions cannot hold unchanged, so the diff had to edit them, which breaks the criterion.",
      "paved_road": "Amend the ticket (and the plan's 19.P2 wiring text) to allow test_triage.py assertion updates that only reflect the added review request and its effect key. Then re-run Implement against the amended ticket."
    },
    {
      "code": "ticket",
      "path": "chupa/driver.py",
      "line": 218,
      "message": "Scope-in says the driver awaits review only 'After the synchronous gates pass'. But the terminal_findings bullet and acceptance criterion 1 require one call to return gate_failed carrying BOTH a hard sync-gate finding and a review finding. That can only happen if the review also runs when sync gates fail. The two specs contradict each other. The diff runs the review unconditionally, which also makes Author spend a review call on candidates that AuthorGate already rejected.",
      "paved_road": "Amend the ticket to say which is intended: either review runs on every call regardless of sync gates (and criterion 1 stands), or review runs only after sync gates pass (and criterion 1 drops the combined sync+review findings requirement)."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "rma"
}
```
