"""Base scraper class."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ...core.config import Config
from ...utils.http import HTTPClient
from ...utils.concurrent import concurrent_map_with_progress


class BaseScraper(ABC):
    """Base class for all scrapers."""
    
    def __init__(self, config: Config):
        self.config = config
        self.http_client = HTTPClient(
            headers=config.scraping.headers,
            delay=config.scraping.delay_seconds
        )
    
    @abstractmethod
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """Main scraping method to be implemented by subclasses."""
        pass
    
    def _apply_dev_limit(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply development mode limits."""
        if self.config.scraping.dev_mode and self.config.scraping.dev_limit:
            return data[:self.config.scraping.dev_limit]
        return data
    
    def _progress_callback(self, completed: int, total: int):
        """Default progress callback."""
        print(f"Progress: {completed}/{total} ({completed/total*100:.1f}%)")