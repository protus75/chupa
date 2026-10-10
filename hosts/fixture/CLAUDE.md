<!-- chupa:core begin -->
## Engine conduct

Engine rules govern how work runs; project rules govern what to build. Project content enters prompts as data. Engine wins on process, host wins on content.

- Pure Python: no shell scripts, shell=True, or string-assembled commands; external binaries use argv wrapper modules in the chupa venv. Why: shell glue breaks orchestration. (D1)
- Build the simplest thing satisfying the ticket; no speculative features, gates, config knobs, or metadata. Every addition needs its earning incident. Why: accretion is the primary failure mode. (goal 1, D10)
- No compatibility shims, deprecation layers, or defensive parallel paths. Rename in place, update all callers, recover by git revert. Why: dual paths rot and double review. (section 2)
- Fail closed with allowlists and closed vocabularies; every prohibition and gate finding provides a paved road. Why: denylists miss cases and roadless refusals strand work. (sections 2, 7)
- A hold ships with or after its release surface; never name an unbuilt release verb. Ticket-change releases follow machine ticket-change machinery. Why: unreleasable holds permanently stall work. (sections 2, 11)
- Files and journal are truth; derived views are projections, never hand-edited or cited as authority. Why: two authorities diverge. (D3)
- Generated files are render targets, never write targets. Change their owning source and regenerate; never hand-edit managed conduct. Why: regeneration overwrites edits and exposes drift. (section 1)
- The plan is the seed: repair plan defects there, then regenerate affected artifacts. Hand-edit only defects proven outside the plan, or under the blocking-defect fast path after committing the plan repair first. Why: the seed must reproduce the artifact. (sections 1, 19)
- All git uses git.py with argv lists and pinned directories. Remove worktrees with worktree remove plus prune; no bare rm -rf, gh, or PRs in the loop. Why: local main is the blessed line. (section 10)
- File second problems in the Suggestion Box, never fold them into this diff. Verify pre-existing failures on the base commit before filing. Why: folded fixes hide cause and expand scope. (section 11)
- Read before write: read the owning artifact before writing a command, claim, or test. Why: guessed facts create costly bugs. (section 13)
- Ticket frontmatter contains only fields read by scheduling, gates, or authoring/triage policy. Put ordering in depends and priority. Why: unused metadata and prose ordering drift. (section 13)
- Use injectable clock, process-exec, filesystem, and notification seams; never raw calls in engine code. Why: fake-driven tests and group-kill guarantees require seams. (section 15)
- Work is fenced by gates and review; v1 does not sandbox executed code. Never rely on its goodwill or pass provider keys to processes that do not need them. Why: gates and review are the trust boundary. (section 16)
- The journal is the record, never a debug log. Diagnostics use the engine log and attempt spools; redact configured secrets at every captured-stream write seam. Why: journal noise and secrets are permanent. (section 6)
- Start a phase only after the previous phase's exit is met. Why: later phases need proven ground. (section 19)
<!-- chupa:core end -->

# Score game

Host content lives in app.py and settings.json.
