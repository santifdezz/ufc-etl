"""Configuration management for UFC scraper."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScrapingConfig:
    """Configuration for scraping parameters."""
    max_workers: int = 5
    delay_seconds: float = 3.0
    dev_mode: bool = False
    dev_limit: int = 20
    headers: dict = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }


@dataclass
class DataConfig:
    """Configuration for data paths."""
    base_dir: str = 'data'
    test_dir: str = 'data/tests'
    
    @property
    def fighters_path(self) -> str:
        return os.path.join(self.base_dir, 'raw','raw_fighters.csv')
    
    @property
    def events_path(self) -> str:
        return os.path.join(self.base_dir, 'raw','raw_events.csv')

    @property
    def fights_path(self) -> str:
        return os.path.join(self.base_dir, 'raw','raw_fights.csv')


class Config:
    """Main configuration class."""
    
    def __init__(self, dev_mode: Optional[bool] = None, dev_limit: Optional[int] = None):
        self.scraping = ScrapingConfig(
            dev_mode=dev_mode or False,
            dev_limit=dev_limit or 20
        )
        self.data = DataConfig()
        
        # Ensure directories exist
        os.makedirs(self.data.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data.base_dir, 'raw'), exist_ok=True)
        os.makedirs(self.data.test_dir, exist_ok=True)