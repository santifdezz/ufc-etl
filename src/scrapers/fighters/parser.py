"""
Implementación del parser de luchadores (Fighter) para el pipeline UFC ETL.
Extrae y estructura información de luchadores y sus estadísticas a partir de HTML, utilizando BeautifulSoup y utilidades propias.
"""
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from ..base.parser import BaseParser
from ...utils.http import extract_id_from_url


class FighterParser(BaseParser):
    """
    Parser especializado para datos de luchadores.
    Proporciona métodos para extraer información básica y detallada de luchadores desde tablas y páginas HTML.
    """
    
    def parse_fighters_table(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extrae la tabla de luchadores desde el HTML y la convierte en una lista de diccionarios.
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup de la página de luchadores.
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los datos de cada luchador.
        """
        fighters = []
        table = soup.find('table', class_='b-statistics__table')
        
        if not table:
            return fighters
        
        rows = table.find_all('tr', class_='b-statistics__table-row')
        field_names = [
            'first', 'last', 'nickname', 'height', 'weight', 
            'reach', 'stance', 'wins', 'defeats', 'draws'
        ]
        
        for row in rows:
            cols = row.find_all('td')
            if not cols:
                continue
            
            # Extract fighter ID from link
            link_tag = cols[0].find('a', href=True)
            if not link_tag:
                continue
            
            fighter_id = extract_id_from_url(link_tag['href'])
            if not fighter_id:
                continue
            
            # Extract field values
            values = []
            for i in range(len(field_names)):
                if len(cols) > i:
                    value = self.normalize_field(cols[i].get_text())
                    values.append(value)
                else:
                    values.append(None)
            
            # Check for belt (usually in column 10+)
            belt = False
            if len(cols) > 10:
                belt_col = cols[10]
                img_tag = belt_col.find('img', src=True)
                if img_tag and 'belt.png' in img_tag['src']:
                    belt = True
            
            # Create fighter dict
            fighter = {'fighter_id': fighter_id, 'belt': belt}
            fighter.update(dict(zip(field_names, values)))
            fighters.append(fighter)
        
        return fighters
    
    def parse_fighter_details(self, html: str) -> Dict[str, Any]:
        """
        Extrae información detallada de un luchador a partir del HTML de su página de detalles.
        Args:
            html (str): HTML de la página de detalles del luchador.
        Returns:
            Dict[str, Any]: Diccionario con los campos detallados del luchador.
        """
        soup = BeautifulSoup(html, 'html.parser')
        details = {}
        
        # Extract DOB from info boxes
        info_boxes = soup.find_all('div', class_='b-list__info-box')
        for box in info_boxes:
            for li in box.find_all('li'):
                title = li.find('i')
                if title and 'DOB' in title.text:
                    dob_text = li.get_text(strip=True).replace('DOB:', '').strip()
                    details['dob'] = self.normalize_field(dob_text)
                    break
        
        # Extract career statistics
        middle_box = soup.find('div', 
            class_='b-list__info-box b-list__info-box_style_middle-width js-guide clearfix')
        
        if middle_box:
            left_section = middle_box.find('div', class_='b-list__info-box-left')
            if left_section:
                stats_mapping = {
                    'SLpM': 'slpm',
                    'Str. Acc.': 'str_acc',
                    'SApM': 'sapm',
                    'Str. Def': 'str_def',
                    'TD Avg.': 'td_avg',
                    'TD Acc.': 'td_acc',
                    'TD Def.': 'td_def',
                    'Sub. Avg.': 'sub_avg'
                }
                
                for li in left_section.find_all('li'):
                    title = li.find('i')
                    if not title:
                        continue
                    
                    title_text = title.text.strip()
                    for stat_key, field_name in stats_mapping.items():
                        if title_text.startswith(stat_key):
                            value_text = li.get_text(strip=True)
                            # Extract value after the colon
                            if ':' in value_text:
                                value = value_text.split(':', 1)[1].strip()
                                details[field_name] = self.normalize_field(value)
                            break
        
        return details