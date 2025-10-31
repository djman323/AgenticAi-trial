from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Context:
    """Holds runtime context for each agent session."""
    user_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
