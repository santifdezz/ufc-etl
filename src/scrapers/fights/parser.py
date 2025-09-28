"""
Implementación del parser de peleas (Fight) para el pipeline UFC ETL.
Extrae y estructura información detallada de peleas a partir de HTML, utilizando BeautifulSoup y utilidades propias.
"""
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from ..base.parser import BaseParser
from ...utils.http import extract_id_from_url, clean_text


class FightParser(BaseParser):
    """
    Parser especializado para datos de peleas.
    Proporciona métodos para extraer información de peleas, detalles, estadísticas y desgloses desde páginas HTML de eventos y peleas.
    """
    
    def parse_event_fights(self, soup: BeautifulSoup, event_id: str) -> List[Dict[str, Any]]:
        """
        Extrae la lista de peleas de una página de evento.
        Args:
            soup (BeautifulSoup): Objeto BeautifulSoup de la página del evento.
            event_id (str): Identificador del evento.
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los datos mínimos de cada pelea.
        """
        fights = []
        fight_table = soup.find('table', class_='b-fight-details__table')
        
        if not fight_table:
            return fights
        
        tbody = fight_table.find('tbody')
        if not tbody:
            return fights
        
        rows = tbody.find_all('tr')
        
        for idx, row in enumerate(rows):
            cols = row.find_all('td')
            if not cols or len(cols) < 10:
                continue
            
            # Extrae el identificador de la pelea (fight_id) desde el atributo data-link
            fight_id = row.get('data-link')
            if fight_id:
                fight_id = extract_id_from_url(fight_id)
            
            if not fight_id:
                continue
            
            fights.append({
                'event_id': event_id,
                'fight_id': fight_id,
                'fight_order': idx + 1
            })
        
        return fights
    
    def parse_fight_details(self, html: str) -> Dict[str, Any]:
        """
        Extrae información detallada de una pelea a partir del HTML de la página de detalles.
        Args:
            html (str): HTML de la página de detalles de la pelea.
        Returns:
            Dict[str, Any]: Diccionario con todos los campos estructurados de la pelea.
        """
        soup = BeautifulSoup(html, 'html.parser')
        fight = {}
        
    # 1. Extraer el identificador del evento (event_id)
        event_tag = soup.find('h2', class_='b-content__title')
        if event_tag:
            event_link = event_tag.find('a', href=True)
            if event_link:
                fight['event_id'] = extract_id_from_url(event_link['href'])
        
    # 2. Extraer información de los luchadores participantes
        self._extract_fighter_info(soup, fight)
        
    # 3. Extraer la categoría de peso/título y los bonus desde el título de la pelea
        fight_title = soup.find('i', class_='b-fight-details__fight-title')
        if fight_title:
            # Extrae el texto de la categoría de peso, excluyendo los iconos de bonus
            title_text = fight_title.get_text(strip=True)
            fight['weight_class'] = title_text

            # Extrae los tipos de bonus a partir de las etiquetas <img>
            bonus_types = []
            bonus_map = {
                'belt.png': 'BELT',
                'ko.png': 'KO',
                'fight.png': 'FIGHT',
                'perf.png': 'PERF',
                'sub.png': 'SUB',
            }
            for img in fight_title.find_all('img', src=True):
                for key, value in bonus_map.items():
                    if img['src'].lower().endswith(key):
                        bonus_types.append(value)
            if bonus_types:
                fight['bonus'] = bonus_types
            else:
                fight['bonus'] = None

        
    # 4. Verifica si la pelea es próxima (sin estadísticas detalladas)
        if self._is_upcoming_fight(soup):
            return self._fill_empty_fields(fight)
        
    # 5. Extrae los detalles de la pelea
        self._extract_fight_details(soup, fight)
        
    # 6. Asigna None a bonus si aún no ha sido definido
        if 'bonus' not in fight:
            fight['bonus'] = None
        
    # 7. Extrae las estadísticas principales de la pelea
        self._extract_fight_statistics(soup, fight)
        
    # 8. Extrae el desglose de golpes significativos
        self._extract_significant_strikes(soup, fight)
        
        return self._fill_empty_fields(fight)
    
    def _extract_fighter_info(self, soup: BeautifulSoup, fight: Dict[str, Any]):
        """
        Extrae información de los luchadores participantes en la pelea (nombres e IDs, ganador).
        """
        persons = soup.find_all('div', class_='b-fight-details__person')
        
        if len(persons) >= 2:
            # Estadísticas del luchador 1
            f1_name = persons[0].find('h3', class_='b-fight-details__person-name')
            if f1_name and f1_name.a:
                fight['red_name'] = f1_name.a.text.strip()
                fight['red_id'] = extract_id_from_url(f1_name.a.get('href', ''))
            
            # Estadísticas del luchador 2
            f2_name = persons[1].find('h3', class_='b-fight-details__person-name')
            if f2_name and f2_name.a:
                fight['blue_name'] = f2_name.a.text.strip()
                fight['blue_id'] = extract_id_from_url(f2_name.a.get('href', ''))
            
            # Determina el ganador de la pelea
            winner_name, winner_id = self.extract_winner_from_status(persons)
            if winner_id:
                fight['winner_id'] = winner_id
            elif winner_name:
                # Alternativa: asocia el nombre del ganador con los IDs de los luchadores
                if winner_name == fight.get('red_name'):
                    fight['winner_id'] = fight.get('red_id', '')
                elif winner_name == fight.get('blue_name'):
                    fight['winner_id'] = fight.get('blue_id', '')

    def _is_upcoming_fight(self, soup: BeautifulSoup) -> bool:
        """
        Verifica si la pelea es próxima (sin estadísticas detalladas disponibles).
        """
        fight_content = soup.find('div', class_='b-fight-details__content')
        stats_table = soup.find('table')
        return not fight_content or not stats_table
    
    def _extract_fight_details(self, soup: BeautifulSoup, fight: Dict[str, Any]):
        """
        Extrae detalles de la pelea como método de victoria, round, tiempo, formato y árbitro.
        """
        fight_content = soup.find('div', class_='b-fight-details__content')
        if not fight_content:
            return
        
    # Busca todos los elementos de texto relevantes
        text_items = fight_content.find_all('i', class_='b-fight-details__text-item')
        text_items_first = fight_content.find_all('i', class_='b-fight-details__text-item_first')
        all_items = text_items_first + text_items
        
        for item in all_items:
            self._parse_fight_detail_item(item, fight)
        
    # Extrae la sección de detalles de la pelea
        self._extract_details_section(fight_content, fight)
    
    def _parse_fight_detail_item(self, item: BeautifulSoup, fight: Dict[str, Any]):
        """
        Parsea un ítem individual de detalle de pelea (método, round, tiempo, formato, árbitro).
        """
        label_tag = item.find('i', class_='b-fight-details__label')
        if not label_tag:
            return
        
        label_text = label_tag.get_text(strip=True).lower().replace(':', '')
        full_text = item.get_text(strip=True)
        
        if label_text == 'method':
            method_element = label_tag.find_next_sibling()
            if method_element and method_element.name == 'i':
                fight['method'] = clean_text(method_element.get_text(strip=True))
            else:
                method_match = re.search(r'Method:\s*(.+?)(?:\s+Round:|$)', full_text)
                if method_match:
                    fight['method'] = clean_text(method_match.group(1))
        
        elif label_text == 'round':
            round_match = re.search(r'Round:\s*(\d+)', full_text)
            if round_match:
                fight['round'] = round_match.group(1)
        
        elif label_text == 'time':
            time_match = re.search(r'Time:\s*(\d+:\d+)', full_text)
            if time_match:
                fight['time'] = time_match.group(1)
        
        elif label_text == 'time format':
            format_match = re.search(r'Time format:\s*(.+?)(?:\s+Referee:|$)', full_text)
            if format_match:
                fight['time_format'] = clean_text(format_match.group(1))
        
        elif label_text == 'referee':
            referee_span = item.find('span')
            if referee_span:
                fight['referee'] = clean_text(referee_span.get_text(strip=True))
            else:
                referee_match = re.search(r'Referee:\s*(.+)', full_text)
                if referee_match:
                    fight['referee'] = clean_text(referee_match.group(1))
    
    def _extract_details_section(self, fight_content: BeautifulSoup, fight: Dict[str, Any]):
        """
        Extrae la sección de detalles específicos del método de victoria.
        """
        details_sections = fight_content.find_all('p', class_='b-fight-details__text')
        
        for section in details_sections:
            details_label = section.find('i', class_='b-fight-details__label')
            if details_label and 'details' in details_label.get_text(strip=True).lower():
                section_text = section.get_text(strip=True)
                details_match = re.search(r'Details:\s*(.+)', section_text, re.IGNORECASE)
                if details_match:
                    fight['details'] = clean_text(details_match.group(1))
                    break
    
    def _extract_fight_statistics(self, soup: BeautifulSoup, fight: Dict[str, Any]):
        """
        Extrae las estadísticas principales de la pelea desde la tabla principal de estadísticas.
        """
        stats_table = soup.find('table')
        if not stats_table:
            return
        
        data_rows = stats_table.find('tbody')
        if not data_rows:
            return
        
        data_row = data_rows.find('tr')
        if not data_row:
            return
        
        cols = data_row.find_all('td')
        if len(cols) < 10:
            return
        
    # Mapeo de columnas basado en la tabla típica de estadísticas de UFC
    # Col 1: Knockdowns, Col 2: Golpes significativos, Col 4: Golpes totales, Col 5: Derribos, Col 7: Intentos de sumisión
    # Col 8: Reversiones, Col 9: Tiempo de control
        
        fight['kd1'] = self._get_stat_for_fighter(cols[1], 0)
        fight['kd2'] = self._get_stat_for_fighter(cols[1], 1)
        fight['str1'] = self._get_stat_for_fighter(cols[2], 0)  # Golpes significativos
        fight['str2'] = self._get_stat_for_fighter(cols[2], 1)
        fight['td1'] = self._get_stat_for_fighter(cols[5], 0)   # Derribos
        fight['td2'] = self._get_stat_for_fighter(cols[5], 1)
        fight['sub1'] = self._get_stat_for_fighter(cols[7], 0)  # Intentos de sumisión
        fight['sub2'] = self._get_stat_for_fighter(cols[7], 1)
        
    # Estadísticas adicionales si están disponibles
        if len(cols) > 8:
            fight['rev1'] = self._get_stat_for_fighter(cols[8], 0)  # Reversiones
            fight['rev2'] = self._get_stat_for_fighter(cols[8], 1)
        
        if len(cols) > 9:
            fight['control_time1'] = self._get_stat_for_fighter(cols[9], 0)  # Tiempo de control
            fight['control_time2'] = self._get_stat_for_fighter(cols[9], 1)
        
        if len(cols) > 4:
            fight['total_str1'] = self._get_stat_for_fighter(cols[4], 0)  # Golpes totales
            fight['total_str2'] = self._get_stat_for_fighter(cols[4], 1)
    
    def _get_stat_for_fighter(self, col: BeautifulSoup, fighter_idx: int) -> str:
        """
        Extrae una estadística específica para un luchador (0 = rojo, 1 = azul) de una columna de la tabla.
        """
        ps = col.find_all('p', class_='b-fight-details__table-text')
        
        if len(ps) >= 2:
            return ps[fighter_idx].get_text(strip=True)
        elif len(ps) == 1:
            return ps[0].get_text(strip=True) if fighter_idx == 0 else '0'
        else:
            return '0'
    
    def _extract_significant_strikes(self, soup: BeautifulSoup, fight: Dict[str, Any]):
        """
        Extrae el desglose de golpes significativos (cabeza, cuerpo, pierna) de la tabla correspondiente.
        """
    # Busca la sección de golpes significativos
        sig_strikes_section = soup.find(
            'p', 
            class_='b-fight-details__collapse-link_tot',
            string=lambda text: text and 'Significant Strikes' in text
        )
        
        if not sig_strikes_section:
            return
        
    # Busca la siguiente tabla de estadísticas
        sig_table = sig_strikes_section.find_next('table')
        if not sig_table:
            return
        
        sig_tbody = sig_table.find('tbody')
        if not sig_tbody:
            return
        
        sig_row = sig_tbody.find('tr')
        if not sig_row:
            return
        
        sig_cols = sig_row.find_all('td')
        
    # Columnas: Luchador, Golpes significativos, %, Cabeza, Cuerpo, Pierna, Distancia, Clinch, Suelo
        if len(sig_cols) >= 9:
            fight['sig_head1'] = self._get_stat_for_fighter(sig_cols[3], 0)  # Golpes a la cabeza
            fight['sig_head2'] = self._get_stat_for_fighter(sig_cols[3], 1)
            fight['sig_body1'] = self._get_stat_for_fighter(sig_cols[4], 0)  # Golpes al cuerpo
            fight['sig_body2'] = self._get_stat_for_fighter(sig_cols[4], 1)
            fight['sig_leg1'] = self._get_stat_for_fighter(sig_cols[5], 0)   # Golpes a la pierna
            fight['sig_leg2'] = self._get_stat_for_fighter(sig_cols[5], 1)
    
    def _fill_empty_fields(self, fight: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rellena los campos vacíos de la pelea con valores por defecto (cero, cadena vacía o None según corresponda).
        """
    # Los campos numéricos toman '0' como valor por defecto
        numeric_fields = [
            'kd1', 'kd2', 'str1', 'str2', 'td1', 'td2', 'sub1', 'sub2',
            'pass1', 'pass2', 'rev1', 'rev2'
        ]
        
    # Los campos de texto toman cadena vacía como valor por defecto, excepto 'bonus' que debe ser None
        string_fields = [
            'event_id', 'red_name', 'blue_name', 'red_id', 'blue_id',
            'winner_id', 'weight_class', 'referee', 'round', 'time', 'time_format',
            'method', 'details', 'control_time1', 'control_time2',
            'sig_head1', 'sig_head2', 'sig_body1', 'sig_body2', 'sig_leg1', 'sig_leg2',
            'total_str1', 'total_str2'
        ]

        for field in numeric_fields:
            if field not in fight:
                fight[field] = '0'

        for field in string_fields:
            if field not in fight:
                fight[field] = ''

        if 'bonus' not in fight:
            fight['bonus'] = None

        return fight