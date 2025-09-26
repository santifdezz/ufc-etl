# UFC Stats Scraper

Professional-grade scraper for UFC statistics data.

## Features

- **Modular Architecture**: Clean separation of concerns
- **Concurrent Processing**: Fast data extraction
- **Development Mode**: Limited scraping for testing
- **Data Validation**: Built-in data integrity checks
- **Comprehensive Testing**: Unit and integration tests
- **Professional Logging**: Structured error handling

## Installation
```bash
    pip install -e .
```
### Creación y Activación del Entorno
```bash
# Crear el entorno desde el archivo
conda env create -f environment.yml

# Activar el entorno
conda activate ufc_scraper

# Actualizar el entorno si ya existe
conda env update -f environment.yml --prune

```
## Quick Start
```python
    pythonfrom src.pipeline.orchestrator import UFCScrapingOrchestrator

    # Run full pipeline
    orchestrator = UFCScrapingOrchestrator()
    orchestrator.run_full_pipeline()

    # Development mode
    orchestrator = UFCScrapingOrchestrator(dev_mode=True, dev_limit=20)
    orchestrator.run_full_pipeline()
```
## Command Line
```bash
    # Full scraping
    python main.py

    # Development mode
    python main.py --dev --limit 50

    # Run development script
    python scripts/run_dev.py

    # Validate data
    python scripts/validate_data.py
```
## Architecture
```bash
src/
├── core/          # Configuration and exceptions
├── scrapers/      # Scraping logic (fighters, events, fights)
├── utils/         # Utilities (HTTP, data, concurrency)
├── models/        # Data models
└── pipeline/      # Orchestration logic
```
## Testing
```bash
    # Run all tests
    pytest

    # Run unit tests only
    pytest tests/unit/

    # Run with coverage
    pytest --cov=src

    # Skip integration tests
    pytest -m "not integration"
```
# Data Output
The scraper generates three main CSV files:

 - data/raw_fighters.csv: Fighter information and statistics
 - data/raw_events.csv: Event information
 - data/raw_fights.csv: Fight details and statistics

## Configuration

Edit src/core/config.py to modify:

 - Scraping parameters (workers, delays)
 - Data paths
 - Development mode settings

## Contributing

 - Fork the repository
 - Create a feature branch
 - Add tests for new functionality
 - Run the test suite
 - Submit a pull request