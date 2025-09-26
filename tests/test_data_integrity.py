import csv
import os
import pytest

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

FILES_AND_MIN_COLS = [
    ('raw_fighters.csv', 10),
    ('raw_events.csv', 10),
    ('raw_event_fights.csv', 10),
]

def get_first_n_rows(file_path, n=10):
    with open(file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for _, row in zip(range(n), reader)]
    return rows, reader.fieldnames

@pytest.mark.parametrize('filename,min_cols', FILES_AND_MIN_COLS)
def test_csv_structure(filename, min_cols):
    file_path = os.path.join(data_dir, filename)
    assert os.path.exists(file_path), f"File not found: {file_path}"
    rows, fieldnames = get_first_n_rows(file_path, 10)
    assert len(fieldnames) >= min_cols, f"{filename} has too few columns: {len(fieldnames)}"
    assert len(rows) == 10 or (len(rows) < 10 and sum(1 for _ in open(file_path)) <= 11), f"{filename} does not have 10 rows"
    # Check that all rows have the same columns
    for i, row in enumerate(rows):
        assert set(row.keys()) == set(fieldnames), f"Row {i} in {filename} has mismatched columns"
