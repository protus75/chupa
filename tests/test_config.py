import textwrap
from pathlib import Path

import pytest

from chupa.config import SCHEMA_VERSION, ConfigError, load_config

VALID = textwrap.dedent(
    """\
    schema_version: 1
    state_dir: .chupa
    providers:
      - name: claude
        kind: cli
        models_by_tier: {low: haiku, medium: sonnet, high: opus, max: opus}
        limits: {concurrency: 1, est_cost_per_call_usd: 0.25}
    routing:
      - {tier: medium, surface: implement, candidates: [{provider: claude, model: sonnet}]}
    review:
      mechanical:
        - {code: pytest, argv: [uv, run, pytest], trigger: always, severity: hard}
        - {code: ruff, argv: [uv, run, ruff, check], trigger: [chupa/], severity: soft}
      surfaces:
        - {name: correctness, trigger: always, rules_doc: docs/review.md, severity: hard}
      trigger_map: {chupa/: [scope_fence]}
      gate_severity: {scope_fence: hard}
    merge:
      safety_checks: [pytest]
      strategies:
        - {paths: [uv.lock], strategy: regenerate, argv: [uv, lock]}
        - {paths: [CHANGELOG.md], strategy: union}
    engine_plane_safety_inventory: [specs/, chupa/gates.py, config.yaml]
    """
)


def write(tmp_path: Path, text: str, name: str = "config.yaml") -> Path:
    path = tmp_path / name
    path.write_text(text)
    return path


def edit(text: str, old: str, new: str) -> str:
    assert old in text
    return text.replace(old, new, 1)


def refusal(tmp_path: Path, text: str) -> ConfigError:
    write(tmp_path, text)
    with pytest.raises(ConfigError) as exc:
        load_config(None, cwd=tmp_path)
    return exc.value


def test_valid_config_loads_from_cwd_with_shipped_defaults(tmp_path):
    cfg = load_config(None, cwd=write(tmp_path, VALID).parent)
    assert cfg.schema_version == SCHEMA_VERSION == 1
    assert cfg.state_dir == tmp_path / ".chupa"
    assert cfg.worktree_root == tmp_path / ".chupa" / "worktrees"
    assert cfg.providers[0].auth is None
    assert cfg.providers[0].limits.quota_window_minutes == 60
    assert cfg.routing[0].candidates[0].provider == "claude"
    assert cfg.routing_default_tier == "medium"
    assert cfg.review.mechanical[0].trigger == "always"
    assert cfg.review.mechanical[1].trigger == ["chupa/"]
    assert cfg.merge.strategies[0].argv == ["uv", "lock"]
    assert cfg.scheduler.max_unmerged == 2
    assert cfg.caps.model_dump() == {
        "diagnosis": 6, "retry": 6, "premise_bounce": 2, "infra": 6, "quarantine": 5, "poison": 2,
    }
    assert cfg.seeding.max_seeds_per_admission == 3
    assert cfg.circuit_breaker.k == 3
    assert cfg.circuit_breaker.cooldown_minutes == 10
    assert cfg.drain.max_runtime_hours == 12
    assert cfg.drain.max_ticket_minutes == 90
    assert cfg.box_policy == {
        "failure_report": "confirmed",
        "retro_finding": "confirmed",
        "override_report": "draft",
        "suggestion": "draft",
        "bug_report_self_diagnosed": "confirmed",
        "bug_report_player_repro": "confirmed",
        "bug_report_player_no_repro": "draft",
    }
    assert cfg.notify is None
    assert cfg.report_inbox is None
    assert cfg.context_files == []


def test_config_flag_path_overrides_cwd(tmp_path):
    other = tmp_path / "elsewhere"
    other.mkdir()
    path = write(other, edit(VALID, "state_dir: .chupa", "state_dir: /var/chupa"), "host.yaml")
    cfg = load_config(path, cwd=tmp_path)
    assert cfg.state_dir == Path("/var/chupa")


def test_explicit_values_override_defaults_and_partial_blocks_keep_the_rest(tmp_path):
    text = VALID + textwrap.dedent(
        """\
        worktree_root: /tmp/wt
        caps: {retry: 4}
        box_policy: {failure_report: draft}
        notify: [notify-send, chupa]
        report_inbox: inbox
        context_files: [docs/arch.md]
        """
    )
    cfg = load_config(write(tmp_path, text), cwd=tmp_path)
    assert cfg.worktree_root == Path("/tmp/wt")
    assert cfg.caps.retry == 4 and cfg.caps.diagnosis == 6
    assert cfg.box_policy["failure_report"] == "draft"
    assert cfg.box_policy["suggestion"] == "draft"
    assert cfg.notify == ["notify-send", "chupa"]
    assert cfg.report_inbox == tmp_path / "inbox"
    assert cfg.context_files == [Path("docs/arch.md")]


@pytest.mark.parametrize(
    "key", ["schema_version", "state_dir", "providers", "routing", "review", "merge",
            "engine_plane_safety_inventory"],
)
def test_missing_required_top_level_key_is_refused_naming_it(tmp_path, key):
    lines = VALID.splitlines(keepends=True)
    start = next(i for i, line in enumerate(lines) if line.startswith(f"{key}:"))
    end = next((i for i in range(start + 1, len(lines)) if not lines[i].startswith(" ")), len(lines))
    err = refusal(tmp_path, "".join(lines[:start] + lines[end:]))
    assert err.key == key
    assert key in str(err)
    assert "missing" in str(err)


def test_missing_nested_required_key_names_full_path(tmp_path):
    err = refusal(tmp_path, edit(VALID, "limits: {concurrency: 1, est_cost_per_call_usd: 0.25}",
                                 "limits: {est_cost_per_call_usd: 0.25}"))
    assert err.key == "providers.0.limits.concurrency"
    assert "providers.0.limits.concurrency" in str(err)


def test_unknown_key_is_refused_naming_it(tmp_path):
    err = refusal(tmp_path, VALID + "workers: 4\n")
    assert err.key == "workers"
    assert "workers" in str(err)


def test_explicit_null_is_refused_naming_key_even_where_a_default_exists(tmp_path):
    err = refusal(tmp_path, VALID + "caps: {retry: null}\n")
    assert err.key == "caps.retry"
    assert "null" in str(err)
    err = refusal(tmp_path, VALID + "notify:\n")
    assert err.key == "notify"


def test_wrong_type_is_refused_not_coerced(tmp_path):
    err = refusal(tmp_path, VALID + 'caps: {retry: "4"}\n')
    assert err.key == "caps.retry"
    err = refusal(tmp_path, VALID + "caps: {retry: true}\n")
    assert err.key == "caps.retry"


def test_newer_schema_version_is_refused(tmp_path):
    err = refusal(tmp_path, edit(VALID, "schema_version: 1", "schema_version: 2") + "future_key: x\n")
    assert err.key == "schema_version"
    assert "newer" in str(err)
    assert "upgrade chupa" in str(err)


def test_older_schema_version_is_refused_naming_migrate_config(tmp_path):
    err = refusal(tmp_path, edit(VALID, "schema_version: 1", "schema_version: 0"))
    assert err.key == "schema_version"
    assert "older" in str(err)
    assert "chupa migrate-config" in str(err)


@pytest.mark.parametrize("value", ['"1"', "1.0", "true", "-1"])
def test_non_integer_or_negative_schema_version_is_refused(tmp_path, value):
    err = refusal(tmp_path, edit(VALID, "schema_version: 1", f"schema_version: {value}"))
    assert err.key == "schema_version"


def test_api_provider_is_refused_until_its_client_ships(tmp_path):
    err = refusal(tmp_path, edit(VALID, "kind: cli", "kind: api\n    auth: ANTHROPIC_API_KEY"))
    assert err.key == "providers.0.kind"
    assert "kind: cli" in str(err)


def test_routing_candidate_must_name_a_declared_provider(tmp_path):
    err = refusal(tmp_path, edit(VALID, "{provider: claude, model: sonnet}", "{provider: gpt, model: x}"))
    assert err.key == "routing.0.candidates.0.provider"
    assert "gpt" in str(err)


def test_retry_cap_above_diagnosis_cap_is_refused(tmp_path):
    err = refusal(tmp_path, VALID + "caps: {retry: 7}\n")
    assert err.key == "caps.retry"


def test_closed_vocabularies_refuse_unknown_values(tmp_path):
    assert refusal(tmp_path, edit(VALID, "severity: soft", "severity: warn")).key == (
        "review.mechanical.1.severity"
    )
    assert refusal(tmp_path, VALID + "box_policy: {bogus_row: draft}\n").key == "box_policy.bogus_row"
    assert refusal(tmp_path, VALID + "routing_default_tier: huge\n").key == "routing_default_tier"


def test_union_strategy_takes_no_argv_and_regenerate_requires_one(tmp_path):
    err = refusal(tmp_path, edit(VALID, "strategy: union}", "strategy: union, argv: [x]}"))
    assert err.key.startswith("merge.strategies.1")
    err = refusal(tmp_path, edit(VALID, "strategy: regenerate, argv: [uv, lock]}", "strategy: regenerate}"))
    assert err.key.startswith("merge.strategies.0")


def test_missing_file_is_refused_with_a_paved_road(tmp_path):
    with pytest.raises(ConfigError) as exc:
        load_config(None, cwd=tmp_path)
    assert str(tmp_path / "config.yaml") in str(exc.value)
    assert "--config" in str(exc.value)


def test_non_mapping_and_unparseable_yaml_are_refused(tmp_path):
    assert "mapping" in str(refusal(tmp_path, "- a\n- b\n"))
    assert "YAML" in str(refusal(tmp_path, "a: [unclosed\n"))


def test_unsafe_yaml_tags_are_refused(tmp_path):
    err = refusal(tmp_path, VALID + "notify: !!python/object/apply:os.system [echo hi]\n")
    assert "YAML" in str(err)
