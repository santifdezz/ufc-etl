"""Integration tests for scrapers."""
import pytest
from src.core.config import Config
from src.scrapers.fighters.scraper import FighterScraper
from src.scrapers.events.scraper import EventScraper


class TestFighterScraper:
    """Test fighter scraper integration."""
    
    def setup_method(self):
        self.config = Config(dev_mode=True, dev_limit=5)
        self.scraper = FighterScraper(self.config)
    
    @pytest.mark.integration
    def test_scrape_fighters_dev_mode(self):
        """Test scraping fighters in dev mode."""
        fighters = self.scraper.scrape()
        
        assert len(fighters) <= self.config.scraping.dev_limit
        assert all('fighter_id' in f for f in fighters)
        assert all(f['fighter_id'] for f in fighters)


class TestEventScraper:
    """Test event scraper integration."""
    
    def setup_method(self):
        self.config = Config(dev_mode=True, dev_limit=5)
        self.scraper = EventScraper(self.config)
    
    @pytest.mark.integration
    def test_scrape_events_dev_mode(self):
        """Test scraping events in dev mode."""
        events = self.scraper.scrape()
        
        assert len(events) <= self.config.scraping.dev_limit
        assert all('event_id' in e for e in events)
        assert all('name' in e for e in events)