# Repository Comparison

## Purpose

This document compares the two repositories:

- ai-agent-platform-starter
- genspark-ai-agent-platform-starter

The goal is to determine which components should become part of the long-term full-stack architecture.

---

## High-Level Comparison

| Area | ai-agent-platform-starter | genspark-ai-agent-platform-starter | Notes |
|------|----------------------------|------------------------------------|------|
| Backend | ✅ FastAPI | ❌ | Backend should remain here |
| Frontend | ❌ | ✅ Next.js | Candidate for migration |
| Provider Registry | ✅ | ✅ | Duplicate implementation |
| Adapter Pattern | ✅ | ✅ | Duplicate implementation |
| Playground | ❌ | ✅ | Candidate |
| Model Selector | ❌ | ✅ | Candidate |
| Provider Dashboard | ❌ | ✅ | Candidate |
| Cost Dashboard | ❌ | ✅ | Candidate |
| History | ❌ | ✅ | Candidate |
| Settings | ❌ | ✅ | Candidate |
| Tests | ✅ Pytest | ? | Verify |
| Documentation | ✅ | ✅ | Merge ideas |

---

## Conclusion

Current assessment:

- ai-agent-platform-starter should remain the backend foundation.
- genspark-ai-agent-platform-starter provides UI concepts worth migrating.