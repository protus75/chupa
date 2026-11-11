# Review: snag

The commit lock, the Git wiring, the composition roots, the doctor reorder and the tests meet the ticket and close both prior findings, but two docs are wrong: the host-contract sentence sits outside the lockfile paragraph, and how-chupa-works.md still lists doctor's checks in the old order.

## Findings

- [acceptance] chupa/docs/host-contract.md:373 Scope in says to add one sentence to the lockfile paragraph. The diff puts `Git writes take <state_dir>/commit.lock with a 60-second wait.` straight after `restarts itself when its chupa/ tree changes.` and follows it with a new blank line. In Markdown the sentence therefore ends the 'ONE instance writes a host repo line' paragraph, and the `<state_dir>/chupa.lock uses advisory flock...` text becomes a separate paragraph. The sentence is not in the lockfile paragraph, and the blank line breaks up the existing Instance custody paragraph. (do instead: Remove the added blank line and put the sentence inside the lockfile paragraph, for example right after `...never delete the lockfile. Child descriptors do not pin it.`. That paragraph must still say `never delete the lockfile`.)
- [acceptance] docs/how-chupa-works.md:- The doctor row in the verb table still says `Checks venv, git, config load, lock probe, journal readability, and core check.` That is the old row order. The diff moves the git row after config (venv, config, git, lock, journal, core), and when the config fails to load the git row now fails with `not checked: config did not load; fix the config and rerun doctor` and runs no git probe. The doc does not describe either change. (do instead: Change the doctor row in docs/how-chupa-works.md to list the checks in the new order (venv, config load, git, lock probe, journal readability, core check). Say that git is not probed when the config fails to load.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "1709943f0d207cc2c2dc4b1967ed928095072ac2",
  "stem": "commit-lock",
  "reviewed_sha": "1709943f0d207cc2c2dc4b1967ed928095072ac2",
  "summary": "The commit lock, the Git wiring, the composition roots, the doctor reorder and the tests meet the ticket and close both prior findings, but two docs are wrong: the host-contract sentence sits outside the lockfile paragraph, and how-chupa-works.md still lists doctor's checks in the old order.",
  "findings": [
    {
      "code": "acceptance",
      "path": "chupa/docs/host-contract.md",
      "line": 373,
      "message": "Scope in says to add one sentence to the lockfile paragraph. The diff puts `Git writes take <state_dir>/commit.lock with a 60-second wait.` straight after `restarts itself when its chupa/ tree changes.` and follows it with a new blank line. In Markdown the sentence therefore ends the 'ONE instance writes a host repo line' paragraph, and the `<state_dir>/chupa.lock uses advisory flock...` text becomes a separate paragraph. The sentence is not in the lockfile paragraph, and the blank line breaks up the existing Instance custody paragraph.",
      "paved_road": "Remove the added blank line and put the sentence inside the lockfile paragraph, for example right after `...never delete the lockfile. Child descriptors do not pin it.`. That paragraph must still say `never delete the lockfile`.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "docs/how-chupa-works.md",
      "line": null,
      "message": "The doctor row in the verb table still says `Checks venv, git, config load, lock probe, journal readability, and core check.` That is the old row order. The diff moves the git row after config (venv, config, git, lock, journal, core), and when the config fails to load the git row now fails with `not checked: config did not load; fix the config and rerun doctor` and runs no git probe. The doc does not describe either change.",
      "paved_road": "Change the doctor row in docs/how-chupa-works.md to list the checks in the new order (venv, config load, git, lock probe, journal readability, core check). Say that git is not probed when the config fails to load.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.4",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
