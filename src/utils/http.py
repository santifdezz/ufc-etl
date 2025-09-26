"""HTTP utilities for scraping."""
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional
from ..core.exceptions import ScrapingError


class HTTPClient:
    """HTTP client for UFC scraping."""
    
    def __init__(self, headers: dict, delay: float = 3.0):
        self.headers = headers
        self.delay = delay
        self._session = requests.Session()
        self._session.headers.update(headers)
    
    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object for URL."""
        try:
            response = self._session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise ScrapingError(f"Failed to fetch {url}: {e}")
    
    def get_html(self, url: str) -> str:
        """Get raw HTML for URL."""
        try:
            response = self._session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ScrapingError(f"Failed to fetch {url}: {e}")
    
    def delay_request(self):
        """Add delay between requests."""
        time.sleep(self.delay)


def extract_id_from_url(url: str) -> str:
    """Extract ID from UFC stats URL."""
    if not url:
        return ""
    import re
    match = re.search(r'/([^/]+)$', url)
    return match.group(1) if match else ""


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    import re
    text = text.strip()
    text = re.sub(r'[\n\r\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text