import os
import csv
import shutil
import pytest
from scrapers.fighter_details import update_fighters_details
from scrapers.fight_details import extract_event_fights_details
from scrapers.events_details import scrape_events
from scrapers.event_fights import parse_all_event_details


from config import DATA_DIR, TEST_DATA_DIR
data_dir = DATA_DIR
test_data_dir = TEST_DATA_DIR
os.makedirs(TEST_DATA_DIR, exist_ok=True)

def copy_csv(src_name, dst_name, n=20):
    src = os.path.join(data_dir, src_name)
    dst = os.path.join(test_data_dir, dst_name)
    with open(src, encoding='utf-8') as fsrc, open(dst, 'w', encoding='utf-8', newline='') as fdst:
        reader = csv.reader(fsrc)
        writer = csv.writer(fdst)
        for i, row in enumerate(reader):
            writer.writerow(row)
            if i == n:
                break
    return dst

def get_first_n_rows(file_path, n=20):
    with open(file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for _, row in zip(range(n), reader)]
    return rows, reader.fieldnames

def test_full_pipeline():
    from config import DEV_MODE, DEV_LIMIT
    # Forzar modo dev/test
    dev_mode = True
    dev_limit = DEV_LIMIT
    # 1. Prepara archivos de entrada de ejemplo
    fighters_csv = copy_csv('raw_fighters.csv', 'raw_fighters.csv', n=20)
    event_fights_csv = copy_csv('raw_event_fights.csv', 'raw_event_fights.csv', n=20)
    events_csv = copy_csv('raw_events.csv', 'raw_events.csv', n=20)

    # 2. Ejecuta los scrapers principales
    update_fighters_details(fighters_csv, dev_mode=dev_mode, dev_limit=dev_limit)
    scrape_events(events_csv, dev_mode=dev_mode, dev_limit=dev_limit)
    parse_all_event_details(event_fights_csv, event_fights_csv, dev_mode=dev_mode, dev_limit=dev_limit)
    fights_details_path = os.path.join(test_data_dir, 'raw_event_fights.csv')
    extract_event_fights_details(event_fights_csv, fights_details_path, dev_mode=dev_mode, dev_limit=dev_limit)

    # 3. Verifica los archivos de salida
    fighters_rows, fighters_fields = get_first_n_rows(fighters_csv)
    assert len(fighters_rows) > 0
    assert len(fighters_fields) >= 20

    events_rows, events_fields = get_first_n_rows(events_csv)
    assert len(events_rows) > 0
    assert len(events_fields) >= 5


    fights_details_path = os.path.join(test_data_dir, 'raw_event_fights.csv')
    fights_rows, fights_fields = get_first_n_rows(fights_details_path)
    assert len(fights_rows) > 0
    assert len(fights_fields) >= 20

    # 4. (Opcional) Valida campos clave
    for i, row in enumerate(fighters_rows):
        has_name = row.get('name') is not None and row.get('name') != ''
        has_first_last = row.get('first') and row.get('last')
        assert has_name or has_first_last, f"Fighter row {i} missing 'name' or ('first' and 'last'): {row}"
    # 'url' ya no es obligatorio
    for i, row in enumerate(events_rows):
        assert row.get('name') is not None and row.get('name') != '', f"Event row {i} missing 'name': {row}"

    # Limpieza opcional
    # shutil.rmtree(test_data_dir)
