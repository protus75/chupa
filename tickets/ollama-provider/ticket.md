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
- tests/unit/test_codex_effort.py
- tests/integration/test_closed_sets.py::test_providers_closed_sets_and_constants
- docs/how-chupa-works.md#8.1 Providers
- chupa/docs/host-contract.md
- config.yaml

## Goal / Why
chupa can route calls only to the `claude` and `codex` CLIs. A provider named `ollama` is refused at setup with `no shipped cli adapter`. The operator wants a third, local provider: the `qwen3-coder:30b` model served by Ollama on their own GPU. It will be used when the hosted providers are rate-limited, out of quota, or down.

Ollama serves models but is not an agent CLI. The installed codex CLI (0.167) can drive a local Ollama model with `codex exec --oss --local-provider ollama`, and it emits the same JSON event stream `CodexAdapter.parse` already reads. When this ticket is done:
- A provider declared as `name: ollama` in `config.yaml` is served by a new `OllamaAdapter`. It is the codex command line plus `--oss --local-provider ollama`.
- A setup README tells the operator how to bring up Ollama and make it reachable from WSL before they route the provider.

Routing the provider is an operator edit to `config.yaml` and is not part of this ticket.

## Scope in / Scope out
- In:
  - `chupa/providers.py`: add `class OllamaAdapter(CodexAdapter)` directly after `CodexAdapter`, then register it as `"ollama": OllamaAdapter` in `ADAPTERS`. The class:
    - keeps `binary = "codex"` and `reports_cost = False` (inherited);
    - sets `AUTH_MARKERS = ()`, since a local Ollama has no login;
    - sets `LOGIN_ROAD` to a paved road telling the operator to start Ollama per `docs/ollama-setup.md`, then run `./dev.py drain`;
    - overrides `argv` to return `CodexAdapter.argv(...)` with `--oss`, `--local-provider`, `ollama` inserted immediately before the trailing `-`, so `-` stays the last element.
  - `tests/unit/test_ollama_adapter.py` (new): unit tests of `OllamaAdapter.argv`, built the way `tests/unit/test_codex_effort.py` builds its adapter.
  - `tests/integration/test_closed_sets.py`: the `ADAPTERS` assertion in `test_providers_closed_sets_and_constants` gains `"ollama": "OllamaAdapter"`. Leave the rest of the test unchanged.
  - `docs/ollama-setup.md` (new): the operator setup README, with these sections in this order:
    1. **What it is**: Ollama serves `qwen3-coder:30b`, and codex `--oss --local-provider ollama` is the agent loop. The provider follows `AGENTS.md`.
    2. **Windows host: install and environment**: Ollama runs on the Windows host, with models on a Windows drive. Set these user environment variables:
       - `OLLAMA_HOST=0.0.0.0:11434`, so WSL can reach it, since by default it listens on `127.0.0.1` only;
       - `OLLAMA_CONTEXT_LENGTH=65536`;
       - `OLLAMA_FLASH_ATTENTION=1`;
       - `OLLAMA_KV_CACHE_TYPE=q8_0`.

       Give both ways to set them: the GUI path (Start → `environment` → *Edit environment variables for your account* → *User variables* → *New...*) and a PowerShell `setx` block, one line per variable. Then: quit Ollama from its tray icon and start it again from the Start menu, so it picks up the variables.
    3. **Windows firewall**: an admin PowerShell code block with `New-NetFirewallRule -DisplayName "Ollama from WSL" -Direction Inbound -Protocol TCP -LocalPort 11434 -InterfaceAlias "vEthernet (WSL*)" -Action Allow`, and one sentence on why: WSL's default NAT networking reaches the host through that interface, and scoping the rule to it keeps the port closed to the LAN.
    4. **Pull the model**: `ollama pull qwen3-coder:30b`, run in PowerShell.
    5. **WSL: point codex at the host**: a `~/.bashrc` line, `export CODEX_OSS_BASE_URL="http://$(ip route show default | awk '{print $3}'):11434/v1"`. Explain why it is computed rather than hard-coded: the host IP changes when WSL restarts. `drain` and `serve` must be started from a shell where it is set, because a provider call inherits the operator's environment.
    6. **Smoke test**: a reachability check, `curl -s "${CODEX_OSS_BASE_URL%/v1}/api/version"`, then the probe, `echo "Reply with the single word ok." | codex exec --json --oss --local-provider ollama -m qwen3-coder:30b --sandbox read-only -c approval_policy=never -`. A pass prints an `agent_message` item whose text is `ok`.
    7. **Route it in config.yaml**: a YAML snippet for the provider:
       ```
       name: ollama
       kind: cli
       package: "@openai/codex"
       models_by_tier: {low: qwen3-coder:30b, medium: qwen3-coder:30b, high: qwen3-coder:30b, max: qwen3-coder:30b}
       limits: {concurrency: 1, est_cost_per_call_usd: 0}
       ```
       Also an example fallback routing row: `{tier: low, surface: implement, candidates: [{provider: codex}, {provider: ollama}]}`. Add one sentence: preflight probes every routed model at drain start, so Ollama must be up whenever the provider is routed.
    8. **Limits**: one short paragraph on context size. A prompt larger than `OLLAMA_CONTEXT_LENGTH` is truncated by Ollama without an error. A 24 GB GPU fits the 30B model with about 64k tokens of context.
  - `docs/how-chupa-works.md` §8.1: change "Two CLI adapters ship: `claude` and `codex`." to name three adapters: `claude`, `codex`, and `ollama` (codex driving a local Ollama model, set up per `docs/ollama-setup.md`). Leave the rest of the section unchanged.
  - `chupa/docs/host-contract.md`: change the sentence "Shipped runtime adapters are `claude` and `codex`" to list `claude`, `codex`, and `ollama`. In the next sentence, also give `ollama` the codex no-cost rule. Leave the rest of the file unchanged.
- Out:
  - `config.yaml`: routing is an operator edit after setup;
  - `chupa/observe.py`: its label already shows `codex <model>` for this command line;
  - `FAILURE_MARKERS` and failure classification: a refused connection stays `unclassified`;
  - `chupa/config.py` and the provider schema;
  - an HTTP or API client for Ollama;
  - any change to `ClaudeAdapter` or `CodexAdapter`.

## Scope fence
- chupa/providers.py
- tests/unit/test_ollama_adapter.py
- tests/integration/test_closed_sets.py
- docs/ollama-setup.md
- docs/how-chupa-works.md
- chupa/docs/host-contract.md

## Acceptance criteria
1. `tests/unit/test_ollama_adapter.py` asserts that `OllamaAdapter.argv(adapter, "qwen3-coder:30b", "low", False)` meets all of the following, and `./dev.py test tests/unit/test_ollama_adapter.py` exits 0:
   - it starts with `codex exec --json -m qwen3-coder:30b`;
   - it contains `--oss` and the adjacent pair `--local-provider`, `ollama`;
   - it contains `--sandbox read-only`;
   - its last element is `-`. Ruled out: flags appended after `-`, and the plain codex command line without `--oss`.
2. The same test file asserts that `OllamaAdapter.argv(adapter, "m", "high", True)` contains `--dangerously-bypass-approvals-and-sandbox` and `--oss`, and does not contain `read-only`.
3. The same test file asserts that `providers.ADAPTERS["ollama"] is OllamaAdapter` and that `OllamaAdapter.AUTH_MARKERS == ()`.
4. `./dev.py test tests/integration/test_closed_sets.py` exits 0 with the `ADAPTERS` assertion naming `claude`, `codex`, and `ollama`.
5. `docs/ollama-setup.md` exists and contains each of these strings: `OLLAMA_HOST=0.0.0.0:11434`, `setx`, `New-NetFirewallRule`, `ollama pull qwen3-coder:30b`, `CODEX_OSS_BASE_URL`, `--oss --local-provider ollama`, `name: ollama`, `{provider: ollama}`.
6. `docs/how-chupa-works.md` and `chupa/docs/host-contract.md` each name `ollama` as a shipped adapter. `grep -n "Two CLI adapters" docs/how-chupa-works.md` prints nothing.
7. `./dev.py test` exits 0.

## Verification
```
./dev.py test
```

## Definition of rejected
Reject the branch if any of the following holds:
- a file outside the scope fence changes, including `config.yaml`;
- `CodexAdapter` or `ClaudeAdapter` behavior changes;
- `OllamaAdapter` calls Ollama over HTTP, or uses a binary other than `codex`;
- the `-` stdin marker is not the last command-line element;
- `FAILURE_MARKERS` changes.

## Time budget
- expected: 30m
- stuck: 90m
