"""Unit tests for parsers."""
import pytest
from bs4 import BeautifulSoup
from src.scrapers.fighters.parser import FighterParser
from src.scrapers.events.parser import EventParser
from src.scrapers.fights.parser import FightParser


class TestFighterParser:
    """Test fighter parser."""
    
    def setup_method(self):
        self.parser = FighterParser()
    
    def test_normalize_field(self):
        """Test field normalization."""
        assert self.parser.normalize_field("  test  ") == "test"
        assert self.parser.normalize_field("--") is None
        assert self.parser.normalize_field("") is None
        assert self.parser.normalize_field(None) is None
    
    def test_parse_fighters_table_empty(self):
        """Test parsing empty table."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        result = self.parser.parse_fighters_table(soup)
        assert result == []


class TestEventParser:
    """Test event parser."""
    
    def setup_method(self):
        self.parser = EventParser()
    
    def test_parse_events_table_empty(self):
        """Test parsing empty events table."""
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        result = self.parser.parse_events_table(soup, "completed")
        assert result == []


class TestFightParser:
    """Test fight parser."""
    
    def setup_method(self):
        self.parser = FightParser()
    
    def test_fill_empty_fields(self):
        """Test filling empty fields."""
        fight = {'event_id': 'test123'}
        result = self.parser._fill_empty_fields(fight)
        
        # Check that numeric fields are '0'
        assert result['kd1'] == '0'
        assert result['kd2'] == '0'
        
        # Check that string fields are empty
        assert result['referee'] == ''
        assert result['method'] == ''