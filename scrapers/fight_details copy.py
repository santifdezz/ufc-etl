import csv
import time
import requests
from bs4 import BeautifulSoup
from config import MAX_WORKERS, DELAY, FIGHT_URL, HEADERS, DATA_DIR, DEV_MODE, DEV_LIMIT
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


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
        # Detectar winner_name por color de status (verde)
        f1_status = f1.find('i', class_='b-fight-details__person-status')
        f2_status = f2.find('i', class_='b-fight-details__person-status')
        if f1_status and 'green' in f1_status.get('class', []):
            winner_name = fight.get('fighter1_name', '').strip()
        elif f2_status and 'green' in f2_status.get('class', []):
            winner_name = fight.get('fighter2_name', '').strip()
        # Si no se detecta por color, intentar heurística por orden
        if not winner_name:
            winner_name = fight.get('fighter1_name', '').strip()
        # Asignar winner_id comparando winner_name con los nombres
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
        fight['weight_class'] = fight_title.text.strip()

    # Detectar si es upcoming (no hay detalles de pelea ni tabla de stats)
    is_upcoming = False
    # Heurística: si no hay div.b-fight-details__content o tabla de stats, es upcoming
    fight_content = soup.find('div', class_='b-fight-details__content')
    stats_table = soup.find('table', class_='b-fight-details__table')
    if not fight_content or not stats_table:
        is_upcoming = True

    # 4. Si es upcoming, dejar solo los datos básicos y el resto vacío/null/0
    all_keys = [
        'event_id', 'fighter1_name', 'fighter2_name', 'winner_nickname', 'loser_nickname',
        'weight_class', 'referee', 'round', 'time', 'time_format', 'method', 'details', 'bonus', 'judge_scores',
        'kd1', 'kd2', 'str1', 'str2', 'td1', 'td2', 'sub1', 'sub2'
    ]
    if is_upcoming:
        # Solo dejar los datos básicos, el resto vacío/null/0
        for k in all_keys:
            if k not in fight:
                if k in ['kd1','kd2','td1','td2','sub1','sub2']:
                    fight[k] = '0'
                else:
                    fight[k] = ''
        return fight

    # 5. Meta info de la pelea (method, round, time, referee, details)
    if fight_content:
        import re
        def clean_value(val):
            if not val:
                return ''
            v = val
            v = re.sub(r'[\n\r\t]+', ' ', v)
            v = re.sub(r'\s+', ' ', v)
            v = v.strip()
            for prefix in ['time:', 'method:', 'round:', 'referee:', 'time format:', 'details:']:
                pattern = re.compile(r'^' + re.escape(prefix) + r'\s*', re.IGNORECASE)
                v = pattern.sub('', v).strip()
            return v

        # 1. Method (solo el texto del método)
        # Método: buscar el <i class='b-fight-details__label'> con texto 'Method:' y tomar el siguiente <i style='font-style: normal'>
        method_val = ''
        method_label = None
        for tag in fight_content.find_all('i', class_='b-fight-details__label'):
            if tag.text.strip().lower().startswith('method'):
                method_label = tag
                break
        if method_label:
            # Buscar el siguiente <i style='font-style: normal'> después del label
            next_i = method_label.find_next_sibling('i')
            if not next_i:
                # Si no es sibling directo, buscar en el parent
                parent = method_label.parent
                if parent:
                    next_i = parent.find('i', style=lambda v: v and 'font-style: normal' in v)
            if next_i and next_i.has_attr('style') and 'font-style: normal' in next_i['style']:
                method_val = next_i.get_text()
        fight['method'] = clean_value(method_val)

        # 2. Round, time, time_format, referee (igual que antes)
        # El bloque anterior de 'items' ya no es necesario porque los campos se extraen individualmente

        # 3. Details: si es decisión, poner los scores; si no, el detalle
        details_p = fight_content.find_all('p', class_='b-fight-details__text')
        judge_scores_regex = re.compile(r'\d+\s*-\s*\d+')
        method = fight.get('method', '').lower()
        for p in details_p:
            txt = p.get_text(separator=' ', strip=True)
            txt_clean = clean_value(txt)
            if method.startswith('decision') and judge_scores_regex.search(txt_clean):
                fight['details'] = txt_clean
            elif not method.startswith('decision') and txt_clean and not txt_clean.lower().startswith('details:'):
                fight['details'] = txt_clean


    # 6. Bonus (si existe)
    bonus_tag = soup.find('i', class_='b-fight-details__fight-bonus')
    if bonus_tag:
        fight['bonus'] = clean_value(bonus_tag.text)

    # 7. Judge scores (si existe)
    judge_scores_tag = soup.find('p', class_='b-fight-details__text')
    if judge_scores_tag:
        fight['judge_scores'] = clean_value(judge_scores_tag.text)

    # 8. Estadísticas principales (tabla Totals)
    if stats_table:
        rows = stats_table.find_all('tr')
        # La primera fila es header, la segunda es datos totales
        if len(rows) > 1:
            cols = rows[1].find_all('td')
            # KD, STR, TD, SUB ATT
            def get_stat(col, idx):
                ps = col.find_all('p')
                if len(ps) == 2:
                    return ps[idx].text.strip()
                elif len(ps) == 1:
                    return ps[0].text.strip()
                else:
                    return col.text.strip()
            if len(cols) >= 10:
                fight['kd1'] = get_stat(cols[1], 0).strip()
                fight['kd2'] = get_stat(cols[1], 1).strip()
                fight['str1'] = get_stat(cols[2], 0).strip()
                fight['str2'] = get_stat(cols[2], 1).strip()
                fight['td1'] = get_stat(cols[5], 0).strip()
                fight['td2'] = get_stat(cols[5], 1).strip()
                fight['sub1'] = get_stat(cols[7], 0).strip()
                fight['sub2'] = get_stat(cols[7], 1).strip()

    # 9. Rellenar campos vacíos
    for k in all_keys:
        if k not in fight:
            if k in ['kd1','kd2','td1','td2','sub1','sub2']:
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
