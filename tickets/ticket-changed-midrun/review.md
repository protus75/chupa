# Review: snag

The mid-run hold works on the stage and admission paths, but the `serve` scan filter silences invalid new tickets, and the queue's `ticket_changed` check overrides an operator kill and an already-landed squash.

## Findings

- [logic] chupa/serve.py:237 `scan` now drops any stem with no committed blob on main. A new ticket that intake refuses (for example invalid frontmatter) stays on disk uncommitted, so `git show` raises `GitError` and the stem is skipped. It never appears in `current`, `watch` never yields it, and the Watcher never parses it, so `watcher_parse_failure` is never journaled. `scan` also discards intake's `refused` result, so `serve` now reports the bad ticket nowhere. Before this diff the stem was yielded and the signal was journaled. `test_serve_watcher_edits_deletions_and_last_good` only covers an already-committed stem, so it misses this. The ticket did not ask for this filter, and the boundary check already holds a run whose ticket is dirty. (do instead: Restore `{stem: self.read(stem) for stem in self.stems()}` in `scan`. If a filter is still needed, it must keep yielding stems with no committed blob so the Watcher reports them, and a serve test must cover an invalid new stem producing `watcher_parse_failure`.)
- [logic] chupa/mergequeue.py:387 `_admit` runs `ticket_changed` before it reads the retained hold's state, so two paths that are not merge admissions get the hold. (1) Kill: when a held stem has a `reject` release and its ticket was edited, the result is `gate_failed`/`ticket_changed` in the Reject queue. The `rejected` transition, `_dead_dependents` and `retire` are all skipped, so the operator's kill is lost and has to be repeated. (2) Landed squash: when `merge/<stem>/<attempt>` has already completed but a crash came before the `merged` terminal, the latest transition is still `running`. An edit then journals `gate_failed` and removes the worktree for work already on main, and a keep re-runs it. The check added to `reconstruct` at line 219 has the same ordering problem for both cases. (do instead: Check `ticket_changed` only on the path that would still admit. For a retained stem, run it after the `reject` release branch and the `completed` squash branch, and before the `_finish` and rebase paths. In `reconstruct`, skip the check when the hold has a reject release or a completed squash effect, and let `_admit` settle those. Add tests for a kill and for a completed squash on a held stem with an edited ticket.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "956b6a3d2624237a582295079d5d61d8c1dcbc8e",
  "stem": "ticket-changed-midrun",
  "reviewed_sha": "956b6a3d2624237a582295079d5d61d8c1dcbc8e",
  "summary": "The mid-run hold works on the stage and admission paths, but the `serve` scan filter silences invalid new tickets, and the queue's `ticket_changed` check overrides an operator kill and an already-landed squash.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 237,
      "message": "`scan` now drops any stem with no committed blob on main. A new ticket that intake refuses (for example invalid frontmatter) stays on disk uncommitted, so `git show` raises `GitError` and the stem is skipped. It never appears in `current`, `watch` never yields it, and the Watcher never parses it, so `watcher_parse_failure` is never journaled. `scan` also discards intake's `refused` result, so `serve` now reports the bad ticket nowhere. Before this diff the stem was yielded and the signal was journaled. `test_serve_watcher_edits_deletions_and_last_good` only covers an already-committed stem, so it misses this. The ticket did not ask for this filter, and the boundary check already holds a run whose ticket is dirty.",
      "paved_road": "Restore `{stem: self.read(stem) for stem in self.stems()}` in `scan`. If a filter is still needed, it must keep yielding stems with no committed blob so the Watcher reports them, and a serve test must cover an invalid new stem producing `watcher_parse_failure`.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/mergequeue.py",
      "line": 387,
      "message": "`_admit` runs `ticket_changed` before it reads the retained hold's state, so two paths that are not merge admissions get the hold. (1) Kill: when a held stem has a `reject` release and its ticket was edited, the result is `gate_failed`/`ticket_changed` in the Reject queue. The `rejected` transition, `_dead_dependents` and `retire` are all skipped, so the operator's kill is lost and has to be repeated. (2) Landed squash: when `merge/<stem>/<attempt>` has already completed but a crash came before the `merged` terminal, the latest transition is still `running`. An edit then journals `gate_failed` and removes the worktree for work already on main, and a keep re-runs it. The check added to `reconstruct` at line 219 has the same ordering problem for both cases.",
      "paved_road": "Check `ticket_changed` only on the path that would still admit. For a retained stem, run it after the `reject` release branch and the `completed` squash branch, and before the `_finish` and rebase paths. In `reconstruct`, skip the check when the hold has a reject release or a completed squash effect, and let `_admit` settle those. Add tests for a kill and for a completed squash on a held stem with an edited ticket.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.2",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
