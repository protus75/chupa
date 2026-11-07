---
id: decision-box-000029-191a4e15
kind: decision
link: box-000029-191a4e15
reopen_after_days: 90
---
`load_config` and `migrate_config` in `chupa/config.py` read a relative `--config` path against the process working directory, not the `cwd` argument they are given. The `cwd` argument is used only to find the default `config.yaml`. The note asks to resolve `config_path` against `cwd` so the seam behaves the same way in both cases.

Nothing goes wrong at runtime today. In `chupa/__main__.py`, `repo` (the value passed as `cwd`) is `Path.cwd()` unless the `cwd` argument is supplied, and every CLI call passes `cwd=repo`, so a relative `--config` resolves to the same file either way. The note itself says no current caller differs. That makes this a consistency fix, not a harmful behavior gap.

- chupa/config.py:269-271: `path = config_path if config_path is not None else Path(cwd) / "config.yaml"`, so a relative config_path is not joined to cwd
- chupa/__main__.py:282: `repo = Path(cwd) if cwd is not None else Path.cwd()`
- chupa/__main__.py:290,314,438: load_config/migrate_config are called with `cwd=repo`, which in CLI use is the process cwd
- The message states that no current caller differs

Message: box-000029-191a4e15
