---
id: tombstone-box-000001-a8df16f3
kind: tombstone
link: pypi-package
reopen_after_days: 90
---
The bootstrap note said chupa had no build backend and no console-script entry point. Merged ticket pypi-package has since resolved both.

The suggestion asked for a decision on a build backend before the first console script was added. The current pyproject.toml declares [build-system] with build-backend uv_build and defines [project.scripts], so chupa is now an installable package. Merged ticket pypi-package covers this ground, so the message duplicates settled work. The leftover pytest pythonpath setting does not cause any incorrect runtime behavior.

- pyproject.toml:1 [build-system]
- pyproject.toml:3 build-backend = "uv_build"
- pyproject.toml:18 [project.scripts]
- merged stem pypi-package

Message: box-000001-a8df16f3
