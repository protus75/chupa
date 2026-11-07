---
id: tombstone-box-000059-07864ba4
kind: tombstone
link: declined-box-000039-af7f01a0
reopen_after_days: 90
---
A bootstrap note points out that the CLI provider adapter writes its own scrubbed stdin prompt file under `spools/providers/<stem>/<provider>-NNNN/`, because `LLMRequest` carries no spool path. The frozen plan says the driver's spooled prompt file is the stdin channel. The note proposes passing the driver's prompt path to the adapter and moving the adapter's event-stream and stderr capture from a per-client sequence directory into the per-attempt spool directory.

The note says itself that it has the same root cause as the driver `prompt_path` suggestion. Registry record 000039 already declined that suggestion because the adapter writes its own spool file, so no `prompt_path` field is needed. Moving the event-stream and stderr capture into the per-attempt directory is a layout refactor of that same design. The note shows no lost, misattributed or unscrubbed capture, and no failed run caused by the current layout. The only gap it shows is a mismatch with the frozen plan's wording, and the plan is not edited.

- The message says: 'Same root cause as the [driver] `prompt_path` suggestion'
- declined-box-000039-af7f01a0 declined `LLMRequest.prompt_path` because the adapter now writes its own spool file
- The message says the adapter's prompt file is already scrubbed, so it reports no secret leak
- No open or merged ticket reports a run that failed or lost evidence because provider capture is kept per client sequence

Message: box-000059-07864ba4
