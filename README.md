# chupa

chupa runs tickets against a git repository: Implement writes the change on a branch, Check runs
mechanical gates, Review has a model judge the diff, and Merge squashes it onto `main`. Failures
are harvested, diagnosed, retried within caps, or held for a human. chupa develops itself: this
repo is both the engine and its first host.

[Install chupa](docs/host-contract.md#install), then run `uv run chupa <verb>`.

## Docs

- `docs/how-chupa-works.md`: how chupa behaves today. Tickets keep it current.
- `docs/host-contract.md`: the config schema and host-facing contract.
- `docs/host-authoring.md`: what to write in a ticket.

`CHUPA_PLAN.md` is the frozen record of how chupa was first built. It is history, not a reference.

## Commands

In this repo, use `./dev.py`:

    ./dev.py new STEM [--kind feature|bug|chore]   # write a ticket skeleton
    ./dev.py lint [STEM...]                         # check tickets
    ./dev.py review STEM...                       # review tickets against merged code
    ./dev.py drain                                  # run every eligible ticket to quiescence
    ./dev.py status                                 # what ran, what is held, total spend
    ./dev.py confirm STEM / ./dev.py reject STEM    # keep or kill a held ticket
    ./dev.py kill                                   # stop a running drain
    ./dev.py test [args]                            # run the test suite

Every chupa verb is listed in `docs/how-chupa-works.md` section 2.
