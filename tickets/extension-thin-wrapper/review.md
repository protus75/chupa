# Review: snag

The extension-side changes and the requested snapshot fields are correct, but six other new snapshot fields have no tests, and the diagnose test reads config.yaml from the current directory.

## Findings

- [acceptance] chupa/observe.py:581 Scope in requires tests in tests/test_watch.py for every new snapshot field. The diff adds `runningStem` and `verdictCommands`, and neither has a test. The extension now depends on both: detail.js uses `runningStem` to pick its fallback row, and the confirm and reject commands get their `--yes` policy from `verdictCommands`. (do instead: Add asserts to test_snapshot_display_fields that `snap["runningStem"] == "live"` (and None when nothing is running) and that `snap["verdictCommands"]` equals the confirm/reject argv the CLI accepts.)
- [acceptance] chupa/observe.py:576 The new step fields `timeDisplay` and `dateDisplay` have no tests, yet StepsTree.getTreeItem now draws them as the label and the tooltip. (do instead: Have a test_watch.py test assert `step["timeDisplay"] == watch.clock(step["ts"])` and the `dateDisplay` value for at least one snapshot step.)
- [acceptance] chupa/observe.py:562 The new merged-row fields `mergedAtDisplay` and `commit.dateDisplay` have no tests, yet detail.js renders both. (do instead: Extend test_snapshot_display_fields to assert `rows["done"]["mergedAtDisplay"]` and `rows["done"]["commit"]["dateDisplay"]` against `watch.local(ts).strftime("%x, %X")`.)
- [logic] tests/test_watch.py:213 test_diagnose_prompt_uses_live_running_state copies `Path("config.yaml")`, a path relative to the process's current directory. The test therefore depends on pytest's launch directory and on the live repo config. It fails or changes meaning when run from any other directory or after a config edit. Other CLI tests write an inline CONFIG constant instead. (do instead: Write a minimal inline config string to tmp_path / "config.yaml", as tests/test_cli.py and tests/test_diagnose_eval.py do, rather than reading the repo's config.yaml.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "e394ca290385afc7ce8c44d11f534b56fe138812",
  "stem": "extension-thin-wrapper",
  "reviewed_sha": "e394ca290385afc7ce8c44d11f534b56fe138812",
  "summary": "The extension-side changes and the requested snapshot fields are correct, but six other new snapshot fields have no tests, and the diagnose test reads config.yaml from the current directory.",
  "findings": [
    {
      "code": "acceptance",
      "path": "chupa/observe.py",
      "line": 581,
      "message": "Scope in requires tests in tests/test_watch.py for every new snapshot field. The diff adds `runningStem` and `verdictCommands`, and neither has a test. The extension now depends on both: detail.js uses `runningStem` to pick its fallback row, and the confirm and reject commands get their `--yes` policy from `verdictCommands`.",
      "paved_road": "Add asserts to test_snapshot_display_fields that `snap[\"runningStem\"] == \"live\"` (and None when nothing is running) and that `snap[\"verdictCommands\"]` equals the confirm/reject argv the CLI accepts.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "chupa/observe.py",
      "line": 576,
      "message": "The new step fields `timeDisplay` and `dateDisplay` have no tests, yet StepsTree.getTreeItem now draws them as the label and the tooltip.",
      "paved_road": "Have a test_watch.py test assert `step[\"timeDisplay\"] == watch.clock(step[\"ts\"])` and the `dateDisplay` value for at least one snapshot step.",
      "kind": null,
      "unit": null
    },
    {
      "code": "acceptance",
      "path": "chupa/observe.py",
      "line": 562,
      "message": "The new merged-row fields `mergedAtDisplay` and `commit.dateDisplay` have no tests, yet detail.js renders both.",
      "paved_road": "Extend test_snapshot_display_fields to assert `rows[\"done\"][\"mergedAtDisplay\"]` and `rows[\"done\"][\"commit\"][\"dateDisplay\"]` against `watch.local(ts).strftime(\"%x, %X\")`.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "tests/test_watch.py",
      "line": 213,
      "message": "test_diagnose_prompt_uses_live_running_state copies `Path(\"config.yaml\")`, a path relative to the process's current directory. The test therefore depends on pytest's launch directory and on the live repo config. It fails or changes meaning when run from any other directory or after a config edit. Other CLI tests write an inline CONFIG constant instead.",
      "paved_road": "Write a minimal inline config string to tmp_path / \"config.yaml\", as tests/test_cli.py and tests/test_diagnose_eval.py do, rather than reading the repo's config.yaml.",
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
