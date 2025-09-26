# main.py
from scrapers.fighters_details import scrape_all_fighters
from scrapers.events_details import scrape_events
from scrapers.fighter_details import update_fighters_details
from scrapers.event_fights import parse_all_event_details
from scrapers.fight_details import extract_event_fights_details

from config import EVENT_URL, DATA_DIR

def main(dev_mode=None, dev_limit=None):
    print("🚀 Iniciando scraping de UFC Stats...")
    print("Modo desarrollo:", dev_mode, "Límite:", dev_limit)
    
    print("Fase 1: Scraping de luchadores")
    scrape_all_fighters(dev_mode=dev_mode, dev_limit=dev_limit)
    
    print("Fase 2: Scraping de eventos")
    scrape_events(dev_mode=dev_mode, dev_limit=dev_limit)
    
    print("Fase 3: Scraping de detalles de los luchadores")
    update_fighters_details(dev_mode=dev_mode, dev_limit=dev_limit)
    
    print("Fase 4: Scraping de peleas y detalles de los eventos")
    parse_all_event_details(max_workers=5,dev_mode=dev_mode,dev_limit=dev_limit)
    
    print("Fase 5: Scraping de detalles de las peleas")
    extract_event_fights_details(max_workers=5,dev_mode=dev_mode,dev_limit=dev_limit)
    
    
    print("\n✅ Scraping completado!")

if __name__ == "__main__":
    main()