import csv
import os
import pytest
from scrapers.event_fights import parse_all_event_details

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
test_data_dir = os.path.join(data_dir, 'tests')
os.makedirs(test_data_dir, exist_ok=True)

def get_first_n_rows(file_path, n=10):
    with open(file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for _, row in zip(range(n), reader)]
    return rows, reader.fieldnames

def test_raw_event_fights_structure():
    file_path = os.path.join(data_dir, 'raw_event_fights.csv')
    rows, fieldnames = get_first_n_rows(file_path)
    assert len(fieldnames) >= 5
    assert len(rows) == 10 or (len(rows) < 10 and sum(1 for _ in open(file_path)) <= 11)
    for i, row in enumerate(rows):
        assert set(row.keys()) == set(fieldnames)

def test_event_fights_scraper_runs():
    src = os.path.join(data_dir, 'raw_event_fights.csv')
    dst = os.path.join(test_data_dir, 'raw_event_fights.csv')
    with open(src, encoding='utf-8') as fsrc, open(dst, 'w', encoding='utf-8', newline='') as fdst:
        reader = csv.reader(fsrc)
        writer = csv.writer(fdst)
        for i, row in enumerate(reader):
            writer.writerow(row)
            if i == 10:
                break
    parse_all_event_details(dst, dst)
    rows, fieldnames = get_first_n_rows(dst)
    assert len(rows) > 0
    assert len(fieldnames) >= 5
