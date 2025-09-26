"""Main entry point for UFC scraper."""
import argparse
from src.pipeline.orchestrator import UFCScrapingOrchestrator


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='UFC Stats Scraper')
    parser.add_argument('--dev', action='store_true', 
                       help='Run in development mode with limited records')
    parser.add_argument('--limit', type=int, default=20,
                       help='Limit number of records in dev mode')
    
    args = parser.parse_args()
    
    # Initialize and run orchestrator
    orchestrator = UFCScrapingOrchestrator(
        dev_mode=args.dev,
        dev_limit=args.limit
    )
    
    orchestrator.run_full_pipeline()


if __name__ == "__main__":
    main()