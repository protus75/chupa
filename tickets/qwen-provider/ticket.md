---
state: confirmed
source: human
priority: P2
kind: feature
---

## Depends on
- none

## Context
- chupa/providers.py
- chupa/watchdog.py
- chupa/__main__.py::main
- tests/unit/test_codex_effort.py
- tests/unit/test_docs_verb.py
- tests/integration/test_closed_sets.py::test_providers_closed_sets_and_constants
- tests/integration/test_cli.py::test_docs_reports_installed_guides
- docs/how-chupa-works.md#8.1 Providers
- chupa/docs/host-contract.md
- chupa/docs/host-running.md

## Goal / Why
chupa can route calls only to the `claude` and `codex` CLIs. A provider named `qwen` is refused at setup with `no shipped cli adapter`. The operator wants a local provider: the `qwen3-coder:30b` model served by Ollama on their own GPU, driven by Qwen's own agent CLI, Qwen Code (`qwen`, pnpm package `@qwen-code/qwen-code`). Qwen Code is tuned for this model, unlike driving it through codex or claude.

A hand test of `qwen` 0.27.1 against Ollama 0.40.16 established these facts:
- `qwen -m <model> -o stream-json --approval-mode plan --chat-recording false` reads the prompt from stdin.
- Its stream is in Claude's format: `system`/`init`, then `assistant` messages whose `content` holds `text` and `tool_use` blocks (each with an `id`), then a terminal `result` event with `subtype: success`, `is_error`, `result`, and `usage`. It has no `total_cost_usd`.
- `ClaudeAdapter.parse` reads it unchanged. So does the watchdog's claude branch (`chupa/watchdog.py`, the `assistant` `tool_use` ids and the `result` usage).
- `--approval-mode yolo` let it read and edit a file. `plan` is its analyze-only mode.
- The Ollama endpoint and model live in the operator's `~/.qwen/settings.json`, through a `modelProviders.openai` entry whose `baseUrl` is `$OLLAMA_BASE_URL`. The command line needs no Ollama details.
- By default qwen loads `AGENTS.md` from the working directory. With `"context": {"fileName": "CLAUDE.md"}` in that settings file, it loads `CLAUDE.md` instead.

The operator chose `CLAUDE.md` as qwen's conduct file because it is the canonical file, and `AGENTS.md` is a curated subset of it.

When this ticket is done:
- A provider declared as `name: qwen` is served by a new `QwenAdapter`, and its conduct file is `CLAUDE.md`.
- A host setup guide, `chupa/docs/host-qwen.md`, tells an operator how to bring Ollama, Qwen Code, and the provider up. `chupa docs` lists it.

Routing the provider is an operator edit to `config.yaml` and is not part of this ticket.

## Scope in / Scope out
- In:
  - `chupa/providers.py`:
    - add `class QwenAdapter(ClaudeAdapter)` directly after `CodexAdapter`, and register `"qwen": QwenAdapter` in `ADAPTERS`. The class sets:
      - `binary = "qwen"`;
      - `reports_cost = False`, since the stream carries no `total_cost_usd`;
      - `AUTH_MARKERS = ()`;
      - `LOGIN_ROAD` to a paved road naming `chupa/docs/host-qwen.md` and `./dev.py drain`;
      - `argv(model, effort, writes)` to return `["qwen", "-m", model, "-o", "stream-json", "--approval-mode", "yolo" if writes else "plan", "--chat-recording", "false"]`. There is no effort flag: effort is recorded in provenance only, as for claude.

      `parse` is inherited unchanged.
    - in `routed_conduct_paths`, select `CLAUDE.md` when the served provider's name is `claude` or `qwen`, and `AGENTS.md` otherwise.
  - `chupa/__main__.py`: the `docs` verb's tuple gains a fourth entry, `("qwen", "local qwen provider setup")`, after `contract`.
  - `tests/unit/test_qwen_adapter.py` (new), built the way `tests/unit/test_codex_effort.py` builds its adapter:
    - unit tests of `QwenAdapter.argv`;
    - a test of `QwenAdapter.parse` over a recorded qwen stream: a `system` init event, an `assistant` event with a `tool_use` block, an `assistant` text event, and a `result` success event with `usage` and no `total_cost_usd`;
    - a test of `routed_conduct_paths` for a config routing a `qwen` provider.
  - `tests/integration/test_closed_sets.py`: the `ADAPTERS` assertion gains `"qwen": "QwenAdapter"`. Leave the rest unchanged.
  - `tests/unit/test_docs_verb.py` and `tests/integration/test_cli.py`: the `docs` assertions expect four guides, ending with `host-qwen.md`.
  - `chupa/docs/host-qwen.md` (new), the host setup guide, with these sections in this order:
    1. **What it is**: Ollama serves `qwen3-coder:30b`, and Qwen Code (`qwen`) is the agent loop. Route it to `implement` only. It reads `CLAUDE.md` as its conduct file, set in its settings file (section 9).
    2. **Ollama on the Windows host**: install or update with `winget upgrade Ollama.Ollama`. Set these Windows user environment variables:
       - `OLLAMA_HOST=0.0.0.0:11434`, because by default Ollama listens on `127.0.0.1` only and WSL cannot reach it;
       - `OLLAMA_CONTEXT_LENGTH=65536`;
       - `OLLAMA_FLASH_ATTENTION=1`;
       - `OLLAMA_KV_CACHE_TYPE=q8_0`.

       Give both ways to set them: the GUI path (Start → `environment` → *Edit environment variables for your account* → *User variables* → *New...*) and a PowerShell `setx` block, one line per variable.
    3. **Restart Ollama**: quit from the tray icon and start Ollama from the Start menu. Note the trap: an Ollama started by the installer, or from a shell opened before `setx`, still listens on `127.0.0.1`. The fallback is tray → *Settings* → *Expose Ollama to the network*.
    4. **Windows firewall**: an admin PowerShell block, `New-NetFirewallRule -DisplayName "Ollama from WSL" -Direction Inbound -Protocol TCP -LocalPort 11434 -InterfaceAlias "vEthernet (WSL*)" -Action Allow`. Explain that it admits WSL's NAT interface only, not the LAN.
    5. **Pull the model**: `ollama pull qwen3-coder:30b`, run in PowerShell.
    6. **WSL environment**: `~/.bashrc` lines `export OLLAMA_BASE_URL="http://$(ip route show default | awk '{print $3}'):11434/v1"` and `export OLLAMA_API_KEY=ollama`. Explain why the URL is computed: the host IP can change when WSL restarts. `drain` and `serve` must start from a shell where both are set. Do not declare `OLLAMA_API_KEY` as the provider's `auth`, because chupa would then redact every occurrence of the word `ollama` from its captures.
    7. **Reachability check**: `curl -s "${OLLAMA_BASE_URL%/v1}/api/tags"` lists `qwen3-coder:30b`.
    8. **Install Qwen Code**: `pnpm add -g @qwen-code/qwen-code@latest`.
    9. **Qwen Code settings**: the full `~/.qwen/settings.json` as a JSON block:
       ```
       {"context": {"fileName": "CLAUDE.md"}, "security": {"auth": {"selectedType": "openai"}}, "modelProviders": {"openai": [{"id": "qwen3-coder:30b", "name": "qwen3-coder (Ollama)", "baseUrl": "$OLLAMA_BASE_URL", "envKey": "OLLAMA_API_KEY"}]}}
       ```
       Say what each key does.
    10. **Smoke test**: `echo "Reply with the single word ok." | qwen -m qwen3-coder:30b -o stream-json --approval-mode plan --chat-recording false`. A pass ends in a `result` event with `subtype: success` and `result: ok`. The first call loads the model, which takes about a minute.
    11. **Route it in config.yaml**: a YAML snippet for the provider:
        ```
        name: qwen
        kind: cli
        package: "@qwen-code/qwen-code"
        models_by_tier: {low: qwen3-coder:30b, medium: qwen3-coder:30b, high: qwen3-coder:30b, max: qwen3-coder:30b}
        limits: {concurrency: 1, est_cost_per_call_usd: 0}
        ```
        Also an example fallback routing row: `{tier: low, surface: implement, candidates: [{provider: codex}, {provider: qwen}]}`. Add one sentence: preflight probes every routed model at drain start, so Ollama must be up whenever `qwen` is routed.
    12. **Limits**: a short paragraph.
        - Ollama truncates a prompt longer than `OLLAMA_CONTEXT_LENGTH` without an error.
        - Qwen Code's own system prompt and tools take about 10k tokens of that window.
        - Each call carries about 12s of CLI startup.
        - A 24 GB GPU fits the model with about 64k tokens of context.
  - `chupa/docs/host-contract.md`: the sentence "Shipped runtime adapters are `claude` and `codex`" lists `claude`, `codex`, and `qwen`, and points to `host-qwen.md` for qwen setup. In the following sentence, also give `qwen` the codex no-cost rule. Leave the rest of the file unchanged.
  - `docs/how-chupa-works.md` §8.1: "Two CLI adapters ship: `claude` and `codex`." names three: `claude`, `codex`, and `qwen` (Qwen Code against a local Ollama model). The write-access bullet adds `qwen --approval-mode yolo`. Add one sentence: `claude` and `qwen` read `CLAUDE.md`, and `codex` reads `AGENTS.md`. Leave the rest of the section unchanged.
- Out:
  - `config.yaml`: routing is an operator edit after setup;
  - `chupa/watchdog.py`: its claude branch already reads qwen's events;
  - `chupa/observe.py`'s live-call label for qwen;
  - `FAILURE_MARKERS` and failure classification;
  - `chupa/config.py` and the provider schema;
  - any change to `ClaudeAdapter`'s or `CodexAdapter`'s behavior;
  - an HTTP client for Ollama.

## Scope fence
- chupa/providers.py
- chupa/__main__.py
- tests/unit/test_qwen_adapter.py
- tests/unit/test_docs_verb.py
- tests/integration/test_closed_sets.py
- tests/integration/test_cli.py
- chupa/docs/host-qwen.md
- chupa/docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/unit/test_qwen_adapter.py` asserts that `QwenAdapter.argv(adapter, "qwen3-coder:30b", "low", False)` equals `["qwen", "-m", "qwen3-coder:30b", "-o", "stream-json", "--approval-mode", "plan", "--chat-recording", "false"]`. It also asserts that the same call with `writes=True` differs only in `yolo` in place of `plan`. Ruled out: `yolo` on a read-only surface, and a positional prompt argument.
2. The same file asserts that `QwenAdapter.parse` over the recorded qwen stream returns the `result` text with `usd is None` and the summed input tokens. Ruled out: a `ValueError`, or a zero cost.
3. The same file asserts that `providers.ADAPTERS["qwen"] is QwenAdapter`, and that `QwenAdapter.reports_cost is False`.
4. The same file asserts that `routed_conduct_paths` returns `(checkout / "CLAUDE.md",)` for a config routing only a `qwen` provider, not `AGENTS.md`. It also asserts that it returns that one path, once, for a config routing `claude` and `qwen`.
5. `./dev.py test tests/unit/test_docs_verb.py tests/integration/test_cli.py tests/integration/test_closed_sets.py` exits 0. In it, `chupa docs` prints four guides, the last being `host-qwen.md`, and `ADAPTERS` names `claude`, `codex`, and `qwen`.
6. `chupa/docs/host-qwen.md` exists and contains each of: `OLLAMA_HOST=0.0.0.0:11434`, `setx`, `Expose Ollama to the network`, `New-NetFirewallRule`, `ollama pull qwen3-coder:30b`, `OLLAMA_BASE_URL`, `@qwen-code/qwen-code`, `$OLLAMA_BASE_URL`, `"fileName": "CLAUDE.md"`, `--approval-mode plan`, `name: qwen`, `{provider: qwen}`.
7. `grep -n "Two CLI adapters" docs/how-chupa-works.md` prints nothing, and `docs/how-chupa-works.md` and `chupa/docs/host-contract.md` each name `qwen` as a shipped adapter.
8. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a file outside the scope fence changes, including `config.yaml` and `chupa/watchdog.py`;
- `ClaudeAdapter` or `CodexAdapter` behavior changes, or `QwenAdapter` overrides `parse`;
- the qwen command line carries Ollama details (a base URL, an API key, or an `--auth-type`);
- a read-only surface runs qwen with `--approval-mode yolo`.

## Time budget
- expected: 40m
- stuck: 120m
