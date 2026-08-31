# Future Architecture

> **Status: Historical (tagged 2026-08-31).** Consolidation-era target
> architecture. It depicts the legacy Execution Service / Provider
> Adapter world; the implemented system moved to the AgentService and
> `providers/` architecture, documented in `architecture.md`.

```
                    Browser

                       │

                   Next.js UI

                       │

                 REST API (JSON)

                       │

                   FastAPI Backend

                       │

                Execution Service

                       │

                Provider Registry

                       │

              Provider Adapters

                       │

   OpenAI  Anthropic  Cerebras  Ollama  Butterbase
```

## Responsibilities

### Next.js

- User interface
- Forms
- Tables
- Dashboards
- Chat window

### FastAPI

- Authentication
- Routing
- Validation
- Logging
- Provider selection

### Registry

- Provider list
- Models
- Pricing
- Capabilities

### Adapters

- Translate generic requests into provider-specific APIs

### Providers

- External AI services