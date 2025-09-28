# UFC ETL - Extracción y Procesamiento de Datos de la UFC

Proyecto profesional para la extracción, limpieza y análisis de datos de peleas, luchadores y eventos de la UFC. Incluye scraping avanzado, validación, transformación y preparación de datasets para Machine Learning.

---

## Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Características Principales](#características-principales)
- [Instalación y Entorno](#instalación-y-entorno)
- [Uso Rápido](#uso-rápido)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Pruebas](#pruebas)
- [Salidas de Datos](#salidas-de-datos)
- [Configuración](#configuración)
- [Contribuciones](#contribuciones)
- [Créditos y Licencia](#créditos-y-licencia)

---

## Descripción General
Este proyecto permite extraer, limpiar y analizar datos históricos de la UFC de manera eficiente y reproducible. El pipeline automatiza la descarga, validación, transformación y exportación de datos listos para análisis y modelado predictivo.

## Características Principales
- **Arquitectura modular**: Separación clara de scraping, modelos, utilidades y orquestación.
- **Procesamiento concurrente**: Extracción rápida y eficiente de grandes volúmenes de datos.
- **Modo desarrollo**: Permite pruebas rápidas con límites configurables.
- **Validación de datos**: Controles de integridad y calidad integrados.
- **Cobertura de pruebas**: Tests unitarios y de integración con Pytest.
- **Logging profesional**: Manejo estructurado de errores y logs.
- **Preparación para ML**: Limpieza y exportación de datasets listos para modelos.

## Instalación y Entorno
1. Clona el repositorio:
   ```bash
   git clone https://github.com/santifdezz/ufc-etl.git
   cd ufc-etl
   ```
2. Crea y activa el entorno Conda:
   ```bash
   conda env create -f environment.yml
   conda activate ufc_scraper
   # Para actualizar el entorno:
   conda env update -f environment.yml --prune
   ```
3. Instala el paquete en modo editable:
   ```bash
   pip install -e .
   ```

## Uso Rápido
### Desde Python
```python
from src.pipeline.orchestrator import UFCScrapingOrchestrator

# Ejecutar el pipeline completo
orchestrator = UFCScrapingOrchestrator()
orchestrator.run_full_pipeline()

# Modo desarrollo (scraping limitado)
orchestrator = UFCScrapingOrchestrator(dev_mode=True, dev_limit=20)
orchestrator.run_full_pipeline()
```
### Desde la línea de comandos
```bash
# Scraping completo
python main.py

# Modo desarrollo
python main.py --dev --limit 50

# Ejecutar script de desarrollo
python scripts/run_dev.py

# Validar datos
python scripts/validate_data.py
```

## Estructura del Proyecto
```text
src/
├── core/          # Configuración y excepciones
├── scrapers/      # Lógica de scraping (luchadores, eventos, peleas)
├── utils/         # Utilidades (HTTP, datos, concurrencia)
├── models/        # Modelos de datos
└── pipeline/      # Orquestación del pipeline
scripts/           # Scripts auxiliares y de validación
notebooks/         # Análisis exploratorio y limpieza avanzada
data/              # Datos brutos y procesados
tests/             # Pruebas unitarias e integración
```

## Pruebas
Ejecuta la batería de tests con Pytest:
```bash
# Ejecutar todos los tests
pytest

# Solo tests unitarios
pytest tests/unit/

# Con reporte de cobertura
pytest --cov=src

# Omitir tests de integración
pytest -m "not integration"
```

## Salidas de Datos
El pipeline genera los siguientes archivos principales:

- `data/raw/raw_fighters.csv`: Información y estadísticas de luchadores
- `data/raw/raw_events.csv`: Información de eventos
- `data/raw/raw_fights.csv`: Detalles y estadísticas de peleas
- `data/processed/`: Archivos limpios y listos para análisis
- `data/ml/`: Datasets finales para Machine Learning

## Configuración
Modifica los parámetros en `src/core/config.py` para ajustar:
- Parámetros de scraping (número de workers, delays)
- Rutas de datos
- Opciones de modo desarrollo

## Contribuciones
¡Las contribuciones son bienvenidas!
1. Haz un fork del repositorio
2. Crea una rama para tu feature o fix
3. Añade pruebas para nuevas funcionalidades
4. Ejecuta la batería de tests
5. Envía un Pull Request con una descripción clara

## Créditos y Licencia
- Autor: Santiago Fernández ([@santifdezz](https://github.com/santifdezz))
- Licencia: MIT
- Inspirado en proyectos de scraping y análisis de datos deportivos

---
Para dudas, sugerencias o reportes de bugs, abre un issue en GitHub.