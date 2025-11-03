from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Context:
    """Context schema for runtime sessions."""
    user_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class ResponseFormat:
    """Defines structured responses from the agent."""
    action: str
    explanation: str
    file_modified: str | None = None

    def __str__(self) -> str:
        """Return the response as plain text (no '=' signs, just normal text).

        Format:
        - first line(s): action (as provided)
        - then a blank line
        - explanation
        - then a blank line (if file_modified present)
        - file_modified (if present)
        """
        parts: list[str] = []
        # Keep provided text as-is (strip only surrounding whitespace)
        if self.action is not None:
            parts.append(self.action.strip())

        if self.explanation is not None:
            parts.append(self.explanation.strip())

        if self.file_modified:
            parts.append(self.file_modified.strip())

        # Join with a blank line between sections to keep readability
        return "\n\n".join(parts)
