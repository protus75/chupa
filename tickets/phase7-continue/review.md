# Review: snag

The authored host-mechanical-check seed misses a production validator consumer: `chupa/triage.py` calls `Frontmatter.model_validate` directly, so its fence and closure snapshot leave a reachable path on the engine-only default.

## Findings

- [acceptance] tests/test_seeded_phase7_01.py:41 The caller closure is incomplete. The seed makes `GateBypass` code acceptance depend on an explicit Pydantic validation context and says no production validation of configured host work may rely on the empty default. However, `chupa/triage.py:200` (`attribute_escape`) calls `Frontmatter.model_validate(yaml.safe_load(front[0]))` directly, with no context. SCAN_PATTERN covers only `parse_ticket`, `validate_ticket`, `intake`, `review_*` and `Watcher` calls, so it never finds this consumer, and `chupa/triage.py` is absent from FENCE_ADDITIONS, CLOSURE_EVIDENCE and the seed's fence. Failure path: a bug ticket with a `gate_bypass` naming a declared host mechanical code now passes Author validation and commits. Triage then re-validates it with engine codes only and raises a ValidationError, which is a ValueError. `chupa/triage.py:116` catches it and logs `escape_attribution_incomplete` with the paved road 'repair repository/evidence access and retry triage'. Retrying cannot succeed, so escape attribution stays permanently unavailable for that ticket. This also breaks the comment at `chupa/triage.py:198`, which says later changes cannot invalidate this historical evidence. The implementer must either leave this regression in place or edit outside the fence. (do instead: Extend the closure scan to cover direct `Frontmatter.model_validate` consumers. Add `chupa/triage.py` to the host-mechanical-check fence and FENCE_ADDITIONS with its exact caller evidence in CLOSURE_EVIDENCE, and record it in the Context/On-demand partition with its size. Have the seed state how triage handles a declared host code and name a test obligation for it. Then re-author the seed and update AUTHORED_TEXT, its hashes and sizes, and the render operands. If 19.L's closure rules do not earn this addition, stop with premise_failed, kind: spec_gap, on unit 19.P7.host-mechanical-check.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "4f809b2d0f738999ec477e4bb19a9aeddfcb9ab3",
  "stem": "phase7-continue",
  "reviewed_sha": "4f809b2d0f738999ec477e4bb19a9aeddfcb9ab3",
  "summary": "The authored host-mechanical-check seed misses a production validator consumer: `chupa/triage.py` calls `Frontmatter.model_validate` directly, so its fence and closure snapshot leave a reachable path on the engine-only default.",
  "findings": [
    {
      "code": "acceptance",
      "path": "tests/test_seeded_phase7_01.py",
      "line": 41,
      "message": "The caller closure is incomplete. The seed makes `GateBypass` code acceptance depend on an explicit Pydantic validation context and says no production validation of configured host work may rely on the empty default. However, `chupa/triage.py:200` (`attribute_escape`) calls `Frontmatter.model_validate(yaml.safe_load(front[0]))` directly, with no context. SCAN_PATTERN covers only `parse_ticket`, `validate_ticket`, `intake`, `review_*` and `Watcher` calls, so it never finds this consumer, and `chupa/triage.py` is absent from FENCE_ADDITIONS, CLOSURE_EVIDENCE and the seed's fence. Failure path: a bug ticket with a `gate_bypass` naming a declared host mechanical code now passes Author validation and commits. Triage then re-validates it with engine codes only and raises a ValidationError, which is a ValueError. `chupa/triage.py:116` catches it and logs `escape_attribution_incomplete` with the paved road 'repair repository/evidence access and retry triage'. Retrying cannot succeed, so escape attribution stays permanently unavailable for that ticket. This also breaks the comment at `chupa/triage.py:198`, which says later changes cannot invalidate this historical evidence. The implementer must either leave this regression in place or edit outside the fence.",
      "paved_road": "Extend the closure scan to cover direct `Frontmatter.model_validate` consumers. Add `chupa/triage.py` to the host-mechanical-check fence and FENCE_ADDITIONS with its exact caller evidence in CLOSURE_EVIDENCE, and record it in the Context/On-demand partition with its size. Have the seed state how triage handles a declared host code and name a test obligation for it. Then re-author the seed and update AUTHORED_TEXT, its hashes and sizes, and the render operands. If 19.L's closure rules do not earn this addition, stop with premise_failed, kind: spec_gap, on unit 19.P7.host-mechanical-check.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.1",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
