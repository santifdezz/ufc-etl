"""Event parser implementation."""
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from ..base.parser import BaseParser
from ...utils.http import extract_id_from_url, clean_text


class EventParser(BaseParser):
    """Parser for event data."""
    
    def parse_events_table(self, soup: BeautifulSoup, event_type: str) -> List[Dict[str, Any]]:
        """Parse events table from soup."""
        events = []
        events_table = soup.find('table', class_='b-statistics__table-events')
        
        if not events_table:
            return events
        
        rows = events_table.find_all('tr')[1:]  # Skip header

        for row in rows:
            # Skip rows with the class 'b-statistics__table-row_type_first'
            if 'b-statistics__table-row_type_first' in row.get('class', []):
                continue
            event_data = self._extract_event_data(row, event_type)
            if event_data:
                events.append(event_data)
        
        return events
    
    def _extract_event_data(self, event_row: BeautifulSoup, event_type: str) -> Dict[str, Any]:
        """Extract data from a single event row."""
        try:
            cells = event_row.find_all('td')
            if len(cells) < 2:
                return None
            
            # First cell: name, link, and date
            content = cells[0].find('i', class_='b-statistics__table-content')
            if not content:
                return None
            
            link_tag = content.find('a', href=True)
            date_tag = content.find('span', class_='b-statistics__date')
            
            if not link_tag or not date_tag:
                return None
            
            # Extract data
            event_url = link_tag['href']
            event_id = extract_id_from_url(event_url)
            name = clean_text(link_tag.get_text())
            date = clean_text(date_tag.get_text())
            
            # Second cell: location
            location = clean_text(cells[1].get_text())
            
            return {
                'event_id': event_id,
                'name': name,
                'date': date,
                'location': location,
                'status': event_type
            }
            
        except Exception as e:
            print(f"Error extracting event data: {e}")
            return None