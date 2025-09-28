"""
Implementación del scraper de peleas (Fight) para el pipeline UFC ETL.
Incluye lógica para extraer índices y detalles de peleas, utilizando concurrencia y manejo de archivos CSV.
"""
from typing import List, Dict, Any
from ..base.scraper import BaseScraper
from .parser import FightParser
from ...core.constants import EVENT_URL, FIGHT_URL
from ...utils.concurrent import concurrent_map_with_progress



class FightScraper(BaseScraper):

    def scrape_all_fights_workflow(self):
        """
        Ejecuta el flujo completo de scraping de peleas para eventos completados y próximos.
        Extrae los datos y los guarda en archivos CSV correspondientes.
        """
        import os
    # Siempre resuelve la ruta desde la raíz del proyecto (se asume que el directorio de trabajo es la raíz)
        events_csv = os.path.join('data', 'raw', 'raw_events.csv')
        fights_csv = os.path.join('data', 'raw', 'raw_fights.csv')
        upcoming_events_csv = os.path.join('data', 'raw', 'raw_upcoming.csv')
        fights_upcoming_csv = os.path.join('data', 'raw', 'raw_fights_upcoming.csv')
        self.scrape_fights_from_events_csv(events_csv, fights_csv)
        self.scrape_fights_from_events_csv(upcoming_events_csv, fights_upcoming_csv)

    def scrape_fights_from_events_csv(self, events_csv: str, output_csv: str):
        """
        Extrae peleas a partir de un archivo CSV de eventos y guarda los resultados (con detalles) en un archivo CSV de salida.
        """
        import pandas as pd
        from ...core.constants import FIGHT_FIELDS
        from ...utils.data import CSVManager
        from .scraper import FightDetailScraper
        events_df = pd.read_csv(events_csv)
    # Si event_id es el índice del DataFrame, se restablece para evitar problemas en el procesamiento
        if 'event_id' not in events_df.columns and events_df.index.name == 'event_id':
            events_df = events_df.reset_index()
        events = events_df.to_dict(orient='records')
        fights_index = self.scrape_fight_index(events)
    # Extrae los detalles de cada pelea a partir de la información disponible
        detail_scraper = FightDetailScraper(self.config)
        fights = detail_scraper.scrape(fights_index)
        CSVManager.save_to_csv(fights, output_csv, FIGHT_FIELDS)
        print(f"💾 Saved {len(fights)} fights (with details) to {output_csv}")
    """Scraper for fight index data."""
    
    def __init__(self, config):
        super().__init__(config)
        self.parser = FightParser()
    
    def scrape(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrae el índice de peleas a partir de una lista de eventos.
        Args:
            events (List[Dict[str, Any]]): Lista de diccionarios de eventos.
        Returns:
            List[Dict[str, Any]]: Lista de peleas extraídas.
        """
        return self.scrape_fight_index(events)

    def scrape_fight_index(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrae el índice de peleas a partir de una lista de eventos, utilizando concurrencia para acelerar el proceso.
        Elimina duplicados y muestra el progreso por evento.
        Args:
            events (List[Dict[str, Any]]): Lista de diccionarios de eventos.
        Returns:
            List[Dict[str, Any]]: Lista deduplicada de peleas extraídas.
        """
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
        
    # Utiliza procesamiento concurrente para acelerar la extracción de datos
        all_fights_nested = concurrent_map_with_progress(
            process_event,
            events,
            max_workers=self.config.scraping.max_workers,
            progress_callback=self._progress_callback
        )
        
    # Aplana los resultados y elimina duplicados para obtener una lista única de peleas
        all_fights = []
        for fights_list in all_fights_nested:
            if fights_list:
                all_fights.extend(fights_list)
        
    # Elimina peleas duplicadas utilizando el identificador fight_id
        unique_fights = {}
        for fight in all_fights:
            fight_id = fight.get('fight_id')
            if fight_id and fight_id not in unique_fights:
                unique_fights[fight_id] = fight
        
        deduplicated_fights = list(unique_fights.values())
        print(f"✅ Total fights extracted (without duplicates): {len(deduplicated_fights)}")
        
        return deduplicated_fights


class FightDetailScraper(BaseScraper):
    """
    Scraper especializado en la extracción de información detallada de peleas.
    Utiliza concurrencia y muestra el progreso de la extracción.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.parser = FightParser()
    
    def scrape(self, fights_index: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrae información detallada de peleas a partir de un índice de peleas.
        Fusiona los detalles extraídos con los datos originales y muestra el progreso.
        Args:
            fights_index (List[Dict[str, Any]]): Lista de diccionarios con el índice de peleas.
        Returns:
            List[Dict[str, Any]]: Lista de peleas con información detallada.
        """
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
                
                # Fusiona los detalles de la pelea con los datos del índice, preservando los campos originales
                merged_fight = {**fight_details, **fight_data}
                
                # Asegura que los campos fight_id y event_id provengan del índice original
                merged_fight['fight_id'] = fight_data['fight_id']
                merged_fight['event_id'] = fight_data['event_id']
                if 'fight_order' in fight_data:
                    merged_fight['fight_order'] = fight_data['fight_order']
                                
                return merged_fight
                
            except Exception as e:
                print(f"Error processing fight {fight_id}: {e}")
                return fight_data
        
    # Utiliza procesamiento concurrente mostrando el progreso de la extracción
        detailed_fights = concurrent_map_with_progress(
            process_fight,
            fights_index,
            max_workers=self.config.scraping.max_workers,
            progress_callback=self._progress_callback
        )
        
        print(f"✅ Fight details scraped: {len(detailed_fights)}")
        return detailed_fights