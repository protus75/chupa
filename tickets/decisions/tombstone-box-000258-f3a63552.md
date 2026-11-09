---
id: tombstone-box-000258-f3a63552
kind: tombstone
link: drain-ceiling-carried-on-handoff
reopen_after_days: 30
---
On a self-upgrade, each child drain starts a new `max_runtime_hours` deadline from its own start time. Every handoff therefore resets the drain's overall wall-clock ceiling, so a drain that hands off repeatedly can run well past the intended runaway backstop.

Open ticket `drain-ceiling-carried-on-handoff` covers this same gap. `_Drain.__init__` computes `self.deadline = clock() + max_runtime_hours` from its own process start, so the child drain after a self-upgrading merge gets a fresh deadline and halts at T + max_runtime_hours instead of the parent's original deadline. The message and the ticket describe the same defect and the same fix: carry the invocation's ceiling across the handoff.

- Open ticket drain-ceiling-carried-on-handoff: `_Drain.__init__` computes `self.deadline = clock() + max_runtime_hours` from its own process start, and a child drain computes a fresh deadline, so each handoff re-arms the ceiling.
- The message proposes carrying the invocation's start or deadline across the handoff, which is the change that ticket scopes.

Message: box-000258-f3a63552
