# Review: snag

The transport works on the success path, but a delivery that keeps failing is retried on every 0.1s serve poll, and each retry writes a new EFFECT_INTENT to the journal and can block maintenance for up to 30s per escalation.

## Findings

- [logic] chupa/serve.py:312 maintenance() now calls reconcile_notifications() on every poll (SERVE_POLL_S = 0.1). Effects.run writes an EFFECT_INTENT before each delivery attempt and records nothing on failure. So a notify command that keeps exiting non-zero, or is missing, adds about 10 intent events per second per pending escalation to the journal, with no limit, plus a notify_failed engine-log line each time. That breaks the rule that the journal is the record, never a debug log. Each poll also reloads config.yaml and re-reads the whole journal. (do instead: Limit retries of a failed key: retry pending keys at startup and only when the journal or config changes, or track failed keys for this serve lifetime with a clock-seam backoff. A persistent failure must not write a new intent on every poll; keep the startup and restart replay that the tests prove.)
- [logic] chupa/notify.py:40 Each send awaits the notify command inline, with a timeout of NOTIFY_TIMEOUT_S (30s), one escalation after another, inside Serve.maintenance. A hung notify command therefore stalls the serve loop for 30s times the number of pending escalations on every poll. During that time control.poll() kill requests, timers, sweep_orphans, the Box recover/checkpoint step and heartbeat.cycle() do not run. Startup recovery is also held for the same length of time before the ready flag is set. (do instead: Don't let notification delivery block the maintenance cadence: bound each poll's delivery attempts and skip keys whose last attempt timed out until a backoff expires, so control and heartbeat processing keep running while a notify command hangs.)

## Record

```json
{
  "artifact_schema_version": 1,
  "produced_by_spec_version": 1,
  "produced_at_sha": "80001844790080873f5e70b417dc0ababe2650db",
  "stem": "notify-transport",
  "reviewed_sha": "80001844790080873f5e70b417dc0ababe2650db",
  "summary": "The transport works on the success path, but a delivery that keeps failing is retried on every 0.1s serve poll, and each retry writes a new EFFECT_INTENT to the journal and can block maintenance for up to 30s per escalation.",
  "findings": [
    {
      "code": "logic",
      "path": "chupa/serve.py",
      "line": 312,
      "message": "maintenance() now calls reconcile_notifications() on every poll (SERVE_POLL_S = 0.1). Effects.run writes an EFFECT_INTENT before each delivery attempt and records nothing on failure. So a notify command that keeps exiting non-zero, or is missing, adds about 10 intent events per second per pending escalation to the journal, with no limit, plus a notify_failed engine-log line each time. That breaks the rule that the journal is the record, never a debug log. Each poll also reloads config.yaml and re-reads the whole journal.",
      "paved_road": "Limit retries of a failed key: retry pending keys at startup and only when the journal or config changes, or track failed keys for this serve lifetime with a clock-seam backoff. A persistent failure must not write a new intent on every poll; keep the startup and restart replay that the tests prove.",
      "kind": null,
      "unit": null
    },
    {
      "code": "logic",
      "path": "chupa/notify.py",
      "line": 40,
      "message": "Each send awaits the notify command inline, with a timeout of NOTIFY_TIMEOUT_S (30s), one escalation after another, inside Serve.maintenance. A hung notify command therefore stalls the serve loop for 30s times the number of pending escalations on every poll. During that time control.poll() kill requests, timers, sweep_orphans, the Box recover/checkpoint step and heartbeat.cycle() do not run. Startup recovery is also held for the same length of time before the ready flag is set.",
      "paved_road": "Don't let notification delivery block the maintenance cadence: bound each poll's delivery attempts and skip keys whose last attempt timed out until a backoff expires, so control and heartbeat processing keep running while a notify command hangs.",
      "kind": null,
      "unit": null
    }
  ],
  "spec_version": "1.0",
  "provider": "claude",
  "model": "claude-opus-5-5",
  "verdict": "snag"
}
```
