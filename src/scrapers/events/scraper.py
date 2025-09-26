"""Event scraper implementation."""
from typing import List, Dict, Any
from ..base.scraper import BaseScraper
from .parser import EventParser
from ...core.constants import EVENTS_COMPLETED_URL, EVENTS_UPCOMING_URL


class EventScraper(BaseScraper):
    """Scraper for event data."""
    
    def __init__(self, config):
        super().__init__(config)
        self.parser = EventParser()
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape all events (completed and upcoming)."""
        print("🎪 Scraping events...")
        
        # Scrape completed events
        completed_events = self._scrape_events_from_url(
            f"{EVENTS_COMPLETED_URL}?page=all", 
            "completed"
        )
        
        # Apply dev limit if in dev mode
        if self.config.scraping.dev_mode and self.config.scraping.dev_limit:
            completed_events = completed_events[:self.config.scraping.dev_limit]
            print(f"✅ Total events scraped (dev mode): {len(completed_events)}")
            return completed_events
        
        # Add delay between requests
        self.http_client.delay_request()
        
        # Scrape upcoming events
        upcoming_events = self._scrape_events_from_url(
            f"{EVENTS_UPCOMING_URL}?page=all", 
            "upcoming"
        )
        
        all_events = completed_events + upcoming_events
        print(f"✅ Total events scraped: {len(all_events)} (Completed: {len(completed_events)}, Upcoming: {len(upcoming_events)})")
        
        return all_events
    
    def _scrape_events_from_url(self, url: str, event_type: str) -> List[Dict[str, Any]]:
        """Scrape events from a specific URL."""
        print(f"Scraping {event_type} events...")
        
        soup = self.http_client.get_soup(url)
        if not soup:
            print(f"Error accessing {event_type} events")
            return []
        
        events = self.parser.parse_events_table(soup, event_type)
        print(f"Found {len(events)} {event_type} events")
        
        return events