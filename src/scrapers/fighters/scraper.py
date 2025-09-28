"""
Implementación del scraper de luchadores (Fighter) para el pipeline UFC ETL.
Incluye lógica para extraer información básica y detallada de luchadores, utilizando concurrencia y manejo de datos estructurados.
"""
from typing import List, Dict, Any
from ..base.scraper import BaseScraper
from .parser import FighterParser
from ...core.constants import FIGHTERS_URL, ALPHABET
from ...utils.concurrent import concurrent_map, concurrent_map_with_progress


class FighterScraper(BaseScraper):
    """
    Scraper especializado para la extracción de datos de luchadores.
    Permite obtener información básica de todos los luchadores, procesando por letra y utilizando concurrencia.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.parser = FighterParser()
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Extrae todos los luchadores de todas las letras del alfabeto y los retorna como una lista de diccionarios.
        Utiliza procesamiento concurrente para acelerar la extracción.
        Returns:
            List[Dict[str, Any]]: Lista de luchadores extraídos.
        """
        print("🥊 Scraping fighters...")
        
        def scrape_letter(letter: str) -> List[Dict[str, Any]]:
            return self._scrape_fighters_by_letter(letter)
        
        # Use concurrent processing
        all_results = concurrent_map(
            scrape_letter, 
            ALPHABET, 
            max_workers=self.config.scraping.max_workers
        )
        
        # Flatten results
        all_fighters = []
        for fighters_list in all_results:
            if fighters_list:
                all_fighters.extend(fighters_list)
        
        all_fighters = self._apply_dev_limit(all_fighters)
        print(f"✅ Total fighters scraped: {len(all_fighters)}")
        
        return all_fighters
    
    def _scrape_fighters_by_letter(self, letter: str) -> List[Dict[str, Any]]:
        """
        Extrae luchadores para una letra específica del alfabeto.
        Args:
            letter (str): Letra a consultar.
        Returns:
            List[Dict[str, Any]]: Lista de luchadores extraídos para la letra dada.
        """
        url = f"{FIGHTERS_URL}?char={letter}&page=all"
        soup = self.http_client.get_soup(url)
        
        if not soup:
            return []
        
        fighters = self.parser.parse_fighters_table(soup)
        print(f"Letter {letter.upper()}: {len(fighters)} fighters")
        
        return fighters


class FighterDetailScraper(BaseScraper):
    """
    Scraper especializado en la extracción de información detallada de luchadores.
    Utiliza concurrencia y muestra el progreso de la extracción.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.parser = FighterParser()
    
    def scrape(self, fighters_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extrae información detallada de luchadores a partir de una lista de datos básicos.
        Fusiona los detalles extraídos con los datos originales y muestra el progreso.
        Args:
            fighters_data (List[Dict[str, Any]]): Lista de diccionarios con datos básicos de luchadores.
        Returns:
            List[Dict[str, Any]]: Lista de luchadores con información detallada.
        """
        print("📊 Scraping fighter details...")
        
        fighters_data = self._apply_dev_limit(fighters_data)
        
        def scrape_fighter_details(fighter_data: Dict[str, Any], idx: int = None) -> Dict[str, Any]:
            fighter_id = fighter_data.get('fighter_id')
            if not fighter_id:
                return fighter_data
            
            details = self._scrape_single_fighter_details(fighter_id)
            if details:
                # Merge details with existing data
                updated_fighter = {**fighter_data, **details}
                if idx is not None:
                    print(f"Processed fighter {fighter_id} ({idx+1}/{len(fighters_data)})")
                return updated_fighter
            
            return fighter_data
        
        # Use concurrent processing with progress
        updated_fighters = concurrent_map_with_progress(
            scrape_fighter_details,
            fighters_data,
            max_workers=self.config.scraping.max_workers,
            progress_callback=self._progress_callback
        )
        
        print(f"✅ Fighter details updated: {len(updated_fighters)}")
        return updated_fighters
    
    def _scrape_single_fighter_details(self, fighter_id: str) -> Dict[str, Any]:
        """
        Extrae los detalles de un solo luchador a partir de su identificador.
        Args:
            fighter_id (str): Identificador del luchador.
        Returns:
            Dict[str, Any]: Diccionario con los detalles extraídos del luchador.
        """
        from ...core.constants import FIGHTER_URL
        
        url = f"{FIGHTER_URL}/{fighter_id}"
        
        try:
            html = self.http_client.get_html(url)
            details = self.parser.parse_fighter_details(html)
            return details
        except Exception as e:
            print(f"Error scraping fighter {fighter_id}: {e}")
            return {}