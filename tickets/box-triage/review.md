# Review: snag

The triage flow is mostly right, but run_seq does not reach the spool path, so all messages in one pass write to the same spool dir, and the main triage test never checks the tier or effect keys that criterion 2 requires.

## Findings

- [acceptance] chupa/driver.py:147 The ticket says that when `run_seq` is given, the call spools under `<surface>/<run_seq>/<attempt>/`, so two messages in one pass never share a spool dir. The diff only swaps `seq` for the effect key. Every `self.spool.write(stem, attempt, ...)` call is unchanged, and `Spool.write` writes to `<root>/<stem>/<attempt>/<name>`. So every triage call in pass N writes `spools/triage/N/call-01/prompt.md` and `output.txt`, and each message overwrites the previous message's prompt and output. (do instead: When `run_seq` is given, put it in the spool path, e.g. a spool stem of `f"{stage.surface}/{run_seq}"` passed to every `self.spool.write` call in `run`. Keep the existing ticket and ticketless paths byte-identical so tests/test_driver.py passes unedited. Add a test assertion that two messages in one pass get distinct spool dirs.)
- [acceptance] tests/test_triage.py:34 Criterion 2 requires the test to prove three `triage` requests at `routing_default_tier` with distinct effect keys `llm/triage/<seq>/triage/0/1`. The test checks only the surface and that the `rendered` texts differ. Those texts differ anyway because the message contents differ. Neither the request tier nor any journaled LLM effect key is asserted, so a wrong tier or a key collision would still pass. (do instead: Assert `r.tier == config.routing_default_tier` for each `llm.requests` entry. Read the journal's LLM effect events and assert the keys equal `{f"llm/triage/{m.seq}/triage/0/1" for m in the three messages}`.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "19b015b037a9fec9bfe4b01b7875e9dbd21e4983",
  "stem": "box-triage",
  "reviewed_sha": "19b015b037a9fec9bfe4b01b7875e9dbd21e4983",
  "summary": "The triage flow is mostly right, but run_seq does not reach the spool path, so all messages in one pass write to the same spool dir, and the main triage test never checks the tier or effect keys that criterion 2 requires.",
  "findings": [
    {
      "code": "acceptance",
      "path": "chupa/driver.py",
      "line": 147,
      "message": "The ticket says that when `run_seq` is given, the call spools under `<surface>/<run_seq>/<attempt>/`, so two messages in one pass never share a spool dir. The diff only swaps `seq` for the effect key. Every `self.spool.write(stem, attempt, ...)` call is unchanged, and `Spool.write` writes to `<root>/<stem>/<attempt>/<name>`. So every triage call in pass N writes `spools/triage/N/call-01/prompt.md` and `output.txt`, and each message overwrites the previous message's prompt and output.",
      "paved_road": "When `run_seq` is given, put it in the spool path, e.g. a spool stem of `f\"{stage.surface}/{run_seq}\"` passed to every `self.spool.write` call in `run`. Keep the existing ticket and ticketless paths byte-identical so tests/test_driver.py passes unedited. Add a test assertion that two messages in one pass get distinct spool dirs."
    },
    {
      "code": "acceptance",
      "path": "tests/test_triage.py",
      "line": 34,
      "message": "Criterion 2 requires the test to prove three `triage` requests at `routing_default_tier` with distinct effect keys `llm/triage/<seq>/triage/0/1`. The test checks only the surface and that the `rendered` texts differ. Those texts differ anyway because the message contents differ. Neither the request tier nor any journaled LLM effect key is asserted, so a wrong tier or a key collision would still pass.",
      "paved_road": "Assert `r.tier == config.routing_default_tier` for each `llm.requests` entry. Read the journal's LLM effect events and assert the keys equal `{f\"llm/triage/{m.seq}/triage/0/1\" for m in the three messages}`."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
