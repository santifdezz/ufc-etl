"""Event data models."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """Event data model."""
    event_id: str
    name: str
    date: Optional[str] = None
    location: Optional[str] = None
    status: str = 'completed'
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})