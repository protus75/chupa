---
state: confirmed
source: human
priority: P2
kind: feature
---

## Goal / Why
Log failed HTTP requests so developers can identify the method, endpoint, and failure type without exposing request credentials.

## Scope in / Scope out
Add warning logs for HTTP error responses and transport errors in the client. Preserve the response and exception behavior. Do not add request tracing or change retry behavior.

## Scope fence
- `http_client.py`
- `tests/test_http_client.py`

## Acceptance criteria
1. Each HTTP error response or transport error produces one warning with the method, URL path, status code when available, and exception class.
2. Successful requests produce no warning.
3. The client forwards request options and re-raises the original exception on failure.
4. Warnings contain no URL query values, request headers, request body, or exception message.

## Verification
`python -m pytest tests/test_http_client.py -q`
