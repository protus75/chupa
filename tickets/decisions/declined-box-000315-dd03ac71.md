---
id: declined-box-000315-dd03ac71
kind: declined
link: box-000315-dd03ac71
reopen_after_days: 30
---
Implement's prompt spec (`chupa/specs/implement.md`) never tells the implementer to look for documentation the diff makes false, but Review does check docs (merged `review-checks-docs`). On ticket-changed-midrun attempt 3, the only Review finding was a stale `docs/how-chupa-works.md` section 6.1 that the ticket did not name. That one finding cost a Review snag, a Diagnosis call and a retry. The proposal adds a step to implement.md: before committing, search `docs/` and `README.md` for statements the diff makes false, fix those inside the fence, and report those outside it in `second_problems`.

The gap is real: implement.md has no documentation rule, and Review enforces one. But the evidence is a single incident costing one retry, and the ticket still converged through the normal Review-then-Diagnosis loop. That loop worked as intended and did not harm runtime behavior. The registry has declined other single-incident, one-retry spec-tuning proposals the same way (declined-box-000313-990b50f9 and declined-box-000314-f43505b4). The retro also flags overcorrection risk: implementers might rewrite loosely related docs and draw `scope` findings. Without a second incident, that risk outweighs the cost of one retry.

- `chupa/specs/implement.md` has no occurrence of 'doc' (searched 2026-11-09), so the gap exists today.
- `review-checks-docs` is merged, so Review does flag stale docs.
- Only one incident is cited: ticket-changed-midrun attempt 3, whose sole finding was docs/how-chupa-works.md section 6.1. It cost one Review snag, one Diagnosis call and one retry.
- Precedent: declined-box-000313-990b50f9 and declined-box-000314-f43505b4 declined implement/review spec rules backed by one retry each.
- The retro's own overcorrection_risk says the proposal rests on one observed failure.

Message: box-000315-dd03ac71
