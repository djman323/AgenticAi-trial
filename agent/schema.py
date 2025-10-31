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
