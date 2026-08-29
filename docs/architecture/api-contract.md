# Backend API Contract

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