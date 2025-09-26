from bs4 import BeautifulSoup
from utils.helpers import clean_text, extract_id

def parse_event_details(html, event_id):
    soup = BeautifulSoup(html, 'html.parser')
    fight_table = soup.find('table', class_='b-fight-details__table')
    if not fight_table:
        return []
    rows = fight_table.find('tbody').find_all('tr')
    fights = []
    for idx, row in enumerate(rows):
        cols = row.find_all('td')
        if not cols or len(cols) < 10:
            continue
        fight_id = row.get('data-link', None)
        if fight_id:
            fight_id = extract_id(fight_id)
        fights.append({
            'event_id': event_id,
            'fight_id': fight_id,
            'fight_order': idx + 1
        })
    return fights
