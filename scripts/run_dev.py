"""Development runner script."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.pipeline.orchestrator import UFCScrapingOrchestrator

def main():
    """Run scraper in development mode."""
    orchestrator = UFCScrapingOrchestrator(dev_mode=True, dev_limit=10)
    orchestrator.run_full_pipeline()

if __name__ == "__main__":
    main()