"""
Pruebas unitarias para los parsers del pipeline UFC ETL.
Incluyen validaciones de normalización, extracción y completado de campos en los parsers de luchadores, eventos y peleas.
"""
import pytest
from bs4 import BeautifulSoup
from src.scrapers.fighters.parser import FighterParser
from src.scrapers.events.parser import EventParser
from src.scrapers.fights.parser import FightParser


class TestFighterParser:
    """
    Pruebas unitarias para el parser de luchadores.
    """
    
    def setup_method(self):
        self.parser = FighterParser()
    
    def test_normalize_field(self):
        """
        Prueba la normalización de campos de texto en el parser de luchadores.
        """
        assert self.parser.normalize_field("  test  ") == "test"
        assert self.parser.normalize_field("--") is None
        assert self.parser.normalize_field("") is None
        assert self.parser.normalize_field(None) is None
    
    def test_parse_fighters_table_empty(self):
        """
        Prueba el parseo de una tabla vacía de luchadores.
        """
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        result = self.parser.parse_fighters_table(soup)
        assert result == []


class TestEventParser:
    """
    Pruebas unitarias para el parser de eventos.
    """
    
    def setup_method(self):
        self.parser = EventParser()
    
    def test_parse_events_table_empty(self):
        """
        Prueba el parseo de una tabla vacía de eventos.
        """
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        result = self.parser.parse_events_table(soup, "completed")
        assert result == []


class TestFightParser:
    """
    Pruebas unitarias para el parser de peleas.
    """
    
    def setup_method(self):
        self.parser = FightParser()
    
    def test_fill_empty_fields(self):
        """
        Prueba el completado automático de campos vacíos en el parser de peleas.
        """
        fight = {'event_id': 'test123'}
        result = self.parser._fill_empty_fields(fight)
        
        # Check that numeric fields are '0'
        assert result['kd1'] == '0'
        assert result['kd2'] == '0'
        
        # Check that string fields are empty
        assert result['referee'] == ''
        assert result['method'] == ''