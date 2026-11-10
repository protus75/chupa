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
- chupa/config.py::Provider
- chupa/watchdog.py
- chupa/__main__.py::main
- tests/unit/test_codex_effort.py
- tests/unit/test_docs_verb.py
- tests/integration/test_closed_sets.py::test_providers_closed_sets_and_constants
- tests/integration/test_cli.py::test_docs_reports_installed_guides
- tests/integration/test_host_contract.py
- docs/how-chupa-works.md#8.1 Providers
- chupa/docs/host-contract.md
- chupa/docs/host-running.md

## Goal / Why
chupa can route calls only to the `claude` and `codex` CLIs. A provider named `qwen` is refused at setup with `no shipped cli adapter`. The operator wants a local implementation provider: the `qwen3-coder:30b` model served by Ollama, driven by Qwen's own agent CLI, Qwen Code (`qwen`, pnpm package `@qwen-code/qwen-code`).

A host user must never configure files in their home directory for this. Everything qwen needs comes from chupa: the host's `config.yaml` and files shipped in the chupa package.

A hand test of `qwen` 0.27.1 against Ollama 0.40.16, run with an empty `HOME`, established these facts:
- `qwen --auth-type openai --openai-base-url <url> --openai-api-key ollama -m <model> -o stream-json --approval-mode plan --chat-recording false` reaches Ollama's OpenAI-compatible endpoint, with the prompt on stdin. Ollama ignores the key's value, but qwen requires one.
- With `QWEN_CODE_SYSTEM_SETTINGS_PATH` naming a JSON file that holds `{"context": {"fileName": "CLAUDE.md"}}`, qwen loads `CLAUDE.md` from the working directory. By default it loads `AGENTS.md`. qwen creates `$HOME/.qwen/` for its own runtime state but needs no configuration there.
- Its stream is in Claude's format: `system`/`init`, then `assistant` messages whose `content` holds `text` and `tool_use` blocks (each with an `id`), then a terminal `result` event with `subtype: success`, `is_error`, `result`, and `usage`. It has no `total_cost_usd`.
- `ClaudeAdapter.parse` reads that stream unchanged. So does the watchdog's claude branch (`chupa/watchdog.py`, the `assistant` `tool_use` ids and the `result` usage).
- `--approval-mode yolo` read and edited a file. `plan` is its analyze-only mode.

When this ticket is done:
- A provider declared as `name: qwen` with a `base_url` is served by a new `QwenAdapter`. Its conduct file is `CLAUDE.md`.
- A host setup guide, `chupa/docs/host-qwen.md`, covers Ollama on Linux and on a Windows host with chupa in WSL. `chupa docs` lists it.
- `chupa probe [PROVIDER ...]` (`./dev.py probe [PROVIDER ...]` in this repo) sends the preflight probe prompt through each provider's real adapter. It prints `ok` or the error with its paved road. The setup guide's smoke test is that command, never a hand-typed `qwen` command line.

Routing the provider in this repo's `config.yaml` is an operator edit and is not part of this ticket.

## Scope in / Scope out
- In:
  - `chupa/config.py`: `Provider` gains `base_url: str | None = None`. It holds the OpenAI-compatible endpoint a local-model CLI calls.
  - `chupa/qwen-settings.json` (new): exactly `{"context": {"fileName": "CLAUDE.md"}}` plus a trailing newline.
  - `chupa/providers.py`:
    - `CliAdapter`:
      - gains a class attribute `uses_base_url = False`. `__init__` raises `ProviderSetupError` when `provider.base_url` is set and `uses_base_url` is false, with a paved road to remove `base_url` from that provider. It also raises when `base_url` is unset and `uses_base_url` is true, with a paved road to set `base_url` in `config.yaml`.
      - gains a method `call_env()` that returns `child_env(self._env, self._config, self.provider)`. `invoke` passes `env=self.call_env()`, with no other change to `invoke`.
    - add `class QwenAdapter(ClaudeAdapter)` directly after `CodexAdapter`, and register `"qwen": QwenAdapter` in `ADAPTERS`. The class sets:
      - `binary = "qwen"`;
      - `reports_cost = False`;
      - `uses_base_url = True`;
      - `AUTH_MARKERS = ()`;
      - `LOGIN_ROAD` to a paved road naming `chupa/docs/host-qwen.md` and `./dev.py drain`;
      - `argv(model, effort, writes)` to return `["qwen", "--auth-type", "openai", "--openai-base-url", self.provider.base_url, "--openai-api-key", "ollama", "-m", model, "-o", "stream-json", "--approval-mode", "yolo" if writes else "plan", "--chat-recording", "false"]`. There is no effort flag;
      - `call_env()` to return the base result plus `QWEN_CODE_SYSTEM_SETTINGS_PATH` set to the absolute path of the installed `chupa/qwen-settings.json`, located from `Path(__file__).parent`.

      `parse` is inherited unchanged.
    - in `routed_conduct_paths`, select `CLAUDE.md` when the served provider's name is `claude` or `qwen`, and `AGENTS.md` otherwise.
  - `chupa/__main__.py`:
    - the `docs` verb's tuple gains a fourth entry, `("qwen", "local qwen provider setup")`, after `contract`.
    - a new `probe` verb: `chupa probe [PROVIDER ...]`. It loads the config, takes no lock, and writes no journal event. For each named provider, or every declared provider when none is named, it does the following for each distinct model in that provider's `models_by_tier`:
      - build that provider's `ADAPTERS` adapter the way `ProviderLLM.__init__` does, with `capture_dir` set to `config.state_dir / "spools" / "probe"`, `exec_=SubprocessExec()`, `fs=LocalFileSystem()`, `redactor=Redactor.from_config(config, os.environ)`, `env=os.environ`, `cwd` the repo, and `timeout=PREFLIGHT_TIMEOUT_S`;
      - send `LLMRequest(surface="preflight", rendered=PROBE_PROMPT, tier=<that tier>, effort="low", ticket=None, worktree=None)` through `invoke`;
      - print `<provider> <model>: ok`, or `<provider> <model>: <error>` followed by the error's paved road when it has one.

      It exits 0 when every probe answered and 1 otherwise. A name that is not a declared provider is refused with exit 2, naming the declared providers.
  - `dev.py`: a `probe` subcommand taking optional provider names, forwarding to `chupa probe [PROVIDER ...]`. Add its docstring line, `./dev.py probe [PROVIDER...]  send the probe prompt through each provider`.
  - `tests/unit/test_qwen_adapter.py` (new), built the way `tests/unit/test_codex_effort.py` builds its adapter, with a `provider` carrying `base_url`:
    - tests of `argv` and `call_env`;
    - a test of `parse` over a recorded qwen stream: a `system` init event, an `assistant` event with a `tool_use` block, an `assistant` text event, and a `result` success event with `usage` and no `total_cost_usd`;
    - tests of the `base_url` setup refusals;
    - tests of `routed_conduct_paths`.
  - `tests/integration/test_closed_sets.py`: the `ADAPTERS` assertion gains `"qwen": "QwenAdapter"`. Leave the rest unchanged.
  - `tests/unit/test_docs_verb.py` and `tests/integration/test_cli.py`: the `docs` assertions expect four guides, ending with `host-qwen.md`.
  - `tests/unit/test_probe_verb.py` (new): tests of `chupa probe` with a fake process exec. Cover one provider passing, one failing (the output carries the paved road and the exit is 1), the default of every declared provider, and an unknown name (exit 2).
  - `tests/integration/test_dev.py`: a test that `./dev.py probe qwen` forwards `["uv", "run", "python", "-m", "chupa", "probe", "qwen"]`.
  - `chupa/docs/host-running.md`: the verb table gains a `probe` row.
  - `chupa/docs/host-contract.md`:
    - the `Provider` row of the schema-defaults block gains `base_url: unset`;
    - the sentence "Shipped runtime adapters are `claude` and `codex`" lists `claude`, `codex`, and `qwen`, and points to `host-qwen.md`;
    - the following sentence also gives `qwen` the codex no-cost rule, and adds that `base_url` is required for `qwen` and refused for the other adapters.

    Leave the rest of the file unchanged.
  - `docs/how-chupa-works.md` §8.1:
    - "Two CLI adapters ship: `claude` and `codex`." names three: `claude`, `codex`, and `qwen` (Qwen Code against a local Ollama model at the provider's `base_url`);
    - the write-access bullet adds `qwen --approval-mode yolo`;
    - add one sentence: `claude` and `qwen` read `CLAUDE.md`, and `codex` reads `AGENTS.md`. chupa points qwen at `CLAUDE.md` through its packaged `qwen-settings.json`.

    Leave the rest of the section unchanged. Also add a `probe` row to the command table and a `probe [PROVIDER...]` row to the `./dev.py` subcommand table.
  - `chupa/docs/host-qwen.md` (new), the host setup guide. It never tells the operator to edit a file in their home directory. Sections, in this order:
    1. **What it is**: Ollama serves `qwen3-coder:30b`, and Qwen Code (`qwen`) is the agent loop. Route it to `implement`. chupa passes the endpoint from `base_url` and points qwen at `CLAUDE.md` itself, so no qwen configuration file is needed.
    2. **Run the Ollama server**, in two variants:
       - **(a) Linux, same machine as chupa:** install with `curl -fsSL https://ollama.com/install.sh | sh`. Set the server settings with `sudo systemctl edit ollama`, as `[Service]` `Environment=` lines for `OLLAMA_CONTEXT_LENGTH=65536`, `OLLAMA_FLASH_ATTENTION=1`, and `OLLAMA_KV_CACHE_TYPE=q8_0`, then `sudo systemctl restart ollama`. `base_url` is `http://localhost:11434/v1`.
       - **(b) Windows host, chupa in WSL:**
         - install or update with `winget upgrade Ollama.Ollama`;
         - set the Windows user environment variables `OLLAMA_HOST=0.0.0.0:11434` (by default Ollama listens on `127.0.0.1` only, which WSL cannot reach), plus the three above. Give both the GUI path (Start → `environment` → *Edit environment variables for your account* → *User variables* → *New...*) and a PowerShell `setx` block;
         - quit Ollama from the tray and start it from the Start menu. Note the trap: an Ollama started by the installer, or from a shell opened before `setx`, still listens on `127.0.0.1`. The fallback is tray → *Settings* → *Expose Ollama to the network*;
         - add the admin PowerShell firewall rule `New-NetFirewallRule -DisplayName "Ollama from WSL" -Direction Inbound -Protocol TCP -LocalPort 11434 -InterfaceAlias "vEthernet (WSL*)" -Action Allow`, which admits WSL's NAT interface only;
         - `base_url` is `http://<host-ip>:11434/v1`, where `<host-ip>` is the Windows host's address as seen from WSL. That address can change when Windows restarts; update `base_url` if `chupa probe qwen` cannot connect.
    3. **Pull the model**: `ollama pull qwen3-coder:30b`.
    4. **Install Qwen Code**: `pnpm add -g @qwen-code/qwen-code@latest`.
    5. **Declare it in config.yaml**: a YAML snippet for the provider:
       ```
       name: qwen
       kind: cli
       package: "@qwen-code/qwen-code"
       base_url: http://localhost:11434/v1
       models_by_tier: {low: qwen3-coder:30b, medium: qwen3-coder:30b, high: qwen3-coder:30b, max: qwen3-coder:30b}
       limits: {concurrency: 1, est_cost_per_call_usd: 0}
       ```
    6. **Probe it**: `chupa probe qwen` (`./dev.py probe qwen` in the chupa repo). `qwen qwen3-coder:30b: ok` means Ollama, Qwen Code, and `base_url` all work. Otherwise it prints the error and its fix. The first call loads the model, which takes about a minute.
    7. **Route it**: an example fallback routing row, `{tier: low, surface: implement, candidates: [{provider: codex}, {provider: qwen}]}`. Add one sentence: preflight probes every routed model at drain start, so Ollama must be up whenever `qwen` is routed.
    8. **Limits**: a short paragraph.
       - Ollama truncates a prompt longer than `OLLAMA_CONTEXT_LENGTH` without an error.
       - Qwen Code's own system prompt and tools take about 10k tokens of that window, and `CLAUDE.md` adds its own size.
       - Each call carries about 12s of CLI startup.
       - A 24 GB GPU fits the model with about 64k tokens of context.
- Out:
  - `config.yaml`: routing is an operator edit after setup;
  - `chupa/watchdog.py`: its claude branch already reads qwen's events;
  - `chupa/observe.py`'s live-call label for qwen;
  - `FAILURE_MARKERS` and failure classification;
  - any change to `ClaudeAdapter`'s or `CodexAdapter`'s argv or parse;
  - an HTTP client for Ollama;
  - resolving the WSL host address automatically.

## Scope fence
- chupa/config.py
- chupa/providers.py
- chupa/qwen-settings.json
- chupa/__main__.py
- dev.py
- tests/unit/test_qwen_adapter.py
- tests/unit/test_probe_verb.py
- tests/unit/test_docs_verb.py
- tests/integration/test_dev.py
- chupa/docs/host-running.md
- tests/integration/test_closed_sets.py
- tests/integration/test_cli.py
- chupa/docs/host-qwen.md
- chupa/docs/host-contract.md
- docs/how-chupa-works.md

## Acceptance criteria
1. `tests/unit/test_qwen_adapter.py` asserts that, for a provider with `base_url="http://h:11434/v1"`, `argv("qwen3-coder:30b", "low", False)` equals `["qwen", "--auth-type", "openai", "--openai-base-url", "http://h:11434/v1", "--openai-api-key", "ollama", "-m", "qwen3-coder:30b", "-o", "stream-json", "--approval-mode", "plan", "--chat-recording", "false"]`. It also asserts that `writes=True` differs only in `yolo` in place of `plan`. Ruled out: `yolo` on a read-only surface, a missing base URL, and a positional prompt argument.
2. The same file asserts that `call_env()` maps `QWEN_CODE_SYSTEM_SETTINGS_PATH` to an absolute path of an existing file whose JSON is `{"context": {"fileName": "CLAUDE.md"}}`. Ruled out: a relative path, or a path under the home directory.
3. The same file asserts that `parse` over the recorded qwen stream returns the `result` text with `usd is None` and the summed input tokens. Ruled out: a `ValueError`, or a zero cost.
4. The same file asserts two refusals: constructing `QwenAdapter` for a provider without `base_url` raises `ProviderSetupError`, and constructing `ClaudeAdapter` for a provider with `base_url` raises `ProviderSetupError`.
5. The same file asserts that `providers.ADAPTERS["qwen"] is QwenAdapter` and that `QwenAdapter.reports_cost is False`. It also asserts that `routed_conduct_paths` returns `(checkout / "CLAUDE.md",)` for a config routing only `qwen`, not `AGENTS.md`.
6. `./dev.py test tests/unit/test_docs_verb.py tests/integration/test_cli.py tests/integration/test_closed_sets.py tests/integration/test_host_contract.py` exits 0. In it:
   - `chupa docs` prints four guides, the last being `host-qwen.md`;
   - `ADAPTERS` names `claude`, `codex`, and `qwen`;
   - the schema-defaults block matches `Provider` with `base_url`.
7. `chupa/docs/host-qwen.md` exists and contains each of: `systemctl edit ollama`, `OLLAMA_HOST=0.0.0.0:11434`, `setx`, `Expose Ollama to the network`, `New-NetFirewallRule`, `ollama pull qwen3-coder:30b`, `@qwen-code/qwen-code`, `base_url:`, `chupa probe qwen`, `name: qwen`, `{provider: qwen}`. It contains none of `~/.qwen`, `~/.bashrc`, `settings.json`, `--openai-base-url`, `stream-json`, or `curl -s`.
8. `./dev.py test tests/unit/test_probe_verb.py tests/integration/test_dev.py` exits 0. These cases are covered:
   - a passing probe prints `<provider> <model>: ok`;
   - a failing probe prints the error with its paved road and exits 1, not 0;
   - no names probes every declared provider;
   - an unknown name exits 2;
   - `./dev.py probe qwen` forwards to `chupa probe qwen`.
9. `grep -n "Two CLI adapters" docs/how-chupa-works.md` prints nothing, and `docs/how-chupa-works.md` and `chupa/docs/host-contract.md` each name `qwen` as a shipped adapter.
10. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a file outside the scope fence changes, including `config.yaml` and `chupa/watchdog.py`;
- the argv or parse of `ClaudeAdapter` or `CodexAdapter` changes;
- `QwenAdapter` overrides `parse`;
- a read-only surface runs qwen with `--approval-mode yolo`;
- any setup step or code path reads or writes a file in the user's home directory.

## Time budget
- expected: 60m
- stuck: 150m
