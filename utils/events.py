# utils/events.py
from bs4 import BeautifulSoup
from utils.helpers import get_soup, extract_id, clean_text, delay_request
from config import EVENTS_COMPLETED_URL, EVENTS_UPCOMING_URL

def extract_event_data(event_row):
    """Extrae datos de una fila de evento"""
    try:
        cells = event_row.find_all('td')
        if len(cells) < 2:
            return None
        # Primer td: nombre, enlace y fecha
        content = cells[0].find('i', class_='b-statistics__table-content')
        if not content:
            return None
        link_tag = content.find('a', href=True)
        date_tag = content.find('span', class_='b-statistics__date')
        if not link_tag or not date_tag:
            return None
        event_url = link_tag['href']
        event_id = extract_id(event_url)
        name = clean_text(link_tag.get_text())
        date = clean_text(date_tag.get_text())
        # Segundo td: ubicación
        location = clean_text(cells[1].get_text())
        return {
            'event_id': event_id,
            'name': name,
            'date': date,
            'location': location
        }
    except Exception as e:
        print(f"Error extrayendo datos de evento: {e}")
        return None

def scrape_events_from_url(url, event_type):
    """Scrapes eventos desde una URL específica"""
    print(f"Scrapeando eventos {event_type}...")
    soup = get_soup(url)
    if not soup:
        print(f"Error al acceder a eventos {event_type}")
        return []
    events_table = soup.find('table', class_='b-statistics__table-events')
    if not events_table:
        print(f"No se encontró tabla de eventos {event_type}")
        return []
    events = []
    rows = events_table.find_all('tr')[1:]  # Saltar header
    # Saltar la primera fila si tiene un img en td.b-statistics__icon (solo en completed)
    if event_type == "completed" and rows:
        first_row = rows[0]
        icon_td = first_row.find('td', class_='b-statistics__icon')
        if icon_td and icon_td.find('img'):
            rows = rows[1:]
    for row in rows:
        event_data = extract_event_data(row)
        if event_data:
            events.append(event_data)
    print(f"Encontrados {len(events)} eventos {event_type}")
    return events

def scrape_all_events(dev_mode=None, dev_limit=None):
    """Scrapes todos los eventos (completados y próximos), con límite opcional"""
    from config import DEV_MODE, DEV_LIMIT
    use_dev = dev_mode if dev_mode is not None else DEV_MODE
    limit = dev_limit if dev_limit is not None else DEV_LIMIT
    completed_events = scrape_events_from_url(f"{EVENTS_COMPLETED_URL}?page=all", "completed")
    for e in completed_events:
        e['status'] = 'completed'
    if use_dev and limit:
        # Solo devolver los primeros N completados en modo dev
        return completed_events[:limit]
    delay_request()
    upcoming_events = scrape_events_from_url(f"{EVENTS_UPCOMING_URL}?page=all", "upcoming")
    for e in upcoming_events:
        e['status'] = 'upcoming'
    all_events = completed_events + upcoming_events
    return all_events