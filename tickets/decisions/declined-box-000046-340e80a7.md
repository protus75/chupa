---
id: declined-box-000046-340e80a7
kind: declined
link: box-000046-340e80a7
reopen_after_days: 90
---
A bootstrap note said nothing in production supplied the `Sleep` seam yet. Callers passed `asyncio.sleep` themselves, and the note expected the Phase 1 drain scaffold to build the seam bundle once per session. That wiring now exists. `chupa/seams.py:16` defines `Sleep`, and `chupa/runner.py:78` sets `asyncio.sleep` as the production default for the `sleep` it passes to the daemon, driver, thresh, timers, watcher and watchdog.

The gap the note describes is closed. One place now supplies the production `Sleep` seam: the session runner's default. Every engine consumer receives it as an injected `Sleep` and does not call `asyncio.sleep` itself. The note shows no wrong runtime behavior, so there is nothing to build.

- chupa/seams.py:16 `Sleep = Callable[[float], Awaitable[None]]`
- chupa/runner.py:78 `sleep: Sleep = asyncio.sleep` is the production default
- chupa/daemon.py:173, chupa/driver.py:135, chupa/thresh.py:117, chupa/timers.py:55, chupa/watcher.py:26, chupa/watchdog.py:148 all take `sleep: Sleep` as an injected parameter
- No direct `asyncio.sleep` call in engine modules other than the runner default

Message: box-000046-340e80a7
