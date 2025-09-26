import csv
import requests
from utils.event_details import parse_event_details
from config import EVENT_URL, DATA_DIR, DEV_MODE, DEV_LIMIT
from utils.common import save_to_csv, concurrent_map
import os
output_path = os.path.join(DATA_DIR, 'raw_event_fights.csv')
input_path = os.path.join(DATA_DIR, 'raw_events.csv')

def parse_all_event_details(event_csv=input_path, output_csv=output_path, max_workers=10, dev_mode=None, dev_limit=None):
    # Leer eventos
    with open(event_csv, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        events = list(reader)
    # Limitar registros si está en modo dev/test
    use_dev = dev_mode if dev_mode is not None else DEV_MODE
    limit = dev_limit if dev_limit is not None else DEV_LIMIT
    if use_dev and limit:
        events = events[:limit]
    print(f"Procesando {len(events)} eventos...")
    def process_event(row):
        event_id = row['event_id']
        url = f"{EVENT_URL}/{event_id}"
        print(f"Descargando y procesando evento: {event_id} - {row.get('name', '')}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
            fights = parse_event_details(html, event_id)
            print(f"  -> {len(fights)} peleas extraídas")
            return fights
        except Exception as e:
            print(f"Error accediendo a {url}: {e}")
            return []
    all_fights_nested = concurrent_map(process_event, events, max_workers=max_workers)
    all_fights = [fight for fights in all_fights_nested for fight in fights]
    # Eliminar duplicados por fight_id
    unique_fights = {}
    for fight in all_fights:
        fid = fight.get('fight_id')
        if fid and fid not in unique_fights:
            unique_fights[fid] = fight
    all_fights_dedup = list(unique_fights.values())
    print(f"Total peleas extraídas (sin duplicados): {len(all_fights_dedup)}")
    if all_fights_dedup:
        fieldnames = ['event_id', 'fight_id', 'fight_order']
        save_to_csv(all_fights_dedup, output_csv, fieldnames)
        print(f"✅ Peleas de eventos guardadas en {output_csv}")
    else:
        print("No se encontraron peleas para los eventos.")


if __name__ == "__main__":
    parse_all_event_details(
        event_csv=DATA_DIR+'/raw_events.csv',
        output_csv= output_path,
        max_workers=5
    )
