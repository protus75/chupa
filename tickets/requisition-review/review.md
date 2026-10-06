# Review: snag

The diff changes where Implement reads Context files, so its renders are no longer byte-identical, and the requisition prompt render can fail with an uncaught RenderOverBound on tickets that pass the headroom check.

## Findings

- [logic] chupa/stages.py:407 implement_stage now calls implement_inputs(ctx.repo, ...), so Context files are read from the main checkout instead of the Implement worktree the old _context_text read. Any uncommitted or in-flight change to a Context file in the main checkout changes the Implement prompt, which breaks 'Implement renders stay byte-identical'. (do instead: Pass the worktree as implement_inputs' root in implement_stage (implement_inputs(worktree, plan, ticket_text, ticket, ctx.config.context_files)). Requisition measurement keeps passing repo.)
- [logic] chupa/requisition.py:128 The requisition prompt holds context and plan_contract twice: once directly and once inside the embedded Implement render. That makes it about twice the base render. It is rendered at effort high (240k bound) outside the try. A ticket whose base render is under the 120k headroom can still go over 240k here, and render() then raises RenderOverBound out of review_ticket instead of returning a closed snag verdict. (do instead: Render the requisition prompt inside the guarded path. Turn RenderOverBound into a mechanical snag with no call, or drop the duplicated plan_contract and context data from the prompt so it fits whenever the base render fits.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "a98b52164c0a2b7cf5520993fdc716c11f28e4a7",
  "stem": "requisition-review",
  "reviewed_sha": "a98b52164c0a2b7cf5520993fdc716c11f28e4a7",
  "summary": "The diff changes where Implement reads Context files, so its renders are no longer byte-identical, and the requisition prompt render can fail with an uncaught RenderOverBound on tickets that pass the headroom check.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/stages.py",
      "line": 407,
      "message": "implement_stage now calls implement_inputs(ctx.repo, ...), so Context files are read from the main checkout instead of the Implement worktree the old _context_text read. Any uncommitted or in-flight change to a Context file in the main checkout changes the Implement prompt, which breaks 'Implement renders stay byte-identical'.",
      "paved_road": "Pass the worktree as implement_inputs' root in implement_stage (implement_inputs(worktree, plan, ticket_text, ticket, ctx.config.context_files)). Requisition measurement keeps passing repo."
    },
    {
      "code": "logic",
      "path": "chupa/requisition.py",
      "line": 128,
      "message": "The requisition prompt holds context and plan_contract twice: once directly and once inside the embedded Implement render. That makes it about twice the base render. It is rendered at effort high (240k bound) outside the try. A ticket whose base render is under the 120k headroom can still go over 240k here, and render() then raises RenderOverBound out of review_ticket instead of returning a closed snag verdict.",
      "paved_road": "Render the requisition prompt inside the guarded path. Turn RenderOverBound into a mechanical snag with no call, or drop the duplicated plan_contract and context data from the prompt so it fits whenever the base render fits."
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
