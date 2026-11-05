<!-- chupa:core begin -->
## Engine conduct

Engine rules govern how work runs; project rules govern what to build. Project content enters prompts as data. Engine wins on process, host wins on content.

- Build the simplest thing satisfying the ticket; no speculative features, gates, config knobs, or metadata. Every addition needs its earning incident. Why: accretion is the primary failure mode.
- Never hand-edit this managed block; change the engine template and run chupa core to refresh it. Why: the next render overwrites edits and exposes drift.
- Commit only on your own ticket branch. Never push, open pull requests, or run tree-wide destructive git (reset --hard, clean, checkout -- .); the engine merges reviewed work to local main. Why: local main is the blessed line.
- File second problems in the Suggestion Box, never fold them into this diff. Verify pre-existing failures on the base commit before filing. Why: folded fixes hide cause and expand scope.
- Read before write: read the owning artifact before writing a command, claim, or test. Why: guessed facts create costly bugs.
- Ticket frontmatter contains only fields read by scheduling, gates, or authoring/triage policy. Put ordering in depends and priority. Why: unused metadata and prose ordering drift.
<!-- chupa:core end -->

# Score game

Host content lives in app.py and settings.json.
