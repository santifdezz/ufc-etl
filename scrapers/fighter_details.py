import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from config import FIGHTER_URL, HEADERS, MAX_WORKERS, DELAY, DATA_DIR, DEV_MODE, DEV_LIMIT
from concurrent.futures import ThreadPoolExecutor, as_completed

output_path = os.path.join(DATA_DIR, 'raw_fighters.csv')
NEW_COLUMNS = [
    'dob', 'slpm', 'str_acc', 'sapm', 'str_def', 'td_avg', 'td_acc', 'td_def', 'sub_avg'
]

# Helper to extract text from a list item
def get_li_value(li):
    return li.get_text(strip=True).split(':', 1)[-1].strip()

# Parse fighter details from HTML text
def parse_fighter_details_from_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    stats = {
        'slpm': None, 'str_acc': None, 'sapm': None, 'str_def': None,
        'td_avg': None, 'td_acc': None, 'td_def': None, 'sub_avg': None, 'dob': None
    }
    # DOB (from first info box)
    info_boxes = soup.find_all('div', class_='b-list__info-box')
    for box in info_boxes:
        for li in box.find_all('li'):
            title = li.find('i')
            if title and 'DOB' in title.text:
                stats['dob'] = li.get_text(strip=True).replace('DOB:', '').strip()
    # Career stats (from middle-width info box)
    middle_box = soup.find('div', class_='b-list__info-box b-list__info-box_style_middle-width js-guide clearfix')
    if middle_box:
        left = middle_box.find('div', class_='b-list__info-box-left')
        if left:
            items = left.find_all('li')
            for li in items:
                title = li.find('i')
                if not title:
                    continue
                t = title.text.strip()
                if t.startswith('SLpM'):
                    stats['slpm'] = get_li_value(li)
                elif t.startswith('Str. Acc.'):
                    stats['str_acc'] = get_li_value(li)
                elif t.startswith('SApM'):
                    stats['sapm'] = get_li_value(li)
                elif t.startswith('Str. Def'):
                    stats['str_def'] = get_li_value(li)
                elif t.startswith('TD Avg.'):
                    stats['td_avg'] = get_li_value(li)
                elif t.startswith('TD Acc.'):
                    stats['td_acc'] = get_li_value(li)
                elif t.startswith('TD Def.'):
                    stats['td_def'] = get_li_value(li)
                elif t.startswith('Sub. Avg.'):
                    stats['sub_avg'] = get_li_value(li)
    return stats


# Worker function for concurrency
def fetch_and_parse_fighter(fighter_id):
    url = f"{FIGHTER_URL}/{fighter_id}"
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            stats = parse_fighter_details_from_html(resp.text)
            print(f"Processed {fighter_id}")
            return fighter_id, stats
        else:
            print(f"Failed to fetch {fighter_id}: {resp.status_code}")
            return fighter_id, None
    except Exception as e:
        print(f"Error fetching {fighter_id}: {e}")
        return fighter_id, None

# Update CSV with new columns and data

def update_fighters_details(csv_path=output_path, dev_mode=None, dev_limit=None):
    # Read fighters
    with open(csv_path, encoding='utf-8', newline='') as f:
        reader = list(csv.DictReader(f))
        fieldnames = reader[0].keys()

    # Limitar registros si está en modo dev/test
    use_dev = dev_mode if dev_mode is not None else DEV_MODE
    limit = dev_limit if dev_limit is not None else DEV_LIMIT
    if use_dev and limit:
        reader = reader[:limit]

    # Add new columns if missing
    new_fieldnames = list(fieldnames)
    for col in NEW_COLUMNS:
        if col not in new_fieldnames:
            new_fieldnames.append(col)

    # Map fighter_id to row
    fighters = {row['fighter_id']: row for row in reader}

    # First pass: fetch and parse in parallel
    failed_ids = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_id = {executor.submit(fetch_and_parse_fighter, fighter_id): fighter_id for fighter_id in fighters}
        for future in as_completed(future_to_id):
            fighter_id = future_to_id[future]
            try:
                fid, stats = future.result()
                if stats:
                    for k, v in stats.items():
                        fighters[fid][k] = v
                else:
                    failed_ids.append(fid)
            except Exception as e:
                print(f"Error processing {fighter_id}: {e}")
                failed_ids.append(fighter_id)

    # Retry failed IDs once
    retry_failed = []
    if failed_ids:
        print(f"Retrying {len(failed_ids)} failed fighters...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_id = {executor.submit(fetch_and_parse_fighter, fighter_id): fighter_id for fighter_id in failed_ids}
            for future in as_completed(future_to_id):
                fighter_id = future_to_id[future]
                try:
                    fid, stats = future.result()
                    if stats:
                        for k, v in stats.items():
                            fighters[fid][k] = v
                    else:
                        retry_failed.append(fid)
                except Exception as e:
                    print(f"Error processing {fighter_id} on retry: {e}")
                    retry_failed.append(fighter_id)
        if retry_failed:
            print(f"Still failed after retry: {retry_failed}")

    # Write updated CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        for fighter in fighters.values():
            writer.writerow(fighter)

if __name__ == '__main__':
    update_fighters_details(output_path)
    print('Fighter details updated in data/raw_fighters.csv')
