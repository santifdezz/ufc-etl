import csv
import time
import requests
from bs4 import BeautifulSoup
from config import MAX_WORKERS, DELAY, FIGHT_URL, HEADERS, DATA_DIR, DEV_MODE, DEV_LIMIT
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import re

output_path = os.path.join(DATA_DIR, 'raw_event_fights.csv')


# Columnas ordenadas y limpias para el CSV final
CSV_COLUMNS = [
    'event_id','fight_id','fight_order','fighter1_id','fighter1_name','fighter2_id','fighter2_name',
    'winner_id',
    'weight_class','referee','round','time','time_format','method','details','bonus',
    'kd1','kd2','str1','str2','td1','td2','sub1','sub2',
    # extras si existen
    'control_time1','control_time2','sig_head1','sig_head2','sig_body1','sig_body2','sig_leg1','sig_leg2',
    'total_str1','total_str2','pass1','pass2','rev1','rev2'
]

def get_text_or_none(tag):
    return tag.get_text(strip=True) if tag else None

def parse_fight_details_from_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    fight = {}

    # 1. Event ID
    event_tag = soup.find('h2', class_='b-content__title')
    if event_tag:
        event_link = event_tag.find('a', href=True)
        if event_link:
            fight['event_id'] = event_link['href'].split('/')[-1]

    # 2. Fighters (names, nicknames, ids)
    persons = soup.find_all('div', class_='b-fight-details__person')
    winner_name = None
    if len(persons) == 2:
        f1 = persons[0]
        f2 = persons[1]
        f1_name = f1.find('h3', class_='b-fight-details__person-name')
        f2_name = f2.find('h3', class_='b-fight-details__person-name')
        if f1_name and f1_name.a:
            fight['fighter1_name'] = f1_name.a.text.strip()
            fight['fighter1_id'] = f1_name.a['href'].split('/')[-1] if f1_name.a.has_attr('href') else ''
        if f2_name and f2_name.a:
            fight['fighter2_name'] = f2_name.a.text.strip()
            fight['fighter2_id'] = f2_name.a['href'].split('/')[-1] if f2_name.a.has_attr('href') else ''

        # Detectar winner por status (verde = W, gris = L)
        f1_status = f1.find('i', class_='b-fight-details__person-status')
        f2_status = f2.find('i', class_='b-fight-details__person-status')
        if f1_status and 'green' in ' '.join(f1_status.get('class', [])):
            winner_name = fight.get('fighter1_name', '').strip()
        elif f2_status and 'green' in ' '.join(f2_status.get('class', [])):
            winner_name = fight.get('fighter2_name', '').strip()
        
        # Asignar winner_id
        winner_id = ''
        if winner_name:
            if winner_name == fight.get('fighter1_name', '').strip():
                winner_id = fight.get('fighter1_id', '')
            elif winner_name == fight.get('fighter2_name', '').strip():
                winner_id = fight.get('fighter2_id', '')
        fight['winner_id'] = winner_id

    # 3. Weight class / título
    fight_title = soup.find('i', class_='b-fight-details__fight-title')
    if fight_title:
        # Limpiar el texto del título, removiendo imágenes de cinturones
        title_text = fight_title.get_text(strip=True)
        fight['weight_class'] = title_text

    # Detectar si es upcoming (no hay detalles de pelea ni tabla de stats)
    is_upcoming = False
    fight_content = soup.find('div', class_='b-fight-details__content')
    stats_table = soup.find('table')
    if not fight_content or not stats_table:
        is_upcoming = True


    # 4. Si es upcoming, dejar solo los datos básicos
    if is_upcoming:
        all_keys = [
            'event_id', 'fighter1_name', 'fighter2_name', 'weight_class', 'referee', 
            'round', 'time', 'time_format', 'method', 'details', 'bonus',
            'kd1', 'kd2', 'str1', 'str2', 'td1', 'td2', 'sub1', 'sub2'
        ]
        for k in all_keys:
            if k not in fight:
                if k in ['kd1','kd2','td1','td2','sub1','sub2']:
                    fight[k] = '0'
                else:
                    fight[k] = ''
        return fight

    # 5. Extraer detalles de la pelea desde b-fight-details__content
    if fight_content:
        # Función para limpiar valores
        def clean_value(val):
            if not val:
                return ''
            v = str(val)
            v = re.sub(r'[\n\r\t]+', ' ', v)
            v = re.sub(r'\s+', ' ', v)
            v = v.strip()
            return v

        # Buscar todos los elementos con clase b-fight-details__text-item
        text_items = fight_content.find_all('i', class_='b-fight-details__text-item')
        text_items_first = fight_content.find_all('i', class_='b-fight-details__text-item_first')
        all_items = text_items_first + text_items

        for item in all_items:
            label_tag = item.find('i', class_='b-fight-details__label')
            if not label_tag:
                continue
            
            label_text = label_tag.get_text(strip=True).lower().replace(':', '')
            
            if label_text == 'method':
                # Method está en el siguiente elemento hermano después del label
                method_element = label_tag.find_next_sibling()
                if method_element and method_element.name == 'i' and method_element.has_attr('style'):
                    fight['method'] = clean_value(method_element.get_text(strip=True))
                else:
                    # Alternativa: buscar texto después del label en el mismo item
                    full_text = item.get_text(strip=True)
                    method_match = re.search(r'Method:\s*(.+?)(?:\s+Round:|$)', full_text)
                    if method_match:
                        fight['method'] = clean_value(method_match.group(1))
                        
            elif label_text == 'round':
                # El round está directamente después del label
                round_text = item.get_text(strip=True)
                round_match = re.search(r'Round:\s*(\d+)', round_text)
                if round_match:
                    fight['round'] = round_match.group(1)
                    
            elif label_text == 'time':
                # El tiempo está directamente después del label
                time_text = item.get_text(strip=True)
                time_match = re.search(r'Time:\s*(\d+:\d+)', time_text)
                if time_match:
                    fight['time'] = time_match.group(1)
                    
            elif label_text == 'time format':
                # El formato está directamente después del label
                format_text = item.get_text(strip=True)
                format_match = re.search(r'Time format:\s*(.+?)(?:\s+Referee:|$)', format_text)
                if format_match:
                    fight['time_format'] = clean_value(format_match.group(1))
                    
            elif label_text == 'referee':
                # El referee puede estar en un span dentro del item
                referee_span = item.find('span')
                if referee_span:
                    fight['referee'] = clean_value(referee_span.get_text(strip=True))
                else:
                    # Alternativa: buscar texto después del label
                    referee_text = item.get_text(strip=True)
                    referee_match = re.search(r'Referee:\s*(.+)', referee_text)
                    if referee_match:
                        fight['referee'] = clean_value(referee_match.group(1))

        # 6. Extraer detalles (método específico o scores de judges)
        details_sections = fight_content.find_all('p', class_='b-fight-details__text')
        for section in details_sections:
            # Buscar si hay detalles específicos del método
            details_label = section.find('i', class_='b-fight-details__label')
            if details_label and 'details' in details_label.get_text(strip=True).lower():
                # Extraer el texto después del label "Details:"
                section_text = section.get_text(strip=True)
                details_match = re.search(r'Details:\s*(.+)', section_text, re.IGNORECASE)
                if details_match:
                    fight['details'] = clean_value(details_match.group(1))
                    break

    # 7. Bonus (si existe)
    bonus_tag = soup.find('i', class_='b-fight-details__fight-bonus')
    if bonus_tag:
        fight['bonus'] = bonus_tag.get_text(strip=True)

    # 8. Estadísticas principales (tabla Totals)
    # Buscar la primera tabla con estadísticas
    stats_table = soup.find('table')
    if stats_table:
        # Buscar la fila de datos (no header)
        data_rows = stats_table.find('tbody')
        if data_rows:
            data_row = data_rows.find('tr')
            if data_row:
                cols = data_row.find_all('td')
                
                def get_stat(col, fighter_idx):
                    """Extrae estadística para fighter_idx (0=fighter1, 1=fighter2)"""
                    ps = col.find_all('p', class_='b-fight-details__table-text')
                    if len(ps) >= 2:
                        return ps[fighter_idx].get_text(strip=True)
                    elif len(ps) == 1:
                        # Solo hay una estadística, asumir que es para fighter1
                        return ps[0].get_text(strip=True) if fighter_idx == 0 else '0'
                    else:
                        return '0'
                
                # Mapeo de columnas según el HTML de ejemplo:
                # Col 0: Fighter names, Col 1: KD, Col 2: Sig. str, Col 3: Sig. str. %
                # Col 4: Total str, Col 5: Td, Col 6: Td %, Col 7: Sub. att, Col 8: Rev, Col 9: Ctrl
                if len(cols) >= 10:
                    fight['kd1'] = get_stat(cols[1], 0)
                    fight['kd2'] = get_stat(cols[1], 1)
                    fight['str1'] = get_stat(cols[2], 0)  # Significant strikes
                    fight['str2'] = get_stat(cols[2], 1)
                    fight['td1'] = get_stat(cols[5], 0)   # Takedowns
                    fight['td2'] = get_stat(cols[5], 1)
                    fight['sub1'] = get_stat(cols[7], 0)  # Submission attempts
                    fight['sub2'] = get_stat(cols[7], 1)
                    
                    # Control time (Col 9)
                    fight['control_time1'] = get_stat(cols[9], 0)
                    fight['control_time2'] = get_stat(cols[9], 1)
                    
                    # Total strikes (Col 4)
                    fight['total_str1'] = get_stat(cols[4], 0)
                    fight['total_str2'] = get_stat(cols[4], 1)
                    
                    # Reversals (Col 8)
                    fight['rev1'] = get_stat(cols[8], 0)
                    fight['rev2'] = get_stat(cols[8], 1)

    # 9. Buscar tabla de significant strikes breakdown (Head, Body, Leg)
    # Esta tabla aparece después con el título "Significant Strikes"
    sig_strikes_section = soup.find('p', class_='b-fight-details__collapse-link_tot', string=lambda text: text and 'Significant Strikes' in text)
    if sig_strikes_section:
        # Buscar la tabla siguiente
        sig_table = sig_strikes_section.find_next('table')
        if sig_table:
            sig_tbody = sig_table.find('tbody')
            if sig_tbody:
                sig_row = sig_tbody.find('tr')
                if sig_row:
                    sig_cols = sig_row.find_all('td')
                    
                    def get_sig_stat(col, fighter_idx):
                        ps = col.find_all('p', class_='b-fight-details__table-text')
                        if len(ps) >= 2:
                            return ps[fighter_idx].get_text(strip=True)
                        return '0'
                    
                    # Columnas: Fighter, Sig. str, Sig. str. %, Head, Body, Leg, Distance, Clinch, Ground
                    if len(sig_cols) >= 9:
                        fight['sig_head1'] = get_sig_stat(sig_cols[3], 0)  # Head
                        fight['sig_head2'] = get_sig_stat(sig_cols[3], 1)
                        fight['sig_body1'] = get_sig_stat(sig_cols[4], 0)  # Body
                        fight['sig_body2'] = get_sig_stat(sig_cols[4], 1)
                        fight['sig_leg1'] = get_sig_stat(sig_cols[5], 0)   # Leg
                        fight['sig_leg2'] = get_sig_stat(sig_cols[5], 1)

    # 10. Rellenar campos vacíos con valores por defecto
    all_keys = [
        'event_id', 'fighter1_name', 'fighter2_name', 'weight_class', 'referee', 
        'round', 'time', 'time_format', 'method', 'details', 'bonus',
        'kd1', 'kd2', 'str1', 'str2', 'td1', 'td2', 'sub1', 'sub2',
        'control_time1', 'control_time2', 'sig_head1', 'sig_head2', 
        'sig_body1', 'sig_body2', 'sig_leg1', 'sig_leg2',
        'total_str1', 'total_str2', 'pass1', 'pass2', 'rev1', 'rev2'
    ]
    
    for k in all_keys:
        if k not in fight:
            if k in ['kd1','kd2','td1','td2','sub1','sub2','pass1','pass2','rev1','rev2']:
                fight[k] = '0'
            else:
                fight[k] = ''
    
    return fight

def extract_event_fights_details(csv_path=output_path, output_csv=output_path, dev_mode=None, dev_limit=None, max_workers=None):
    # Read base event fights (index) from csv_path
    with open(csv_path, encoding='utf-8', newline='') as f:
        base_rows = list(csv.DictReader(f))
    fight_ids = [row['fight_id'] for row in base_rows if row.get('fight_id')]
    
    # Limitar registros si está en modo dev/test
    use_dev = dev_mode if dev_mode is not None else DEV_MODE
    limit = dev_limit if dev_limit is not None else DEV_LIMIT
    if use_dev and limit:
        fight_ids = fight_ids[:limit]

    fights = {}  # fight_id -> details dict
    total = len(fight_ids)
    
    def fetch_fight(fight_id, idx=None):
        url = f"{FIGHT_URL}/{fight_id}"
        try:
            resp = requests.get(url, headers=HEADERS)
            if resp.status_code == 200:
                fight = parse_fight_details_from_html(resp.text)
                fight['fight_id'] = fight_id
                if idx is not None:
                    print(f"Processed {fight_id} ({idx+1}/{len(fight_ids)})")
                else:
                    print(f"Processed {fight_id}")
                return fight_id, fight
            else:
                print(f"Failed to fetch {fight_id}: {resp.status_code}")
                return fight_id, None
        except Exception as e:
            print(f"Error fetching {fight_id}: {e}")
            return fight_id, None

    # Concurrency: fetch and parse in parallel
    workers = max_workers if max_workers is not None else MAX_WORKERS
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_id = {executor.submit(fetch_fight, fight_id, idx): fight_id for idx, fight_id in enumerate(fight_ids)}
        for future in as_completed(future_to_id):
            fight_id = future_to_id[future]
            try:
                fid, fight = future.result()
                if fight:
                    fights[fid] = fight
            except Exception as e:
                print(f"Error processing {fight_id}: {e}")

    # Merge details into base rows by fight_id
    merged_rows = []
    for base in base_rows:
        fid = base.get('fight_id')
        details = fights.get(fid, {})
        # Start with details, but only keep allowed columns
        merged = {k: details.get(k, '') for k in CSV_COLUMNS}
        # Always take fight_order from base (never from details)
        if 'fight_order' in base:
            merged['fight_order'] = base['fight_order']
        # Also take event_id and fight_id from base to ensure consistency
        if 'event_id' in base:
            merged['event_id'] = base['event_id']
        if 'fight_id' in base:
            merged['fight_id'] = base['fight_id']
        merged_rows.append(merged)

    # Write merged output to output_csv if given, else overwrite RAW_EVENT_FIGHTS_CSV
    output_path = output_csv if output_csv else output_path
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in merged_rows:
            writer.writerow(row)

if __name__ == '__main__':
    extract_event_fights_details(output_path)
    print(f'Fight details extracted to {output_path}')