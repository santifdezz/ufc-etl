"""
Script para ejecutar el pipeline en modo desarrollo.
Permite lanzar el orquestador con un límite reducido de datos para pruebas y depuración.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.pipeline.orchestrator import UFCScrapingOrchestrator

def main():
    """
    Ejecuta el pipeline de scraping en modo desarrollo.
    Lanza el orquestador con un límite bajo de registros para facilitar pruebas rápidas.
    """
    orchestrator = UFCScrapingOrchestrator(dev_mode=True, dev_limit=10)
    orchestrator.run_full_pipeline()

if __name__ == "__main__":
    main()