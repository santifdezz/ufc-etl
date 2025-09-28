"""
Implementación del scraper de eventos (Event) para el pipeline UFC ETL.
Incluye lógica para extraer eventos completados y próximos, y guardar los resultados en archivos CSV.
"""
from typing import List, Dict, Any
from ..base.scraper import BaseScraper
from .parser import EventParser
from ...core.constants import EVENTS_COMPLETED_URL, EVENTS_UPCOMING_URL


class EventScraper(BaseScraper):
    """
    Scraper especializado para la extracción de datos de eventos.
    Permite obtener eventos completados y próximos, y almacenarlos de forma estructurada.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.parser = EventParser()
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Extrae todos los eventos (completados y próximos) y guarda cada grupo en su archivo CSV correspondiente.
        Returns:
            List[Dict[str, Any]]: Lista combinada de eventos completados y próximos.
        """
        from ...core.constants import EVENT_FIELDS
        from ...utils.data import CSVManager
        import os
        print("🎪 Scraping events...")

        # Scrape completed events
        completed_events = self._scrape_events_from_url(
            f"{EVENTS_COMPLETED_URL}?page=all",
            "completed"
        )
        # Save completed events immediately
        events_path = self.config.data.events_path
        CSVManager.save_to_csv(completed_events, events_path, EVENT_FIELDS)
        print(f"💾 Saved {len(completed_events)} completed events to {events_path}")

        # Add delay between requests
        self.http_client.delay_request()

        # Scrape upcoming events
        upcoming_events = self._scrape_events_from_url(
            f"{EVENTS_UPCOMING_URL}?page=all",
            "upcoming"
        )
        # Save upcoming events immediately
        upcoming_path = events_path.replace('raw_events.csv', 'raw_upcoming.csv')
        CSVManager.save_to_csv(upcoming_events, upcoming_path, EVENT_FIELDS)
        print(f"💾 Saved {len(upcoming_events)} upcoming events to {upcoming_path}")

        all_events = completed_events + upcoming_events
        print(f"✅ Total events scraped: {len(all_events)} (Completed: {len(completed_events)}, Upcoming: {len(upcoming_events)})")
        return all_events
    
    def _scrape_events_from_url(self, url: str, event_type: str) -> List[Dict[str, Any]]:
        """
        Extrae eventos desde una URL específica, según el tipo de evento.
        Args:
            url (str): URL de la página de eventos.
            event_type (str): Tipo de evento (completado o próximo).
        Returns:
            List[Dict[str, Any]]: Lista de eventos extraídos.
        """
        print(f"Scraping {event_type} events...")
        
        soup = self.http_client.get_soup(url)
        if not soup:
            print(f"Error accessing {event_type} events")
            return []
        
        events = self.parser.parse_events_table(soup, event_type)
        print(f"Found {len(events)} {event_type} events")
        
        return events