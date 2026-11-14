# Running chupa on a host

From the host checkout root, with chupa [installed](host-contract.md#install) and `config.yaml` set up as in the [host contract](host-contract.md), run:

```sh
uv run chupa doctor
uv run chupa serve
```

Use the same prefix for the other verbs below. The host checkout remains the working directory; `--config PATH` before the verb selects a different config. `serve` is the normal mode: it runs until `kill`, `stop`, or Ctrl-C. `drain` is a finite run to quiescence. Closing its terminal, SIGTERM, or Ctrl-C ends it as `kill` does. Serve stops on SIGHUP as it does on Ctrl-C: an unjournaled stop that the next start reconciles. A running serve picks up config edits and new ticket files live. Drafts written by Author wait for `confirm`.

| Verb | Works while serve runs? | What it does |
|---|---|---|
| `watch` | Yes | Show the live text view; `--once` prints one view. |
| `snapshot` | Yes | Print the extension snapshot as JSON. |
| `status` | Yes | Show the journal projection. |
| `stats` | Yes | Show the read-only health and efficiency projection. |
| `lint` | Yes | Validate tickets without writing. |
| `retro` | Yes | Run a retro report now, or queue one on the running engine (serve accepts it but does not yet run it). |
| `doctor` | No | Inspect setup; its lock probe reports a held lock as a failure. |
| `prompt` | Yes | Render an operator prompt for a ticket, named box IDs, or all committed drafts without writing state. |
| `core` | Yes | Refresh managed conduct files. |
| `probe` | Yes | Probe declared providers and models. |
| `docs` | Yes | Print the installed host guide paths and their purposes. |
| `migrate-config` | Yes | Validate and migrate an older config. |
| `pause` | Yes | Ask the running engine to pause admission. |
| `resume` | Yes | Ask the running engine to release its current hold. |
| `kill` | Yes | Ask the running engine to stop at a safe point. |
| `stop` | Yes | Finish active work and exit. |
| `review` | Yes | Only the named ticket's pending edits are committed through intake before reviewing the committed ticket. |
| `suggest` | Yes | File an idea into the Suggestion Box. |
| `triage` | No | Make one pass over named pending box IDs, or all pending messages. |
| `dismiss` | No | Dismiss named box IDs without a model call. |
| `covmap` | Yes | Runs `review.coverage_map.argv` and writes `<state_dir>/coverage-map.json`; exits 0 on success or 2 on refusal. |
| `covgate` | Yes | Run a unit command and check its coverage report. |
| `new` | Yes | Create and lint a ticket skeleton. |
| `order` | Yes | Validate and edit a ticket's priority or runs-before ordering. |
| `run` | No | Intake the named ticket and run it through the pipeline; other pending tickets are left untouched. |
| `confirm` | Yes | Intake the named ticket, then apply or publish a keep verdict after interactive confirmation; other pending tickets are left untouched. |
| `reject` | Yes | Intake the named ticket, then apply or publish a reject verdict after interactive confirmation; other pending tickets are left untouched. |
| `drain` | No | Run eligible tickets to quiescence. `--detach` runs in its own session, surviving terminal or editor closing, and appends output to `<state_dir>/drain.out`. |
| `serve` | No | Run the continuous daemon. |

Stop serve before `triage`, `dismiss`, `run`, `drain`, or another `serve`: each takes the writer lock outright and refuses while it is held. `doctor` also needs the lock available to pass its probe. There is one writer per host; the kernel releases its lock when the holder exits. Never delete `chupa.lock`—wait for or stop the holder instead.
