# chupa roadmap

The one place that orders chupa's planned work. Each plan under `docs/` owns its own design; this document owns what the plans share: priority, release slot, cross-plan ordering, shared budgets, and the decisions that settle where plans overlap or contradict. It also carries the audit of the code and documents that the ordering rests on: what is duplicated, what is missing, and where the documents have drifted from the code.

A plan change that moves a ticket, adds a dependency on another plan, or spends a shared budget updates this document in the same change. A ticket authored from a row here is linked by stem in that row.

## Status

Written 2026-11-13 at commit `80b76d5d` (chupa `0.1.5`, extension `0.0.40`, no git tags). The audit sections are a snapshot at that commit, produced by six read-only passes over `chupa/`, `tests/`, `dev.py`, `docs/`, `chupa/docs/`, `chupa/specs/`, `CLAUDE.md`, `AGENTS.md`, `README.md`, and `CHUPA_PLAN.md` §18-19. Re-run the audit before each minor release; the section headings are the checklist.

Facts the ordering rests on:

- 506 tickets merged, 0 in flight, 0 confirmed and unrun. The queue is empty. One stem awaits a verdict in the Reject queue (`vscode-help`, `premise_failed`). Four stems are blocked in the journal with no ticket directory (`authoring-reading-specs`, `host-mechanical-check`, `phase7-continue`, `journal-sql-refactor-plan`).
- Four Suggestion Box messages are pending: `box-000324` (fence closure misses in-code registries; recurrence recorded in `tickets/retro/000046.md`), `box-000440` (operator prompts hard-code `./dev.py`), `box-000441` and `box-000442` (unit-test criteria that need disk pass requisition review, then fail Implement). None is a ticket yet.
- Spend to date $2,681.50. 5,090 commits since 2026-10-01.
- `CHUPA_PLAN.md` phases P3-P6 are complete. P7 `host-review-surfaces` was refused instead of built (`config.py:308-309`). P8 `rules-render` (`core --check`, a start-command file) and the "Onboarding a host" and "Operating facts" sections of `chupa/docs/host-contract.md` were never built and have no ticket. The registry that tracked them was retired, so only this document and the frozen plan record them.
- The CLI has 29 verbs (`chupa/__main__.py:237-287`) against the frozen plan's closed set of 16 (§18.1). Each arrived by ticket; the plan cannot be amended.

## 1. Release plan

Versions follow `pyproject.toml` (`0.1.5` today). Each release below is a minor version and gets a git tag. `./dev.py publish` bumps only the patch version and nothing creates a tag today, so the first ticket in 0.2.0 is the release verb that makes the rest of this table executable.

| Release | Theme | Gate to start | Gate to ship |
|---|---|---|---|
| **0.2.0** | Truth, hygiene, and shared infrastructure | none | every P0 and P1 row merged; evidence capture live; `docs-truth-sweep` merged so the next audit starts clean |
| **0.3.0** | Journal query layer (`docs/journal-sql-refactor-plan.md`) | re-measurement shows a drain start or `status` still dominated by journal reads after `journal-incremental-read` (merged `f790cf71`); if not, this release slides behind 0.5.0 and its slot is skipped | all four port groups merged and the SQL-only gate in place; no feature ticket runs during the window |
| **0.4.0** | Parallel runs and the graphics kind (`docs/parallel-tickets-plan.md`, `docs/gemini-graphics-refactor-plan.md` Part B) | 0.2.0 dedup tickets merged (`active-slot-single-owner`, `merge-admission-single-owner`, `closed-sets-single-home`) | `scheduler.parallel.enabled: true` has run this repo's own queue for one week with no conflict rerun cap hit |
| **0.5.0** | Training flywheel (`docs/training-data-plan.md`, evidence verbs) | evidence store has captured at least one full drain | `training export` produces every record kind from this repo's journal; `training eval` scores one lens |
| **0.6.0** | Document agent (`docs/document-agent-plan.md`) | isolated read-only calls proven by `isolated-readonly-call`; the owner's lens prompts adapted | the three plans written on 2026-11-13 moved into doc sets and reviewed with `scope` and `buildability` |

Independent of release: `gemini-provider` and `upstream-issue-verb` land in 0.2.0 because they touch nothing the later releases reshape, and both wait on a hand test (their plans say which facts).

### 1.1 Why this order

- **Truth first.** The audit found 16 places where the maintained documents say something the code does not do, a wrong surface label on every provider failure in Implement, Check, and Review, and a capture bug that has lost 1,491 of 3,944 raw model-call records. None of the feature plans can be authored against documents that are wrong, and the training plan cannot capture data that is being overwritten.
- **Dedup before parallel.** Parallel runs change the one-run assumption in six separate trackers and the merge path in two separate implementations. Making each of those a single owner first turns the parallel tickets from a rewrite into an edit.
- **Capture early, export late.** The evidence store (0.2.0) only has value once it holds data. Export and eval (0.5.0) are useful on day one if capture started three releases earlier.
- **Journal window is conditional.** Its measured trigger (157 of 164 seconds in journal reads) predates `journal-incremental-read`. The refactor freezes features for a release; it earns that only if re-measurement shows the cost is still there.
- **Document agent last.** It is the largest new surface, depends on the isolated-call mode and the evidence record, and its first real use is reviewing the other plans, which is more useful once those plans have tickets behind them.

## 2. Analysis: duplication

Ranked by how many later tickets it blocks. Every item names the single owner that should remain.

### 2.1 Engine core

| # | Duplicated | Locations | Owner after fix | Ticket |
|---|---|---|---|---|
| 1 | Inline merge and queue admission share about 15 steps verbatim: `ticket_change_findings`, timing and `_refused`, `rev_parse`, `main_code_unchanged`, `restore(TICKETS_DIR)`, the `RebaseRefused` finding text, `gather_safety_evidence`, the skip rule, `read_candidate`, `check_severity`, `run_gates` on both gate sets, hard and soft flattening, `dirty_overlap`, `write_squash` + `retire` | `merge.merge` (`chupa/merge.py:285-328`) vs `MergeQueue._admit` (`chupa/mergequeue.py:271-370`) | `_admit`, with the conflict ladder, safety tier, receipt, tree check, and red streak as parameters; `merge.merge` becomes a thin inline call | `merge-admission-single-owner` |
| 2 | Six trackers for "is something running": `scheduler.py:35-36`, `daemon.py:547-549` (`DaemonAdmission`), `daemon.py:440` (`TicketWriter.active`), `mergequeue.py:86,91`, `driver.py:152`, `restart.py:16` + `serve.py:112`. `serve.upgrade_idle` reads five of them (`serve.py:325-333`). `Scheduler._slot` wraps `admission.dispatch`, which takes its own lock | as listed | `DaemonAdmission` owns the run set; others read it | `active-slot-single-owner` |
| 3 | Three filters over `review.mechanical`: `stages.triggered_hosts` (`stages.py:982-987`), `merge.py:317` (`hard_only=True`), `MergeQueue.host_checks` (`mergequeue.py:198-224`); spool names also diverge (`check/host-NN`, `merge/host-NN`, `merge-<tier>/host-NN`). `docs/how-chupa-works.md:337` says "one shared command runner": true for execution, false for selection | as listed | `triggered_hosts(tier=...)` | `host-check-selection-single-owner` |
| 4 | Run-argv-with-stuck-budget, spool, tail: `run_host_command` (`stages.py:712-728`), `gather_evidence` branch loop (872-885), base loop (893-902), `_gather_bug.execute` (822-829); `MergeQueue._command` (195-196) is a pure pass-through | `chupa/stages.py` | `run_host_command` | `host-check-selection-single-owner` |
| 5 | "Latest `state_transition` for stem" scanned inline 13 times: `stages.py:287,1562`; `serve.py:151,158,411`; `drain.py:107,456,547,586,594,681,699,731`. `status.last_states` returns only the state string | as listed | `journal.last_transition(events, stem)` beside `run_terminals` | `journal-last-transition-helper` |
| 6 | Effect-completion lookups by key bypass `Effects._recorded` (`effects.py:49-53`): `stages.served_review:198`, `mergequeue.retained_ticket:138`, `merge.lifted_report_paths:370-376`, `runner.apply_admission:676-680`, `mergequeue._finish:164`, `checkpoint._history` | as listed | `Effects.recorded(key)` | `journal-last-transition-helper` |
| 7 | Eligibility filter: `Scheduler.dispatch_next` (`scheduler.py:50-76`) and `_Drain._select` (`drain.py:508-558`) both compute `settled_dependencies`, `supersedes_maps`, `authored_at`, `parked_blob`, `reofferable`, then `order_tickets` + `write_queue`; drain adds `depends_cycle`, over-budget, storm, drought | as listed | one `eligible(events, tickets, ...)` in `drain.py`, consumed by `Scheduler` | `serve-parallel-dispatch` (it rewrites `dispatch_next` anyway) |
| 8 | Provider-exception to `StageResult` mapping copied: `runner.drive:188-194` vs `run_stages` (`stages.py:1602-1615`). The copy hard-codes `surface="requisition_review"` at `stages.py:1609` for Implement, Check, and Review failures, so the Box `failure_report.stage` and the auth-notification identity name the wrong surface | as listed | one mapper in `runner.py` | `stage-failure-surface-label` (P0) |
| 9 | `running` transition + reoffer written by three callers: `runner.run_ticket:525-526`, `drain._run_one:571-574`, `serve.py:150-154` | as listed | `runner.run_ticket` | `serve-parallel-dispatch` |
| 10 | Constructors repeated: `EngineLog(...)` built 8 times (`runner.py:123,503`; `drain.py:232,357,606`; `serve.py:117`; `driver.py:190`; `triage.py:369`), `storm_producer(...)` 15 times with identical args, `Driver.from_config(...); driver.journal = ...; driver.effects = Effects(...)` 5 times (`__main__.py:619-621`, `triage.py:85-87,110-112`, `runner.py:139-141,487-489`). `Driver.from_config` builds a `Journal` and `Effects` every caller overwrites; `Effects.__init__` scans the whole journal, so each bind pays a wasted read | as listed | `Checkout`/`StageContext` carry `log` and `box`; `Driver.from_config` takes `journal` | `main-verb-groups` |
| 11 | `gather_safety_evidence` runs twice per admission: `merge.py:307` then inside `gather_evidence` (`stages.py:911`); same at `mergequeue.py:312` + 330 | as listed | `gather_evidence` reuses the safety result | `merge-admission-single-owner` |
| 12 | "Refused" constructors: `merge._refused`, the `refused` closure in `_admit`, `stages._short`, and inline `StageResult(outcome="gate_failed", ...)` at `runner.py:219`, `stages.py:1454,1457,1465,1577`, `daemon.py:360,404,415-422` | as listed | `artifacts.refused(findings, cost)` | `merge-admission-single-owner` |
| 13 | Fence matching: owner `stages._in_fence` (978-979); re-implemented at `watchdog.py:60`, `drain.py:484` (different semantics: trailing-slash dirs only), raw `startswith(f"{TICKETS_DIR}/")` at `merge.py:108,248,385`, `stages.py:1224` | as listed | `_in_fence`, moved to `chupa/tickets.py` (the fence grammar's home) | `fence-overlap` (it adds the pure overlap function beside it) |
| 14 | `retro_check` phase logging with two outcome vocabularies: `drain.py:605-613` ("ran"/"no_report") vs `serve.py:339-353` ("due"/"not_due") | as listed | one vocabulary in `retro.py` | `docs-truth-sweep` |

### 2.2 Closed sets with more than one home

| Set | Homes | Owner |
|---|---|---|
| Tiers `low|medium|high|max` | `config.py:21`, `llm.py:10-11`, `tickets.py:33`, `caps.py:13`, `policy.py:15`, `__main__.py:378` | `llm.py` |
| Priorities `P0..P3` | `tickets.py:58`, `__main__.py:273`, `dev.py:87` (`observe.py:716` already derives from `Frontmatter`) | `tickets.py` |
| Kinds `feature|bug|chore` | `tickets.py:59`, `tickets.py:810`, `__main__.py:269,791`, `dev.py:83`, `author.py:245` (different order), `hostfiles.py` CORE_TEMPLATE | `tickets.py`; the template names the verb, not the list |
| Settled and retired states | `status.py:17` `SETTLED`, `drain.py:53` `RETIRED`, `stats.py:11` `SETTLED` (same name, different set), `tickets.py:711` literal; `SETTLED | {"rejected"}` spelled out 15 times, `SETTLED | RETIRED` 8 times | `status.CLOSED = SETTLED | RETIRED`; `stats.SETTLED` deleted |
| Failed-attempt terminals | `caps.py:48`, `scorecard.py:85`, `journal.py:101`, `stats.py:122` | `journal.py` |
| Surfaces | `specs/__init__.py:32` (8), `observe.py:33-44` (10), `stats.py:12` (6), `observe.py:274,814`, `providers.py:29`, `policy.py:14` | `specs/__init__.py`; observe and stats derive |
| Spike kinds | `config.py:23` owner; `chupa/docs/host-contract.md` repeats the list at lines 133, 193, 202, 206 | `config.py`; the contract lists it once |
| Box classes and policy rows | `box.py:18`, `config.py:25-49`, `policy.py:33-45`, `host-contract.md:134,213`, `specs/triage.md:20-28` | `box.py` (classes), `config.py` (rows), `policy.py` the only bridge |
| Triage verdicts | `triage.py:33`, `box.py:63,69,403` (three overlapping Literals in one file) | `box.py` |
| Control verbs | `control.py:16,72`, `__main__.py:254-257`, `lockfile.py:19`, `observe.py:835-842` | `control.py` |
| Ask kinds | `ask.py:11` owner; `__main__.py:398-421` branches per literal; `observe.py:527-529` hand-lists three menu entries | `ask.py` |
| Finding codes | `ticket_schema` at `tickets.py:30`, `author.py:39`, `rework.py:66`; `requisition_review`/`requisition_rma` at nine sites; `core_drift` at `hostfiles.py:192,205,214` | `gates.ENGINE_GATE_CODES` plus one registry for stage finding codes |
| Conduct-file routing `{claude, qwen}` -> `CLAUDE.md` | `providers.py:131`, `host-contract.md:274`, `how-chupa-works.md:756` | `providers.py`; docs cite it |

Ticket: `closed-sets-single-home`.

### 2.3 Repeated helpers and projections

- `NonBlank` redefined in `author.py:28`, `triage.py:27`, `box.py:55`, `inbox.py:15` while `artifacts.py:25` exists. `_Strict` bases in `config.py:61`, `box.py:58`, `inbox.py:29`, `artifacts.py:47`, `stages.py:79`.
- Repo-relative path validators: `tickets.py:210`, `box.py:22`, `inbox.py:22`, `config.py:118`, `covgate.py:54`.
- Spec-major extraction `int(version.split(".")[0])`: `requisition.py:141,161`, `rework.py:212`, `policy.py:28`, `baseline.py:45`; `stages.py:391` is already a helper nobody calls.
- Hand-rolled git blob SHA: `requisition.py:136`, `hostfiles.py:203`, `stages.py:281`.
- Retro-recurrence reopen boundary: `author.py:159-161,179-181`, `triage.py:263-270`.
- `requisition_verdict` signal body built by hand: `__main__.py:643-655`, `author.py:360-364`, `rework.py:169-180`, `runner.py:199`. `ticket_intake` body: `tickets.py:768` uses `INTAKE_SIGNAL`, `author.py:359` a literal.
- Scorecard table builder byte-identical in `status.py:246-255` and `retro.py:255-265`.
- Literal `"box"` instead of `BOX_DIR` at `__main__.py:80,460`, `author.py:74`, `ask.py:24`, `observe.py:757`; `f"tickets/{stem}/ticket.md"` instead of `ticket_path()` at `__main__.py:141`, `triage.py:201`, `observe.py:240,678,687`.
- Last-state fold: `status.py:58-60` canonical; re-implemented at `observe.py:395-398,604-607,552`, `__main__.py:128,160-162,431`, `providers.py:244`. `observe.journal()` returns dicts, so `observe` wraps them in `SimpleNamespace` four times to call Event-typed helpers.
- Attempt counting with three semantics: `caps.py:54-56`, `observe.py:403`, `stats.py:112`. Spend sum at `status.py:194`, `stats.py:130-131`, `retro.py:151,160`.
- Frontmatter read by regex outside the owner: `observe.py:218-224,278-281`, `retro.py:228` (duplicates `tickets.py:82` `_BUDGET`), `__main__.py:789-792`.
- `"cap spent"` produced by `caps.py:108` and parsed back by `observe.py:315`. `provider_drought` body probed at 14 sites.
- `__main__.py`: lock acquire/try/release written four times (514-520, 527-539, 672-715, 839-861); `_require_engine` + `read_active` + `ValueError -> Refusal` three times; `observe.Context(...)` twice; `lambda: load_config(...)` six times; four ad-hoc `print(..., file=sys.stderr); return 2` beside the shared handler at 580-586; `checkout` built for every verb past line 435.

Tickets: `main-verb-groups` (the `__main__.py` items and constructors), `closed-sets-single-home` (helpers that guard a closed set), `journal-last-transition-helper` (projection folds).

### 2.4 Provider stream parsing

`ClaudeAdapter.parse` (`providers.py:465-479`) and `CodexAdapter.parse` (493-511) read the terminal event and usage; `watchdog.CallMeter._consume` (85-126) re-parses the same fields with its own guards; `observe.live_call` (189-215) re-encodes the adapters' argv by regex over `ps` output. `docs/evidence-trail-plan.md` makes the per-provider normalizer the single parser and lists moving `CallMeter` and `Parsed` onto it as a follow-up once normalizers have run on real traffic.

### 2.5 Rules stated in more than one home

Second problems to the Box and verify at base (`hostfiles.py:55`, `CLAUDE.md:90-91`, `AGENTS.md:84-85`, `specs/implement.md:24-26,133-134`); read before write (`hostfiles.py:56`, `CLAUDE.md:92-93`, `AGENTS.md:86-87`); smallest change (`hostfiles.py:52`, `CLAUDE.md:72-73`, `AGENTS.md:68-69`, `implement.md:23-24`); never push (`hostfiles.py:44,54`, `CLAUDE.md:88-89`, `implement.md:56-58`); never hand-edit the managed block (`hostfiles.py:53`, `CLAUDE.md:82-83`, `host-contract.md:272`); the set-membership grep rule verbatim in `host-authoring.md:55` and `specs/requisition_review.md:24`; the bug-evidence refusal sentence three times (`host-authoring.md:88-92`, `how-chupa-works.md:148-151,315-318`); unit-test discipline in `implement.md:60-68`, `review.md:37-39`, `retro.md:24`, `how-chupa-works.md:225-229`.

The `CLAUDE.md` rule "a rule has one of two homes" is the fix; `docs-truth-sweep` removes the restatements in `docs/` and `chupa/docs/`, and `conduct-files-parity` settles the three rule files. Specs may restate a rule the model needs; documents may not.

### 2.6 Tests

- No `conftest.py` anywhere. 37 test modules double as fixture libraries (257 top-level cross-test imports); `tests/integration/serve_rig.py:21-24` imports from four test modules; `test_drain.py:30-33` imports and calls a test function from `test_merge.py` as its body; `test_merge.py:43` reads `test_stages.py` as text and slices its `CONFIG` literal out.
- Fakes: 9 clock fakes, 18 exec fakes, 11 filesystem fakes, 10 journal fakes, 8 git fakes defined across tests; `chupa/seams.py` ships none (only `FakeLLM` in `chupa/llm.py:58`).
- `until`/wait has three implementations with three semantics (`serve_rig.py:27`, `test_drain_admissions.py:15`, `tests/waiting.py:10`); `repo()` fixtures six times building the same shape; `git()` four times with four meanings; `reply()` seven times.
- `CONFIG` literal at 12 sites (three byte-identical groups), `TICKET` at 7, `config.yaml` written in 63 files, git-init sequences in 22.
- The five do-not-grow files named in `docs/parallel-tickets-plan.md` §7 took 53 commits in the 13 days to 2026-11-13; the list is in no rule file yet.

Tickets: `test-fakes-and-conftest`, `contention-authoring-rules`.

## 3. Analysis: gaps

### 3.1 Defects found by the audit

| Defect | Location | Ticket |
|---|---|---|
| Provider failures in Implement, Check, and Review are labelled `surface="requisition_review"` in the Box `failure_report` and the auth notification | `stages.py:1609` | `stage-failure-surface-label` (P0) |
| Raw provider captures overwritten across processes: `_seq` restarts at 0 per process, so `providers/<stem>/<provider>-0001` is rewritten by the next run of the same stem. 3,944 journaled calls, 2,453 capture directories | `providers.py:294,324-325` | `provider-capture-overwrite` (P0); cause fix `evidence-envelope` |
| `served_review` swallows `ValueError, KeyError, TypeError, AttributeError, GitError` to `(None, None)`, nulling the receipt's provider and model on any defect | `stages.py:227-228` | `docs-truth-sweep` names it; fix in `merge-admission-single-owner` |
| Coverage parse `except: pass`, so coverage is silently absent although §5.4 says it is recorded; base `results` read then discarded | `stages.py:1104-1105,1191-1194` | `host-check-selection-single-owner` |
| `diagnosis.json` is not written when the worktree is gone, although §6.3 promises it | `runner.py:275-277` | `docs-truth-sweep` (document the truth) |
| Drain report paved roads print `uv run python -m chupa drain|confirm|reject`, the one operator surface that names argv instead of a verb; `Admission("refuse", "unknown box id")` carries `paved_road=""`; `retro.py:458` collapses the stage outcome into `ValueError`; seven `BoxError`s name the fault without a repair | `drain.py:182,186,710,721`; `status.py:149`; `retro.py:458`; `box.py:179-434` | `paved-roads-name-verbs` |
| `watch` shows spec-frontmatter tier and effort for review, diagnose, author, triage, and requisition_review, but the code never passes spec tier for those surfaces | `observe.py:229-231`; `author.py:316`, `triage.py:311`, `stages.py:453,660,1508` | `watch-surface-tier-truth` |
| `harvest.json` is written without the redactor; `diff_stat` and finding messages are not pre-scrubbed. `redact.py:7-9` checklist says "journal writer NOT YET WIRED" and "harvest serialization: not built" | `runner.py:443-483`; `redact.py:7-9` | `redaction-harvest-seam` |
| `argparse` help for `review` says "under the lock"; the verb takes no `Lockfile` | `__main__.py:258` vs 589-660 | `docs-truth-sweep` |

### 3.2 Seams bypassed

`FileSystem` (`seams.py:207-216`) has no `mkdir` or `remove`, so callers cannot comply: `enginelog.py:29-32,39` raw `mkdir`/`open("ab")`/`Path.replace`; `journal.py:149` constructs `LocalFileSystem()` itself and `176-191` uses raw `os.open`/`os.write`; `stages.py:486,496` raw `mkdir`, `519,867,1068,1186,1446-1447` raw `unlink`; `driver.py:189` `fs or LocalFileSystem()` default in engine code; `scheduler.py:80` reaches into `journal.dir.parent`, `journal._fs`, `journal._clock` to write `queue.json`. Ticket: `fs-seam-mkdir-remove`, which also makes `write_queue` take the seams it needs.

### 3.3 Deferred items whose trigger has fired

| §18.2 item | Trigger | Fired | Decision |
|---|---|---|---|
| Mechanical scope-fence closure analyzer | first fence-gap escape `requisition_review` misses | twice: `box-000324` (three rejects), recurrence in `tickets/retro/000046.md` proposal 2 (`test_menu_verb_parity.py:185`) | 0.2.0 widens the prompt rule to in-code registries (`fence-closure-registries`). A mechanical analyzer is an owner decision (section 6); the prompt rule has now failed once, so a third escape makes it a 0.3.0 candidate |
| DuckDB analytics | first projection measured too slow as a fold | yes, 157 of 164 seconds (`tickets/journal-incremental-read/evidence/`), before the incremental reader merged | re-measure; 0.3.0 is conditional on it |
| Triage-dedup real-model eval | daemon-era entry | yes, serve has run since the daemon era | not scheduled; `training-eval` (0.5.0) covers triage records and makes this the first lens to score |
| Concurrent worker pool, dispatch overlap skip | measured starvation post-cutover | not fired; owner chose to bring it back for contention, not starvation | 0.4.0, declared in `docs/parallel-tickets-plan.md` |
| Conflict-only micro-rework | first chronically re-resolved conflict in `merge_conflict_facts` | 13 events exist; nobody has read them | `merge-model-resolve` starts by reading them (its plan's A0) |

### 3.4 Never built, no ticket

- P8 `rules-render`: `chupa core --check` and a start-command file. `doctor` has a `core` drift row (`doctor.py:67-73`); `serve`, `drain`, `run` refuse on stale blocks. Owner decision whether `--check` is still wanted (section 6).
- `chupa/docs/host-contract.md` "Onboarding a host" and "Operating facts" sections (P8). Its two sections still titled "Pending report-inbox contract" and "Pending cutover contract" describe shipped code. `docs-truth-sweep` retitles them; the onboarding checklist is `training-docs`' sibling, `host-onboarding-doc`, scheduled in 0.2.0.
- `review.surfaces`: refused at config load "until a host that uses them onboards". Stays refused. `docs/document-agent-plan.md` Open decision 2 is the first proposal that would need host-defined prompts and it routes them as data instead.
- `kind: api` provider: refused at `config.py:460-465`; stays deferred.

### 3.5 Dev surface and tests

- Five verbs have no `./dev.py` subcommand: `covgate`, `doctor`, `migrate-config`, `retro`, `snapshot` (`pause`, `resume` also absent). `CLAUDE.md` §B says a missing command becomes a subcommand; `chupa/docs/host-running.md:6` tells operators to run `doctor` and this repo cannot. `retro` is reachable only from the extension's Engine picker.
- `./dev.py test` runs `uv run pytest -q` with `addopts = "-n auto"`; it never loads `chupa.testguard`, so the unit IO guard and the 60-second budget apply only inside Check. `how-chupa-works.md:79` says otherwise.
- `tests/regress_*.py` (45 files) run only as bug tickets' `## Regression` argv; 10 have no `__main__` guard and execute at import. `tests/vscode_task_identity.js` is referenced by one of them and no test.
- `test-gate.toml` lists 57 of 59 modules; `chupa/graph.py` has no floor; eight modules sit at floor 0 (`audit`, `covmap`, `doctor`, `observe` at 856 lines, `seams`, `stats`, `thresh`, `watchdog`).
- Lint and the authoring guide disagree in both directions. Guide rules not linted: spec version "next minor above main" with a fenced pin (`host-authoring.md:57-58`), fence the document a behavior change affects (55-57), criterion names the wrong result it rules out (63-65). Linted rules the guide does not state: banned adjectives (`tickets.py:78`), no `chupa/specs/*.md` in `## Context` (377-378), `stuck` exceeds `expected` (462-463), `## On-demand` under the fence (422-423), `## Depends on` accepts `none` (342), reserved stems (28), `## Regression` refused on a non-bug (447), the stuck ceiling (`__main__.py:718`).
- Extension: `order` argv is assembled in JavaScript (`vscode-chupa/extension.js:52,56,58`) while `confirm`/`reject`/`drain` argv come from the snapshot; `review`, `lint`, `run`, `triage`, `dismiss`, `serve`, `stop`, `prompt <kind>` are JavaScript literals (334-371); `chupaRoot()` (9-13) picks the workspace folder by probing the filesystem. `CLAUDE.md` says argv and policy come from the snapshot.
- Config declared and read nowhere: `caps.poison` (`config.py:182`), `review.trigger_map` (151; pinned by four test files), `ReviewSurface` and `rules_doc` (129-133, unreachable). Spec frontmatter `consumes`, `emits`, `gates` (`specs/__init__.py:76-80`) is validated and read by no stage; `tier:` is honored only by retro (`retro.py:451`). `requisition_review.md:54-58` `context` always receives the literal `"included in render"` (`requisition.py:218`).
- No engine caller: `heartbeat.is_fresh`, `Timers.wait_next`, `Git.branch`, `Git.init`, the `effects.effect` decorator, `gates.lint_gate`, `providers.CliAdapter.parsed_failure`, `requisition.RequisitionGate`, `requisition.base_render_chars`, `observe.uncommitted_tickets` (20+ tests monkeypatch it), `policy.baseline_identity`, `audit.audit`, `watchdog.Detector.watch`. Untested production paths: `mergequeue.retained_ticket`, `stages.served_review`, `serve.Responsiveness`, `runner.PreparedDispatch`, `stages.ticket_blob`.

Tickets: `dev-surface-completeness`, `regress-scripts-guarded`, `test-gate-floors`, `lint-guide-parity`, `extension-argv-from-snapshot`, `dead-config-and-spec-fields`.

## 4. Analysis: drift

Every row is a claim the owning document makes that the code contradicts. `docs-truth-sweep` fixes each by changing the document to the code's behavior, except where the row names a code ticket.

### 4.1 `docs/how-chupa-works.md`

| Line | Claim | Code | Truth |
|---|---|---|---|
| 79 | unit tests "run under `chupa.testguard`" via `./dev.py test` | `dev.py:62`, `pyproject.toml:30`, no conftest | only the Check-gate argv loads the plugin (`config.yaml:36`); code fix in `dev-surface-completeness` |
| 131 | `draft` "awaits `confirm`" | `tickets.py:692-695` | intake stamps every new hand-written ticket `confirmed`; only Author drafts wait |
| 177-178 | lift "refuses symlinks" | `stages.py:332-342` | symlinks are skipped silently; only over-size raises |
| 244 | Check "runs configured autofix commands" | `stages.py:1407` | only when Implement replied `ok` and `review.autofix` is nonempty |
| 373 | lift kind `harvest` | `runner.py:371` | also `harvest-rework` |
| 388-389 | worktree gone: `diagnosis.json` is lifted | `runner.py:275-277` | nothing is written or lifted; only the journal signal |
| 452-453, 485-488 | paved roads say `./dev.py confirm|reject` | `drain.py:182,186,710,721` | drain prints `uv run python -m chupa ...`; code fix in `paved-roads-name-verbs` |
| 463-464 | Reconcile reaps any stem still `running` | `reconcile.py:22,38` | stems with a HELD regate receipt at the current attempt and intents under `llm/review-<stem>/` are excluded |
| 475-477 | drain loop steps omit Box intake | `drain.py:396` | drain calls `triage.report_intake` every iteration |
| 528-530 | queue skip rule | `mergequeue.py:313` | also requires no HELD receipt |
| 581 | preflight at run/drain/serve/triage | `__main__.py:618,696-697` | also `review` and `retro` with a report |
| 592-593 | "a call waiting over 60s spills" | `thresh.py:167,177` | spill is decided up front from the projected wait |
| 679-680 | prune candidate: 25+ evaluations and no catch | `scorecard.py:94` | also requires zero escapes |
| 694 | one `retro_check` phase | `serve.py:353`, `drain.py:613` | two outcome vocabularies |
| 708 | `signal` is "a closed list" | `journal.py:94` | no registry; writers use `signal` or `kind` as the body key |
| 72 | `reject <stem> [--yes]` | `__main__.py:277-281` | also `--extension` |
| 10.1 table | state_dir files | `__main__.py:342,370`, `covmap.py:32`, `rework.py:122`, `box.py:268` | omits `drain.out`, `coverage-map.json`, `rework/<stem>/<attempt>/<call>/`, `spools/probe/`, `box.seq/`, `worktrees/.base/`, `.regression-base/`; rotation bounds 16 MiB x 3 and 64 MiB / 24 h unstated |
| 10.2 | event types | `journal.py:32` | `checkpoint` type exists, never emitted; about 30 signal kinds unlisted |
| 3.3:188 | engine commits on main | `retro.py:298`, `stages.py:1393` | omits `chupa(decisions): <id>`, `chupa: retro NNNNNN`, `undo refused rework`, branch `autofix` |
| 11 | config areas | `config.py:83-91,226,75` | `providers[].package` (required for every CLI) unmentioned; `routing_default_tier` and `quota_window_minutes` defaults unstated |
| 54 | `probe` row | `__main__.py:391` | exits 1 when any probe fails |
| 61 | `drain [--detach]` | `__main__.py:284-285` | also `--parked STEM`, `--deadline ISO` (set by the self-upgrade re-exec) |

### 4.2 Other documents

| Document | Claim | Truth |
|---|---|---|
| `README.md:31` | runs that exhaust attempt caps file to the Suggestion Box | they route to the Reject queue (`runner.py:390-393`, `drain.py:687`); `how-chupa-works.md:416,432` are right |
| `chupa/docs/host-running.md:19` | serve "accepts [retro] but does not yet run it" | `serve.py:339-355` runs it |
| `chupa/docs/host-contract.md:6-7,383,422,442` | "Pending report-inbox contract", "Pending cutover contract", "adds no report consumer" | `triage.py:358-372`, `inbox.py:120` ship the consumer |
| `host-contract.md:45,330` | `trigger_map` is "engine gate codes only" | `config.py:151` validates nothing; it is read by nothing |
| `host-contract.md:299` | "Put ordering in Depends on and priority" | `## Runs before` exists for ordering; `Depends on` is merged-code only (`hostfiles.py:22`, `host-authoring.md:33-38`) |
| `host-authoring.md:15-21` | lint's checks | omits the `drain.max_ticket_minutes` stuck ceiling (`__main__.py:718-721,759`) |
| CORE_TEMPLATE (`hostfiles.py:20`) | `chupa docs` prints "(authoring, running, config contract)" | four guides including qwen (`__main__.py:312`); dropping the parenthetical frees 36 of the template's 352 spare bytes |
| `CLAUDE.md` vs `AGENTS.md` | "a rule add/change/remove touches both files" | `AGENTS.md` lacks "Lean ticket frontmatter" (`CLAUDE.md:94-95`), "The plan is the seed" (86-87), "Phase order" (107-108), and the "compress it to one line" sentence (57) |
| `chupa/docs/host-authoring.md:12,16,25`, `host-qwen.md:66`, `chupa/specs/ask/*.md` | name `./dev.py` | engine-owned files carry this repo's dev surface, which no host has (`box-000440`) |
| `chupa/mergequeue.py:1`, `chupa/heartbeat.py:1` | "Dormant" | serve routes every merge through the queue (`serve.py:129`); serve refreshes the heartbeat every loop (`serve.py:203-209`) |
| `chupa/redact.py:7-9` | "journal writer NOT YET WIRED", "harvest serialization: not built" | harvest exists (`runner.py:443-483`); the checklist is stale and harvest is unscrubbed |
| `vscode-chupa` settings | `how-chupa-works.md:116-119` names `chupa.playAction`, `chupa.statsWindow` | `chupa.command` (`package.json:73-83`) is named only in `README.md:77` |

### 4.3 Plan documents (fixed in this revision)

| Plan | Was | Now |
|---|---|---|
| training-data | `docs/host-contract.md` | `chupa/docs/host-contract.md` |
| training-data | 2,301 capture directories | 2,453 (directories holding `events.jsonl` at `0895b5d4`) |
| training-data, evidence-trail | two stores (`training/`, `evidence/`), two layouts, two retention stories, `spools/providers/` both kept and replaced | one store, section 5 decision 1 |
| parallel-tickets | `tests/test_stages.py` | `tests/integration/test_stages.py` (tickets fenced the old path) |
| gemini-graphics | `__main__.py:771`; "the watchdog's unit test file" | the kind check in `_new` (line 791 at `80b76d5d`); `tests/integration/test_watchdog.py`, `test_watchdog_activation.py` |
| journal-sql | measurement presented as current | `journal-incremental-read` merged at `f790cf71`; trigger must be re-measured |
| upstream-issue | status cites `ed48cbc9` (the Gemini plan's commit) | written 2026-11-13; revised at `80b76d5d` |
| document-agent | `docs:` config block, `specs/doc/review.md`, `writes` "flag" | `documents:`, `specs/doc/lens.md`, `writes` is derived from `WRITING_SURFACES` |
| all seven | different status forms, ticket-table columns, "Deferred" vs "Open" decisions, no priorities in three | one shape, section 7 |

## 5. Cross-plan decisions

Each decision settles a place where two plans overlapped or contradicted. The plans are revised to match; a plan that wants to change one of these changes it here first.

1. **One call-record store.** `<state_dir>/evidence/` (`docs/evidence-trail-plan.md`) is the only store for model-call records. The training plan adds attempt manifests, export, and eval on top of it and owns no store of its own. `spools/providers/` is replaced by the evidence store in `evidence-envelope`; the per-attempt `spools/<stem>/<attempt>/` (prompt, output, check output) stays until a later ticket moves it, which no plan schedules.
2. **Capture always on, training gated.** The envelope and raw stdout/stderr are captured for every call, as `spools/providers/` is today, because diagnosis and harvest read them. Retention is `evidence.max_gb` (default 20; evidence plan). Attempt manifests with full diffs, export, and eval are behind `training_data.enabled` (default false; training plan). `training_data.dir` is dropped: the store location is fixed.
3. **Record identity.** A record's id is the journal effect key. Ticketless calls key under their surface name (`driver.py:274`), so `stem` is nullable and `group` is the stem or, for triage, author, retro, and document lenses, the surface. Isolated calls (document agent) record `repo: null` and `process.cwd` as the scratch directory; no conduct file is loaded and the record says so.
4. **One P0 for the capture bug.** `provider-capture-overwrite` is a single bug ticket owned by this roadmap. Its cause fix, under the CORE two-ticket rule, is `evidence-envelope` (every capture path keyed by the journal identity of what it captures). Both plans cite the stems; neither owns them.
5. **CORE_TEMPLATE byte ledger.** 7,840 of 8,192 bytes used (`tests/integration/test_hostfiles.py:33`). Spend: `conduct-files-parity` frees 36; `upstream-issue-verb` adds about 264; `graphics-kind` adds 9. Order in 0.2.0 and 0.4.0 keeps them from colliding; after both, about 115 bytes remain. Any further template text first compresses a rule that has gained its gate (`CLAUDE.md:57`).
6. **Names.** The document agent's config block is `documents:` (not `docs:`, which is a verb and a directory). Its lens spec is `chupa/specs/doc/lens.md` (not `review.md`, which exists at `chupa/specs/`). Its specs carry the spec frontmatter that `tests/unit/test_specs.py:24` checks on everything under `chupa/specs/`.
7. **Journal window.** 0.3.0 runs only on re-measurement. Its port tickets touch the same files as `serve-parallel-dispatch` and `conflict-discard-rerun`, so the parallel tickets land after the window, or before it if the window slides. Several runs in one process appending to the journal is compatible with the query layer's per-process offset because `journal.lock` serializes appends; the journal plan states this.
8. **Shared files between plans.** `graphics-render-check` and `conflict-discard-rerun` both bump `chupa/specs/implement.md`; `graphics-render-check` runs first (it heads the longer chain). `upstream-issue-verb` (0.2.0) and `graphics-kind` (0.4.0) both edit `hostfiles.py`, `CLAUDE.md`, `AGENTS.md`, `README.md`; releases separate them. `gemini-provider`, `evidence-envelope`, `isolated-readonly-call`, and the journal ports all fence `chupa/providers.py`; under the parallel plan's own overlap rule they serialize, which the release slots already arrange.
9. **Design-record departures are declared.** A plan that re-opens a `CHUPA_PLAN.md` §18 item names the item, the trigger, and the owner decision in a "Departures from the design record" table. The parallel plan already did; the training, evidence, and document plans now do (audit trail and blob store, §18.1; metadata taxonomies, §18.1). The owner's decision of 2026-11-13 is the cited incident.
10. **Host-command lock.** The parallel plan's engine-wide semaphore around `run_host_command` also serializes the graphics plan's render command and the merge queue's host checks. One lock, stated in both plans.
11. **The mergequeue docstring** is fixed by `docs-truth-sweep`, not by a parallel-plan ticket; that plan's row 2 now points at the roadmap's `active-slot-single-owner` and `merge-admission-single-owner`, the two 0.2.0 chores its dispatch and merge tickets depend on.

## 6. Owner decisions pending

Not scheduled until the owner decides. Each names its default if nothing is said.

1. **Mechanical fence-closure analyzer** (§18.2; trigger fired twice). Default: prompt rule only (`fence-closure-registries`); a third escape schedules a spike in 0.3.0.
2. **P8 `core --check` and start-command file.** Default: not built; `doctor`'s `core` row and the start refusal cover the need.
3. **Settled-ticket archive.** 537 directories under `tickets/`. Default: nothing until a measured cost (lint time, intake scan) is filed.
4. **Split the five large test files.** Default: do-not-grow rule only (0.2.0); splitting is chore tickets during the 0.3.0 window if it runs, else 0.4.0.
5. **Parallel plan**: `serve` only or `drain` too (default `serve`); chain ordering below P0 only (default yes); conflict reruns outside `retry` (default yes).
6. **Training plan**: store the full tool-call stream (default yes); include Author-written tickets tagged by author (default yes).
7. **Evidence plan**: copy providers' own session logs (default no); store Claude thinking text (default yes).
8. **Document plan**: `diverse` panels by default (default off); host-defined lenses as data (default yes); verbs only, no `doc` ticket kind (default yes).
9. **Journal plan**: DuckDB vs Polars (default DuckDB); whether the SQL-only rule becomes a gate (default yes, landing with the last port).
10. **Upstream issue plan**: the four critical classes (default as proposed).

## 7. Plan document shape

Every plan under `docs/` has these sections in this order, so the next audit can read them mechanically: title; one-paragraph summary; `## Status` (one line: "Draft plan. Nothing in it is in effect and no ticket is authored. Written <date> at commit `<sha>`; revised <date> at commit `<sha>`."); `## Roadmap` (release slot, what it needs from other plans, what needs it, shared budgets it spends); `## Current state`; `## Departures from the design record` (when any); `## Target design`; `## Where each piece lives`; `## Ticket breakdown` with columns `# | Stem | Kind | P | Depends on | Content` and a `Runs before` sentence under the table; `## Risks`; `## Open decisions`. Stems are unique across all plans and this document, and none reuses a stem the journal already holds (`journal-sql-refactor-plan` is taken, rejected).

## 8. Master ticket table

Every proposed ticket, in release and priority order. "Owner" is the plan whose design the ticket implements; "roadmap" means the ticket comes from the audit above. `Depends on` lists only tickets whose merged code is needed; ordering that is not a dependency is in the `Runs before` column. No row is authored yet; authoring follows `chupa new` and the authoring guide, and the row gains a link when it is.

### 0.2.0

| # | Stem | Owner | Kind | P | Depends on | Runs before | Content |
|---|---|---|---|---|---|---|---|
| 1 | `provider-capture-overwrite` | roadmap (decision 4) | bug | P0 | | `evidence-store` | Name capture directories by the journal call key so a later process cannot overwrite an earlier capture (`providers.py:294,325`). Evidence: 3,944 calls, 2,453 directories. |
| 2 | `stage-failure-surface-label` | roadmap | bug | P0 | | | One provider-exception mapper in `runner.py`; delete the copy at `stages.py:1602-1615` whose `surface="requisition_review"` mislabels Implement, Check, and Review failures. |
| 3 | `release-verb` | journal plan (a) | feature | P1 | | | `./dev.py release --minor|--patch`: bumps `pyproject.toml`, commits, tags `v<version>`; `publish` keeps bumping only the patch. Needed to tag 0.2.0. |
| 4 | `docs-truth-sweep` | roadmap | chore | P1 | | | Every row in section 4.1 and 4.2 that is a document fix; the `mergequeue.py` and `heartbeat.py` docstrings; the `redact.py` checklist; the `review` argparse help; `how-chupa-works.md` 10.1 and 10.2 gain the missing paths, the `checkpoint` type, and the signal-kind list. |
| 5 | `conduct-files-parity` | roadmap | chore | P1 | | `upstream-issue-verb` | `AGENTS.md` gains the four rules it lacks; CORE_TEMPLATE drops "(authoring, running, config contract)"; `chupa core` refreshes both blocks. |
| 6 | `paved-roads-name-verbs` | roadmap | chore | P1 | | | Drain report roads name `./dev.py` verbs in this repo and `chupa` verbs on a host (`drain.py:182,186,710,721`); `status.py:149` carries a road; `retro.py:458` keeps the stage outcome; the seven `BoxError`s name a repair. |
| 7 | `dev-surface-completeness` | roadmap | chore | P1 | | | `./dev.py` gains `doctor`, `retro`, `snapshot`, `pause`, `resume`, `migrate-config`, `covgate`; `./dev.py test` loads `chupa.testguard` and `test-gate.toml`'s budget for `tests/unit`. |
| 8 | `host-prompts-no-dev-py` | roadmap (`box-000440`) | chore | P1 | | | `chupa/specs/ask/*.md`, `host-authoring.md`, `host-qwen.md` render the host's verb prefix; `./dev.py` appears only in `README.md` and `how-chupa-works.md` §2.2. |
| 9 | `unit-criteria-disk-snag` | roadmap (`box-000441`, `box-000442`) | feature | P1 | | | `requisition_review.md` snags a `tests/unit` criterion that needs disk, process, or network, with a road naming an in-fence seam; `diagnose.md` keeps floored lines reachable from `tests/unit`. |
| 10 | `fence-closure-registries` | roadmap (`box-000324`) | feature | P1 | | | `requisition_review.md:24` traces in-code registries and tables (menu keys, closed sets, adapter maps), not only symbol closure. |
| 11 | `watch-surface-tier-truth` | roadmap | bug | P1 | | | `watch` shows the tier the code will use per surface (`observe.py:229-231`), or the code honors spec `tier:` for every surface; one truth. |
| 12 | `redaction-harvest-seam` | roadmap | chore | P1 | | | `harvest.json` passes the redactor; `redact.py` checklist matches the writers. |
| 13 | `contention-authoring-rules` | parallel plan 1 | chore | P1 | | every feature ticket below | Section 7 of the parallel plan: new tests in new files, new fixtures in new modules, fence only what is forced, the do-not-grow list in `CLAUDE.md` and `AGENTS.md`. |
| 14 | `fs-seam-mkdir-remove` | roadmap | chore | P2 | | `evidence-store` | `FileSystem` gains `mkdir` and `remove`; `enginelog`, `journal`, `stages`, `driver`, `scheduler.write_queue` use the seam. |
| 15 | `active-slot-single-owner` | roadmap | chore | P2 | | `serve-parallel-dispatch` | `DaemonAdmission` owns the running set; `Scheduler._slot`, `TicketWriter.active`, `restart.mutating` read it; `serve.upgrade_idle` reads one thing. |
| 16 | `merge-admission-single-owner` | roadmap | chore | P2 | | `merge-model-resolve` | `merge.merge` becomes a thin call into `MergeQueue._admit` with the ladder, safety tier, receipt, tree check, and red streak as parameters; `gather_safety_evidence` runs once; one `refused` constructor; `served_review` stops swallowing. |
| 17 | `host-check-selection-single-owner` | roadmap | chore | P2 | | | `triggered_hosts(tier=...)` is the one filter; `run_host_command` the one runner; the coverage parse and base `results` read stop swallowing. |
| 18 | `journal-last-transition-helper` | roadmap | chore | P2 | | | `journal.last_transition(events, stem)` replaces 13 scans; `Effects.recorded(key)` replaces six hand scans; `status.last_states` is the one fold observe and `__main__` use. |
| 19 | `closed-sets-single-home` | roadmap | chore | P2 | | `graphics-kind` | Section 2.2 table: each set has one owner; argparse and `dev.py` derive choices; `NonBlank`, `_Strict`, path validators, spec-major, blob SHA become single helpers. |
| 20 | `main-verb-groups` | roadmap | chore | P2 | | | `__main__.py` verb handlers grouped (utilities, projections, authoring, control, lock holders); one lock wrapper, one `_require_engine`, one `Context`, one error printer; `Checkout`/`StageContext` carry `log` and `box`; `Driver.from_config` takes the journal. |
| 21 | `test-fakes-and-conftest` | roadmap | chore | P2 | | | `tests/conftest.py` and `tests/fakes.py` with one clock, exec, filesystem, journal, and git fake and one `until`; `serve_rig.py` and the ten largest providers migrate; `test_merge.py:43` stops parsing another test's source. |
| 22 | `test-gate-floors` | roadmap | chore | P2 | | | `chupa/graph.py` gains a floor; the eight floor-0 modules take their measured coverage as a ratchet. |
| 23 | `lint-guide-parity` | roadmap | chore | P2 | | | Every rule `tickets.py` lints is in `host-authoring.md`; the three guide rules lint can check (spec pin fenced on a version bump, document fenced on a behavior change, `## Depends on` ticket exists) are linted. |
| 24 | `extension-argv-from-snapshot` | roadmap | chore | P2 | | | Every verb the extension runs comes from an `observe.py` table; `chupaRoot()` uses the snapshot's root. |
| 25 | `dead-config-and-spec-fields` | roadmap | chore | P3 | | | Remove `caps.poison`, `review.trigger_map`, `ReviewSurface`; spec frontmatter `consumes`/`emits`/`gates` removed or wired; `requisition_review.md` `context` input removed; `host-contract.md` inventory follows. |
| 26 | `regress-scripts-guarded` | roadmap | chore | P3 | | | The ten `tests/regress_*.py` without a `__main__` guard get one; a test imports each script module and asserts nothing runs. |
| 27 | `host-onboarding-doc` | roadmap (P8 gap) | chore | P2 | `docs-truth-sweep` | | `chupa/docs/host-contract.md` gains "Onboarding a host" (checklist from install to first merge) and "Operating facts" (locks, state dir, upgrade, rollback). |
| 28 | `evidence-store` | evidence plan 2 | feature | P2 | `provider-capture-overwrite`, `fs-seam-mkdir-remove` | | Blob store, `chupa.evidence.*` schemas, strict writer, tolerant reader, JSON Schema generation, `evidence.max_gb` prune. |
| 29 | `evidence-envelope` | evidence plan 3 | feature | P2 | `evidence-store` | | `start.json`/`end.json` from `CliAdapter.invoke`; arrival times and rusage through the exec seam; tree ids through `git.py`; CLI version probe; `engine.log` stage events carry `call_key`; every reader of `spools/providers/` moves; the old writer is deleted. Cause fix for row 1. |
| 30 | `evidence-normalize-codex` | evidence plan 4 | feature | P2 | `evidence-store` | | Codex normalizer and golden fixture; pins whether `input_tokens` includes `cached_input_tokens`. |
| 31 | `evidence-normalize-claude` | evidence plan 5 | feature | P2 | `evidence-store` | | Claude normalizer and fixture; qwen reuses it flagged `unverified`. |
| 32 | `gemini-provider` | gemini plan A1 | feature | P2 | | | `GeminiAdapter`, two settings files, watchdog branch, live view, `host-gemini.md`; after the hand test A0. |
| 33 | `evidence-normalize-gemini` | evidence plan | feature | P3 | `evidence-store`, `gemini-provider` | | Gemini normalizer and fixture. |
| 34 | `upstream-issue-verb` | upstream plan 1 | feature | P2 | | | `chupa issue`, the CORE_TEMPLATE sentence (about 264 bytes), docs; after its hand test. |

### 0.3.0 (conditional)

| # | Stem | Owner | Kind | P | Depends on | Runs before | Content |
|---|---|---|---|---|---|---|---|
| 35 | (re-measure) | journal plan | evidence | | | | Profile a drain start and `status` at the 0.2.0 tag; the window runs only if journal reads still dominate. |
| 36 | `journal-query-layer` | journal plan (b) | feature | P2 | `release-verb` | | DuckDB connection, bulk load, incremental insert, `duckdb` dependency. |
| 37 | `journal-ports-run-path` | journal plan (c) | chore | P2 | `journal-query-layer` | | `runner`, `stages`, `merge`, `mergequeue`, `rework`, `effects`, `driver`. |
| 38 | `journal-ports-loop` | journal plan (c) | chore | P2 | `journal-query-layer` | | `drain`, `serve`, `daemon`, `scheduler`, `timers`, `watcher`, `control`, `checkpoint`, `reconcile`. |
| 39 | `journal-ports-feedback` | journal plan (c) | chore | P2 | `journal-query-layer` | | `retro`, `triage`, `box`, `storm`, `flake`, `thresh`, `audit`, `notify`, `providers`. |
| 40 | `journal-ports-cli-authoring` | journal plan (c) | chore | P2 | `journal-query-layer` | | `__main__`, `author`, `tickets`, `observe` (its raw reader goes). |
| 41 | `journal-query-rule-gate` | journal plan (d) | chore | P2 | rows 37-40 | | The rule in `CLAUDE.md`/`AGENTS.md` and the lint that refuses `journal.read()` outside `chupa/journal.py`. |

### 0.4.0

| # | Stem | Owner | Kind | P | Depends on | Runs before | Content |
|---|---|---|---|---|---|---|---|
| 42 | `parallel-config` | parallel plan 3 | feature | P2 | | | `scheduler.parallel` model, doctor warning, config table. |
| 43 | `fence-overlap` | parallel plan 4 | feature | P2 | | | `fences_overlap`, run-alone rule, `_in_fence` moved to `tickets.py`. |
| 44 | `chain-order` | parallel plan 5 | feature | P2 | | | `chain()`, parallel order, slot filling, starvation guard. |
| 45 | `serve-parallel-dispatch` | parallel plan 6 | feature | P2 | `parallel-config`, `fence-overlap`, `chain-order`, `active-slot-single-owner` | | Run set, slots, one eligibility filter, one `running` writer, host-command lock, idle checks. |
| 46 | `merge-model-resolve` | parallel plan 7 | feature | P2 | `merge-admission-single-owner` | | After reading the 13 `merge_conflict_facts` events: `specs/resolve.md`, bounds, re-review of the resolution delta, `model` step value. |
| 47 | `conflict-discard-rerun` | parallel plan 8 | feature | P2 | `merge-model-resolve` | | Delete the Rework handoff; retire and re-offer; `prior-diff` lift; `implement.md` and `rework.md` bumps; rerun cap. |
| 48 | `status-hot-paths` | parallel plan 9 | feature | P3 | | | Hot-paths table in the snapshot and extension. |
| 49 | `graphics-kind` | gemini plan B1 | feature | P2 | `closed-sets-single-home` | | `kind: graphics`, `## Render`, `--reference`, lint, authoring guide, CORE_TEMPLATE `|graphics` (9 bytes). |
| 50 | `graphics-render-check` | gemini plan B2 | feature | P2 | `graphics-kind` | `conflict-discard-rerun` | Render protocol at Check; `implement.md` block. |
| 51 | `visual-review-surface` | gemini plan B3 | feature | P2 | `graphics-render-check` | | `review_visual` spec, stage, gate. |

### 0.5.0

| # | Stem | Owner | Kind | P | Depends on | Runs before | Content |
|---|---|---|---|---|---|---|---|
| 52 | `training-config` | training plan 1 | feature | P2 | | | `training_data: {enabled, exclude}` with the fixed exclude list; export refuses when off. |
| 53 | `training-attempt-manifest` | training plan 2 | feature | P2 | `training-config`, `evidence-envelope` | | Attempt manifest and full diff before worktree removal on every terminal. |
| 54 | `training-export` | training plan 3 | feature | P2 | `training-attempt-manifest` | | Record kinds, both formats, `--holdout`, scrub with drop count, provider-terms notice, `./dev.py training-export`. The `conflict` kind lands with `merge-model-resolve` merged, else is skipped with a count. |
| 55 | `training-eval` | training plan 4 | feature | P3 | `training-export` | | Replay held-out records through a route; agreement scores. |
| 56 | `training-docs` | training plan 5 | chore | P3 | `training-export` | | Host guide: enabling, exclusions, provider terms, retrieval first. |
| 57 | `evidence-verbs` | evidence plan 6 | feature | P3 | `evidence-envelope`, rows 30-31 | | `evidence show`, `schema`, `renormalize`, `coverage`. |

### 0.6.0

| # | Stem | Owner | Kind | P | Depends on | Runs before | Content |
|---|---|---|---|---|---|---|---|
| 58 | `doc-facet-registry` | document plan 1 | feature | P2 | | | Facet format, loader, `chupa doc facets`, facet files. |
| 59 | `docset-manifest` | document plan 2 | feature | P2 | | | `chupa.docset/1.0`, section hashing, `chupa doc status`. |
| 60 | `isolated-readonly-call` | document plan 3 | feature | P2 | `evidence-envelope` | | Scratch working directory with only the declared files; evidence record with `repo: null`. |
| 61 | `doc-review-runner` | document plan 4 | feature | P2 | `doc-facet-registry`, `isolated-readonly-call` | | `doc_review` surface over `specs/doc/lens.md`, stage runner, accounting gate, report. |
| 62 | `doc-lenses-from-owner-prompts` | document plan 5 | feature | P2 | `doc-review-runner` | | `scope`, `viability`, `buildability`, `compression` facets from the owner's files. |
| 63 | `doc-lens-automatable` | document plan 6 | feature | P2 | `doc-review-runner`, `fence-overlap` | | The Automatable lens, mechanical ticket lint stage, automation ratio. |
| 64 | `doc-derive-fidelity` | document plan 7 | feature | P2 | `docset-manifest`, `doc-lenses-from-owner-prompts` | | `doc_derive`, fidelity gate by derive class. |
| 65 | `doc-fold-apply` | document plan 8 | feature | P2 | `docset-manifest`, `doc-derive-fidelity` | | `doc_fold`, `doc apply`, accept flow, `derive --stale`. |
| 66 | `doc-render` | document plan 9 | feature | P2 | `doc-facet-registry` | | Markdown to HTML with themes; PDF through host argv; `documents` config. |
| 67 | `doc-draft` | document plan 10 | feature | P2 | `doc-facet-registry`, `docset-manifest` | | Headless draft and the `doc-plan` ask prompt. |
| 68 | `doc-extension-menu` | document plan 11 | feature | P3 | `doc-fold-apply`, `doc-draft` | | Snapshot fields and menu items. |

### Operator actions (not tickets)

- Decide `vscode-help`: edit its fence to include `tests/unit/test_menu_admission.py` and `tests/unit/test_verdict_menu_parity.py` (its diagnosis names them) and `confirm`, or `reject`.
- Triage `box-000324`, `box-000440`, `box-000441`, `box-000442` to the rows above (10, 8, 9, 9) so the box and the roadmap agree.
- Hand tests before authoring: Gemini CLI facts (gemini plan A0), GitHub prefill limits (upstream plan step 0), the 13 conflict-facts events (parallel plan A0), the journal re-measurement (row 35).

## 9. Keeping this document true

- A ticket authored from a row links its stem in that row; a merged row is struck through, not deleted, until the release ships; a shipped release's rows move to a "Shipped" section at the end.
- The audit (sections 2-4) is re-run before each minor release with the same six passes; rows that are fixed are removed, rows that recur are marked with the release that was supposed to fix them.
- Shared budgets (section 5, decision 5) and shared files (decision 8) are updated whenever a plan adds a ticket that touches them.
