
import os
from utils.events import scrape_all_events
from utils.common import save_to_csv
from config import DATA_DIR

output_path = os.path.join(DATA_DIR, "raw_events.csv")

def scrape_events(output_csv=output_path, dev_mode=None, dev_limit=None):
    events_data = scrape_all_events(dev_mode=dev_mode, dev_limit=dev_limit)
    event_fields = ['event_id', 'name', 'date', 'location', 'status']
    event_fields = [f.lower() for f in event_fields]
    save_to_csv(events_data, output_csv, event_fields)
    print(f"📁 Eventos: {len(events_data)} registros guardados en {output_csv}")

if __name__ == "__main__":
    scrape_events()
