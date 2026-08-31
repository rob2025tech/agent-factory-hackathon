# Keep / Replace / Remove

> **Status: Historical — contains an open contradiction (tagged
> 2026-08-31).** "Execution Service: Keep" conflicts with the current
> treatment of the legacy pipeline as unwired and frozen
> (`architecture.md` §9 and §13). The disposition of the legacy
> Execution Service is an open decision; do not act on this table
> until it is resolved.

## Keep

| Component | Reason |
|----------|--------|
| FastAPI | Backend foundation |
| Provider Registry | Single source of truth |
| ButterbaseClient | Provider implementation |
| CerebrasAdapter | Provider implementation |
| Ollama Adapter | Provider implementation |
| Execution Service | Business logic |
| Tests | Existing coverage |

---

## Reuse

| Component | Source |
|----------|--------|
| Playground UI | Genspark |
| Model Selector UI | Genspark |
| Provider Dashboard UI | Genspark |
| Cost Dashboard UI | Genspark |
| Request History UI | Genspark |
| Settings UI | Genspark |

---

## Remove Eventually

| Component | Reason |
|----------|--------|
| TypeScript Provider Registry | Duplicate |
| TypeScript Adapter Factory | Duplicate |
| OpenAICompatibleAdapter.ts | Duplicate |
| AnthropicAdapter.ts | Duplicate |
| GoogleAdapter.ts | Duplicate |
| TokenRouterAdapter.ts | Duplicate |

These components should disappear after the frontend communicates exclusively with the FastAPI backend.