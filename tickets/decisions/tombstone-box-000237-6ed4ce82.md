---
id: tombstone-box-000237-6ed4ce82
kind: tombstone
link: declined-box-000096-26627240
reopen_after_days: 90
---
`run <stem>` refuses to run a ticket until every stem in its `Depends on` list is journal-`merged`, and it tells the operator to run each dependency first. The frozen plan's section 18 states this eligibility rule only for `drain`. The note asks for the plan to state the rule for `run` too, or for `run` to stop enforcing it.

Registry record declined-box-000096-26627240 already decided this same request: `run` refuses when dependencies are not merged, the plan states the rule only for drain, and the note asks to either state it for run or drop it. The request only concerns how the frozen plan is worded. It reports no runtime behavior that is wrong.

- declined-box-000096-26627240 records the same observation: `run <stem>` refuses a stem whose dependencies are not journal-`merged`, and section 18 pins the rule only for `drain`.
- The message reports no failure and gives no stage or outcome. It asks for a plan-wording change or a relaxed policy.

Message: box-000237-6ed4ce82
