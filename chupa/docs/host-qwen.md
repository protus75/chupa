# Local qwen provider setup

## What it is

Ollama serves `qwen3-coder:30b` and Qwen Code (`qwen`) runs the agent loop. Route it to `implement`. chupa passes the endpoint from `base_url` and points qwen at `CLAUDE.md` itself, so no qwen configuration file is needed.

## Run the Ollama server

### (a) Linux, same machine as chupa

Install with `curl -fsSL https://ollama.com/install.sh | sh`. Run `sudo systemctl edit ollama` and add:

```ini
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=65536"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
```

Run `sudo systemctl restart ollama`. Set `base_url` to `http://localhost:11434/v1`.

### (b) Windows host, chupa in WSL

Install or update with `winget upgrade Ollama.Ollama`. Set Windows user environment variables via Start → `environment` → *Edit environment variables for your account* → *User variables* → *New...*, or in PowerShell:

```powershell
setx OLLAMA_HOST "0.0.0.0:11434"
setx OLLAMA_CONTEXT_LENGTH "65536"
setx OLLAMA_FLASH_ATTENTION "1"
setx OLLAMA_KV_CACHE_TYPE "q8_0"
```

`OLLAMA_HOST=0.0.0.0:11434` is needed because Ollama normally listens only on `127.0.0.1`, which WSL cannot reach. Quit Ollama from the tray and start it from the Start menu. An instance started by the installer or from a shell opened before `setx` still listens on `127.0.0.1`. As a fallback, use tray → *Settings* → *Expose Ollama to the network*.

In administrator PowerShell add a firewall rule admitting only WSL's NAT interface:

```powershell
New-NetFirewallRule -DisplayName "Ollama from WSL" -Direction Inbound -Protocol TCP -LocalPort 11434 -InterfaceAlias "vEthernet (WSL*)" -Action Allow
```

Set `base_url` to `http://<host-ip>:11434/v1`, using the Windows host address as seen from WSL. This can change on restart; update it if `chupa probe qwen` cannot connect.

## Pull the model

Run `ollama pull qwen3-coder:30b`.

## Install Qwen Code

Run `pnpm add -g @qwen-code/qwen-code@latest`.

## Declare it in config.yaml

Add this provider:

```yaml
name: qwen
kind: cli
package: "@qwen-code/qwen-code"
base_url: http://localhost:11434/v1
models_by_tier: {low: qwen3-coder:30b, medium: qwen3-coder:30b, high: qwen3-coder:30b, max: qwen3-coder:30b}
limits: {concurrency: 1, est_cost_per_call_usd: 0}
```

## Probe it

Run `chupa probe qwen` (`./dev.py probe qwen` in the chupa repo). `qwen qwen3-coder:30b: ok` means Ollama, Qwen Code, and `base_url` all work; otherwise the error is printed. `error_during_execution` usually means qwen could not reach Ollama at `base_url`: check that Ollama is running, the URL, and on Windows the firewall rule and `OLLAMA_HOST`. The first call loads the model, which takes about a minute.

## Route it

For example, add a fallback routing row:

```yaml
{tier: low, surface: implement, candidates: [{provider: codex}, {provider: qwen}]}
```

Preflight probes every routed model at drain start, so Ollama must be up whenever `qwen` is routed.

## Limits

Ollama truncates prompts longer than `OLLAMA_CONTEXT_LENGTH` without an error. Qwen Code's own system prompt and tools take about 10k tokens of that window, and `CLAUDE.md` adds its own size. Each call carries about 12s of CLI startup. A 24 GB GPU fits the model with about 64k tokens of context.
