"""Fighter data models."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Fighter:
    """Fighter data model."""
    fighter_id: str
    first: Optional[str] = None
    last: Optional[str] = None
    nickname: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    reach: Optional[str] = None
    stance: Optional[str] = None
    wins: Optional[str] = None
    losses: Optional[str] = None
    defeats: Optional[str] = None
    belt: Optional[bool] = None
    
    # Detailed stats
    dob: Optional[str] = None
    slpm: Optional[str] = None
    str_acc: Optional[str] = None
    sapm: Optional[str] = None
    str_def: Optional[str] = None
    td_avg: Optional[str] = None
    td_acc: Optional[str] = None
    td_def: Optional[str] = None
    sub_avg: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Fighter':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})