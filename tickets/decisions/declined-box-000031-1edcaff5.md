---
id: declined-box-000031-1edcaff5
kind: declined
link: box-000031-1edcaff5
reopen_after_days: 90
---
A bootstrap note points out that the annotation `StageResult.artifact: Artifact | None` in `chupa/artifacts.py` does not fit the Author stage. That stage produces a ticket, and a ticket has no base `Artifact` fields. The note asks the design text to settle it one of two ways: make `Artifact` a root class with no fields and put the provenance fields on a subclass, or widen `StageResult.artifact` to `BaseModel`.

This is a type-annotation and design-wording mismatch, and nothing shows it causes wrong behavior at runtime. `StageResult` is a plain class (`chupa/artifacts.py:239`), so the annotation is never enforced when the program runs. The paths that matter already accept any pydantic model: `Gate.check` takes `BaseModel` (`chupa/gates.py:72`), the driver's `done()` takes `BaseModel | None` (`chupa/driver.py:279`), and the author gate checks a `BaseModel` (`chupa/author.py:55`). The merged tickets `author-stage` and `requisition-author-path` show that the Author stage already runs. The plan is frozen, so the 'pin it in section 5' request cannot be done as asked. What is left is cleaning up the annotation, which falls below the bar for authoring a ticket.

- chupa/artifacts.py:239-241 `class StageResult` with `artifact: Artifact | None` is not a pydantic validator, so the annotation is not checked at runtime
- chupa/gates.py:72 `Gate.check(self, artifact: BaseModel, ...)` already accepts any model
- chupa/driver.py:279 `done(outcome, artifact: BaseModel | None = None) -> StageResult` already passes models that are not `Artifact`
- chupa/author.py:55 the author gate checks a `BaseModel`, and the merged `author-stage` ticket runs end to end
- CHUPA_PLAN.md is frozen per CLAUDE.md, so the requested change to the plan wording cannot be made

Message: box-000031-1edcaff5
