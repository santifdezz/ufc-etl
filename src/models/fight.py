"""Fight data models."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Fight:
    """Fight data model."""
    event_id: str
    fight_id: str
    fight_order: Optional[int] = None
    
    # Fighters
    fighter1_id: Optional[str] = None
    fighter1_name: Optional[str] = None
    fighter2_id: Optional[str] = None
    fighter2_name: Optional[str] = None
    winner_id: Optional[str] = None
    
    # Fight details
    weight_class: Optional[str] = None
    referee: Optional[str] = None
    round: Optional[str] = None
    time: Optional[str] = None
    time_format: Optional[str] = None
    method: Optional[str] = None
    details: Optional[str] = None
    bonus: Optional[str] = None
    
    # Statistics
    kd1: str = '0'
    kd2: str = '0'
    str1: str = '0'
    str2: str = '0'
    td1: str = '0'
    td2: str = '0'
    sub1: str = '0'
    sub2: str = '0'
    
    # Extended stats
    control_time1: Optional[str] = None
    control_time2: Optional[str] = None
    sig_head1: Optional[str] = None
    sig_head2: Optional[str] = None
    sig_body1: Optional[str] = None
    sig_body2: Optional[str] = None
    sig_leg1: Optional[str] = None
    sig_leg2: Optional[str] = None
    total_str1: Optional[str] = None
    total_str2: Optional[str] = None
    pass1: Optional[str] = None
    pass2: Optional[str] = None
    rev1: Optional[str] = None
    rev2: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Fight':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})