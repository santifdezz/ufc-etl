"""
Script para validación de datos en el pipeline UFC ETL.
Permite validar la integridad de los datos extraídos de luchadores, eventos y peleas, mostrando estadísticas de éxito.
"""
import sys
import os
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.config import Config
from src.utils.validation import DataValidator

def main():
    """
    Ejecuta la validación de los datos extraídos.
    Valida los archivos de luchadores, eventos y peleas, mostrando el porcentaje de registros válidos.
    """
    config = Config()
    validator = DataValidator()
    
    # Validate fighters
    print("Validating fighters data...")
    try:
        with open(config.data.fighters_path, 'r', encoding='utf-8') as f:
            fighters = list(csv.DictReader(f))
        
        stats = validator.validate_dataset(fighters, 'fighter')
        print(f"Fighters: {stats['valid']}/{stats['total']} valid ({stats['success_rate']:.1f}%)")
    except FileNotFoundError:
        print("Fighters file not found")
    
    # Validate events
    print("\nValidating events data...")
    try:
        with open(config.data.events_path, 'r', encoding='utf-8') as f:
            events = list(csv.DictReader(f))
        
        stats = validator.validate_dataset(events, 'event')
        print(f"Events: {stats['valid']}/{stats['total']} valid ({stats['success_rate']:.1f}%)")
    except FileNotFoundError:
        print("Events file not found")
    
    # Validate fights
    print("\nValidating fights data...")
    try:
        with open(config.data.fights_path, 'r', encoding='utf-8') as f:
            fights = list(csv.DictReader(f))
        
        stats = validator.validate_dataset(fights, 'fight')
        print(f"Fights: {stats['valid']}/{stats['total']} valid ({stats['success_rate']:.1f}%)")
    except FileNotFoundError:
        print("Fights file not found")

if __name__ == "__main__":
    main()