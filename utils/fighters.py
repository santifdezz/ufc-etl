# utils/fighters.py
from bs4 import BeautifulSoup
from utils.helpers import get_soup, extract_id, clean_text, safe_extract, delay_request
from config import ALPHABET, FIGHTERS_URL, DATA_DIR
import time
from utils.common import save_to_csv, concurrent_map

def get_fighter_links_for_letter(letter):
    """Obtiene todos los links de luchadores para una letra específica"""
    url = f"{FIGHTERS_URL}?char={letter}&page=all"
    soup = get_soup(url)
    
    if not soup:
        return []
    
    fighter_links = []
    table = soup.find('table', class_='b-statistics__table')
    
    if table:
        links = table.find_all('a', href=True)
        for link in links:
            href = link['href']
            if '/fighter-details/' in href:
                fighter_links.append(href)
    
    return fighter_links

def normalize_field(value):
    value = value.strip() if isinstance(value, str) else value
    if not value or value == '--':
        return None
    return value

def extract_fighters_from_table(table):
    fighters = []
    rows = table.find_all('tr', class_='b-statistics__table-row')
    field_names = [
        'first', 'last', 'nickname', 'height', 'weight', 'reach', 'stance', 'wins', 'losses', 'defeats'
    ]
    for row in rows:
        cols = row.find_all('td')
        if not cols:
            continue
        link_tag = cols[0].find('a', href=True)
        if not link_tag:
            continue
        # Normalizar todos los campos con un bucle
        values = [normalize_field(cols[i].get_text()) if len(cols) > i else None for i in range(len(field_names))]
        fighter_id = extract_id(link_tag['href']) if link_tag else None
        belt = None
        if len(cols) > 10:
            belt_col = cols[10]
            img_tag = belt_col.find('img', src=True)
            if img_tag and img_tag['src'].endswith('/belt.png'):
                belt = True
            else:
                belt = False
        fighter = {'fighter_id': fighter_id, 'belt': belt}
        fighter.update(dict(zip(field_names, values)))
        fighters.append(fighter)
    return fighters


def scrape_fighters_by_letter(letter, dev_mode=None, dev_limit=None, current_total=0):
    """Scrapea los luchadores de una letra, respetando dev_limit si está en dev_mode."""
    url = f"{FIGHTERS_URL}?char={letter}&page=all"
    soup = get_soup(url)
    if not soup:
        return []
    table = soup.find('table', class_='b-statistics__table')
    if not table:
        return []
    fighters = extract_fighters_from_table(table)
    # Si estamos en dev_mode, solo devuelve los que faltan para el límite
    if dev_mode and dev_limit:
        remaining = dev_limit - current_total
        fighters = fighters[:remaining]
    print(f"Letra {letter.upper()}: {len(fighters)} luchadores")
    return fighters

