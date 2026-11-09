---
id: declined-box-000349-216853da
kind: declined
link: box-000349-216853da
reopen_after_days: 60
---
The `vscode` task in `dev.py` (lines 148-152) bumps the patch version in `vscode-chupa/package.json`. It rewrites the whole file with `json.dumps(package, indent="\t")`, so inline arrays become multi-line and non-ASCII characters such as the ellipsis become `\u2026` escapes. The uncommitted diff after an install is therefore larger than the one-line version change.

The rewritten manifest has the same meaning: JSON parsers decode `\u2026` to the same character, and VS Code and vsce read the same values. Only the formatting of the diff changes. Each install already leaves `package.json` dirty because of the version bump, so any harm from a dirty manifest, such as `dirty_overlap` refusing a merge that touches the file, happens with or without the reformatting. Nothing incorrect happens at runtime, so this is cleanup and formatting preference, which the admission bar declines.

- dev.py:149-152 loads package.json, increments the patch version, and writes it back with json.dumps(package, indent="\t") + "\n". It uses the default ensure_ascii=True and does not keep the original formatting.
- The comment at dev.py:147 says every install bumps the version on purpose, so package.json is dirty after an install whether or not the formatting changes.
- No open ticket, merged stem or registry record covers how dev.py formats package.json.

Message: box-000349-216853da
