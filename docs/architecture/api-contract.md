# Backend API Contract

> **Status: Stale (tagged 2026-08-31).** This document describes
> endpoints that were planned but never implemented (`/api/chat`,
> `/api/providers`, `/api/models`, `/api/history`, `/api/costs`,
> `/api/settings`). The implemented API contract lives in
> `apps/api/models/` and is documented in `architecture.md` §4.
> Do not implement against this document without an explicit decision.

## Health

GET /health

Response

```json
{
  "status": "ok"
}
```

---

## Chat

POST /api/chat

Request

```json
{
  "provider": "openai",
  "model": "gpt-5",
  "prompt": "Explain AI agents."
}
```

Response

```json
{
  "response": "..."
}
```

---

## Providers

GET /api/providers

Response

```json
[
  {
    "name": "OpenAI",
    "enabled": true
  }
]
```

---

## Models

GET /api/models

Response

```json
[
  {
    "provider": "OpenAI",
    "model": "gpt-5",
    "input_price": 2.50,
    "output_price": 10.00
  }
]
```

---

## History

GET /api/history

Returns previous requests.

---

## Costs

GET /api/costs

Returns aggregated spend and token usage.

---

## Settings

GET /api/settings

Returns masked provider configuration.