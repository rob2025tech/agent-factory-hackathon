# Keep / Replace / Remove

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