"""
Utilidades para operaciones con archivos CSV.
Incluye funciones para guardar, leer y copiar datos en formato CSV de manera robusta y consistente.
"""
import csv
from typing import List, Dict, Any
from pathlib import Path


class CSVManager:
    """
    Clase gestora de operaciones con archivos CSV, incluyendo guardado, lectura y copiado de filas.
    """
    
    @staticmethod
    def save_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str]):
        """
        Guarda una lista de diccionarios en un archivo CSV, asegurando formato y consistencia en los nombres de columnas.
        Si el directorio de destino no existe, lo crea automáticamente.
        Convierte valores None a cadenas vacías para evitar errores de escritura.
        """
        if not data:
            # Si no hay datos, no realiza ninguna acción
            return
            
        # Asegura que el directorio de destino exista antes de guardar el archivo
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Normaliza los nombres de las columnas a minúsculas para mantener consistencia
        fieldnames_lower = [f.lower() for f in fieldnames]
        
        # Convierte los valores None a cadenas vacías para evitar errores en la escritura del CSV
        normalized_data = []
        for row in data:
            normalized_row = {}
            for key, value in row.items():
                key_lower = key.lower()
                normalized_row[key_lower] = '' if value is None else str(value)
            normalized_data.append(normalized_row)
        
        # Escribe el archivo CSV en disco con los datos proporcionados
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames_lower, restval='')
            writer.writeheader()
            writer.writerows(normalized_data)
    
    @staticmethod
    def read_from_csv(filename: str) -> List[Dict[str, str]]:
        """
        Lee los datos de un archivo CSV y los devuelve como una lista de diccionarios.
        """
        with open(filename, 'r', encoding='utf-8') as csvfile:
            return list(csv.DictReader(csvfile))
    
    @staticmethod
    def copy_first_n_rows(source: str, destination: str, n: int = 20):
        """
        Copia las primeras N filas de un archivo CSV origen a un archivo CSV destino.
        Útil para crear muestras pequeñas de grandes datasets.
        """
        with open(source, 'r', encoding='utf-8') as src:
            with open(destination, 'w', encoding='utf-8', newline='') as dst:
                reader = csv.reader(src)
                writer = csv.writer(dst)
                for i, row in enumerate(reader):
                    writer.writerow(row)
                    if i >= n:
                        break
