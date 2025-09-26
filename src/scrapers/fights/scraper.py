"""Fight scraper implementation."""
from typing import List, Dict, Any
from ..base.scraper import BaseScraper
from .parser import FightParser
from ...core.constants import EVENT_URL, FIGHT_URL
from ...utils.concurrent import concurrent_map_with_progress


class FightScraper(BaseScraper):
    """Scraper for fight index data."""
    
    def __init__(self, config):
        super().__init__(config)
        self.parser = FightParser()
    
    def scrape(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self.scrape_fight_index(events)

    def scrape_fight_index(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scrape fight index from events."""
        print("⚔️ Scraping fight index from events...")
        
        events = self._apply_dev_limit(events)
        
        def process_event(event_data: Dict[str, Any], idx: int = None) -> List[Dict[str, Any]]:
            event_id = event_data.get('event_id')
            if not event_id:
                return []
            
            url = f"{EVENT_URL}/{event_id}"
            event_name = event_data.get('name', '')
            
            try:
                soup = self.http_client.get_soup(url)
                if soup:
                    fights = self.parser.parse_event_fights(soup, event_id)
                    if idx is not None:
                        print(f"Event {event_id} ({event_name}): {len(fights)} fights ({idx+1}/{len(events)})")
                    return fights
                else:
                    print(f"Failed to fetch event {event_id}")
                    return []
                    
            except Exception as e:
                print(f"Error processing event {event_id}: {e}")
                return []
        
        # Use concurrent processing
        all_fights_nested = concurrent_map_with_progress(
            process_event,
            events,
            max_workers=self.config.scraping.max_workers,
            progress_callback=self._progress_callback
        )
        
        # Flatten results and remove duplicates
        all_fights = []
        for fights_list in all_fights_nested:
            if fights_list:
                all_fights.extend(fights_list)
        
        # Remove duplicates by fight_id
        unique_fights = {}
        for fight in all_fights:
            fight_id = fight.get('fight_id')
            if fight_id and fight_id not in unique_fights:
                unique_fights[fight_id] = fight
        
        deduplicated_fights = list(unique_fights.values())
        print(f"✅ Total fights extracted (without duplicates): {len(deduplicated_fights)}")
        
        return deduplicated_fights


class FightDetailScraper(BaseScraper):
    """Scraper for detailed fight information."""
    
    def __init__(self, config):
        super().__init__(config)
        self.parser = FightParser()
    
    def scrape(self, fights_index: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scrape detailed fight information."""
        print("🥊 Scraping detailed fight information...")
        
        fights_index = self._apply_dev_limit(fights_index)
        
        def process_fight(fight_data: Dict[str, Any], idx: int = None) -> Dict[str, Any]:
            fight_id = fight_data.get('fight_id')
            if not fight_id:
                return fight_data
            
            url = f"{FIGHT_URL}/{fight_id}"
            
            try:
                html = self.http_client.get_html(url)
                fight_details = self.parser.parse_fight_details(html)
                
                # Merge with index data, preserving index fields
                merged_fight = {**fight_details, **fight_data}
                
                # Ensure fight_id and event_id are from index
                merged_fight['fight_id'] = fight_data['fight_id']
                merged_fight['event_id'] = fight_data['event_id']
                if 'fight_order' in fight_data:
                    merged_fight['fight_order'] = fight_data['fight_order']
                
                if idx is not None:
                    print(f"Processed fight {fight_id} ({idx+1}/{len(fights_index)})")
                
                return merged_fight
                
            except Exception as e:
                print(f"Error processing fight {fight_id}: {e}")
                return fight_data
        
        # Use concurrent processing with progress
        detailed_fights = concurrent_map_with_progress(
            process_fight,
            fights_index,
            max_workers=self.config.scraping.max_workers,
            progress_callback=self._progress_callback
        )
        
        print(f"✅ Fight details scraped: {len(detailed_fights)}")
        return detailed_fights