# Review: snag

The activation wiring and fixture adoption follow the contract, but committed_core can misreport valid conduct when it reads the committed blob, and a candidate engine template it cannot parse crashes evidence gathering instead of producing a core_drift finding.

## Findings

- [logic] chupa/hostfiles.py:165 When the checkout bytes do not hash-match the committed blob, committed_core reads the blob with `git._run(... 'show' ...)`. That path goes through SubprocessExec, which decodes stdout with `errors="replace"`, and the code then calls `.encode()` on the result. Any committed conduct file with non-UTF-8 project bytes therefore comes back with U+FFFD in place of the original bytes. A file that is current in the commit (the fixtures use `\xff` remainders) then fails the byte comparison and classifies `drifted`, or `missing` if the damage reaches the markers. The hard gate then refuses a valid candidate, so classification depends on whether the worktree is dirty, not only on the committed bytes. (do instead: Read the committed blob as raw bytes through a Git-seam method that returns bytes undecoded (for example `cat-file blob <sha>` through an exec call that keeps the bytes). Alternatively, fail closed with a finding when the checkout and the blob differ. Add a test with a dirty worktree and a non-UTF-8 committed conduct file that is current, and assert it classifies `current`.)
- [logic] chupa/hostfiles.py:148 committed_core runs `ast.parse` on the candidate's `chupa/hostfiles.py` and raises `ValueError` when `CORE_TEMPLATE` is not a single literal bytes assignment. It is called from gather_safety_evidence before any gate runs. A self-host candidate whose hostfiles.py has a syntax error, or builds the template any other way (for example by concatenation), therefore crashes Check and the merge reruns with an uncaught exception. The gate never gets to emit a `core_drift` Finding with a paved road, which breaks the rule that every gate refusal carries a road. (do instead: Catch SyntaxError and ValueError from the template extraction. Carry the failure into Evidence so that CoreDriftGate emits a `core_drift` Finding naming `chupa/hostfiles.py`, with a road such as 'define CORE_TEMPLATE as one literal bytes assignment'. Add a test where the candidate's hostfiles.py is malformed and assert the gate fails with that finding and does not raise.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "fe3f7e1c5ba43d15df6749be413f542e73f1d5a3",
  "stem": "core-drift-activation",
  "reviewed_sha": "fe3f7e1c5ba43d15df6749be413f542e73f1d5a3",
  "summary": "The activation wiring and fixture adoption follow the contract, but committed_core can misreport valid conduct when it reads the committed blob, and a candidate engine template it cannot parse crashes evidence gathering instead of producing a core_drift finding.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/hostfiles.py",
      "line": 165,
      "message": "When the checkout bytes do not hash-match the committed blob, committed_core reads the blob with `git._run(... 'show' ...)`. That path goes through SubprocessExec, which decodes stdout with `errors=\"replace\"`, and the code then calls `.encode()` on the result. Any committed conduct file with non-UTF-8 project bytes therefore comes back with U+FFFD in place of the original bytes. A file that is current in the commit (the fixtures use `\\xff` remainders) then fails the byte comparison and classifies `drifted`, or `missing` if the damage reaches the markers. The hard gate then refuses a valid candidate, so classification depends on whether the worktree is dirty, not only on the committed bytes.",
      "paved_road": "Read the committed blob as raw bytes through a Git-seam method that returns bytes undecoded (for example `cat-file blob <sha>` through an exec call that keeps the bytes). Alternatively, fail closed with a finding when the checkout and the blob differ. Add a test with a dirty worktree and a non-UTF-8 committed conduct file that is current, and assert it classifies `current`.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/hostfiles.py",
      "line": 148,
      "message": "committed_core runs `ast.parse` on the candidate's `chupa/hostfiles.py` and raises `ValueError` when `CORE_TEMPLATE` is not a single literal bytes assignment. It is called from gather_safety_evidence before any gate runs. A self-host candidate whose hostfiles.py has a syntax error, or builds the template any other way (for example by concatenation), therefore crashes Check and the merge reruns with an uncaught exception. The gate never gets to emit a `core_drift` Finding with a paved road, which breaks the rule that every gate refusal carries a road.",
      "paved_road": "Catch SyntaxError and ValueError from the template extraction. Carry the failure into Evidence so that CoreDriftGate emits a `core_drift` Finding naming `chupa/hostfiles.py`, with a road such as 'define CORE_TEMPLATE as one literal bytes assignment'. Add a test where the candidate's hostfiles.py is malformed and assert the gate fails with that finding and does not raise.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
