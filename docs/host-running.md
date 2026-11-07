# Running chupa on a host

From the host checkout root, with `config.yaml` set up as in the [host contract](host-contract.md), point `CHUPA_CHECKOUT` at the absolute path to a chupa checkout and run:

```sh
CHUPA_CHECKOUT=/absolute/path/to/chupa
PYTHONPATH="$CHUPA_CHECKOUT" uv run --project "$CHUPA_CHECKOUT" python -m chupa doctor
PYTHONPATH="$CHUPA_CHECKOUT" uv run --project "$CHUPA_CHECKOUT" python -m chupa serve
```

Use the same prefix for the other verbs below. The host checkout remains the working directory; `--config PATH` before the verb selects a different config. `serve` is the normal mode: it runs until `kill`, `stop`, or Ctrl-C. `drain` is a finite run to quiescence. A running serve picks up config edits and new ticket files live. Drafts written by Author wait for `confirm`.

| Verb | Works while serve runs? | What it does |
|---|---|---|
| `status` | Yes | Show the journal projection. |
| `stats` | Yes | Show the read-only health and efficiency projection. |
| `lint` | Yes | Validate tickets without writing. |
| `retro` | No | Force a retro report. |
| `doctor` | No | Inspect setup; its lock probe reports a held lock as a failure. |
| `prompt` | Yes | Render an operator prompt for a ticket without writing state. |
| `core` | Yes | Refresh managed conduct files. |
| `migrate-config` | Yes | Validate and migrate an older config. |
| `pause` | Yes | Ask the running engine to pause admission. |
| `resume` | Yes | Ask the running engine to release its current hold. |
| `kill` | Yes | Ask the running engine to stop at a safe point. |
| `stop` | Yes | Finish active work and exit. |
| `review` | No | Review a committed ticket. |
| `triage` | No | Make one pass over pending suggestions. |
| `covgate` | Yes | Run a unit command and check its coverage report. |
| `new` | Yes | Create and lint a ticket skeleton. |
| `order` | Yes | Validate and edit a ticket's priority or runs-before ordering. |
| `run` | No | Run one ticket through the pipeline. |
| `confirm` | Yes | After interactive confirmation, publish a keep verdict to serve. |
| `reject` | Yes | After interactive confirmation, publish a reject verdict to serve. |
| `drain` | No | Run eligible tickets to quiescence. |
| `serve` | No | Run the continuous daemon. |

Stop serve before `retro`, `review`, `triage`, `run`, `drain`, or another `serve`: each takes the writer lock outright and refuses while it is held. `doctor` also needs the lock available to pass its probe. There is one writer per host; the kernel releases its lock when the holder exits. Never delete `chupa.lock`—wait for or stop the holder instead.
