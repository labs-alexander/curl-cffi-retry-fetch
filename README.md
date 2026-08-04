# curl-cffi-retry-fetch

A fetch function built around resilience (retry).

## What it is

I built this thinking about resilience (retry). It's meant for general use, meaning it works for practically any HTTP request.

It's not a generic retry wrapper for the sake of being generic. It's practical and solid specifically in the `get_session` and `create_session` functions, a retry built for this type of work. Not generalist, but built to work the right way for the job it's meant for.

## How it works

The `apply_retry` decorator wraps a fetch call and classifies whatever exception it raises:

- `RetryableError` (rate limits, server errors like 5xx) → logs a warning and retries with a linear backoff plus random jitter, to avoid multiple requests retrying at the exact same time.
- `BlockedError` (403, 401) → logs the block and retries, with a hook left in place to handle IP/session rotation on block (not wired in yet).
- `UnknownError` (any status code not mapped) → logs it and raises immediately, no point retrying blindly on something uncatalogued.
- `FatalError` (404, 410, 400, 451) → logs and raises immediately, since retrying won't fix a permanent failure like a dead endpoint or a legal block.

`classify_response` does the actual mapping from HTTP status code to exception type, using `STATUS_MAP` defined in `exceptions.py`.

## Structure

The project is split into two files: `fetch.py` (the retry logic and the request itself) and `exceptions.py` (the error types and the status code mapping).

## Example usage

```python
from fetch import fetch, create_session

session = create_session()
response = fetch("https://www.yoururl.com", session=session)
print(response.status_code)
```

## Limitations

Proxy rotation is not automated. This was intentional, the goal here was to demonstrate a solid retry/error-classification pattern, not a full scraping infrastructure. Proxy handling depends on the specific project and provider being used.
