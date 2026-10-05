# chupa

chupa is a continuously running orchestration engine that authors and runs tickets against host repos, including itself: author -> implement -> check -> review -> merge, with failures harvested and follow-ups filed.
Engine plane (chupa-owned) is HOW work runs; host plane (target-repo-owned) is WHAT to build and enters the pipeline only as data. Engine wins on process, host wins on content.

**Read first:** `CHUPA_PLAN.md` is canonical for all design detail. This file is the curated subset of `CLAUDE.md` for non-Claude agent CLIs; `CLAUDE.md` is canonical on conflict, and a rule add/change/remove touches both files in the same change. (section 17)

Every rule below is behavioral (no gate checks it yet): the prose is the only enforcement.

## Engine conduct

- **Pure Python.** No shell scripts, no `shell=True`, no string-assembled commands. External binaries only via argv-list wrapper modules; run only in the chupa venv.
  Why: shell glue is the orchestration failure this design bans. (D1)
- **Simplest thing that satisfies the ticket.** No speculative features, gates, config knobs, or metadata; every addition cites the incident that earned it.
  Why: feature/check accretion is the primary failure mode. (goal 1, D10)
- **No dual-path code.** No compat shims, deprecation layers, or defensive parallel paths. Rename in place, update every call site in the same change, recover by `git revert`.
  Why: parallel paths rot silently and double the review surface. (section 2)
- **Fail closed.** Allowlists and closed vocabularies, never denylists. Every prohibition and every gate finding ships a paved road (what to do instead).
  Why: a denylist misses the case nobody imagined; a prohibition without a road strands the agent. (sections 2, 7)
- **Files + journal are the source of truth.** Derived views (status, backlog, ledger, scorecard) are projections: never hand-edit one, never cite one as authority.
  Why: two authorities diverge; crash recovery folds the journal. (D3)
- **Generated files are render targets, never write targets.** README.md and `bootstrap/conductor.py` extract from the plan's appendix sentinel blocks; CLAUDE.md and AGENTS.md are authored from plan section 17. A change edits the plan and reruns the generator, never the rendered file.
  Why: a hand-edit is overwritten on the next render and the plan drifts from reality. (section 1)
- **All git through `git.py`.** Argv lists, dir-pinned. Worktree cleanup via `worktree remove` + `prune`, never bare `rm -rf`. No `gh`, no PRs in the loop.
  Why: local main is the blessed line; GitHub is a non-blocking sidecar. (section 10)
- **File second problems; never fold them in.** A second problem goes to the Suggestion Box, not the current diff. A pre-existing failure is verified on the base commit, then filed.
  Why: folded fixes blow scope and hide cause. (section 11)
- **Read before write.** No command, claim, or test is written until the artifact that owns that fact has been read.
  Why: guessed facts are the cheapest bug to write and the costliest to find. (section 13)
- **Use the injectable seams.** Clock, process exec, filesystem, and notifications go through their seams; never called raw in engine code.
  Why: fake-driven tests and group-kill guarantees exist only at the seam. (section 15)
- **Fenced by gates, not jailed.** v1 does not sandbox executed code; never rely on its goodwill. Never pass a provider key to a process that does not need it.
  Why: gates and review are the trust boundary. (section 16)
- **The journal is the record, never a debug log.** Diagnostics go to the engine log and attempt spools. Configured secret values are redacted from every captured stream at the write seam.
  Why: the journal is folded for truth; noise and secrets in it are permanent. (section 6)
