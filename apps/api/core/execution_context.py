from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionContext:
    """
    Shared context for a single agent execution.

    Keeps request-scoped metadata together so services do not need to
    repeatedly pass individual values such as user_id, session_id,
    model, or routing preferences.
    """

    user_id: str | None = None
    agent_id: str | None = None
    session_id: str | None = None
    conversation_id: str | None = None

    model: str | None = None
    provider: str | None = None

    task: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_metadata(self, **values: Any) -> "ExecutionContext":
        """
        Return a new context with additional metadata.

        Existing metadata is preserved and values supplied here take
        precedence when keys overlap.
        """
        merged = dict(self.metadata)
        merged.update(values)

        return ExecutionContext(
            user_id=self.user_id,
            agent_id=self.agent_id,
            session_id=self.session_id,
            conversation_id=self.conversation_id,
            model=self.model,
            provider=self.provider,
            task=self.task,
            metadata=merged,
        )

    def set_routing(
        self,
        *,
        model: str | None = None,
        provider: str | None = None,
    ) -> "ExecutionContext":
        """
        Return a new context containing the selected model/provider.
        """
        return ExecutionContext(
            user_id=self.user_id,
            agent_id=self.agent_id,
            session_id=self.session_id,
            conversation_id=self.conversation_id,
            model=model if model is not None else self.model,
            provider=provider if provider is not None else self.provider,
            task=self.task,
            metadata=dict(self.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the context to a JSON-friendly dictionary.
        """
        return {
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "conversation_id": self.conversation_id,
            "model": self.model,
            "provider": self.provider,
            "task": self.task,
            "metadata": dict(self.metadata),
        }