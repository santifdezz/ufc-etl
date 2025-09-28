"""
Implementación del parser de eventos (Event) para el pipeline UFC ETL.
Extrae y estructura información de eventos a partir de HTML, utilizando BeautifulSoup y utilidades propias.
"""
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from ..base.parser import BaseParser
from ...utils.http import extract_id_from_url, clean_text


class EventParser(BaseParser):
    """
    Parser especializado para datos de eventos.
    Proporciona métodos para extraer información de eventos desde tablas HTML.
    """
    
    def parse_events_table(self, soup: BeautifulSoup, event_type: str) -> List[Dict[str, Any]]:
        """
        Extrae la tabla de eventos desde el HTML y la convierte en una lista de diccionarios.
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup de la página de eventos.
            event_type (str): Tipo de evento (completado o próximo).
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los datos de cada evento.
        """
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
        """
        Extrae los datos de un evento individual a partir de una fila de la tabla.
        Args:
            event_row (BeautifulSoup): Fila de la tabla de eventos.
            event_type (str): Tipo de evento.
        Returns:
            Dict[str, Any]: Diccionario con los datos del evento, o None si hay error.
        """
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
                'location': location
            }
            
        except Exception as e:
            print(f"Error extracting event data: {e}")
            return None