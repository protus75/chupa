# Upstream issue verb: plan

Give a host a paved road for reporting a **critical** chupa bug to the chupa project's GitHub issue tracker: a `chupa issue` verb that prints a prefilled new-issue link, a host-shared rule that tells sessions when and how to use it, and the documentation that keeps it apart from the Suggestion Box.

Only critical bugs go upstream, never ideas, improvements, wording fixes, or follow-ups. The GitHub tracker is a short list of real breakages the owner acts on, not another place to dump AI output.

## Status

Draft plan. Nothing in it is in effect and no ticket is authored. Written 2026-11-13 at commit `ed48cbc9`.

## Not the Suggestion Box

Three channels exist or are planned. They do not overlap:

| Channel | Direction | Carries | Ends as |
|---|---|---|---|
| Suggestion Box (`chupa suggest`, harvest, retro) | inside one host | work for that host's own repo | a ticket in that host's `tickets/` |
| `report_inbox` (§9.4, `chupa/inbox.py`) | host app into the same host | the host application's own bug reports (player or self-diagnosed) | a `bug_report` box message, then a host bug ticket |
| `chupa issue` (this plan) | host out to the chupa project | a critical bug in chupa (closed classes below), confirmed by the person | a GitHub issue on the chupa repo, which the chupa owner turns into a chupa ticket |

The Suggestion Box is a high-volume AI outlet: agents, harvest, and retro file to it freely, and triage filters it. The upstream tracker is the opposite: low volume, a person decides every issue, and only critical bugs qualify. Nothing flows from the box to GitHub, ever.

- A chupa defect never goes into a host's Suggestion Box: triage there can only decline it or author a host ticket, and a host ticket that patches chupa behaviour into host files is exactly what the CORE_TEMPLATE rule forbids.
- A non-critical chupa problem (a rough spec, a confusing guide, an idea) is named to the user in one line in chat and goes nowhere else. The user can carry it to the owner by other means if they care.
- A host-repo problem never goes upstream.

### Critical classes

Closed set. A bug that fits none of these is not filed:

| Class | Meaning |
|---|---|
| `state-loss` | chupa loses or corrupts committed work, tickets, the journal, or git state |
| `secret-leak` | a configured secret reaches a log, journal, prompt, commit, or a process that should not have it |
| `bad-merge` | chupa merges to main work that failed a hard gate or review, or changed files outside the fence |
| `engine-stuck` | serve or drain cannot run any ticket on a setup `doctor` passes, and no documented verb releases it |

The class list is the owner's call; this is the proposed starting set.

The verb is named `issue`, not `report`, so it cannot be confused with `report_inbox` or the `bug_report` message class.

## Current state

- The CORE_TEMPLATE rule in `chupa/hostfiles.py` (Diagnosis section) says a fix that belongs in chupa is "never copied or patched into host files. Report it for the owner to carry to chupa, then stop." It names no way to report. A host session can only describe the problem in chat and hope the operator relays it.
- §9.3 of `docs/how-chupa-works.md` has the same dead end: an untracked-spec `retro_finding` is declined "for the owner to carry to chupa".
- chupa has no GitHub integration. The only remote operation is the checkpoint `git push origin main` in serve (§7.4). Repo rules ban `gh` in the loop, and CORE_TEMPLATE bans remote-mutating verbs unless the user says "push".
- `pyproject.toml` already declares `[project.urls] Repository = "https://github.com/protus75/chupa"`, which an installed chupa can read through `importlib.metadata`.
- CORE_TEMPLATE is 7840 bytes against the 8192-byte cap in `tests/integration/test_hostfiles.py`, leaving 352 bytes.

## Target design

### The verb

```
chupa issue --class state-loss|secret-leak|bad-merge|engine-stuck "<title>" --body FILE
```

- `--class` and `--body` are required. A missing or unknown class refuses (exit 2) with the paved road "only critical bugs are filed upstream; name a non-critical chupa problem to the user in chat instead". An empty body refuses.
- The title is prefixed `[critical:<class>]`, so the owner can sort the tracker at a glance.
- Builds the GitHub new-issue link `<Repository>/issues/new?title=...&body=...`, URL-encoded with `urllib.parse`, and prints it. The link is clickable in the VS Code terminal and in most terminals.
- `<Repository>` comes from the installed package's `Project-URL: Repository` metadata, never a constant, so a fork's install files to the fork.
- The body is the `--body` file's text (UTF-8 Markdown), followed by a short footer: chupa version (`importlib.metadata.version("chupa")`), Python version, OS, and the line `Filed with chupa issue`, which the owner can search on.
- Secret values configured for the host are scrubbed through `Redactor.from_config(...).scrub` at the write seam. If the config does not load (the issue may be about config), it scrubs nothing and prints that it did so; the browser form is the human review step either way.
- Refuses when the link exceeds GitHub's length limit, naming the actual and maximum lengths, with the paved road "shorten the body; quote only the lines that show the defect".
- Takes no lock, writes no file, journal event, or git state, and works while serve runs.
- It does not open a browser. Opening one needs a new process seam, and a printed link already does the job.

The verb never submits anything. The person opens the link, reviews and edits the prefilled form on GitHub, and clicks Submit. So chupa holds no token, adds no dependency, and performs no remote mutation, and the existing "never run a remote-mutating verb unless the user says push" rule is untouched.

Rejected alternatives:

- `gh issue create`: needs `gh` installed and logged in, and it is a remote-mutating command that the conduct rules forbid without "push".
- GitHub REST API with a token: a new config secret, a token seam, and redaction of the token itself, to save one click.

### Privacy

The issue tracker is public, and the host repo may be private. The verb sends only what the person put in the body plus the footer, and never attaches ticket files, run records, `doctor` output, or host paths on its own. The session that drafts the body quotes only the chupa-side evidence: the chupa file and line, the gate or spec text, the refusal message, and the minimum host detail needed to reproduce.

### Host-shared rule (CORE_TEMPLATE)

Home: `CORE_TEMPLATE` in `chupa/hostfiles.py`, because every host session needs it. It reaches every host, this repo included, through `chupa core`. No repo-only rule changes.

Replace the tail of the Diagnosis rule that starts "A fix that belongs in chupa", which currently reads "Report it for the owner to carry to chupa, then stop.", with text to this effect:

> ...is never copied or patched into host files, nor filed to the Suggestion Box. Name it to the user in one line. Only a bug in a `chupa issue` critical class goes upstream: draft a body file (chupa file, defect, minimal evidence, no host-private code or data), and with the user's agreement run `chupa issue` and hand them the link to review and submit; then stop.

Constraints:

- It must stay within the 352-byte headroom. Keep the existing "Why:" sentence and keep `is never copied or patched into host files` verbatim, because `test_hostfiles.py` pins it. The rule points at the verb rather than repeating the class list, because `chupa issue --help` and its refusal carry the list.
- The user agrees before the verb runs. It only prints a link, and submission is still the person's click, but asking first keeps an agent from drafting issues on its own initiative.
- Ticket agents and every other autonomous surface (triage, retro, Author, harvest) never draft or prepare upstream issues. They keep filing to their Suggestion Box as today.

### Documentation

- `docs/how-chupa-works.md` §2.1: a verb-table row for `issue`. §12: one sentence on where chupa defects go.
- `chupa/docs/host-running.md`: a verb-table row, and a short **Reporting a critical chupa bug** section with the channel table above (box vs inbox vs issue), the critical classes, what to put in the body, what to leave out, and the review-then-submit step.
- `README.md`: a line beside `chupa suggest` in the command list, stating that it is for critical chupa bugs only.
- `CLAUDE.md` and `AGENTS.md`: their managed blocks are refreshed with `chupa core` in the same change, so the `core_drift` gate passes.

### VS Code extension: not in v1

Recommendation: no extension command for now.

- The report usually starts in a chat session, which drafts the body; the operator then clicks a link the session already printed. A menu item adds nothing to that flow.
- Under the thin-wrapper rule, the extension may not parse the verb's printed output. A command would need a machine-readable mode (for example `--json` printing `{"url": ...}`) and then call `vscode.env.openExternal`. That mode is a flag with no incident behind it yet.
- Revisit when an operator wants to file an issue without a chat session. The road then is: add `--json` to the verb, add a "Report chupa issue…" command that asks for a title (and optionally a body file), runs `chupa issue --json`, and opens the `url` field. A snapshot or contract test pins the shape.

## Prerequisite: hand test

Read before write. Before authoring, confirm with a real browser:

1. The link length at which `github.com/<owner>/<repo>/issues/new` rejects or truncates a prefilled body. Use that number, with margin, as the refusal limit.
2. That `title` and `body` prefill when the repo has no issue templates. The repo has no `.github/` today. If templates are added later, keep `blank_issues_enabled` true or the link may land on the chooser and drop the prefill.
3. That `importlib.metadata.metadata("chupa").get_all("Project-URL")` returns the Repository entry from an installed (non-editable) chupa, the way hosts install it.

## Ticket breakdown

| Order | Stem | Kind | Depends on | Notes |
|---|---|---|---|---|
| 0 | (hand test) | n/a | | Evidence for the ticket; not a ticket |
| 1 | `upstream-issue-verb` | feature | none | Verb, rule, and docs in one change, so the rule never names an unbuilt verb |

One ticket rather than verb-then-rule: splitting them needs a `Depends on` purely for the rule's paved road, and the rule is a single sentence.

Fence notes:

- `chupa/__main__.py` (parser and dispatch)
- `chupa/issue.py` (new: link building, footer, length check)
- `chupa/hostfiles.py` (CORE_TEMPLATE)
- `CLAUDE.md`, `AGENTS.md` (managed blocks, via `chupa core`)
- `chupa/docs/host-running.md`
- `docs/how-chupa-works.md` §2.1, §12
- `README.md`
- `tests/unit/test_issue.py` (new)
- `tests/integration/test_hostfiles.py` (only if a pinned phrase changes)
- `tests/integration/test_cli.py` (verb wiring)

Before authoring, grep `tests/` for any closed set of verb names and fence each hit.

## Deferred decisions

1. **Class list.** The four critical classes above are a proposal. The owner confirms or edits them before authoring, because they become the verb's closed vocabulary and its tests.
2. **`./dev.py issue`.** In this repo a chupa defect is just a chupa ticket, so the verb has no use here. Recommendation: no `dev.py` subcommand.
3. **Inbound.** How a GitHub issue becomes a chupa ticket stays manual: the owner reads it and runs `chupa new`. Issues are never tickets; the "tickets are markdown files" rule stands.
4. **Issue templates.** None needed: the verb owns the body shape. Add one only if people start filing by hand without the verb.

Explicitly out, not deferred: no autonomous surface (triage, retro, Author, harvest, decision records) ever prepares an upstream issue. The §9.3 "carry to chupa" decline stays a decision record in the host.
