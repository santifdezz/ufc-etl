# utils/helpers.py
import re
import time
from bs4 import BeautifulSoup
import requests
from config import HEADERS, DELAY

def get_soup(url):
    """Obtiene el contenido HTML de una URL y retorna un objeto BeautifulSoup"""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return None

def extract_id(url):
    """Extrae el ID de una URL de UFC Stats"""
    if not url:
        return ""
    match = re.search(r'/([^/]+)$', url)
    return match.group(1) if match else ""

def clean_text(text):
    """Limpia y normaliza el texto extraído"""
    if not text:
        return ""
    return text.strip().replace('\n', ' ').replace('  ', ' ')

def safe_extract(element, selector, attribute=None):
    """Extrae contenido de forma segura de un elemento BeautifulSoup"""
    if not element:
        return ""
    
    found = element.select_one(selector)
    if not found:
        return ""
    
    if attribute:
        return found.get(attribute, "").strip()
    else:
        return clean_text(found.get_text())

def delay_request():
    """Pausa entre requests para ser respetuoso con el servidor"""
    time.sleep(DELAY)