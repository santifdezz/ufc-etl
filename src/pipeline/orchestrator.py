"""
Orquestador principal del pipeline ETL de UFC.
Coordina la ejecución de las distintas fases de scraping y procesamiento de datos, gestionando la configuración y el almacenamiento.
"""
from typing import Optional
from ..core.config import Config
from ..scrapers.fighters.scraper import FighterScraper, FighterDetailScraper
from ..scrapers.events.scraper import EventScraper
from ..scrapers.fights.scraper import FightScraper, FightDetailScraper
from ..utils.data import CSVManager
from ..core.constants import FIGHTER_FIELDS, EVENT_FIELDS, FIGHT_FIELDS, FIGHTER_DETAIL_FIELDS


class UFCScrapingOrchestrator:
    """
    Orquesta la ejecución completa del pipeline de scraping de UFC.
    Gestiona la configuración, la ejecución de scrapers y el almacenamiento de los datos extraídos y procesados.
    """
    
    def __init__(self, dev_mode: Optional[bool] = None, dev_limit: Optional[int] = None):
        self.config = Config(dev_mode=dev_mode, dev_limit=dev_limit)
        self.csv_manager = CSVManager()
    
    def run_full_pipeline(self):
        """
        Ejecuta el pipeline completo de scraping y procesamiento de datos de UFC.
        Realiza las fases de extracción de luchadores, eventos, peleas y detalles, guardando los resultados en archivos CSV.
        """
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

        # Phase 3: Fights (completed and upcoming)
        print("\n" + "="*50)
        print("PHASE 3: FIGHTS (COMPLETED & UPCOMING)")
        print("="*50)
        from ..scrapers.fights.scraper import FightScraper
        FightScraper(self.config).scrape_all_fights_workflow()

        # Phase 4: Fighter Details
        print("\n" + "="*50)
        print("PHASE 4: FIGHTER DETAILS")
        print("="*50)
        self._scrape_fighter_details()

        # Phase 5: Fight Details
        print("\n" + "="*50)
        print("PHASE 5: FIGHT DETAILS")
        print("="*50)
        self._scrape_fight_details()
        
        print("\n🎉 Pipeline completed successfully!")
    
    def _scrape_fighters(self):
        """
        Extrae información básica de luchadores y la almacena en el archivo correspondiente.
        """
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
        """
        Extrae información de eventos y la almacena en el archivo correspondiente.
        """
        scraper = EventScraper(self.config)
        scraper.scrape()
    
    def _scrape_fighter_details(self):
        """
        Extrae información detallada de luchadores y actualiza el archivo correspondiente.
        """
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
        """
        Extrae el índice de peleas a partir de los eventos y lo almacena en el archivo correspondiente.
        """
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
        """
        Extrae información detallada de peleas y actualiza el archivo correspondiente.
        """
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