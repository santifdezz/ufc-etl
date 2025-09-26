from utils.fighters import ALPHABET, scrape_fighters_by_letter
from utils.common import save_to_csv, concurrent_map
from config import DATA_DIR
import os
output_fighters_path = os.path.join(DATA_DIR, 'raw_fighters.csv')

def scrape_all_fighters(output_csv=output_fighters_path, max_workers=10, dev_mode=None, dev_limit=None):
    letters = list(ALPHABET)
    all_fighters = []
    for fighters in concurrent_map(scrape_fighters_by_letter, letters, max_workers=max_workers):
        all_fighters.extend(fighters)
    # Aplica el límite solo si está en modo dev y hay límite
    if dev_mode and dev_limit:
        all_fighters = all_fighters[:dev_limit]
    fighter_fields = [
        'fighter_id', 'first', 'last', 'nickname', 'height', 
        'weight', 'reach', 'stance', 'wins', 'losses', 'defeats', 'belt'
    ]
    save_to_csv(all_fighters, output_csv, fighter_fields)
    print(f"📁 Luchadores: {len(all_fighters)} registros guardados en {output_csv}")


if __name__ == "__main__":
    scrape_all_fighters()
