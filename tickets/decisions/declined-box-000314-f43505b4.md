---
id: declined-box-000314-f43505b4
kind: declined
link: box-000314-f43505b4
reopen_after_days: 30
---
During the merged `parallel-tests` ticket, the attempt 1 Review paved road told Implement how to fix a timeout test: arm the deadline once `received` is set. It did not say that the seam's real `asyncio.timeout` had to stay under test. Attempt 2 followed the road, and Review then raised a snag because the configured timeout was no longer exercised. Diagnosis reversed direction, and one retry was spent. The proposal is a `chupa/specs/review.md` rule: a paved road that changes a test must name the behavior the test has to keep proving, and should describe the outcome rather than a mechanism.

The evidence is one chain in one ticket, and that ticket has merged. It cost one retry, and nothing shows the problem recurring on other stems or in other retro windows. The registry already declined a sibling finding from the same `parallel-tests` attempt-2 incident (declined-box-000313-990b50f9: tests rewritten so they could no longer fail). That proposal also sought a spec rule from this single episode, so authoring this one would go against that decision. The message admits a real overcorrection risk: vaguer roads would weaken the rule that every finding ships a usable paved road, and reviewers might start padding findings. One incident does not justify that tradeoff. The open tickets do not cover review paved-road wording, so this is not a duplicate.

- Source: retro/17, about the merged ticket `parallel-tests`. One retry was spent between attempts 1 and 2, and the stem was later merged.
- Sibling decision declined-box-000313-990b50f9 declined a spec rule drawn from the same `parallel-tests` attempt-2 test-weakening episode.
- The message's own overcorrection_risk says it 'rests on one chain in one ticket' and warns that roads could become too vague to steer a retry.
- No open ticket or registry record covers review paved roads that prescribe a test mechanism, so tombstone does not apply.

Message: box-000314-f43505b4
