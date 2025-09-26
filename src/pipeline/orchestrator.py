"""Main pipeline orchestrator."""
from typing import Optional
from ..core.config import Config
from ..scrapers.fighters.scraper import FighterScraper, FighterDetailScraper
from ..scrapers.events.scraper import EventScraper
from ..scrapers.fights.scraper import FightScraper, FightDetailScraper
from ..utils.data import CSVManager
from ..core.constants import FIGHTER_FIELDS, EVENT_FIELDS, FIGHT_FIELDS, FIGHTER_DETAIL_FIELDS


class UFCScrapingOrchestrator:
    """Orchestrates the entire UFC scraping pipeline."""
    
    def __init__(self, dev_mode: Optional[bool] = None, dev_limit: Optional[int] = None):
        self.config = Config(dev_mode=dev_mode, dev_limit=dev_limit)
        self.csv_manager = CSVManager()
    
    def run_full_pipeline(self):
        """Run the complete scraping pipeline."""
        print("🚀 Starting UFC Stats scraping pipeline...")
        print(f"Mode: {'Development' if self.config.scraping.dev_mode else 'Production'}")
        if self.config.scraping.dev_mode:
            print(f"Limit: {self.config.scraping.dev_limit}")
        
        # Phase 1: Fighters
        print("\n" + "="*50)
        print("PHASE 1: FIGHTERS")
        print("="*50)
        self._scrape_fighters()
        
        # Phase 2: Events
        print("\n" + "="*50)
        print("PHASE 2: EVENTS")
        print("="*50)
        self._scrape_events()
        
        # Phase 3: Fighter Details
        print("\n" + "="*50)
        print("PHASE 3: FIGHTER DETAILS")
        print("="*50)
        self._scrape_fighter_details()
        
        # Phase 4: Fight Index
        print("\n" + "="*50)
        print("PHASE 4: FIGHT INDEX")
        print("="*50)
        self._scrape_fights_index()
        
        # Phase 5: Fight Details
        print("\n" + "="*50)
        print("PHASE 5: FIGHT DETAILS")
        print("="*50)
        self._scrape_fight_details()
        
        print("\n🎉 Pipeline completed successfully!")
    
    def _scrape_fighters(self):
        """Scrape basic fighter information."""
        scraper = FighterScraper(self.config)
        fighters = scraper.scrape()
        
        all_fields = FIGHTER_FIELDS + FIGHTER_DETAIL_FIELDS
        self.csv_manager.save_to_csv(
            fighters, 
            self.config.data.fighters_path, 
            all_fields
        )
        print(f"💾 Saved {len(fighters)} fighters to {self.config.data.fighters_path}")
    
    def _scrape_events(self):
        """Scrape event information."""
        scraper = EventScraper(self.config)
        events = scraper.scrape()
        
        self.csv_manager.save_to_csv(
            events, 
            self.config.data.events_path, 
            EVENT_FIELDS
        )
        print(f"💾 Saved {len(events)} events to {self.config.data.events_path}")
    
    def _scrape_fighter_details(self):
        """Scrape detailed fighter information."""
        # Load existing fighters
        fighters = self.csv_manager.read_from_csv(self.config.data.fighters_path)
        
        # Scrape details
        scraper = FighterDetailScraper(self.config)
        updated_fighters = scraper.scrape(fighters)
        
        # Save updated data
        all_fields = FIGHTER_FIELDS + FIGHTER_DETAIL_FIELDS
        self.csv_manager.save_to_csv(
            updated_fighters, 
            self.config.data.fighters_path, 
            all_fields
        )
        print(f"💾 Updated fighter details in {self.config.data.fighters_path}")
    
    def _scrape_fights_index(self):
        """Scrape fight index from events."""
        # Load existing events
        events = self.csv_manager.read_from_csv(self.config.data.events_path)
        
        # Scrape fight index
        scraper = FightScraper(self.config)
        fights = scraper.scrape_fight_index(events)
        
        # Save fight index
        index_fields = ['event_id', 'fight_id', 'fight_order']
        self.csv_manager.save_to_csv(
            fights, 
            self.config.data.fights_path, 
            index_fields
        )
        print(f"💾 Saved {len(fights)} fight records to {self.config.data.fights_path}")
    
    def _scrape_fight_details(self):
        """Scrape detailed fight information."""
        # Load fight index
        fights = self.csv_manager.read_from_csv(self.config.data.fights_path)
        
        # Scrape fight details
        scraper = FightDetailScraper(self.config)
        detailed_fights = scraper.scrape(fights)
        
        # Save detailed fight data
        self.csv_manager.save_to_csv(
            detailed_fights, 
            self.config.data.fights_path, 
            FIGHT_FIELDS
        )
        print(f"💾 Updated fight details in {self.config.data.fights_path}")