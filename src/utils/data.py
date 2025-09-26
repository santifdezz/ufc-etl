"""Data utilities for CSV operations."""
import csv
from typing import List, Dict, Any
from pathlib import Path


class CSVManager:
    """Manager for CSV file operations."""
    
    @staticmethod
    def save_to_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str]):
        """Save data to CSV with proper formatting."""
        if not data:
            return
            
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Normalize fieldnames to lowercase
        fieldnames_lower = [f.lower() for f in fieldnames]
        
        # Convert None values to empty strings
        normalized_data = []
        for row in data:
            normalized_row = {}
            for key, value in row.items():
                key_lower = key.lower()
                normalized_row[key_lower] = '' if value is None else str(value)
            normalized_data.append(normalized_row)
        
        # Write CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames_lower, restval='')
            writer.writeheader()
            writer.writerows(normalized_data)
    
    @staticmethod
    def read_from_csv(filename: str) -> List[Dict[str, str]]:
        """Read data from CSV file."""
        with open(filename, 'r', encoding='utf-8') as csvfile:
            return list(csv.DictReader(csvfile))
    
    @staticmethod
    def copy_first_n_rows(source: str, destination: str, n: int = 20):
        """Copy first N rows from source to destination CSV."""
        with open(source, 'r', encoding='utf-8') as src:
            with open(destination, 'w', encoding='utf-8', newline='') as dst:
                reader = csv.reader(src)
                writer = csv.writer(dst)
                for i, row in enumerate(reader):
                    writer.writerow(row)
                    if i >= n:
                        break
