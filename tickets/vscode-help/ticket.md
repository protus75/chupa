---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- vscode-chupa/extension.js
- vscode-chupa/package.json
- vscode-chupa/media/view.js
- vscode-chupa/media/detail.js
- vscode-chupa/media/box.js
- vscode-chupa/README.md
- chupa/observe.py::snapshot
- chupa/observe.py::recent_steps
- chupa/observe.py::STEP_NAMES
- chupa/observe.py::PHASE_NAMES
- chupa/observe.py::STEP_KINDS
- chupa/stats.py::stats_tree
- chupa/stats.py::project_stats
- chupa/status.py::SETTLED
- chupa/box.py::MessageClass
- chupa/__main__.py::_parser
- chupa/docs/host-running.md
- chupa/docs/host-contract.md#VS Code extension
- tests/unit/test_host_running.py
- tests/integration/test_stats.py::test_stats_tree_generic_rows
- tests/integration/test_step_icons.py
- tests/integration/test_vscode_command_not_found.py
- tests/regress_vscode_task_identity.py
- tests/vscode_step_icons.js

## On-demand
- docs/how-chupa-works.md
- tests/integration/test_watch.py
- tests/vscode_task_identity.js
- tests/vscode_command_not_found.js
- CLAUDE.md
- AGENTS.md

## Goal / Why
The VS Code extension explains almost nothing on screen. Its row statuses, section badges, lock
icons, step kinds, Suggestion Box classes and counts, Stats rows, and menu actions carry no hover
text or doc links. The one place with explanatory text, the Engine… picker, uses `detail` strings
hand-copied into `chupa/observe.py::snapshot`. They restate rows of the run guide's verb table and
will drift from it.

When this ticket is done, every surface the extension shows has help with the same shape. One
sentence says what the thing is. A `Before:` line says what generally comes before it, and an
`After:` line says what generally follows. A link opens the doc section that owns the fact. All
help comes from one Python source, `chupa/help.py`, delivered through the snapshot and
`stats --tree` output. Extension JavaScript only draws it, following the thin-wrapper rule. Tests fail when a
new command, view, setting, or snapshot vocabulary value lacks help, or when a help link points at a
missing heading. A new chupa-only rule in `CLAUDE.md` and `AGENTS.md` keeps help text current.

Help text sources, in order of preference:
1. A string the code already owns: the status reasons `chupa/observe.py::snapshot` builds stay as
   they are, with their help attached alongside.
2. A string a doc owns: a verb topic's `what` sentence is the `What it does` cell of that verb's
   row in `chupa/docs/host-running.md`, read at snapshot time with backticks removed. That table is
   already pinned to the CLI parser by `tests/unit/test_host_running.py`.
3. Otherwise, text written in `chupa/help.py` that links to the doc heading that owns the fact.
   `Before:` and `After:` text is always written there.

Link targets, deterministic per doc file (no fallback path):
- A doc shipped in the package (`chupa/docs/*.md`, found as `Path(chupa.__file__).parent / "docs"`)
  links to that installed file and the 0-based line of the target heading. A verb topic links to
  the line of its verb-table row. The extension opens the file in an editor with the cursor on that
  line, so a host gets the guide matching its installed version.
- A doc not shipped in the package (`docs/how-chupa-works.md`) links to
  `<Repository URL>/blob/main/<repo path>#<GitHub heading slug>`. The Repository URL is read from
  the installed package metadata (`importlib.metadata`, the `Project-URL` named `Repository`),
  never typed as a literal in `chupa/help.py`.

## Scope in / Scope out
Scope in:
- New `chupa/help.py` holds the help registry.
  - Topic keys form one closed vocabulary with kind prefixes: `view.<view id>`,
    `command.<command id>` (non-verb commands only), `verb.<verb>`, `section.<section>`,
    `status.<reason>`, `step.<step>`, `box.<message class>`, `boxOutcome.<outcome>`, `stat.<key>`,
    `lock.<engine|commit>`, and `priority`.
  - Each topic has `what`, `before`, `after`, and a link target (doc path plus heading, or for
    verbs, the verb row).
  - A command map sends each contributed command id to its topic: a verb-backed command maps to
    its `verb.*` topic, for example `chupa.ticket.review` to `verb.review` and `chupa.ticket.priority`
    to `verb.order`. Every other command has its own `command.*` topic.
  - A function builds, for the snapshot, `{key: {"what", "before", "after", "text", "link"}}`.
    `text` is exactly `<what>\nBefore: <before>\nAfter: <after>`. `link` is
    `{"label", "path", "line"}` for a packaged doc and `{"label", "url"}` otherwise.
  - The same module supplies a builder for the Help picker list (see `chupa.help` below).
  - A link whose heading or verb row does not resolve raises; it does not return a partial map.
  - The builders take the doc reader as a parameter (`read: Callable[[Path], str]`). `snapshot`
    passes `Path.read_text`, and unit tests pass in-memory text, so `tests/unit/test_help.py`
    writes nothing to disk.
- `chupa/observe.py::snapshot` adds these fields:
  - top-level `help`, the map above;
  - `helpPick`, an ordered QuickPick list, with one `{"kind": "separator", "label"}` per topic kind,
    then `{"label", "description", "detail", "topic"}` items, plus one final settings item
    `{"label", "detail", "command": "chupa.openSettings"}`, which carries `command` and no `topic`;
  - `headerHelp`, the topic keys for each Tickets header count and each lock indicator;
  - `boxHeaderHelp`, the topic key for each Suggestion Box header count.
- Each status branch in `snapshot` names its `status.*` key next to the text it builds; `snapshot`
  never parses status text. The branches are:
  - invalid, new, draft, held until change, held for keep or kill, waits on, not eligible;
  - interrupted, retry pending, after, ready;
  - running, merged, and each other settled state.

  These keys form a closed module-level vocabulary in `chupa/observe.py`.
- Snapshot items carry topic keys:
  - each ticket row carries `help: {"section": key, "status": key}`, and `priorityHelp` when it shows a
    priority tag;
  - each ticket row carries `next`, the help keys of the menu actions that are `on` for it, in menu
    order;
  - each box row carries `help: {"class": key, "outcome": key}`;
  - each step carries `help`, its `step.*` key (start, ok, and failed share one step topic) and
    `tooltip`, the full tooltip text that Python builds from the date, stem, step text, and topic text.
- In `engineVerbs`, `detail` becomes the `what` of the verb topic. This removes the hand-copied strings.
- `chupa/stats.py::stats_tree` gives each top-level row whose key has a `stat.<key>` topic a
  `tooltip` equal to that topic's `text`. Child rows do not change.
- `vscode-chupa/package.json` changes:
  - adds a `chupa.help` command (title `Help`, icon `$(question)`), visible in the Command Palette and placed
    in every chupa view's title overflow menu;
  - replaces each setting's `description` with a `markdownDescription` in the same three-part shape,
    ending with a link to its doc section as a `https://github.com/protus75/chupa/blob/main/...#slug`
    URL. `chupa.command` links to `chupa/docs/host-contract.md` `## VS Code extension`.
    `chupa.statsWindow`, `chupa.refreshSeconds`, `chupa.unavailableMenuItems`, and
    `chupa.playAction` link to the `docs/how-chupa-works.md` section 2.2 heading;
  - adds `viewsWelcome` entries for `chupa.steps` and `chupa.stats` when they are empty: one sentence
    plus `[Open chupa help](command:chupa.help)`.
- `vscode-chupa/extension.js` changes:
  - registers `chupa.help`, which shows `snap.helpPick`. For the chosen item it runs `item.command` when
    the item has one, and otherwise runs `chupa.openHelp(item.topic)`;
  - registers an internal `chupa.openHelp(topic)`, not contributed. It opens a `path` link in a text
    editor with the selection at `line` and a `url` link with `openExternal`;
  - shows Recent Steps tooltips as a trusted `MarkdownString` of `step.tooltip` plus a
    `command:chupa.openHelp` "Learn more" link;
  - shows Stats top-level tooltips from `row.tooltip`;
  - handles a webview `{type: 'help', topic}` message by running `chupa.openHelp`;
  - handles a webview `{type: 'readme'}` message by opening the bundled `README.md` in the Markdown
    preview.
- Webview changes:
  - `media/view.js`:
    - header counts and lock icons get `title` from their topics;
    - each row gets `title` from its status topic `text`;
    - the priority tag gets `title` from `priority`.
  - `media/box.js`: header counts and rows get `title` from their topics.
  - `media/detail.js`:
    - the section badge gets `title` from the section topic, and the status line is followed by the
      status topic `text` and a "Learn more" link;
    - a `Next` section lists each `next` topic's `what` with its own "Learn more" link;
    - a box message shows its class and outcome topic `text` the same way;
    - the empty state shows the `view.chupa.details` topic `text`, not the hard-coded sentence.
  - `media/view.js` and `media/box.js`: the `snapshot failed` error state adds an "Open setup help"
    link that posts `{type: 'readme'}`.
  - `media/view.css`: styling for the help text and links only.
- `vscode-chupa/README.md` gains a `## Help` section. It says where help appears (hover, Details
  `Next`, the Help command, settings) and that the error-state link opens this README.
- `docs/how-chupa-works.md` section 2.2's extension paragraph says that the extension's help comes
  from `chupa/help.py` through the snapshot, that each surface shows what it is plus `Before:` and
  `After:` lines and a doc link, and that `chupa.help` lists every topic. It also gains one sentence
  each for `chupa.refreshSeconds` and `chupa.unavailableMenuItems`, so every setting's link has a
  documented target.
- `chupa/docs/host-contract.md` `## VS Code extension` gains one sentence naming the Help command
  and hover help.
- `CLAUDE.md` section A and `AGENTS.md` gain this rule, placed right after the "extension is a thin
  wrapper" rule and outside the `chupa:core` managed block. Its home is this repo, not
  `CORE_TEMPLATE`, because it governs chupa's own extension and does not apply to hosts:

  ```
  - **Extension help has one source.** Every extension surface a person sees (view, command, setting, header indicator, and each snapshot vocabulary value) shows help: one sentence saying what it is, then what comes before and after it, with a link to the doc section that owns the fact. Help comes from `chupa/help.py`, which reuses a code- or doc-owned string (a status reason, a `chupa/docs/host-running.md` verb row) where one exists and writes text only where none does; settings carry theirs in `package.json` `markdownDescription`. A change that adds an extension surface or vocabulary value, or changes behavior a help entry or its linked section describes, updates that entry in the same change. `tests/unit/test_help.py` fails on a missing entry or a dead link; keeping the text true is this rule's job.
    Why: help copied into the extension drifts from the code and docs it describes; the snapshot already carried hand-copied verb descriptions (`engineVerbs`) that restated the run guide (2026-11-13).
  ```
- `tests/vscode_step_icons.js`, `tests/vscode_task_identity.js`, and `tests/vscode_command_not_found.js`
  may gain only the `vscode` mock members the new extension code calls, such as `MarkdownString`. Their
  assertions do not change.
- `tests/integration/test_watch.py` changes one expectation: the `engineVerbs[0]` `detail` equals
  the `drain` row's `What it does` cell from `chupa/docs/host-running.md` with backticks removed, not
  the old literal. It also gains the
  snapshot help assertions in criterion 8.

Scope out:
- The lifecycle panel and `media/ticket-lifecycle.svg` stay as they are, because the image is static.
- A `contributes.walkthroughs` onboarding flow is left out because it would copy the install steps
  that `chupa/docs/host-contract.md` owns.
- Priority QuickPick items, the Activity Bar badge tooltip, and `showErrorMessage` texts stay as they are.
- `chupa/docs/host-running.md` content, `chupa/__main__.py`, and `chupa/stats.py::project_stats` stay
  as they are.
- Shipping `docs/how-chupa-works.md` inside the package stays out of scope; it is linked on GitHub.
- No help text is written in JavaScript. The only JavaScript string literals added are the link
  labels "Learn more" and "Open setup help", plus the section heading `Next`.

## Scope fence
- chupa/help.py
- chupa/observe.py
- chupa/stats.py
- vscode-chupa/extension.js
- vscode-chupa/package.json
- vscode-chupa/media/view.js
- vscode-chupa/media/detail.js
- vscode-chupa/media/box.js
- vscode-chupa/media/view.css
- vscode-chupa/README.md
- docs/how-chupa-works.md
- chupa/docs/host-contract.md
- CLAUDE.md
- AGENTS.md
- tests/unit/test_help.py
- tests/integration/test_watch.py
- tests/vscode_step_icons.js
- tests/vscode_task_identity.js
- tests/vscode_command_not_found.js

## Acceptance criteria
1. `tests/unit/test_help.py::test_topic_shape`: every topic's `text` has exactly three lines.
   - Line 1 is the non-empty `what` and ends with `.`.
   - Line 2 starts with `Before: ` and line 3 starts with `After: `, each followed by non-empty text.

   A topic missing `before` or `after`, or with an empty `what`, fails.
2. `tests/unit/test_help.py::test_links_resolve`: every topic's link resolves.
   - A `path` link names a file under the installed `chupa/docs`, and its `line` holds the named
     heading or, for a verb, that verb's table row.
   - A `url` link starts with the package metadata Repository URL plus `/blob/main/`, names a repo
     file that exists, and has a fragment equal to the GitHub slug of a heading in that file.

   A link to a renamed or missing heading fails, as does a line number off by one.
3. `tests/unit/test_help.py::test_vocabularies_covered`: each of these has a topic:
   - `blocked`, `queued`, `running`, and `merged`;
   - every member of the `chupa/observe.py` status-key vocabulary;
   - every step in `STEP_KINDS` values;
   - every `chupa.box.MessageClass` member;
   - every box outcome (`pending`, `reopened`, `author`, `tombstone`, `declined`);
   - every top-level key of `project_stats` run on an empty journal;
   - both lock indicators;
   - every `engineVerbs` argv verb.

   Adding a value to any of these vocabularies without a topic fails.
4. `tests/unit/test_help.py::test_manifest_covered` reads `vscode-chupa/package.json`.
   - Every `contributes.commands[].command` is in the command map, and every mapped topic exists.
   - Every `contributes.views.chupa[].id` has a `view.*` topic.
   - Every `contributes.configuration.properties` entry has a `markdownDescription` containing
     `Before:` and `After:` and no `description` key. Its GitHub link resolves under the rule in
     criterion 2.

   A new command, view, or setting without help fails.
5. `tests/unit/test_help.py::test_verb_what_from_run_guide`: for every `verb.*` topic, `what` equals
   that verb's `What it does` cell in `chupa/docs/host-running.md` with backticks removed. The test
   then passes the builder in-memory run-guide text with the `review` cell rewritten and asserts that
   `verb.review`'s `what` changes to match. A separately typed string fails.
6. `tests/unit/test_help.py::test_unresolved_link_raises`: the builder raises in two cases, when
   given in-memory doc text with a linked heading renamed, and when given run-guide text missing a
   verb row. Returning a map without the topic fails.
7. `tests/unit/test_help.py::test_help_pick_list`: the Help picker builder returns one separator per
   topic kind, each before that kind's items. Every non-separator item except the last carries a
   `topic` that is a help key. The last item carries `"command": "chupa.openSettings"` and no `topic`.
8. `./dev.py test tests/integration/test_watch.py` passes with the existing snapshot fixture.
   - `snap["engineVerbs"][0]["detail"]` equals the `drain` row's `What it does` cell with
     backticks removed, not `"Run every eligible ticket to quiescence, then exit."`.
   - Every row's `help.section` and `help.status` and every key in its `next` are keys of
     `snap["help"]`.
   - Every step's `help` is a key of `snap["help"]`, and its `tooltip` contains that topic's `text`.
   - Every non-separator `helpPick` item carries either a `topic` that is a key of `snap["help"]`,
     or a `command`, which only the settings item carries.

   A row or step that names a key missing from the map fails.
9. `tests/unit/test_help.py::test_stats_tree_tooltips`: `stats_tree` of `project_stats` on an empty
   journal gives every top-level row a `tooltip` equal to its `stat.*` topic `text`. The existing
   `tests/integration/test_stats.py::test_stats_tree_generic_rows` still passes unchanged, so child
   rows have no `tooltip` key.
10. `node --check` exits 0 for `vscode-chupa/extension.js`, `vscode-chupa/media/view.js`,
   `vscode-chupa/media/detail.js`, and `vscode-chupa/media/box.js`.
11. `./dev.py test tests/integration/test_step_icons.py tests/integration/test_vscode_command_not_found.py`
   passes, so no step kind's icon becomes `null` and the not-found message text is unchanged.
   `uv run python tests/regress_vscode_task_identity.py` prints `{"regression_result": "pass"}` and
   exits 0, so `activate()` still runs under the harness mock.
12. `CLAUDE.md` and `AGENTS.md` each contain the `**Extension help has one source.**` rule exactly
    as quoted in Scope in, after the `<!-- chupa:core end -->` line in `CLAUDE.md`. This is checked by
    the `python -c` command in `## Verification`.
13. Readers can check these docs:
    - `docs/how-chupa-works.md` section 2.2 names `chupa/help.py`, the `Before:`/`After:` shape, and
      `chupa.help`;
    - `chupa/docs/host-contract.md` `## VS Code extension` names the Help command;
    - `vscode-chupa/README.md` has a `## Help` section.
14. `./dev.py test` exits 0.

## Verification
```
node --check vscode-chupa/extension.js
node --check vscode-chupa/media/view.js
node --check vscode-chupa/media/detail.js
node --check vscode-chupa/media/box.js
uv run python -c "import pathlib; c = pathlib.Path('CLAUDE.md').read_text(); a = pathlib.Path('AGENTS.md').read_text(); r = '**Extension help has one source.**'; assert c.index(r) > c.index('<!-- chupa:core end -->') and r in a"
./dev.py test tests/unit/test_help.py tests/integration/test_watch.py tests/integration/test_stats.py tests/unit/test_host_running.py
./dev.py test tests/integration/test_step_icons.py tests/integration/test_vscode_command_not_found.py
uv run python tests/regress_vscode_task_identity.py
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- JavaScript writes help text, builds a topic key from a string, parses a status or doc, or looks up
  help any other way than reading a key the snapshot or `stats --tree` row supplies;
- `chupa/help.py` contains the GitHub repository URL as a literal, or copies a verb's `What it does`
  text instead of reading it from `chupa/docs/host-running.md`;
- a link built by `chupa/help.py` falls back from a local path to a URL, or the reverse, for the
  same doc;
- `engineVerbs` still carries a hand-written `detail` string;
- the new rule is placed inside the `chupa:core` managed block or in `chupa/hostfiles.py` `CORE_TEMPLATE`;
- `chupa/docs/host-running.md`, `chupa/__main__.py`, or `project_stats` changes.

## Time budget
- expected: 120m
- stuck: 180m
