---
id: declined-box-000175-aaca96f8
kind: declined
link: box-000175-aaca96f8
reopen_after_days: 90
---
A bootstrap handoff note says `confirm <stem>` from `reject-queue-verbs` should also move a committed `state: draft` ticket to `confirmed`, because the drain report already tells operators to confirm drafts and box-authored drafts need a working release. It asks for frozen-plan unit 19.P2 to mention this draft flip next to the Reject-queue keep.

The code already does this. In `chupa/runner.py`, the confirm path finds a committed `state: draft` ticket, flips it to confirmed, journals a `draft_confirmed` signal and prints `confirmed draft <stem>`. So drafts already have a working release. All that is left is a wording change to `CHUPA_PLAN.md`, which is a frozen bootstrap record and is never edited. No incorrect runtime behavior can be reached.

- chupa/runner.py:521 docstring: "Resolve a draft or Reject item while holding the same writer lock as run and drain."
- chupa/runner.py:551-557: a committed ticket in `draft` state is confirmed, journaled as signal `draft_confirmed`, and reported as `confirmed draft <stem>`
- chupa/runner.py:571: a stem that is neither a draft nor in the Reject queue is refused with a paved road
- `reject-queue-verbs` is merged; CHUPA_PLAN.md is frozen per repo rules

Message: box-000175-aaca96f8
