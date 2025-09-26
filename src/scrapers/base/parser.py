"""Base parser class."""
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from ...utils.http import clean_text, extract_id_from_url


class BaseParser(ABC):
    """Base class for all parsers."""
    
    def normalize_field(self, value: Any) -> Optional[str]:
        """Normalize field value."""
        if value is None:
            return None
        
        value = str(value).strip()
        if not value or value in ['--', 'null', 'None']:
            return None
        
        return value
    
    def safe_find_text(self, element: BeautifulSoup, selector: str, 
                      attribute: str = None, default: str = "") -> str:
        """Safely find text in element."""
        if not element:
            return default
        
        found = element.select_one(selector)
        if not found:
            return default
        
        if attribute:
            return found.get(attribute, default).strip()
        else:
            return clean_text(found.get_text())
    
    def extract_winner_from_status(self, persons: List[BeautifulSoup]) -> tuple:
        """Extract winner information from person status indicators."""
        winner_name = None
        winner_id = None
        
        if len(persons) >= 2:
            f1_status = persons[0].find('i', class_='b-fight-details__person-status')
            f2_status = persons[1].find('i', class_='b-fight-details__person-status')
            
            # Check for green status (winner)
            if f1_status and 'green' in ' '.join(f1_status.get('class', [])):
                name_elem = persons[0].find('h3', class_='b-fight-details__person-name')
                if name_elem and name_elem.a:
                    winner_name = name_elem.a.text.strip()
                    winner_id = extract_id_from_url(name_elem.a.get('href', ''))
            elif f2_status and 'green' in ' '.join(f2_status.get('class', [])):
                name_elem = persons[1].find('h3', class_='b-fight-details__person-name')
                if name_elem and name_elem.a:
                    winner_name = name_elem.a.text.strip()
                    winner_id = extract_id_from_url(name_elem.a.get('href', ''))
        
        return winner_name, winner_id